#!/usr/bin/env python3
"""Efsane Cuma kaydırmalı gönderi (8 sayfa, 1080×1350). Kullanım: python3 carousel.py <arka_plan_klasörü> <çıktı_klasörü>
arka_plan_klasörü: c1.jpg..c7.jpg (Higgsfield videolarından alınan kareler)"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); BG, OUT = map(os.path.abspath, sys.argv[1:3]); os.makedirs(OUT, exist_ok=True)
FONTS = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts'))
LOGO = ('<svg width="{s}" height="{s}" viewBox="0 0 120 120" aria-hidden="true"><rect x="18" y="8" width="24" height="104" rx="5" fill="#F3F5F8"/>'
        '<circle cx="68" cy="72" r="28" fill="none" stroke="#F3F5F8" stroke-width="24"/><circle cx="68" cy="72" r="8" fill="#C6FF3D"/></svg>')
CSS = f'''@font-face{{font-family:Sora;font-weight:700;src:url(file://{FONTS}/Sora-Bold.ttf)}}
@font-face{{font-family:Sora;font-weight:800;src:url(file://{FONTS}/Sora-ExtraBold.ttf)}}
@font-face{{font-family:Inter;font-weight:400;src:url(file:///usr/share/fonts/opentype/inter/Inter-Regular.otf)}}
@font-face{{font-family:Inter;font-weight:600;src:url(file:///usr/share/fonts/opentype/inter/Inter-SemiBold.otf)}}
@font-face{{font-family:Mono;font-weight:500;src:url(file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf)}}
*{{box-sizing:border-box;margin:0}} body{{width:1080px;height:1350px;overflow:hidden;background:#0B0E14;font-family:Inter,sans-serif;color:#F3F5F8}}
.bg{{position:absolute;inset:0;background-size:cover;background-position:center}}
.scrim{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,14,20,.82),rgba(11,14,20,.72) 40%,rgba(11,14,20,.9))}}
.wm{{position:absolute;right:-170px;bottom:-60px;opacity:.05}}
.page{{position:absolute;inset:0;padding:72px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.chip{{display:inline-flex;align-items:center;gap:10px;padding:10px 20px;border-radius:999px;background:#C6FF3D;color:#0B0E14;font-family:Mono,monospace;font-size:22px;letter-spacing:.12em}}
.chip.red{{background:#FF5A5A}} .chip.ghost{{background:rgba(243,245,248,.08);color:#F3F5F8;border:2px solid rgba(243,245,248,.16)}}
.mono{{font-family:Mono,monospace;letter-spacing:.12em;text-transform:uppercase}}
.h1{{font-family:Sora,sans-serif;font-weight:700;letter-spacing:-.035em;line-height:1.05}}
.big{{font-family:Sora,sans-serif;font-weight:800;letter-spacing:-.045em;line-height:.95}}
.v{{color:#C6FF3D}} .c{{color:#8A93A6}} .r{{color:#FF5A5A}}
.hl{{background:#C6FF3D;color:#0B0E14;padding:0 14px;border-radius:8px}}
.glass{{background:linear-gradient(160deg,rgba(26,31,43,.94),rgba(11,14,20,.9));border:2px solid rgba(243,245,248,.1);border-radius:36px}}
.badge{{width:104px;height:104px;border-radius:30px;background:#C6FF3D;color:#0B0E14;display:flex;align-items:center;justify-content:center;font-family:Sora,sans-serif;font-weight:800;font-size:62px;flex:none}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:center;padding-top:26px;border-top:2px solid rgba(243,245,248,.1)}}
.body{{font-size:40px;line-height:1.4;color:#D9DEE7}}
.ex{{font-family:Mono,monospace;font-size:44px;padding:30px 36px}}
'''
def page(n, bg, body, label='DİKKAT!', swipe=False):
    sw = ('<span class="mono v" style="font-size:22px;display:flex;align-items:center;gap:10px">KAYDIR <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#C6FF3D" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg></span>' if swipe else '')
    bgs = f'<div class="bg" style="background-image:url(file://{BG}/{bg})"></div><div class="scrim"></div>' if bg else ''
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{bgs}
<svg class="wm" width="760" height="760" viewBox="0 0 120 120"><rect x="18" y="8" width="24" height="104" rx="5" fill="#F3F5F8"/><circle cx="68" cy="72" r="28" fill="none" stroke="#F3F5F8" stroke-width="24"/><circle cx="68" cy="72" r="8" fill="#F3F5F8"/></svg>
<div class="page"><div class="top"><span class="chip {'red' if label=='DİKKAT!' else ''}">{label}</span><span class="mono c" style="font-size:22px">EFSANE CUMA · 27 KASIM</span></div>
<div style="flex:1;display:flex;flex-direction:column;justify-content:center">{body}</div>
<div class="foot"><div style="display:flex;align-items:center;gap:14px">{LOGO.format(s=44)}<span style="font-size:28px;font-weight:600">@bentaka</span></div>
<div style="display:flex;align-items:center;gap:26px">{sw}<span class="mono c" style="font-size:22px">{n}/8</span></div></div></div></body></html>'''

def sign(k, title, desc, extra=''):
    return f'''<div style="display:flex;align-items:center;gap:32px">{f'<div class="badge">{k}</div>'}<div class="mono v" style="font-size:26px">İŞARET {k} / 5</div></div>
<div class="h1" style="font-size:88px;margin-top:44px">{title}</div><div class="body" style="margin-top:30px">{desc}</div>{extra}'''

P = [
 page(1, 'c1.jpg', '''<div class="h1" style="font-size:104px">Efsane Cuma'da<br><span class="hl">sahte siteyi</span><br>10 saniyede anla.</div>
<div class="body" style="margin-top:44px">Dolandırıcılar büyük alışveriş sitelerinin birebir kopyasını yapıyor. Ödemeden önce bu 5 işarete bak.</div>''', swipe=True),
 page(2, 'c2.jpg', sign(1, 'Adrese bak.', 'Tek bir harf farkı bile sahte site demek. "m" yerine "rn", "l" yerine "1" en sık kullanılan hileler.',
   '''<div style="display:flex;flex-direction:column;gap:20px;margin-top:50px"><div class="glass ex"><span class="c">https://</span>magaza.com <span class="v" style="font-size:28px">✓ GERÇEK</span></div>
   <div class="glass ex" style="border-color:rgba(255,90,90,.6)"><span class="c">https://</span><u class="r">rn</u>agaza.com <span class="r" style="font-size:28px">✕ SAHTE</span></div></div>''')),
 page(3, 'c3.jpg', sign(2, 'Kilit simgesi<br>kanıt değil.', 'Adres çubuğundaki kilit ya da "güvenli" yazısı sadece bağlantının şifreli olduğunu gösterir. Sahte siteler de kilit alabilir.')),
 page(4, 'c4.jpg', sign(3, 'Akıl almaz indirim<br>+ geri sayım = <span class="r">DUR.</span>', 'Piyasanın çok altında fiyat ve "son 5 dakika" baskısı, düşünmeden ödeme yaptırmak için kullanılır.',
   '<div style="display:flex;align-items:center;gap:30px;margin-top:44px"><span class="big r" style="font-size:170px">%90</span><span class="glass mono" style="padding:22px 30px;font-size:44px">00:04:59</span></div>')),
 page(5, 'c5.jpg', sign(4, "IBAN'a havale isteyen<br>satıcı.", 'Sosyal medyada ön ödemeyi IBAN\'a isteyen hesaplar ürünü göndermeyebilir. Havalede paranı geri almak çok zor.')),
 page(6, 'c5.jpg', sign(5, 'Linkli SMS\'e<br>tıklama.', 'Kargo, banka ya da mağaza adına gelen "adresini güncelle", "ödemen alınamadı" mesajlarındaki linke basma. Uygulamayı kendin aç.',
   '<div style="margin-top:44px;padding:30px 36px;border-radius:36px 36px 36px 10px;background:#F3F5F8;color:#0B0E14;font-size:36px;line-height:1.35">Kargonuz teslim edilemedi. Adresinizi güncelleyin: <u style="color:#2B59FF">kargo-takip.top/x7k</u></div>')),
 page(7, 'c6.jpg', '''<div class="mono v" style="font-size:26px">ÇÖZÜM</div><div class="h1" style="font-size:100px;margin-top:24px">Sanal kart <span class="v">kullan.</span></div>
<div style="display:flex;flex-direction:column;gap:22px;margin-top:44px;font-size:42px;font-weight:600">
<div>✅ Bankanın uygulamasından sanal kart aç</div><div>✅ Limiti ürün tutarı kadar yap</div><div>✅ Alışverişten sonra kartı kapat</div></div>
<div class="glass" style="margin-top:44px;padding:30px 36px;font-size:34px;line-height:1.4"><b class="r">Kart bilgin çalındıysa:</b> hemen bankanı ara, kartı iptal ettir ve savcılığa ya da polise bildir.</div>''', label='ÇÖZÜM'),
 page(8, 'c7.jpg', '''<div class="h1" style="font-size:110px">Bunu <span class="v">annene</span> gönder.</div>
<div class="body" style="margin-top:34px">İnternetten alışveriş yapan herkesin bilmesi lazım. Kaydet, Efsane Cuma'da lazım olacak.</div>
<div style="display:flex;gap:20px;margin-top:56px"><span class="chip" style="font-size:28px;padding:18px 30px">GÖNDER</span><span class="chip ghost" style="font-size:28px;padding:18px 30px">KAYDET</span><span class="chip ghost" style="font-size:28px;padding:18px 30px">TAKİP ET</span></div>
<div style="display:flex;align-items:center;gap:24px;margin-top:80px">''' + LOGO.format(s=90) + '''<span style="font-family:Sora;font-weight:700;font-size:90px;letter-spacing:-.045em">bentaka</span></div>
<div style="font-family:Sora;font-weight:700;font-size:40px;color:#8A93A6;margin-top:14px">Future, first<span class="v">.</span></div>''', label='PAYLAŞ'),
]
tmp = os.path.join(OUT, '_html'); os.makedirs(tmp, exist_ok=True)
for i, h in enumerate(P, 1): open(os.path.join(tmp, f'p{i}.html'), 'w').write(h)
js = f'''const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1350}}}});
for(let i=1;i<=8;i++){{await p.goto('file://{tmp}/p'+i+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(150);
await p.screenshot({{path:'{OUT}/efsane-cuma-'+i+'.jpg',type:'jpeg',quality:92}});}}await b.close();}})();'''
open(os.path.join(tmp, 'r.js'), 'w').write(js)
subprocess.run(['node', os.path.join(tmp, 'r.js')], check=True)
print('tamam')
