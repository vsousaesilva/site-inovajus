"""Mix: intro audio + narration (v2/audio/<id>.wav at timeline positions) + music with ducking. Output v2/mix_final.wav (-16 LUFS)."""
import json,subprocess,numpy as np,soundfile as sf,librosa
from scipy.signal import butter,sosfilt
SR=48000; T=json.load(open('v2/render/timing.json')); N=int(T['total']*SR); H0=T['scenes']['H'][0]
def mavg(x,k):
    c=np.cumsum(np.concatenate([[0],x])); h=k//2
    i=np.arange(len(x)); lo=np.clip(i-h,0,len(x)); hi=np.clip(i-h+k,0,len(x))
    return (c[hi]-c[lo])/k
voice=np.zeros(N)
for id,l in T['lines'].items():
    a,sr=sf.read(f"v2/audio/{id}.wav")
    if a.ndim>1: a=a.mean(1)
    if sr!=SR: a=librosa.resample(a.astype(np.float32),orig_sr=sr,target_sr=SR)
    i=int(l['start']*SR); voice[i:i+len(a)]+=a[:N-i]
voice=sosfilt(butter(2,75,'high',fs=SR,output='sos'),voice)
voice+=0.2*sosfilt(butter(2,[2200,4500],'band',fs=SR,output='sos'),voice)
env=np.sqrt(np.maximum(mavg(voice**2,int(.03*SR)),0))+1e-9
voice*=np.where(env>0.08,(0.08/env)**0.4,1.0); voice/=np.abs(voice).max(); voice*=0.85
act=(env>0.01).astype(float); k=int(.35*SR); act=np.clip(mavg(act,k)*3,0,1)
duck=10**(-(9*act)/20)
m,_=sf.read('v2/music.wav'); m=m[:N]
intro,_=sf.read('audio/intro.wav'); intro=intro[:int(8*SR)]; ti=np.arange(len(intro))/SR; intro*=np.clip((8-ti)/0.8,0,1)[:,None]
tt=np.arange(N)/SR; boost=10**((3.5*np.clip((tt-(H0-1.2))/1.4,0,1))/20)
out=m*10**(-17/20)*(duck*boost)[:,None]; out[:len(intro)]+=intro*0.9; out+=voice[:,None]*0.7
sf.write('v2/mix_raw.wav',out.astype(np.float32),SR)
r=subprocess.run(['ffmpeg','-i','v2/mix_raw.wav','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
d=json.loads(r[r.rfind('{'):r.rfind('}')+1])
af=f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true,aresample=48000"
subprocess.run(['ffmpeg','-v','error','-y','-i','v2/mix_raw.wav','-af',af,'-c:a','pcm_s16le','v2/mix_final.wav'],check=True); print('mix ok')
