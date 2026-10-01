export const SUMMARY_COLUMNS=['exercise','set','reps','duration_seconds','average_score','best_score','worst_score','main_error','quality_seconds','status'];

export function goalProgress(exercise,reps,holdSeconds,target){
 const plank=exercise==='plank',limit=Number.isFinite(Number(target))&&Number(target)>0?Math.min(3600,Math.floor(Number(target))):plank?30:10;
 const progress=plank?Math.max(0,Number(holdSeconds)||0):Math.max(0,Math.floor(Number(reps)||0));
 return {progress,target:limit,unit:plank?'秒':'次',percent:Math.min(100,100*progress/limit),reached:progress>=limit};
}

export function summaryRows(engine,score=null){
 if(!engine)return [];
 const name=engine.exercise,rows=(engine.sets||[]).map(s=>({exercise:name,set:s.set,reps:s.reps,duration_seconds:s.duration,average_score:s.average_score,best_score:s.best_score,worst_score:s.worst_score,main_error:s.main_error,quality_seconds:s.quality_seconds??'',status:'completed'}));
 if(name==='plank'){
  if(engine.hold>0)rows.push({exercise:name,set:rows.length+1,reps:0,duration_seconds:Number(engine.hold.toFixed(1)),average_score:engine.holdScoreCount?Number((engine.holdScoreSum/engine.holdScoreCount).toFixed(1)):score,best_score:engine.holdBest??'',worst_score:engine.holdWorst??'',main_error:[...(engine.holdErrors||new Map())].sort((a,b)=>b[1]-a[1])[0]?.[0]||'',quality_seconds:Number(engine.qualityHold.toFixed(1)),status:'current'});
 }else if(engine.current?.length){
  const scores=engine.current.map(r=>r.total_score).filter(Number.isFinite),errors=new Map();
  for(const rep of engine.current)for(const key of rep.detected_errors||[])errors.set(key,(errors.get(key)||0)+1);
  const main=[...errors].sort((a,b)=>b[1]-a[1])[0]?.[0]||'';
  rows.push({exercise:name,set:rows.length+1,reps:engine.current.length,duration_seconds:Number(Math.max(0,(engine.lastActivity??0)-(engine.setStart??0)).toFixed(1)),average_score:scores.length?Number((scores.reduce((a,b)=>a+b,0)/scores.length).toFixed(1)):null,best_score:scores.length?Math.max(...scores):null,worst_score:scores.length?Math.min(...scores):null,main_error:main,quality_seconds:'',status:'current'});
 }
 return rows;
}

export function summaryCSV(rows){
 const quote=value=>`"${String(value??'').replaceAll('"','""')}"`;
 return '\ufeff'+[SUMMARY_COLUMNS.join(','),...rows.map(row=>SUMMARY_COLUMNS.map(key=>quote(row[key])).join(','))].join('\r\n')+'\r\n';
}
