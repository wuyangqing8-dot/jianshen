"""Phase event CSV columns: state,time_seconds, separately for truth and predicted."""
import argparse,csv,json
from evaluate_reps import evaluate

def analyze(truth,predicted,tolerance=.3):
    names=sorted(set(r['state'] for r in truth)|set(r['state'] for r in predicted))
    return {name:evaluate([float(r['time_seconds']) for r in truth if r['state']==name],[float(r['time_seconds']) for r in predicted if r['state']==name],tolerance) for name in names}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('truth');p.add_argument('predicted');p.add_argument('--tolerance',type=float,default=.3);a=p.parse_args()
    with open(a.truth,encoding='utf-8-sig') as f:truth=list(csv.DictReader(f))
    with open(a.predicted,encoding='utf-8-sig') as f:pred=list(csv.DictReader(f))
    print(json.dumps(analyze(truth,pred,a.tolerance),indent=2))
