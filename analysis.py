"""Private analysis of reviewed human responses, separated by protocol/stimuli."""
import collections,json,sqlite3
import numpy as np

def export(data,resamples=2000):
 c=sqlite3.connect(data/'responses.sqlite3');c.row_factory=sqlite3.Row
 rows=[];coverage=collections.Counter();progress=[];seen=set()
 for s in c.execute('SELECT * FROM sessions').fetchall():
  plan=json.loads(s['plan']);answers=c.execute('SELECT * FROM answers WHERE session_id=? ORDER BY idx',(s['id'],)).fetchall()
  order='>'.join([plan[0]['key'].rsplit(':',1)[1],plan[20]['key'].rsplit(':',1)[1]])
  progress.append(dict(participant_id=s['id'],protocol_version=s['protocol_version'],stimulus_version=s['stimulus_version'],is_test=bool(s['is_test']),submitted=s['submitted'] is not None,eligibility_status=s['eligibility_status'],answered_trials=len(answers),completion_seconds=s['submitted']-s['created'] if s['submitted'] else None,task_order=order))
  if s['is_test'] or s['submitted'] is None or s['eligibility_status']!='valid':continue
  if len(answers)!=40:raise ValueError('Submitted response is incomplete')
  for a in answers:
   t=plan[a['idx']];sample,mode=t['key'].rsplit(':',1);baseline=next(m for m in t['methods'] if m!='mainline');side='A' if t['methods'][0]=='mainline' else 'B'
   coverage[(s['protocol_version'],s['stimulus_version'],mode,sample,baseline,side,order)]+=1
   cov=json.loads(a['coverage']) if a['coverage'] else None
   for criterion,value in json.loads(a['ratings']).items():
    unique=(s['id'],mode,sample,criterion)
    if unique in seen:raise ValueError('Duplicate participant/task/source/criterion')
    seen.add(unique)
    outcome='U' if value=='na' else 'T' if value=='0' else 'W' if t['methods'][0 if int(value)<0 else 1]=='mainline' else 'L'
    rows.append(dict(protocol_version=s['protocol_version'],stimulus_version=s['stimulus_version'],participant_id=s['id'],assignment_slot=s['assignment_slot'],task_order=order,task=mode,trial_order=a['idx']+1,source_id=sample,source_video_id=sample.rsplit('_',3)[0],baseline_id=baseline,storymotion_side=side,criterion=criterion,response=value,outcome=outcome,watch_coverage_A=cov[0] if cov else None,watch_coverage_B=cov[1] if cov else None,response_time=a['elapsed'],submitted=True,is_test=False,eligibility_status='valid'))
 groups=collections.defaultdict(list)
 for r in rows:groups[(r['protocol_version'],r['stimulus_version'],r['task'],r['baseline_id'],r['criterion'])].append(r)
 rng=np.random.default_rng(1709);summary=[]
 for key,rs in sorted(groups.items()):
  counts=collections.Counter(r['outcome'] for r in rs);n=sum(counts[k] for k in 'WTL');valid=[r for r in rs if r['outcome']!='U']
  pi={v:i for i,v in enumerate(sorted({r['participant_id'] for r in rs}))};si={v:i for i,v in enumerate(sorted({r['source_video_id'] for r in rs}))};ci=None
  if n and len(pi)>1 and len(si)>1:
   pidx=np.array([pi[r['participant_id']] for r in valid]);sidx=np.array([si[r['source_video_id']] for r in valid]);scores=np.array([{'W':1.,'T':.5,'L':0.}[r['outcome']] for r in valid]);boot=[]
   for _ in range(resamples):
    pw=rng.multinomial(len(pi),np.full(len(pi),1/len(pi)));sw=rng.multinomial(len(si),np.full(len(si),1/len(si)));w=pw[pidx]*sw[sidx]
    if w.sum():boot.append(float(np.dot(w,scores)/w.sum()))
   if boot:ci=np.quantile(boot,[.025,.975]).tolist()
  row=dict(zip(['protocol_version','stimulus_version','task','baseline_id','criterion'],key))
  row.update(valid_comparisons=n,participants=len(pi),source_clips=len({r['source_id'] for r in rs}),source_videos=len(si),W=counts['W'],T=counts['T'],L=counts['L'],NA=counts['U'],NA_fraction=counts['U']/len(rs),win_fraction=counts['W']/n if n else None,tie_fraction=counts['T']/n if n else None,loss_fraction=counts['L']/n if n else None,preference_including_ties=(counts['W']+.5*counts['T'])/n if n else None,conditional_win_excluding_ties=counts['W']/(counts['W']+counts['L']) if counts['W']+counts['L'] else None,preference_ci95=ci,raw_preference_counts=dict(collections.Counter('NA' if r['outcome']=='U' else 'equal' if r['outcome']=='T' else ('much_' if abs(int(r['response']))==2 else 'slightly_')+('win' if r['outcome']=='W' else 'loss') for r in rs)))
  summary.append(row)
 out=data/'exports';out.mkdir(exist_ok=True)
 # Explicit zero cells make missing completed coverage visible.
 catalog=json.loads((data/'catalog.json').read_text())
 versions={(s['protocol_version'],s['stimulus_version']) for s in progress}
 for protocol,stimulus in versions:
  if stimulus!=catalog['version']:continue
  for s in catalog['samples']:
   for m in s['methods']:
    if m=='mainline':continue
    for side in ['A','B']:
     for order in ['given>joint','joint>given']:coverage.setdefault((protocol,stimulus,s['mode'],s['id'],m,side,order),0)
 payloads={'responses':rows,'coverage':[dict(zip(['protocol_version','stimulus_version','task','source_id','baseline_id','storymotion_side','task_order'],k),completed_comparisons=v) for k,v in sorted(coverage.items())],'session_progress':progress,'summary':{'valid_human_participants':sum(not r['is_test'] and r['submitted'] and r['eligibility_status']=='valid' for r in progress),'pending_review_submissions':sum(not r['is_test'] and r['submitted'] and r['eligibility_status']=='pending_review' for r in progress),'bootstrap_resamples':resamples,'interval_method':'participant x source-video crossed bootstrap, product multiplicities, separated by protocol and stimulus','preferences':summary}}
 for name,obj in payloads.items():(out/(name+'.json')).write_text(json.dumps(obj,indent=2,ensure_ascii=False))
 lines=['# User study results','', '| Protocol | Stimulus | Task | Baseline | Criterion | N | W | T | L | NA | Preference | 95% CI |','|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|']
 for r in summary:
  p=r['preference_including_ties'];ci=r['preference_ci95'];vals=[r[k] for k in ['protocol_version','stimulus_version','task','baseline_id','criterion','valid_comparisons','W','T','L','NA']]+[f'{p:.3f}' if p is not None else '—',f'{ci[0]:.3f}–{ci[1]:.3f}' if ci else '—'];lines.append('| '+' | '.join(map(str,vals))+' |')
 if not summary:lines+=['','No reviewed, completed human responses are available.']
 lines+=['','Preference = (W + 0.5 T)/(W + T + L). NA is separate. Intervals account for participant and source-video clustering, not selection bias or independent training seeds. Results describe this manually selected cohort.']
 (out/'RESULTS.md').write_text('\n'.join(lines))
 return payloads
