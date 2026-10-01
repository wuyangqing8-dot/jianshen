"""CSV columns: system_score,expert_score. No fabricated training data."""
import argparse,csv,json
import numpy as np

def ranks(a):
    order=np.argsort(a);out=np.empty(len(a),float);i=0
    while i<len(a):
        j=i+1
        while j<len(a) and a[order[j]]==a[order[i]]:j+=1
        out[order[i:j]]=(i+j-1)/2;i=j
    return out

def evaluate(a,b):
    a,b=np.asarray(a,float),np.asarray(b,float)
    if len(a)<2 or a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('Need at least two finite paired scores')
    corr=lambda x,y:float(np.corrcoef(x,y)[0,1]) if np.std(x)>0 and np.std(y)>0 else None
    return dict(n=len(a),pearson=corr(a,b),spearman=corr(ranks(a),ranks(b)),mae=float(np.mean(abs(a-b))),rmse=float(np.sqrt(np.mean((a-b)**2))))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv');args=p.parse_args()
    with open(args.csv,encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    print(json.dumps(evaluate([r['system_score'] for r in rows],[r['expert_score'] for r in rows]),indent=2))
