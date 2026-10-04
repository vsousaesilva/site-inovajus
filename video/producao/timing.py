import json, numpy as np, soundfile as sf
T="tts/"
starts=[9.0,14.0,21.2,29.0,31.9,34.8,37.9,45.8,57.0,70.0,77.0]
disp=["Este é o Inovajus, o Laboratório de Inovação da Justiça Federal no Ceará.",
"Desde 2019, transformamos a cultura institucional com método, ciência e humanização.",
"São mais de 150 servidores capacitados, 11 projetos e 4 eixos de atuação.",
"PJe e Automação de Fluxos.","Segurança no Tratamento de Dados.","Tecnologia e Inteligência Artificial.",
"E o novo Eixo de Linguagem Simples e Acessibilidade, que aproxima a Justiça do cidadão.",
"No Laboratório de Fluxos do PJe, automatizamos peças repetitivas|e redesenhamos fluxos processuais, com alcance nacional.",
"E no Lab Low Code, os próprios servidores criam automações,|formulários inteligentes e aplicações, com baixo código e inteligência artificial generativa.",
"Do Mandado Cidadão ao Teatro PopRua, levamos inovação a quem mais precisa.",
"Inovajus. Uma Justiça mais eficiente, acessível e centrada nas pessoas."]
cues=[];lines=[]
for i,(st,d) in enumerate(zip(starts,disp)):
    a,sr=sf.read(f"{T}l{i:02d}.wav"); dur=len(a)/sr
    # trim leading/trailing silence for exact speech bounds
    env=np.convolve(np.abs(a),np.ones(int(.02*sr))/int(.02*sr),'same')
    on=np.where(env>0.01)[0]; s0=on[0]/sr; s1=on[-1]/sr
    lines.append(dict(i=i,start=st,dur=dur,speech=[st+s0,st+s1]))
    parts=d.split('|')
    if len(parts)==1: cues.append([st+s0-0.08,st+s1+0.25,d]); continue
    frac=len(parts[0])/len(d.replace('|',''))
    est=s0+(s1-s0)*frac; w=int(.12*sr)
    best=min(range(int((est-.8)*sr),int((est+.8)*sr),int(.01*sr)),key=lambda k:env[k:k+w].mean())
    cut=(best+w/2)/sr
    cues.append([st+s0-0.08,st+cut,parts[0]]); cues.append([st+cut,st+s1+0.25,parts[1]])
    print(i,'cut',round(est,2),'->',round(cut,2))
json.dump(dict(cues=cues,lines=lines),open("video/timing.json","w"),ensure_ascii=False,indent=1)
open("video/timing.js","w").write("window.TIMING="+json.dumps(dict(cues=cues,lines=lines),ensure_ascii=False)+";")
for c in cues: print(f"{c[0]:6.2f} {c[1]:6.2f} {c[2]}")
