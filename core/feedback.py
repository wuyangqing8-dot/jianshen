import platform,subprocess,queue,threading,time
class VoiceFeedback:
    def __init__(self,language='en',mode='mute'):
        self.language=language; self.mode=mode; self.q=queue.Queue(maxsize=1); self.last=0
        threading.Thread(target=self._worker,daemon=True).start()
    def speak(self,text,reps=1):
        if self.mode=='mute' or (self.mode=='batch' and reps%5) or time.monotonic()-self.last<2:return
        try:self.q.put_nowait(text); self.last=time.monotonic()
        except queue.Full:pass
    def _worker(self):
        while True:
            text=self.q.get()
            try:
                if platform.system()=='Darwin':subprocess.run(['say','-v','Tingting' if self.language=='zh' else 'Samantha',text],timeout=12,check=False)
                elif platform.system()=='Windows':
                    script='[Console]::InputEncoding=New-Object System.Text.UTF8Encoding($false); Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; try { $s.SelectVoiceByHints(0,0,0,(New-Object System.Globalization.CultureInfo($args[0]))) } catch {} ; $s.Speak([Console]::In.ReadToEnd())'
                    subprocess.run(['powershell','-NoProfile','-Command',script,'zh-CN' if self.language=='zh' else 'en-US'],input=text,text=True,encoding='utf-8',timeout=12,check=False)
            except (OSError,subprocess.TimeoutExpired):pass
