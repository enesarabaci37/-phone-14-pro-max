#!/usr/bin/env python3
"""Bentaka marka kılavuzu (HTML → PDF, Playwright ile yazdırılır)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from build import COLORS, PALETTE_KEYS, SLOGAN, SLOGAN_TR, SP, FONTDIR, rgb

S = json.load(open(f'{SP}/build/guide_svgs.json'))

def logo(key, width, style=''):
    return S[key].replace('class="logo"', f'class="logo" style="width:{width}px;height:auto;{style}"', 1)

swatches = ''
for k in PALETTE_KEYS:
    c = COLORS[k]
    r, g, b = rgb(k)
    tc = '#0B0E14' if k in ('bulut', 'volt', 'iyon', 'celik') else '#F3F5F8'
    border = 'border:1px solid #C9CED8;' if k == 'bulut' else ''
    swatches += f'''<div class="sw"><div class="chip" style="background:{c['hex']};color:{tc};{border}">{c['name']}</div>
<div class="codes"><span>HEX</span>{c['hex']}<br><span>RGB</span>{r} {g} {b}<br><span>CMYK</span>{' '.join(str(v) for v in c['cmyk'])}</div>
<div class="role">{c['role']}</div></div>'''

wrong_color = S['yatay_acik'].replace('#0B0E14', '#E5484D').replace('#5B7CFF', '#F5A524')
wrong_color = wrong_color.replace('class="logo"', 'class="logo" style="width:220px;height:auto"', 1)
xmark = '<svg class="x" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="#E5484D"/><path d="M8 8l8 8M16 8l-8 8" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></svg>'

files = [
    ('Instagram', 'instagram-profil-1080x1080.png · öne çıkan kapaklar 1080×1920 (Haber, İnceleme, İpucu, Kıyas)'),
    ('Facebook', 'facebook-profil-1080x1080.png · facebook-kapak-1640x624.png'),
    ('X (Twitter)', 'x-profil-400x400.png · x-kapak-1500x500.png'),
    ('YouTube', 'youtube-profil-800x800.png · youtube-banner-2560x1440.png · youtube-filigran-150x150.png'),
    ('LinkedIn', 'linkedin-logo-400x400.png · linkedin-kapak-1128x191.png'),
    ('TikTok · Threads', 'tiktok-profil-1080x1080.png (Threads, Instagram profilini kullanır)'),
    ('WhatsApp · Telegram', 'whatsapp-telegram-profil-640x640.png'),
    ('E-posta', 'eposta-profil-512x512.png · eposta-imza-logo-600x160.png (açık / koyu)'),
    ('Web sitesi', 'favicon.ico · favicon.svg · apple-touch-icon · icon-192 / 512 · og-paylasim-gorseli-1200x630.png'),
    ('Matbaa', '01 Logo › Baskı: CMYK PDF ve EPS (kartvizit, afiş, tabela, tişört)'),
    ('Tasarım programı', 'SVG logolar · bentaka-renkler.ase (Adobe renk örnekleri) · Bentaka-Fontlar.zip'),
]
rows = ''.join(f'<tr><th>{a}</th><td>{b}</td></tr>' for a, b in files)

html = f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>Bentaka Marka Kılavuzu</title>
<style>
@font-face{{font-family:Sora;font-weight:600;src:url(file://{FONTDIR}/Sora-SemiBold.ttf)}}
@font-face{{font-family:Sora;font-weight:700;src:url(file://{FONTDIR}/Sora-Bold.ttf)}}
@font-face{{font-family:Inter;font-weight:400;src:url(file:///usr/share/fonts/opentype/inter/Inter-Regular.otf)}}
@font-face{{font-family:Inter;font-weight:600;src:url(file:///usr/share/fonts/opentype/inter/Inter-SemiBold.otf)}}
@font-face{{font-family:Mono;font-weight:500;src:url(file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf)}}
@page{{size:297mm 210mm;margin:0}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:Inter,sans-serif;color:#0B0E14;background:#fff}}
.page{{width:297mm;height:210mm;padding:16mm 18mm;position:relative;overflow:hidden;page-break-after:always;display:flex;flex-direction:column;gap:9mm}}
.page:last-child{{page-break-after:auto}}
.dark{{background:#0B0E14;color:#F3F5F8}}
.light{{background:#F3F5F8}}
.kicker{{font-family:Mono;font-size:10pt;letter-spacing:.12em;color:#1A1F2B}}
.dark .kicker{{color:#8A93A6}}
h1{{margin:0;font-family:Sora;font-weight:600;font-size:30pt;letter-spacing:-.02em;line-height:1}}
h2{{margin:0;font-family:Sora;font-weight:600;font-size:14pt}}
p,li{{font-size:10.5pt;line-height:1.55;margin:0}}
.muted{{color:#1A1F2B}}
.dark .muted{{color:#8A93A6}}
.grid{{display:grid;gap:6mm}}
.panel{{border-radius:5mm;display:flex;align-items:center;justify-content:center;padding:8mm}}
.cap{{font-size:9.5pt;line-height:1.45;color:#1A1F2B;margin-top:2.5mm}}
.vdot{{color:#C6FF3D}}
.sw{{background:#fff;border-radius:4mm;overflow:hidden;display:flex;flex-direction:column}}
.chip{{height:30mm;padding:4mm;display:flex;align-items:flex-end;font-family:Sora;font-weight:600;font-size:15pt;border-radius:4mm 4mm 0 0}}
.codes{{font-family:Mono;font-size:8.3pt;line-height:1.75;padding:3.5mm 3mm 1mm;white-space:nowrap}}
.codes span{{display:inline-block;width:10mm;color:#1A1F2B}}
.role{{font-size:9pt;color:#1A1F2B;padding:0 3mm 4mm;line-height:1.4}}
.bad{{background:#fff;border-radius:4mm;padding:5mm;display:flex;flex-direction:column;align-items:center;gap:4mm;position:relative}}
.bad .stage{{height:26mm;display:flex;align-items:center;justify-content:center}}
.x{{width:7mm;height:7mm;position:absolute;top:3mm;right:3mm}}
.bad p{{font-size:9.5pt;font-weight:600}}
table{{border-collapse:collapse;width:100%}}
th,td{{text-align:left;font-size:10pt;padding:2.6mm 3mm;border-bottom:1px solid #DDE1E8;vertical-align:top}}
th{{width:42mm;font-family:Sora;font-weight:600}}
td{{font-family:Mono;font-size:8.8pt;line-height:1.5;color:#1A1F2B}}
.ratio{{display:flex;height:9mm;border-radius:2.5mm;overflow:hidden;border:1px solid #8A93A6}}
</style></head><body>

<section class="page dark" style="justify-content:space-between">
  <div class="kicker">MARKA KILAVUZU · SÜRÜM 1.0 · 2026</div>
  <div style="display:flex;flex-direction:column;align-items:center;gap:9mm">
    {logo('yatay_koyu', 560)}
    <div style="font-family:Sora;font-weight:600;font-size:26pt;color:#8A93A6;letter-spacing:-.01em">Future, first<span class="vdot">.</span></div>
  </div>
  <p class="muted" style="max-width:150mm">Bu kılavuz Bentaka logosunun, renklerinin ve yazı tiplerinin her yerde aynı ve doğru kullanılması için hazırlanmıştır.</p>
</section>

<section class="page light">
  <div><div class="kicker">01 · LOGO</div><h1 style="margin-top:3mm">Logo ve türleri</h1></div>
  <div class="grid" style="grid-template-columns:1fr 1fr;flex:1">
    <div><div class="panel" style="background:#fff;height:44mm">{logo('yatay_acik', 330)}</div>
      <div class="cap"><b>Yatay logo (varsayılan).</b> Web sitesi, kapak görselleri, e-posta imzası, sunumlar. Açık zeminde nokta İyon mavisi.</div></div>
    <div><div class="panel" style="background:#0B0E14;height:44mm">{logo('yatay_koyu', 330)}</div>
      <div class="cap"><b>Koyu zemin.</b> Markanın asıl görünümü. Koyu zeminde nokta her zaman Volt yeşili.</div></div>
    <div class="grid" style="grid-template-columns:1fr 1fr 1fr;gap:6mm">
      <div><div class="panel" style="background:#fff;height:46mm">{logo('dikey_acik', 120)}</div><div class="cap"><b>Dikey logo.</b> Kare alanlar, afiş, tişört.</div></div>
      <div><div class="panel" style="background:#0B0E14;height:46mm">{logo('dikey_koyu', 120)}</div><div class="cap">Dikey logo, koyu zemin.</div></div>
      <div><div class="panel" style="background:#fff;height:46mm"><div style="width:34mm;height:34mm;border-radius:50%;background:#0B0E14;display:flex;align-items:center;justify-content:center">{logo('mono_koyu', 62)}</div></div><div class="cap"><b>Monogram.</b> Profil fotoğrafı, favicon, uygulama ikonu, filigran.</div></div>
    </div>
    <div style="display:flex;flex-direction:column;gap:3mm;justify-content:center;padding-left:4mm">
      <h2>Monogramın anlamı</h2>
      <p class="muted">Küçük harf <b>b</b> ve içindeki nokta: bit, çekirdek, odak. Nokta markanın imzasıdır; slogan sonundaki Volt nokta da aynı fikri taşır.</p>
      <p class="muted">Tek renk gereken yerlerde (damga, gravür, faks, tek renk baskı) siyah veya beyaz sürüm kullanılır.</p>
    </div>
  </div>
</section>

<section class="page light">
  <div><div class="kicker">02 · KULLANIM</div><h1 style="margin-top:3mm">Kurallar</h1></div>
  <div class="grid" style="grid-template-columns:1.1fr 1fr;flex:1">
    <div style="display:flex;flex-direction:column;gap:6mm">
      <div class="panel" style="background:#fff;height:58mm;flex-direction:column;gap:3mm">
        <div style="border:1.5px dashed #5B7CFF;padding:9mm 11mm;border-radius:2mm">{logo('yatay_acik', 270)}</div>
        <div class="kicker" style="color:#1A1F2B">BOŞLUK = MONOGRAM GENİŞLİĞİNİN YARISI</div>
      </div>
      <div>
        <h2>Güvenli alan ve en küçük boyut</h2>
        <ul style="padding-left:5mm;margin:2mm 0 0;display:flex;flex-direction:column;gap:1.5mm">
          <li>Logonun çevresinde en az monogram genişliğinin yarısı kadar boşluk bırakın.</li>
          <li>Yatay logo en az <b>120 px</b> (ekran) / <b>30 mm</b> (baskı) genişlikte kullanılır.</li>
          <li>Monogram en az <b>24 px</b> / <b>8 mm</b>. Favicon (16 px) tek istisnadır.</li>
          <li>Volt yeşili açık zeminde yazı veya logo noktası olarak kullanılmaz.</li>
        </ul>
      </div>
    </div>
    <div class="grid" style="grid-template-columns:1fr 1fr;align-content:start">
      <div class="bad">{xmark}<div class="stage">{logo('yatay_acik', 150, 'transform:scaleX(1.45)')}</div><p>Esnetmeyin</p></div>
      <div class="bad">{xmark}<div class="stage">{logo('yatay_acik', 190, 'transform:rotate(-14deg)')}</div><p>Döndürmeyin</p></div>
      <div class="bad">{xmark}<div class="stage">{wrong_color}</div><p>Renkleri değiştirmeyin</p></div>
      <div class="bad">{xmark}<div class="stage">{logo('yatay_acik', 220, 'filter:drop-shadow(5px 6px 4px rgba(0,0,0,.5))')}</div><p>Gölge veya efekt eklemeyin</p></div>
      <div class="bad">{xmark}<div class="stage" style="background:#8A93A6;padding:0 5mm;border-radius:2mm">{logo('yatay_acik', 200)}</div><p>Düşük kontrastlı zemine koymayın</p></div>
      <div class="bad">{xmark}<div class="stage" style="font-family:Inter;font-weight:700;font-size:22pt;letter-spacing:.02em">BENTAKA</div><p>Logoyu başka fontla yazmayın</p></div>
    </div>
  </div>
</section>

<section class="page light">
  <div><div class="kicker">03 · RENKLER</div><h1 style="margin-top:3mm">Renk paleti</h1></div>
  <div class="grid" style="grid-template-columns:repeat(6,1fr);gap:4mm">{swatches}</div>
  <div style="display:flex;flex-direction:column;gap:3mm">
    <h2>Kullanım oranı</h2>
    <div class="ratio"><div style="width:60%;background:#0B0E14"></div><div style="width:20%;background:#F3F5F8"></div><div style="width:10%;background:#1A1F2B"></div><div style="width:7%;background:#C6FF3D"></div><div style="width:3%;background:#5B7CFF"></div></div>
    <p class="muted" style="font-family:Mono;font-size:9pt">GECE %60 · BULUT %20 · GRAFİT %10 · VOLT %7 · İYON %3</p>
    <p class="muted">CMYK değerleri kuşe kâğıt baskı için önerilir; baskıdan önce matbaadan renk provası isteyin. Volt ve İyon ekranda baskıdan daha canlı görünür. Tek renk baskıda Siyah = C0 M0 Y0 K100.</p>
  </div>
</section>

<section class="page dark">
  <div><div class="kicker">04 · YAZI VE SES</div><h1 style="margin-top:3mm">Tipografi ve slogan</h1></div>
  <div class="grid" style="grid-template-columns:repeat(3,1fr)">
    <div style="background:#1A1F2B;border-radius:4mm;padding:6mm;display:flex;flex-direction:column;gap:3mm">
      <div class="kicker" style="color:#C6FF3D">BAŞLIK · LOGO</div>
      <div style="font-family:Sora;font-weight:700;font-size:26pt;letter-spacing:-.02em">Sora</div>
      <p class="muted">600 ve 700 kalınlık. Logo, başlıklar ve gönderi manşetleri.</p>
      <p style="font-family:Sora;font-size:12pt;color:#8A93A6">ĞÜŞİÖÇ ğüşıöç 0123456789</p>
    </div>
    <div style="background:#1A1F2B;border-radius:4mm;padding:6mm;display:flex;flex-direction:column;gap:3mm">
      <div class="kicker" style="color:#C6FF3D">METİN</div>
      <div style="font-family:Inter;font-weight:600;font-size:26pt">Inter</div>
      <p class="muted">400 ve 600 kalınlık. Açıklamalar, uzun metinler, web sitesi.</p>
      <p style="font-family:Inter;font-size:12pt;color:#8A93A6">ĞÜŞİÖÇ ğüşıöç 0123456789</p>
    </div>
    <div style="background:#1A1F2B;border-radius:4mm;padding:6mm;display:flex;flex-direction:column;gap:3mm">
      <div class="kicker" style="color:#C6FF3D">ETİKET · VERİ</div>
      <div style="font-family:Mono;font-size:22pt">JetBrains Mono</div>
      <p class="muted">500 kalınlık, büyük harf. Etiketler, teknik özellikler, rakamlar.</p>
      <p style="font-family:Mono;font-size:11pt;color:#8A93A6">ĞÜŞİÖÇ ğüşıöç 0123456789</p>
    </div>
  </div>
  <div class="grid" style="grid-template-columns:1.2fr 1fr;flex:1;align-items:center">
    <div>
      <div class="kicker">SLOGAN</div>
      <div style="font-family:Sora;font-weight:700;font-size:44pt;letter-spacing:-.03em;margin-top:3mm">Future, first<span class="vdot">.</span></div>
      <div class="kicker" style="margin-top:4mm;color:#C6FF3D">YALNIZCA İNGİLİZCE · ÇEVİRİSİ YANINA YAZILMAZ</div>
    </div>
    <ul style="padding-left:5mm;margin:0;display:flex;flex-direction:column;gap:2mm" class="muted">
      <li><b style="color:#F3F5F8">Slogan her yerde İngilizce ve tek başına kullanılır.</b> Türkçe karşılığı logonun yanına, altına veya sloganın yanına yazılmaz.</li>
      <li>Türkçe karşılığı ("{SLOGAN_TR}") gerekirse yalnızca Türkçe gönderi açıklamalarında ve reklam metinlerinde kullanılabilir.</li>
      <li>Slogan logonun altında, logo yüksekliğinin yaklaşık %30'u boyutunda ve Çelik renginde yazılır; sondaki nokta Volt.</li>
      <li>Marka sesi: net, sade, meraklı, abartısız.</li>
    </ul>
  </div>
</section>

<section class="page light">
  <div><div class="kicker">05 · DOSYALAR</div><h1 style="margin-top:3mm">Hangi dosya nerede?</h1></div>
  <table>{rows}</table>
  <p class="muted" style="font-size:9pt">Platform ölçüleri zaman zaman değişir; yüklemeden önce platformun yardım sayfasından güncel ölçüyü kontrol edin. Profil fotoğrafları daireye kırpılmaya uygun tasarlanmıştır.</p>
</section>

</body></html>'''

open(f'{SP}/build/guide.html', 'w').write(html)
print('ok')
