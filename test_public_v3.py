"""Public deployment smoke test. Synthetic, explicitly excluded from human results."""
import concurrent.futures,json,secrets,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'runtime'
BASE='https://1f615aa6c39a3de9c0.gradio.live'
def req(path,method='GET',body=None,token=None,headers=None):
    h={'Content-Type':'application/json',**(headers or {})}
    if token:h['Authorization']='Bearer '+token
    r=urllib.request.Request(BASE+path,method=method,headers=h,data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(r,timeout=40) as x:return x.status,x.read(),x.headers
health=json.loads(req('/api/health')[1]);assert health['version']=='blender-v3-20260919'
body=dict(language='zh',consent=True,test_mode=True,test_key=(ROOT/'test.key').read_text().strip(),protocol_version='paired-40-v2',request_id=secrets.token_hex(32))
s=json.loads(req('/api/start','POST',body)[1]);assert s['is_test'] and s['version']==health['version']
assert len(s['trials'])==40 and sum(len(t['questions']) for t in s['trials'])==160
assert json.loads(req('/api/start','POST',body)[1])['token']==s['token']
for i,t in enumerate(s['trials']):
    req('/api/answers/'+str(i),'PUT',dict(ratings={q:'na' for q in t['questions']},watched=[True,True],coverage=[1,1],elapsed=10),s['token'])
done=json.loads(req('/api/submit','POST',token=s['token'])[1])
assert json.loads(req('/api/submit','POST',token=s['token'])[1])==done
assert len(json.loads(req('/api/session',token=s['token'])[1])['answers'])==40
catalog=json.loads((ROOT/'catalog.json').read_text())
ids=[m['media_id'] for s in catalog['samples'] for m in s['methods'].values()]
def check(mid):
    status,data,h=req('/media/'+mid,headers={'Range':'bytes=0-1023'})
    assert status==206 and len(data)==1024 and h['Content-Type']=='video/mp4'
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(check,ids))
print(json.dumps(dict(status='PASS',version=health['version'],public_media_range_checks=len(ids),test_only_complete_submissions=1,answers=40,judgments=160)))
