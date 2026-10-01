from collections import deque
import numpy as np
class TemporalFilter:
    def __init__(self,window=5,mode='moving',alpha=.4):
        self.window=window; self.mode=mode; self.alpha=alpha; self.reset()
    def reset(self): self.history={}; self.previous={}
    def update(self,key,value):
        if value is None or not np.isfinite(value).all():
            self.history.pop(key,None); self.previous.pop(key,None); return None
        v=np.asarray(value,dtype=float)
        if self.mode=='ema':
            result=v if key not in self.previous else self.alpha*v+(1-self.alpha)*self.previous[key]
            self.previous[key]=result
        else:
            q=self.history.setdefault(key,deque(maxlen=self.window)); q.append(v); result=np.mean(q,axis=0)
        return float(result) if result.ndim==0 else result
    def pose(self,keypoints,threshold):
        out=keypoints.copy()
        for i,p in enumerate(out):
            xy=self.update(i,p[:2] if p[2]>=threshold else None)
            if xy is not None: out[i,:2]=xy
        return out
