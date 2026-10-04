import sherpa_onnx, soundfile as sf, sys, numpy as np, librosa
def tts(voice):
    import os; d=os.path.join(os.path.dirname(os.path.abspath(__file__)),f"vits-piper-pt_BR-{voice}/")
    cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=d+f"pt_BR-{voice}.onnx",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data"),num_threads=4))
    return sherpa_onnx.OfflineTts(cfg)
if __name__=="__main__":
    t="Em tecnologia, o curso Servidor mais IA já formou mais de duzentos servidores multiplicadores, com foco na área fim."
    for v in ["dii-high","miro-high"]:
        a=tts(v).generate(t,sid=0,speed=1.0); s=np.array(a.samples); sf.write(f"test_{v}.wav",s,a.sample_rate)
        f0,vf,_=librosa.pyin(s,fmin=60,fmax=400,sr=a.sample_rate)
        print(v,a.sample_rate,round(len(s)/a.sample_rate,2),'F0 median',np.nanmedian(f0))
    s,sr=sf.read("dora.wav"); f0,_,_=librosa.pyin(s,fmin=60,fmax=400,sr=sr); print('kokoro dora F0',np.nanmedian(f0))
