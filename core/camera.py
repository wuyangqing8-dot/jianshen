import threading,time,math
import cv2
class Camera:
    def __init__(self,source=0,width=640,height=480,fps=30):
        if source=='auto':
            found=self.discover()
            if not found:raise RuntimeError('No local camera found. Check camera permissions or use a video file.')
            source=found[0]
        self.source=source; self.cap=cv2.VideoCapture(source)
        if not self.cap.isOpened():raise RuntimeError(f'Cannot open camera/video: {source}. Check permissions, camera ID or path.')
        self.file=isinstance(source,str)
        if not self.file:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,width); self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height); self.cap.set(cv2.CAP_PROP_FPS,fps)
        reported_rate=self.cap.get(cv2.CAP_PROP_FPS)
        self.rate=reported_rate if math.isfinite(reported_rate) and reported_rate>0 else fps
        self.fps=0; self.lock=threading.Lock(); self.latest=None; self.running=True; self.eof=False
        self.thread=threading.Thread(target=self._run,daemon=True); self.thread.start()
    def _run(self):
        seq=0; start=time.monotonic(); failed_since=None
        while self.running:
            ok,frame=self.cap.read()
            if not ok:
                if self.file:self.eof=True;break
                if failed_since is None:failed_since=time.monotonic()
                if time.monotonic()-failed_since>=1.5:self.eof=True;break
                time.sleep(.03);continue
            failed_since=None
            seq+=1; t=time.monotonic()
            with self.lock:self.latest=(seq,t,frame)
            self.fps=seq/max(t-start,.001)
            if self.file:
                delay=start+seq/self.rate-time.monotonic()
                if delay>0:time.sleep(delay)
        self.running=False
    def read(self):
        with self.lock:return self.latest
    def close(self):
        self.running=False; self.thread.join(timeout=2); self.cap.release()
    @staticmethod
    def discover(limit=4):
        found=[]
        for i in range(limit):
            c=cv2.VideoCapture(i)
            if c.isOpened():
                ok,_=c.read()
                if ok:found.append(i)
            c.release()
        return found
