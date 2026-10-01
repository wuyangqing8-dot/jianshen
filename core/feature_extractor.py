"""Observable 2D COCO17 features. All distances are scale-free."""
import numpy as np
from .geometry import angle, vertical_angle, point_to_line_distance_normalized

SIDE_IDS={'left':(5,7,9,11,13,15,3),'right':(6,8,10,12,14,16,4)}

def extract(k,threshold=.45,preferred_side=None,exercise='squat'):
    def ok(*ids):return all(np.isfinite(k[i]).all() and k[i,2]>=threshold for i in ids)
    def dist(i,j):return float(np.linalg.norm(k[i,:2]-k[j,:2])) if ok(i,j) else None
    f={};quality={}
    for side,(s,e,w,h,n,a,ear) in SIDE_IDS.items():
        relevant={'squat':(s,h,n,a),'lunge':(s,h,n,a),'pushup':(s,e,w,h,a),'plank':(s,e,h,a),'glute_bridge':(s,h,n,a),'crunch':(s,h,n,a),'lateral_raise':(s,e,w,h),'shoulder_press':(s,e,w,h),'jumping_jack':(s,w,h,a)}.get(exercise,(s,h,n,a))
        quality[side]=min(float(k[i,2]) for i in relevant)
        for name,ids in [('knee',(h,n,a)),('elbow',(s,e,w)),('hip',(s,h,n)),('shoulder',(e,s,h)),('body',(s,h,a)),('bridge',(s,h,n)),('head',(ear,s,h))]:
            f[side+'_'+name]=angle(*(k[i,:2] for i in ids)) if ok(*ids) else None
        f[side+'_lean']=vertical_angle(k[s,:2],k[h,:2]) if ok(s,h) else None
        f[side+'_offset']=point_to_line_distance_normalized(k[h,:2],k[s,:2],k[a,:2]) if ok(s,h,a) else None
        f[side+'_hip_sag']=None;f[side+'_hip_pike']=None
        if ok(s,h,a):
            horizontal=float(k[a,0]-k[s,0]);line=float(np.linalg.norm(k[a,:2]-k[s,:2]))
            if line>1e-8 and abs(horizontal)>line*.3:
                projection=float((k[h,0]-k[s,0])/horizontal)
                if 0<=projection<=1:
                    signed=float((k[h,1]-k[s,1]-projection*(k[a,1]-k[s,1]))/line)
                    f[side+'_hip_sag']=max(0,signed)
                    f[side+'_hip_pike']=max(0,-signed)
        scale=dist(s,h)
        f[side+'_shoulder_y']=float((k[s,1]-k[a,1])/scale) if scale and ok(a) else None
        f[side+'_hip_y']=float((k[h,1]-k[s,1])/scale) if scale else None
        f[side+'_wrist_height']=float((k[s,1]-k[w,1])/scale) if scale and ok(w) else None
        f[side+'_ankle_distance']=float((k[a,0]-k[h,0])/scale) if scale and ok(a) else None
    if preferred_side in quality and quality[preferred_side]>=threshold:side=preferred_side
    else:side=max(quality,key=quality.get)
    f['side']=side
    for name in ('knee','elbow','hip','shoulder','body','bridge','head','lean','offset','hip_sag','hip_pike','shoulder_y','hip_y','wrist_height','ankle_distance'):
        f[name]=f[side+'_'+name]
    for name in ('knee','elbow','shoulder','wrist_height','hip_y'):
        left,right=f['left_'+name],f['right_'+name]
        f[name+'_asymmetry']=abs(left-right) if left is not None and right is not None else None
    if ok(5,6,11,12):
        shoulder=(k[5,:2]+k[6,:2])/2;hip=(k[11,:2]+k[12,:2])/2
        scale=float(np.linalg.norm(shoulder-hip))
    else:scale=dist(SIDE_IDS[side][0],SIDE_IDS[side][3])
    feet=dist(15,16)
    f['feet']=feet/scale if scale and feet is not None else None
    f['wrist_asymmetry']=float(abs(k[9,1]-k[10,1])/scale) if scale and ok(9,10) else None
    f['arm_elevation']=min(f['left_shoulder'],f['right_shoulder']) if f['left_shoulder'] is not None and f['right_shoulder'] is not None else None
    f['wrist_height']=min(f['left_wrist_height'],f['right_wrist_height']) if f['left_wrist_height'] is not None and f['right_wrist_height'] is not None else None
    f['curl']=90-f['lean'] if f['lean'] is not None else None
    f['jack']=min(f['arm_elevation']/150,f['feet']/1.5) if f['arm_elevation'] is not None and f['feet'] is not None else None
    f['front_knee']=None;f['rear_knee']=None;f['front_side']=None
    if scale and ok(0,5,6,15,16) and all(f[s+'_knee'] is not None for s in ('left','right')):
        facing=float(k[0,0]-(k[5,0]+k[6,0])/2)
        separation=float(abs(k[15,0]-k[16,0]))
        if abs(facing)>scale*.12 and separation>scale*.5:
            front='left' if (k[15,0]-k[16,0])*facing>0 else 'right'
            rear='right' if front=='left' else 'left'
            f['front_knee']=f[front+'_knee'];f['rear_knee']=f[rear+'_knee'];f['front_side']=front
    return f
