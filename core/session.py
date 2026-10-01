from collections import Counter
class TrainingSession:
    def __init__(self,idle_seconds=12): self.idle_seconds=idle_seconds; self.reset()
    def reset(self): self.sets=[]; self.current=[]; self.start=None; self.last_activity=None
    def add(self,result,t):
        if self.start is None: self.start=t-result.get('duration',0)
        self.current.append(result); self.last_activity=t
    def finish(self,t):
        if not self.current:return None
        scores=[x['total_score'] for x in self.current if x.get('total_score') is not None]
        errors=Counter(e for x in self.current for e in x.get('detected_errors',[]))
        row=dict(set=len(self.sets)+1,reps=len(self.current),duration=round((self.last_activity or t)-self.start,2),average_score=round(sum(scores)/len(scores),1) if scores else None,best_score=max(scores) if scores else None,worst_score=min(scores) if scores else None,main_error=errors.most_common(1)[0][0] if errors else None)
        self.sets.append(row); self.current=[]; self.start=None; self.last_activity=None; return row
    def idle(self,t,resting):
        if resting and self.last_activity is not None and t-self.last_activity>=self.idle_seconds:return self.finish(t)
