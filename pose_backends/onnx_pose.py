from pathlib import Path
import cv2
import numpy as np
import onnxruntime as ort
from core.pose_result import PoseResult
from .base_pose import PoseEstimator

class ONNXPoseEstimator(PoseEstimator):
    """Adapter for YOLOv8 COCO17, float32 NCHW, raw [1,56,N], no embedded NMS."""
    def __init__(self,path,confidence=.4,iou=.45,threads=2):
        self.confidence=confidence; self.iou=iou; self.threads=threads; self.last_result=None
        self.load_model(path)
    def load_model(self,path):
        if not Path(path).is_file():
            raise FileNotFoundError(f'Model missing: {path}. Extract the complete project archive and verify models/pose_model.onnx.')
        opts=ort.SessionOptions(); opts.intra_op_num_threads=self.threads
        self.session=ort.InferenceSession(str(path),sess_options=opts,providers=['CPUExecutionProvider'])
        inp=self.session.get_inputs()[0]; self.name=inp.name
        if len(inp.shape)!=4 or inp.shape[1]!=3 or not isinstance(inp.shape[2],int) or inp.shape[2]!=inp.shape[3]:
            raise ValueError('Expected static square NCHW model; export with dynamic=False.')
        self.size=inp.shape[2]
    def preprocess(self,frame):
        h,w=frame.shape[:2]; s=min(self.size/w,self.size/h)
        nw,nh=round(w*s),round(h*s); left=(self.size-nw)//2; top=(self.size-nh)//2
        out=np.full((self.size,self.size,3),114,np.uint8)
        out[top:top+nh,left:left+nw]=cv2.resize(frame,(nw,nh))
        tensor=np.ascontiguousarray(out[:,:,::-1].transpose(2,0,1)[None],dtype=np.float32)/255.
        return tensor,(nw/w,nh/h,left,top,w,h)
    def postprocess(self,outputs,transform):
        a=np.asarray(outputs[0])[0]
        if a.shape[0]==56: a=a.T
        if a.ndim!=2 or a.shape[1]!=56: raise ValueError(f'Unsupported output {a.shape}; expected YOLOv8 [56,N].')
        a=a[np.isfinite(a).all(axis=1)&(a[:,4]>=self.confidence)]
        if not len(a): return None
        boxes=np.column_stack((a[:,0]-a[:,2]/2,a[:,1]-a[:,3]/2,a[:,2:4]))
        ids=cv2.dnn.NMSBoxes(boxes.tolist(),a[:,4].tolist(),self.confidence,self.iou)
        ids=np.asarray(ids).reshape(-1)
        if not len(ids): return None
        row=a[ids[np.argmax(a[ids,4])]]; sx,sy,px,py,w,h=transform
        k=row[5:].reshape(17,3).copy(); k[:,0]=(k[:,0]-px)/sx; k[:,1]=(k[:,1]-py)/sy
        outside=(k[:,0]<0)|(k[:,0]>=w)|(k[:,1]<0)|(k[:,1]>=h); k[outside,2]=0
        box=[float((row[0]-row[2]/2-px)/sx),float((row[1]-row[3]/2-py)/sy),float((row[0]+row[2]/2-px)/sx),float((row[1]+row[3]/2-py)/sy)]
        return PoseResult(box,k,float(row[4]),len(ids))
    def infer(self,frame):
        x,t=self.preprocess(frame); self.last_result=self.postprocess(self.session.run(None,{self.name:x}),t)
        return self.last_result
