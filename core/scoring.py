import math
class ScoringEngine:
    """Continuous penalties; absent dimensions excluded, never replaced by zero."""
    @staticmethod
    def range_score(value,low,high,slope):
        if value is None or not math.isfinite(value): return None
        return max(0.,100.-slope*max(low-value,0,value-high))
    def evaluate(self,features,rules):
        scores={}; errors=[]; weight=0; total=0
        for name,lo,hi,slope,w,message in rules:
            score=self.range_score(features.get(name),lo,hi,slope)
            if score is None: continue
            scores[name]=round(score,1); total+=w*score; weight+=w
            if score<75: errors.append((score,name,message))
        errors.sort()
        return dict(total_score=round(total/weight,1) if weight else None,dimension_scores=scores,detected_errors=[x[1] for x in errors[:2]],feedback=[x[2] for x in errors[:2]])
