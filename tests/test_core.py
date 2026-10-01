import numpy as np
import pytest
from core.geometry import angle,point_to_line_distance_normalized
from core.filtering import TemporalFilter
from core.state_machine import ExerciseStateMachine,CycleConfig
from core.scoring import ScoringEngine
from core.session import TrainingSession
from core.training_tools import goal_progress,summary_rows
from core.camera import Camera
from core.engine import ExerciseEngine
from core.pose_result import PoseResult
from pose_backends.onnx_pose import ONNXPoseEstimator

def feed(machine,values):
    t=0
    for v in values:
        for _ in range(5):machine.update(v,t);t+=.04
    return machine.reps

def test_geometry():
    assert angle([1,0],[0,0],[0,1])==pytest.approx(90)
    assert angle([0,0],[1,0],[2,0])==pytest.approx(180)
    assert angle([0,0],[0,0],[1,0]) is None
    assert point_to_line_distance_normalized([1,1],[0,0],[2,0])==pytest.approx(.5)

def test_filter_missing_resets():
    f=TemporalFilter();assert f.update('a',10)==10;assert f.update('a',20)==15
    assert f.update('a',None) is None;assert f.update('a',100)==100

def test_squat_cycle():
    m=ExerciseStateMachine();assert feed(m,[170,165,150,130,115,100,90,95,110,130,155,170])==1

def test_jitter():
    assert feed(ExerciseStateMachine(),[170,149,151,148,152,150,153])==0

def test_no_initial_stand():
    assert feed(ExerciseStateMachine(),[90,110,130,170])==0

def test_partial_cycle():
    assert feed(ExerciseStateMachine(),[170,140,130,150,170])==0

def test_dropout_cancels():
    assert feed(ExerciseStateMachine(),[170,140,90,None,130,170])==0

def test_reverse_cycle():
    assert feed(ExerciseStateMachine(CycleConfig(low=20,high=75,increasing=True)),[10,30,60,80,60,30,10])==1

def test_timeout_reset():
    m=ExerciseStateMachine(CycleConfig(timeout_seconds=.5));feed(m,[170,140])
    for i in range(20):m.update(140,.4+i*.1)
    assert m.phase==0 and not m.armed

def test_score_missing_and_continuous():
    e=ScoringEngine();rules=[('a',80,100,2,1,'error')]
    assert e.evaluate({},rules)['total_score'] is None
    assert e.evaluate({'a':110},rules)['total_score']==80
    assert e.evaluate({'a':1000},rules)['total_score']==0

def test_session_idle():
    s=TrainingSession();s.add(dict(total_score=90,detected_errors=[],duration=2),10)
    assert s.idle(21,True) is None
    assert s.idle(23,False) is None
    assert s.idle(23,True)['reps']==1

def test_plank_missing_no_time():
    e=ExerciseEngine('plank');assert e.update(None,1)['score'] is None;assert e.hold==0

def test_multi_person_no_score():
    e=ExerciseEngine();p=PoseResult([0,0,100,100],np.ones((17,3)),.9,2)
    assert e.update(p,1)['score'] is None

def test_letterbox_and_nms():
    # Exercise real preprocessing/postprocessing, bypass model loading only.
    m=object.__new__(ONNXPoseEstimator);m.size=320;m.confidence=.4;m.iou=.45
    x,t=m.preprocess(np.zeros((480,640,3),np.uint8));assert x.shape==(1,3,320,320)
    row=np.zeros(56,np.float32);row[:5]=[160,160,100,200,.9];row[5:]=np.tile([160,160,.8],17)
    result=m.postprocess([np.stack([row,row],axis=1)[None]],t)
    assert result.person_count==1
    assert result.keypoints[0,0]==pytest.approx(320)
    assert result.keypoints[0,1]==pytest.approx(240)

def test_outside_frame_invalid():
    m=object.__new__(ONNXPoseEstimator);m.confidence=.4;m.iou=.45
    r=np.zeros((1,56,1),np.float32);r[0,:5,0]=[160,160,100,100,.9];r[0,5:,0]=np.tile([160,10,.9],17)
    p=m.postprocess([r],(.5,.5,0,40,640,480));assert (p.keypoints[:,2]==0).all()

def squat_pose(degrees):
    k=np.zeros((17,3));k[:,2]=.95
    for delta,s,e,w,h,n,a in [(0,5,7,9,11,13,15),(80,6,8,10,12,14,16)]:
        k[s,:2]=[100+delta,30];k[e,:2]=[80+delta,60];k[w,:2]=[70+delta,90];k[h,:2]=[100+delta,100];k[n,:2]=[100+delta,200]
        k[a,:2]=[100+delta+100*np.sin(np.radians(degrees)),200-100*np.cos(np.radians(degrees))]
    return PoseResult([0,0,400,400],k,.95)

def test_full_engine_squat():
    e=ExerciseEngine();t=0
    for v in [170,165,150,130,115,100,90,95,110,130,155,170]:
        for _ in range(10):r=e.update(squat_pose(v),t);t+=.04
    assert r['reps']==1 and r['score'] is not None
    assert len(e.session.current)==1

def test_standing_is_not_plank():
    e=ExerciseEngine('plank');r=e.update(squat_pose(180),0)
    assert r['score'] is None and e.hold==0

def test_real_model_image():
    from pathlib import Path
    import cv2
    root=Path(__file__).resolve().parents[1]
    if not (root/'models/pose_model.onnx').exists():pytest.skip('Model not installed')
    model=ONNXPoseEstimator(root/'models/pose_model.onnx')
    p=model.infer(cv2.imread(str(root/'tests/assets/person.jpg')))
    assert p is not None and p.keypoints.shape==(17,3)
    assert np.isfinite(p.keypoints).all()

def test_webcam_one_failed_read_recovers(monkeypatch):
    import time
    class TemporaryFailure:
        attempts=0
        def isOpened(self):return True
        def set(self,*_):pass
        def get(self,*_):return float('nan')
        def read(self):
            self.attempts+=1
            if self.attempts==1:return False,None
            time.sleep(.01)
            return True,np.zeros((16,16,3),np.uint8)
        def release(self):pass
    cap=TemporaryFailure()
    monkeypatch.setattr('core.camera.cv2.VideoCapture',lambda _:cap)
    camera=Camera(0)
    try:
        deadline=time.monotonic()+1
        while camera.read() is None and time.monotonic()<deadline:time.sleep(.01)
        assert camera.read() is not None and not camera.eof
        assert camera.rate==30
    finally:camera.close()

def test_goal_and_export_rows_do_not_contain_pose_data():
    e=ExerciseEngine('squat')
    e.session.add(dict(total_score=88,detected_errors=['depth'],duration=2),10)
    progress=goal_progress('squat',len(e.session.current),999,1)
    assert progress['reached'] and progress['unit']=='次'
    rows=summary_rows(e)
    assert len(rows)==1 and rows[0]['status']=='current' and rows[0]['main_error']=='depth'
    assert 'keypoints' not in rows[0]
    e.session.finish(10)
    assert summary_rows(e)[0]['status']=='completed'
    p=ExerciseEngine('plank');p.hold=35.;p.quality_hold=20.
    assert goal_progress('plank',0,p.hold,30)['reached']
    assert summary_rows(p,75)[0]['quality_seconds']==20.

def test_desktop_exercise_switch_archives_previous_set():
    from app import Dashboard
    from core.action_recognizer import ActionRecognizer
    d=object.__new__(Dashboard)
    d.cfg={'pose_model':{'keypoint_confidence':.45},'filter':{'window':5,'mode':'moving','alpha':.4}}
    d.engine=ExerciseEngine('squat');d.engine.session.add(dict(total_score=88,detected_errors=[],duration=2),10)
    d.result=(10,None,{'score':88});d.workout_history=[];d.recognizer=ActionRecognizer()
    d.select_exercise_locked('plank')
    assert d.engine.exercise=='plank' and d.workout_history[0]['exercise']=='squat'
    assert d.workout_history[0]['reps']==1 and d.workout_history[0]['status']=='completed'
    d.clear_workout_locked('squat')
    assert d.workout_history==[] and d.engine.exercise=='squat'
