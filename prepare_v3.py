"""Package author-approved Blender views, preserving frames and anonymous display."""
import concurrent.futures,json,secrets,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]/'blender_render/user_study'
OUT=ROOT/'runtime'; (OUT/'blind_media').mkdir(parents=True,exist_ok=True)
sources=json.loads((BASE/'inputs/render_manifest.json').read_text())['samples']
records=json.loads((BASE/'v3/delivery_manifest.json').read_text())['records']
catalog={'version':'blender-v3-20260919','approval':'Author approved all renders on 2026-09-19','samples':[]}
for s in sources:
    matches=[r for r in records if (r['mode'],r['sample_id'])==(s['mode'],s['sample_id'])]
    assert len(matches)==(4 if s['mode']=='given' else 3)
    catalog['samples'].append(dict(id=s['sample_id'],mode=s['mode'],source_video_id=s['source_video_id'],human_text=s['human_text'],camera_text=s['camera_text'],duration=s['duration_seconds'],methods={r['method']:{'media_id':secrets.token_hex(16)} for r in matches}))
def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(p)]))['streams'][0]
def work(r):
    s=next(s for s in catalog['samples'] if (s['mode'],s['id'])==(r['mode'],r['sample_id']))
    target=OUT/'blind_media'/(s['methods'][r['method']]['media_id']+'.mp4')
    inputs=[Path(r['views'][v]) for v in ['camera','spatial']]
    a,b=map(probe,inputs)
    for key in ['width','height','nb_frames','avg_frame_rate']:
        assert a[key]==b[key],(inputs,key)
    cmd=['ffmpeg','-v','error','-y','-i',str(inputs[0]),'-i',str(inputs[1]),'-filter_complex','[0:v][1:v]vstack=inputs=2,setsar=1','-an','-map_metadata','-1','-c:v','libx264','-threads','2','-preset','slow','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    subprocess.run(cmd,check=True)
    c=probe(target)
    assert c['nb_frames']==a['nb_frames'] and c['avg_frame_rate']==a['avg_frame_rate'] and c['width']==a['width'] and c['height']==2*a['height']
    assert c['codec_name']=='h264' and c['pix_fmt']=='yuv420p'
    subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
    return dict(mode=r['mode'],sample=r['sample_id'],method=r['method'],bytes=target.stat().st_size,frames=int(c['nb_frames']),width=c['width'],height=c['height'],command=cmd,status='PASS')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    audit=[]
    for row in pool.map(work,records):
        audit.append(row); print('Packaged',len(audit),'/140',flush=True)
assert len(audit)==140
(OUT/'catalog.json').write_text(json.dumps(catalog,indent=2))
(OUT/'v3_media_audit.json').write_text(json.dumps({'status':'PASS','records':audit,'total_bytes':sum(r['bytes'] for r in audit)},indent=2))
