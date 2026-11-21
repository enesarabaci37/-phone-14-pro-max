#!/usr/bin/env python3
"""iPhone 17 'kaç saat çalışman gerek' Reels'i. Kullanım: python3 build.py <ses_klasörü> [tempo=1.2]
Veriler (21 Kasım 2026): Apple TR 256 GB 99.999 TL · DE 949 € · ABD 799 $ · asgari ücret saatlik TR 146,80 TL (33.030/225), DE 13,90 €, ABD 7,25 $ · USD/TRY 50,5 · IMEI harcı 54.258 TL"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
VO, TEMPO = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 1.2
GAP, LEAD, TAIL, N = 0.3, 0.25, 2.3, 7
dur = lambda p: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
D = [dur(os.path.join(VO, f't{i}.wav')) / TEMPO for i in range(1, N + 1)]
V = [0.4]
for d in D[:-1]: V.append(round(V[-1] + d + GAP, 3))
S = [0.0] + [round(v - LEAD, 3) for v in V[1:]]
END = round(V[-1] + D[-1] + TAIL, 2); E = S[1:] + [99]
r = lambda i, x: round(x * D[i] + LEAD, 2)
TR, DE, US = 99999 / 146.80, 949 / 13.90, 799 / 7.25
USD, IMEI = 50.5, 54258
abroad = 799 * USD
T = lambda n: f'{n:,.0f}'.replace(',', '.')
LOGO = ('<svg width="{s}" height="{s}" viewBox="0 0 120 120" aria-hidden="true"><rect x="18" y="8" width="24" height="104" rx="5" fill="#F3F5F8"/>'
        '<circle cx="68" cy="72" r="28" fill="none" stroke="#F3F5F8" stroke-width="24"/><circle {id} cx="68" cy="72" r="8" fill="#C6FF3D"/></svg>')
SEND = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7z"/></svg>'
def bar(label, hours, accent, t, dd):
    col = '#C6FF3D' if accent else '#8A93A6'
    return (f'<div class="el" data-in="{t}"><div style="display:flex;justify-content:space-between;align-items:baseline"><span class="sora" style="font-weight:600;font-size:54px">{label}</span>'
            f'<span class="sora num" style="font-weight:{800 if accent else 700};font-size:{100 if accent else 72}px;color:{col if accent else "#F3F5F8"}"><span data-count="{hours:.3f}" data-cs="{t+.1}" data-cd="{dd}" data-fmt="int">0</span> saat</span></div>'
            f'<div style="height:{52 if accent else 38}px;border-radius:26px;background:rgba(26,31,43,.9);margin-top:14px;overflow:hidden"><div data-bar="{hours/TR:.4f}" data-bs="{t+.1}" data-bd="{dd}" style="height:100%;width:0;border-radius:26px;background:{col}"></div></div></div>')
scenes = [
f'''<div class="pad" style="top:460px">
  <div class="el mono c" data-in="0.1" style="font-size:30px">256 GB · Apple Türkiye fiyatı</div>
  <div class="el big" data-in="{r(0,.0)}" data-fx="punch" style="font-size:190px;margin-top:20px">iPhone 17</div>
  <div class="el h1" data-in="{r(0,.2)}" style="font-size:96px;margin-top:40px">için <span class="hl dark" data-hl="{r(0,.3)}">kaç saat<i></i></span><br>çalışman gerek?</div>
</div>''',
f'''<div class="pad" style="top:560px">
  <div class="el label" data-in="0.1">Türkiye fiyatı</div>
  <div class="el big num v" data-in="{r(1,.25)}" data-fx="punch" style="font-size:200px;margin-top:40px;text-shadow:0 0 80px rgba(198,255,61,.35)"><span data-count="99999" data-cs="{r(1,.25)}" data-cd="1.6" data-fmt="int">0</span></div>
  <div class="el h1" data-in="{r(1,.35)}" style="font-size:90px">TL</div>
  <div class="el mono c" data-in="{r(1,.6)}" style="font-size:26px;margin-top:40px">iPhone 17 · 256 GB</div>
</div>''',
f'''<div class="pad" style="top:400px">
  <div class="el label" data-in="0.1">Asgari ücretle çalışma süresi</div>
  <div style="display:flex;flex-direction:column;gap:60px;margin-top:70px">
  {bar("Almanya", DE, False, r(2,.0), 1.0)}{bar("ABD", US, False, r(2,.28), 1.0)}{bar("Türkiye", TR, True, r(2,.58), 2.2)}
  </div>
  <div class="el mono c" data-in="{r(2,.2)}" style="font-size:22px;margin-top:40px;line-height:1.7">949 € ÷ 13,90 € · 799 $ ÷ 7,25 $ · 99.999 TL ÷ 146,80 TL</div>
</div>''',
f'''<div class="pad" style="top:480px">
  <div class="el h1 c" data-in="0.1" style="font-size:70px">Yani tam</div>
  <div style="display:flex;align-items:baseline;gap:30px">
  <div class="el big v num" data-in="{r(3,.0)}" data-fx="punch" style="font-size:330px;text-shadow:0 0 90px rgba(198,255,61,.35)"><span data-count="90.8" data-cs="{r(3,.0)}" data-cd="1.1" data-fmt="int">0</span></div>
  <div class="el h1" data-in="{r(3,.15)}" style="font-size:96px">iş günü</div></div>
  <div class="el glass" data-in="{r(3,.5)}" style="display:inline-block;padding:28px 38px;margin-top:40px;font-size:46px;font-weight:600">= <span class="v">3 aylık</span> brüt asgari ücret</div>
</div>''',
f'''<div class="pad" style="top:400px">
  <div class="el label" data-in="0.1">Yurt dışından getirsen?</div>
  <div class="el glass" data-in="{r(4,.05)}" data-fx="left" style="margin-top:50px">
    <div class="row2"><span>ABD fiyatı <span class="c" style="font-size:30px">799 $</span></span><span class="sora num">≈ {T(abroad)} TL</span></div>
    <div class="row2 el" data-in="{r(4,.32)}"><span>IMEI kayıt harcı</span><span class="sora num" style="color:#FF5A5A">+ {T(IMEI)} TL</span></div>
    <div class="row2 el" data-in="{r(4,.55)}"><span><b>Toplam</b></span><span class="sora num" style="font-weight:800">≈ {T(abroad+IMEI)} TL</span></div>
  </div>
  <div class="el h1" data-in="{r(4,.72)}" data-fx="punch" style="font-size:84px;margin-top:60px">Kâr sadece <span class="hl dark" data-hl="{r(4,.8)}">≈ {T(99999-abroad-IMEI)} TL<i></i></span></div>
  <div class="el mono c" data-in="{r(4,.8)}" style="font-size:22px;margin-top:30px">Kur 50,5 TL · ABD satış vergisi hariç</div>
</div>''',
f'''<div class="pad" style="top:470px">
  <div class="el" data-in="0.1" data-fx="plane">{SEND.format(s=180,c="#C6FF3D")}</div>
  <div class="el h1" data-in="{r(5,.0)}" style="font-size:100px;margin-top:50px">iPhone almayı düşünen <span class="v">arkadaşına</span> gönder.</div>
  <div class="el" data-in="{r(5,.55)}" style="font-size:46px;margin-top:50px">Sence değer mi? <span class="v">Yorumlara yaz.</span></div>
</div>''',
f'''<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding-bottom:160px">
  <div class="el" data-in="0.1" data-fx="punch" style="display:flex;align-items:center;gap:32px">{LOGO.format(s=170,id='id="dot"')}<span class="sora" style="font-weight:700;font-size:170px;letter-spacing:-.045em;padding-bottom:14px">bentaka</span></div>
  <div class="el sora c" data-in="0.7" style="font-weight:600;font-size:60px;margin-top:40px">Future, first<span class="v">.</span></div>
  <div class="el" data-in="1.3" style="margin-top:60px"><span class="chip" style="font-size:28px;padding:16px 30px">TAKİP ET · @BENTAKATR</span></div>
</div>''',
]
secs = ''.join(f'<section class="scene" data-s="{S[i]}" data-e="{E[i]}">{scenes[i]}</section>\n' for i in range(N))
h = open(os.path.join(HERE, 'template.html')).read()
fl = [S[2] + r(2, .58) + 2.3, S[3] + r(3, .0), S[6] + .1]
h = (h.replace('/*SCENES*/', secs).replace('/*WIPES*/', ','.join(str(x) for x in [S[1], S[2], S[4], S[5], S[6]]))
     .replace('/*FLASH*/', ','.join(str(round(x, 3)) for x in fl)).replace('/*END*/', str(END)).replace('/*LAST*/', str(S[6])).replace('/*CD*/', '0,0'))
open(os.path.join(HERE, 'reels.html'), 'w').write(h)
tl = {'END': END, 'S': S, 'V': V, 'D': D, 'SPEED': TEMPO, 'cuts': S[1:], 'impacts': fl,
      'risers': [[round(S[2] + r(2, .58) - .9, 3), 1.0], [round(S[6] - 1.2, 3), 1.2]],
      'tr_ticks': [S[2] + r(2, .58) + .1, 2.2], 'day_ticks': [S[3] + r(3, .0), 1.1],
      'sections': [[S[1], 'full'], [S[2], 'tension'], [S[2] + r(2, .5), 'full'], [S[3], 'build'], [S[6], 'full'], [999, 'outro']]}
json.dump(tl, open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
print(json.dumps({'S': S, 'END': END, 'abroad': round(abroad), 'kar': round(99999 - abroad - IMEI)}))
