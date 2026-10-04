import json,sys,numpy as np,soundfile as sf,librosa,sherpa_onnx
W="sherpa-onnx-whisper-small/"
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=W+"small-encoder.int8.onnx",decoder=W+"small-decoder.int8.onnx",tokens=W+"small-tokens.txt",language="pt",task="transcribe",num_threads=4)
only=sys.argv[1:]
for l in json.load(open('v2/script.json')):
    if only and l['id'] not in only: continue
    s,sr=sf.read(f"v2/audio/{l['id']}.wav"); a=librosa.resample(s.astype(np.float32),orig_sr=sr,target_sr=16000)
    st=rec.create_stream(); st.accept_waveform(16000,a); rec.decode_stream(st); print(f"[{l['id']}] {len(s)/sr:.2f}s | {st.result.text.strip()}")
