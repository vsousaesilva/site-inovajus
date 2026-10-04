# Placeholder voice: Kokoro pf_dora (offline). Writes v2/audio/<id>.wav
import json,sys,os,soundfile as sf
from kokoro_onnx import Kokoro
k=Kokoro("tts/kokoro-v1.0.onnx","tts/voices-v1.0.bin")
os.makedirs('v2/audio',exist_ok=True); only=sys.argv[1:]
for l in json.load(open('v2/script.json')):
    if only and l['id'] not in only: continue
    s,sr=k.create(l['tts'],voice="pf_dora",speed=0.95,lang="pt-br"); sf.write(f"v2/audio/{l['id']}.wav",s,sr)
