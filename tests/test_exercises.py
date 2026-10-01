"""Exercise-level motion tests. Coordinates describe idealized joint motion, not accuracy evidence."""
import json
from pathlib import Path
import numpy as np
import pytest
from core.engine import ExerciseEngine
from core.pose_result import PoseResult
from core.action_recognizer import ActionRecognizer
from core.feature_extractor import extract
from core.exercise_rules import RULES

def base():
    k=np.zeros((17,3),float);k[:,2]=.95
    for shift,ear,s,e,w,h,n,a in [(0,3,5,7,9,11,13,15),(10,4,6,8,10,12,14,16)]:
        k[s,:2]=[100+shift,50];k[ear,:2]=[100+shift,30];k[e,:2]=[80+shift,90];k[w,:2]=[70+shift,120];k[h,:2]=[100+shift,150];k[n,:2]=[100+shift,250];k[a,:2]=[100+shift,350]
    k[0,:2]=[100,25]
    return k

def frame(name,degree):
    k=base()
    for shift,ear,s,e,w,h,n,a in [(0,3,5,7,9,11,13,15),(10,4,6,8,10,12,14,16)]:
        if name in ('squat','lunge'):
            k[a,:2]=[100+shift+100*np.sin(np.radians(degree)),250-100*np.cos(np.radians(degree))]
            if name=='lunge':
                if shift==0:k[0,:2]=[140,25]
                else:k[a,:2]=[0,300]
        if name in ('plank','pushup'):
            k[s,:2]=[100+shift,110];k[h,:2]=[200+shift,110];k[a,:2]=[300+shift,110];k[n,:2]=[250+shift,110]
            k[e,:2]=[100+shift,160]
            k[w,:2]=[100+shift+50*np.sin(np.radians(degree)),160-50*np.cos(np.radians(degree))]
            k[ear,:2]=[70+shift,110]
        if name=='glute_bridge':
            k[s,:2]=[100+shift,100];k[h,:2]=[200+shift,100+degree];k[n,:2]=[300+shift,100];k[a,:2]=[300+shift,200];k[ear,:2]=[70+shift,100]
        if name=='crunch':
            k[s,:2]=[100+shift+degree,100-degree];k[h,:2]=[200+shift,100]
            k[n,:2]=[240+shift,120];k[a,:2]=[290+shift,110]
            k[ear,:2]=k[s,:2]+(k[s,:2]-k[h,:2])*.2
        if name in ('lateral_raise','jumping_jack'):
            rad=np.radians(degree)
            k[e,:2]=k[s,:2]+[50*np.sin(rad),50*np.cos(rad)]
            k[w,:2]=k[e,:2]+[40*np.sin(rad),40*np.cos(rad)]
            if name=='jumping_jack':
                spacing=10 if degree<20 else 90
                k[a,0]=100+(-spacing if shift==0 else spacing)
                k[n,0]=k[a,0]
        if name=='shoulder_press':
            k[e,:2]=k[s,:2]+[-35,-35]
            u=(k[s,:2]-k[e,:2])/np.linalg.norm(k[s,:2]-k[e,:2])
            rad=np.radians(degree);v=np.array([u[0]*np.cos(rad)-u[1]*np.sin(rad),u[0]*np.sin(rad)+u[1]*np.cos(rad)])
            k[w,:2]=k[e,:2]+60*v
    return PoseResult([0,0,400,400],k,.95)

def simulate(name,sequence,repeat=16):
    engine=ExerciseEngine(name);time=0.;outputs=[]
    for item in sequence:
        for _ in range(repeat):
            outputs.append(engine.update(frame(name,item),time));time+=.04
    return engine,outputs

@pytest.mark.parametrize('name,sequence',[
    ('squat',[170,160,135,110,90,110,130,160,170]),
    ('pushup',[170,165,140,115,90,110,140,160,170]),
    ('lateral_raise',[5,10,30,55,90,75,50,20,5]),
    ('shoulder_press',[100,100,120,145,170,150,125,105,100]),
    ('jumping_jack',[5,5,40,80,150,150,80,40,5]),
    ('glute_bridge',[75,65,50,25,0,0,25,50,75]),
    ('crunch',[0,5,15,25,50,50,25,10,0]),
])
def test_seven_cycle_signatures(name,sequence):
    e,outputs=simulate(name,sequence)
    assert e.machine.reps==1,(name,[x['state'] for x in outputs[::16]])
    assert len(e.session.current)==1
    assert 0<=e.session.current[0]['total_score']<=100


def test_plank_duration_and_score_separated():
    e,outputs=simulate('plank',[170]*10,repeat=6)
    assert outputs[-1]['state']=='HOLD'
    assert outputs[-1]['duration']>1
    assert 0<=outputs[-1]['quality_duration']<=outputs[-1]['duration']
    assert 0<=outputs[-1]['score']<=100


def test_plank_end_set_keeps_quality_and_starts_new_hold():
    e,outputs=simulate('plank',[170]*10,repeat=6)
    previous=e.hold
    row=e.finish_set(2.4)
    assert row['duration']==round(previous,1) and row['quality_seconds']==round(outputs[-1]['quality_duration'],1)
    assert row['average_score'] is not None and e.hold==0
    time=2.4
    for _ in range(25):e.update(frame('plank',170),time);time+=.04
    assert 0<e.hold<previous


def test_lunge_without_front_view_abstains():
    e,outputs=simulate('lunge',[170,140,100,170])
    assert outputs[-1]['reps']==0
    assert outputs[-1]['score'] is None


def test_lunge_with_visible_front_leg_counts():
    e,outputs=simulate('lunge',[170,170,150,120,90,90,120,150,170,170])
    assert outputs[-1]['reps']==1
    assert e.session.current[0]['total_score'] is not None


def test_auto_static_plank_recognition():
    r=ActionRecognizer();found=[]
    for i in range(100):found.append(r.update(frame('plank',170),i*.04))
    assert 'plank' in found


def test_partial_squat_prompt_without_count():
    e,outputs=simulate('squat',[170,170,140,130,155,170,170])
    assert e.machine.reps==0
    assert any('not counted' in row['feedback'] for row in outputs)


def test_plank_sag_and_pike_distinguished_in_side_view():
    flat=frame('plank',170)
    sag=flat.keypoints.copy();pike=flat.keypoints.copy()
    sag[[11,12],1]+=40;pike[[11,12],1]-=40
    f_sag=extract(sag,exercise='plank');f_pike=extract(pike,exercise='plank')
    assert f_sag['hip_sag']>.08 and f_sag['hip_pike']==0
    assert f_pike['hip_pike']>.08 and f_pike['hip_sag']==0


def test_auto_squat_after_temporal_evidence():
    r=ActionRecognizer();t=0.;found=[]
    for angle_value in [170,170,155,125,90,90,120,155,170]:
        for _ in range(13):
            found.append(r.update(frame('squat',angle_value),t));t+=.04
    assert 'squat' in found


def test_auto_mode_nine_idealized_motions():
    fixtures=json.loads((Path(__file__).parent/'assets/motion_sequences.json').read_text())
    for name,rows in fixtures.items():
        recognizer=ActionRecognizer();t=0.;guesses=set()
        for row in rows:
            k=np.array([[p['x'],p['y'],p['confidence']] for p in row['keypoints']])
            for _ in range(16):
                found=recognizer.update(PoseResult(row['bbox'],k,.95),t)
                if found:guesses.add(found)
                t+=.04
        assert guesses=={name},(name,guesses)


def test_all_rules_have_observable_weighted_dimensions():
    for name,config in RULES.items():
        assert sum(row[4] for row in config['rules'])==pytest.approx(1),name
        pose=frame(name,170 if name not in ('glute_bridge','crunch','lateral_raise','jumping_jack','shoulder_press') else 0)
        features=extract(pose.keypoints,exercise=name)
        # Missing dimensions are permitted; every movement must have a measurable primary signal.
        assert config['feature'] in features
