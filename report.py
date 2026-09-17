"""Private CLI: export completed real responses and descriptive preferences."""
import argparse, collections, csv, json, sqlite3
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--data',type=Path,default=Path(__file__).resolve().parent/'runtime')
a=p.parse_args()
c=sqlite3.connect(a.data/'responses.sqlite3');c.row_factory=sqlite3.Row
rows=[];counts=collections.defaultdict(collections.Counter)
sessions=c.execute('SELECT * FROM sessions WHERE submitted IS NOT NULL AND is_test=0').fetchall()
for s in sessions:
    plan=json.loads(s['plan'])
    for answer in c.execute('SELECT * FROM answers WHERE session_id=? ORDER BY idx',(s['id'],)):
        trial=plan[answer['idx']];sample,mode=trial['key'].rsplit(':',1)
        baseline=next(m for m in trial['methods'] if m!='mainline')
        for question,value in json.loads(answer['ratings']).items():
            if value=='na': outcome='cannot_judge'
            elif value=='0': outcome='tie'
            else: outcome='storymotion' if trial['methods'][0 if int(value)<0 else 1]=='mainline' else 'baseline'
            counts[(mode,baseline,question)][outcome]+=1
            rows.append({'participant':s['id'],'sample':sample,'mode':mode,'baseline':baseline,'criterion':question,'choice':value,'left':trial['methods'][0],'right':trial['methods'][1],'outcome':outcome,'elapsed_seconds':answer['elapsed']})
out=a.data/'exports';out.mkdir(exist_ok=True)
with (out/'responses.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=['participant','sample','mode','baseline','criterion','choice','left','right','outcome','elapsed_seconds']);w.writeheader();w.writerows(rows)
summary={'completed_participants':len(sessions),'test_sessions_excluded':c.execute('SELECT COUNT(*) FROM sessions WHERE is_test=1').fetchone()[0],'incomplete_sessions_excluded':c.execute('SELECT COUNT(*) FROM sessions WHERE submitted IS NULL AND is_test=0').fetchone()[0],'preferences':[{'mode':k[0],'baseline':k[1],'criterion':k[2],'storymotion_wins':v['storymotion'],'baseline_wins':v['baseline'],'ties':v['tie'],'cannot_judge':v['cannot_judge'],'storymotion_win_fraction_excluding_ties_and_unjudged': v['storymotion']/(v['storymotion']+v['baseline']) if v['storymotion']+v['baseline'] else None} for k,v in sorted(counts.items())], 'interpretation':'Descriptive paired preferences, not independent per-question significance tests. Repeated observations cluster by participant and sample. The cohort was manually selected; do not generalize to the full test set.'}
(out/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
