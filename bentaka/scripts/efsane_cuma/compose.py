#!/usr/bin/env python3
"""Higgsfield görsel/videolarından 59 sn arka plan yolu kurar, yazı katmanını ve sesi üstüne bindirir.
Kullanım: python3 compose.py <hf_klasörü> <overlay_kare_klasörü> <mix.wav> <çıktı.mp4>
hf_klasörü: v1.mp4 v2.mp4 v3.mp4 i2.png i4.png i5.png i6.png i7.png i8.png (+ yedek test1.jpg)
"""
import os, subprocess, sys

HF, OV, MIX, OUT = sys.argv[1:5]
FPS = 30
# (başlangıç, bitiş, kaynak, hareket)  hareket: in = yakınlaş, out = uzaklaş, pan = yatay kay
import json
TL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timeline.json')))
_S, _E = TL['S'], TL['END']
_SRC = [('c1.mp4', None), ('c2.mp4', None), ('c3.mp4', None), ('c4.mp4', None), ('c5.mp4', None),
        ('c6.mp4', None), ('c7.mp4', None), ('end.mp4', None)]
PLAN = [(_S[i], _S[i + 1] if i < len(_S) - 1 else _E, src, mv) for i, (src, mv) in enumerate(_SRC)]
TMP = os.path.join(os.path.dirname(OUT), '_seg'); os.makedirs(TMP, exist_ok=True)
GRADE = 'eq=contrast=1.06:saturation=1.08,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p'

def run(args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'] + args, check=True)

def dur(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]))

segs = []
for i, (a, b, src, mv) in enumerate(PLAN):
    n = round(b * FPS) - round(a * FPS); d = n / FPS; out = os.path.join(TMP, f's{i}.mp4'); path = os.path.join(HF, src)
    if src.endswith('.mp4') and not os.path.exists(path):  # video gelmediyse yedek görsel
        path, mv = os.path.join(HF, 'test1.jpg'), 'in'
    if path.endswith('.mp4'):
        k = max(d / dur(path), 1.0)  # gerekirse yavaşlat
        run(['-i', path, '-vf', f'setpts={k:.4f}*PTS,{GRADE}', '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', out])
    else:
        if mv == 'in':   z, x = f'1+0.10*on/{n}', 'iw/2-(iw/zoom/2)'
        elif mv == 'out': z, x = f'1.10-0.10*on/{n}', 'iw/2-(iw/zoom/2)'
        else:             z, x = '1.12', f'(iw-iw/zoom)*on/{n}'
        vf = (f'scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,'
              f"zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps={FPS},{GRADE}")
        run(['-loop', '1', '-i', path, '-vf', vf, '-frames:v', str(n), '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', out])
    segs.append(out)

lst = os.path.join(TMP, 'list.txt')
open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
bg = os.path.join(TMP, 'bg.mp4')
run(['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', bg])
run(['-i', bg, '-framerate', str(FPS), '-i', os.path.join(OV, 'o%04d.png'), '-i', MIX,
     '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto,noise=alls=5:allf=t,format=yuv420p[v]',
     '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-r', str(FPS),
     '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT])
print('tamam:', OUT)
