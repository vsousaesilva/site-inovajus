import numpy as np, soundfile as sf, json, librosa
from scipy.signal import butter, sosfilt
SR=48000; N=int(90*SR)
T=json.load(open('video/timing.json'))
voice=np.zeros(N)
for l in T['lines']:
    a,sr=sf.read(f"tts/l{l['i']:02d}.wav"); a=librosa.resample(a.astype(np.float32),orig_sr=sr,target_sr=SR)
    i=int(l['start']*SR); voice[i:i+len(a)]+=a[:N-i]
voice=sosfilt(butter(2,75,'high',fs=SR,output='sos'),voice)
# gentle presence boost (+2dB around 3k) via parallel bandpass
bp=sosfilt(butter(2,[2200,4500],'band',fs=SR,output='sos'),voice); voice=voice+0.25*bp
# simple soft compression
env=np.sqrt(np.convolve(voice**2,np.ones(int(.03*SR))/int(.03*SR),'same'))+1e-9
thr=0.08; gain=np.where(env>thr,(thr/env)**0.4,1.0); voice*=gain
voice/=np.abs(voice).max(); voice*=0.85
# ducking envelope from speech activity
act=(env>0.01).astype(float)
k=int(.35*SR); act=np.convolve(act,np.ones(k)/k,'same'); act=np.clip(act*3,0,1)
duck=10**(-(9*act)/20)
m,_=sf.read('audio/music.wav')
intro,_=sf.read('audio/intro.wav'); intro=intro[:int(8*SR)]
ti=np.arange(len(intro))/SR; intro*=np.clip((8.0-ti)/0.8,0,1)[:,None]
mus_level=10**(-17/20)
out=np.zeros((N,2))
tt=np.arange(N)/SR; boost=10**((3.5*np.clip((tt-81.8)/1.4,0,1))/20)
out+=m[:N]*mus_level*(duck*boost)[:,None]
out[:len(intro)]+=intro*0.9
out+=voice[:,None]*0.7
sf.write('audio/mix_raw.wav',out.astype(np.float32),SR)
print('peak',np.abs(out).max())
