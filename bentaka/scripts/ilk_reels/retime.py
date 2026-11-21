#!/usr/bin/env python3
"""Seslendirme sürelerine göre zaman çizelgesini yeniden kurar.
reels_base.html (Azure zamanlaması) -> reels.html, ayrıca timeline.json (music.py ve compose.py okur).
Kullanım: python3 retime.py <ses_klasörü> [hız=1.05]
ses_klasörü: t1.wav ... t9.wav (sessizliği kırpılmış satırlar)
"""
import json, re, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
VO, SPEED = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 1.05
GAP, LEAD, TAIL = 0.3, 0.25, 2.3
dur = lambda p: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

OS = [0, 4.9, 8.3, 18.3, 26, 37.2, 42.3, 46, 53.4]       # eski sahne başları
OV = [0.4, 5.2, 8.6, 18.6, 26.3, 37.5, 42.6, 46.3, 53.9]  # eski ses başları
OD = [4.12, 2.68, 9.28, 7.02, 10.49, 4.41, 3.03, 6.79, 3.02]
OEND = 59.0

D = [dur(os.path.join(VO, f't{i}.wav')) / SPEED for i in range(1, 10)]
V = [0.4]
for i in range(8):
    V.append(round(V[-1] + D[i] + GAP, 3))
S = [0.0] + [round(v - LEAD, 3) for v in V[1:]]
END = round(V[8] + D[8] + TAIL, 2)
K = [max(0.6, min(1.6, D[i] / OD[i])) for i in range(9)]

def scene_of(t):
    i = 0
    while i < 8 and t >= OS[i + 1]: i += 1
    return i
def rel(i, r):  # sahne içi göreli zaman
    return round(r if r <= LEAD else LEAD + (r - LEAD) * K[i], 3)
def f(t):       # mutlak zaman eşleme
    if t >= OEND: return END + (t - OEND)
    i = scene_of(t); return round(S[i] + rel(i, t - OS[i]), 3)

h = open(os.path.join(HERE, 'reels_base.html')).read()
# sahneleri tek tek işle
parts = re.split(r'(<section class="scene" data-s="[\d.]+" data-e="[\d.]+">)', h)
out = [parts[0]]; idx = -1
for p in parts[1:]:
    m = re.match(r'<section class="scene" data-s="([\d.]+)" data-e="([\d.]+)">', p)
    if m:
        idx = OS.index(float(m.group(1)))
        e = 99 if idx == 8 else S[idx + 1]
        out.append(f'<section class="scene" data-s="{S[idx]}" data-e="{e}">'); continue
    if idx >= 0:
        body, sep, rest = p.partition('</section>')
        body = re.sub(r'data-(in|cs|bs|hl)="([\d.]+)"', lambda mm: f'data-{mm.group(1)}="{rel(idx, float(mm.group(2)))}"', body)
        body = re.sub(r'data-(cd|bd)="([\d.]+)"', lambda mm: f'data-{mm.group(1)}="{round(float(mm.group(2)) * K[idx], 3)}"', body)
        p = body + sep + rest
    out.append(p)
h = ''.join(out)
# JS içindeki mutlak zamanlar
h = re.sub(r'const WIPES=\[([^\]]*)\]', lambda m: 'const WIPES=[' + ','.join(str(f(float(x))) for x in m.group(1).split(',')) + ']', h)
h = re.sub(r'const FLASH=\[([^\]]*)\]', lambda m: 'const FLASH=[' + ','.join(str(f(float(x))) for x in m.group(1).split(',')) + ']', h)
h = h.replace('prog(t,53.1,.3)', f'prog(t,{round(S[8]-0.3,3)},.3)')
h = h.replace('Math.sin((t-53.4)*4))*2.5*(t>53.4?1:0)', f'Math.sin((t-{S[8]})*4))*2.5*(t>{S[8]}?1:0)')
h = h.replace("t>58.2?`brightness(${(1-prog(t,58.2,.8))", f"t>{END-0.8}?`brightness(${{(1-prog(t,{END-0.8},.8))")
h = h.replace('if(s===37.2)', f'if(s==={S[5]})')
h = h.replace('fill=3.632*eInOut(prog(lt,1.2,1.4))', f'fill=3.632*eInOut(prog(lt,{rel(5,1.2)},{round(1.4*K[5],3)}))')
h = re.sub(r"const k=\[\[0,\.25\][^;]*;", lambda m: 'const k=' + re.sub(r'\[([\d.]+),', lambda mm: '[' + str(f(float(mm.group(1))) if float(mm.group(1)) < 99 else 99) + ',', m.group(0)[8:]), h, count=1)
h = h.replace('window.TOTAL=59;', f'window.TOTAL={END};')
open(os.path.join(HERE, 'reels.html'), 'w').write(h)

tl = {'END': END, 'S': S, 'V': V, 'D': D, 'K': K, 'SPEED': SPEED,
      'cuts': S[1:], 'impacts': [f(x) for x in [0.35, 26.0, 32.8, 37.6, 53.5]],
      'risers': [[round(S[4] - 1.0, 3), 1.0], [round(S[8] - 1.2, 3), 1.2]],
      'tr_ticks': [f(30.2), round(2.6 * K[4], 3)], 'day_ticks': [f(38.4), round(1.4 * K[5], 3)],
      'sections': [[S[1], 'full'], [S[2], 'tension'], [S[4], 'full'], [round(S[4] + 4 * K[4], 3), 'build'], [S[8], 'full'], [999, 'outro']]}
json.dump(tl, open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
print(json.dumps({'S': S, 'V': V, 'END': END, 'K': [round(k, 2) for k in K]}))
