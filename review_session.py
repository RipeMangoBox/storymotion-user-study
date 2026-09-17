"""Explicit eligibility review. No exclusions based on method preference."""
import argparse,sqlite3,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path(__file__).resolve().parent/'runtime');p.add_argument('--session',type=int,required=True);p.add_argument('--status',choices=['valid','excluded','pending_review'],required=True);p.add_argument('--reason',required=True)
a=p.parse_args()
with sqlite3.connect(a.data/'responses.sqlite3') as c:
 row=c.execute('SELECT is_test,submitted,eligibility_status FROM sessions WHERE id=?',(a.session,)).fetchone()
 if row is None:raise SystemExit('Unknown session')
 if a.status=='valid' and (row[0] or row[1] is None):raise SystemExit('Test/incomplete sessions cannot be valid human responses')
 c.execute('CREATE TABLE IF NOT EXISTS eligibility_reviews (session_id INTEGER,reviewed REAL,previous TEXT,status TEXT,reason TEXT)')
 c.execute('INSERT INTO eligibility_reviews VALUES(?,?,?,?,?)',(a.session,time.time(),row[2],a.status,a.reason))
 c.execute('UPDATE sessions SET eligibility_status=? WHERE id=?',(a.status,a.session))
print('Eligibility status updated; original answers retained.')
