#!/usr/bin/env python3
"""Bentaka marka kiti üretici: vektör logolar, PNG'ler, sosyal medya görselleri,
web ikonları, CMYK PDF/EPS baskı dosyaları ve renk paleti."""
import os, math, struct, json, zipfile, shutil, hashlib
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import cairosvg
from PIL import Image
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfgen.canvas import FILL_EVEN_ODD, FILL_NON_ZERO

SP = '/tmp/claude-0/-home-user--phone-14-pro-max/569bf7ec-9978-5eab-8205-b564a734360e/scratchpad'
OUT = os.path.join(SP, 'Bentaka-Marka-Kiti')
FONTDIR = os.path.join(SP, 'fonts')

SLOGAN = 'Future, first.'
SLOGAN_TR = 'Geleceği ilk sen gör.'

FONTS = {
    'sora700': f'{FONTDIR}/Sora-Bold.ttf',
    'sora600': f'{FONTDIR}/Sora-SemiBold.ttf',
    'inter400': '/usr/share/fonts/opentype/inter/Inter-Regular.otf',
    'inter600': '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf',
    'mono500': '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf',
}

COLORS = {
    'gece':   {'name': 'Gece',   'hex': '#0B0E14', 'cmyk': (70, 55, 35, 95), 'role': 'Ana zemin'},
    'grafit': {'name': 'Grafit', 'hex': '#1A1F2B', 'cmyk': (82, 70, 48, 55), 'role': 'Kartlar ve yüzeyler, açık zeminde ikincil metin'},
    'celik':  {'name': 'Çelik',  'hex': '#8A93A6', 'cmyk': (48, 36, 24, 6),  'role': 'Koyu zeminde ikincil metin ve çizgiler'},
    'bulut':  {'name': 'Bulut',  'hex': '#F3F5F8', 'cmyk': (4, 2, 1, 0),     'role': 'Koyu zeminde ana metin, açık zemin'},
    'volt':   {'name': 'Volt',   'hex': '#C6FF3D', 'cmyk': (25, 0, 85, 0),   'role': 'Ana vurgu: logo noktası, etiketler'},
    'iyon':   {'name': 'İyon',   'hex': '#5B7CFF', 'cmyk': (68, 52, 0, 0),   'role': 'İkincil vurgu: bağlantı, grafik, veri'},
    'siyah':  {'name': 'Siyah',  'hex': '#000000', 'cmyk': (0, 0, 0, 100),   'role': 'Tek renk baskı'},
    'beyaz':  {'name': 'Beyaz',  'hex': '#FFFFFF', 'cmyk': (0, 0, 0, 0),     'role': 'Ters (koyu zemin) tek renk'},
}
PALETTE_KEYS = ['gece', 'grafit', 'celik', 'bulut', 'volt', 'iyon']

def rgb(key):
    h = COLORS[key]['hex'].lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# ---------------------------------------------------------------- geometry
K = 0.5522847498

def circle_cmds(cx, cy, r):
    k = K * r
    return [('M', cx + r, cy),
            ('C', cx + r, cy + k, cx + k, cy + r, cx, cy + r),
            ('C', cx - k, cy + r, cx - r, cy + k, cx - r, cy),
            ('C', cx - r, cy - k, cx - k, cy - r, cx, cy - r),
            ('C', cx + k, cy - r, cx + r, cy - k, cx + r, cy),
            ('Z',)]

def rect_cmds(x, y, w, h):
    return [('M', x, y), ('L', x + w, y), ('L', x + w, y + h), ('L', x, y + h), ('Z',)]

def rrect_cmds(x, y, w, h, r, top_only=False):
    k = K * r
    c = [('M', x + r, y), ('L', x + w - r, y),
         ('C', x + w - r + k, y, x + w, y + r - k, x + w, y + r)]
    if top_only:
        c += [('L', x + w, y + h), ('L', x, y + h)]
    else:
        c += [('L', x + w, y + h - r),
              ('C', x + w, y + h - r + k, x + w - r + k, y + h, x + w - r, y + h),
              ('L', x + r, y + h),
              ('C', x + r - k, y + h, x, y + h - r + k, x, y + h - r)]
    c += [('L', x, y + r), ('C', x, y + r - k, x + r - k, y, x + r, y), ('Z',)]
    return c

def tf(cmds, s, dx, dy):
    out = []
    for c in cmds:
        if c[0] == 'Z':
            out.append(c)
            continue
        n = [c[0]]
        for j in range(1, len(c), 2):
            n += [c[j] * s + dx, c[j + 1] * s + dy]
        out.append(tuple(n))
    return out

def bbox(cmds):
    xs, ys = [], []
    for c in cmds:
        if c[0] == 'Z':
            continue
        xs += c[1::2]
        ys += c[2::2]
    return min(xs), min(ys), max(xs), max(ys)

def place(items, s, dx, dy):
    return [dict(it, cmds=tf(it['cmds'], s, dx, dy)) for it in items]

# ---------------------------------------------------------------- text → paths
class CmdPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.cmds = []
    def _moveTo(self, p): self.cmds.append(('M', p[0], p[1]))
    def _lineTo(self, p): self.cmds.append(('L', p[0], p[1]))
    def _curveToOne(self, a, b, c): self.cmds.append(('C', a[0], a[1], b[0], b[1], c[0], c[1]))
    def _closePath(self): self.cmds.append(('Z',))
    def _endPath(self): pass

_fc = {}
def font(key):
    if key not in _fc:
        path = FONTS[key]
        tt = TTFont(path)
        face = hb.Face(hb.Blob.from_file_path(path))
        _fc[key] = dict(gs=tt.getGlyphSet(), order=tt.getGlyphOrder(), hb=hb.Font(face), upem=face.upem)
    return _fc[key]

def text_glyphs(key, text, size, x=0, y=0, tracking=0.0, anchor='start'):
    f = font(key)
    s = size / f['upem']
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(f['hb'], buf, {'kern': True, 'liga': True})
    infos, poss = buf.glyph_infos, buf.glyph_positions
    advs = []
    for i, p in enumerate(poss):
        a = p.x_advance * s
        if i < len(poss) - 1:
            a += tracking * size
        advs.append(a)
    width = sum(advs)
    if anchor == 'middle':
        x -= width / 2
    elif anchor == 'end':
        x -= width
    glyphs, penx = [], x
    for inf, p, a in zip(infos, poss, advs):
        pen = CmdPen(f['gs'])
        f['gs'][f['order'][inf.codepoint]].draw(pen)
        ox, oy = penx + p.x_offset * s, y - p.y_offset * s
        g = []
        for c in pen.cmds:
            if c[0] == 'Z':
                g.append(c)
                continue
            n = [c[0]]
            for j in range(1, len(c), 2):
                n += [ox + c[j] * s, oy - c[j + 1] * s]
            g.append(tuple(n))
        glyphs.append(g)
        penx += a
    return glyphs, width

def text_cmds(*a, **kw):
    glyphs, w = text_glyphs(*a, **kw)
    return [c for g in glyphs for c in g], w

def text_item(key, text, size, x, y, color, **kw):
    cmds, w = text_cmds(key, text, size, x, y, **kw)
    return dict(cmds=cmds, fill=color) if cmds else None

# ---------------------------------------------------------------- brand marks
MARK_W_RATIO = 90 / 104  # monogram content box: x 18..108, y 8..112

def mark_items(x, y, height, body, dot):
    s = height / 104.0
    dx, dy = x - 18 * s, y - 8 * s
    return [dict(cmds=tf(rrect_cmds(18, 8, 24, 104, 5), s, dx, dy), fill=body),
            dict(cmds=tf(circle_cmds(68, 72, 40) + circle_cmds(68, 72, 16), s, dx, dy), fill=body, rule='evenodd'),
            dict(cmds=tf(circle_cmds(68, 72, 8), s, dx, dy), fill=dot)]

def wordmark(F=100):
    cmds, _ = text_cmds('sora700', 'bentaka', F, 0, 0, tracking=-0.045)
    return cmds

def lockup(body, dot, text, F=100):
    """Yatay logo: monogram + yazı. Dönen koordinatlar (0,0)'dan başlar, kenar boşluğu yok."""
    wm = wordmark(F)
    x0, y0, x1, y1 = bbox(wm)
    bh = -y0                   # 'b' harfinin taban çizgisi üstündeki yüksekliği
    mh = bh * 1.12
    mw = mh * MARK_W_RATIO
    gap = F * 0.30
    top, bottom = -mh, max(y1, 0)
    items = mark_items(0, 0, mh, body, dot)
    items.append(dict(cmds=tf(wm, 1, mw + gap - x0, -top), fill=text))
    return items, mw + gap + (x1 - x0), bottom - top

def vlockup(body, dot, text, F=100):
    wm = wordmark(F)
    x0, y0, x1, y1 = bbox(wm)
    ww, bh = x1 - x0, -y0
    mh = bh * 2.0
    mw = mh * MARK_W_RATIO
    gap = bh * 0.60
    W = max(ww, mw)
    items = mark_items((W - mw) / 2, 0, mh, body, dot)
    items.append(dict(cmds=tf(wm, 1, (W - ww) / 2 - x0, mh + gap + bh), fill=text))
    return items, W, mh + gap + bh + max(y1, 0)

def monogram(body, dot):
    mh = 104.0
    return mark_items(0, 0, mh, body, dot), mh * MARK_W_RATIO, mh

def with_margin(items, w, h, ratio):
    m = h * ratio
    return place(items, 1, m, m), w + 2 * m, h + 2 * m

# ---------------------------------------------------------------- writers
def d_of(cmds):
    out = []
    for c in cmds:
        if c[0] == 'Z':
            out.append('Z')
        else:
            out.append(c[0] + ' '.join(f'{v:.2f}' for v in c[1:]))
    return ''.join(out)

def svg_doc(items, w, h, title='Bentaka', extra='', px=None):
    pw, ph = px if px else (round(w, 2), round(h, 2))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw}" height="{ph}" viewBox="0 0 {w:.2f} {h:.2f}">',
           f'<title>{title}</title>']
    for it in items:
        if it is None:
            continue
        rule = ' fill-rule="evenodd"' if it.get('rule') == 'evenodd' else ''
        out.append(f'<path d="{d_of(it["cmds"])}" fill="{COLORS[it["fill"]]["hex"]}"{rule}/>')
    out.append(extra)
    out.append('</svg>')
    return '\n'.join(out)

def write(path, data, mode='w'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as f:
        f.write(data)

def png(items, w, h, path, out_w, out_h=None, extra='', title='Bentaka'):
    out_h = out_h or round(out_w * h / w)
    svg = svg_doc(items, w, h, title=title, extra=extra, px=(out_w, out_h))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cairosvg.svg2png(bytestring=svg.encode('utf-8'), write_to=path, output_width=out_w, output_height=out_h)

def pdf_cmyk(items, w, h, path, title, scale=1.0):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    W, H = w * scale, h * scale
    c = rl_canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(title)
    c.setAuthor('Bentaka')
    c.setCreator('Bentaka marka kiti')
    for it in items:
        if it is None:
            continue
        p = c.beginPath()
        for cmd in it['cmds']:
            if cmd[0] == 'M':
                p.moveTo(cmd[1] * scale, H - cmd[2] * scale)
            elif cmd[0] == 'L':
                p.lineTo(cmd[1] * scale, H - cmd[2] * scale)
            elif cmd[0] == 'C':
                p.curveTo(cmd[1] * scale, H - cmd[2] * scale, cmd[3] * scale, H - cmd[4] * scale,
                          cmd[5] * scale, H - cmd[6] * scale)
            else:
                p.close()
        cc, mm, yy, kk = COLORS[it['fill']]['cmyk']
        c.setFillColorCMYK(cc / 100, mm / 100, yy / 100, kk / 100)
        c.drawPath(p, stroke=0, fill=1,
                   fillMode=FILL_EVEN_ODD if it.get('rule') == 'evenodd' else FILL_NON_ZERO)
    c.showPage()
    c.save()

def eps_cmyk(items, w, h, path, title):
    L = ['%!PS-Adobe-3.0 EPSF-3.0',
         f'%%BoundingBox: 0 0 {math.ceil(w)} {math.ceil(h)}',
         f'%%HiResBoundingBox: 0 0 {w:.3f} {h:.3f}',
         f'%%Title: {title}', '%%Creator: Bentaka marka kiti', '%%LanguageLevel: 2',
         '%%DocumentData: Clean7Bit', '%%Pages: 1', '%%EndComments', '%%Page: 1 1', 'gsave']
    for it in items:
        if it is None:
            continue
        cc, mm, yy, kk = COLORS[it['fill']]['cmyk']
        L.append(f'{cc/100:.3f} {mm/100:.3f} {yy/100:.3f} {kk/100:.3f} setcmykcolor newpath')
        for cmd in it['cmds']:
            if cmd[0] == 'M':
                L.append(f'{cmd[1]:.3f} {h-cmd[2]:.3f} moveto')
            elif cmd[0] == 'L':
                L.append(f'{cmd[1]:.3f} {h-cmd[2]:.3f} lineto')
            elif cmd[0] == 'C':
                L.append(f'{cmd[1]:.3f} {h-cmd[2]:.3f} {cmd[3]:.3f} {h-cmd[4]:.3f} {cmd[5]:.3f} {h-cmd[6]:.3f} curveto')
            else:
                L.append('closepath')
        L.append('eofill' if it.get('rule') == 'evenodd' else 'fill')
    L += ['grestore', 'showpage', '%%EOF']
    write(path, '\n'.join(L) + '\n')

# ---------------------------------------------------------------- scenes
def bg_item(w, h, color):
    return dict(cmds=rect_cmds(0, 0, w, h), fill=color)

def dotgrid_item(w, h, color):
    sp = w / 48
    r = sp * 0.065
    nx, ny = int(w // sp) + 2, int(h // sp) + 2
    ox, oy = (w - (nx - 1) * sp) / 2, (h - (ny - 1) * sp) / 2
    cmds = []
    for i in range(nx):
        for j in range(ny):
            cmds += circle_cmds(ox + i * sp, oy + j * sp, r)
    return dict(cmds=cmds, fill=color)

def slogan_items(size, cx, top):
    """Slogan; sondaki nokta Volt renginde (logodaki noktanın yankısı)."""
    glyphs, _ = text_glyphs('sora600', SLOGAN, size, 0, 0, tracking=-0.01, anchor='middle')
    allc = [c for g in glyphs for c in g if g]
    x0, y0, x1, y1 = bbox(allc)
    body = [c for g in glyphs[:-1] for c in g]
    dot = glyphs[-1]
    items = [dict(cmds=tf(body, 1, cx, top - y0), fill='celik')]
    if dot:
        items.append(dict(cmds=tf(dot, 1, cx, top - y0), fill='volt'))
    return items, y1 - y0

def cover(w, h, safe_w, safe_h, lock_ratio=0.40, grid=True):
    items = [bg_item(w, h, 'gece')]
    if grid:
        items.append(dotgrid_item(w, h, 'grafit'))
    L, lw, lh = lockup('bulut', 'volt', 'bulut')
    s = safe_h * lock_ratio / lh
    if lw * s > safe_w * 0.86:
        s = safe_w * 0.86 / lw
    lw2, lh2 = lw * s, lh * s
    gap = lh2 * 0.42
    # slogan yüksekliğini ölç
    _, sh = slogan_items(lh2 * 0.30, 0, 0)
    block = lh2 + gap + sh
    top = (h - block) / 2
    items += place(L, s, (w - lw2) / 2, top)
    sl, _ = slogan_items(lh2 * 0.30, w / 2, top + lh2 + gap)
    return items + sl

def profile(size, ratio=0.52, bg='gece', body='bulut', dot='volt'):
    items = [bg_item(size, size, bg)] if bg else []
    mh = size * ratio
    mw = mh * MARK_W_RATIO
    return items + mark_items((size - mw) / 2, (size - mh) / 2, mh, body, dot)

ICONS = {
    'haber': '<path d="M4 5h12v14H6a2 2 0 0 1-2-2V5z"/><path d="M16 9h4v8a2 2 0 0 1-2 2h-2"/><path d="M7.5 9h5"/><path d="M7.5 13h5"/>',
    'inceleme': '<circle cx="11" cy="11" r="6"/><path d="M15.5 15.5L20 20"/>',
    'ipucu': '<path d="M9 18h6"/><path d="M10 21h4"/><path d="M12 3a6 6 0 0 0-3.8 10.6c.7.6 1 1.4 1 2.4h5.6c0-1 .3-1.8 1-2.4A6 6 0 0 0 12 3z"/>',
    'kiyas': '<rect x="3" y="5" width="7" height="14" rx="1.5"/><rect x="14" y="5" width="7" height="14" rx="1.5"/>',
}

def icon_svg(name, cx, cy, size, color):
    s = size / 24
    return (f'<g transform="translate({cx - size/2:.2f},{cy - size/2:.2f}) scale({s:.4f})" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')

# ---------------------------------------------------------------- build
MANIFEST = []
def reg(path, folder, mime):
    MANIFEST.append(dict(path=path, folder=folder, mime=mime))

def build_logos():
    variants = {
        'koyu-zemin': ('bulut', 'volt', 'bulut'),
        'acik-zemin': ('gece', 'iyon', 'gece'),
        'siyah': ('siyah', 'siyah', 'siyah'),
        'beyaz': ('beyaz', 'beyaz', 'beyaz'),
    }
    svgdir, pngdir, prdir = f'{OUT}/01-Logo/SVG', f'{OUT}/01-Logo/PNG', f'{OUT}/01-Logo/Baski-CMYK'
    for v, (b, d, t) in variants.items():
        # yatay
        it, w, h = with_margin(*lockup(b, d, t), 0.12)
        n = f'bentaka-logo-yatay-{v}'
        write(f'{svgdir}/{n}.svg', svg_doc(it, w, h, title='Bentaka logo'))
        reg(f'{svgdir}/{n}.svg', 'logo_svg', 'image/svg+xml')
        png(it, w, h, f'{pngdir}/{n}.png', 3000)
        reg(f'{pngdir}/{n}.png', 'logo_png', 'image/png')
        # monogram
        it, w, h = with_margin(*monogram(b, d), 0.12)
        n = f'bentaka-monogram-{v}'
        write(f'{svgdir}/{n}.svg', svg_doc(it, w, h, title='Bentaka monogram'))
        reg(f'{svgdir}/{n}.svg', 'logo_svg', 'image/svg+xml')
        png(it, w, h, f'{pngdir}/{n}.png', round(2000 * w / h), 2000)
        reg(f'{pngdir}/{n}.png', 'logo_png', 'image/png')
        # dikey (yalnızca renkli iki sürüm)
        if v in ('koyu-zemin', 'acik-zemin'):
            it, w, h = with_margin(*vlockup(b, d, t), 0.10)
            n = f'bentaka-logo-dikey-{v}'
            write(f'{svgdir}/{n}.svg', svg_doc(it, w, h, title='Bentaka logo dikey'))
            reg(f'{svgdir}/{n}.svg', 'logo_svg', 'image/svg+xml')
            png(it, w, h, f'{pngdir}/{n}.png', 2000)
            reg(f'{pngdir}/{n}.png', 'logo_png', 'image/png')

    # baskı: CMYK PDF + EPS
    prints = []
    it, w, h = with_margin(*lockup('gece', 'iyon', 'gece'), 0.12)
    prints.append(('bentaka-logo-yatay-acik-zemin-CMYK', it, w, h))
    it, w, h = with_margin(*lockup('bulut', 'volt', 'bulut'), 0.25)
    prints.append(('bentaka-logo-yatay-koyu-zeminli-CMYK', [bg_item(w, h, 'gece')] + it, w, h))
    it, w, h = with_margin(*lockup('siyah', 'siyah', 'siyah'), 0.12)
    prints.append(('bentaka-logo-yatay-siyah-CMYK', it, w, h))
    it, w, h = with_margin(*monogram('gece', 'iyon'), 0.12)
    prints.append(('bentaka-monogram-acik-zemin-CMYK', it, w, h))
    it, w, h = with_margin(*monogram('bulut', 'volt'), 0.25)
    prints.append(('bentaka-monogram-koyu-zeminli-CMYK', [bg_item(w, h, 'gece')] + it, w, h))
    it, w, h = with_margin(*monogram('siyah', 'siyah'), 0.12)
    prints.append(('bentaka-monogram-siyah-CMYK', it, w, h))
    for n, it, w, h in prints:
        sc = 2.0  # ~ yatay logo 400 pt genişlik
        pdf_cmyk(it, w, h, f'{prdir}/{n}.pdf', title=n, scale=sc)
        reg(f'{prdir}/{n}.pdf', 'logo_print', 'application/pdf')
        eps_cmyk(place(it, sc, 0, 0), w * sc, h * sc, f'{prdir}/{n}.eps', title=n)
        reg(f'{prdir}/{n}.eps', 'logo_print', 'application/postscript')

def build_social():
    S = f'{OUT}/02-Sosyal-Medya'
    def prof(path, folder, size):
        png(profile(size), size, size, path, size, size)
        reg(path, folder, 'image/png')
    def cov(path, folder, w, h, sw, shh, ratio=0.40):
        png(cover(w, h, sw, shh, ratio), w, h, path, w, h)
        reg(path, folder, 'image/png')

    prof(f'{S}/Instagram/instagram-profil-1080x1080.png', 'sm_instagram', 1080)
    for name in ['haber', 'inceleme', 'ipucu', 'kiyas']:
        p = f'{S}/Instagram/instagram-one-cikan-{name}-1080x1920.png'
        png([bg_item(1080, 1920, 'gece')], 1080, 1920, p, 1080, 1920,
            extra=icon_svg(name, 540, 960, 400, COLORS['volt']['hex']))
        reg(p, 'sm_instagram', 'image/png')

    prof(f'{S}/Facebook/facebook-profil-1080x1080.png', 'sm_facebook', 1080)
    cov(f'{S}/Facebook/facebook-kapak-1640x624.png', 'sm_facebook', 1640, 624, 1000, 480)

    prof(f'{S}/X/x-profil-400x400.png', 'sm_x', 400)
    cov(f'{S}/X/x-kapak-1500x500.png', 'sm_x', 1500, 500, 1100, 330, 0.42)

    prof(f'{S}/YouTube/youtube-profil-800x800.png', 'sm_youtube', 800)
    cov(f'{S}/YouTube/youtube-banner-2560x1440.png', 'sm_youtube', 2560, 1440, 1235, 338, 0.55)
    p = f'{S}/YouTube/youtube-filigran-150x150.png'
    png(profile(150, ratio=0.80, bg=None), 150, 150, p, 150, 150)
    reg(p, 'sm_youtube', 'image/png')

    prof(f'{S}/LinkedIn/linkedin-logo-400x400.png', 'sm_linkedin', 400)
    cov(f'{S}/LinkedIn/linkedin-kapak-1128x191.png', 'sm_linkedin', 1128, 191, 900, 160, 0.44)

    prof(f'{S}/TikTok/tiktok-profil-1080x1080.png', 'sm_tiktok', 1080)
    prof(f'{S}/WhatsApp-Telegram/whatsapp-telegram-profil-640x640.png', 'sm_whatsapp', 640)

def build_email():
    E = f'{OUT}/03-E-posta'
    p = f'{E}/eposta-profil-512x512.png'
    png(profile(512), 512, 512, p, 512, 512)
    reg(p, 'email', 'image/png')
    for name, bgc, b, d, t in [('eposta-imza-logo-600x160.png', 'beyaz', 'gece', 'iyon', 'gece'),
                               ('eposta-imza-logo-koyu-600x160.png', 'gece', 'bulut', 'volt', 'bulut')]:
        W, H = 600, 160
        L, lw, lh = lockup(b, d, t)
        s = H * 0.46 / lh
        items = [bg_item(W, H, bgc)] + place(L, s, (W - lw * s) / 2, (H - lh * s) / 2)
        png(items, W, H, f'{E}/{name}', W, H)
        reg(f'{E}/{name}', 'email', 'image/png')

def build_web():
    D = f'{OUT}/04-Web'
    # favicon.svg: yuvarlak köşeli Gece kare
    sz = 64
    mh = sz * 0.60
    mw = mh * MARK_W_RATIO
    fav = [dict(cmds=rrect_cmds(0, 0, sz, sz, sz * 0.22), fill='gece')] + \
        mark_items((sz - mw) / 2, (sz - mh) / 2, mh, 'bulut', 'volt')
    write(f'{D}/favicon.svg', svg_doc(fav, sz, sz, title='Bentaka'))
    reg(f'{D}/favicon.svg', 'web', 'image/svg+xml')
    tmp = f'{SP}/build/_fav256.png'
    png(fav, sz, sz, tmp, 256, 256)
    Image.open(tmp).save(f'{D}/favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    reg(f'{D}/favicon.ico', 'web', 'image/x-icon')
    for name, size in [('apple-touch-icon-180x180.png', 180), ('icon-192x192.png', 192), ('icon-512x512.png', 512)]:
        png(profile(size, ratio=0.56), size, size, f'{D}/{name}', size, size)
        reg(f'{D}/{name}', 'web', 'image/png')
    png(cover(1200, 630, 1000, 480), 1200, 630, f'{D}/og-paylasim-gorseli-1200x630.png', 1200, 630)
    reg(f'{D}/og-paylasim-gorseli-1200x630.png', 'web', 'image/png')

def build_palette():
    P = f'{OUT}/05-Renk-Paleti'
    W, H = 2400, 1560
    items = [bg_item(W, H, 'bulut')]
    items.append(text_item('sora600', 'Bentaka renk paleti', 72, 120, 190, 'gece', tracking=-0.02))
    items.append(text_item('inter400', 'Ekran için HEX ve RGB, baskı için CMYK (kuşe kâğıt) değerleri.', 32, 120, 252, 'grafit'))
    cw, ch, gx, gy, top = 688, 520, 48, 48, 320
    for i, key in enumerate(PALETTE_KEYS):
        c = COLORS[key]
        x = 120 + (i % 3) * (cw + gx)
        y = top + (i // 3) * (ch + gy)
        items.append(dict(cmds=rrect_cmds(x, y, cw, ch, 28), fill='beyaz'))
        if key == 'bulut':
            items.append(dict(cmds=rrect_cmds(x, y, cw, 300, 28, top_only=True), fill='celik'))
            items.append(dict(cmds=rrect_cmds(x + 2, y + 2, cw - 4, 296, 26, top_only=True), fill=key))
        else:
            items.append(dict(cmds=rrect_cmds(x, y, cw, 300, 28, top_only=True), fill=key))
        txt = 'gece' if key in ('bulut', 'volt', 'iyon', 'celik') else 'bulut'
        items.append(text_item('sora600', c['name'], 48, x + 36, y + 264, txt, tracking=-0.01))
        r_, g_, b_ = rgb(key)
        cc, mm, yy, kk = c['cmyk']
        rows = [('HEX', c['hex']), ('RGB', f'{r_}  {g_}  {b_}'), ('CMYK', f'{cc}  {mm}  {yy}  {kk}')]
        for j, (lab, val) in enumerate(rows):
            yy_ = y + 356 + j * 44
            items.append(text_item('mono500', lab, 26, x + 36, yy_, 'grafit'))
            items.append(text_item('mono500', val, 26, x + 156, yy_, 'gece'))
        items.append(text_item('inter400', c['role'], 24, x + 36, y + 488, 'grafit'))
    items.append(text_item('inter400', 'CMYK değerleri kuşe kâğıt baskı için önerilir; baskıdan önce matbaadan prova isteyin. '
                           'Volt ve İyon ekranda baskıdan daha canlı görünür.', 26, 120, 1480, 'grafit'))
    png(items, W, H, f'{P}/bentaka-renk-paleti.png', W, H)
    reg(f'{P}/bentaka-renk-paleti.png', 'palette', 'image/png')
    pdf_cmyk(items, W, H, f'{P}/bentaka-renk-paleti-CMYK.pdf', 'Bentaka renk paleti (CMYK)', scale=842 / W)
    reg(f'{P}/bentaka-renk-paleti-CMYK.pdf', 'palette', 'application/pdf')

    # Adobe Swatch Exchange
    def nb(n):
        return struct.pack('>H', len(n) + 1) + (n + '\0').encode('utf-16-be')
    def blk(t, data):
        return struct.pack('>HI', t, len(data)) + data
    blocks = [blk(0xC001, nb('Bentaka'))]
    for key in PALETTE_KEYS:
        c = COLORS[key]
        r_, g_, b_ = rgb(key)
        blocks.append(blk(0x0001, nb(f"{c['name']} RGB") + b'RGB ' + struct.pack('>fff', r_ / 255, g_ / 255, b_ / 255) + struct.pack('>H', 0)))
        cc, mm, yy, kk = c['cmyk']
        blocks.append(blk(0x0001, nb(f"{c['name']} CMYK") + b'CMYK' + struct.pack('>ffff', cc / 100, mm / 100, yy / 100, kk / 100) + struct.pack('>H', 0)))
    blocks.append(blk(0xC002, b''))
    write(f'{P}/bentaka-renkler.ase', b'ASEF' + struct.pack('>HHI', 1, 0, len(blocks)) + b''.join(blocks), 'wb')
    reg(f'{P}/bentaka-renkler.ase', 'palette', 'application/octet-stream')

    lines = ['BENTAKA — RENK KODLARI', '=' * 60, '',
             f"{'Renk':<8}{'HEX':<10}{'RGB':<15}{'CMYK (kuşe)':<18}Görev", '-' * 60]
    for key in PALETTE_KEYS:
        c = COLORS[key]
        r_, g_, b_ = rgb(key)
        lines.append(f"{c['name']:<8}{c['hex']:<10}{f'{r_} {g_} {b_}':<15}{' '.join(str(v) for v in c['cmyk']):<18}{c['role']}")
    lines += ['', 'Tek renk baskı: Siyah = C0 M0 Y0 K100, ters kullanım = Beyaz.',
              'Kullanım oranı: Gece %60 · Bulut %20 · Grafit %10 · Volt %7 · İyon %3',
              'Kural: Volt açık zeminde yazı rengi olarak kullanılmaz.', '',
              'CSS değişkenleri:', ':root {']
    for key in PALETTE_KEYS:
        lines.append(f"  --bentaka-{key}: {COLORS[key]['hex']};")
    lines += ['}', '', f'Slogan: {SLOGAN}  (Türkçe: {SLOGAN_TR})',
              'Fontlar: Sora (başlık, logo) · Inter (metin) · JetBrains Mono (etiket, veri)']
    write(f'{P}/bentaka-renk-kodlari.txt', '\n'.join(lines) + '\n')
    reg(f'{P}/bentaka-renk-kodlari.txt', 'palette', 'text/plain')

def build_fonts():
    F = f'{OUT}/06-Fontlar'
    os.makedirs(F, exist_ok=True)
    z = f'{F}/Bentaka-Fontlar.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for n in ['Sora-Regular.ttf', 'Sora-SemiBold.ttf', 'Sora-Bold.ttf']:
            zf.write(f'{FONTDIR}/{n}', f'Sora/{n}')
        zf.write(f'{SP}/fontsrc/package/LICENSE', 'Sora/OFL-lisans.txt')
        for n in ['Inter-Regular.otf', 'Inter-Medium.otf', 'Inter-SemiBold.otf', 'Inter-Bold.otf']:
            zf.write(f'/usr/share/fonts/opentype/inter/{n}', f'Inter/{n}')
        zf.write('/usr/share/doc/fonts-inter/copyright', 'Inter/lisans.txt')
        for n in ['JetBrainsMono-Regular.ttf', 'JetBrainsMono-Medium.ttf']:
            zf.write(f'/usr/share/fonts/truetype/jetbrains-mono/{n}', f'JetBrains-Mono/{n}')
        zf.write('/usr/share/doc/fonts-jetbrains-mono/copyright', 'JetBrains-Mono/lisans.txt')
        zf.writestr('OKUBENI.txt', 'Bentaka marka fontları. Üçü de SIL Open Font License (OFL) ile ücretsizdir;\n'
                    'kişisel ve ticari kullanım serbesttir. Kurmak için .ttf / .otf dosyasına çift tıklayın.\n\n'
                    'Sora: logo ve başlıklar (600, 700)\nInter: metin (400, 600)\nJetBrains Mono: etiket ve veri (500)\n')
    reg(z, 'fonts', 'application/zip')

def export_svgs_for_guide():
    """Kılavuz sayfası için satır içi SVG'ler."""
    out = {}
    for key, args in {'yatay_koyu': ('bulut', 'volt', 'bulut'), 'yatay_acik': ('gece', 'iyon', 'gece')}.items():
        it, w, h = lockup(*args)
        out[key] = svg_doc(it, w, h).replace('<svg ', '<svg class="logo" ', 1)
    for key, args in {'dikey_koyu': ('bulut', 'volt', 'bulut'), 'dikey_acik': ('gece', 'iyon', 'gece')}.items():
        it, w, h = vlockup(*args)
        out[key] = svg_doc(it, w, h).replace('<svg ', '<svg class="logo" ', 1)
    for key, args in {'mono_koyu': ('bulut', 'volt'), 'mono_acik': ('gece', 'iyon'), 'mono_siyah': ('siyah', 'siyah')}.items():
        it, w, h = monogram(*args)
        out[key] = svg_doc(it, w, h).replace('<svg ', '<svg class="logo" ', 1)
    write(f'{SP}/build/guide_svgs.json', json.dumps(out))

if __name__ == '__main__':
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    build_logos()
    build_social()
    build_email()
    build_web()
    build_palette()
    build_fonts()
    export_svgs_for_guide()
    write(f'{SP}/build/manifest.json', json.dumps(MANIFEST, ensure_ascii=False, indent=1))
    print(len(MANIFEST), 'dosya')
