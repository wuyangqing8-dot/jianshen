"""Image inference benchmark: does NOT claim camera or UI FPS."""
import argparse,json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cv2,numpy as np,psutil
from pose_backends.onnx_pose import ONNXPoseEstimator
p=argparse.ArgumentParser();p.add_argument('--image',default='tests/assets/person.jpg');p.add_argument('--model',default='models/pose_model.onnx');p.add_argument('--runs',type=int,default=50);p.add_argument('--output',default='docs/benchmark.json');a=p.parse_args()
m=ONNXPoseEstimator(a.model);im=cv2.imread(a.image)
if im is None:raise ValueError('Input image not found')
try: proc=psutil.Process()
except (psutil.Error, OSError): proc=None
rows=[]
for w,h in [(640,480),(480,360),(320,240)]:
    frame=cv2.resize(im,(w,h))
    for _ in range(5):m.infer(frame)
    if proc: proc.cpu_percent()
    start=time.perf_counter();times=[]
    for _ in range(a.runs):
        t=time.perf_counter();m.infer(frame);times.append((time.perf_counter()-t)*1000)
    elapsed=time.perf_counter()-start
    rows.append(dict(source_width=w,source_height=h,model_input=m.size,runs=a.runs,mean_inference_ms=float(np.mean(times)),p95_ms=float(np.percentile(times,95)),pose_throughput_fps=a.runs/elapsed,camera_fps=None,ui_fps=None,cpu_percent_process=proc.cpu_percent() if proc else None,memory_mb=proc.memory_info().rss/1024**2 if proc else None,gpu_utilization=None))
Path(a.output).write_text(json.dumps(dict(environment='Linux server CPU; not M2; repeated image test',results=rows),indent=2));print(json.dumps(rows,indent=2))
