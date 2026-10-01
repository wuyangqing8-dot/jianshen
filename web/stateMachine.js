export class ExerciseStateMachine{
 constructor(config){this.c=config;this.reps=0;this.reset();}
 reset(){this.phase=0;this.armed=false;this.pending=null;this.since=0;this.lastT=null;this.lastV=null;this.motion=null;this.start=null;this.velocity=0;this.lastEvent=null;}
 get state(){return this.c.states[this.phase];}
 update(value,t){if(value==null){this.reset();return false;}const c=this.c,v=c.increasing?-value:value,lo=c.increasing?-c.high:c.low,hi=c.increasing?-c.low:c.high;
 if(this.lastT!=null&&(t<=this.lastT||t-this.lastT>2))this.reset();let dt=this.lastT==null?0:t-this.lastT;this.velocity=dt?(v-this.lastV)/dt:0;
 if(this.motion==null||Math.abs(this.velocity)>c.motion_threshold)this.motion=t;if(this.phase&&t-this.motion>c.timeout_seconds)this.reset();this.lastT=t;this.lastV=v;
 let target=null;if(!this.armed){if(v>=hi)target='arm';}else if(this.phase===0&&v<hi-c.hysteresis)target=1;else if(this.phase===1){if(v<=lo)target=2;else if(v>=hi)target='abort';}else if(this.phase===2){if(v>=hi)target=0;else if(v>lo+c.hysteresis)target=3;}else if(this.phase===3){if(v>=hi)target=0;else if(v<=lo)target=2;}
 if(target===null){this.pending=null;return false;}const sparse=dt>=Math.max(.18,2*c.minimum_duration);if(target!==this.pending){this.pending=target;this.since=t;if(!sparse)return false;}if(!sparse&&t-this.since+1e-9<c.minimum_duration)return false;this.pending=null;
 if(target==='arm'){this.armed=true;return false;}if(target==='abort'){this.reset();this.lastEvent='partial';return false;}this.phase=target;if(target===1)this.start=t;if(target===0){const valid=this.start!=null&&t-this.start>=c.minimum_cycle;this.start=null;if(valid)this.reps++;return valid;}return false;
 }
}
