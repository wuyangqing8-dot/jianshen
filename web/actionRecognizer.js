import {TemporalFilter} from './filters.js?v=20260928b';
import {extract} from './engine.js?v=20260928b';
export class ActionRecognizer{
 constructor(threshold=.28){this.threshold=threshold;this.filter=new TemporalFilter(3);this.history=[];this.poseHistory=[];this.candidate=null;this.since=null;}
 reset(){this.filter.reset();this.history=[];this.poseHistory=[];this.candidate=null;this.since=null;}
 update(pose,t){if(!pose){if(this.history.length&&t-this.history.at(-1)[0]>1.2)this.reset();return null;}if(this.history.length&&(t<=this.history.at(-1)[0]||t-this.history.at(-1)[0]>2))this.reset();this.filter.window=this.history.length&&t-this.history.at(-1)[0]>.2?1:3;const f=extract(this.filter.pose(pose.keypoints,this.threshold),this.threshold);this.history.push([t,f]);this.poseHistory.push([t,pose]);this.history=this.history.filter(x=>t-x[0]<=6);this.poseHistory=this.poseHistory.filter(x=>t-x[0]<=6);if(this.history.length<7||t-this.history[0][0]<1.5)return null;
 const seq=name=>this.history.map(x=>x[1][name]).filter(x=>typeof x==='number'&&Number.isFinite(x)),top=name=>seq(name).length?Math.max(...seq(name)):null,bottom=name=>seq(name).length?Math.min(...seq(name)):null,span=name=>seq(name).length>3?top(name)-bottom(name):null,median=name=>{const a=seq(name).sort((x,y)=>x-y);return a.length?a[Math.floor(a.length/2)]:null;},ge=(a,b)=>a!=null&&a>=b,le=(a,b)=>a!=null&&a<=b;
 const guesses=[],floor=ge(median('lean'),55);
 if(floor){
 if(ge(span('bridge'),28)&&ge(span('hip_y'),.12))guesses.push('glute_bridge');
 if(ge(span('curl'),20)&&ge(span('shoulder_y'),.12)&&le(span('bridge'),35)&&ge(median('head'),145))guesses.push('crunch');
 if(ge(span('elbow'),40)&&ge(top('elbow'),155)&&ge(median('body'),150)&&le(span('bridge'),25)&&ge(median('lean'),70))guesses.push('pushup');
 if(ge(median('body'),158)&&le(span('elbow'),18)&&le(span('bridge'),25)&&le(span('curl'),18)&&t-this.history[0][0]>=2)guesses.push('plank');
 }else{
 if(ge(top('feet'),1.1)&&ge(span('feet'),.5)&&ge(top('arm_elevation'),125)&&ge(span('arm_elevation'),50))guesses.push('jumping_jack');
 if(ge(span('elbow'),40)&&ge(top('elbow'),155)&&ge(top('wrist_height'),.4)&&ge(top('arm_elevation'),115))guesses.push('shoulder_press');
 if(ge(span('arm_elevation'),45)&&ge(top('arm_elevation'),70)&&le(top('arm_elevation'),120)&&ge(median('elbow'),125)&&le(span('feet'),.4))guesses.push('lateral_raise');
 if(ge(span('front_knee'),35)&&le(bottom('front_knee'),125)&&ge(top('feet'),.7))guesses.push('lunge');
 if(ge(span('knee'),40)&&le(bottom('knee'),125)&&le(top('feet'),.65))guesses.push('squat');
 }
 const guess=guesses.length===1?guesses[0]:null;if(guess!==this.candidate){this.candidate=guess;this.since=t;}return guess!=null&&t-this.since>=.35?guess:null;
 }
}
