#!/usr/bin/env python3
"""15 yaş sosyal medya yasağı kaydırmalı gönderi (8 sayfa, 1080×1350). Kullanım: python3 carousel.py <arka_plan_klasörü> <çıktı_klasörü>
Kaynak: 7578 sayılı Kanun (RG 1 Mayıs 2026), Siber Güvenlik Başkanlığı yönetmeliği (RG 10 Ekim 2026, yürürlük 1 Kasım 2026)."""
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
def page(n, bg, body, label='BUNU BİLMİYORDUN', swipe=False):
    sw = ('<span class="mono v" style="font-size:22px;display:flex;align-items:center;gap:10px">KAYDIR <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#C6FF3D" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg></span>' if swipe else '')
    bgs = f'<div class="bg" style="background-image:url(file://{BG}/{bg})"></div><div class="scrim"></div>' if bg else ''
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{bgs}
<svg class="wm" width="760" height="760" viewBox="0 0 120 120"><rect x="18" y="8" width="24" height="104" rx="5" fill="#F3F5F8"/><circle cx="68" cy="72" r="28" fill="none" stroke="#F3F5F8" stroke-width="24"/><circle cx="68" cy="72" r="8" fill="#F3F5F8"/></svg>
<div class="page"><div class="top"><span class="chip {'red' if label=='YASAK' else ''}">{label}</span><span class="mono c" style="font-size:22px">SOSYAL MEDYA · 15 YAŞ</span></div>
<div style="flex:1;display:flex;flex-direction:column;justify-content:center">{body}</div>
<div class="foot"><div style="display:flex;align-items:center;gap:14px">{LOGO.format(s=44)}<span style="font-size:28px;font-weight:600">@bentaka</span></div>
<div style="display:flex;align-items:center;gap:26px">{sw}<span class="mono c" style="font-size:22px">{n}/8</span></div></div></div></body></html>'''

def sign(k, title, desc, extra=''):
    return f'''<div style="display:flex;align-items:center;gap:32px">{f'<div class="badge">{k}</div>'}<div class="mono v" style="font-size:26px">İŞARET {k} / 5</div></div>
<div class="h1" style="font-size:88px;margin-top:44px">{title}</div><div class="body" style="margin-top:30px">{desc}</div>{extra}'''

P = [
 page(1, 'y1.png', '''<div class="h1" style="font-size:100px">15 yaş altına<br>sosyal medya<br><span class="hl">yasağı başladı.</span></div>
<div class="h1" style="font-size:64px;margin-top:44px">Hesabın kapanır mı? <span class="v">Kaydır, öğren.</span></div>''', swipe=True),
 page(2, 'y1.png', '''<div class="mono v" style="font-size:26px">NE DEĞİŞTİ?</div><div class="h1" style="font-size:84px;margin-top:30px">1 Kasım 2026'dan beri sosyal ağlar <span class="v">15 yaşından küçüklere</span> hizmet veremiyor.</div>
<div class="body" style="margin-top:36px">Instagram, TikTok, X, Facebook gibi platformlar artık kullanıcının yaşını doğrulamak zorunda.</div>'''),
 page(3, 'y3.png', '''<div class="mono v" style="font-size:26px">YAŞ NASIL DOĞRULANIYOR?</div><div class="h1" style="font-size:96px;margin-top:30px"><span class="v">e-Devlet</span> üzerinden.</div>
<div class="glass" style="margin-top:44px;padding:34px 40px;font-size:40px;line-height:1.45">Platforma kimliğin <b>gitmiyor.</b> Sadece <b class="v">"15 yaş üstü"</b> ya da <b class="v">"18 yaş üstü"</b> bilgisi gidiyor.</div>'''),
 page(4, 'y4.png', '''<div class="mono v" style="font-size:26px">MEVCUT HESAPLAR</div><div class="h1" style="font-size:100px;margin-top:30px">Son tarih:<br><span class="hl">31 Mart 2027</span></div>
<div class="body" style="margin-top:40px">Bu tarihe kadar yaşı doğrulanmayan ya da 15 yaşından küçük çıkan hesaplar <b class="r">kapatılıyor</b>, verileri siliniyor.</div>'''),
 page(5, 'y2.png', '''<div class="mono v" style="font-size:26px">15–17 YAŞ ARASI</div><div class="h1" style="font-size:84px;margin-top:30px">Hesap kapanmıyor ama <span class="v">kurallar değişiyor.</span></div>
<div style="display:flex;flex-direction:column;gap:20px;margin-top:40px;font-size:42px;font-weight:600"><div>🔒 Hesap varsayılan olarak gizli</div><div>📵 Canlı yayın yok</div><div>♾️ Sonsuz kaydırma yok</div><div>🎯 Kişiselleştirilmiş reklam yok</div></div>'''),
 page(6, 'y2.png', '''<div class="mono v" style="font-size:26px">EBEVEYNSEN</div><div class="h1" style="font-size:90px;margin-top:30px">3 şey yap:</div>
<div style="display:flex;flex-direction:column;gap:26px;margin-top:40px;font-size:42px;font-weight:600"><div>1️⃣ Çocuğunla hesaplarını konuş</div><div>2️⃣ 31 Mart 2027'den önce yaşını doğrulat</div><div>3️⃣ Kapanacak hesaplardaki fotoğrafları yedekle</div></div>'''),
 page(7, 'y3.png', '''<div class="mono v" style="font-size:26px">EFSANE Mİ, GERÇEK Mİ?</div>
<div class="glass" style="margin-top:36px;padding:32px 38px"><div style="font-size:40px;font-weight:600">"Kimliğim Instagram'a gidecek."</div><div class="h1 r" style="font-size:54px;margin-top:12px">EFSANE ✕</div><div class="body" style="font-size:32px;margin-top:8px">Sadece yaş grubu bilgisi paylaşılıyor.</div></div>
<div class="glass" style="margin-top:26px;padding:32px 38px"><div style="font-size:40px;font-weight:600">"Hesabım yarın kapanacak."</div><div class="h1 r" style="font-size:54px;margin-top:12px">EFSANE ✕</div><div class="body" style="font-size:32px;margin-top:8px">Mevcut hesaplar için süre 31 Mart 2027.</div></div>''', label='EFSANE Mİ?'),
 page(8, 'y4.png', '''<div class="h1" style="font-size:100px">Çocuğu ya da kardeşi olan <span class="v">birine gönder.</span></div>
<div class="body" style="margin-top:34px">Son güne kalmasınlar. Kaydet, 31 Mart'tan önce lazım olacak.</div>
<div style="display:flex;gap:20px;margin-top:56px"><span class="chip" style="font-size:28px;padding:18px 30px">GÖNDER</span><span class="chip ghost" style="font-size:28px;padding:18px 30px">KAYDET</span><span class="chip ghost" style="font-size:28px;padding:18px 30px">TAKİP ET</span></div>
<div style="display:flex;align-items:center;gap:24px;margin-top:80px">''' + LOGO.format(s=90) + '''<span style="font-family:Sora;font-weight:700;font-size:90px;letter-spacing:-.045em">bentaka</span></div>
<div style="font-family:Sora;font-weight:700;font-size:40px;color:#8A93A6;margin-top:14px">Future, first<span class="v">.</span></div>''', label='PAYLAŞ'),
]
tmp = os.path.join(OUT, '_html'); os.makedirs(tmp, exist_ok=True)
for i, h in enumerate(P, 1): open(os.path.join(tmp, f'p{i}.html'), 'w').write(h)
js = f'''const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1350}}}});
for(let i=1;i<=8;i++){{await p.goto('file://{tmp}/p'+i+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(150);
await p.screenshot({{path:'{OUT}/yas-'+i+'.jpg',type:'jpeg',quality:92}});}}await b.close();}})();'''
open(os.path.join(tmp, 'r.js'), 'w').write(js)
subprocess.run(['node', os.path.join(tmp, 'r.js')], check=True)
print('tamam')
