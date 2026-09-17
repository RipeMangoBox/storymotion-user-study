"""Run on the study host. All created sessions are explicitly test sessions."""
import concurrent.futures, json, os, urllib.request, urllib.error
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parent/'runtime'
key=(root/'test.key').read_text().strip()
base='http://127.0.0.1:7898'
def request(path,method='GET',body=None,token=None,headers=None):
    h={'Content-Type':'application/json',**(headers or {})}
    if token:h['Authorization']='Bearer '+token
    req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=h,method=method)
    try:
        with urllib.request.urlopen(req,timeout=20) as r:return r.status,r.read(),r.headers
    except urllib.error.HTTPError as e:return e.code,e.read(),e.headers
assert request('/api/session')[0]==401
assert request('/api/start','POST',{'language':'en','consent':False})[0]==400
sessions=[]
for _ in range(6):
    code,data,_=request('/api/start','POST',{'language':'en','consent':True,'test_key':key})
    assert code==200
    session=json.loads(data);sessions.append(session)
    assert session['is_test'] and len(session['trials'])==40
    assert [r['mode'] for r in session['trials']]==['given']*20+['joint']*20
    assert 'mainline' not in data.decode() and 'pulp_dit' not in data.decode()
token=sessions[0]['token']
assert request('/api/submit','POST',token=token)[0]==400
assert request('/api/answers/0','PUT',{'ratings':{},'watched':[True,True],'elapsed':1},token)[0]==400
assert request('/api/answers/40','PUT',{'ratings':{},'watched':[True,True],'elapsed':1},token)[0]==400
assert request('/api/answers/0','PUT',{'ratings':{q:'0' for q in sessions[0]['trials'][0]['questions']},'watched':[False,False],'elapsed':1},token)[0]==400
catalog=json.loads((root/'catalog.json').read_text())
media={v['media_id']:m for s in catalog['samples'] for m,v in s['methods'].items()}
for s in sessions:
    for block in [s['trials'][:20],s['trials'][20:]]:
        assert sum(media[t['videos'][0].split('/')[-1]]=='mainline' for t in block)==10
        baseline_counts=Counter()
        for t in block:
            methods=[media[v.split('/')[-1]] for v in t['videos']]
            assert len(set(methods))==2 and 'mainline' in methods and 'gt' not in methods
            baseline_counts.update(m for m in methods if m!='mainline')
        assert max(baseline_counts.values())-min(baseline_counts.values())<=1
def check_media(mid):
    code,data,h=request('/media/'+mid,headers={'Range':'bytes=0-1023'})
    assert code==206 and len(data)==1024 and h.get('Content-Type')=='video/mp4'
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(check_media,media))
assert request('/runtime/responses.sqlite3')[0]==404
assert request('/media/not-in-catalog')[0]==404
print(json.dumps({'passed':True,'test_sessions':6,'media_range_checks':len(media),'auth_validation_incomplete_submission_and_balance_checks':True}))
