"""Professional narration via Google (needs a key in the environment):
  GOOGLE_TTS_API_KEY -> Cloud Text-to-Speech (voice default pt-BR-Chirp3-HD-Aoede; override with TTS_VOICE)
  GEMINI_API_KEY     -> Gemini TTS (voice default 'Kore'; override with TTS_VOICE, model with TTS_MODEL)
Writes v2/audio/<id>.wav. Usage: python3 v2/voice_google.py [ids...]"""
import os,sys,json,base64,urllib.request,numpy as np,soundfile as sf
def spoken(l):
    t=l['text'].replace('|',' ')
    for a,b in [('Servidor + IA','Servidor mais I.A.'),('PJe','pê-jota-é'),('JFCE','Justiça Federal no Ceará'),('área-fim','área fim'),('PopRua','Pop Rua')]: t=t.replace(a,b)
    return t
def post(url,body):
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(req,timeout=120))
def cloud(text,key):
    v=os.environ.get('TTS_VOICE','pt-BR-Chirp3-HD-Aoede')
    r=post(f'https://texttospeech.googleapis.com/v1/text:synthesize?key={key}',{'input':{'text':text},'voice':{'languageCode':'pt-BR','name':v},'audioConfig':{'audioEncoding':'LINEAR16','sampleRateHertz':48000}})
    pcm=base64.b64decode(r['audioContent'])[44:]; return np.frombuffer(pcm,np.int16)/32768,48000
def gemini(text,key):
    v=os.environ.get('TTS_VOICE','Kore'); models=[os.environ['TTS_MODEL']] if 'TTS_MODEL' in os.environ else ['gemini-2.5-pro-preview-tts','gemini-2.5-flash-preview-tts']
    prompt=('Narre em português do Brasil, com voz feminina, tom institucional, acolhedor e confiante, ritmo calmo e dicção clara, '
            'como em um vídeo institucional da Justiça Federal. Leia exatamente o texto: '+text)
    last=None
    for m in models:
        try:
            r=post(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}',
                {'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':v}}}}})
            b=r['candidates'][0]['content']['parts'][0]['inlineData']['data']; return np.frombuffer(base64.b64decode(b),np.int16)/32768,24000
        except Exception as e: last=e
    raise last
if __name__=='__main__':
    kc,kg=os.environ.get('GOOGLE_TTS_API_KEY'),os.environ.get('GEMINI_API_KEY')
    if not (kc or kg): sys.exit('Defina GOOGLE_TTS_API_KEY ou GEMINI_API_KEY no ambiente.')
    os.makedirs('v2/audio',exist_ok=True); only=sys.argv[1:]
    for l in json.load(open('v2/script.json')):
        if only and l['id'] not in only: continue
        a,sr=cloud(spoken(l),kc) if kc else gemini(spoken(l),kg)
        sf.write(f"v2/audio/{l['id']}.wav",a.astype(np.float32),sr); print(l['id'],round(len(a)/sr,2),'s')
