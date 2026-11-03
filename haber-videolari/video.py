"""Kastamonu sarı kod uyarısı - dikey (9:16) haber videosu.

Kareleri PIL ile çizer, ffmpeg'e boru (pipe) ile gönderir.
Kullanım: python3 video.py <cikti_sessiz.mp4>
"""
import math
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
MARGIN = 84
CONTENT_W = W - 2 * MARGIN
Y_SHIFT = 90  # sahne içeriğini dikeyde ortalamak için

FONT_DIR = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name + ".otf", size)


# Renkler
YELLOW = (255, 196, 0)
WHITE = (255, 255, 255)
SOFT = (184, 198, 222)
NAVY_TOP = (8, 14, 28)
NAVY_BOT = (18, 36, 66)
CARD = (255, 255, 255, 22)

# Sahne zamanları (saniye)
SCENES = [
    ("hook", 0.0, 5.0),
    ("when", 5.0, 12.0),
    ("where", 12.0, 18.0),
    ("amount", 18.0, 24.0),
    ("risks", 24.0, 32.0),
    ("tips", 32.0, 39.0),
    ("outro", 39.0, 43.0),
]
DURATION = SCENES[-1][2]
FLASHES = [0.25, 24.05]  # şimşek anları (müzikte gök gürültüsü ile eşleşir)


# ---------------------------------------------------------------- yardımcılar

def ease_out_cubic(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if fnt.getlength(test) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_font(lines, name, max_size, max_w):
    size = max_size
    while size > 20:
        f = font(name, size)
        if all(f.getlength(l) <= max_w for l in lines):
            return f
        size -= 2
    return font(name, size)


def text_image(lines, fnt, color, line_gap=1.08, align="left", width=None):
    """Satırları sıkı bir RGBA görsele çizer."""
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * line_gap)
    tw = width or int(max(fnt.getlength(l) for l in lines)) + 8
    img = Image.new("RGBA", (tw, lh * len(lines) + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        x = 0
        if align == "center":
            x = (tw - fnt.getlength(l)) / 2
        d.text((x, i * lh), l, font=fnt, fill=color)
    return img


def rounded(w, h, r, fill, outline=None, width=0):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=outline, width=width)
    return img


def chip(text, fg, bg, size=34, pad_x=26, pad_y=14, icon=None):
    f = font("Inter-ExtraBold", size)
    tw = int(f.getlength(text))
    icon_w = int(size * 1.15) if icon else 0
    w = tw + 2 * pad_x + icon_w
    asc, desc = f.getmetrics()
    h = asc + desc + 2 * pad_y - 6
    img = rounded(w, h, h // 2, bg)
    d = ImageDraw.Draw(img)
    x = pad_x
    if icon == "warn":
        s = size * 0.95
        cy = h / 2
        d.polygon([(x, cy + s / 2), (x + s / 2, cy - s / 2), (x + s, cy + s / 2)], fill=fg)
        d.rectangle((x + s / 2 - 2.5, cy - s / 6, x + s / 2 + 2.5, cy + s / 4 - 1), fill=bg)
        d.ellipse((x + s / 2 - 3, cy + s / 3 - 3, x + s / 2 + 3, cy + s / 3 + 3), fill=bg)
        x += icon_w
    d.text((x, pad_y - 4), text, font=f, fill=fg)
    return img


def with_alpha(img, a):
    if a >= 0.999:
        return img
    r, g, b, al = img.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))


class El:
    """Sahnede animasyonla giren bir öğe."""

    def __init__(self, img, x, y, delay=0.0, dur=0.55, dy=60, center=False):
        self.img = img
        self.x = (W - img.width) // 2 if center else x
        self.y = y + Y_SHIFT
        self.delay = delay
        self.dur = dur
        self.dy = dy

    def draw(self, frame, t_local, out_alpha):
        p = ease_out_cubic((t_local - self.delay) / self.dur)
        if p <= 0:
            return
        a = p * out_alpha
        y = int(self.y + (1 - p) * self.dy)
        frame.alpha_composite(with_alpha(self.img, a), (int(self.x), y))


# ---------------------------------------------------------------- arka plan

def make_background():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        c = tuple(int(NAVY_TOP[i] + (NAVY_BOT[i] - NAVY_TOP[i]) * k) for i in range(3))
        d.line((0, y, W, y), fill=c)
    return bg.convert("RGBA")


def make_clouds():
    """Yavaşça kayacak bulutlu doku (genişliği ekranın 2 katı)."""
    random.seed(3)
    img = Image.new("RGBA", (W * 2, 900), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(60):
        cx = random.randint(-100, W * 2 + 100)
        cy = random.randint(80, 600)
        rx = random.randint(140, 380)
        ry = random.randint(60, 150)
        g = random.randint(70, 120)
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(g, g + 10, g + 30, random.randint(25, 60)))
    return img.filter(ImageFilter.GaussianBlur(60))


class Rain:
    def __init__(self, n=170):
        random.seed(11)
        self.drops = [
            [random.uniform(0, W + 300), random.uniform(0, H), random.uniform(28, 60), random.uniform(0.25, 1.0)]
            for _ in range(n)
        ]

    def draw(self, frame, dt):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for drop in self.drops:
            x, y, spd, depth = drop
            length = 30 + 50 * depth
            dx, dy = -0.22 * length, length
            d.line((x, y, x + dx, y + dy), fill=(190, 210, 240, int(40 + 70 * depth)), width=1 if depth < 0.6 else 2)
            drop[1] += spd * depth * 60 * dt * 1.6
            drop[0] -= spd * depth * 60 * dt * 0.35
            if drop[1] > H:
                drop[1] = random.uniform(-200, -20)
                drop[0] = random.uniform(0, W + 300)
        frame.alpha_composite(layer)


# ---------------------------------------------------------------- sahneler

F_LABEL = font("Inter-ExtraBold", 40)
F_BODY = font("Inter-SemiBold", 50)
F_SMALL = font("Inter-Medium", 38)


def label(text):
    """Sarı küçük başlık + altında çizgi."""
    t = text_image([text], F_LABEL, YELLOW)
    img = Image.new("RGBA", (t.width, t.height + 22), (0, 0, 0, 0))
    img.alpha_composite(t)
    ImageDraw.Draw(img).rectangle((0, t.height + 8, 90, t.height + 15), fill=YELLOW)
    return img


def build_scenes():
    scenes = {}

    # 1) HOOK
    els = []
    els.append(El(chip("SARI KOD", (20, 20, 20), YELLOW, size=40, icon="warn"), MARGIN, 520, 0.15))
    head = ["KASTAMONU'YA", "KUVVETLİ", "SAĞANAK UYARISI"]
    fh = fit_font(head, "InterDisplay-Black", 140, CONTENT_W)
    y = 640
    for i, line in enumerate(head):
        col = YELLOW if i == 1 else WHITE
        img = text_image([line], fh, col, line_gap=1.0)
        els.append(El(img, MARGIN, y, 0.3 + i * 0.14, dy=80))
        y += int(img.height * 0.98)
    sub = text_image(wrap("Meteoroloji Genel Müdürlüğü, Batı Karadeniz için uyarı yaptı.", F_BODY, CONTENT_W), F_BODY, SOFT)
    els.append(El(sub, MARGIN, y + 40, 0.9))
    scenes["hook"] = els

    # 2) NE ZAMAN
    els = [El(label("NE ZAMAN?"), MARGIN, 470, 0.05)]
    card_w, card_h = CONTENT_W, 300
    for i, (tag, day, hour) in enumerate(
        [("BAŞLIYOR", "4 Kasım Çarşamba", "12.00"), ("SONA ERİYOR", "5 Kasım Perşembe", "18.00")]
    ):
        card = rounded(card_w, card_h, 36, CARD, outline=(255, 255, 255, 40), width=2)
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, 14, card_h - 1), 7, fill=YELLOW)
        d.text((56, 42), tag, font=font("Inter-Bold", 34), fill=SOFT)
        d.text((56, 92), day, font=font("InterDisplay-ExtraBold", 66), fill=WHITE)
        d.text((56, 186), "saat " + hour, font=font("InterDisplay-Bold", 56), fill=YELLOW)
        els.append(El(card, MARGIN, 580 + i * (card_h + 40), 0.25 + i * 0.3))
    note = text_image(wrap("Yaklaşık 30 saat boyunca etkili olması bekleniyor.", F_BODY, CONTENT_W), F_BODY, WHITE)
    els.append(El(note, MARGIN, 580 + 2 * (card_h + 40) + 20, 1.0))
    scenes["when"] = els

    # 3) NEREDE
    els = [El(label("NEREDE?"), MARGIN, 470, 0.05)]
    big = ["Kastamonu'nun", "kuzey kesimleri"]
    fb = fit_font(big, "InterDisplay-Black", 120, CONTENT_W)
    img = text_image(big, fb, WHITE, line_gap=1.0)
    els.append(El(img, MARGIN, 580, 0.2, dy=80))
    y = 580 + img.height + 50
    t2 = text_image(wrap("Uyarı kapsamındaki diğer iller:", F_BODY, CONTENT_W), F_BODY, SOFT)
    els.append(El(t2, MARGIN, y, 0.6))
    y += t2.height + 30
    x = MARGIN
    for i, city in enumerate(["Zonguldak", "Bartın", "Düzce", "Sinop"]):
        c = chip(city, WHITE, (255, 255, 255, 34), size=44, pad_x=30, pad_y=18)
        if x + c.width > W - MARGIN:
            x = MARGIN
            y += c.height + 22
        els.append(El(c, x, y, 0.85 + i * 0.15, dy=40))
        x += c.width + 20
    scenes["where"] = els

    # 4) MİKTAR (sayı animasyonlu, aşağıda özel çizilir)
    els = [El(label("NE KADAR YAĞIŞ?"), MARGIN, 470, 0.05)]
    unit = text_image(["kilogram / metrekare"], font("InterDisplay-Bold", 64), YELLOW)
    els.append(El(unit, MARGIN, 900, 0.7))
    desc = text_image(
        wrap("Yer yer gök gürültülü ve kuvvetli sağanak şeklinde görülecek.", F_BODY, CONTENT_W), F_BODY, WHITE
    )
    els.append(El(desc, MARGIN, 1020, 1.0))
    scenes["amount"] = els

    # 5) RİSKLER
    els = [El(label("OLASI RİSKLER"), MARGIN, 440, 0.05)]
    items = ["Ani sel ve su baskını", "Yıldırım ve yerel dolu", "Heyelan", "Ağaç devrilmesi", "Çatı uçması"]
    fi = font("InterDisplay-Bold", 64)
    for i, it in enumerate(items):
        row = Image.new("RGBA", (CONTENT_W, 120), (0, 0, 0, 0))
        d = ImageDraw.Draw(row)
        d.rounded_rectangle((0, 0, CONTENT_W - 1, 119), 28, fill=CARD)
        d.ellipse((34, 44, 66, 76), fill=YELLOW)
        d.text((100, 22), it, font=fi, fill=WHITE)
        els.append(El(row, MARGIN, 560 + i * 140, 0.3 + i * 0.32, dy=50))
    scenes["risks"] = els

    # 6) ÖNERİLER
    els = [El(label("NELERE DİKKAT ETMELİ?"), MARGIN, 440, 0.05)]
    tips = [
        "Dere yataklarından uzak durun",
        "Araçlarınızı ağaç altına park etmeyin",
        "Zorunlu değilse yola çıkmayın",
        "Resmi uyarıları takip edin",
    ]
    ft = font("InterDisplay-SemiBold", 54)
    y = 560
    for i, tip in enumerate(tips):
        lines = wrap(tip, ft, CONTENT_W - 130)
        th = len(lines) * 66 + 70
        row = Image.new("RGBA", (CONTENT_W, th), (0, 0, 0, 0))
        d = ImageDraw.Draw(row)
        d.rounded_rectangle((0, 0, CONTENT_W - 1, th - 1), 28, fill=CARD)
        d.rounded_rectangle((26, th / 2 - 36, 98, th / 2 + 36), 18, fill=YELLOW)
        num = str(i + 1)
        fnum = font("InterDisplay-Black", 48)
        d.text((62 - fnum.getlength(num) / 2, th / 2 - 31), num, font=fnum, fill=(20, 20, 20))
        for j, l in enumerate(lines):
            d.text((126, 32 + j * 66), l, font=ft, fill=WHITE)
        els.append(El(row, MARGIN, y, 0.3 + i * 0.45, dy=50))
        y += th + 26
    scenes["tips"] = els

    # 7) KAPANIŞ
    els = []
    big = ["Dikkatli olun,", "güvende kalın."]
    fb = fit_font(big, "InterDisplay-Black", 120, CONTENT_W)
    img = text_image(big, fb, WHITE, line_gap=1.02, align="center", width=CONTENT_W)
    els.append(El(img, 0, 720, 0.1, center=True))
    src = text_image(["Kaynak: Meteoroloji Genel Müdürlüğü"], F_SMALL, SOFT, align="center", width=CONTENT_W)
    els.append(El(src, 0, 720 + img.height + 60, 0.6, center=True))
    follow = chip("Gelişmeler için takipte kalın", (20, 20, 20), YELLOW, size=40)
    els.append(El(follow, 0, 720 + img.height + 150, 0.9, center=True))
    scenes["outro"] = els
    return scenes


def draw_amount_number(frame, t_local, out_alpha):
    """21 – 50 sayısını sayarak gösterir."""
    p = ease_out_cubic((t_local - 0.2) / 1.2)
    if p <= 0:
        return
    a = min(1.0, (t_local - 0.2) / 0.4) * out_alpha
    lo = int(round(21 * p))
    hi = int(round(50 * p))
    f = font("InterDisplay-Black", 260)
    txt = f"{lo}–{hi}"
    img = text_image([txt], f, WHITE, line_gap=1.0)
    frame.alpha_composite(with_alpha(img, max(0.0, a)), (MARGIN - 8, 590 + Y_SHIFT + int((1 - p) * 40)))


# ---------------------------------------------------------------- sabit katman (üst bar + ilerleme)

def draw_chrome(frame, t):
    d = ImageDraw.Draw(frame)
    # üst sol: konum etiketi, yanıp sönen sarı nokta
    pulse = 0.55 + 0.45 * math.sin(t * 5)
    cx, cy = MARGIN + 14, 300
    r = 11
    d.ellipse((cx - r - 8 * pulse, cy - r - 8 * pulse, cx + r + 8 * pulse, cy + r + 8 * pulse),
              fill=(255, 196, 0, int(70 * (1 - pulse) + 20)))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YELLOW)
    d.text((cx + 30, cy - 24), "KASTAMONU", font=font("Inter-ExtraBold", 40), fill=WHITE)
    fd = font("Inter-SemiBold", 34)
    date = "3 KASIM 2026"
    d.text((W - MARGIN - fd.getlength(date), cy - 19), date, font=fd, fill=SOFT)
    d.line((MARGIN, cy + 50, W - MARGIN, cy + 50), fill=(255, 255, 255, 45), width=2)

    # alt: sahne göstergeleri (segmentli ilerleme)
    n = len(SCENES)
    gap = 12
    seg_w = (CONTENT_W - gap * (n - 1)) / n
    y = 1560
    for i, (_, s, e) in enumerate(SCENES):
        x0 = MARGIN + i * (seg_w + gap)
        d.rounded_rectangle((x0, y, x0 + seg_w, y + 8), 4, fill=(255, 255, 255, 50))
        prog = max(0.0, min(1.0, (t - s) / (e - s)))
        if prog > 0:
            d.rounded_rectangle((x0, y, x0 + seg_w * prog, y + 8), 4, fill=YELLOW)


# ---------------------------------------------------------------- ana döngü

def main():
    out = sys.argv[1]
    preview = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    bg = make_background()
    clouds = make_clouds()
    rain = Rain()
    scenes = build_scenes()
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(40):
        a = int(4 * i)
        vd.rectangle((i * 6, i * 6, W - i * 6, H - i * 6), outline=(0, 0, 0, max(0, 160 - a)), width=6)
    vignette = vignette.filter(ImageFilter.GaussianBlur(30))

    proc = None if preview else subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE,
    )
    total = int(DURATION * FPS)
    dt = 1 / FPS
    for fi in range(total):
        t = fi / FPS
        frame = bg.copy()
        # bulutlar yavaşça kayar
        off = int((t * 18) % W)
        frame.alpha_composite(clouds.crop((off, 0, off + W, 900)), (0, 0))
        rain.draw(frame, dt)

        for name, s, e in SCENES:
            if s <= t < e:
                tl = t - s
                out_alpha = 1.0 - ease_in_out((t - (e - 0.4)) / 0.4) if name != "outro" else 1.0
                if name == "outro":
                    out_alpha = 1.0 - ease_in_out((t - (e - 0.8)) / 0.8)
                if name == "amount":
                    draw_amount_number(frame, tl, out_alpha)
                for el in scenes[name]:
                    el.draw(frame, tl, out_alpha)

        draw_chrome(frame, t)
        frame.alpha_composite(vignette)

        # şimşek: kısa, çift parlama
        for ft in FLASHES:
            k = t - ft
            if 0 <= k < 0.45:
                inten = max(0.0, 1 - k / 0.12) * 0.55 + (0.35 if 0.18 < k < 0.26 else 0)
                if inten > 0:
                    flash = Image.new("RGBA", (W, H), (220, 230, 255, int(255 * min(inten, 0.8))))
                    frame.alpha_composite(flash)

        # genel giriş/çıkış karartma
        fade = min(1.0, t / 0.3, (DURATION - t) / 0.5)
        if fade < 1:
            frame.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - max(0, fade))))))

        if preview:
            if any(abs(t - p) < dt / 2 for p in preview):
                frame.convert("RGB").save(f"{out}_{t:05.2f}.png")
            continue
        proc.stdin.write(frame.convert("RGB").tobytes())
        if fi % 150 == 0:
            print(f"kare {fi}/{total}", flush=True)
    if proc:
        proc.stdin.close()
        proc.wait()


if __name__ == "__main__":
    main()
