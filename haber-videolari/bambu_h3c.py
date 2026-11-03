"""Bambu Lab H3C tanıtım videosu: 10 sayfa, dikey (9:16).

Her sayfa farklı bir tasarıma sahip. Altta 10 parçalı sayfa göstergesi ve
"4 / 10 · 6 sayfa kaldı" bilgisi bütün sayfalarda görünür.

Kullanım:
  python3 bambu_h3c.py <cikti_sessiz.mp4>              # video
  python3 bambu_h3c.py <onek> --pngs                   # her sayfanın son halini PNG kaydeder (carousel)
  python3 bambu_h3c.py <onek> --preview 3.2,9.5        # belirli anların karelerini PNG kaydeder
"""
import math
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

import video as V
from video import El, chip, ease_in_out, ease_out_cubic, fit_font, font, rounded, text_image, with_alpha, wrap

V.Y_SHIFT = 0

W, H, FPS = V.W, V.H, V.FPS
M = V.MARGIN
CW = V.CONTENT_W

GREEN = (0, 214, 98)
GREEN_D = (0, 150, 70)
WHITE = (255, 255, 255)
SOFT = (170, 180, 192)
DIM = (110, 120, 132)
BG_TOP = (6, 8, 11)
BG_BOT = (14, 20, 24)
CARD = (255, 255, 255, 16)
CARD_LINE = (255, 255, 255, 34)
RED = (255, 92, 92)

# Sayfa süreleri (saniye)
DURS = [4.5, 5.5, 5.0, 6.0, 5.0, 5.0, 5.5, 6.0, 6.5, 6.5]
STARTS = [sum(DURS[:i]) for i in range(len(DURS))]
TOTAL = sum(DURS)
T_TR = 0.45  # sayfa geçiş süresi

F_BODY = font("Inter-SemiBold", 46)
F_SMALL = font("Inter-Medium", 36)


# ---------------------------------------------------------------- ortak parçalar

def title_block(kicker, title, y=400, size=96, color=WHITE):
    """Küçük yeşil üst başlık + büyük başlık. (öğeler, alt y) döner."""
    els = []
    k = text_image([kicker], font("Inter-ExtraBold", 36), GREEN)
    els.append(El(k, M, y, 0.05, dy=30))
    lines = wrap(title, font("InterDisplay-Black", size), CW)
    f = fit_font(lines, "InterDisplay-Black", size, CW)
    img = text_image(lines, f, color, line_gap=1.02)
    els.append(El(img, M, y + 62, 0.15, dy=70))
    return els, y + 62 + img.height


def para(text, y, delay, color=SOFT, fnt=F_BODY, width=CW, x=M):
    img = text_image(wrap(text, fnt, width), fnt, color, line_gap=1.2)
    return El(img, x, y, delay), y + img.height


def glow(img, radius=28, strength=2):
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = img.filter(ImageFilter.GaussianBlur(radius))
    for _ in range(strength):
        base.alpha_composite(g)
    base.alpha_composite(img)
    return base


def pad_canvas(img, p):
    c = Image.new("RGBA", (img.width + 2 * p, img.height + 2 * p), (0, 0, 0, 0))
    c.alpha_composite(img, (p, p))
    return c


# ---------------------------------------------------------------- sayfalar
# Her sayfa: (öğeler listesi, dinamik çizim fonksiyonu veya None)

def page1():
    els = []
    els.append(El(chip("BUGÜN TANITILDI", (8, 12, 10), GREEN, size=36), M, 430, 0.1, dy=30))
    k = text_image(["BAMBU LAB"], font("InterDisplay-Black", 70), SOFT)
    els.append(El(k, M, 540, 0.25, dy=40))
    big = text_image(["H3C"], font("InterDisplay-Black", 380), WHITE, line_gap=0.95)
    big_g = pad_canvas(big, 60)
    tinted = Image.new("RGBA", big_g.size, GREEN + (0,))
    tinted.putalpha(big_g.split()[3])
    gl = tinted.filter(ImageFilter.GaussianBlur(40))
    combo = Image.new("RGBA", big_g.size, (0, 0, 0, 0))
    combo.alpha_composite(gl)
    combo.alpha_composite(big_g)
    els.append(El(combo, M - 72, 580, 0.4, dur=0.7, dy=120))
    t = text_image(["9 kafa.", "Tek yazıcı."], font("InterDisplay-Black", 104), WHITE, line_gap=1.0)
    els.append(El(t, M, 1040, 0.9, dy=60))
    s = text_image(["Takım değiştiricili yeni amiral gemisi"], font("Inter-SemiBold", 42), GREEN)
    els.append(El(s, M, 1290, 1.3, dy=30))

    def dyn(layer, tl, a):
        # 9 küçük nokta sırayla yanar
        d = ImageDraw.Draw(layer)
        for i in range(9):
            on = tl > 1.5 + i * 0.08
            x = M + i * 54
            col = GREEN + (int(255 * a),) if on else (255, 255, 255, int(40 * a))
            d.ellipse((x, 1375, x + 30, 1405), fill=col)

    return els, dyn


def tool_icon(size, on):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    border = GREEN if on else CARD_LINE
    fill = (0, 214, 98, 40) if on else CARD
    d.rounded_rectangle((0, 0, size - 1, size - 1), 26, fill=fill, outline=border, width=3)
    cx = size / 2
    # basit baskı kafası çizimi: gövde + nozul
    k = size / 180
    d.rounded_rectangle((cx - 34 * k, 34 * k, cx + 34 * k, 104 * k), 12 * k, fill=(255, 255, 255, 220 if on else 90))
    d.polygon([(cx - 16 * k, 104 * k), (cx + 16 * k, 104 * k), (cx, 134 * k)], fill=GREEN if on else (255, 255, 255, 90))
    if on:
        d.ellipse((cx - 7 * k, 140 * k, cx + 7 * k, 154 * k), fill=(255, 170, 60))
    return img


def page2():
    els, y = title_block("NASIL ÇALIŞIYOR?", "Swaptek takım değiştirici", size=92)
    p, y2 = para("9 bağımsız kafa: her birinin kendi ısıtıcısı, kesicisi ve çelik nozulu var.",
                 y + 30, 0.4, color=WHITE)
    els.append(p)
    grid_y = y2 + 36
    TS = 118
    icon_off = tool_icon(TS, False)
    icon_on = tool_icon(TS, True)
    gap = (CW - 3 * TS) / 2
    st, _ = para("Baskı alanı: 330 × 320 × 325 mm", grid_y + 3 * TS + 2 * 20 + 36, 1.6, color=SOFT, fnt=F_SMALL)
    els.append(st)

    def dyn(layer, tl, a):
        active = int((tl - 0.6) / 0.35) % 9 if tl > 0.6 else -1
        for i in range(9):
            p_in = ease_out_cubic((tl - 0.5 - i * 0.06) / 0.4)
            if p_in <= 0:
                continue
            r, c = divmod(i, 3)
            x = int(M + c * (TS + gap))
            yy = int(grid_y + r * (TS + 20) + (1 - p_in) * 30)
            ic = icon_on if i == active else icon_off
            layer.alpha_composite(with_alpha(ic, p_in * a), (x, yy))

    return els, dyn


def page3():
    els = []
    k = text_image(["MALZEME DEĞİŞİMİ"], font("Inter-ExtraBold", 36), GREEN)
    els.append(El(k, 0, 400, 0.05, center=True, dy=30))
    cx, cy, R = W // 2, 800, 300
    p1, y = para("Tüm kafalar önceden ısıtılmış ve filament yüklü bekler. Renk değiştirmek için filamenti boşaltıp yeniden yüklemeye gerek yok.",
                 1160, 0.9, color=WHITE)
    els.append(p1)

    def dyn(layer, tl, a):
        d = ImageDraw.Draw(layer)
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(255, 255, 255, int(30 * a)), width=26)
        p = ease_out_cubic((tl - 0.2) / 1.4)
        if p > 0:
            d.arc((cx - R, cy - R, cx + R, cy + R), -90, -90 + 360 * p, fill=GREEN + (int(255 * a),), width=26)
            ang = math.radians(-90 + 360 * p)
            ex, ey = cx + R * math.cos(ang), cy + R * math.sin(ang)
            d.ellipse((ex - 22, ey - 22, ex + 22, ey + 22), fill=WHITE + (int(255 * a),))
        sec = 6 * max(0.0, min(1.0, p))
        f1 = font("InterDisplay-Black", 230)
        txt = f"{sec:.0f}" if p < 1 else "6"
        f_small = font("InterDisplay-Black", 90)
        w_lt = f_small.getlength("<")
        w_n = f1.getlength(txt)
        tot = w_lt + 12 + w_n
        x0 = cx - tot / 2
        d.text((x0, cy - 40), "<", font=f_small, fill=GREEN + (int(255 * a),))
        d.text((x0 + w_lt + 12, cy - 150), txt, font=f1, fill=WHITE + (int(255 * a),))
        f2 = font("Inter-Bold", 46)
        lab = "saniye"
        d.text((cx - f2.getlength(lab) / 2, cy + 110), lab, font=f2, fill=SOFT + (int(255 * a),))

    return els, dyn


def page4():
    els, y = title_block("GERÇEK TEST", "2 kattan daha hızlı bitirdi", size=92)
    p, y = para("Aynı çok renkli baskı (How-To Geek testi):", y + 30, 0.35, color=SOFT)
    els.append(p)
    bars_y = y + 60
    note, _ = para("Klasik sistemlerde her renk değişiminde filament atık kuleye boşaltılır. H3C ise kafa değiştirir.",
                   bars_y + 430, 1.6, color=WHITE, fnt=font("Inter-Medium", 38))
    els.append(note)

    def dyn(layer, tl, a):
        d = ImageDraw.Draw(layer)
        rows = [("H3C", 28, GREEN, "28 saat"), ("H2C", 62, (120, 128, 138), "62 saat*")]
        maxw = CW - 20
        for i, (name, hrs, col, lab) in enumerate(rows):
            yy = bars_y + i * 180
            p = ease_out_cubic((tl - 0.6 - i * 0.25) / 1.0)
            fa = int(255 * a * min(1, max(0, (tl - 0.5 - i * 0.25) / 0.3)))
            d.text((M, yy), name, font=font("InterDisplay-Black", 56), fill=WHITE + (fa,))
            d.rounded_rectangle((M, yy + 80, M + maxw, yy + 150), 20, fill=(255, 255, 255, int(18 * a)))
            if p > 0:
                bw = maxw * hrs / 62 * p
                d.rounded_rectangle((M, yy + 80, M + max(40, bw), yy + 150), 20, fill=col + (fa,))
                fl = font("InterDisplay-Black", 44)
                tx = M + max(40, bw) + 18
                if tx + fl.getlength(lab) > W - M:
                    tx = M + max(40, bw) - fl.getlength(lab) - 22
                    d.text((tx, yy + 90), lab, font=fl, fill=(10, 10, 10, fa))
                else:
                    d.text((tx, yy + 90), lab, font=fl, fill=WHITE + (fa,))
        fa = int(255 * a * min(1, max(0, (tl - 1.4) / 0.4)))
        d.text((M, bars_y + 370), "* H2C: dilimleyici tahmini, 258 g atık kule ile", font=font("Inter-Medium", 32),
               fill=DIM + (fa,))

    return els, dyn


def page5():
    els = []
    k = text_image(["HIZ"], font("Inter-ExtraBold", 36), GREEN)
    els.append(El(k, M, 400, 0.05, dy=30))
    cx, cy, R = W // 2, 760, 300
    stats = [("25.000 mm/s²", "ivme"), ("%40", "daha hafif hareket sistemi*")]
    y = 1110
    for i, (v, l) in enumerate(stats):
        card = rounded(CW, 120, 30, CARD, outline=CARD_LINE, width=2)
        d = ImageDraw.Draw(card)
        fv = font("InterDisplay-Black", 56)
        d.text((36, 26), v, font=fv, fill=GREEN)
        d.text((36 + fv.getlength(v) + 24, 40), l, font=font("Inter-SemiBold", 40), fill=WHITE)
        els.append(El(card, M, y + i * 140, 1.0 + i * 0.25, dy=40))
    src = text_image(["* Bambu Lab'in açıklamasına göre"], font("Inter-Medium", 30), DIM)
    els.append(El(src, M, y + 290, 1.6, dy=20))

    def dyn(layer, tl, a):
        d = ImageDraw.Draw(layer)
        aa = int(255 * a)
        # hız göstergesi yayı (210° -> -30°)
        d.arc((cx - R, cy - R, cx + R, cy + R), 150, 390, fill=(255, 255, 255, int(28 * a)), width=22)
        p = ease_out_cubic((tl - 0.2) / 1.3)
        if p > 0:
            d.arc((cx - R, cy - R, cx + R, cy + R), 150, 150 + 240 * p, fill=GREEN + (aa,), width=22)
        for i in range(13):
            ang = math.radians(150 + 240 * i / 12)
            r1, r2 = R - 40, R - (70 if i % 3 == 0 else 55)
            d.line((cx + r1 * math.cos(ang), cy + r1 * math.sin(ang), cx + r2 * math.cos(ang), cy + r2 * math.sin(ang)),
                   fill=(255, 255, 255, int(110 * a)), width=4)
        ang = math.radians(150 + 240 * p)
        d.line((cx, cy, cx + (R - 150) * math.cos(ang), cy + (R - 150) * math.sin(ang)), fill=WHITE + (aa,), width=10)
        d.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=GREEN + (aa,))
        val = int(1400 * p)
        txt = f"{val:,}".replace(",", ".")
        f = font("InterDisplay-Black", 130)
        d.text((cx - f.getlength(txt) / 2, cy + 100), txt, font=f, fill=WHITE + (aa,))
        u = "mm/s"
        fu = font("Inter-Bold", 44)
        d.text((cx - fu.getlength(u) / 2, cy + 255), u, font=fu, fill=SOFT + (aa,))

    return els, dyn


def page6():
    els, y = title_block("ISI", "Zorlu malzemelere hazır", size=96)
    p, _ = para("Aktif ısıtmalı kabin: yüksek sıcaklık isteyen mühendislik filamentleri için.", 1250, 1.4, color=WHITE)
    els.append(p)
    vals = [("NOZUL", 350, 350), ("TABLA", 120, 350), ("KABİN", 65, 350)]
    top, bottom = y + 60, 1180
    col_w = 200
    gap = (CW - 3 * col_w) / 2

    def dyn(layer, tl, a):
        d = ImageDraw.Draw(layer)
        aa = int(255 * a)
        for i, (lab, v, mx) in enumerate(vals):
            x = M + i * (col_w + gap)
            p = ease_out_cubic((tl - 0.4 - i * 0.2) / 1.1)
            bar_top = top + 120
            d.rounded_rectangle((x + 60, bar_top, x + col_w - 60, bottom - 70), 40, fill=(255, 255, 255, int(20 * a)))
            hgt = (bottom - 70 - bar_top) * (v / mx) * max(0, p)
            if p > 0:
                for k in range(int(hgt)):
                    yy = bottom - 70 - k
                    frac = k / max(1, (bottom - 70 - bar_top))
                    c = (int(0 + 255 * frac), int(214 - 120 * frac), int(98 - 60 * frac))
                    d.line((x + 62, yy, x + col_w - 62, yy), fill=c + (aa,))
            num = f"{int(v * max(0, p))}°C"
            f = font("InterDisplay-Black", 64)
            d.text((x + col_w / 2 - f.getlength(num) / 2, top + 20), num, font=f, fill=WHITE + (aa,))
            fl = font("Inter-ExtraBold", 34)
            d.text((x + col_w / 2 - fl.getlength(lab) / 2, bottom - 40), lab, font=fl, fill=SOFT + (aa,))

    return els, dyn


def page7():
    els = []
    k = text_image(["YUMUŞAK TPU İÇİN ÖZEL KAFA"], font("Inter-ExtraBold", 36), GREEN)
    els.append(El(k, M, 400, 0.05, dy=30))
    big = text_image(["75A"], font("InterDisplay-Black", 330), WHITE, line_gap=0.9)
    els.append(El(glow(pad_canvas(big, 30), 30, 1), M - 40, 440, 0.2, dur=0.7, dy=90))
    s = text_image(["sertliğe kadar esnek TPU"], font("InterDisplay-Bold", 58), GREEN)
    els.append(El(s, M, 810, 0.55, dy=40))
    p, _ = para("9. kafa 2,85 mm filament kullanıyor. Bambu Lab'e göre 3 kata kadar daha fazla akış.",
                1280, 1.3, color=WHITE)
    els.append(p)

    def dyn(layer, tl, a):
        d = ImageDraw.Draw(layer)
        aa = int(255 * a)
        y0 = 960
        items = [("1,75 mm", 1.75, (120, 128, 138), "standart"), ("2,85 mm", 2.85, GREEN, "9. kafa")]
        for i, (lab, mm, col, sub) in enumerate(items):
            p = ease_out_cubic((tl - 0.8 - i * 0.25) / 0.6)
            if p <= 0:
                continue
            x = M
            r = mm * 34 * p
            cx, cy = x + 100, y0 + i * 175
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (aa,))
            d.text((x + 240, cy - 52), lab, font=font("InterDisplay-Black", 52), fill=WHITE + (aa,))
            d.text((x + 240, cy + 10), sub, font=font("Inter-SemiBold", 36), fill=SOFT + (aa,))

    return els, dyn


SPOOL_COLORS = [(235, 64, 52), (255, 160, 20), (250, 220, 40), (0, 214, 98), (30, 160, 255),
                (130, 80, 230), (240, 240, 240), (40, 40, 44), (255, 105, 180)]


def page8():
    els, y = title_block("YENİ AMS 3H", "9 makara, tek ünite", size=96)
    feats = ["9 kapalı yuva, RFID ile otomatik tanıma", "Filamenti kendisi yükler",
             "2 yuvada 85°C'ye kadar kurutma", "Eski AMS'lerle 24 makaraya kadar"]
    grid_y = y + 50
    sp = 118
    gap = (CW - 3 * sp) / 2
    fy = grid_y + 3 * sp + 2 * 18 + 44
    for i, f_ in enumerate(feats):
        row = Image.new("RGBA", (CW, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(row)
        d.line((6, 32, 20, 46), fill=GREEN, width=7)
        d.line((20, 46, 44, 16), fill=GREEN, width=7)
        d.text((66, 6), f_, font=font("Inter-SemiBold", 42), fill=WHITE)
        els.append(El(row, M, fy + i * 72, 1.0 + i * 0.22, dy=30))

    def dyn(layer, tl, a):
        d = ImageDraw.Draw(layer)
        aa = int(255 * a)
        for i in range(9):
            p = ease_out_cubic((tl - 0.4 - i * 0.07) / 0.5)
            if p <= 0:
                continue
            r_, c_ = divmod(i, 3)
            cx = M + c_ * (sp + gap) + sp / 2
            cy = grid_y + r_ * (sp + 18) + sp / 2
            R = sp / 2 * p
            col = SPOOL_COLORS[i]
            d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=col + (aa,))
            d.ellipse((cx - R * 0.42, cy - R * 0.42, cx + R * 0.42, cy + R * 0.42), fill=(30, 34, 38, aa))
            d.ellipse((cx - R * 0.16, cy - R * 0.16, cx + R * 0.16, cy + R * 0.16), fill=(10, 12, 14, aa))
            # dönen makara çizgisi
            ang = tl * 2.2 + i
            d.line((cx + R * 0.45 * math.cos(ang), cy + R * 0.45 * math.sin(ang),
                    cx + R * 0.92 * math.cos(ang), cy + R * 0.92 * math.sin(ang)), fill=(0, 0, 0, int(90 * a)), width=5)

    return els, dyn


def proscons_card(title, items, color, sign):
    h = 104 + len(items) * 68
    card = rounded(CW, h, 34, CARD, outline=color + (110,), width=3)
    d = ImageDraw.Draw(card)
    d.text((40, 26), title, font=font("InterDisplay-Black", 48), fill=color)
    fi = font("Inter-SemiBold", 38)
    for i, it in enumerate(items):
        y = 100 + i * 68
        d.ellipse((40, y + 4, 84, y + 48), fill=color + (50,))
        if sign == "+":
            d.line((52, y + 26, 72, y + 26), fill=color, width=5)
            d.line((62, y + 16, 62, y + 36), fill=color, width=5)
        else:
            d.line((52, y + 26, 72, y + 26), fill=color, width=5)
        d.text((108, y), it, font=fi, fill=WHITE)
    return card


def page9():
    els, y = title_block("DÜRÜST DEĞERLENDİRME", "Artıları ve eksileri", size=92)
    pros = proscons_card("ARTILARI", ["6 sn'den kısa renk değişimi", "Çok daha az filament atığı",
                                      "Yumuşak TPU için özel kafa", "350°C nozul, ısıtmalı kabin"], GREEN, "+")
    cons = proscons_card("EKSİLERİ", ["Nozullar hızlı değiştirilemiyor", "Ek AMS'ler tek kafadan beslenir",
                                      "H2C'den daha pahalı", "Büyük ve ağır: ~1 m, 36 kg"], RED, "-")
    els.append(El(pros, M, y + 40, 0.4, dy=50))
    els.append(El(cons, M, y + 40 + pros.height + 26, 0.9, dy=50))
    return els, None


def page10():
    els = []
    k = text_image(["FİYAT VE SATIŞ"], font("Inter-ExtraBold", 36), GREEN)
    els.append(El(k, M, 400, 0.05, dy=30))
    s = text_image(["H3C AMS Combo · bugün satışta"], font("Inter-SemiBold", 42), SOFT)
    els.append(El(s, M, 720, 0.6, dy=30))
    rows = [("İngiltere", "£2.199"), ("Bambu Station ile", "$2.799"), ("Kapalı istasyon + E1 hava temizleyici", "$3.049")]
    y = 820
    for i, (l, v) in enumerate(rows):
        row = rounded(CW, 100, 26, CARD, outline=CARD_LINE, width=2)
        d = ImageDraw.Draw(row)
        fl = font("Inter-SemiBold", 36 if len(l) > 20 else 40)
        d.text((32, 28 if len(l) <= 20 else 31), l, font=fl, fill=WHITE)
        fv = font("InterDisplay-Black", 46)
        d.text((CW - 32 - fv.getlength(v), 22), v, font=fv, fill=GREEN)
        els.append(El(row, M, y + i * 120, 0.9 + i * 0.2, dy=30))
    q = text_image(["Sen olsan alır mıydın?"], font("InterDisplay-Black", 76), WHITE)
    els.append(El(q, M, 1230, 1.8, dy=40))
    c = chip("Yorumlara yaz, takipte kal", (8, 12, 10), GREEN, size=38)
    els.append(El(c, M, 1340, 2.1, dy=30))

    def dyn(layer, tl, a):
        d = ImageDraw.Draw(layer)
        p = ease_out_cubic((tl - 0.2) / 1.0)
        if p <= 0:
            return
        val = int(2499 * p)
        txt = "$" + f"{val:,}".replace(",", ".")
        f = font("InterDisplay-Black", 210)
        d.text((M - 6, 450 + (1 - p) * 40), txt, font=f, fill=WHITE + (int(255 * a * min(1, p * 2)),))

    return els, dyn


PAGES = [page1, page2, page3, page4, page5, page6, page7, page8, page9, page10]


# ---------------------------------------------------------------- arka plan & sabit katman

def make_background():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * k) for i in range(3)))
    bg = bg.convert("RGBA")
    # ince teknik ızgara
    grid = Image.new("RGBA", (W, H + 80), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 80):
        gd.line((x, 0, x, H + 80), fill=(255, 255, 255, 9), width=1)
    for y in range(0, H + 80, 80):
        gd.line((0, y, W, y), fill=(255, 255, 255, 9), width=1)
    return bg, grid


def make_glows():
    """Her sayfa için farklı konumda yumuşak yeşil ışık lekesi."""
    random.seed(5)
    out = []
    for i in range(len(PAGES)):
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(g)
        cx = random.choice([150, W - 150, W // 2])
        cy = random.choice([600, 900, 1200])
        d.ellipse((cx - 420, cy - 420, cx + 420, cy + 420), fill=(0, 214, 98, 38))
        out.append(g.filter(ImageFilter.GaussianBlur(160)))
    return out


def draw_chrome(frame, t, page_idx, page_prog):
    d = ImageDraw.Draw(frame)
    # üst bar
    y = 290
    d.rounded_rectangle((M, y - 22, M + 44, y + 22), 10, fill=GREEN)
    d.text((M + 12, y - 21), "3D", font=font("Inter-Black", 22), fill=(8, 12, 10))
    d.text((M + 62, y - 23), "BAMBU LAB H3C", font=font("Inter-ExtraBold", 38), fill=WHITE)
    fd = font("Inter-SemiBold", 32)
    date = "3 KASIM 2026"
    d.text((W - M - fd.getlength(date), y - 18), date, font=fd, fill=SOFT)
    d.line((M, y + 48, W - M, y + 48), fill=(255, 255, 255, 40), width=2)

    # alt sayfa göstergesi: 10 parça
    n = len(PAGES)
    gap = 10
    seg_w = (CW - gap * (n - 1)) / n
    by = 1478
    for i in range(n):
        x0 = M + i * (seg_w + gap)
        d.rounded_rectangle((x0, by, x0 + seg_w, by + 8), 4, fill=(255, 255, 255, 48))
        if i < page_idx:
            prog = 1.0
        elif i == page_idx:
            prog = page_prog
        else:
            prog = 0.0
        if prog > 0:
            d.rounded_rectangle((x0, by, x0 + max(8, seg_w * prog), by + 8), 4, fill=GREEN)
    cur = page_idx + 1
    left = f"{cur} / {n}"
    remaining = n - cur
    right = "Son sayfa" if remaining == 0 else f"{remaining} sayfa kaldı"
    fl = font("Inter-ExtraBold", 34)
    fr = font("Inter-SemiBold", 32)
    d.text((M, by + 26), left, font=fl, fill=WHITE)
    d.text((W - M - fr.getlength(right), by + 28), right, font=fr, fill=SOFT)


# ---------------------------------------------------------------- render

def page_local_time(k, t):
    # Sayfanın kendi saati, gelen geçiş başladığında başlar
    return t - (STARTS[k] - (T_TR if k > 0 else 0))


def render_page(k, built, tl, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    els, dyn = built[k]
    if dyn:
        dyn(layer, tl, alpha)
    for el in els:
        el.draw(layer, tl, alpha)
    return layer


def frame_at(t, bg, grid, glows, built):
    frame = bg.copy()
    off = int((t * 14) % 80)
    frame.alpha_composite(grid.crop((0, off, W, off + H)))

    k = max(i for i in range(len(PAGES)) if STARTS[i] <= t) if t < TOTAL else len(PAGES) - 1
    end = STARTS[k] + DURS[k]
    in_tr = k < len(PAGES) - 1 and t > end - T_TR
    p = ease_in_out((t - (end - T_TR)) / T_TR) if in_tr else 0.0

    g = glows[k] if not in_tr else Image.blend(glows[k], glows[k + 1], p)
    frame.alpha_composite(g)

    cur = render_page(k, built, page_local_time(k, t), 1 - p)
    out_shift = int(p * W * 0.35)
    if out_shift:
        cur = cur.crop((out_shift, 0, W + out_shift, H))  # sola kayar (sağ taraf boş kalır)
    frame.alpha_composite(cur)
    if in_tr:
        nxt = render_page(k + 1, built, page_local_time(k + 1, t), p)
        in_shift = int((1 - p) * W * 0.35)
        if in_shift:
            nxt = nxt.crop((-in_shift, 0, W - in_shift, H))  # sağdan gelir
        frame.alpha_composite(nxt)

    # gösterge: geçişin yarısında bir sonraki sayfaya geç
    shown = k + 1 if in_tr and p > 0.5 else k
    if shown == k:
        prog = (t - STARTS[k]) / DURS[k]
    else:
        prog = 0.0
    draw_chrome(frame, t, shown, max(0.0, min(1.0, prog)))

    # giriş parlaması ve genel fade
    if t < 0.35:
        frame.alpha_composite(Image.new("RGBA", (W, H), (200, 255, 220, int(160 * (1 - t / 0.35)))))
    fade = min(1.0, t / 0.25, (TOTAL - t) / 0.6)
    if fade < 1:
        frame.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - max(0.0, fade))))))
    return frame


def main():
    out = sys.argv[1]
    bg, grid = make_background()
    glows = make_glows()
    built = [f() for f in PAGES]

    if "--pngs" in sys.argv:
        for k in range(len(PAGES)):
            t = STARTS[k] + DURS[k] - T_TR - 0.05
            frame_at(t, bg, grid, glows, built).convert("RGB").save(f"{out}_sayfa{k + 1:02d}.png")
        return
    if "--preview" in sys.argv:
        times = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        for t in times:
            frame_at(t, bg, grid, glows, built).convert("RGB").save(f"{out}_{t:05.2f}.png")
        return

    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE,
    )
    total = int(TOTAL * FPS)
    for fi in range(total):
        proc.stdin.write(frame_at(fi / FPS, bg, grid, glows, built).convert("RGB").tobytes())
        if fi % 300 == 0:
            print(f"kare {fi}/{total}", flush=True)
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    main()
