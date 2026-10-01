"""Deterministic offline analysis: every frame, source timestamps, no camera dropping."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cv2
from core.engine import ExerciseEngine
from core.exercise_rules import RULES
from pose_backends.onnx_pose import ONNXPoseEstimator
p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--exercise',choices=RULES,default='squat');p.add_argument('--model',default='models/pose_model.onnx');p.add_argument('--output',default='video_results.json');a=p.parse_args()
cap=cv2.VideoCapture(a.video)
if not cap.isOpened():raise ValueError('Cannot open video')
fps=cap.get(cv2.CAP_PROP_FPS) or 30;model=ONNXPoseEstimator(a.model);engine=ExerciseEngine(a.exercise);events=[];i=0
while True:
    ok,frame=cap.read()
    if not ok:break
    t=i/fps;r=engine.update(model.infer(frame),t)
    if r['completed']:events.append(dict(timestamp=t,rep=r['reps'],score=r['score'],feedback=r['feedback']))
    i+=1
cap.release();hold_seconds=engine.hold;quality_hold_seconds=engine.quality_hold;engine.finish_set(i/fps)
Path(a.output).write_text(json.dumps(dict(exercise=a.exercise,frames=i,source_fps=fps,events=events,sets=engine.session.sets,hold_seconds=hold_seconds,quality_hold_seconds=quality_hold_seconds),indent=2))
print(f'Processed {i} frames; wrote {a.output}')
