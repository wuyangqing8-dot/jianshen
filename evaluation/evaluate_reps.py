"""Event matching with a time tolerance; counts alone do not measure precision."""
import argparse,json

def evaluate(truth,predicted,tolerance=.5):
    # Sorted greedy pairing is maximum-cardinality for fixed symmetric tolerance.
    truth=sorted(truth);predicted=sorted(predicted);i=j=matched=0
    while i<len(truth) and j<len(predicted):
        if abs(truth[i]-predicted[j])<=tolerance:matched+=1;i+=1;j+=1
        elif predicted[j]<truth[i]-tolerance:j+=1
        else:i+=1
    precision=matched/len(predicted) if predicted else None;recall=matched/len(truth) if truth else None
    return dict(ground_truth=len(truth),predicted=len(predicted),tp=matched,fp=len(predicted)-matched,fn=len(truth)-matched,precision=precision,recall=recall,count_absolute_error=abs(len(truth)-len(predicted)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('json');p.add_argument('--tolerance',type=float,default=.5);a=p.parse_args()
    with open(a.json) as f:d=json.load(f)
    print(json.dumps(evaluate(d['truth'],d['predicted'],a.tolerance),indent=2))
