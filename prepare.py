"""Freeze the selected gallery cohort without editing the original gallery."""
import argparse, json, secrets, subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--gallery', required=True, type=Path)
p.add_argument('--selections', required=True, type=Path)
p.add_argument('--output', default='runtime/catalog.json', type=Path)
a = p.parse_args()
gallery = json.loads(a.gallery.read_text())
catalog = {'version': 'paired-40-v1', 'samples': []}
for mode, group, filename in [('given', 'given_baselines', 'given_h_selected_samples.json'), ('joint', 'pulp', 'full_selected_samples.json')]:
    ids = json.loads((a.selections / filename).read_text())['sample_ids']
    assert len(ids) == len(set(ids)) == 20, (mode, len(ids))
    rows = {r['sample_id']: r for r in gallery[group]}
    for sample_id in ids:
        row = rows[sample_id]
        methods = {}
        for method, arm in row['arms'].items():
            if method == 'gt':
                continue
            path = (Path(arm['root']) / arm['preview_video']).resolve()
            assert path.is_file() and path.stat().st_size > 0, path
            methods[method] = {'path': str(path), 'media_id': secrets.token_hex(16)}
        assert 'mainline' in methods and len(methods) == (7 if mode == 'given' else 3), methods.keys()
        catalog['samples'].append({'id': sample_id, 'mode': mode, 'human_text': row['human_text'], 'camera_text': row['camera_text'], 'duration': row['valid_frames'] / 30, 'methods': methods})
a.output.parent.mkdir(parents=True, exist_ok=True)
assert not a.output.exists(), 'Do not overwrite an active study catalog'
a.output.write_text(json.dumps(catalog, indent=2))
print(json.dumps({'samples': len(catalog['samples']), 'videos': sum(len(r['methods']) for r in catalog['samples']), 'methods': {m: sorted(next(r for r in catalog['samples'] if r['mode'] == m)['methods']) for m in ('given', 'joint')}}))
