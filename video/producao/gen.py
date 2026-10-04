import json,sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
import sherpa_onnx
k=Kokoro("kokoro-v1.0.onnx","voices-v1.0.bin")
W="../sherpa-onnx-whisper-small/"
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=W+"small-encoder.int8.onnx",decoder=W+"small-decoder.int8.onnx",tokens=W+"small-tokens.txt",language="pt",task="transcribe",num_threads=4)
lines=json.load(open("script.json"))
only=sys.argv[1:]
for i,l in enumerate(lines):
    if only and str(i) not in only: continue
    s,sr=k.create(l["tts"],voice="pf_dora",speed=l.get("speed",0.95),lang="pt-br")
    sf.write(f"l{i:02d}.wav",s,sr)
    import librosa
    a=librosa.resample(s.astype(np.float32),orig_sr=sr,target_sr=16000)
    st=rec.create_stream(); st.accept_waveform(16000,a); rec.decode_stream(st)
    print(f"[{i}] {len(s)/sr:.2f}s | {st.result.text.strip()}")
