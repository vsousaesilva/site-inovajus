#!/usr/bin/env bash
set -e
cd v2/render && printf "file 'seg0.mp4'\nfile 'seg1.mp4'\nfile 'seg2.mp4'\nfile 'seg3.mp4'\n" > segs.txt
TOT=$(python3 -c "import json;print(json.load(open('timing.json'))['total'])")
ffmpeg -v error -y -i ${INTRO:-../../intro.mp4} -f concat -safe 0 -i segs.txt -i ../mix_final.wav -filter_complex "[0:v]scale=3840:2160:flags=lanczos,fps=30,format=yuv420p,setsar=1,setpts=PTS-STARTPTS[a];[1:v]fps=30,format=yuv420p,setsar=1,setpts=PTS-STARTPTS[b];[a][b]xfade=transition=fade:duration=0.8:offset=7.2,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 16 -profile:v high -level 5.1 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -movflags +faststart -c:a aac -b:a 320k -t $TOT ../final_4k.mp4
echo "final: v2/final_4k.mp4"
