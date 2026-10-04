#!/usr/bin/env bash
# Rebuilds the whole video from the narration in v2/audio/*.wav (run from the production root).
set -e
python3 v2/timeline.py
N=$(python3 -c "import json,math;d=json.load(open('v2/render/timing.json'));print(math.ceil((d['total']-d['body0'])*30))"); q=$(( (N+3)/4 ))
( cd v2/render && { node render.mjs 0 $q seg0.mp4 & node render.mjs $q $((2*q)) seg1.mp4 & node render.mjs $((2*q)) $((3*q)) seg2.mp4 & node render.mjs $((3*q)) $N seg3.mp4 & wait; } )
python3 v2/music.py && python3 v2/mix.py && bash v2/assemble.sh
