"""One-time network setup. The running app never downloads models."""
from pathlib import Path
import argparse, shutil, hashlib, json
p=argparse.ArgumentParser(); p.add_argument('--size',type=int,default=320); args=p.parse_args()
from ultralytics import YOLO
root=Path(__file__).resolve().parents[1]; dest=root/'models/pose_model.onnx'; dest.parent.mkdir(exist_ok=True)
model=YOLO('yolov8n-pose.pt')
path=model.export(format='onnx',imgsz=args.size,opset=17,simplify=False,dynamic=False,nms=False)
shutil.copy2(path,dest)
(root/'models/manifest.json').write_text(json.dumps(dict(architecture='YOLOv8n-pose',input_size=args.size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),source='https://github.com/ultralytics/assets',license='Ultralytics AGPL-3.0 / enterprise; see upstream terms'),indent=2))
print(dest)
