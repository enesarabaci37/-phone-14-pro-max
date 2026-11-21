#!/usr/bin/env python3
"""Efsane Cuma Reels: seslendirme sürelerinden zaman çizelgesi + yazı katmanı (reels.html) + timeline.json üretir.
Kullanım: python3 build.py <ses_klasörü> [tempo=1.22]   (ses_klasörü: t1.wav..t8.wav)
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
VO, TEMPO = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 1.22
GAP, LEAD, TAIL = 0.3, 0.25, 2.3
dur = lambda p: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
D = [dur(os.path.join(VO, f't{i}.wav')) / TEMPO for i in range(1, 9)]
V = [0.4]
for d in D[:-1]: V.append(round(V[-1] + d + GAP, 3))
S = [0.0] + [round(v - LEAD, 3) for v in V[1:]]
END = round(V[-1] + D[-1] + TAIL, 2)
E = S[1:] + [99]
r = lambda i, x: round(x * D[i] + LEAD, 2)   # sahne içi zaman: ses süresinin oranı

LOGO = ('<svg width="{s}" height="{s}" viewBox="0 0 120 120" aria-hidden="true"><rect x="18" y="8" width="24" height="104" rx="5" fill="#F3F5F8"/>'
        '<circle cx="68" cy="72" r="28" fill="none" stroke="#F3F5F8" stroke-width="24"/><circle {id} cx="68" cy="72" r="8" fill="#C6FF3D"/></svg>')
ICON = {
 'send': '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7z"/></svg>',
 'save': '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
 'lock': '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
 'warn': '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
 'card': '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/></svg>',
}
ic = lambda n, s=40, c='#C6FF3D': ICON[n].format(s=s, c=c)
num = lambda n: f'<div class="badge">{n}</div>'

def sign(n, title, sub, t):
    return (f'<div class="el glass sign" data-in="{t}" data-fx="left">{num(n)}<div><div class="st">{title}</div>'
            f'<div class="ss">{sub}</div></div></div>')

scenes = [
# 1 Kanca
f'''<div class="pad" style="top:430px">
  <div class="el" data-in="0.1"><span class="chip red">{ic("warn",26,"#0B0E14")} DİKKAT!</span></div>
  <div class="el h1" data-in="{r(0,.0)}" style="font-size:118px;margin-top:44px">Efsane Cuma'da</div>
  <div class="el h1" data-in="{r(0,.3)}" style="font-size:96px;margin-top:10px">bu hatayı yaparsan</div>
  <div class="el big" data-in="{r(0,.62)}" data-fx="punch" style="font-size:150px;margin-top:40px"><span class="hl dark" data-hl="{r(0,.7)}">paran gider.<i></i></span></div>
</div>''',
# 2 Kopya site
f'''<div class="pad" style="top:440px">
  <div class="el label" data-in="0.1">Sahte site tuzağı</div>
  <div class="el h1" data-in="{r(1,.0)}" style="font-size:88px;margin-top:40px">Büyük sitelerin <span class="v">birebir kopyası</span> yapılıyor.</div>
  <div class="el" data-in="{r(1,.3)}" style="display:flex;gap:24px;margin-top:70px">
    <div class="glass mock"><div class="bar"><b></b><b></b><b></b><span>magaza.com</span></div><div class="ok">GERÇEK</div></div>
    <div class="glass mock bad"><div class="bar"><b></b><b></b><b></b><span>rnagaza.com</span></div><div class="ko">SAHTE</div></div>
  </div>
  <div class="el h1" data-in="{r(1,.6)}" data-fx="punch" style="font-size:72px;margin-top:80px">5 işaretle <span class="v">hemen anla</span> 👇</div>
</div>''',
# 3 İşaret 1-2
f'''<div class="pad" style="top:400px">
  <div class="el label" data-in="0.1">5 işaret</div>
  <div style="display:flex;flex-direction:column;gap:30px;margin-top:44px">
    {sign(1, "Adrese bak", "Tek harf farkı = sahte site", r(2,.0))}
    <div class="el glass url" data-in="{r(2,.12)}"><span class="c">https://</span><span class="m">r</span><span class="m">n</span>agaza.com <span class="tag">m değil “r+n”</span></div>
    {sign(2, "Kilit simgesi kanıt değil", "“Güvenli” yazısı, sitenin gerçek olduğunu göstermez", r(2,.5))}
  </div>
</div>''',
# 4 İşaret 3
f'''<div class="pad" style="top:440px">
  {sign(3, "Akıl almaz indirim", "+ geri sayım baskısı varsa", r(3,.0))}
  <div class="el big num" data-in="{r(3,.15)}" data-fx="punch" style="font-size:250px;margin-top:60px;color:#FF5A5A">%90</div>
  <div class="el glass" data-in="{r(3,.3)}" style="display:inline-flex;align-items:center;gap:20px;padding:26px 40px;margin-top:30px">
    <span class="mono c" style="font-size:26px">BİTİYOR</span><span class="sora num" id="cd" style="font-weight:700;font-size:72px">00:04:59</span></div>
  <div class="el big" data-in="{r(3,.65)}" data-fx="punch" style="font-size:150px;margin-top:60px"><span class="hl dark" data-hl="{r(3,.72)}">DUR.<i></i></span></div>
</div>''',
# 5 İşaret 4-5
f'''<div class="pad" style="top:400px">
  <div style="display:flex;flex-direction:column;gap:30px">
    {sign(4, "IBAN'a havale isteyen satıcı", "Sosyal medyadan ön ödeme = risk", r(4,.0))}
    {sign(5, "Linkli kargo / banka SMS'i", "Mesajdaki linke tıklama", r(4,.48))}
    <div class="el sms" data-in="{r(4,.6)}"><div class="mono c" style="font-size:22px">KARGO · şimdi</div>
      <div style="font-size:38px;line-height:1.35;margin-top:10px">Kargonuz teslim edilemedi. Adresinizi güncelleyin: <u class="lnk">kargo-takip.top/x7k</u></div></div>
  </div>
</div>''',
# 6 Çözüm
f'''<div class="pad" style="top:440px">
  <div class="el label" data-in="0.1">Çözüm</div>
  <div class="el h1" data-in="{r(5,.0)}" style="font-size:110px;margin-top:36px">Sanal kart <span class="v">kullan.</span></div>
  <div class="el vcard" data-in="{r(5,.15)}" data-fx="punch"><div style="display:flex;justify-content:space-between;align-items:center">{ic("card",56,"#0B0E14")}<span class="mono" style="font-size:24px;color:#0B0E14">SANAL KART</span></div>
    <div class="sora num" style="font-size:54px;font-weight:700;color:#0B0E14;margin-top:60px">•••• •••• •••• 2711</div>
    <div class="mono" style="font-size:24px;color:#0B0E14;margin-top:18px">LİMİT = ÜRÜN TUTARI</div></div>
  <div class="el step" data-in="{r(5,.35)}">{num("✓")}<span>Limit: ürün tutarı kadar</span></div>
  <div class="el step" data-in="{r(5,.7)}">{num("✓")}<span>Alışverişten sonra <b class="v">kapat</b></span></div>
</div>''',
# 7 Çağrı
f'''<div class="pad" style="top:470px">
  <div class="el" data-in="0.1" data-fx="plane">{ic("send",180)}</div>
  <div class="el h1" data-in="{r(6,.0)}" style="font-size:110px;margin-top:50px">Bunu <span class="v">annene</span> gönder.</div>
  <div class="el h1 c" data-in="{r(6,.35)}" style="font-size:62px;margin-top:30px">İnternetten alışveriş yapan herkese.</div>
  <div class="el" data-in="{r(6,.6)}" style="display:flex;gap:22px;margin-top:80px">
    <span class="chip" style="font-size:30px;padding:20px 34px">{ic("send",30,"#0B0E14")}GÖNDER</span>
    <span class="chip ghost" style="font-size:30px;padding:20px 34px">{ic("save",30,"#F3F5F8")}KAYDET</span></div>
</div>''',
# 8 Kapanış
f'''<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding-bottom:160px">
  <div class="el" data-in="0.1" data-fx="punch" style="display:flex;align-items:center;gap:32px">{LOGO.format(s=170,id='id="dot"')}
    <span class="sora" style="font-weight:700;font-size:170px;letter-spacing:-.045em;padding-bottom:14px">bentaka</span></div>
  <div class="el sora c" data-in="0.7" style="font-weight:600;font-size:60px;margin-top:40px">Future, first<span class="v">.</span></div>
  <div class="el" data-in="1.3" style="margin-top:60px"><span class="chip" style="font-size:28px;padding:16px 30px">TAKİP ET · @BENTAKA</span></div>
</div>''',
]

secs = ''.join(f'<section class="scene" data-s="{S[i]}" data-e="{E[i]}">{scenes[i]}</section>\n' for i in range(8))
cd_s, cd_e = S[3], E[3]
html = open(os.path.join(HERE, 'template.html')).read()
html = (html.replace('/*SCENES*/', secs).replace('/*WIPES*/', ','.join(str(x) for x in [S[1], S[2], S[5], S[6], S[7]]))
        .replace('/*FLASH*/', ','.join(str(x) for x in [0.4 + r(0, .62) - .25, S[3] + r(3, .65), S[7] + .1]))
        .replace('/*END*/', str(END)).replace('/*LAST*/', str(S[7])).replace('/*CD*/', f'{cd_s},{cd_e}'))
open(os.path.join(HERE, 'reels.html'), 'w').write(html)
tl = {'END': END, 'S': S, 'V': V, 'D': D, 'SPEED': TEMPO, 'cuts': S[1:],
      'impacts': [0.4 + r(0, .62) - .25, S[3] + r(3, .65), S[7] + .1],
      'risers': [[round(S[5] - 1.0, 3), 1.0], [round(S[7] - 1.2, 3), 1.2]],
      'tr_ticks': [S[3] + r(3, .3), 1.2], 'day_ticks': [S[5] + r(5, .15), 0.6],
      'sections': [[S[1], 'full'], [S[2], 'tension'], [S[5], 'full'], [S[6], 'build'], [S[7], 'full'], [999, 'outro']]}
json.dump(tl, open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
print(json.dumps({'S': S, 'END': END}))
