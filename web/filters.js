export class TemporalFilter{
 constructor(window=5,mode='moving',alpha=.4){this.window=window;this.mode=mode;this.alpha=alpha;this.reset();}
 reset(){this.history=new Map();}
 update(key,v){if(v==null){this.history.delete(key);return null;}const q=this.history.get(key)||[];let r;
 if(this.mode==='ema'){r=q.length? v.map((x,i)=>this.alpha*x+(1-this.alpha)*q[0][i]):v;this.history.set(key,[r]);}
 else {q.push(v);while(q.length>this.window)q.shift();this.history.set(key,q);r=v.map((_,i)=>q.reduce((s,x)=>s+x[i],0)/q.length);}return r;}
 pose(k,threshold){return k.map((p,i)=>{const xy=this.update(i,p[2]>=threshold?p.slice(0,2):null);return xy?[...xy,p[2]]:[...p];});}
}
