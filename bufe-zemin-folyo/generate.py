#!/usr/bin/env python3
"""Büfe zemin folyosu – 100 x 400 cm (1 cm taşma payı ile 102 x 402 cm).
Koordinat birimi: milimetre. Görselin ALT kenarı = kapı tarafı (giren kişi yukarı doğru okur)."""
import random

BLEED = 10            # mm, her kenar
TW, TH = 1000, 4000   # net (kesim) ölçü
W, H = TW + 2 * BLEED, TH + 2 * BLEED
CX = W / 2

GOLD = "url(#gold)"
random.seed(7)


def bottle(kind, x, y, s=1.0):
    """x,y = şişe tabanının ortası."""
    shapes = {
        "wine": ("M-70 0 L-70 -300 C-70 -370 -25 -390 -25 -450 L-25 -585 L-29 -600 L29 -600 L25 -585 "
                 "L25 -450 C25 -390 70 -370 70 -300 L70 0 Z", (-60, -260, 120, 150), (-27, -600, 54, 70)),
        "whisky": ("M-95 0 L-95 -360 Q-95 -400 -55 -410 L-32 -420 L-32 -500 L32 -500 L32 -420 L55 -410 "
                   "Q95 -400 95 -360 L95 0 Z", (-80, -300, 160, 170), (-36, -540, 72, 50)),
        "beer": ("M-58 0 L-58 -250 C-58 -310 -22 -330 -22 -400 L-22 -505 L22 -505 L22 -400 "
                 "C22 -330 58 -310 58 -250 L58 0 Z", (-50, -220, 100, 110), (-26, -520, 52, 22)),
        "raki": ("M-55 0 L-55 -420 C-55 -470 -20 -480 -20 -540 L-20 -640 L20 -640 L20 -540 "
                 "C20 -480 55 -470 55 -420 L55 0 Z", (-46, -380, 92, 200), (-23, -680, 46, 45)),
        "champ": ("M-72 0 L-72 -290 C-72 -400 -24 -420 -24 -500 L-24 -600 L24 -600 L24 -500 "
                  "C24 -420 72 -400 72 -290 L72 0 Z", (-62, -250, 124, 130), (-30, -640, 60, 120)),
    }
    path, label, cap = shapes[kind]
    lx, ly, lw, lh = label
    cx_, cy_, cw, ch = cap
    return f'''
  <g transform="translate({x} {y}) scale({s})">
    <ellipse cx="0" cy="4" rx="{abs(lx)*1.6}" ry="16" fill="#000" opacity=".55"/>
    <path d="{path}" fill="url(#glass)" stroke="url(#gold)" stroke-width="5"/>
    <path d="{path}" fill="url(#shine)"/>
    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="6" fill="#120c08" stroke="url(#gold)" stroke-width="4"/>
    <rect x="{lx+10}" y="{ly+lh*0.32}" width="{lw-20}" height="4" fill="url(#gold)"/>
    <rect x="{lx+10}" y="{ly+lh*0.62}" width="{lw-20}" height="4" fill="url(#gold)"/>
    <circle cx="0" cy="{ly+lh*0.47}" r="{min(lw,lh)*0.09}" fill="url(#gold)"/>
    <rect x="{cx_}" y="{cy_}" width="{cw}" height="{ch}" rx="4" fill="url(#gold)"/>
  </g>'''


def ice(x, y, s, r):
    return f'''
  <g transform="translate({x} {y}) rotate({r}) scale({s})">
    <rect x="-50" y="-50" width="100" height="100" rx="18" fill="url(#ice)" stroke="#d9f3ff" stroke-width="3" opacity=".95"/>
    <path d="M-34 -30 Q-10 -40 22 -32" stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none" opacity=".8"/>
    <path d="M-30 -14 L-30 20" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".45"/>
  </g>'''


def bubbles(x0, y0, x1, y1, n, rmin, rmax, op=0.35):
    out = []
    for _ in range(n):
        x = random.uniform(x0, x1); y = random.uniform(y0, y1); r = random.uniform(rmin, rmax)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="#f3d88a" '
                   f'stroke-width="{max(1.5, r/6):.1f}" opacity="{random.uniform(op*0.4, op):.2f}"/>')
    return "\n  ".join(out)


def chevrons(cy, n=3):
    out = []
    for i in range(n):
        y = cy - i * 70
        op = 1 - i * 0.28
        out.append(f'<path d="M{CX-110} {y+45} L{CX} {y-25} L{CX+110} {y+45}" fill="none" stroke="url(#gold)" '
                   f'stroke-width="22" stroke-linecap="round" stroke-linejoin="round" opacity="{op:.2f}"/>')
    return "\n  ".join(out)


def deco_divider(y, w=700):
    x0, x1 = CX - w / 2, CX + w / 2
    return f'''
  <g>
    <line x1="{x0}" y1="{y}" x2="{CX-70}" y2="{y}" stroke="url(#gold)" stroke-width="5"/>
    <line x1="{CX+70}" y1="{y}" x2="{x1}" y2="{y}" stroke="url(#gold)" stroke-width="5"/>
    <line x1="{x0+60}" y1="{y+16}" x2="{CX-90}" y2="{y+16}" stroke="url(#gold)" stroke-width="2"/>
    <line x1="{CX+90}" y1="{y+16}" x2="{x1-60}" y2="{y+16}" stroke="url(#gold)" stroke-width="2"/>
    <path d="M{CX} {y-40} L{CX+40} {y} L{CX} {y+40} L{CX-40} {y} Z" fill="url(#gold)"/>
    <path d="M{CX} {y-22} L{CX+22} {y} L{CX} {y+22} L{CX-22} {y} Z" fill="#0b0a12"/>
    <circle cx="{x0}" cy="{y}" r="9" fill="url(#gold)"/><circle cx="{x1}" cy="{y}" r="9" fill="url(#gold)"/>
  </g>'''


def corner(x, y, sx, sy):
    return f'''<g transform="translate({x} {y}) scale({sx} {sy})">
    <path d="M0 140 L0 0 L140 0" fill="none" stroke="url(#gold)" stroke-width="8"/>
    <path d="M22 110 L22 22 L110 22" fill="none" stroke="url(#gold)" stroke-width="3"/>
    <path d="M0 0 L46 46" stroke="url(#gold)" stroke-width="3"/>
    <circle cx="46" cy="46" r="10" fill="url(#gold)"/>
  </g>'''


def wine_glass(x, y, s=1):
    return f'''
  <g transform="translate({x} {y}) scale({s})">
    <ellipse cx="0" cy="0" rx="80" ry="14" fill="none" stroke="url(#gold)" stroke-width="6"/>
    <line x1="0" y1="0" x2="0" y2="-190" stroke="url(#gold)" stroke-width="9"/>
    <path d="M-95 -420 C-100 -300 -60 -200 0 -190 C60 -200 100 -300 95 -420 Z" fill="none" stroke="url(#gold)" stroke-width="6"/>
    <path d="M-92 -330 C-85 -255 -50 -205 0 -200 C50 -205 85 -255 92 -330 Z" fill="url(#wine)"/>
    <ellipse cx="0" cy="-330" rx="92" ry="12" fill="#c0304a" opacity=".85"/>
    <path d="M-70 -400 C-75 -340 -60 -290 -40 -260" stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none" opacity=".5"/>
  </g>'''


def beer_mug(x, y, s=1):
    return f'''
  <g transform="translate({x} {y}) scale({s})">
    <path d="M90 -330 Q190 -330 190 -220 Q190 -110 90 -110" fill="none" stroke="url(#gold)" stroke-width="22"/>
    <path d="M-110 -400 L-100 0 L100 0 L110 -400 Z" fill="url(#beer)" stroke="url(#gold)" stroke-width="7"/>
    <path d="M-120 -400 Q-130 -470 -70 -470 Q-50 -520 0 -500 Q50 -530 80 -480 Q135 -480 122 -400 Z" fill="#fff8e6"/>
    <circle cx="-60" cy="-440" r="14" fill="#fff"/><circle cx="30" cy="-470" r="18" fill="#fff"/><circle cx="80" cy="-430" r="12" fill="#fff"/>
    <line x1="-55" y1="-370" x2="-50" y2="-40" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".4"/>
    <line x1="45" y1="-370" x2="42" y2="-40" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".25"/>
    {"".join(f'<circle cx="{random.uniform(-80,80):.0f}" cy="{random.uniform(-380,-30):.0f}" r="{random.uniform(4,10):.0f}" fill="#fff" opacity=".55"/>' for _ in range(16))}
  </g>'''


def tumbler(x, y, s=1):
    return f'''
  <g transform="translate({x} {y}) scale({s})">
    <path d="M-100 -280 L-90 0 L90 0 L100 -280 Z" fill="none" stroke="url(#gold)" stroke-width="7"/>
    <path d="M-95 -150 L-90 -8 L90 -8 L95 -150 Z" fill="url(#whisky)"/>
    {ice(-35, -170, .7, 12)}
    {ice(40, -150, .6, -18)}
    <rect x="-90" y="-12" width="180" height="16" fill="url(#gold)" opacity=".6"/>
  </g>'''


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0a0d18"/>
    <stop offset=".35" stop-color="#160c1a"/>
    <stop offset=".65" stop-color="#1b0d12"/>
    <stop offset="1" stop-color="#090a12"/>
  </linearGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f6e09a"/>
    <stop offset=".45" stop-color="#d4a64a"/>
    <stop offset=".7" stop-color="#9c6f22"/>
    <stop offset="1" stop-color="#f0cf7a"/>
  </linearGradient>
  <linearGradient id="goldText" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fbeab0"/>
    <stop offset=".5" stop-color="#dcae52"/>
    <stop offset="1" stop-color="#a87726"/>
  </linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1d2a1a"/><stop offset=".5" stop-color="#2f4128"/><stop offset="1" stop-color="#121a10"/>
  </linearGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".22" stop-color="#fff" stop-opacity=".28"/>
    <stop offset=".3" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="ice" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#e8f8ff"/><stop offset="1" stop-color="#6fb8dc"/>
  </linearGradient>
  <linearGradient id="wine" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#a3203a"/><stop offset="1" stop-color="#4a0815"/>
  </linearGradient>
  <linearGradient id="beer" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffc94a"/><stop offset="1" stop-color="#d07a12"/>
  </linearGradient>
  <linearGradient id="whisky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e3922e"/><stop offset="1" stop-color="#7a3a0a"/>
  </linearGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#e09a3a" stop-opacity=".55"/>
    <stop offset=".6" stop-color="#a0401a" stop-opacity=".15"/>
    <stop offset="1" stop-color="#000" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glowBlue" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#5fb6e6" stop-opacity=".45"/>
    <stop offset="1" stop-color="#000" stop-opacity="0"/>
  </radialGradient>
  <pattern id="deco" width="80" height="80" patternUnits="userSpaceOnUse">
    <path d="M0 80 L40 0 L80 80" fill="none" stroke="#d4a64a" stroke-width="1.2" opacity=".09"/>
  </pattern>
</defs>

<!-- ZEMİN (taşma payı dahil) -->
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#deco)"/>

<!-- ÇERÇEVE -->
<rect x="{BLEED+40}" y="{BLEED+40}" width="{TW-80}" height="{TH-80}" fill="none" stroke="url(#gold)" stroke-width="10"/>
<rect x="{BLEED+62}" y="{BLEED+62}" width="{TW-124}" height="{TH-124}" fill="none" stroke="url(#gold)" stroke-width="3"/>
{corner(BLEED+40, BLEED+40, 1, 1)}
{corner(W-BLEED-40, BLEED+40, -1, 1)}
{corner(BLEED+40, H-BLEED-40, 1, -1)}
{corner(W-BLEED-40, H-BLEED-40, -1, -1)}

<!-- ===== 1) ÜST BÖLÜM (iç taraf): yasal uyarı ===== -->
<g font-family="Oswald" text-anchor="middle">
  <rect x="{CX-380}" y="150" width="760" height="250" rx="20" fill="#0b0a12" stroke="url(#gold)" stroke-width="6"/>
  <circle cx="{CX}" cy="150" r="62" fill="#b3172f" stroke="url(#gold)" stroke-width="7"/>
  <text x="{CX}" y="172" font-size="62" font-weight="700" fill="#fff">18+</text>
  <text x="{CX}" y="275" font-size="58" font-weight="700" fill="#f6e3a8" letter-spacing="2">18 YAŞINDAN KÜÇÜKLERE</text>
  <text x="{CX}" y="345" font-size="58" font-weight="700" fill="#f6e3a8" letter-spacing="2">ALKOLLÜ İÇKİ SATILMAZ</text>
  <text x="{CX}" y="460" font-size="40" font-weight="500" fill="#d4a64a" letter-spacing="14">ÖLÇÜLÜ TÜKETİNİZ</text>
</g>

<!-- ===== 2) BUZ GİBİ ===== -->
<ellipse cx="{CX}" cy="930" rx="520" ry="420" fill="url(#glowBlue)"/>
{bubbles(110, 560, 910, 1350, 40, 6, 22, .45)}
{beer_mug(CX-170, 1180, .95)}
{tumbler(CX+215, 1180, 1.05)}
{ice(CX+40, 1240, .9, 20)}
{ice(CX-360, 1250, .7, -15)}
{ice(CX+380, 1255, .65, 30)}
<g font-family="Oswald" text-anchor="middle">
  <text x="{CX}" y="1450" font-size="150" font-weight="700" fill="#e9f7ff" letter-spacing="10">BUZ GİBİ</text>
  <text x="{CX}" y="1540" font-size="58" font-weight="500" fill="#8fd0f0" letter-spacing="12">HER ZAMAN SOĞUK</text>
</g>
{deco_divider(1660)}

<!-- ===== 3) ANA BÖLÜM: SEÇKİN İÇKİLER ===== -->
<ellipse cx="{CX}" cy="2180" rx="560" ry="520" fill="url(#glow)"/>
{bubbles(110, 1720, 910, 2500, 45, 5, 18, .4)}
{bottle("whisky", CX-300, 2450, .82)}
{bottle("raki", CX-150, 2450, .88)}
{bottle("champ", CX, 2450, .92)}
{bottle("wine", CX+150, 2450, .88)}
{bottle("beer", CX+295, 2450, .86)}
<rect x="{CX-400}" y="2455" width="800" height="14" rx="7" fill="url(#gold)"/>
<g text-anchor="middle">
  <text x="{CX}" y="2690" font-family="Playfair Display" font-style="italic" font-weight="700" font-size="190" fill="url(#goldText)">Seçkin</text>
  <text x="{CX}" y="2900" font-family="Oswald" font-weight="700" font-size="215" fill="url(#goldText)" letter-spacing="14">İÇKİLER</text>
  <text x="{CX}" y="3010" font-family="Oswald" font-weight="500" font-size="46" fill="#f3e2b4" letter-spacing="3">BİRA · ŞARAP · RAKI · VİSKİ · VOTKA</text>
</g>
{deco_divider(3110)}

<!-- ===== 4) TEKEL / BÜFE ===== -->
<g font-family="Oswald" text-anchor="middle">
  <text x="{CX}" y="3300" font-size="120" font-weight="700" fill="#fff" letter-spacing="30">TEKEL</text>
  <text x="{CX}" y="3390" font-size="42" font-weight="500" fill="#d4a64a" letter-spacing="6">SOĞUK İÇECEK · ATIŞTIRMALIK</text>
</g>

<!-- ===== 5) ALT BÖLÜM (kapı tarafı): HOŞ GELDİNİZ + yön okları ===== -->
{chevrons(3600)}
<g text-anchor="middle">
  <text x="{CX}" y="3830" font-family="Playfair Display" font-style="italic" font-weight="700" font-size="125" fill="url(#goldText)">Hoş Geldiniz</text>
</g>
</svg>'''

html = f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Playfair+Display:ital,wght@1,700&display=block" rel="stylesheet">
<style>@page {{ size: {W}mm {H}mm; margin: 0 }} html,body {{ margin:0; padding:0; background:#000 }}
svg {{ display:block; width:{W}mm; height:{H}mm }}</style></head><body>{svg}</body></html>'''

import pathlib
out = pathlib.Path(__file__).parent
(out / "zemin_folyo.svg").write_text(svg, encoding="utf-8")
(out / "zemin_folyo.html").write_text(html, encoding="utf-8")
print("ok", W, H)
