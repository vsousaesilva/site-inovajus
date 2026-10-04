# Placeholder voice: Piper pt_BR "dii" (offline). Writes v2/audio/<id>.wav
import json,sys,os,numpy as np,soundfile as sf
sys.path.insert(0,os.path.abspath('tts')); from piper import tts
os.makedirs('v2/audio',exist_ok=True)
os.chdir('tts'); eng=tts('dii-high'); os.chdir('..')
only=sys.argv[1:]
for l in json.load(open('v2/script.json')):
    if only and l['id'] not in only: continue
    a=eng.generate(l['tts'],sid=0,speed=0.97); sf.write(f"v2/audio/{l['id']}.wav",np.array(a.samples),a.sample_rate)
    print(l['id'],round(len(a.samples)/a.sample_rate,2))
