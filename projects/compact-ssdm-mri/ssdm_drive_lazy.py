"""Manifest-indexed Drive access; validate each used cache header on read.

Avoid opening all 509 HDF5 files during each dataset construction. This is an
I/O-only adapter for the explicitly incomplete educational pilot. Manifest
source identities retain the original training provenance; unused file headers
are not freshly verified. No image, training, mask, or sampler math changes.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import h5py
import torch
import ssdm_experiment as e


def manifest(directory):
    root = Path(directory)
    saved = json.loads((root / 'download_manifest.json').read_text())
    files = sorted(root.glob('*.h5'))
    assert sorted(saved['archive_files']) == [p.name for p in files]
    assert saved['cache_schema'] and isinstance(saved['complete_archive'], bool)
    for p in files:
        v = saved['volumes'][p.name]
        assert len(v['source_sha256']) == 64
        assert len(v['source_kspace_shape']) == 3
        assert int(v['slices']) == int(v['source_kspace_shape'][0])
    return saved, files


class ManifestSlices(torch.utils.data.Dataset):
    def __init__(self, directory, training=True, size=320, seed=42, subjects=None):
        self.saved, self.files = manifest(directory)
        self.size, self.index = size, []
        rng = np.random.RandomState(seed)
        selected = self.files if training or subjects is None else [self.files[i] for i in rng.permutation(len(self.files))[:subjects]]
        for p in selected:
            count = int(self.saved['volumes'][p.name]['slices'])
            ids = range(count) if training else [int(rng.randint(count))]
            self.index.extend((p, i) for i in ids)

    def __len__(self):
        return len(self.index)

    def __getitem__(self, index):
        p, i = self.index[index]
        expected = self.saved['volumes'][p.name]
        with h5py.File(p, 'r') as f:
            assert str(f.attrs['ssdm_cache_schema']) == self.saved['cache_schema']
            assert str(f.attrs['source_sha256']) == expected['source_sha256']
            assert list(f.attrs['source_kspace_shape']) == expected['source_kspace_shape']
            images = f['images_complex64']
            assert images.shape == (expected['slices'], self.size, self.size)
            assert images.dtype == np.complex64
            x = torch.from_numpy(images[i])
        assert torch.isfinite(x).all()
        return e.complex_to_ri(x), p.name, i


def provenance(directory, files):
    saved, present = manifest(directory)
    assert [p.name for p in sorted(files)] == [p.name for p in present]
    volumes = [dict(filename=p.name, source_sha256=saved['volumes'][p.name]['source_sha256'],
                    source_kspace_shape=saved['volumes'][p.name]['source_kspace_shape'], storage='cache') for p in present]
    identity = dict(schema='ssdm-data-provenance-v1', cache_schema=saved['cache_schema'], volumes=volumes)
    return hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def inventory(cfg):
    train = ManifestSlices(cfg.train_dir, True, cfg.image_size)
    val = ManifestSlices(cfg.val_dir, False, cfg.image_size, cfg.seed, cfg.evaluation_subjects)
    assert not set(p.name for p in train.files).intersection(p.name for p in val.files)
    identity = lambda ds: hashlib.sha256('\n'.join(f'{p.name}:{i}' for p,i in ds.index).encode()).hexdigest()
    info = dict(train_volumes=len(train.files), train_slices=len(train), validation_volumes=len(val.files),
                evaluation_subjects=len(val), complete_archives=False, image_size=cfg.image_size,
                train_index_hash=identity(train), val_index_hash=identity(val),
                train_provenance_hash=provenance(cfg.train_dir, train.files),
                val_provenance_hash=provenance(cfg.val_dir, val.files), training_uses_validation=False,
                validation_policy='manifest index; cache headers verified lazily for every accessed slice')
    e.json_write(Path(cfg.output_dir)/'data_inventory.json', info)
    print(json.dumps(info, indent=2), flush=True)
    return train, val, info


def install():
    e.FastMRISlices = ManifestSlices
    e._split_provenance = provenance
    e.dataset_inventory = inventory
    print('Drive lazy I/O installed: unchanged model and data order; accessed headers verified.', flush=True)
