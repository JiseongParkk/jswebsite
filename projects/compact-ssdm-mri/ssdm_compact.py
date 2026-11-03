"""Reduced-width SSDM experiment, with volume-disjoint tuning and final scoring.

Preserves 320x320 complex images, 8 CDL components, joint component attention,
epsilon+summed-reconstruction training, CG/global measurement guidance and DDIM.
Not an exact paper reproduction: width64, partial pretrained CDL and data,
train-estimated common component scaling, and finite update budgets are explicit.
"""
from pathlib import Path
from dataclasses import asdict
import gc, hashlib, json, time
import numpy as np
import torch
import psutil
import h5py
import ssdm_experiment as ex
from ssdm_backbone import SSDMUNet, BackboneConfig
from ssdm_cdl import CoupledDictionary, complex_to_ri, ri_to_complex, fft2c, ifft2c
from ssdm_sampling import sample_ssdm, SamplerConfig
from ssdm_drive_lazy import ManifestSlices, manifest, provenance

ARCH = BackboneConfig(model_channels=64, num_head_channels=32, cross_attention_heads=4)
SEED = 20261023
CANDIDATES = {'lr1e-4': 1e-4, 'lr3e-4': 3e-4}


def release():
    gc.collect()
    torch.cuda.empty_cache()


def seed(n):
    np.random.seed(n % 2**32)
    torch.manual_seed(n)
    torch.cuda.manual_seed_all(n)


def memory():
    return dict(system_used_GiB=round(psutil.virtual_memory().used/2**30,3),
                process_RSS_GiB=round(psutil.Process().memory_info().rss/2**30,3),
                GPU_peak_GiB=round(torch.cuda.max_memory_allocated()/2**30,3))


class CompactRun:
    def __init__(self, base='/content/drive/MyDrive/SSDM320_full_run'):
        assert torch.cuda.is_available(), 'GPU runtime is required.'
        self.base = Path(base)
        self.root = self.base/'compact320_20261023'
        self.root.mkdir(exist_ok=True)
        self.train_data = ManifestSlices(self.base/'data/train', training=True, size=320)
        self.val_manifest, self.val_files = manifest(self.base/'data/val')
        assert not {p.name for p in self.train_data.files} & {p.name for p in self.val_files}
        self.cdl_path = self.base/'available_train_run/cdl_latest.pt'
        self.cdl_hash = ex._file_sha256(self.cdl_path)
        state = torch.load(self.cdl_path, map_location='cpu', weights_only=False)
        train_identity = hashlib.sha256('\n'.join(f'{p.name}:{i}' for p,i in self.train_data.index).encode()).hexdigest()
        assert state['data_info']['train_index_hash'] == train_identity
        assert state['data_info']['train_provenance_hash'] == provenance(self.base/'data/train', self.train_data.files)
        self.cdl = CoupledDictionary().cuda().eval().requires_grad_(False)
        self.cdl.load_state_dict(state['model'])
        cdl_updates = state['updates']
        del state
        self.betas = torch.linspace(1e-4,.02,1000,device='cuda')
        self.ac = (1-self.betas).cumprod(0)
        protocol_path = self.root/'protocol.json'
        if protocol_path.exists():
            self.protocol = json.loads(protocol_path.read_text())
            assert self.protocol['cdl_sha256'] == self.cdl_hash
            assert self.protocol['train_index_hash'] == train_identity
        else:
            # Exclude the two previously inspected validation subjects.
            excluded = {'file1000932.h5','file1000178.h5'}
            available = [p.name for p in self.val_files if p.name not in excluded]
            chosen = np.random.RandomState(SEED).permutation(available).tolist()
            def plan(names):
                return [dict(file=n, slice=int(self.val_manifest['volumes'][n]['slices'])//2) for n in names]
            self.protocol = dict(schema=1, seed=SEED, architecture=asdict(ARCH),
                cdl_sha256=self.cdl_hash, cdl_updates=cdl_updates, cdl_completed=False,
                train_index_hash=train_identity, train_volumes=len(self.train_data.files),
                train_slices=len(self.train_data), dev=plan(chosen[:4]), final=plan(chosen[4:12]),
                excluded_previously_seen=sorted(excluded), candidates=CANDIDATES,
                screen_updates=300, selected_target_updates=900, reconstruction_weight=.001,
                component_scale=None, normalization='one common RMS estimated from32 train slices; y/anchors scaled identically',
                sampling=dict(inference_steps=100,sigma_schedule='paper_literal'),
                selection_metric='mean development PSNR over R8 and R16',
                image_size=320, components=8, slice_policy='one middle slice per volume',
                paper_reproduction=False, complete_training_archive=False,
                notes='Unpublished choices are declared; LR selected on dev only. Final volumes never guide selection.')
            ex.json_write(protocol_path,self.protocol)
        self.scale = self.protocol['component_scale']
        print('Compact experiment:',self.root,'train',len(self.train_data),'dev4 / final8 disjoint volumes',flush=True)

    def calibrate(self):
        if self.scale is None:
            values=[]
            for i in np.random.RandomState(SEED).choice(len(self.train_data),32,replace=False):
                x,_,_=self.train_data[int(i)]
                with torch.no_grad():
                    c=self.cdl(x[None].cuda()).subspaces
                    values.append(float(c.square().mean()))
            self.scale=float(np.sqrt(np.mean(values)))
            assert np.isfinite(self.scale) and self.scale>1e-6
            self.protocol['component_scale']=self.scale
            ex.json_write(self.root/'protocol.json',self.protocol)
        print('Frozen train-only component scale:',self.scale,flush=True)

    def _step(self, model, optimizer, scaler, index):
        x,_,_=self.train_data[index]
        x=x[None].cuda()
        with torch.no_grad():
            clean=self.cdl(x).subspaces/self.scale
        t=torch.randint(1000,(1,),device='cuda')
        a=self.ac[t].reshape(1,1,1,1,1)
        noise=torch.randn_like(clean)
        noisy=a.sqrt()*clean+(1-a).sqrt()*noise
        optimizer.zero_grad(set_to_none=True)
        # GPU activation checkpointing, with NO CPU activation offload.
        with torch.autocast('cuda',dtype=torch.float16):
            eps=model(noisy,t)
        eps=eps.float()
        noise_loss=(eps-noise).square().mean()
        pred=(noisy-(1-a).sqrt()*eps)/a.sqrt()
        rec=(pred.sum(1)-x/self.scale).square().sum(1).mean()
        loss=noise_loss+.001*rec
        assert torch.isfinite(loss), 'Non-finite loss'
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        grad=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,foreach=False)
        previous_scale=scaler.get_scale()
        scaler.step(optimizer); scaler.update()
        return dict(noise=float(noise_loss.detach()),reconstruction=float(rec.detach()),
                    grad=float(grad),updated=scaler.get_scale()>=previous_scale)

    def preflight(self):
        self.calibrate(); seed(SEED); release()
        torch.cuda.reset_peak_memory_stats()
        model=SSDMUNet(ARCH).cuda().train()
        opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=0,foreach=False)
        scaler=torch.amp.GradScaler('cuda',init_scale=128)
        start=time.time(); rows=[]
        for j in range(3):
            rows.append(self._step(model,opt,scaler,j*37))
        torch.cuda.synchronize()
        result=dict(parameters=sum(p.numel() for p in model.parameters()),
                    seconds_per_step=(time.time()-start)/3,steps=rows,**memory())
        del model,opt,scaler; release()
        assert any(r['updated'] for r in rows), 'No successful update in preflight'
        assert result['system_used_GiB']<9.5, 'Insufficient system RAM headroom'
        ex.json_write(self.root/'memory_preflight.json',result)
        print('MEMORY PREFLIGHT',json.dumps(result),flush=True)
        return result

    def train(self, candidate, target):
        assert candidate in CANDIDATES
        self.calibrate(); seed(SEED); release()
        path=self.root/f'{candidate}.pt'
        model=SSDMUNet(ARCH).cuda().train()
        opt=torch.optim.AdamW(model.parameters(),lr=CANDIDATES[candidate],weight_decay=0,foreach=False)
        scaler=torch.amp.GradScaler('cuda',init_scale=128)
        updates=attempts=0
        if path.exists():
            state=torch.load(path,map_location='cpu',weights_only=False)
            assert state['cdl_sha256']==self.cdl_hash and state['scale']==self.scale
            assert state['candidate']==candidate and state['architecture']==asdict(ARCH)
            model.load_state_dict(state['model']); opt.load_state_dict(state['optimizer'])
            scaler.load_state_dict(state['scaler'])
            updates,attempts=state['updates'],state['attempts']
            torch.set_rng_state(state['rng_cpu']); torch.cuda.set_rng_state_all(state['rng_cuda'])
            del state; gc.collect()
        start=time.time(); initial=updates; last={}
        print('TRAIN',candidate,updates,'->',target,flush=True)
        while updates<target:
            index=int(np.random.RandomState(SEED+attempts).randint(len(self.train_data)))
            last=self._step(model,opt,scaler,index); attempts+=1
            if last['updated']: updates+=1
            elif attempts-updates>100: raise RuntimeError('Too many skipped FP16 steps')
            if last['updated'] and (updates%25==0 or updates<=initial+2):
                print(candidate,'step',updates,'noise',round(last['noise'],5),'rec',round(last['reconstruction'],5),
                      'sec/update',round((time.time()-start)/max(1,updates-initial),2),flush=True)
            if last['updated'] and (updates%100==0 or updates==target):
                state=dict(candidate=candidate,architecture=asdict(ARCH),updates=updates,attempts=attempts,
                    model=model.state_dict(),optimizer=opt.state_dict(),scaler=scaler.state_dict(),
                    cdl_sha256=self.cdl_hash,scale=self.scale,rng_cpu=torch.get_rng_state(),
                    rng_cuda=torch.cuda.get_rng_state_all(),train_index_hash=self.protocol['train_index_hash'])
                ex.checkpoint_write(path,state)
                del state
                ex.json_write(self.root/f'{candidate}_status.json',dict(updates=updates,attempts=attempts,last=last,**memory()))
        del model,opt,scaler; release()
        return updates

    def _read_val(self, case):
        path=self.base/'data/val'/case['file']
        with h5py.File(path,'r') as f:
            assert str(f.attrs['source_sha256'])==self.val_manifest['volumes'][case['file']]['source_sha256']
            image=torch.from_numpy(f['images_complex64'][case['slice']])
        assert image.shape==(320,320) and torch.isfinite(image).all()
        return image[None].cuda()

    def evaluate(self,candidate,split):
        assert split in ('dev','final')
        path=self.root/f'{candidate}.pt'
        checkpoint_hash=ex._file_sha256(path)
        if split=='final':
            selected=json.loads((self.root/'selection.json').read_text())
            assert selected['candidate']==candidate and selected['checkpoint_sha256']==checkpoint_hash
        folder=self.root/'evaluations'/f'{candidate}_{checkpoint_hash[:12]}_{split}'
        folder.mkdir(parents=True,exist_ok=True)
        out=folder/'results.json'
        records=json.loads(out.read_text())['records'] if out.exists() else []
        completed={(r['file'],r['R']) for r in records}
        state=torch.load(path,map_location='cpu',weights_only=False)
        updates=state['updates']
        model=SSDMUNet(ARCH).cuda().eval()
        model.load_state_dict(state['model']); del state; release()
        def predictor(x,t):
            with torch.no_grad(),torch.autocast('cuda',dtype=torch.float16):
                return model(x,t).float()
        for i,case in enumerate(self.protocol[split]):
            for R in (8,16):
                if (case['file'],R) in completed: continue
                mask_seed=SEED+i+(0 if split=='dev' else 1000)
                sampler_seed=mask_seed*100+R
                x=self._read_val(case)
                mask=ex.random_cartesian_mask(320,R,.04,mask_seed).cuda()
                y=mask[:,0]*fft2c(x)
                zf=ifft2c(y)
                with torch.no_grad():
                    anchors=mask*fft2c(ri_to_complex(self.cdl(complex_to_ri(zf)).subspaces))
                seed(sampler_seed); started=time.time()
                with torch.no_grad():
                    recovered,_=sample_ssdm(predictor,y/self.scale,mask,anchors/self.scale,self.betas,
                        SamplerConfig(inference_steps=100,sigma_schedule='paper_literal'))
                recovered=ri_to_complex(recovered)*self.scale
                ref=x.abs()[0].cpu().numpy(); z=zf.abs()[0].cpu().numpy(); rec=recovered.abs()[0].cpu().numpy()
                dc=float((mask[:,0]*fft2c(recovered)-y).norm()/y.norm().clamp_min(1e-12))
                record=dict(**case,R=R,mask_seed=mask_seed,sampler_seed=sampler_seed,
                    zero_filled=ex.metric_values(ref,z),ssdm=ex.metric_values(ref,rec),DC=dc,
                    sampling_seconds=round(time.time()-started,2))
                np.savez_compressed(folder/f'{i:02d}_R{R}.npz',reference=ref,zero_filled=z,ssdm=rec)
                records.append(record)
                ex.json_write(out,dict(candidate=candidate,split=split,updates=updates,checkpoint_sha256=checkpoint_hash,
                    records=records,complete=len(records)==len(self.protocol[split])*2))
                print('EVAL',split,candidate,case['file'],'R',R,'SSDM',record['ssdm'],'ZF',record['zero_filled'],flush=True)
        del model; release()
        result=json.loads(out.read_text())
        assert result['complete']
        result['mean_psnr']=float(np.mean([r['ssdm']['PSNR'] for r in records]))
        ex.json_write(out,result)
        return result

    def tune(self):
        assert (self.root/'memory_preflight.json').exists(), 'Run memory preflight first'
        if (self.root/'selection.json').exists():
            return json.loads((self.root/'selection.json').read_text())
        if (self.root/'tuning.json').exists():
            winner=json.loads((self.root/'tuning.json').read_text())['candidate']
        else:
            results=[]
            for candidate in CANDIDATES:
                self.train(candidate,self.protocol['screen_updates'])
                results.append(self.evaluate(candidate,'dev'))
            winner=max(results,key=lambda r:r['mean_psnr'])['candidate']
            ex.json_write(self.root/'tuning.json',dict(candidate=winner,screening=results,
                rule=self.protocol['selection_metric'],final_data_used=False))
        print('Development-selected learning rate:',CANDIDATES[winner],flush=True)
        self.train(winner,self.protocol['selected_target_updates'])
        # Freeze the candidate and exact checkpoint BEFORE opening final images.
        validation=self.evaluate(winner,'dev')
        selection=dict(candidate=winner,checkpoint_sha256=ex._file_sha256(self.root/f'{winner}.pt'),
            updates=validation['updates'],development=validation,final_data_used=False)
        ex.json_write(self.root/'selection.json',selection)
        return selection

    def final_evaluation(self):
        selection=json.loads((self.root/'selection.json').read_text())
        result=self.evaluate(selection['candidate'],'final')
        ex.json_write(self.root/'final_results.json',result)
        return result

    def report(self):
        import pandas as pd
        result=json.loads((self.root/'final_results.json').read_text())
        assert result['complete']
        rows=[]
        for R in (8,16):
            records=[r for r in result['records'] if r['R']==R]
            for method in ('zero_filled','ssdm'):
                rows.append(dict(R=R,method=method,n=len(records),**{k:float(np.mean([r[method][k] for r in records])) for k in ('PSNR','SSIM','MAE')}))
            delta=np.array([r['ssdm']['PSNR']-r['zero_filled']['PSNR'] for r in records])
            print('R',R,'mean paired PSNR change',round(float(delta.mean()),4),'dB; wins',int((delta>0).sum()),'/',len(delta),flush=True)
        print(pd.DataFrame(rows).to_string(index=False),flush=True)
        print('Reduced-width SSDM; partial CDL and training data. Full paper reproduction: False.',flush=True)
        ex.json_write(self.root/'summary.json',dict(rows=rows,selection=json.loads((self.root/'selection.json').read_text()),protocol=self.protocol))
        return rows

