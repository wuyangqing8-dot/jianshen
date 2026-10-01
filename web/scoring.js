export function evaluate(features,rules){let total=0,weight=0;const dimensions={},errors=[];
 for(const [name,lo,hi,slope,w,message] of rules){const v=features[name];if(v==null||!Number.isFinite(v))continue;const score=Math.max(0,100-slope*Math.max(lo-v,0,v-hi));dimensions[name]=score;total+=w*score;weight+=w;if(score<75)errors.push({score,name,message});}
 errors.sort((a,b)=>a.score-b.score);return {total_score:weight?Math.round(total/weight*10)/10:null,dimension_scores:dimensions,detected_errors:errors.slice(0,2).map(x=>x.name),feedback:errors.slice(0,2).map(x=>x.message)};
}
