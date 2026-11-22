#!/usr/bin/env python3
"""Mizah Reels: 'Efsane Cuma'dan önceki gece sen' (seslendirmesiz, ~24 sn). Kullanım: python3 build.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DUR = [2.8, 2.8, 2.6, 2.8, 2.8, 3.0, 3.8, 3.4]
S = [0.0]
for d in DUR[:-1]: S.append(round(S[-1] + d, 2))
END = round(S[-1] + DUR[-1], 2); E = S[1:] + [99]
LOGO = ('<svg width="{s}" height="{s}" viewBox="0 0 120 120" aria-hidden="true"><rect x="18" y="8" width="24" height="104" rx="5" fill="#F3F5F8"/>'
        '<circle cx="68" cy="72" r="28" fill="none" stroke="#F3F5F8" stroke-width="24"/><circle {id} cx="68" cy="72" r="8" fill="#C6FF3D"/></svg>')
SEND = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7z"/></svg>'
cap = lambda txt, t=0.15, size=104, fx='punch', extra='': f'<div class="el big" data-in="{t}" data-fx="{fx}" style="font-size:{size}px;line-height:1.02;{extra}">{txt}</div>'
scenes = [
f'''<div class="pad" style="top:330px"><div class="el mono v" data-in="0.05" style="font-size:40px">POV:</div>{cap("Efsane Cuma'dan önceki gece <span class='hl dark' data-hl='0.7'>sen<i></i></span> 🌙", .15, 112)}</div>''',
f'''<div class="pad" style="top:330px">{cap("Sepete", .05, 96, "up")}<div class="el big num v" data-in="0.25" data-fx="punch" style="font-size:300px;text-shadow:0 0 80px rgba(198,255,61,.4)"><span data-count="47" data-cs="0.25" data-cd="1.2" data-fmt="int">0</span></div>{cap("ürün ekledin 🛒", .5, 96, "up")}</div>''',
f'''<div class="pad" style="top:330px">{cap("Hiçbirine", .1, 120)}{cap("ihtiyacın <span class='hl dark' data-hl='0.9'>yok.<i></i></span>", .45, 120)}</div>''',
f'''<div class="pad" style="top:330px"><div class="el glass num" data-in="0.05" data-fx="punch" style="display:inline-block;padding:20px 40px;font-family:Sora;font-weight:800;font-size:120px;color:#FF5A5A">23:59</div>{cap("Sayfayı <span class='v'>40. kez</span> yeniliyorsun 🔄", .5, 96, "up", "margin-top:40px")}</div>''',
f'''<div class="pad" style="top:330px"><div class="el glass num" data-in="0.0" style="display:inline-block;padding:20px 40px;font-family:Sora;font-weight:800;font-size:120px;color:#C6FF3D">00:00</div>{cap("SİTE ÇÖKTÜ 💀", .35, 150, "punch", "margin-top:40px;color:#FF5A5A")}</div>''',
f'''<div class="pad" style="top:330px"><div class="el mono c" data-in="0.05" style="font-size:40px">ERTESİ SABAH ☕</div>{cap("Sepetteki her şey <span class='hl dark' data-hl='1.1'>aynı fiyat<i></i></span> 🙃", .3, 104)}</div>''',
f'''<div class="pad" style="top:330px"><div class="el" data-in="0.05" data-fx="plane">{SEND.format(s=170,c="#C6FF3D")}</div>{cap("Bunu sepeti dolu olan <span class='v'>arkadaşına</span> gönder 😅", .3, 96, "up", "margin-top:40px")}
<div class="el glass" data-in="1.6" style="display:inline-block;margin-top:60px;padding:24px 34px;font-size:38px;font-weight:600">Sahte site uyarısı profilde 👀</div></div>''',
f'''<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding-bottom:160px">
  <div class="el" data-in="0.1" data-fx="punch" style="display:flex;align-items:center;gap:32px">{LOGO.format(s=170,id='id="dot"')}<span class="sora" style="font-weight:700;font-size:170px;letter-spacing:-.045em;padding-bottom:14px">bentaka</span></div>
  <div class="el sora c" data-in="0.7" style="font-weight:600;font-size:60px;margin-top:40px">Future, first<span class="v">.</span></div>
  <div class="el" data-in="1.2" style="margin-top:60px"><span class="chip" style="font-size:28px;padding:16px 30px">TAKİP ET · @BENTAKATR</span></div>
</div>''',
]
# data-hl göreli; sayaçlar için fmt template'te var mı kontrol: whatsapp template'te yok, ekle
secs = ''.join(f'<section class="scene" data-s="{S[i]}" data-e="{E[i]}">{scenes[i]}</section>\n' for i in range(len(scenes)))
h = open(os.path.join(HERE, 'template.html')).read()
if 'data-count' not in h:
    h = h.replace("const scenes=[", "const fmt=(x,f)=>Math.round(x).toLocaleString('tr-TR');\nconst scenes=[", 1)
    h = h.replace("    sc.querySelectorAll('[data-on]')", "    sc.querySelectorAll('[data-count]').forEach(el=>{const p=eOut(prog(lt,+el.dataset.cs,+el.dataset.cd));el.textContent=fmt(+el.dataset.count*p)});\n    sc.querySelectorAll('[data-on]')", 1)
h = (h.replace('/*SCENES*/', secs).replace('/*WIPES*/', ','.join(str(x) for x in [S[4], S[6], S[7]]))
     .replace('/*FLASH*/', ','.join(str(x) for x in [S[4] + .35, S[7] + .1])).replace('/*END*/', str(END)).replace('/*LAST*/', str(S[7])).replace('/*CD*/', '0,0'))
open(os.path.join(HERE, 'reels.html'), 'w').write(h)
tl = {'END': END, 'S': S, 'SPEED': 1, 'cuts': S[1:], 'impacts': [S[4] + .35, S[7] + .1, 0.2],
      'risers': [[round(S[4] - 1.0, 2), 1.0]], 'tr_ticks': [S[1] + .25, 1.2], 'day_ticks': [S[3] + .1, 2.5],
      'sections': [[S[3], 'full'], [S[4], 'build'], [S[7], 'full'], [999, 'outro']]}
json.dump(tl, open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
print(json.dumps({'S': S, 'END': END}))
