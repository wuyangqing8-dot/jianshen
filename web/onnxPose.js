export class PoseEstimator{async infer(){throw new Error('Implement pose backend');}}
export class ONNXPoseEstimator extends PoseEstimator{
 async load_model(path='../models/pose_model.onnx'){
  this.path=path;ort.env.wasm.wasmPaths=new URL('./vendor/',location.href).href;ort.env.wasm.numThreads=1;this.provider='wasm';
  this.session=await ort.InferenceSession.create(path,{executionProviders:['wasm']});
  const meta=this.session.inputMetadata?.[0];this.size=meta?.shape?.[2]||meta?.dimensions?.[2]||320;if(!Number.isInteger(this.size))throw new Error('Static model input required');this.canvas=new OffscreenCanvas(this.size,this.size);this.ctx=this.canvas.getContext('2d',{willReadFrequently:true});
 }
 preprocess(source){const w=source.videoWidth||source.width,h=source.videoHeight||source.height,s=Math.min(this.size/w,this.size/h),nw=Math.round(w*s),nh=Math.round(h*s),px=Math.floor((this.size-nw)/2),py=Math.floor((this.size-nh)/2);
 this.ctx.fillStyle='rgb(114,114,114)';this.ctx.fillRect(0,0,this.size,this.size);this.ctx.drawImage(source,px,py,nw,nh);const rgba=this.ctx.getImageData(0,0,this.size,this.size).data,n=this.size*this.size,x=new Float32Array(n*3);for(let i=0;i<n;i++){x[i]=rgba[i*4]/255;x[n+i]=rgba[i*4+1]/255;x[n*2+i]=rgba[i*4+2]/255;}return {tensor:new ort.Tensor('float32',x,[1,3,this.size,this.size]),transform:[nw/w,nh/h,px,py,w,h]};}
 postprocess(output,t){const [sx,sy,px,py,w,h]=t,[,channels,n]=output.dims;if(channels!==56)throw new Error('Expected YOLOv8 raw COCO17 [1,56,N] model');const a=output.data,rows=[];
 for(let j=0;j<n;j++){const score=a[4*n+j];if(score<.25)continue;const x=a[j],y=a[n+j],bw=a[2*n+j],bh=a[3*n+j];rows.push({j,score,box:[x-bw/2,y-bh/2,x+bw/2,y+bh/2]});}
 rows.sort((a,b)=>b.score-a.score);const kept=[];for(const row of rows){if(!kept.some(k=>iou(row.box,k.box)>.45))kept.push(row);}if(!kept.length)return null;
 const r=kept[0],keypoints=[];for(let i=0;i<17;i++){const x=(a[(5+i*3)*n+r.j]-px)/sx,y=(a[(6+i*3)*n+r.j]-py)/sy,c=a[(7+i*3)*n+r.j];keypoints.push([x,y,x<0||x>=w||y<0||y>=h?0:c]);}
 return {bbox:[(r.box[0]-px)/sx,(r.box[1]-py)/sy,(r.box[2]-px)/sx,(r.box[3]-py)/sy],keypoints,person_confidence:r.score,person_count:kept.length};}
 async infer(source){const {tensor,transform}=this.preprocess(source);let out;try{out=await this.session.run({[this.session.inputNames[0]]:tensor});this.last=this.postprocess(out[this.session.outputNames[0]],transform);return this.last;}finally{tensor.dispose();if(out)for(const v of Object.values(out))v.dispose();}}
 get_keypoints(){return this.last?.keypoints;}
}
function iou(a,b){const area=r=>Math.max(0,r[2]-r[0])*Math.max(0,r[3]-r[1]),inter=area([Math.max(a[0],b[0]),Math.max(a[1],b[1]),Math.min(a[2],b[2]),Math.min(a[3],b[3])]);return inter/(area(a)+area(b)-inter+1e-9);}
