"""Pose to movement, set statistics, and continuous quality feedback."""
from collections import deque,Counter
import numpy as np
from .filtering import TemporalFilter
from .feature_extractor import extract
from .state_machine import ExerciseStateMachine
from .exercise_rules import RULES
from .scoring import ScoringEngine
from .session import TrainingSession

class ExerciseEngine:
    def __init__(self,exercise='squat',threshold=.45,filter_config=None):
        self.exercise=exercise;self.rule=RULES[exercise];self.threshold=threshold
        self.filter=TemporalFilter(**(filter_config or {}));self.scoring=ScoringEngine();self.session=TrainingSession()
        self.machine=ExerciseStateMachine(self.rule['cycle']) if 'cycle' in self.rule else None
        self.samples=[];self.last_score=None;self.hold=0.;self.quality_hold=0.;self.hold_score_sum=0.;self.hold_score_count=0;self.hold_best=None;self.hold_worst=None;self.hold_errors=Counter();self.last_t=None
        self.last_box=None;self.last_side=None;self.hold_history=deque(maxlen=30);self.partial_feedback=None
    def invalidate(self):
        self.filter.reset();self.samples.clear();self.last_t=None;self.last_side=None;self.last_box=None
        self.hold_history.clear()
        if self.machine:self.machine.reset()
    def finish_set(self,t):
        if self.machine is not None:return self.session.finish(t)
        if self.hold<=0:return None
        row=dict(set=len(self.session.sets)+1,reps=0,duration=round(self.hold,1),quality_seconds=round(self.quality_hold,1),average_score=round(self.hold_score_sum/self.hold_score_count,1) if self.hold_score_count else None,best_score=self.hold_best,worst_score=self.hold_worst,main_error=self.hold_errors.most_common(1)[0][0] if self.hold_errors else None)
        self.session.sets.append(row)
        self.hold=0.;self.quality_hold=0.;self.hold_score_sum=0.;self.hold_score_count=0;self.hold_best=None;self.hold_worst=None;self.hold_errors.clear();self.invalidate()
        return row
    @staticmethod
    def aggregate(samples,feature,top_hold):
        rows=[f for _,f in samples];agg={}
        for name in rows[0]:
            values=[float(f[name]) for f in rows if isinstance(f.get(name),(int,float)) and np.isfinite(f[name])]
            if values:agg[name]=float(np.mean(values))
        def values(name):return [float(f[name]) for f in rows if isinstance(f.get(name),(int,float)) and np.isfinite(f[name])]
        primary=values(feature)
        agg.update(depth=min(primary),peak=max(primary),duration=samples[-1][0]-samples[0][0],top_hold=top_hold)
        for name,source in [('arms_top','arm_elevation'),('feet_top','feet'),('wrist_top','wrist_height')]:
            seq=values(source)
            if seq:agg[name]=max(seq)
        for name,source in [('shoulder_travel','shoulder_y'),('hip_range','hip_y')]:
            seq=values(source)
            if seq:agg[name]=max(seq)-min(seq)
        for name,source in [('rear_depth','rear_knee'),('body','body')]:
            seq=values(source)
            if seq:agg[name]=min(seq)
        lean=values('lean')
        if lean:agg['stability']=float(np.std(lean))
        return agg
    def update(self,pose,t):
        out=dict(state='NO_POSE',reps=self.machine.reps if self.machine else None,score=None,feedback='Please ensure the required joints are visible',duration=self.hold,quality_duration=self.quality_hold,completed=False,features={},keypoints=None)
        if pose is None:
            self.invalidate();return out
        if pose.person_count>1:
            self.invalidate();out['feedback']='Multiple people detected. Keep only one person in view.';return out
        box=np.array(pose.bbox)
        if self.last_box is not None:
            center=(box[:2]+box[2:])/2;old=(self.last_box[:2]+self.last_box[2:])/2
            if np.linalg.norm(center-old)>max(40,np.linalg.norm(box[2:]-box[:2])*.4):self.invalidate()
        self.last_box=box
        if self.last_t is not None and (t<=self.last_t or t-self.last_t>1):self.invalidate()
        raw=extract(pose.keypoints,self.threshold,self.last_side,self.exercise)
        k=self.filter.pose(pose.keypoints,self.threshold)
        f=extract(k,self.threshold,self.last_side,self.exercise)
        out.update(features=f,raw_features=raw,keypoints=k)
        if any(f.get(name) is None for name in self.rule['required']):
            self.invalidate();out['feedback']='Move back or turn to the recommended view so all required joints are visible';return out
        if self.last_side and self.last_side!=f['side']:
            self.samples.clear()
            if self.machine:self.machine.reset()
        self.last_side=f['side']
        floor=self.exercise in ('plank','pushup','glute_bridge','crunch')
        if (floor and f['lean'] is not None and f['lean']<45) or (self.exercise=='shoulder_press' and f['arm_elevation']<60):
            self.invalidate();out['feedback']='Check exercise position and recommended camera view';return out
        dt=min(.2,t-self.last_t) if self.last_t is not None else 0
        self.last_t=t
        if self.machine is None:
            self.hold_history.append((t,f['body']))
            while self.hold_history and t-self.hold_history[0][0]>1.5:self.hold_history.popleft()
            f['hold_stability']=float(np.std([v for _,v in self.hold_history])) if self.hold_history else None
            score=self.scoring.evaluate(f,self.rule['rules']);self.hold+=max(0,dt)
            if score['total_score'] is not None:
                value=score['total_score'];self.hold_score_sum+=value;self.hold_score_count+=1
                self.hold_best=value if self.hold_best is None else max(self.hold_best,value)
                self.hold_worst=value if self.hold_worst is None else min(self.hold_worst,value)
                if value>=70:self.quality_hold+=max(0,dt)
            self.hold_errors.update(score['detected_errors'])
            out.update(state='HOLD',score=score['total_score'],feedback='; '.join(score['feedback']) or 'Maintain a steady position',duration=round(self.hold,1),quality_duration=round(self.quality_hold,1),detected_errors=score['detected_errors'])
            return out
        old=self.machine.phase;completed=self.machine.update(f[self.rule['feature']],t)
        if old==0 and self.machine.phase==1:
            self.samples=[(t,f.copy())];self.top_hold=0.
            self.partial_feedback=None
        elif self.machine.phase or old:self.samples.append((t,f.copy()))
        if old==2 and self.machine.phase==2:self.top_hold+=max(dt,0)
        if self.machine.last_event=='partial':
            self.samples.clear();self.partial_feedback='Incomplete range; this attempt was not counted'
            self.machine.last_event=None
        if completed and self.samples:
            agg=self.aggregate(self.samples,self.rule['feature'],self.top_hold)
            self.last_score=self.scoring.evaluate(agg,self.rule['rules'])
            self.last_score['duration']=agg['duration'];self.last_score['timestamp']=t
            self.session.add(self.last_score,t);self.samples.clear();self.partial_feedback=None
        if self.machine.phase==0 and not completed:self.samples.clear()
        self.session.idle(t,self.machine.phase==0)
        feedback=self.partial_feedback or ('; '.join(self.last_score['feedback']) if self.last_score and self.last_score['feedback'] else 'Move steadily through the full range')
        out.update(state=self.machine.state,reps=self.machine.reps,score=self.last_score['total_score'] if self.last_score else None,feedback=feedback,completed=completed,velocity=self.machine.velocity,detected_errors=self.last_score['detected_errors'] if self.last_score and not self.partial_feedback else [])
        if self.exercise=='jumping_jack' and self.session.current and self.session.start is not None:
            elapsed=max(t-self.session.start,.01);out['reps_per_min']=round(60*len(self.session.current)/elapsed,1)
        return out
