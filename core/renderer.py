import cv2,math
from .pose_result import EDGES

def draw(frame,pose,threshold=.45,debug=False,smoothed=None,features=None,exercise=None):
    out=frame.copy()
    if pose is None:return out
    k=pose.keypoints if smoothed is None else smoothed
    for a,b in EDGES:
        if min(k[a,2],k[b,2])>=threshold:cv2.line(out,tuple(k[a,:2].astype(int)),tuple(k[b,:2].astype(int)),(210,220,50),2,cv2.LINE_AA)
    for i in range(5,17):
        x,y,c=k[i]
        if c>=threshold:
            cv2.circle(out,(int(x),int(y)),4,(100,255,180),-1,cv2.LINE_AA)
            if debug:cv2.putText(out,f'{i}:{c:.2f}',(int(x)+5,int(y)-5),0,.35,(255,255,255),1,cv2.LINE_AA)
    angle_key={'squat':'knee','lunge':'front_knee','pushup':'elbow','plank':'body','glute_bridge':'bridge','crunch':'curl','lateral_raise':'arm_elevation','shoulder_press':'elbow','jumping_jack':'arm_elevation'}.get(exercise)
    value=features.get(angle_key) if features and angle_key else None
    if isinstance(value,(int,float)) and math.isfinite(value):
        side=features.get('front_side') if exercise=='lunge' else features.get('side')
        joint=(13 if side=='left' else 14) if exercise=='lunge' else (11 if side=='left' else 12) if exercise in ('plank','glute_bridge') else (7 if side=='left' else 8) if exercise in ('pushup','shoulder_press') else (5 if side=='left' else 6) if exercise in ('crunch','lateral_raise','jumping_jack') else (13 if side=='left' else 14)
        if k[joint,2]>=threshold:
            x,y=map(int,k[joint,:2]);label=f'{angle_key}: {value:.0f} deg';origin=(max(4,x+9),max(16,y-9))
            (w,h),_=cv2.getTextSize(label,cv2.FONT_HERSHEY_SIMPLEX,.48,1)
            cv2.rectangle(out,(origin[0]-3,origin[1]-h-3),(origin[0]+w+3,origin[1]+3),(20,32,40),-1)
            cv2.putText(out,label,origin,cv2.FONT_HERSHEY_SIMPLEX,.48,(180,245,195),1,cv2.LINE_AA)
    if debug:
        x,y,r,b=map(int,pose.bbox);cv2.rectangle(out,(x,y),(r,b),(130,130,255),1)
        if smoothed is not None:
            for x,y,c in pose.keypoints[5:]:
                if c>=threshold:cv2.circle(out,(int(x),int(y)),2,(255,100,100),1)
    return out
