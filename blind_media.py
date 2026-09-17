"""Create separate blind stimuli, masking only the existing 24px label strip."""
import concurrent.futures, hashlib, json, os, subprocess
from pathlib import Path
root=Path(__file__).resolve().parent/'runtime'
catalog=json.loads((root/'catalog.json').read_text())
out=root/'blind_media';out.mkdir(exist_ok=True)
def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(path)]))['streams'][0]
def run(v):
    source=Path(v['path']);target=out/(v['media_id']+'.mp4')
    before=probe(source)
    assert (before['width'],before['height'])==(320,492), before
    command=['ffmpeg','-nostdin','-v','error','-n','-i',str(source),'-map','0:v:0','-vf','drawbox=x=0:y=180:w=iw:h=24:color=white:t=fill','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','1','-an','-map_metadata','-1','-movflags','+faststart',str(target)]
    if not target.exists():subprocess.run(command,check=True)
    after=probe(target)
    for field in ['width','height','nb_frames','avg_frame_rate']:
        assert before.get(field)==after.get(field),(field,before.get(field),after.get(field))
    assert abs(float(before['duration'])-float(after['duration'])) < 0.001
    subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
    return {'media_id':v['media_id'],'source':str(source),'output':str(target),'command':command,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'input_probe':before,'output_probe':after,'bytes':target.stat().st_size}
items=[v for s in catalog['samples'] for v in s['methods'].values()]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(run,items))
(root/'blind_media_acceptance.json').write_text(json.dumps({'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],'count':len(results),'mask':[0,180,320,24],'results':results},indent=2))
print(json.dumps({'videos':len(results),'bytes':sum(x['bytes'] for x in results),'all_probes_and_full_decode_passed':True}))
