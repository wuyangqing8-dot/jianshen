"""Local pose milestone: python pose_camera.py [--source video.mp4] [--headless]."""
import argparse,time,json
from pathlib import Path
import cv2,yaml
from pose_backends.onnx_pose import ONNXPoseEstimator
from core.renderer import draw
from core.camera import Camera

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',default='auto');p.add_argument('--model');p.add_argument('--headless',action='store_true');p.add_argument('--frames',type=int,default=0);p.add_argument('--output');p.add_argument('--list-cameras',action='store_true');p.add_argument('--config',default=str(Path(__file__).with_name('config.yaml')));a=p.parse_args()
    if a.list_cameras:print(Camera.discover());return
    cfg=yaml.safe_load(Path(a.config).read_text()); m=cfg['pose_model'];root=Path(a.config).resolve().parent
    model=ONNXPoseEstimator(a.model or root/m['path'],m['confidence'],threads=m['threads'])
    source=int(a.source) if a.source.isdecimal() else a.source;c=Camera(source,**cfg['camera']);writer=None;count=0;last=0;lat=[];start=time.monotonic();detected=0
    try:
        while True:
            item=c.read()
            if item is None or item[0]==last:
                if c.eof:break
                time.sleep(.002);continue
            last,t,frame=item;tic=time.perf_counter();pose=model.infer(frame);ms=(time.perf_counter()-tic)*1000;lat.append(ms);count+=1;detected+=pose is not None
            out=draw(frame,pose,m['keypoint_confidence'],True)
            cv2.putText(out,f'Camera {c.fps:.1f} | Pose {count/(time.monotonic()-start):.1f} FPS | {ms:.1f} ms',(10,25),0,.5,(255,255,255),1)
            if a.output:
                if writer is None:
                    writer=cv2.VideoWriter(a.output,cv2.VideoWriter_fourcc(*'mp4v'),c.rate,(out.shape[1],out.shape[0]))
                    if not writer.isOpened():raise RuntimeError('Cannot create output video')
                writer.write(out)
            if not a.headless:
                cv2.imshow('Local Pose - Q to quit',out)
                if cv2.waitKey(1)&255==ord('q'):break
            if a.frames and count>=a.frames:break
    finally:
        c.close()
        if writer:writer.release()
        if not a.headless:cv2.destroyAllWindows()
    print(json.dumps(dict(frames=count,detected_frames=detected,mean_inference_ms=sum(lat)/len(lat) if lat else None,pose_fps=count/max(time.monotonic()-start,.001)),indent=2))
if __name__=='__main__':main()
