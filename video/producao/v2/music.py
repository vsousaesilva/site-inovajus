import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt
import json
TMJ=json.load(open("v2/render/timing.json")); SCN=TMJ["scenes"]
SR=48000; DUR=TMJ["total"]; N=int(SR*DUR); t=np.arange(N)/SR
H0=SCN["H"][0]
rng=np.random.default_rng(3)
def hz(m): return 440*2**((m-69)/12)
# chords as midi (scene-synced)
D,Bm,G,A,Em=[50,57,62,66,69,76],[47,54,62,66,69,73],[43,55,59,62,66,74],[45,57,62,64,69,71],[40,55,59,62,66,71]
Gm9=[43,55,59,62,66,69]
PROG={"A":D,"B":Bm,"C":G,"D":D,"P":A,"L":Bm,"S":Em,"E":G,"J":D,"F":Bm,"G":A,"H":D}
sched=[(6.8 if k=="A" else SCN[k][0],PROG[k]) for k in ["A","B","C","D","P","L","S","E","J","F","G","H"]]+[(DUR+5,None)]
pad=np.zeros((N,2))
def env(s,e,att=2.6,rel=3.2):
    a=np.clip((t-s)/att,0,1); r=np.clip(1-(t-e)/rel,0,1)
    return (np.sin(a*np.pi/2)**2)*(np.sin(r*np.pi/2)**2)*(t>=s)
for (s,ch),(e,_) in zip(sched[:-1],sched[1:]):
    E=env(s,e)
    m=E>0
    for k,n in enumerate(ch):
        f=hz(n); amp=0.9 if k==0 else 0.55
        for ch_i,det in ((0,-5),(1,5)):
            for d2 in (0,7):
                ff=f*2**((det+d2-3.5)/1200)
                ph=rng.uniform(0,6.28)
                w=np.zeros(m.sum())
                for h in range(1,6):
                    w+=np.sin(2*np.pi*ff*h*t[m]+ph*h)/h**1.8
                pad[m,ch_i]+=amp*w*E[m]*(1+0.15*np.sin(2*np.pi*0.11*t[m]+k))
# bass
bass=np.zeros(N)
for (s,ch),(e,_) in zip(sched[:-1],sched[1:]):
    E=env(s,e,3,3); bass+=np.sin(2*np.pi*hz(ch[0]-12)*t)*E
pad[:,0]+=bass*1.4; pad[:,1]+=bass*1.4
pad/=np.abs(pad).max()
# bells
bell=np.zeros((N,2))
def ding(at,midi,a=1.0,dec=2.6,pan=0.5):
    i=int(at*SR); L=int(SR*4); tt=np.arange(L)/SR
    if i+L>N: L=N-i; tt=tt[:L]
    f=hz(midi); s=(np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*f*2.0*tt)*np.exp(-tt*2)+.12*np.sin(2*np.pi*f*3.01*tt)*np.exp(-tt*3))
    s*=np.exp(-tt/dec*2.2)*np.clip(tt/0.004,0,1)*a
    bell[i:i+L,0]+=s*(1-pan); bell[i:i+L,1]+=s*pan
x=8.6
while x<H0-1:
    cur=[c for (s,c) in sched if s<=x and c][-1]
    ding(x,rng.choice(cur[2:])+12,a=rng.uniform(.5,.9),pan=rng.uniform(.25,.75))
    x+=rng.choice([1.6,2.0,2.4,3.2])
# closing chime: D major arpeggio at logo assembly
for k,n in enumerate([74,78,81,86,90]): ding(H0+1.7+k*0.09,n,a=.9-k*.08,dec=4,pan=.3+k*.1)
for k,n in enumerate([62,69,74]): ding(H0+1.7,n,a=.6,dec=5,pan=.5)
bell/=np.abs(bell).max()
# whoosh for flying pieces
wh=np.zeros(N); i0=int((H0+0.2)*SR); L=int(1.6*SR); noise=rng.standard_normal(L)
tt=np.arange(L)/L
from scipy.signal import lfilter
out=np.zeros(L); y=0; 
cut=200+4000*np.sin(np.pi*tt)**2
alpha=1-np.exp(-2*np.pi*cut/SR)
for k in range(L): y+=alpha[k]*(noise[k]-y); out[k]=y
wh[i0:i0+L]=out*np.sin(np.pi*tt)**2
wh/=np.abs(wh).max()
mix=pad*0.55+bell*0.22
mix[:,0]+=wh*0.18; mix[:,1]+=wh*0.18
# reverb
Lr=int(3.2*SR); tr=np.arange(Lr)/SR
ir=np.stack([rng.standard_normal(Lr)*np.exp(-tr/0.75) for _ in range(2)],1)
sos=butter(2,5000,'low',fs=SR,output='sos'); ir=sosfilt(sos,ir,axis=0); ir/=np.sqrt((ir**2).sum(0))
wet=np.stack([fftconvolve(mix[:,c],ir[:,c])[:N] for c in range(2)],1)
mix=mix*0.65+wet*0.55
sos=butter(2,40,'high',fs=SR,output='sos'); mix=sosfilt(sos,mix,axis=0)
# global fades
g=np.clip((t-6.8)/2.2,0,1)*np.clip((DUR-t)/1.4,0,1)
mix*=g[:,None]
mix/=np.abs(mix).max()*1.12
sf.write('v2/music.wav',mix.astype(np.float32),SR); print('ok')
