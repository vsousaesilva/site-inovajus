# Produção do vídeo Inovajus

Rode os comandos a partir desta pasta. É preciso ter `ffmpeg`, `node` (com `playwright-core`) e Python (`numpy`, `scipy`, `soundfile`, `librosa`).
Copie também `../../Animate_logo_elements.mp4` para `intro.mp4` nesta pasta.

1. **Narração** em `v2/audio/<id>.wav`, um arquivo por fala (ids em `v2/script.json`). Formas de gerar:
   - **Voz profissional Google:** defina `GEMINI_API_KEY` ou `GOOGLE_TTS_API_KEY` e rode `python3 v2/voice_google.py`.
   - **Gravação única com pausas de ~1,5 s entre as falas:** `python3 v2/split_recording.py gravacao.wav`.
2. **Montagem completa:** `bash v2/build.sh`. Recalcula a linha do tempo pela duração das falas, renderiza em 4K, gera trilha e mixagem e entrega o resultado em `v2/final_4k.mp4`.
