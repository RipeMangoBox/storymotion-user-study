"""Isolated synthetic tests; never reads or modifies respondent databases."""
import collections,json,os,random,shutil,tempfile
from pathlib import Path
from fastapi.testclient import TestClient

with tempfile.TemporaryDirectory(prefix='study-v2-test-') as tmp:
 data=Path(tmp);shutil.copyfile(Path(__file__).parent/'runtime/catalog.json',data/'catalog.json')
 os.environ['STUDY_DATA']=str(data);os.environ['STUDY_TEST_KEY']='isolated-test-key'
 import server
 from analysis import export
 client=TestClient(server.app)
 sessions=[];cells=collections.Counter();starts=[]
 assert client.post('/api/start',json={'language':'en','consent':True,'protocol_version':'paired-40-v2','test_mode':True}).status_code==403
 for i in range(48):
  request={'language':'en','consent':True,'protocol_version':'paired-40-v2','test_mode':True,'test_key':'isolated-test-key','request_id':f'{i:064x}'}
  r=client.post('/api/start',json=request);assert r.status_code==200,r.text
  s=r.json();sessions.append(s);assert s['is_test'] and s['protocol_version']=='paired-40-v2'
  assert client.post('/api/start',json=request).json()['token']==s['token']
 with server.connect() as c:
  stored=c.execute('SELECT * FROM sessions').fetchall();assert len(stored)==48
  assert len({s['assignment_slot'] for s in stored})==48
  for s in stored:
   plan=json.loads(s['plan']);order=plan[0]['key'].rsplit(':',1)[1];starts.append(order)
   for block in [plan[:20],plan[20:]]:
    assert sum(t['methods'][0]=='mainline' for t in block)==10
    assert len({t['key'].rsplit(':',1)[1] for t in block})==1
    for t in block:
     mode=t['key'].rsplit(':',1)[1];baseline=next(m for m in t['methods'] if m!='mainline')
     cells[(mode,t['key'],baseline,t['methods'][0]=='mainline',order)]+=1
 assert collections.Counter(starts)=={'given':24,'joint':24}
 assert all(v==(2 if k[0]=='given' else 6) for k,v in cells.items())
 # Cached v1 frontend keeps given-first order and its original answer schema.
 legacy=client.post('/api/start',json={'language':'en','consent':True,'test_key':'isolated-test-key'}).json()
 assert legacy['protocol_version']=='paired-40-v1'
 assert [t['mode'] for t in legacy['trials']]==['given']*20+['joint']*20
 assert client.put('/api/answers/0',headers={'Authorization':'Bearer '+legacy['token']},json={'ratings':{q:'0' for q in legacy['trials'][0]['questions']},'watched':[True,True],'elapsed':5}).status_code==200
 for s in sessions[:2]:
  headers={'Authorization':'Bearer '+s['token']}
  assert client.post('/api/submit',headers=headers).status_code==400
  for i,t in enumerate(s['trials']):
   body={'ratings':{q:'0' for q in t['questions']},'watched':[True,True],'coverage':[1.,1.],'elapsed':5}
   if i==0:
    bad={**body,'coverage':[.89,1.]};assert client.put('/api/answers/0',json=bad,headers=headers).status_code==400
   r=client.put(f'/api/answers/{i}',json=body,headers=headers);assert r.status_code==200,r.text
  receipt=client.post('/api/submit',headers=headers).json()['receipt']
  assert client.post('/api/submit',headers=headers).json()['receipt']==receipt
  assert len(client.get('/api/session',headers=headers).json()['answers'])==40
 assert export(data,50)['summary']['valid_human_participants']==0
 # Synthetic only: exercise analysis with two eligible rows, then exclusions.
 with server.connect() as c:c.execute("UPDATE sessions SET is_test=0,eligibility_status='valid' WHERE submitted IS NOT NULL")
 result=export(data,100);assert result['summary']['valid_human_participants']==2
 assert len(result['responses'])==320
 assert all(r['preference_including_ties']==.5 and r['conditional_win_excluding_ties'] is None for r in result['summary']['preferences'])
 with server.connect() as c:c.execute("UPDATE answers SET ratings=replace(ratings, '\"0\"', '\"na\"')")
 result=export(data,50)
 assert all(r['preference_including_ties'] is None and r['NA_fraction']==1 for r in result['summary']['preferences'])
 assert all(not any(r['valid_by_criterion'].values()) for r in result['coverage'])
 print(json.dumps({'passed':True,'slots':48,'task_order':[24,24],'complete_test_sessions':2,'paired_cells':len(cells),'checks':['idempotent start','coverage gate','complete-only submission','idempotent submit','test exclusion','pending review exclusion','ties','NA','zero coverage cells']}))
