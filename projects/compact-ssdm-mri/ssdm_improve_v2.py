"""Validation-selected compact SSDM extension. Original runs are read-only.
CDL validation uses the existing development volumes, never the new final set.
All budgets and sampler candidates are declared before final evaluation.
"""
import copy, json, shutil, time, os
from pathlib import Path
from dataclasses import asdict
import numpy as np
import torch
import ssdm_experiment as ex
from ssdm_compact import CompactRun, ARCH, SEED, seed, release, memory
from ssdm_backbone import SSDMUNet
from ssdm_cdl import (CoupledDictionary, coupled_dictionary_loss,
                      complex_to_ri, ri_to_complex, fft2c, ifft2c)
from ssdm_sampling import sample_ssdm, SamplerConfig

class LocalVolumes:
    """Demand-only sequential reads avoid Drive FUSE random-read amplification.
    Images are never accumulated in host RAM. 12 GiB bounded local disk cache.
    """
    def __init__(self):
        self.root=Path('/content/ssdm_volume_cache');self.root.mkdir(exist_ok=True)
    def get(self, source):
        dest=self.root/(source.parent.name+'_'+source.name)
        if not dest.exists():
            size=source.stat().st_size
            entries=sorted(self.root.glob('*.h5'),key=lambda p:p.stat().st_mtime)
            total=sum(p.stat().st_size for p in entries)
            while entries and total+size>12*2**30:
                p=entries.pop(0);total-=p.stat().st_size;p.unlink()
            partial=dest.with_suffix('.partial')
            with source.open('rb') as src,partial.open('wb') as out:
                shutil.copyfileobj(src,out,length=1024*1024)
            assert partial.stat().st_size==size
            partial.replace(dest)
            print('LOCAL CACHE',source.name,round(size/2**20,1),'MiB',flush=True)
        os.utime(dest,None)
        return dest

class LocalSlices:
    def __init__(self, original, cache):
        self.original,self.cache=original,cache
        self.index,self.files=original.index,original.files
    def __len__(self):return len(self.original)
    def __getitem__(self,index):
        import h5py
        p,i=self.index[index];expected=self.original.saved['volumes'][p.name]
        with h5py.File(self.cache.get(p),'r') as f:
            assert str(f.attrs['source_sha256'])==expected['source_sha256']
            x=torch.from_numpy(f['images_complex64'][i])
        assert x.shape==(320,320) and torch.isfinite(x).all()
        return complex_to_ri(x),p.name,i


class ImprovementRun(CompactRun):
    def __init__(self, base):
        super().__init__(base)
        self.local_cache=LocalVolumes()
        self.train_data=LocalSlices(self.train_data,self.local_cache)
        self.original_root = self.root
        self.root = self.base/'improve320_v2'
        self.root.mkdir(exist_ok=True)
        self.protocol = copy.deepcopy(self.protocol)
        path = self.root/'plan.json'
        if path.exists():
            self.plan = json.loads(path.read_text())
        else:
            excluded = set(self.protocol['excluded_previously_seen'])
            excluded.update(c['file'] for s in ('dev','final') for c in self.protocol[s])
            names = sorted(p.name for p in self.val_files if p.name not in excluded)
            names = np.random.RandomState(20261024).permutation(names)[:16]
            self.plan = dict(seed=20261024, cdl_extra_updates=1000, cdl_check_every=250,
                cdl_lr=1e-4, cdl_selection='minimum mean coupled CDL validation objective',
                diffusion_targets=[1500,3000,6000], diffusion_lr=3e-4,
                early_stop='two consecutive validation checkpoints without improvement',
                sampler_candidates=[dict(gamma=1.,resample_every=10),
                    dict(gamma=100.,resample_every=10),
                    dict(gamma=10000.,resample_every=10),
                    dict(gamma=10000.,resample_every=1)],
                inference_steps=100, sigma_schedule='paper_literal',
                dev=self.protocol['dev'], excluded_final_files=sorted(excluded),
                final=[dict(file=str(n),slice=int(self.val_manifest['volumes'][n]['slices'])//2) for n in names],
                paper_reproduction=False, full_training=False)
            ex.json_write(path,self.plan)
        assert not set(c['file'] for c in self.plan['final']) & set(self.plan['excluded_final_files'])
        self.protocol['final']=self.plan['final']

    def _read_val(self,case):
        import h5py
        p=self.base/'data/val'/case['file']
        with h5py.File(self.local_cache.get(p),'r') as f:
            assert str(f.attrs['source_sha256'])==self.val_manifest['volumes'][case['file']]['source_sha256']
            image=torch.from_numpy(f['images_complex64'][case['slice']])
        assert image.shape==(320,320) and torch.isfinite(image).all()
        return image[None].cuda()

    @torch.no_grad()
    def cdl_validation(self, model):
        model.eval(); scores=[]; rec=[]
        for i,case in enumerate(self.plan['dev']):
            x=self._read_val(case); xr=complex_to_ri(x)
            for R in (8,16):
                mask=ex.random_cartesian_mask(320,R,.04,SEED+i).cuda()
                y=mask[:,0]*fft2c(x)
                loss,terms,full,under=coupled_dictionary_loss(model,xr,complex_to_ri(ifft2c(y)),y,mask)
                scores.append(float(loss))
                rec.append(float((full.reconstruction-xr).norm()/xr.norm()))
        return dict(objective=float(np.mean(scores)),relative_reconstruction_error=float(np.mean(rec)))

    def refine_cdl(self):
        selected=self.root/'cdl_selection.json'
        if selected.exists():
            return json.loads(selected.read_text())
        latest=self.root/'cdl_latest.pt'; best=self.root/'cdl_best.pt'
        model=CoupledDictionary().cuda().train()
        opt=torch.optim.Adam(model.parameters(),lr=self.plan['cdl_lr'],foreach=False)
        done=0; seed(20261024)
        if latest.exists():
            s=torch.load(latest,map_location='cpu',weights_only=False)
            model.load_state_dict(s['model']);opt.load_state_dict(s['optimizer']);done=s['extra_updates']
            torch.set_rng_state(s['rng_cpu']);torch.cuda.set_rng_state_all(s['rng_cuda']);del s
            history=json.loads((self.root/'cdl_history.json').read_text())
        else:
            model.load_state_dict(self.cdl.state_dict())
            initial=self.cdl_validation(model)
            history=[dict(extra_updates=0,**initial)]
            ex.checkpoint_write(best,dict(model=model.state_dict(),extra_updates=0))
            ex.json_write(self.root/'cdl_history.json',history)
            print('CDL BASELINE',initial,flush=True)
        start=time.time()
        for update in range(done+1,self.plan['cdl_extra_updates']+1):
            model.train()
            index=int(np.random.RandomState(20261024+update).randint(len(self.train_data)))
            x,_,_=self.train_data[index];x=x[None].cuda()
            mask=ex.random_cartesian_mask(320,(8,16)[update%2],.04,20261024+update).cuda()
            y=mask[:,0]*fft2c(ri_to_complex(x))
            opt.zero_grad(set_to_none=True)
            loss,terms,_,_=coupled_dictionary_loss(model,x,complex_to_ri(ifft2c(y)),y,mask)
            assert torch.isfinite(loss)
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step()
            if update%25==0:
                print('CDL extra',update,'loss',round(float(loss.detach()),6),'seconds',round(time.time()-start),flush=True)
            if update%self.plan['cdl_check_every']==0:
                score=self.cdl_validation(model)
                if score['objective'] < min(h['objective'] for h in history):
                    ex.checkpoint_write(best,dict(model=model.state_dict(),extra_updates=update))
                history.append(dict(extra_updates=update,**score))
                ex.json_write(self.root/'cdl_history.json',history)
                ex.checkpoint_write(latest,dict(model=model.state_dict(),optimizer=opt.state_dict(),extra_updates=update,
                    rng_cpu=torch.get_rng_state(),rng_cuda=torch.cuda.get_rng_state_all()))
                print('CDL VALIDATION',history[-1],flush=True)
        result=min(history,key=lambda h:h['objective'])
        result=dict(result,checkpoint_sha256=ex._file_sha256(best),source_sha256=self.cdl_hash)
        ex.json_write(selected,result)
        del model,opt;release()
        print('CDL SELECTED',result,flush=True)
        return result

    def prepare_diffusion(self):
        choice=json.loads((self.root/'cdl_selection.json').read_text())
        self.cdl_path=self.root/'cdl_best.pt'
        assert ex._file_sha256(self.cdl_path)==choice['checkpoint_sha256']
        s=torch.load(self.cdl_path,map_location='cpu',weights_only=False)
        self.cdl.load_state_dict(s['model']);del s
        self.cdl.eval().requires_grad_(False)
        self.cdl_hash=choice['checkpoint_sha256']
        protocol_path=self.root/'protocol.json'
        if protocol_path.exists():
            self.protocol=json.loads(protocol_path.read_text())
            assert self.protocol['cdl_sha256']==self.cdl_hash
            self.scale=self.protocol['component_scale']
        else:
            self.protocol.update(cdl_sha256=self.cdl_hash,cdl_updates=1600+choice['extra_updates'],
                cdl_completed=False,component_scale=None,final=self.plan['final'],plan=self.plan)
            self.scale=None;self.calibrate()
        # Restart for changed component targets. An unchanged CDL may reuse its model.
        dst=self.root/'lr3e-4.pt'
        if choice['extra_updates']==0 and not dst.exists():
            s=torch.load(self.original_root/'lr3e-4.pt',map_location='cpu',weights_only=False)
            assert abs(s['scale']-self.scale)<1e-8
            s['cdl_sha256']=self.cdl_hash
            ex.checkpoint_write(dst,s);del s;release()
        print('DIFFUSION READY CDL extra',choice['extra_updates'],'scale',self.scale,flush=True)

    def evaluate_variant(self, model_path, sampler, split, tag):
        assert split in ('dev','final')
        model_hash=ex._file_sha256(model_path)
        folder=self.root/'evaluations'/f'{model_hash[:12]}_{tag}_{split}'
        folder.mkdir(parents=True,exist_ok=True)
        out=folder/'results.json'
        if out.exists():
            data=json.loads(out.read_text());records=data['records']
            assert data['sampler']==asdict(sampler)
        else: records=[]
        completed={(r['file'],r['R']) for r in records}
        model=SSDMUNet(ARCH).cuda().eval()
        s=torch.load(model_path,map_location='cpu',weights_only=False)
        assert s['cdl_sha256']==self.cdl_hash and s['scale']==self.scale
        model.load_state_dict(s['model']);updates=s['updates'];del s;release()
        def predictor(x,t):
            with torch.no_grad(),torch.autocast('cuda',dtype=torch.float16):
                return model(x,t).float()
        for i,case in enumerate(self.protocol[split]):
            for R in (8,16):
                if (case['file'],R) in completed:continue
                mask_seed=SEED+i+(0 if split=='dev' else 2000)
                x=self._read_val(case)
                mask=ex.random_cartesian_mask(320,R,.04,mask_seed).cuda()
                y=mask[:,0]*fft2c(x);zf=ifft2c(y)
                with torch.no_grad():
                    anchors=mask*fft2c(ri_to_complex(self.cdl(complex_to_ri(zf)).subspaces))
                    seed(mask_seed*100+R)
                    rec,_=sample_ssdm(predictor,y/self.scale,mask,anchors/self.scale,self.betas,sampler)
                    rec=ri_to_complex(rec)*self.scale
                dc=float((mask[:,0]*fft2c(rec)-y).norm()/y.norm().clamp_min(1e-12))
                assert dc<1e-4, f'Data consistency failed: {dc}'
                ref=x.abs()[0].cpu().numpy();z=zf.abs()[0].cpu().numpy();r=rec.abs()[0].cpu().numpy()
                row=dict(**case,R=R,zero_filled=ex.metric_values(ref,z),ssdm=ex.metric_values(ref,r),DC=dc)
                records.append(row)
                np.savez_compressed(folder/f'{i:02d}_R{R}.npz',reference=ref,zero_filled=z,ssdm=r)
                data=dict(records=records,sampler=asdict(sampler),updates=updates,checkpoint_sha256=model_hash,
                    complete=len(records)==len(self.protocol[split])*2)
                ex.json_write(out,data)
                print('V2 EVAL',split,tag,updates,case['file'],R,'deltaPSNR',round(row['ssdm']['PSNR']-row['zero_filled']['PSNR'],3),flush=True)
        del model;release()
        data=json.loads(out.read_text());data['mean_psnr']=float(np.mean([r['ssdm']['PSNR'] for r in records]))
        ex.json_write(out,data);return data

    def train_and_select(self):
        if (self.root/'selection.json').exists():return json.loads((self.root/'selection.json').read_text())
        self.prepare_diffusion()
        path=self.root/'training_history.json'
        history=json.loads(path.read_text()) if path.exists() else []
        stale=0
        for a,b in zip(history,history[1:]):
            stale=stale+1 if b['mean_psnr']<=max(h['mean_psnr'] for h in history if h['updates']<b['updates']) else 0
        for target in self.plan['diffusion_targets']:
            if any(h['updates']==target for h in history):continue
            if stale>=2:break
            self.train('lr3e-4',target)
            result=self.evaluate_variant(self.root/'lr3e-4.pt',SamplerConfig(),'dev','default')
            better=not history or result['mean_psnr']>max(h['mean_psnr'] for h in history)
            if better:shutil.copyfile(self.root/'lr3e-4.pt',self.root/'diffusion_best.pt')
            stale=0 if better else stale+1
            history.append(result);ex.json_write(path,history)
            print('DIFFUSION VALIDATION',target,result['mean_psnr'],'best',better,flush=True)
        candidates=[]
        for i,params in enumerate(self.plan['sampler_candidates']):
            config=SamplerConfig(**params)
            result=self.evaluate_variant(self.root/'diffusion_best.pt',config,'dev',f'sampler{i}')
            candidates.append(dict(tag=f'sampler{i}',sampler=asdict(config),mean_psnr=result['mean_psnr']))
        best=max(candidates,key=lambda r:r['mean_psnr'])
        selection=dict(**best,checkpoint_sha256=ex._file_sha256(self.root/'diffusion_best.pt'),
            cdl_sha256=self.cdl_hash,candidates=candidates,final_data_used=False)
        ex.json_write(self.root/'selection.json',selection)
        print('FROZEN SELECTION',selection,flush=True);return selection

    def final_v2(self):
        self.prepare_diffusion()
        selection=json.loads((self.root/'selection.json').read_text())
        assert ex._file_sha256(self.root/'diffusion_best.pt')==selection['checkpoint_sha256']
        result=self.evaluate_variant(self.root/'diffusion_best.pt',SamplerConfig(**selection['sampler']),'final',selection['tag'])
        ex.json_write(self.root/'final_results.json',result)
        rows=[]
        for R in (8,16):
            rr=[r for r in result['records'] if r['R']==R]
            for method in ('zero_filled','ssdm'):
                rows.append(dict(R=R,method=method,n=len(rr),**{k:float(np.mean([r[method][k] for r in rr])) for k in ('PSNR','SSIM','MAE')}))
            delta=np.array([r['ssdm']['PSNR']-r['zero_filled']['PSNR'] for r in rr])
            print('FINAL',R,'paired PSNR delta',float(delta.mean()),'wins',int((delta>0).sum()),'/',len(rr),flush=True)
        ex.json_write(self.root/'summary.json',dict(rows=rows,selection=selection,plan=self.plan))
        import pandas as pd
        print(pd.DataFrame(rows).to_string(index=False),flush=True)
        return rows

    def execute(self):
        self.refine_cdl()
        self.train_and_select()
        return self.final_v2()
