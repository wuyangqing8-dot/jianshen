import {angle,lean,offset} from './geometry.js?v=20260928b';
import {TemporalFilter} from './filters.js?v=20260928b';
import {ExerciseStateMachine} from './stateMachine.js?v=20260928b';
import {evaluate} from './scoring.js?v=20260928b';
const SIDES={left:[5,7,9,11,13,15,3],right:[6,8,10,12,14,16,4]};
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const deviation=a=>Math.sqrt(mean(a.map(x=>(x-mean(a))**2)));
const FEATURE_LABELS={knee:'膝盖和脚踝',hip:'肩膀和髋部',lean:'肩膀和髋部',elbow:'肩膀、手肘和手腕',body:'肩膀、髋部和脚踝',shoulder_y:'肩膀和脚踝',front_knee:'前腿膝盖',rear_knee:'后腿膝盖',bridge:'肩膀、髋部和膝盖',curl:'肩膀和髋部',arm_elevation:'双臂',wrist_height:'双手',feet:'双脚',offset:'肩膀、髋部和脚踝'};
export function extract(k,threshold=.28,preferredSide=null,exercise='squat'){
 const f={},quality={},ok=(...ids)=>ids.every(i=>k[i][2]>=threshold&&k[i].every(Number.isFinite));
 const dist=(i,j)=>ok(i,j)?Math.hypot(k[i][0]-k[j][0],k[i][1]-k[j][1]):null;
 for(const [side,ids] of Object.entries(SIDES)){
  const [s,e,w,h,n,a,ear]=ids;
  const relevant={squat:[s,h,n,a],lunge:[s,h,n,a],pushup:[s,e,w,h,a],plank:[s,e,h,a],glute_bridge:[s,h,n,a],crunch:[s,h,n,a],lateral_raise:[s,e,w,h],shoulder_press:[s,e,w,h],jumping_jack:[s,w,h,a]}[exercise]||[s,h,n,a];
  quality[side]=Math.min(...relevant.map(i=>k[i][2]));
  for(const [name,joints] of [['knee',[h,n,a]],['elbow',[s,e,w]],['hip',[s,h,n]],['shoulder',[e,s,h]],['body',[s,h,a]],['bridge',[s,h,n]],['head',[ear,s,h]]])f[side+'_'+name]=ok(...joints)?angle(...joints.map(i=>k[i])):null;
  f[side+'_lean']=ok(s,h)?lean(k[s],k[h]):null;
  f[side+'_offset']=ok(s,h,a)?offset(k[h],k[s],k[a]):null;
  f[side+'_hip_sag']=null;f[side+'_hip_pike']=null;
  if(ok(s,h,a)){const horizontal=k[a][0]-k[s][0],length=dist(s,a);if(length>1e-8&&Math.abs(horizontal)>length*.3){const projection=(k[h][0]-k[s][0])/horizontal;if(projection>=0&&projection<=1){const signed=(k[h][1]-k[s][1]-projection*(k[a][1]-k[s][1]))/length;f[side+'_hip_sag']=Math.max(0,signed);f[side+'_hip_pike']=Math.max(0,-signed);}}}
  const scale=dist(s,h);
  f[side+'_shoulder_y']=scale&&ok(a)?(k[s][1]-k[a][1])/scale:null;
  f[side+'_hip_y']=scale?(k[h][1]-k[s][1])/scale:null;
  f[side+'_wrist_height']=scale&&ok(w)?(k[s][1]-k[w][1])/scale:null;
  f[side+'_ankle_distance']=scale&&ok(a)?(k[a][0]-k[h][0])/scale:null;
 }
 f.side=preferredSide&&quality[preferredSide]>=threshold?preferredSide:quality.left>quality.right?'left':'right';
 for(const name of ['knee','elbow','hip','shoulder','body','bridge','head','lean','offset','hip_sag','hip_pike','shoulder_y','hip_y','wrist_height','ankle_distance'])f[name]=f[f.side+'_'+name];
 for(const name of ['knee','elbow','shoulder','wrist_height','hip_y'])f[name+'_asymmetry']=f['left_'+name]!=null&&f['right_'+name]!=null?Math.abs(f['left_'+name]-f['right_'+name]):null;
 let scale=null;
 if(ok(5,6,11,12))scale=Math.hypot((k[5][0]+k[6][0]-k[11][0]-k[12][0])/2,(k[5][1]+k[6][1]-k[11][1]-k[12][1])/2);
 else{const [s,,,h]=SIDES[f.side];scale=dist(s,h);}
 const feet=dist(15,16);
 f.feet=scale&&feet!=null?feet/scale:null;
 f.wrist_asymmetry=scale&&ok(9,10)?Math.abs(k[9][1]-k[10][1])/scale:null;
 f.arm_elevation=f.left_shoulder!=null&&f.right_shoulder!=null?Math.min(f.left_shoulder,f.right_shoulder):null;
 f.wrist_height=f.left_wrist_height!=null&&f.right_wrist_height!=null?Math.min(f.left_wrist_height,f.right_wrist_height):null;
 f.curl=f.lean!=null?90-f.lean:null;
 f.jack=f.arm_elevation!=null&&f.feet!=null?Math.min(f.arm_elevation/150,f.feet/1.5):null;
 f.front_knee=null;f.rear_knee=null;f.front_side=null;
 if(f.left_knee!=null&&f.right_knee!=null){let front=null;if(scale&&ok(0,5,6,15,16)){const facing=k[0][0]-(k[5][0]+k[6][0])/2,separation=Math.abs(k[15][0]-k[16][0]);if(Math.abs(facing)>scale*.08&&separation>scale*.35)front=(k[15][0]-k[16][0])*facing>0?'left':'right';}front??=f.left_knee<f.right_knee?'left':'right';const rear=front==='left'?'right':'left';f.front_knee=f[front+'_knee'];f.rear_knee=f[rear+'_knee'];f.front_side=front;}
 return f;
}
export class ExerciseEngine{
 constructor(exercise,rule,filterConfig={}){this.exercise=exercise;this.rule=rule;this.filter=new TemporalFilter(filterConfig.window??3,filterConfig.mode??'moving',filterConfig.alpha??.4);this.machine=rule.cycle?new ExerciseStateMachine(rule.cycle):null;this.samples=[];this.lastScore=null;this.hold=0;this.qualityHold=0;this.holdScoreSum=0;this.holdScoreCount=0;this.holdBest=null;this.holdWorst=null;this.holdErrors=new Map();this.lastT=null;this.lastSide=null;this.lastBox=null;this.holdHistory=[];this.sets=[];this.current=[];this.lastActivity=null;this.partialFeedback=null;}
 invalidate(){this.filter.reset();this.samples=[];this.lastT=null;this.lastSide=null;this.lastBox=null;this.holdHistory=[];this.machine?.reset();}
 finish(){if(!this.machine){if(this.hold<=0)return;this.sets.push({set:this.sets.length+1,reps:0,duration:Number(this.hold.toFixed(1)),quality_seconds:Number(this.qualityHold.toFixed(1)),average_score:this.holdScoreCount?Number((this.holdScoreSum/this.holdScoreCount).toFixed(1)):null,best_score:this.holdBest,worst_score:this.holdWorst,main_error:[...this.holdErrors].sort((a,b)=>b[1]-a[1])[0]?.[0]||null});this.hold=0;this.qualityHold=0;this.holdScoreSum=0;this.holdScoreCount=0;this.holdBest=null;this.holdWorst=null;this.holdErrors.clear();this.invalidate();return;}
 if(!this.current.length)return;const scores=this.current.map(x=>x.total_score).filter(x=>x!=null),errors={};for(const r of this.current)for(const e of r.detected_errors)errors[e]=(errors[e]||0)+1;this.sets.push({set:this.sets.length+1,reps:this.current.length,average_score:scores.length?mean(scores):null,best_score:scores.length?Math.max(...scores):null,worst_score:scores.length?Math.min(...scores):null,duration:this.lastActivity-this.setStart,main_error:Object.entries(errors).sort((a,b)=>b[1]-a[1])[0]?.[0]||null});this.current=[];this.lastActivity=null;}
 static aggregate(samples,feature,topHold){const rows=samples.map(x=>x[1]),agg={},values=name=>rows.map(x=>x[name]).filter(v=>typeof v==='number'&&Number.isFinite(v));for(const n of Object.keys(rows[0])){const a=values(n);if(a.length)agg[n]=mean(a);}const primary=values(feature);Object.assign(agg,{depth:Math.min(...primary),peak:Math.max(...primary),duration:samples.at(-1)[0]-samples[0][0],top_hold:topHold});for(const [name,source] of [['arms_top','arm_elevation'],['feet_top','feet'],['wrist_top','wrist_height']]){const a=values(source);if(a.length)agg[name]=Math.max(...a);}for(const [name,source] of [['shoulder_travel','shoulder_y'],['hip_range','hip_y']]){const a=values(source);if(a.length)agg[name]=Math.max(...a)-Math.min(...a);}for(const [name,source] of [['rear_depth','rear_knee'],['body','body']]){const a=values(source);if(a.length)agg[name]=Math.min(...a);}const leans=values('lean');if(leans.length)agg.stability=deviation(leans);return agg;}
 update(pose,t){const r={state:'NO_POSE',reps:this.machine?.reps??null,score:null,feedback:'暂未检测到完整人体，请让身体进入画面',duration:this.hold,quality_duration:this.qualityHold,completed:false,features:{}};
  if(!pose){if(this.lastT!=null&&t-this.lastT>1.2)this.invalidate();return r;}
  if(this.lastT!=null&&(t<=this.lastT||t-this.lastT>2))this.invalidate();const b=pose.bbox;if(this.lastBox){const old=this.lastBox;if(Math.hypot((b[0]+b[2]-old[0]-old[2])/2,(b[1]+b[3]-old[1]-old[3])/2)>Math.max(70,Math.hypot(b[2]-b[0],b[3]-b[1])*.65))this.invalidate();}this.lastBox=b;
  this.filter.window=this.lastT!=null&&t-this.lastT>.2?1:3;
  const raw=extract(pose.keypoints,.28,this.lastSide,this.exercise),k=this.filter.pose(pose.keypoints,.28),f=extract(k,.28,this.lastSide,this.exercise);r.keypoints=k;r.features=f;r.raw_features=raw;
  const missing=this.rule.required.filter(n=>f[n]==null);if(missing.length){if(this.lastT!=null&&t-this.lastT>1.2)this.invalidate();r.feedback='已检测到人体，但看不清'+[...new Set(missing.map(n=>FEATURE_LABELS[n]||n))].join('、')+'；请调整距离或视角';return r;}
  this.lastSide=f.side;
  const dt=this.lastT==null?0:Math.max(0,Math.min(.2,t-this.lastT));this.lastT=t;
  if(!this.machine){this.holdHistory.push([t,f.body]);this.holdHistory=this.holdHistory.filter(x=>t-x[0]<=1.5);f.hold_stability=deviation(this.holdHistory.map(x=>x[1]));const score=evaluate(f,this.rule.rules);this.hold+=dt;if(score.total_score!=null){this.holdScoreSum+=score.total_score;this.holdScoreCount++;this.holdBest=this.holdBest==null?score.total_score:Math.max(this.holdBest,score.total_score);this.holdWorst=this.holdWorst==null?score.total_score:Math.min(this.holdWorst,score.total_score);if(score.total_score>=70)this.qualityHold+=dt;}for(const key of score.detected_errors)this.holdErrors.set(key,(this.holdErrors.get(key)||0)+1);return {...r,state:'HOLD',score:score.total_score,feedback:score.feedback.join('; ')||'保持稳定 / Hold steady',duration:this.hold,quality_duration:this.qualityHold,detected_errors:score.detected_errors};}
  const old=this.machine.phase,completed=this.machine.update(f[this.rule.feature],t);
  if(old===0&&this.machine.phase===1){this.samples=[[t,{...f}]];this.topHold=0;this.partialFeedback=null;}
  else if(this.machine.phase||old)this.samples.push([t,{...f}]);
  if(old===2&&this.machine.phase===2)this.topHold+=Math.max(dt,0);
  if(this.machine.lastEvent==='partial'){this.samples=[];this.partialFeedback='动作幅度不足，本次未计数';this.machine.lastEvent=null;}
  if(completed&&this.samples.length){const agg=ExerciseEngine.aggregate(this.samples,this.rule.feature,this.topHold);this.lastScore={...evaluate(agg,this.rule.rules),duration:agg.duration,timestamp:t};if(!this.current.length)this.setStart=t-agg.duration;this.current.push(this.lastScore);this.lastActivity=t;this.samples=[];this.partialFeedback=null;}
  if(this.machine.phase===0&&!completed)this.samples=[];
  if(this.machine.phase===0&&this.lastActivity!=null&&t-this.lastActivity>=12)this.finish();
  const cue=!this.machine.armed?'已检测到人体；请摆好起始姿势':this.machine.phase===0?'起始姿势已识别，可以开始动作':this.machine.phase===1?'动作进行中；继续到另一端':this.machine.phase===2?'已达到动作幅度；返回起始姿势':'正在返回起始姿势，完成后计数';
  const out={...r,state:this.machine.state,reps:this.machine.reps,completed,score:this.lastScore?.total_score??null,feedback:completed?'完成 1 次；'+(this.lastScore?.feedback?.join('; ')||'继续下一次'):this.partialFeedback||cue,detected_errors:completed?this.lastScore?.detected_errors||[]:[]};
  if(this.exercise==='jumping_jack'&&this.current.length)out.reps_per_min=Math.round(600* this.current.length/Math.max(.01,t-this.setStart))/10;
  return out;
 }
}
