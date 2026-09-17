"""Private CLI; exports only reviewed, completed human responses."""
import argparse,json
from pathlib import Path
from analysis import export
p=argparse.ArgumentParser()
p.add_argument('--data',type=Path,default=Path(__file__).resolve().parent/'runtime')
p.add_argument('--resamples',type=int,default=2000)
a=p.parse_args()
result=export(a.data,a.resamples)
print(json.dumps({k:v for k,v in result['summary'].items() if k!='preferences'},indent=2))
