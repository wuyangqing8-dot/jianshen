import numpy as np

def angle(a,b,c):
    u,v=np.asarray(a)-np.asarray(b),np.asarray(c)-np.asarray(b)
    den=np.linalg.norm(u)*np.linalg.norm(v)
    return None if den<1e-8 else float(np.degrees(np.arccos(np.clip(u@v/den,-1,1))))

def point_to_line_distance_normalized(p,a,b):
    p,a,b=map(np.asarray,(p,a,b)); v=b-a; den=float(v@v)
    return None if den<1e-8 else float(abs(v[0]*(p-a)[1]-v[1]*(p-a)[0])/den)

def vertical_angle(a,b):
    v=np.asarray(a)-np.asarray(b)
    return None if np.linalg.norm(v)<1e-8 else float(np.degrees(np.arctan2(abs(v[0]),abs(v[1]))))
