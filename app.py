"""Tk desktop dashboard. Camera and inference have separate latest-frame workers."""
import argparse,csv,json,threading,time,queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
import yaml
from PIL import Image,ImageTk
from core.camera import Camera
from core.engine import ExerciseEngine
from core.action_recognizer import ActionRecognizer
from core.exercise_rules import RULES
from core.feedback import VoiceFeedback
from core.i18n import feedback_zh
from core.training_tools import COLUMNS,goal_progress,summary_rows
from core.renderer import draw
from pose_backends.onnx_pose import ONNXPoseEstimator

class Dashboard:
    def __init__(self,root,args):
        self.root=root;self.args=args;self.camera=None;self.model=None;self.running=False;self.paused=False;self.closed=False;self.result=None;self.error=None;self.lock=threading.Lock();self.commands=queue.Queue();self.voice=VoiceFeedback();self.pose_fps=0;self.latency=0;self.last_ui=time.monotonic();self.ui_fps=0;self.rendered_seq=-1;self.workout_history=[]
        self.cfg=yaml.safe_load(Path(__file__).with_name('config.yaml').read_text());self.engine=ExerciseEngine();self.recognizer=ActionRecognizer();self.exercise=tk.StringVar(value='squat');self.debug=tk.BooleanVar(value=False);self.voice_mode=tk.StringVar(value='mute');self.language=tk.StringVar(value='zh');self.source=tk.StringVar(value=args.source);self.goal=tk.IntVar(value=10)
        root.title('FORM / Local Fitness Coach');root.geometry('1200x800');root.configure(bg='#0d1421')
        style=ttk.Style();style.theme_use('clam');style.configure('TFrame',background='#0d1421');style.configure('TLabel',background='#0d1421',foreground='#dce5f4',font=('Arial',12));style.configure('TButton',font=('Arial',11),padding=9)
        head=ttk.Frame(root);head.pack(fill='x',padx=24,pady=18)
        ttk.Label(head,text='FORM  /  LOCAL FITNESS',font=('Arial',22,'bold')).pack(side='left');ttk.Label(head,text='ON DEVICE  •  NO VIDEO UPLOAD',foreground='#64dcc1').pack(side='right')
        body=ttk.Frame(root);body.pack(fill='both',expand=True,padx=24)
        self.video=tk.Label(body,bg='#141f31',fg='#b4c0d7',text='Choose an exercise and press Start\nCamera video stays on your device',font=('Arial',18));self.video.pack(side='left',fill='both',expand=True)
        side=ttk.Frame(body,width=300);side.pack(side='right',fill='y',padx=(24,0));side.pack_propagate(False)
        self.stats={}
        for name in ['Camera view','State','Reps / Hold','Goal','Score','Set / Average','Camera FPS','Pose FPS / latency','UI FPS']:
            ttk.Label(side,text=name,foreground='#889cb7').pack(anchor='w',pady=(12,2));v=ttk.Label(side,text='—',font=('Arial',18,'bold'));v.pack(anchor='w');self.stats[name]=v
        self.feedback=ttk.Label(root,text='Scoring rules are experimental; use the recommended camera view.',wraplength=1100);self.feedback.pack(fill='x',padx=24,pady=12)
        controls=ttk.Frame(root);controls.pack(fill='x',padx=24,pady=10)
        box=ttk.Combobox(controls,textvariable=self.exercise,values=['auto']+list(RULES),state='readonly',width=17);box.pack(side='left');box.bind('<<ComboboxSelected>>',self.change_exercise)
        for text,fn in [('Start',self.start),('Stop camera',self.stop),('Pause / Resume',self.pause),('Reset action',self.reset_exercise),('End set',self.end_set),('New session',self.new_workout),('Export JSON',self.export),('Export CSV',self.export_csv)]:ttk.Button(controls,text=text,command=fn).pack(side='left',padx=4)
        settings=ttk.Frame(root);settings.pack(fill='x',padx=24,pady=(0,15));ttk.Label(settings,text='Camera ID / video:').pack(side='left');ttk.Entry(settings,textvariable=self.source,width=15).pack(side='left');ttk.Button(settings,text='Scan cameras',command=self.scan_cameras).pack(side='left',padx=5);ttk.Button(settings,text='Video…',command=self.choose_video).pack(side='left',padx=5)
        ttk.Label(settings,text='Goal').pack(side='left',padx=(12,3));ttk.Spinbox(settings,from_=1,to=3600,textvariable=self.goal,width=5).pack(side='left')
        ttk.Label(settings,text='Voice').pack(side='left');ttk.Combobox(settings,textvariable=self.voice_mode,values=['mute','single','batch'],state='readonly',width=8).pack(side='left');ttk.Combobox(settings,textvariable=self.language,values=['en','zh'],state='readonly',width=4).pack(side='left');ttk.Checkbutton(settings,text='Debug',variable=self.debug).pack(side='left',padx=10)
        self.debug_text=ttk.Label(root,text='',wraplength=1140,font=('Arial',9));self.debug_text.pack(fill='x',padx=24)
        root.protocol('WM_DELETE_WINDOW',self.close);self.tick()
    def choose_video(self):
        path=filedialog.askopenfilename(filetypes=[('Video','*.mp4 *.avi *.mov'),('All','*')])
        if path:self.source.set(path)
    def change_exercise(self,_=None):
        self.goal.set(30 if self.exercise.get()=='plank' else 10)
        if self.running:self.commands.put(('exercise',self.exercise.get()))
        else:
            with self.lock:self.select_exercise_locked(self.exercise.get())
    def reset_exercise(self):
        if self.running:self.commands.put(('reset',self.exercise.get()))
        else:
            with self.lock:self.select_exercise_locked(self.exercise.get())
    def end_set(self):
        if self.running:self.commands.put(('end',None))
        else:
            with self.lock:
                if self.engine:
                    self.engine.finish_set(time.monotonic())
                    self.result=None
    def select_exercise_locked(self,value):
        if self.engine:
            self.engine.finish_set(time.monotonic())
            previous=self.result[2].get('score') if self.result else None
            self.workout_history.extend({**row,'status':'completed'} for row in summary_rows(self.engine,previous))
        self.recognizer.reset()
        m=self.cfg['pose_model']
        self.engine=None if value=='auto' else ExerciseEngine(value,m['keypoint_confidence'],self.cfg.get('filter'))
        self.result=None
    def clear_workout_locked(self,value):
        self.workout_history.clear();self.engine=None
        self.select_exercise_locked(value)
    def new_workout(self):
        with self.lock:has_data=bool(self.workout_history or summary_rows(self.engine,self.result[2].get('score') if self.result else None))
        if has_data and not messagebox.askyesno('新训练','清空当前训练记录？未导出的记录将丢失。'):return
        if self.running:self.commands.put(('new',self.exercise.get()))
        else:
            with self.lock:self.clear_workout_locked(self.exercise.get())
        self.feedback.config(text='新训练已开始')
    def scan_cameras(self):
        if self.running:
            self.feedback.config(text='先关闭摄像头，再扫描可用设备')
            return
        found=Camera.discover()
        if found:
            if self.source.get()=='auto':self.source.set(str(found[0]))
            self.feedback.config(text='可用摄像头 ID：'+', '.join(map(str,found)))
        else:self.feedback.config(text='未找到可用摄像头；检查权限或选择视频文件')
    def start(self):
        if self.running:return
        if hasattr(self,'worker') and self.worker.is_alive():
            self.feedback.config(text='正在关闭上一段输入，稍后启动…')
            self.root.after(100,self.start)
            return
        self.error=None;self.running=True;self.paused=False;self.feedback.config(text='Loading local model and opening input…')
        source=self.source.get();self.worker=threading.Thread(target=self.work,args=(source,),daemon=True);self.worker.start()
    def work(self,source):
        camera=None
        try:
            m=self.cfg['pose_model'];self.model=ONNXPoseEstimator(self.args.model or Path(__file__).parent/m['path'],m['confidence'],threads=m['threads']);camera=Camera(int(source) if source.isdecimal() else source,**self.cfg['camera']);self.camera=camera;last=0;n=0;begin=time.monotonic()
            while self.running:
                while not self.commands.empty():
                    command,value=self.commands.get()
                    with self.lock:
                        if command in ['exercise','reset']:
                            self.select_exercise_locked(value)
                        elif command=='new':self.clear_workout_locked(value)
                        elif command=='end' and self.engine:
                            self.engine.finish_set(time.monotonic())
                            self.result=None
                if self.paused:
                    with self.lock:
                        if self.engine:self.engine.invalidate()
                        self.recognizer.reset();self.result=None
                    time.sleep(.03);continue
                item=camera.read()
                if item is None or last==item[0]:
                    if camera.eof:break
                    time.sleep(.003);continue
                last,t,frame=item;tic=time.perf_counter();pose=self.model.infer(frame);self.latency=(time.perf_counter()-tic)*1000;n+=1;self.pose_fps=n/max(time.monotonic()-begin,.001)
                if not self.running:break
                with self.lock:
                    if self.engine is None:
                        guessed=self.recognizer.update(pose,t)
                        if guessed:
                            self.engine=ExerciseEngine(guessed,m['keypoint_confidence'],self.cfg.get('filter'))
                        result=dict(state='IDENTIFYING' if guessed is None else 'READY',reps=0,score=None,
                                    feedback=('先做一次清晰的动作供系统识别；从下一次开始计数' if guessed is None else f'已识别 {guessed}，回到起始姿势后再开始') if self.voice.language=='zh' else ('Perform one clear movement to identify it; counting starts on the next rep' if guessed is None else f'Identified {guessed}. Return to start position.'),
                                    completed=False,features={},keypoints=pose.keypoints if pose else None)
                    else:result=self.engine.update(pose,t)
                    self.result=(t,pose,result)
                if result['completed']:
                    msg=f"第{result['reps']}次，评分{result['score']}。{feedback_zh(self.engine.exercise,result.get('detected_errors',[]),'动作完成')}" if self.voice.language=='zh' else f"Rep {result['reps']}. {result['feedback']}"
                    self.voice.speak(msg,result['reps'])
        except Exception as exc:self.error=str(exc)
        finally:
            if camera:camera.close()
            if self.camera is camera:self.camera=None
            self.running=False
    def stop(self):
        if self.running:
            with self.lock:
                if self.engine:self.engine.finish_set(time.monotonic())
                self.result=None
            self.running=False
            self.feedback.config(text='Camera closed')
    def pause(self):self.paused=not self.paused
    def export(self):
        path=filedialog.asksaveasfilename(defaultextension='.json',initialfile='training.json')
        if path:
            with self.lock:
                e=self.engine;last=self.result[2].get('score') if self.result else None
                data=dict(workout_summary=self.workout_history+summary_rows(e,last),exercise=e.exercise if e else 'identifying',goal=self.goal.get(),sets=e.session.sets if e else [],current_reps=e.session.current if e else [],hold_seconds=e.hold if e else 0,quality_hold_seconds=e.quality_hold if e else 0)
            Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    def export_csv(self):
        with self.lock:
            latest_score=self.result[2].get('score') if self.result else None
            rows=self.workout_history+summary_rows(self.engine,latest_score)
        if not rows:
            self.feedback.config(text='暂无训练记录；完成一次动作后再导出')
            return
        path=filedialog.asksaveasfilename(defaultextension='.csv',initialfile='training_summary.csv',filetypes=[('CSV','*.csv')])
        if path:
            with open(path,'w',newline='',encoding='utf-8-sig') as f:
                writer=csv.DictWriter(f,fieldnames=COLUMNS);writer.writeheader();writer.writerows(rows)
    def tick(self):
        if self.closed:return
        now=time.monotonic();self.voice.mode=self.voice_mode.get();self.voice.language=self.language.get()
        if self.error:self.feedback.config(text=self.error)
        camera=self.camera;item=camera.read() if camera else None
        with self.lock:
            latest=self.result;e=self.engine;ex=e.exercise if e else 'auto';sets=len(e.session.sets) if e else 0;scores=[r['total_score'] for r in e.session.current if r['total_score'] is not None] if e else []
        if item and item[0]!=self.rendered_seq:
            self.rendered_seq=item[0];self.ui_fps=1/max(now-self.last_ui,.001);self.last_ui=now
            valid=latest is not None and now-latest[0]<.5 and not self.paused
            pose=latest[1] if valid else None;r=latest[2] if valid else {}
            frame=draw(item[2],pose,self.cfg['pose_model']['keypoint_confidence'],self.debug.get(),r.get('keypoints'),r.get('features'),ex)
            im=Image.fromarray(frame[:,:,::-1]);im.thumbnail((max(320,self.video.winfo_width()),max(240,self.video.winfo_height())));photo=ImageTk.PhotoImage(im);self.video.config(image=photo,text='');self.video.image=photo
            try:target=self.goal.get()
            except tk.TclError:target=30 if ex=='plank' else 10
            progress=goal_progress(ex,len(e.session.current) if e else 0,e.hold if e else 0,target)
            goal_label=f"{progress['progress']:.1f}" if ex=='plank' else str(int(progress['progress']))
            values={'Camera view':RULES[ex]['view'] if ex in RULES else 'Full body / 全身','State':'PAUSED' if self.paused else r.get('state','WAITING'),'Reps / Hold':f"{r.get('duration',0):.1f} s" if ex=='plank' else str(r.get('reps',0)),'Goal':f"{goal_label} / {progress['target']} {progress['unit']}"+(' ✓' if progress['reached'] else ''),'Score':str(r.get('score') if r.get('score') is not None else '—'),'Set / Average':f"{sets+1} / {sum(scores)/len(scores):.1f}" if scores else f'{sets+1} / —','Camera FPS':f'{camera.fps:.1f}','Pose FPS / latency':f'{self.pose_fps:.1f} / {self.latency:.0f} ms','UI FPS':f'{self.ui_fps:.1f}'}
            for k,v in values.items():self.stats[k].config(text=v)
            if not self.error:
                message=r.get('feedback','Paused' if self.paused else 'Waiting for pose')
                if self.language.get()=='zh' and ex in RULES:message=feedback_zh(ex,r.get('detected_errors',[]),message)
                self.feedback.config(text=message)
            self.debug_text.config(text=json.dumps(dict(raw=r.get('raw_features'),smoothed=r.get('features'),model_input=self.model.size if self.model else None,inference_ms=self.latency),ensure_ascii=False)[:1300] if self.debug.get() else '')
        self.root.after(16,self.tick)
    def close(self):self.closed=True;self.running=False;self.root.destroy()

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',default='auto');p.add_argument('--model');a=p.parse_args();root=tk.Tk();Dashboard(root,a);root.mainloop()
if __name__=='__main__':main()
