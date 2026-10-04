"""Split one continuous narration recording (lines in script order, ~1.5 s pause between them) into v2/audio/<id>.wav.
Usage: python3 v2/split_recording.py gravacao.wav"""
import sys,json,numpy as np,librosa,soundfile as sf
ids=[l['id'] for l in json.load(open('v2/script.json'))]
a,sr=librosa.load(sys.argv[1],sr=48000,mono=True)
e=librosa.feature.rms(y=a,frame_length=2048,hop_length=480)[0]; thr=max(e.max()*0.04,np.percentile(e,20)*2)
voiced=e>thr; hop=480/sr
# segments separated by >= 0.8 s silence
segs=[];start=None;sil=0
for i,v in enumerate(voiced):
    if v:
        if start is None: start=i
        sil=0
    elif start is not None:
        sil+=1
        if sil*hop>=0.8: segs.append((start,i-sil+1)); start=None; sil=0
if start is not None: segs.append((start,len(voiced)))
segs=[s for s in segs if (s[1]-s[0])*hop>0.6]
print(len(segs),'trechos encontrados para',len(ids),'falas')
if len(segs)!=len(ids): sys.exit('Número de trechos diferente do roteiro: grave com pausas de ~1,5 s entre as falas.')
for id,(s,e2) in zip(ids,segs):
    i0=max(0,int((s*hop-0.08)*sr)); i1=min(len(a),int((e2*hop+0.15)*sr)); sf.write(f'v2/audio/{id}.wav',a[i0:i1],sr)
print('ok')
