#!/usr/bin/env python3
"""GTA 6 içeriği: 5 sayfalık kaydırmalı gönderi + 18 sn Reels (HTML kaynakları)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.abspath(os.path.join(HERE, '..', '..', 'fonts'))

# --- Hesaplar (2026) -------------------------------------------------------
TR_PRICE, TR_GROSS, TR_HOURS_MONTH = 3999, 33030, 225
DE_PRICE, DE_WAGE = 79.99, 13.90
US_PRICE, US_WAGE = 79.99, 7.25
tr_hourly = TR_GROSS / TR_HOURS_MONTH            # 146,80 TL
H = {'de': DE_PRICE / DE_WAGE, 'us': US_PRICE / US_WAGE, 'tr': TR_PRICE / tr_hourly}
TR_DAYS = H['tr'] / 7.5

def tr_num(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')

HEAD = f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Bentaka GTA 6</title><style>
@font-face{{font-family:Sora;font-weight:600;src:url(file://{FONTDIR}/Sora-SemiBold.ttf)}}
@font-face{{font-family:Sora;font-weight:700;src:url(file://{FONTDIR}/Sora-Bold.ttf)}}
@font-face{{font-family:Inter;font-weight:400;src:url(file:///usr/share/fonts/opentype/inter/Inter-Regular.otf)}}
@font-face{{font-family:Inter;font-weight:600;src:url(file:///usr/share/fonts/opentype/inter/Inter-SemiBold.otf)}}
@font-face{{font-family:Mono;font-weight:500;src:url(file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf)}}
*{{box-sizing:border-box}} body{{margin:0;background:#0B0E14}}
.root{{position:relative;overflow:hidden;background:#0B0E14;font-family:Inter,sans-serif;color:#F3F5F8}}
.mono{{font-family:Mono,monospace;letter-spacing:.1em}}
.sora{{font-family:Sora,sans-serif}}
.chip{{padding:10px 20px;border-radius:999px;background:#C6FF3D;color:#0B0E14;font-family:Mono,monospace;font-size:22px;letter-spacing:.1em}}
.v{{color:#C6FF3D}} .c{{color:#8A93A6}}
.card{{border-radius:32px;background:#1A1F2B}}
</style></head><body>'''

MONO_SVG = ('<svg width="{s}" height="{s}" viewBox="0 0 120 120" aria-hidden="true"><rect x="18" y="8" width="24" height="104" rx="5" fill="{b}"></rect>'
            '<circle cx="68" cy="72" r="28" fill="none" stroke="{b}" stroke-width="24"></circle><circle cx="68" cy="72" r="8" fill="{d}"></circle></svg>')

def mono(s, b='#F3F5F8', d='#C6FF3D'):
    return MONO_SVG.format(s=s, b=b, d=d)

WATERMARK = ('<svg style="position:absolute;right:-190px;bottom:{b}px;opacity:.05;pointer-events:none" width="880" height="880" viewBox="0 0 120 120" aria-hidden="true">'
             '<rect x="18" y="8" width="24" height="104" rx="5" fill="#F3F5F8"></rect><circle cx="68" cy="72" r="28" fill="none" stroke="#F3F5F8" stroke-width="24"></circle>'
             '<circle cx="68" cy="72" r="8" fill="#F3F5F8"></circle></svg>')

# Özgün çizim: koltukta oturan, kulaklıklı oyuncu (arkadan) ve ekranda neon sahil şehri.
PALM = ('<path d="M330 360 C334 320 344 280 362 236" fill="none" stroke="#1A1F2B" stroke-width="10" stroke-linecap="round"/>'
        '<path d="M362 236 C330 220 305 226 286 244 C312 232 336 234 362 236Z M362 236 C340 204 316 196 296 200 C322 206 342 216 362 236Z '
        'M362 236 C368 200 384 184 404 180 C390 196 378 214 362 236Z M362 236 C396 214 424 218 440 236 C418 228 392 230 362 236Z '
        'M362 236 C392 240 410 256 418 278 C402 262 384 250 362 236Z M362 236 C340 248 326 266 322 290 C334 268 346 254 362 236Z" fill="#1A1F2B"/>')

def windows(x, y, w, h):
    out = []
    for yy in range(y + 14, y + h - 10, 22):
        for xx in range(x + 10, x + w - 10, 16):
            if (xx * 7 + yy * 3) % 5 < 2:
                out.append(f'<rect x="{xx}" y="{yy}" width="6" height="9" fill="#5B7CFF"/>')
    return ''.join(out)

BUILDINGS = [(150, 250, 58, 110), (204, 206, 46, 154), (246, 276, 70, 84), (598, 228, 52, 132),
             (646, 188, 42, 172), (684, 262, 64, 98), (744, 222, 46, 138)]

def scene_svg(width, height):
    b = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#1A1F2B"/>' + windows(x, y, w, h) for x, y, w, h in BUILDINGS)
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 940 620" role="img" aria-label="Koltukta kulaklıkla oyun oynayan kişi, ekranda neon sahil şehri (çizim)">
<defs><clipPath id="scr"><rect x="150" y="40" width="640" height="380" rx="14"/></clipPath></defs>
<rect width="940" height="620" fill="#1A1F2B"/>
<rect x="126" y="18" width="688" height="424" rx="30" fill="#C6FF3D" opacity="0.06"/>
<rect x="146" y="36" width="648" height="388" rx="18" fill="#0B0E14" stroke="#8A93A6" stroke-width="4"/>
<g clip-path="url(#scr)">
<rect x="150" y="40" width="640" height="380" fill="#0B0E14"/>
<circle cx="470" cy="250" r="118" fill="#C6FF3D"/>
<rect x="340" y="238" width="260" height="7" fill="#0B0E14"/><rect x="340" y="258" width="260" height="9" fill="#0B0E14"/>
<rect x="340" y="281" width="260" height="11" fill="#0B0E14"/><rect x="340" y="307" width="260" height="13" fill="#0B0E14"/>
<rect x="340" y="335" width="260" height="15" fill="#0B0E14"/>
{b}
<rect x="150" y="360" width="640" height="60" fill="#0B0E14"/>
<rect x="415" y="372" width="110" height="4" fill="#C6FF3D" opacity="0.7"/><rect x="432" y="386" width="76" height="3" fill="#C6FF3D" opacity="0.5"/>
<rect x="448" y="398" width="44" height="3" fill="#C6FF3D" opacity="0.35"/>
<g transform="translate(40 -10)">{PALM}</g>
<g transform="translate(900 -10) scale(-1 1)">{PALM}</g>
</g>
<rect x="420" y="424" width="100" height="16" fill="#0B0E14"/><rect x="330" y="440" width="280" height="10" rx="5" fill="#0B0E14"/>
<rect x="60" y="492" width="130" height="170" rx="40" fill="#0B0E14"/><rect x="750" y="492" width="130" height="170" rx="40" fill="#0B0E14"/>
<rect x="100" y="526" width="740" height="140" rx="40" fill="#0B0E14"/>
<path d="M352 620 C352 538 398 500 470 500 C542 500 588 538 588 620Z" fill="#1A1F2B" stroke="#C6FF3D" stroke-width="3"/>
<circle cx="470" cy="456" r="56" fill="#0B0E14" stroke="#C6FF3D" stroke-width="3"/>
<path d="M410 452 C410 396 530 396 530 452" fill="none" stroke="#5B7CFF" stroke-width="10" stroke-linecap="round"/>
<rect x="398" y="438" width="22" height="40" rx="9" fill="#5B7CFF"/><rect x="520" y="438" width="22" height="40" rx="9" fill="#5B7CFF"/>
<path d="M640 600 c8 -12 52 -12 60 0 c7 10 5 26 -5 26 c-9 0 -12 -9 -25 -9 c-13 0 -16 9 -25 9 c-10 0 -12 -16 -5 -26z" fill="#8A93A6"/>
</svg>'''

def footer(page, cover=False):
    swipe = ('<span style="display:flex;align-items:center;gap:10px;color:#C6FF3D">KAYDIR '
             '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#C6FF3D" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg></span>') if cover else ''
    return (f'<div style="display:flex;align-items:center;justify-content:space-between;padding-top:28px;border-top:2px solid #1A1F2B">'
            f'<div style="display:flex;align-items:center;gap:14px">{mono(40)}<span style="font-size:26px;font-weight:600">@bentaka</span></div>'
            f'<div class="mono" style="display:flex;align-items:center;gap:24px;font-size:22px;letter-spacing:.08em">{swipe}<span class="c">{page}</span></div></div>')

def topbar(label):
    return f'<div style="display:flex;align-items:center;gap:18px"><span class="chip">OYUN</span><span class="mono c" style="font-size:22px">{label}</span></div>'

def slide(body, page, cover=False):
    return (HEAD + '<div class="root" style="width:1080px;height:1350px"><div style="height:1350px;padding:72px;display:flex;flex-direction:column;gap:48px">'
            + body + footer(page, cover) + '</div>' + WATERMARK.format(b=150) + '</div></body></html>')

def bar_row(label, hours, detail, max_h, accent, width=936, big=52):
    pct = hours / max_h * 100
    color = '#C6FF3D' if accent else '#8A93A6'
    return (f'<div style="display:flex;flex-direction:column;gap:14px">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline"><span class="sora" style="font-weight:600;font-size:40px">{label}</span>'
            f'<span class="sora" style="font-weight:700;font-size:{big}px;color:{"#C6FF3D" if accent else "#F3F5F8"}">{tr_num(hours)} saat</span></div>'
            f'<div style="height:28px;border-radius:14px;background:#1A1F2B;overflow:hidden"><div style="width:{pct:.1f}%;height:100%;border-radius:14px;background:{color}"></div></div>'
            f'<span class="mono c" style="font-size:22px;letter-spacing:.06em">{detail}</span></div>')

MAXH = H['tr']
ROWS = [('Almanya', H['de'], '13,90 € / SAAT · OYUN 79,99 €', False),
        ('ABD', H['us'], '7,25 $ / SAAT · OYUN 79,99 $', False),
        ('Türkiye', H['tr'], f'{tr_num(tr_hourly, 2)} TL / SAAT · OYUN 3.999 TL', True)]

S1 = slide(topbar('GTA 6 · 19 KASIM 2026') + f'''
<div style="flex-grow:1;position:relative;border-radius:36px;overflow:hidden;display:flex;align-items:center;justify-content:center;background:#1A1F2B">
{scene_svg(936, 618)}
<span class="mono" style="position:absolute;left:32px;bottom:26px;font-size:18px;color:#F3F5F8;opacity:.45">© BENTAKA</span></div>
<div style="display:flex;flex-direction:column;gap:18px">
<h1 class="sora" style="margin:0;font-weight:700;font-size:86px;line-height:1.04;letter-spacing:-.03em">GTA 6 için <span class="v">kaç saat</span> çalışman gerekiyor?</h1>
<p class="c" style="margin:0;font-size:32px;line-height:1.4">Türkiye, Almanya ve ABD'de asgari ücretle hesapladık.</p></div>''', '01 / 05', cover=True)

S2 = slide(topbar('TÜRKİYE FİYATI') + f'''
<div style="flex-grow:1;display:flex;flex-direction:column;justify-content:center;gap:36px">
<h2 class="sora" style="margin:0;font-weight:700;font-size:80px;line-height:1.05;letter-spacing:-.03em">Türkiye'de kaç TL?</h2>
<div class="card" style="padding:44px;display:flex;justify-content:space-between;align-items:flex-end">
<div style="display:flex;flex-direction:column;gap:10px"><span class="mono v" style="font-size:22px">STANDART</span><span class="c" style="font-size:30px">Dijital sürüm</span></div>
<span class="sora" style="font-weight:700;font-size:112px;line-height:1;letter-spacing:-.04em">3.999 TL</span></div>
<div class="card" style="padding:44px;display:flex;justify-content:space-between;align-items:flex-end">
<div style="display:flex;flex-direction:column;gap:10px"><span class="mono v" style="font-size:22px">ULTIMATE</span><span class="c" style="font-size:30px">Ek içerik paketiyle</span></div>
<span class="sora" style="font-weight:700;font-size:112px;line-height:1;letter-spacing:-.04em">4.999 TL</span></div>
<p style="margin:0;font-size:36px;line-height:1.45">Oyun şimdilik yalnızca <span class="v" style="font-weight:600">PS5</span> ve <span class="v" style="font-weight:600">Xbox Series X|S</span> için çıktı.</p>
<span class="mono c" style="font-size:20px;letter-spacing:.08em">KAYNAK: PLAYSTATION STORE TÜRKİYE · KASIM 2026</span></div>''', '02 / 05')

S3 = slide(topbar('ASGARİ ÜCRETLE') + f'''
<div style="flex-grow:1;display:flex;flex-direction:column;justify-content:center;gap:30px">
<h2 class="sora" style="margin:0;font-weight:700;font-size:64px;line-height:1.06;letter-spacing:-.03em">Asgari ücretle kaç saat çalışmalısın?</h2>
{''.join(bar_row(*r[:3], MAXH, r[3]) for r in ROWS)}
<div class="card" style="padding:30px 36px;font-size:32px;line-height:1.4">Türkiye'de yaklaşık <span class="v" style="font-weight:600">{tr_num(TR_DAYS)} iş günü</span>, Almanya'da bir iş gününden az.</div>
<span class="mono c" style="font-size:19px;letter-spacing:.06em;line-height:1.6">BRÜT SAATLİK ASGARİ ÜCRET 2026 · STANDART SÜRÜM<br>TR: 33.030 TL / 225 SAAT · ABD: FEDERAL ASGARİ ÜCRET</span></div>''', '03 / 05')

def item(n, title, desc, last=False):
    bb = 'border-bottom:2px solid #1A1F2B;' if last else ''
    return (f'<div style="display:flex;gap:32px;padding:30px 0;border-top:2px solid #1A1F2B;{bb}"><span class="mono v" style="font-size:26px;padding-top:12px">{n}</span>'
            f'<div style="display:flex;flex-direction:column;gap:8px"><span class="sora" style="font-weight:600;font-size:46px;letter-spacing:-.02em">{title}</span>'
            f'<span class="c" style="font-size:32px;line-height:1.4">{desc}</span></div></div>')

S4 = slide(topbar('BİLMEN GEREKENLER') + f'''
<div style="flex-grow:1;display:flex;flex-direction:column;justify-content:center;gap:40px">
<h2 class="sora" style="margin:0;font-weight:700;font-size:80px;line-height:1.05;letter-spacing:-.03em">Almadan önce</h2>
<div style="display:flex;flex-direction:column">
{item('01', 'PC sürümü yok', 'Şimdilik yalnızca PS5 ve Xbox Series X|S. PC için tarih açıklanmadı.')}
{item('02', 'Ultimate şart değil', "Standart'ı alıp ek paketi sonradan da satın alabilirsin.")}
{item('03', 'İlk gün hataları', 'Oyuncular haritadan düşme gibi hatalar paylaşıyor. Güncellemeleri takip et.')}
{item('04', 'Yaş sınırı', "Yetişkinlere yönelik: ABD'de 17+, Almanya'da 18+.", last=True)}
</div></div>''', '04 / 05')

def action(icon, title, sub):
    return (f'<div class="card" style="display:flex;align-items:center;gap:32px;padding:30px 36px;border-radius:28px">'
            f'<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#C6FF3D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{icon}</svg>'
            f'<div style="display:flex;flex-direction:column;gap:4px"><span class="sora" style="font-weight:600;font-size:40px">{title}</span><span class="c" style="font-size:28px">{sub}</span></div></div>')

I_SAVE = '<path d="M6 3h12v18l-6-4-6 4z"/>'
I_SEND = '<path d="M21 3L10 14"/><path d="M21 3l-7 18-4-7-7-4z"/>'
I_FOLLOW = '<circle cx="9" cy="8" r="4"/><path d="M2 21c0-3.9 3.1-7 7-7s7 3.1 7 7"/><path d="M19 8v6"/><path d="M16 11h6"/>'

S5 = slide(f'''
<div style="flex-grow:1;display:flex;flex-direction:column;justify-content:center;gap:44px">
<span class="mono v" style="font-size:24px;letter-spacing:.12em">SIRA SENDE</span>
<h2 class="sora" style="margin:0;font-weight:700;font-size:92px;line-height:1.04;letter-spacing:-.03em">Sence 3.999 TL'ye değer mi?</h2>
<p class="c" style="margin:0;font-size:36px">Yorumlara yaz.</p>
<div style="display:flex;flex-direction:column;gap:20px;margin-top:12px">
{action(I_SAVE, 'Kaydet', 'Fiyat değişirse geri dön')}
{action(I_SEND, 'Paylaş', "GTA'cı arkadaşına gönder")}
{action(I_FOLLOW, 'Takip et', 'Oyun dünyasında bir adım önde ol')}
</div>
<span class="sora c" style="font-weight:600;font-size:34px">Future, first<span class="v">.</span></span></div>''', '05 / 05')

# --- Reels (1080x1920, 18 sn) — zaman çizelgesi data-in / data-out ile -----------
def bar_row_anim(label, hours, detail, accent, t0):
    w = hours / MAXH * 936
    color = '#C6FF3D' if accent else '#8A93A6'
    dur = 2.0 if accent else 1.0
    return (f'<div data-in="{t0}" data-out="12.4" style="display:flex;flex-direction:column;gap:14px;opacity:0">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline"><span class="sora" style="font-weight:600;font-size:52px">{label}</span>'
            f'<span class="sora" style="font-weight:700;font-size:68px;color:{"#C6FF3D" if accent else "#F3F5F8"}"><span data-count="{hours:.4f}" data-cs="{t0 + 0.1}" data-cd="{dur}">0,0</span> saat</span></div>'
            f'<div style="height:34px;border-radius:17px;background:#1A1F2B;overflow:hidden"><div data-bar="{w:.1f}" data-bs="{t0 + 0.1}" data-bd="{dur}" style="width:0;height:100%;border-radius:17px;background:{color}"></div></div>'
            f'<span class="mono c" style="font-size:24px;letter-spacing:.06em">{detail}</span></div>')

REELS = HEAD + f'''<div class="root" id="stage" style="width:1080px;height:1920px">
{WATERMARK.format(b=420)}
<div data-in="0" data-out="15.4" style="position:absolute;left:72px;top:250px;display:flex;align-items:center;gap:18px;opacity:0"><span class="chip">OYUN</span><span class="mono c" style="font-size:24px">GTA 6 · 19 KASIM 2026</span></div>

<div data-in="0.05" data-out="3.6" style="position:absolute;left:72px;top:340px;border-radius:40px;overflow:hidden;opacity:0">{scene_svg(936, 618)}</div>
<div style="position:absolute;left:72px;right:72px;top:1010px;display:flex;flex-direction:column;gap:22px">
<span data-in="0.35" data-out="3.6" class="sora c" style="font-weight:700;font-size:72px;letter-spacing:-.03em;opacity:0">GTA 6 çıktı.</span>
<span data-in="1.0" data-out="3.6" class="sora" style="font-weight:700;font-size:84px;line-height:1.04;letter-spacing:-.035em;opacity:0">Peki onu almak için <span class="v">kaç saat</span> çalışman gerekiyor?</span></div>

<div style="position:absolute;left:72px;right:72px;top:360px;display:flex;flex-direction:column;gap:40px">
<div data-in="3.7" data-out="12.4" style="display:flex;flex-direction:column;gap:18px;opacity:0"><span class="mono v" style="font-size:26px">ASGARİ ÜCRETLE HESAPLADIK</span>
<span class="sora" style="font-weight:700;font-size:76px;line-height:1.05;letter-spacing:-.03em">Bir oyun kaç saatlik emek?</span></div>
{bar_row_anim('Almanya', H['de'], '13,90 € / SAAT · OYUN 79,99 €', False, 4.0)}
{bar_row_anim('ABD', H['us'], '7,25 $ / SAAT · OYUN 79,99 $', False, 5.7)}
{bar_row_anim('Türkiye', H['tr'], f'{tr_num(tr_hourly, 2)} TL / SAAT · OYUN 3.999 TL', True, 7.4)}
<div data-in="10.0" data-out="12.4" class="sora" style="font-weight:700;font-size:58px;line-height:1.1;letter-spacing:-.03em;opacity:0">Türkiye'de yaklaşık <span class="v">{tr_num(TR_DAYS)} iş günü.</span></div>
</div>

<div data-in="12.5" data-out="15.4" style="position:absolute;left:72px;top:340px;border-radius:40px;overflow:hidden;opacity:0">{scene_svg(936, 618)}</div>
<div style="position:absolute;left:72px;right:72px;top:1010px;display:flex;flex-direction:column;gap:26px">
<span data-in="12.8" data-out="15.4" class="sora" style="font-weight:700;font-size:100px;line-height:1.02;letter-spacing:-.035em;opacity:0">Sen olsan <span class="v">alır mıydın?</span></span>
<span data-in="13.4" data-out="15.4" class="c" style="font-size:40px;line-height:1.4;opacity:0">Yorumlara yaz, GTA'cı arkadaşına gönder.</span></div>

<div data-in="0" data-out="15.4" style="position:absolute;left:72px;top:1460px;display:flex;align-items:center;gap:14px;opacity:0">{mono(44)}<span style="font-size:30px;font-weight:600">@bentaka</span></div>

<div data-in="15.6" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px;opacity:0;padding-bottom:180px">
<div style="display:flex;align-items:center;gap:30px">{mono(150)}<span class="sora" style="font-weight:700;font-size:150px;letter-spacing:-.045em;padding-bottom:12px">bentaka</span></div>
<span class="sora c" style="font-weight:600;font-size:52px">Future, first<span class="v">.</span></span>
<span class="mono c" style="font-size:20px;letter-spacing:.06em;text-align:center;line-height:1.7;margin-top:40px">KAYNAK: PLAYSTATION STORE TR / DE · 2026 BRÜT ASGARİ ÜCRETLER<br>TR 33.030 TL / 225 SAAT · DE 13,90 € · ABD FEDERAL 7,25 $</span></div>
</div>
<script>
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const prog=(t,s,d)=>clamp((t-s)/d,0,1);
const ease=p=>1-Math.pow(1-p,3);
const fmt=x=>x.toFixed(1).replace('.',',');
window.render=function(t){{
  document.querySelectorAll('[data-in]').forEach(el=>{{
    const a=ease(prog(t,+el.dataset.in,0.45));
    const o=el.dataset.out?1-ease(prog(t,+el.dataset.out,0.35)):1;
    el.style.opacity=Math.min(a,o);
    el.style.transform='translateY('+((1-a)*40).toFixed(1)+'px)';
  }});
  document.querySelectorAll('[data-bar]').forEach(el=>{{
    el.style.width=(ease(prog(t,+el.dataset.bs,+el.dataset.bd))*+el.dataset.bar).toFixed(1)+'px';
  }});
  document.querySelectorAll('[data-count]').forEach(el=>{{
    el.textContent=fmt(ease(prog(t,+el.dataset.cs,+el.dataset.cd))*+el.dataset.count);
  }});
}};
window.render(0);
</script></body></html>'''

if __name__ == '__main__':
    for i, s in enumerate([S1, S2, S3, S4, S5], 1):
        open(os.path.join(HERE, f'slide-{i}.html'), 'w').write(s)
    open(os.path.join(HERE, 'reels.html'), 'w').write(REELS)
    print({k: round(v, 2) for k, v in H.items()}, 'TR saatlik', round(tr_hourly, 2), 'gün', round(TR_DAYS, 2))
