from dataclasses import dataclass
@dataclass
class CycleConfig:
    low: float=100
    high: float=155
    increasing: bool=False
    states: tuple=('STAND','DOWN','BOTTOM','UP')
    minimum_duration: float=.09
    hysteresis: float=5
    timeout_seconds: float=8
    motion_threshold: float=2
    minimum_cycle: float=.5

class ExerciseStateMachine:
    """Four-phase cycle. Dwell is wall-clock time, independent of inference FPS."""
    def __init__(self,config=None):
        self.config=config or CycleConfig(); self.reps=0; self.reset()
    def reset(self):
        self.phase=0; self.armed=False; self.pending=None; self.pending_since=0; self.last_t=None; self.last_v=None; self.last_motion=None; self.cycle_start=None; self.velocity=0; self.last_event=None
    @property
    def state(self): return self.config.states[self.phase]
    def update(self,value,t):
        if value is None: self.reset(); return False
        c=self.config; v=-value if c.increasing else value
        low,high=(-c.high,-c.low) if c.increasing else (c.low,c.high)
        if self.last_t is not None and (t<=self.last_t or t-self.last_t>1): self.reset()
        dt=t-self.last_t if self.last_t is not None else 0
        self.velocity=(v-self.last_v)/dt if dt else 0
        if self.last_motion is None or abs(self.velocity)>c.motion_threshold: self.last_motion=t
        if self.phase and t-self.last_motion>c.timeout_seconds: self.reset()
        self.last_t=t; self.last_v=v
        target=None
        if not self.armed:
            if v>=high: target='arm'
        elif self.phase==0 and v<high-c.hysteresis: target=1
        elif self.phase==1:
            if v<=low: target=2
            elif v>=high: target='abort'
        elif self.phase==2 and v>low+c.hysteresis: target=3
        elif self.phase==3:
            if v>=high: target=0
            elif v<=low: target=2
        if target is None: self.pending=None; return False
        if target!=self.pending: self.pending=target; self.pending_since=t
        if t-self.pending_since+1e-9<c.minimum_duration: return False
        self.pending=None
        if target=='arm': self.armed=True; return False
        if target=='abort': self.reset(); self.last_event='partial'; return False
        self.phase=target
        if target==1: self.cycle_start=t
        if target==0:
            valid=self.cycle_start is not None and t-self.cycle_start>=c.minimum_cycle
            self.cycle_start=None
            if valid: self.reps+=1
            return valid
        return False
