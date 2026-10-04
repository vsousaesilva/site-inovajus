"""Builds the full timeline from the narration audio durations.
Output: v2/render/timing.js + timing.json (scenes, lines, subtitle cues, total)."""
import json, numpy as np, soundfile as sf, os
S=json.load(open('v2/script.json'))
# scene order: (scene, lead before first line, gap between lines, tail after last line)
PLAN=[('A',1.8,0.45,0.6),('B',0.5,0.4,1.2),('C',0.6,0.5,1.6),('D',1.0,0.4,1.3),('P',1.0,0.4,1.3),
      ('L',1.0,0.35,1.3),('S',1.3,0.6,1.5),('E',1.0,0.4,1.3),('J',1.0,0.55,1.5),('F',0.7,0.4,1.0),('G',1.0,0.4,1.2)]
BODY0=7.2          # body starts (crossfade with intro 7.2-8.0)
HDUR=7.0           # closing logo
lines={};scenes={};cues=[]
t=BODY0
for sc,lead,gap,tail in PLAN:
    start=t; t+=lead
    ls=[l for l in S if l['scene']==sc]
    for k,l in enumerate(ls):
        a,sr=sf.read(f"v2/audio/{l['id']}.wav")
        if a.ndim>1: a=a.mean(1)
        w=int(.02*sr); env=np.convolve(np.abs(a),np.ones(w)/w,'same')
        on=np.where(env>0.01)[0]; s0,s1=on[0]/sr,on[-1]/sr
        lines[l['id']]=dict(start=t,dur=len(a)/sr,s0=t+s0,s1=t+s1,tts=l['tts'],text=l['text'].replace('|',' '))
        parts=l['text'].split('|')
        if len(parts)==1: cues.append([t+s0-0.08,t+s1+0.25,parts[0]])
        else:
            frac=len(parts[0])/len(l['text'].replace('|','')); est=s0+(s1-s0)*frac; wq=int(.12*sr)
            rng=range(max(0,int((est-.9)*sr)),min(len(env)-wq,int((est+.9)*sr)),int(.01*sr))
            best=min(rng,key=lambda q:env[q:q+wq].mean()); cut=(best+wq/2)/sr
            cues.append([t+s0-0.08,t+cut,parts[0]]); cues.append([t+cut,t+s1+0.25,parts[1]])
        t+=len(a)/sr+(gap if k<len(ls)-1 else 0)
    t+=tail; scenes[sc]=[start,t]
scenes['H']=[t,t+HDUR]; total=t+HDUR
os.makedirs('v2/render',exist_ok=True)
D=dict(scenes=scenes,lines=lines,cues=cues,total=total,body0=BODY0)
json.dump(D,open('v2/render/timing.json','w'),ensure_ascii=False,indent=1)
open('v2/render/timing.js','w').write('window.TIMING='+json.dumps(D,ensure_ascii=False)+';')
for k,v in scenes.items(): print(k,round(v[0],2),round(v[1],2))
print('TOTAL',round(total,2))
