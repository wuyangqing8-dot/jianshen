"""Conservative temporal exercise suggestion; abstains when 2D evidence overlaps."""
from collections import deque
import numpy as np
from .filtering import TemporalFilter
from .feature_extractor import extract

class ActionRecognizer:
    def __init__(self,threshold=.45):
        self.threshold=threshold;self.filter=TemporalFilter();self.history=deque();self.candidate=None;self.since=None
    def reset(self):
        self.filter.reset();self.history.clear();self.candidate=None;self.since=None
    def update(self,pose,t):
        if pose is None or pose.person_count!=1:
            self.reset();return None
        if self.history and (t<=self.history[-1][0] or t-self.history[-1][0]>1):
            self.reset()
        k=self.filter.pose(pose.keypoints,self.threshold)
        f=extract(k,self.threshold)
        self.history.append((t,f))
        while self.history and t-self.history[0][0]>6:self.history.popleft()
        if len(self.history)<12 or t-self.history[0][0]<1.5:return None
        def seq(name):return [x[name] for _,x in self.history if isinstance(x.get(name),(int,float)) and np.isfinite(x[name])]
        def top(name):
            a=seq(name);return max(a) if a else None
        def bottom(name):
            a=seq(name);return min(a) if a else None
        def span(name):
            a=seq(name);return max(a)-min(a) if len(a)>3 else None
        def median(name):
            a=seq(name);return float(np.median(a)) if a else None
        def ge(a,b):return a is not None and a>=b
        def le(a,b):return a is not None and a<=b
        floor=ge(median('lean'),55)
        guesses=[]
        if floor:
            if ge(span('bridge'),28) and ge(span('hip_y'),.12):guesses.append('glute_bridge')
            if ge(span('curl'),20) and ge(span('shoulder_y'),.12) and le(span('bridge'),35) and ge(median('head'),145):guesses.append('crunch')
            if ge(span('elbow'),40) and ge(top('elbow'),155) and ge(median('body'),150) and le(span('bridge'),25) and ge(median('lean'),70):guesses.append('pushup')
            if ge(median('body'),158) and le(span('elbow'),18) and le(span('bridge'),25) and le(span('curl'),18) and t-self.history[0][0]>=2:guesses.append('plank')
        else:
            if ge(top('feet'),1.1) and ge(span('feet'),.5) and ge(top('arm_elevation'),125) and ge(span('arm_elevation'),50):guesses.append('jumping_jack')
            if ge(span('elbow'),40) and ge(top('elbow'),155) and ge(top('wrist_height'),.4) and ge(top('arm_elevation'),115):guesses.append('shoulder_press')
            if ge(span('arm_elevation'),45) and ge(top('arm_elevation'),70) and le(top('arm_elevation'),120) and ge(median('elbow'),125) and le(span('feet'),.4):guesses.append('lateral_raise')
            if ge(span('front_knee'),35) and le(bottom('front_knee'),125) and ge(top('feet'),.7):guesses.append('lunge')
            if ge(span('knee'),40) and le(bottom('knee'),125) and le(top('feet'),.65):guesses.append('squat')
        guess=guesses[0] if len(guesses)==1 else None
        if guess!=self.candidate:self.candidate=guess;self.since=t
        return guess if guess is not None and t-self.since>=.35 else None
