"""Run on the target computer, not a repeated-image throughput estimate."""
import argparse,json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import psutil
from core.camera import Camera
from pose_backends.onnx_pose import ONNXPoseEstimator
p=argparse.ArgumentParser();p.add_argument('--camera',type=int,default=0);p.add_argument('--seconds',type=float,default=15);p.add_argument('--model',default='models/pose_model.onnx');p.add_argument('--output',default='camera_benchmark.json');a=p.parse_args()
m=ONNXPoseEstimator(a.model);rows=[]
try:proc=psutil.Process()
except (psutil.Error,OSError):proc=None
for w,h in [(640,480),(480,360),(320,240)]:
    c=Camera(a.camera,w,h,30);last=0;count=0;lat=[];start=time.monotonic()
    if proc:proc.cpu_percent()
    try:
        while time.monotonic()-start<a.seconds:
            item=c.read()
            if item is None or item[0]==last:
                if c.eof:raise RuntimeError('Camera stopped')
                time.sleep(.002);continue
            last,t,frame=item;tic=time.perf_counter();m.infer(frame);lat.append((time.perf_counter()-tic)*1000);count+=1
        rows.append(dict(requested_resolution=[w,h],actual_resolution=[frame.shape[1],frame.shape[0]] if count else None,camera_fps=c.fps,pose_fps=count/(time.monotonic()-start),ui_fps=None,inference_ms=sum(lat)/len(lat) if lat else None,cpu_percent=proc.cpu_percent() if proc else None,memory_mb=proc.memory_info().rss/1024**2 if proc else None,gpu_utilization=None))
    finally:c.close()
Path(a.output).write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
