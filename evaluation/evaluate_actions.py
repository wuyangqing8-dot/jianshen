"""Evaluate labeled exercise clips with abstention. CSV: truth,predicted columns."""
import argparse,csv,json
from collections import Counter
from pathlib import Path

def evaluate(rows):
    rows=list(rows)
    if not rows:raise ValueError('Empty labeled set')
    labels=sorted({r['truth'] for r in rows})
    if 'unknown' in labels:raise ValueError('Use a known ground-truth exercise; predicted may be unknown')
    detail={}
    for label in labels:
        tp=sum(r['truth']==label and r['predicted']==label for r in rows)
        fp=sum(r['truth']!=label and r['predicted']==label for r in rows)
        fn=sum(r['truth']==label and r['predicted']!=label for r in rows)
        precision=tp/(tp+fp) if tp+fp else None
        recall=tp/(tp+fn) if tp+fn else None
        detail[label]=dict(tp=tp,fp=fp,fn=fn,precision=precision,recall=recall,f1=(2*precision*recall/(precision+recall)) if precision is not None and recall is not None and precision+recall else None)
    classified=sum(r['predicted']!='unknown' for r in rows)
    correct=sum(r['truth']==r['predicted'] for r in rows)
    return dict(n=len(rows),coverage=classified/len(rows),correct_on_all=correct/len(rows),accuracy_when_classified=correct/classified if classified else None,by_exercise=detail,confusion={a:dict(Counter(r['predicted'] for r in rows if r['truth']==a)) for a in labels})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv');a=p.parse_args()
    with open(a.csv,encoding='utf-8-sig') as f:print(json.dumps(evaluate(csv.DictReader(f)),ensure_ascii=False,indent=2))
