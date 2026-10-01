import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import {angle} from './geometry.js';import {ExerciseStateMachine} from './stateMachine.js';import {evaluate} from './scoring.js';
const rules=JSON.parse(await readFile(new URL('./rules.json',import.meta.url)));
function feed(values){const m=new ExerciseStateMachine(rules.squat.cycle);let t=0;for(const v of values)for(let i=0;i<5;i++){m.update(v,t);t+=.04;}return m.reps;}
test('geometry',()=>assert.equal(angle([1,0],[0,0],[0,1]),90));
test('full squat',()=>assert.equal(feed([170,165,150,130,115,100,90,95,110,130,155,170]),1));
test('jitter is not a rep',()=>assert.equal(feed([170,149,151,148,152,150,153]),0));
test('missing pose cancels',()=>assert.equal(feed([170,140,90,null,130,170]),0));
test('missing score remains null',()=>assert.equal(evaluate({},rules.squat.rules).total_score,null));
import {ExerciseEngine} from './engine.js';import {ActionRecognizer} from './actionRecognizer.js';
import {calibratedCycle,stableReading} from './calibration.js';
import {goalProgress,summaryRows,summaryCSV} from './trainingTools.js';
const fixtures=JSON.parse(await readFile(new URL('../tests/assets/motion_sequences.json',import.meta.url)));
function pose(row){return {bbox:row.bbox,person_count:1,keypoints:row.keypoints.map(p=>[p.x,p.y,p.confidence])};}
for(const name of ['squat','pushup','lunge','jumping_jack','glute_bridge','crunch','lateral_raise','shoulder_press']){
 test(`${name} synthetic COCO17 full cycle`,()=>{
 const e=new ExerciseEngine(name,rules[name]);let t=0;for(const row of fixtures[name])for(let i=0;i<16;i++){e.update(pose(row),t);t+=.04;}
 assert.equal(e.machine.reps,1);
 assert.ok(e.current[0].total_score>=0&&e.current[0].total_score<=100);
 });
}
test('plank hold quality and duration remain separate',()=>{
 const e=new ExerciseEngine('plank',rules.plank);let t=0,last;
 for(const row of fixtures.plank)for(let i=0;i<6;i++){last=e.update(pose(row),t);t+=.04;}
 assert.equal(last.state,'HOLD');assert.ok(last.duration>1);assert.ok(last.quality_duration<=last.duration);assert.ok(last.score>=0&&last.score<=100);
});
test('auto recognizer abstains at rest and identifies clear squat',()=>{
 const a=new ActionRecognizer();let t=0,found=[];
 for(const row of fixtures.squat){for(let i=0;i<16;i++){found.push(a.update(pose(row),t));t+=.04;}}
 assert.equal(found[0],null);assert.ok(found.includes('squat'));
});
test('auto mode recognizes each idealized nine-action trajectory without another label',()=>{
 for(const [name,rows] of Object.entries(fixtures)){
  const a=new ActionRecognizer(),found=new Set();let t=0;
  for(const row of rows)for(let i=0;i<16;i++){const guess=a.update(pose(row),t);if(guess)found.add(guess);t+=.04;}
  assert.deepEqual([...found],[name],name);
 }
});
test('short cycles count at four and eight pose frames per second',()=>{
 for(const fps of [4,8])for(const name of ['squat','pushup','lunge','jumping_jack','glute_bridge','crunch','lateral_raise','shoulder_press']){
  const e=new ExerciseEngine(name,rules[name]);let t=0;
  for(const row of fixtures[name])for(let i=0;i<fps/4;i++){e.update(pose(row),t);t+=1/fps;}
  assert.equal(e.machine.reps,1,`${name} at ${fps} pose FPS`);
 }
});
test('a short missing pose does not erase a valid cycle',()=>{
 for(const name of ['squat','pushup','jumping_jack']){
  const e=new ExerciseEngine(name,rules[name]);let t=0,n=0;
  for(const row of fixtures[name])for(let i=0;i<2;i++){e.update(n++===7?null:pose(row),t);t+=.125;}
  assert.equal(e.machine.reps,1,name);
 }
});
test('moderate ankle confidence still supports a visible squat cycle',()=>{
 const e=new ExerciseEngine('squat',rules.squat);let t=0;
 for(const row of fixtures.squat)for(let i=0;i<2;i++){
  const p=pose(row);for(const joint of [15,16])p.keypoints[joint][2]=.36;
  e.update(p,t);t+=.125;
 }
 assert.equal(e.machine.reps,1);
});
test('a modest squat counts while a second detected person is visible',()=>{
 const e=new ExerciseEngine('squat',rules.squat),base=pose(fixtures.squat[0]);let t=0,last;
 for(const kneeAngle of [154,151,147,142,136,130,123,128,135,142,148,154]){
  const p=structuredClone(base);p.person_count=2;
  for(const [hip,knee,ankle] of [[11,13,15],[12,14,16]]){
   const bend=(180-kneeAngle)*Math.PI/180,length=100;
   p.keypoints[ankle][0]=p.keypoints[knee][0]+Math.sin(bend)*length;
   p.keypoints[ankle][1]=p.keypoints[knee][1]+Math.cos(bend)*length;
  }
  last=e.update(p,t);t+=.25;
 }
 assert.equal(e.machine.reps,1);
 assert.equal(last.reps,1);
 assert.notEqual(last.state,'NO_POSE');
});
test('missing joints explain why a detected person is not counted',()=>{
 const e=new ExerciseEngine('squat',rules.squat),p=pose(fixtures.squat[0]);
 for(const i of [13,14,15,16])p.keypoints[i][2]=.05;
 const result=e.update(p,0);
 assert.equal(result.state,'NO_POSE');
 assert.match(result.feedback,/已检测到人体.*看不清/);
 assert.equal(result.features.knee,null);
});
test('personal calibration counts a visible small squat range that preset thresholds miss',()=>{
 const sequence=[151,150,147,144,141,138,136,139,142,146,150,151];
 const run=rule=>{const e=new ExerciseEngine('squat',rule);let t=0;for(const degrees of sequence){const p=pose(fixtures.squat[0]);for(const [knee,ankle] of [[13,15],[14,16]]){const bend=(180-degrees)*Math.PI/180;p.keypoints[ankle][0]=p.keypoints[knee][0]+100*Math.sin(bend);p.keypoints[ankle][1]=p.keypoints[knee][1]+100*Math.cos(bend);}e.update(p,t);t+=.25;}return e.machine.reps;};
 assert.equal(run(rules.squat),0);
 const calibrated={...rules.squat,cycle:calibratedCycle(rules.squat.cycle,151,136,'knee')};
 assert.equal(run(calibrated),1);
 assert.throws(()=>calibratedCycle(rules.squat.cycle,136,151,'knee'),/顺序相反/);
});
test('calibration rejects unstable and missing joint readings',()=>{
 assert.equal(stableReading([[.1,'knee',145],[.2,'knee',146],[.3,'knee',144]],.3,'knee'),145);
 assert.throws(()=>stableReading([[0,'knee',145],[.2,'knee',126],[.4,'knee',150]],.4,'knee'),/仍在变化/);
 assert.throws(()=>stableReading([[0,'knee',145]],.2,'knee'),/尚未连续识别/);
});
test('automatic identification replays and counts its first full action',()=>{
 for(const name of ['squat','pushup','lunge','jumping_jack','glute_bridge','crunch','lateral_raise','shoulder_press']){
  const recognizer=new ActionRecognizer();let engine=null,t=0;
  for(const row of fixtures[name])for(let i=0;i<2;i++){
   const p=pose(row);
   if(!engine){const found=recognizer.update(p,t);if(found){engine=new ExerciseEngine(found,rules[found]);for(const [at,recorded] of recognizer.poseHistory)engine.update(recorded,at);}}
   else engine.update(p,t);
   t+=.125;
  }
  assert.equal(engine?.exercise,name,`${name} detection`);assert.equal(engine.machine.reps,1,`${name} first cycle`);
 }
});
test('set goal tracks current repetitions and plank seconds independently',()=>{
 assert.deepEqual(goalProgress('squat',12,999,10),{progress:12,target:10,unit:'次',percent:100,reached:true});
 const plank=goalProgress('plank',20,12.5,30);assert.equal(plank.progress,12.5);assert.equal(plank.reached,false);
 assert.equal(goalProgress('squat',0,0,0).target,10);
});
test('CSV includes completed and current sets without video or keypoints',()=>{
 const engine={exercise:'squat',sets:[{set:1,reps:3,duration:15,average_score:80,best_score:90,worst_score:70,main_error:'lean'}],current:[{total_score:75,detected_errors:['depth']}],setStart:20,lastActivity:23};
 const rows=summaryRows(engine),csv=summaryCSV(rows);assert.equal(rows.length,2);assert.equal(rows[1].status,'current');assert.equal(rows[1].main_error,'depth');assert.ok(csv.startsWith('\ufeffexercise,set,reps'));assert.ok(!csv.includes('keypoints'));
 assert.equal(summaryRows({exercise:'plank',sets:[],hold:32.2,qualityHold:21.1},85)[0].quality_seconds,21.1);
});
test('finishing a plank stores a scored set and resets the next hold',()=>{
 const e=new ExerciseEngine('plank',rules.plank);let t=0;
 for(let n=0;n<60;n++){e.update(pose(fixtures.plank[0]),t);t+=.04;}
 const before=e.hold;assert.ok(before>1);e.finish();assert.equal(e.sets.length,1);
 assert.equal(e.sets[0].duration,Number(before.toFixed(1)));assert.equal(e.hold,0);
 assert.equal(summaryRows(e)[0].quality_seconds,e.sets[0].quality_seconds);
 for(let n=0;n<25;n++){e.update(pose(fixtures.plank[0]),t);t+=.04;}
 assert.ok(e.hold>0&&e.hold<before);
});
