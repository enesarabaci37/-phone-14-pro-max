"""Arabacı Reklam - Oto cam filmi Instagram kaydırmalı gönderi (10 görsel, 1080x1350).

Kullanım: python3 carousel.py <cikti_klasoru>
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1350
M = 80
CW = W - 2 * M
N = 10
PHONE = "0534 080 26 79"

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(HERE, "..", "logo-arabaci-reklam.png")
FONT_DIR = "/usr/share/fonts/opentype/inter/"

# Logodan alınan marka renkleri
RED = (202, 76, 75)
GREEN = (164, 181, 66)
TEAL = (101, 173, 164)
GRAY = (69, 75, 82)
DARK = (38, 42, 47)
LIGHT = (246, 247, 244)
WHITE = (255, 255, 255)


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name + ".otf", size)


# ---------------------------------------------------------------- logo

def load_logo():
    logo = Image.open(LOGO_PATH).convert("RGBA")
    arr = np.array(logo)
    # Gri yazıyı beyaza çeviren koyu zemin versiyonu
    rgb = arr[..., :3].astype(int)
    is_gray = (np.abs(rgb - np.array(GRAY)).sum(axis=2) < 60)
    white = arr.copy()
    white[is_gray, 0:3] = 255
    return logo, Image.fromarray(white)


LOGO, LOGO_W = load_logo()


def logo_header(dark):
    """Üst başlık: sembol + ARABACI REKLAM yazısı yan yana."""
    src = LOGO_W if dark else LOGO
    mark = src.crop((300, 0, 700, 392))
    word = src.crop((0, 445, 1004, 749))
    mh = 84
    mark = mark.resize((int(mark.width * mh / mark.height), mh), Image.LANCZOS)
    wh = 62
    word = word.resize((int(word.width * wh / word.height), wh), Image.LANCZOS)
    img = Image.new("RGBA", (mark.width + 18 + word.width, mh), (0, 0, 0, 0))
    img.alpha_composite(mark, (0, 0))
    img.alpha_composite(word, (mark.width + 18, (mh - wh) // 2 + 4))
    return img


# ---------------------------------------------------------------- metin yardımcıları

def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if fnt.getlength(test) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, fnt, fill, max_w=CW, gap=1.22, align="left"):
    lines = wrap(text, fnt, max_w)
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * gap)
    for i, l in enumerate(lines):
        xx = x if align == "left" else x + (max_w - fnt.getlength(l)) / 2
        d.text((xx, y + i * lh), l, font=fnt, fill=fill)
    return y + len(lines) * lh


def kicker(d, x, y, text, color):
    f = font("Inter-ExtraBold", 30)
    d.text((x, y), text, font=f, fill=color)
    d.rectangle((x, y + 46, x + 70, y + 52), fill=color)
    return y + 80


# ---------------------------------------------------------------- ikonlar

def icon_sun(d, cx, cy, r, color):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    for i in range(12):
        a = math.radians(i * 30)
        r1, r2 = r * 1.35, r * 1.75
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a), cy + r2 * math.sin(a)),
               fill=color, width=max(6, int(r * 0.16)))


def icon_thermo(d, cx, cy, s, color, fill_col, bg):
    w = s * 0.32
    d.rounded_rectangle((cx - w / 2, cy - s, cx + w / 2, cy + s * 0.5), w / 2, outline=color, width=10, fill=bg)
    d.ellipse((cx - s * 0.33, cy + s * 0.25, cx + s * 0.33, cy + s * 0.91), fill=fill_col, outline=color, width=10)
    d.rounded_rectangle((cx - w / 4, cy - s * 0.2, cx + w / 4, cy + s * 0.5), w / 4, fill=fill_col)
    for k in range(4):
        y = cy - s * 0.8 + k * s * 0.22
        d.line((cx + w / 2 + 14, y, cx + w / 2 + 44, y), fill=color, width=7)


def icon_eye(d, cx, cy, s, color, bg):
    """Badem şeklinde göz + güneş gözlüğü camı gibi yarı koyu üst kısım."""
    n = 60
    top = [(cx - s + 2 * s * i / n, cy - s * 0.55 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    bot = [(cx + s - 2 * s * i / n, cy + s * 0.55 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    d.polygon(top + bot, fill=color)
    inner_top = [(cx - s * 0.8 + 1.6 * s * i / n, cy - s * 0.4 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    inner_bot = [(cx + s * 0.8 - 1.6 * s * i / n, cy + s * 0.4 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    d.polygon(inner_top + inner_bot, fill=bg)
    d.ellipse((cx - s * 0.36, cy - s * 0.36, cx + s * 0.36, cy + s * 0.36), fill=color)
    d.ellipse((cx - s * 0.15, cy - s * 0.15, cx + s * 0.15, cy + s * 0.15), fill=bg)
    d.ellipse((cx + s * 0.08, cy - s * 0.22, cx + s * 0.2, cy - s * 0.1), fill=bg)


def icon_lock(d, cx, cy, s, color, bg):
    d.arc((cx - s * 0.55, cy - s * 1.15, cx + s * 0.55, cy - s * 0.05), 180, 360, fill=color, width=int(s * 0.18))
    d.line((cx - s * 0.55 + s * 0.09, cy - s * 0.6, cx - s * 0.55 + s * 0.09, cy - s * 0.1), fill=color, width=int(s * 0.18))
    d.line((cx + s * 0.55 - s * 0.09, cy - s * 0.6, cx + s * 0.55 - s * 0.09, cy - s * 0.1), fill=color, width=int(s * 0.18))
    d.rounded_rectangle((cx - s * 0.85, cy - s * 0.2, cx + s * 0.85, cy + s * 0.95), s * 0.18, fill=color)
    d.ellipse((cx - s * 0.16, cy + s * 0.15, cx + s * 0.16, cy + s * 0.47), fill=bg)
    d.rectangle((cx - s * 0.06, cy + s * 0.35, cx + s * 0.06, cy + s * 0.7), fill=bg)


def icon_shield(d, cx, cy, s, color, bg):
    pts = [(cx, cy - s), (cx + s * 0.85, cy - s * 0.65), (cx + s * 0.75, cy + s * 0.25),
           (cx, cy + s), (cx - s * 0.75, cy + s * 0.25), (cx - s * 0.85, cy - s * 0.65)]
    d.polygon(pts, fill=color)
    d.line((cx - s * 0.38, cy, cx - s * 0.08, cy + s * 0.3), fill=bg, width=int(s * 0.16))
    d.line((cx - s * 0.08, cy + s * 0.3, cx + s * 0.42, cy - s * 0.25), fill=bg, width=int(s * 0.16))


def icon_seat(d, cx, cy, s, color):
    d.rounded_rectangle((cx - s * 0.45, cy - s, cx + s * 0.2, cy + s * 0.25), s * 0.2, fill=color)
    d.rounded_rectangle((cx - s * 0.45, cy + s * 0.05, cx + s * 0.8, cy + s * 0.5), s * 0.18, fill=color)
    d.rounded_rectangle((cx - s * 0.32, cy - s * 1.35, cx + s * 0.08, cy - s * 1.05), s * 0.12, fill=color)
    d.line((cx - s * 0.2, cy + s * 0.5, cx - s * 0.3, cy + s * 0.95), fill=color, width=int(s * 0.14))
    d.line((cx + s * 0.6, cy + s * 0.5, cx + s * 0.7, cy + s * 0.95), fill=color, width=int(s * 0.14))


def car(w, tint, body, glass_line=WHITE):
    """Yandan görünüm araç silueti, camları filmli."""
    s = w / 1000
    img = Image.new("RGBA", (w, int(420 * s)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    P = lambda pts: [(x * s, y * s) for x, y in pts]
    body_pts = [(40, 300), (60, 220), (180, 190), (300, 90), (420, 60), (640, 60), (760, 160), (900, 190),
                (960, 230), (970, 300), (930, 330), (70, 330)]
    d.polygon(P(body_pts), fill=body)
    # camlar
    d.polygon(P([(320, 110), (430, 82), (520, 82), (520, 185), (230, 190)]), fill=tint)
    d.polygon(P([(545, 82), (630, 82), (735, 175), (545, 185)]), fill=tint)
    # cam yansıması
    d.line(P([(330, 170), (400, 100)]), fill=glass_line + (90,), width=int(10 * s))
    d.line(P([(580, 170), (640, 110)]), fill=glass_line + (90,), width=int(10 * s))
    # tekerlekler
    for x in (230, 770):
        d.ellipse(P([(x - 85, 245), (x + 85, 415)]), fill=(25, 27, 30))
        d.ellipse(P([(x - 45, 285), (x + 45, 375)]), fill=(150, 156, 162))
    # far
    d.rounded_rectangle(P([(905, 215), (955, 240)]), int(8 * s), fill=(255, 230, 160))
    return img


# ---------------------------------------------------------------- sabit parçalar

def base(bg, dark):
    img = Image.new("RGBA", (W, H), bg + (255,))
    d = ImageDraw.Draw(img)
    # üstte logonun 3 renginden ince şerit
    third = W / 3
    for i, c in enumerate([RED, GREEN, TEAL]):
        d.rectangle((i * third, 0, (i + 1) * third, 10), fill=c)
    img.alpha_composite(logo_header(dark), (M, 54))
    return img, d


def footer(img, idx, dark, accent=TEAL):
    d = ImageDraw.Draw(img)
    fg = WHITE if dark else GRAY
    y = H - 132
    # telefon kapsülü
    fnum = font("InterDisplay-ExtraBold", 40)
    pw = int(fnum.getlength(PHONE)) + 120
    pill_bg = WHITE if dark else GRAY
    pill_fg = GRAY if dark else WHITE
    d.rounded_rectangle((M, y, M + pw, y + 76), 38, fill=pill_bg)
    # telefon ikonu
    cx, cy = M + 46, y + 38
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=accent)
    d.rounded_rectangle((cx - 8, cy - 13, cx + 8, cy + 13), 4, outline=WHITE, width=3)
    d.line((cx - 3, cy + 8, cx + 3, cy + 8), fill=WHITE, width=2)
    d.text((M + 86, y + 13), PHONE, font=fnum, fill=pill_fg)
    # sayfa göstergesi: 10 çizgi + sayaç
    seg, gap = 22, 7
    total_w = N * seg + (N - 1) * gap
    x0 = W - M - total_w
    for i in range(N):
        x = x0 + i * (seg + gap)
        col = accent if i <= idx else ((255, 255, 255, 70) if dark else (69, 75, 82, 55))
        d.rounded_rectangle((x, y + 22, x + seg, y + 28), 3, fill=col)
    f = font("Inter-Bold", 26)
    left = N - idx - 1
    txt = f"{idx + 1}/{N}" + ("  ·  Son" if left == 0 else f"  ·  {left} kaldı")
    d.text((W - M - f.getlength(txt), y + 40), txt, font=f, fill=fg)


def swipe_hint(d, dark, text="Kaydır"):
    f = font("Inter-Bold", 30)
    col = WHITE if dark else GRAY
    x = W - M - f.getlength(text) - 50
    y = H - 210
    d.text((x, y), text, font=f, fill=col)
    ax = W - M - 30
    d.line((ax - 10, y + 20, ax + 24, y + 20), fill=col, width=5)
    d.polygon([(ax + 30, y + 20), (ax + 14, y + 8), (ax + 14, y + 32)], fill=col)


# ---------------------------------------------------------------- sayfalar

def s1():
    img, d = base(DARK, True)
    # arka planda logonun üçgen renkleri ile büyük yay
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((520, 140, 1300, 920), fill=TEAL + (60,))
    gd.ellipse((-300, 700, 450, 1450), fill=RED + (45,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(img)
    fc = font("Inter-ExtraBold", 26)
    chip_t = "PROFESYONEL UYGULAMA"
    d.rounded_rectangle((M, 230, M + fc.getlength(chip_t) + 52, 286), 28, fill=TEAL)
    d.text((M + 26, 241), chip_t, font=fc, fill=WHITE)
    fb = font("InterDisplay-Black", 150)
    d.text((M - 4, 300), "OTO CAM", font=fb, fill=WHITE)
    d.text((M - 4, 450), "FİLMİ", font=fb, fill=GREEN)
    text_block(d, M, 640, "Serin, güvenli ve şık bir sürüş için bilmeniz gerekenler.", font("Inter-SemiBold", 40),
               (210, 216, 222), max_w=700)
    c = car(820, (20, 24, 28, 255), (226, 230, 234))
    img.alpha_composite(c, ((W - c.width) // 2, 770))
    swipe_hint(d, True)
    footer(img, 0, True)
    return img


def s2():
    img, d = base(LIGHT, False)
    y = kicker(d, M, 220, "TEMEL BİLGİ", TEAL)
    d.text((M, y), "Cam filmi nedir?", font=font("InterDisplay-Black", 92), fill=GRAY)
    y = text_block(d, M, y + 130, "Araç camlarının iç yüzeyine uygulanan, çok katmanlı ince bir polyester filmdir. "
                               "Güneş ışınlarını süzer, camı güçlendirir ve aracınıza şık bir görünüm kazandırır.",
                   font("Inter-Medium", 40), (80, 86, 94))
    # katman diyagramı
    y += 50
    layers = [("Dış ortam", None), ("Araç camı", (190, 214, 222)), ("Cam filmi", TEAL), ("Araç içi", None)]
    lx = M
    d.rounded_rectangle((lx, y, lx + CW, y + 300), 30, fill=WHITE)
    # güneş -> cam -> film -> iç
    icon_sun(d, lx + 110, y + 150, 46, (240, 170, 40))
    d.rectangle((lx + 280, y + 40, lx + 330, y + 260), fill=(190, 214, 222))
    d.rectangle((lx + 330, y + 40, lx + 352, y + 260), fill=TEAL)
    for k, (yy, alpha) in enumerate([(100, 255), (150, 255), (200, 255)]):
        d.line((lx + 180, y + yy, lx + 275, y + yy), fill=(240, 170, 40), width=8)
        d.line((lx + 360, y + yy, lx + 440, y + yy), fill=(240, 170, 40, 255), width=3)
    f = font("Inter-Bold", 30)
    d.text((lx + 270, y + 272 - 4), "", font=f, fill=GRAY)
    tx = lx + 500
    d.text((tx, y + 60), "Cam", font=font("Inter-Bold", 34), fill=(120, 150, 160))
    d.text((tx, y + 110), "+ Cam filmi", font=font("Inter-Bold", 34), fill=TEAL)
    d.text((tx, y + 175), "= Daha az ısı,", font=font("InterDisplay-ExtraBold", 38), fill=GRAY)
    d.text((tx, y + 222), "daha az UV", font=font("InterDisplay-ExtraBold", 38), fill=GRAY)
    footer(img, 1, False)
    return img


def s3():
    img, d = base(TEAL, True)
    y = kicker(d, M, 220, "SAĞLIĞINIZ İÇİN", WHITE)
    icon_sun(d, W - M - 130, 420, 70, (255, 255, 255, 255))
    d.text((M - 8, y - 10), "%99", font=font("InterDisplay-Black", 280), fill=WHITE)
    d.text((M, y + 300), "UV koruması", font=font("InterDisplay-Black", 84), fill=DARK)
    text_block(d, M, y + 430, "Kaliteli cam filmleri, güneşin zararlı UV ışınlarının %99'a varan kısmını engeller. "
                              "Uzun yolculuklarda cildinizi ve gözlerinizi korur.",
               font("Inter-SemiBold", 40), WHITE)
    footer(img, 2, True, accent=DARK)
    return img


def s4():
    img, d = base(LIGHT, False)
    y = kicker(d, M, 220, "KONFOR", RED)
    d.text((M, y), "Daha serin", font=font("InterDisplay-Black", 110), fill=GRAY)
    d.text((M, y + 120), "bir araç", font=font("InterDisplay-Black", 110), fill=RED)
    icon_thermo(d, W - M - 150, y + 130, 150, RED, (238, 160, 150), LIGHT)
    yy = y + 320
    items = [("Güneş ısısını azaltır", "Araç içi yaz aylarında çok daha serin kalır."),
             ("Klima daha az yorulur", "Daha hızlı soğuma, yakıt tasarrufuna katkı."),
             ("Direksiyon ve koltuklar", "Güneşte bekleyen araçta daha az ısınır.")]
    for i, (t, sub) in enumerate(items):
        d.rounded_rectangle((M, yy, M + CW, yy + 140), 26, fill=WHITE)
        d.rounded_rectangle((M, yy, M + 14, yy + 140), 7, fill=RED)
        d.text((M + 46, yy + 24), t, font=font("InterDisplay-ExtraBold", 42), fill=GRAY)
        d.text((M + 46, yy + 80), sub, font=font("Inter-Medium", 32), fill=(110, 116, 124))
        yy += 160
    footer(img, 3, False, accent=RED)
    return img


def s5():
    img, d = base(DARK, True)
    y = kicker(d, M, 220, "GÜVENLİ SÜRÜŞ", GREEN)
    # ikon: göz, büyük
    icon_eye(d, W // 2, 520, 190, GREEN, DARK)
    d.text((M, 700), "Daha az parlama", font=font("InterDisplay-Black", 100), fill=WHITE)
    text_block(d, M, 840, "Güneşin ve karşıdan gelen farların yarattığı göz kamaşmasını azaltır. "
                          "Gözleriniz daha az yorulur, yola daha rahat odaklanırsınız.",
               font("Inter-Medium", 40), (205, 211, 218))
    footer(img, 4, True, accent=GREEN)
    return img


def s6():
    img, d = base(RED, True)
    y = kicker(d, M, 220, "MAHREMİYET", WHITE)
    d.text((M, y), "Daha fazla", font=font("InterDisplay-Black", 110), fill=WHITE)
    d.text((M, y + 120), "mahremiyet", font=font("InterDisplay-Black", 110), fill=DARK)
    icon_lock(d, W - M - 120, y + 160, 110, WHITE, RED)
    yy = y + 330
    for t in ["Araç içi dışarıdan zor görünür, eşyalarınız meraklı gözlerden uzak kalır",
              "Hırsızlık riskine karşı caydırıcı olur",
              "Kendinizi daha özel ve rahat hissedersiniz"]:
        d.ellipse((M, yy + 14, M + 30, yy + 44), fill=WHITE)
        yy = text_block(d, M + 56, yy, t, font("Inter-SemiBold", 40), WHITE, max_w=CW - 56) + 28
    footer(img, 5, True, accent=DARK)
    return img


def s7():
    img, d = base(LIGHT, False)
    y = kicker(d, M, 220, "EKSTRA GÜVENLİK", TEAL)
    d.text((M, y), "Cam kırılsa bile", font=font("InterDisplay-Black", 88), fill=GRAY)
    d.text((M, y + 100), "dağılmaz", font=font("InterDisplay-Black", 88), fill=TEAL)
    # kırık cam çizimi
    gx, gy, gw, gh = M, y + 250, CW, 340
    d.rounded_rectangle((gx, gy, gx + gw, gy + gh), 30, fill=(214, 232, 236))
    cx, cy = gx + gw * 0.42, gy + gh * 0.5
    import random
    random.seed(4)
    for k in range(14):
        a = k / 14 * 2 * math.pi + random.uniform(-0.15, 0.15)
        L = random.uniform(140, 330)
        px, py = cx, cy
        for seg in range(3):
            nx = px + math.cos(a + random.uniform(-0.3, 0.3)) * L / 3
            ny = py + math.sin(a + random.uniform(-0.3, 0.3)) * L / 3
            nx = min(max(nx, gx + 10), gx + gw - 10)
            ny = min(max(ny, gy + 10), gy + gh - 10)
            d.line((px, py, nx, ny), fill=WHITE, width=5)
            px, py = nx, ny
    for r in (40, 90):
        d.ellipse((cx - r, cy - r * 0.8, cx + r, cy + r * 0.8), outline=WHITE, width=4)
    icon_shield(d, gx + gw - 130, gy + gh / 2, 85, TEAL, (214, 232, 236))
    text_block(d, M, gy + gh + 40, "Kaza veya darbe anında film, cam parçalarını bir arada tutar. "
                                   "Sıçrayan cam parçalarının yaralanmalara yol açma riskini azaltır.",
               font("Inter-Medium", 38), (80, 86, 94))
    footer(img, 6, False)
    return img


def s8():
    img, d = base(GREEN, True)
    y = kicker(d, M, 220, "İÇ MEKAN KORUMASI", DARK)
    icon_seat(d, W - M - 160, y + 170, 130, DARK)
    d.text((M, y), "Aracınız", font=font("InterDisplay-Black", 108), fill=WHITE)
    d.text((M, y + 118), "daha uzun", font=font("InterDisplay-Black", 108), fill=WHITE)
    d.text((M, y + 236), "yeni kalır", font=font("InterDisplay-Black", 108), fill=DARK)
    yy = y + 420
    cards = [("Döşeme", "Solmayı geciktirir"), ("Torpido", "Çatlama riski azalır"), ("Değer", "İkinci elde avantaj")]
    cw = (CW - 2 * 24) / 3
    for i, (t, s) in enumerate(cards):
        x = M + i * (cw + 24)
        d.rounded_rectangle((x, yy, x + cw, yy + 220), 26, fill=WHITE)
        d.text((x + 28, yy + 34), t, font=font("InterDisplay-Black", 44), fill=GRAY)
        text_block(d, x + 28, yy + 104, s, font("Inter-SemiBold", 30), (100, 106, 114), max_w=cw - 56, gap=1.25)
    footer(img, 7, True, accent=DARK)
    return img


def s9():
    img, d = base(LIGHT, False)
    y = kicker(d, M, 220, "DOĞRU SEÇİM", RED)
    d.text((M, y), "Film çeşitleri", font=font("InterDisplay-Black", 96), fill=GRAY)
    yy = y + 150
    cols = [("Karbon Film", GRAY, ["Mat ve şık görünüm", "Solmaya dayanıklı", "Uygun fiyatlı",
                                   "İyi ısı yalıtımı"]),
            ("Nano Seramik", TEAL, ["En yüksek ısı yalıtımı", "Net ve berrak görüş",
                                    "Telefon/GPS sinyalini kesmez", "Uzun ömürlü"])]
    cw = (CW - 30) / 2
    for i, (title, col, feats) in enumerate(cols):
        x = M + i * (cw + 30)
        d.rounded_rectangle((x, yy, x + cw, yy + 560), 30, fill=WHITE, outline=col, width=4)
        d.rounded_rectangle((x, yy, x + cw, yy + 110), 30, fill=col)
        d.rectangle((x, yy + 80, x + cw, yy + 110), fill=col)
        d.text((x + 30, yy + 28), title, font=font("InterDisplay-Black", 46), fill=WHITE)
        fy = yy + 150
        for ft in feats:
            d.line((x + 32, fy + 22, x + 44, fy + 34), fill=col, width=6)
            d.line((x + 44, fy + 34, x + 64, fy + 8), fill=col, width=6)
            fy = text_block(d, x + 84, fy, ft, font("Inter-SemiBold", 32), GRAY, max_w=cw - 110, gap=1.2) + 34
    text_block(d, M, yy + 600, "Hangisinin size uygun olduğuna birlikte karar verelim.", font("Inter-SemiBold", 36),
               RED)
    footer(img, 8, False, accent=RED)
    return img


def s10():
    img, d = base(DARK, True)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((140, 160, 940, 900), fill=TEAL + (55,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(140)))
    d = ImageDraw.Draw(img)
    lg = LOGO_W.resize((520, int(520 * LOGO_W.height / LOGO_W.width)), Image.LANCZOS)
    img.alpha_composite(lg, ((W - lg.width) // 2, 200))
    y = 200 + lg.height + 60
    f1 = font("InterDisplay-Black", 64)
    t = "Randevu için hemen arayın"
    d.text(((W - f1.getlength(t)) / 2, y), t, font=f1, fill=WHITE)
    # büyük numara kartı
    fnum = font("InterDisplay-Black", 92)
    nw = fnum.getlength(PHONE)
    bx0, by0 = (W - nw) / 2 - 50, y + 110
    d.rounded_rectangle((bx0, by0, bx0 + nw + 100, by0 + 150), 40, fill=GREEN)
    d.text((bx0 + 50, by0 + 22), PHONE, font=fnum, fill=WHITE)
    fs = font("Inter-SemiBold", 34)
    s = "Profesyonel uygulama · Kaliteli malzeme"
    d.text(((W - fs.getlength(s)) / 2, by0 + 190), s, font=fs, fill=(200, 206, 212))
    fs2 = font("Inter-Medium", 26)
    s2 = "Uygulamalar yasal mevzuata uygun şekilde yapılır."
    d.text(((W - fs2.getlength(s2)) / 2, by0 + 245), s2, font=fs2, fill=(140, 148, 156))
    footer(img, 9, True, accent=GREEN)
    return img


SLIDES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(out, exist_ok=True)
    for i, fn in enumerate(SLIDES):
        fn().convert("RGB").save(os.path.join(out, f"oto-cam-filmi-{i + 1:02d}.png"), optimize=True)


if __name__ == "__main__":
    main()
