"""StitchAnatolia desen üretici: her desen için designs/<slug>/pattern.js yazar."""
import json, os

PAL = {
  'RD': {'dmc': '347',  'name': 'Salmon Very Dark',          'hex': '#B8312F', 'sym': '▲'},
  'NV': {'dmc': '311',  'name': 'Navy Blue Medium',          'hex': '#1F3B5C', 'sym': '●'},
  'GD': {'dmc': '729',  'name': 'Old Gold Medium',           'hex': '#CFA14A', 'sym': '◆'},
  'CR': {'dmc': '712',  'name': 'Cream',                     'hex': '#F3EBD3', 'sym': '○'},
  'BR': {'dmc': '938',  'name': 'Coffee Brown Ultra Dark',   'hex': '#3A2214', 'sym': '■'},
  'TQ': {'dmc': '3809', 'name': 'Turquoise Very Dark',       'hex': '#3A7C82', 'sym': '★'},
  'GN': {'dmc': '3363', 'name': 'Pine Green Medium',         'hex': '#5E7A4E', 'sym': '♣'},
  'RB': {'dmc': '820',  'name': 'Royal Blue Very Dark',      'hex': '#123A8C', 'sym': '●'},
  'LB': {'dmc': '3846', 'name': 'Light Bright Turquoise',    'hex': '#2EC1D6', 'sym': '◇'},
  'WH': {'dmc': 'Blanc','name': 'White',                     'hex': '#FFFFFF', 'sym': '□'},
  'BK': {'dmc': '310',  'name': 'Black',                     'hex': '#111111', 'sym': '■'},
}

class G:
    def __init__(s, W, H):
        s.W, s.H, s.CX, s.CY = W, H, W // 2, H // 2
        s.g = [[None] * W for _ in range(H)]
    def put(s, x, y, c):
        if 0 <= x < s.W and 0 <= y < s.H: s.g[y][x] = c
    def mirx(s, x, y, c):
        s.put(x, y, c); s.put(s.W - 1 - x, y, c)
    def stamp(s, tpl, x0, y0, c, mapping=None):
        for j, row in enumerate(tpl):
            for i, ch in enumerate(row):
                if ch == '.': continue
                col = (mapping or {}).get(ch, c)
                s.put(x0 + i, y0 + j, col)
    def diamond(s, cx, cy, layers):
        """layers: list of (maxdist, color) from outside in"""
        R = layers[0][0]
        for dy in range(-R, R + 1):
            for dx in range(-R, R + 1):
                d = abs(dx) + abs(dy)
                col = None
                for (md, c) in layers:
                    if d <= md: col = c
                if col: s.put(cx + dx, cy + dy, col)
    def frame(s, outer='BR', zig='RD', dot='GD', inner='NV', band=True):
        W, H = s.W, s.H
        for x in range(W): s.put(x, 0, outer); s.put(x, H - 1, outer)
        for y in range(H): s.put(0, y, outer); s.put(W - 1, y, outer)
        if band:
            def tri(n):
                t = n % 8; return t if t <= 4 else 8 - t
            for x in range(1, W - 1):
                o = tri(abs(x - s.CX))
                for yy in (2 + o, 3 + o): s.put(x, yy, zig); s.put(x, H - 1 - yy, zig)
                if o == 4: s.put(x, 3, dot); s.put(x, H - 4, dot)
            for y in range(1, H - 1):
                o = tri(abs(y - s.CY))
                for xx in (2 + o, 3 + o): s.put(xx, y, zig); s.put(W - 1 - xx, y, zig)
                if o == 4: s.put(3, y, dot); s.put(W - 4, y, dot)
            for x in range(8, W - 8): s.put(x, 8, inner); s.put(x, H - 9, inner)
            for y in range(8, H - 8): s.put(8, y, inner); s.put(W - 9, y, inner)
            for (x0, y0) in [(0, 0), (W - 9, 0), (0, H - 9), (W - 9, H - 9)]:
                for j in range(9):
                    for i in range(9):
                        edge = i in (0, 8) or j in (0, 8); d = abs(i - 4) + abs(j - 4)
                        s.put(x0 + i, y0 + j, outer if edge else (dot if d <= 1 else (zig if d <= 3 else 'CR')))
    def colors_used(s):
        return sorted({c for row in s.g for c in row if c}, key=list(PAL).index)

def save(slug, gr, meta):
    used = gr.colors_used()
    cols = {k: PAL[k] for k in used}
    # semboller benzersiz olsun
    seen = set()
    alt = iter('✚✖◐▼♦☗♠✿')
    for k in used:
        if cols[k]['sym'] in seen: cols[k] = dict(cols[k], sym=next(alt))
        seen.add(cols[k]['sym'])
    counts = {k: sum(r.count(k) for r in gr.g) for k in used}
    os.makedirs(f'designs/{slug}', exist_ok=True)
    data = {'W': gr.W, 'H': gr.H, 'grid': gr.g, 'colors': cols, 'counts': counts, 'meta': meta}
    open(f'designs/{slug}/pattern.js', 'w').write('const P=' + json.dumps(data, ensure_ascii=False) + ';')
    print(slug, gr.W, 'x', gr.H, counts, sum(counts.values()))

KOC = ["X.....X",
       "X.....X",
       "XX...XX",
       ".XX.XX.",
       "..XXX.."]
def rot(t):  # 90 derece saat yönü
    return [''.join(t[len(t) - 1 - j][i] for j in range(len(t))) for i in range(len(t[0]))]
# ---------------------------------------------------------------- 1. Hayat Ağacı
def tree_of_life():
    gr = G(61, 85); gr.frame()
    cx = gr.CX
    top, base = 14, 66
    for y in range(top + 6, base + 1):
        gr.put(cx, y, 'BR'); gr.put(cx - 1, y, 'BR'); gr.put(cx + 1, y, 'BR')
    # dallar: yukarı doğru eğik, kısalan
    lvl = 0
    for by in range(base - 8, top + 8, -7):
        L = 6 + min(lvl, 4) * 2 if lvl < 3 else max(6, 18 - lvl * 2)
        L = [10, 13, 15, 15, 13, 11, 8][min(lvl, 6)]
        for k in range(1, L + 1):
            y = by - k // 2
            gr.mirx(cx + 1 + k, y, 'GN'); gr.mirx(cx + 1 + k, y + 1, 'GN')
        ex, ey = cx + 1 + L + 2, by - L // 2
        gr.diamond(ex, ey, [(2, 'RD'), (0, 'GD')]); gr.diamond(gr.W - 1 - ex, ey, [(2, 'RD'), (0, 'GD')])
        # dal üstü küçük yapraklar
        mx, my = cx + 1 + L // 2, by - L // 4 - 2
        gr.mirx(mx, my, 'GN'); gr.mirx(mx, my - 1, 'GN'); gr.mirx(mx + 1, my - 1, 'GN')
        lvl += 1
    # tepe: yıldız / baklava
    gr.diamond(cx, top + 3, [(5, 'NV'), (4, 'RD'), (2, 'GD'), (0, 'NV')])
    # kök / saksı (kademeli üçgen)
    for i in range(0, 7):
        for x in range(cx - 4 - i * 2, cx + 5 + i * 2):
            gr.put(x, base + 1 + i, 'RD' if i % 3 != 2 else 'NV')
    # üst köşelerde koruyucu baklavalar
    for (x, y) in [(14, 16), (gr.W - 15, 16)]:
        gr.diamond(x, y, [(3, 'TQ'), (1, 'GD')])
    save('tree_of_life', gr, {
      'slug': 'tree_of_life', 'title': 'Anatolian Kilim<br>“Tree of Life”', 'short': 'Tree of Life',
      'tagline': 'The kilim tree of life — a wish for long life, family and continuity — framed by the river path border.',
      'level': 'Beginner+',
      'motifs': [
        ['tree', 'Hayat Ağacı · Tree of Life', 'CENTER', 'One of the oldest Anatolian symbols: immortality, family roots and the hope that life goes on.'],
        ['eye', 'Göz · Evil Eye', 'TREE TOP', 'A protective diamond crowning the tree, keeping harm away from the family.'],
        ['diamond', 'Baklava · Diamond', 'UPPER CORNERS', 'Small diamonds woven as wishes for protection and good luck.'],
        ['water', 'Su Yolu · River Path', 'BORDER', 'The zigzag of flowing water — life, continuity and abundance.'],
      ]})

# ---------------------------------------------------------------- 2. Elibelinde
ELI = [".......X.......",
       "......XAX......",
       ".....XABAX.....",
       "......XAX......",
       ".......X.......",
       "..XXXXXXXXXXX..",
       ".XX....X....XX.",
       "XX.....X.....XX",
       "XX....XXX....XX",
       ".XX..XXAXX..XX.",
       "..XXXXXAXXXXX..",
       ".....XXAXX.....",
       "....XXXAXXX....",
       "...XXXXAXXXX...",
       "..XXXXXAXXXXX..",
       ".XXXXXXAXXXXXX."]
def elibelinde():
    gr = G(57, 89); gr.frame()
    cx = gr.CX
    cols = [('RD', 'GD', 'NV'), ('NV', 'GD', 'RD'), ('RD', 'GD', 'NV')]
    for i, y0 in enumerate([14, 37, 60]):
        c, a, b = cols[i]
        gr.stamp(ELI, cx - 7, y0, c, {'A': a, 'B': b})
        # yan koçboynuzları (dışa bakan)
        R = rot(KOC); Lh = [r[::-1] for r in R]
        gr.stamp(Lh, cx - 18, y0 + 5, 'BR'); gr.stamp(R, cx + 14, y0 + 5, 'BR')
    # figürler arası küçük baklavalar
    for y in (33, 56):
        for dx in (-12, 0, 12):
            gr.diamond(cx + dx, y, [(2, 'TQ'), (0, 'GD')])
    save('elibelinde', gr, {
      'slug': 'elibelinde', 'title': 'Anatolian Kilim<br>“Elibelinde”', 'short': 'Elibelinde',
      'tagline': 'Three “hands-on-hips” figures — the kilim symbol of women, motherhood and abundance.',
      'level': 'Beginner+',
      'motifs': [
        ['hands', 'Elibelinde · Hands on Hips', 'CENTER ×3', 'A stylised woman with hands on her hips: motherhood, fertility and the strength of women.'],
        ['ram', 'Koçboynuzu · Ram’s Horn', 'SIDES', 'Male strength beside the female figure — together they mean a fertile, happy home.'],
        ['diamond', 'Baklava · Diamond', 'BETWEEN', 'Small diamonds woven between figures as wishes for protection and luck.'],
        ['water', 'Su Yolu · River Path', 'BORDER', 'The zigzag of flowing water — life, continuity and abundance.'],
      ]})

# ---------------------------------------------------------------- 3. Bereket
def bereket():
    gr = G(71, 71); gr.frame()
    cx, cy = gr.CX, gr.CY
    gr.diamond(cx, cy, [(16, 'NV'), (15, 'GD'), (13, 'RD'), (9, 'CR'), (7, 'NV'), (6, 'TQ'), (3, 'GD'), (1, 'RD'), (0, 'NV')])
    # elibelinde mini figürler köşegenlerde (bereket = elibelinde + koçboynuzu)
    up = KOC; down = up[::-1]; right = rot(KOC); left = [r[::-1] for r in right]
    gr.stamp(up, cx - 3, cy - 23, 'BR'); gr.stamp(down, cx - 3, cy + 19, 'BR')
    gr.stamp(left, cx - 23, cy - 3, 'BR'); gr.stamp(right, cx + 19, cy - 3, 'BR')
    for (dx, dy) in [(-15, -15), (15, -15), (-15, 15), (15, 15)]:
        gr.diamond(cx + dx, cy + dy, [(4, 'TQ'), (3, 'CR'), (2, 'RD'), (0, 'GD')])
    save('bereket', gr, {
      'slug': 'bereket', 'title': 'Anatolian Kilim<br>“Bereket”', 'short': 'Bereket',
      'tagline': 'A square medallion of abundance — ram’s horns guarding a layered diamond, ideal for pillows and framed art.',
      'level': 'Beginner+',
      'motifs': [
        ['diamond', 'Bereket · Abundance', 'CENTER', 'Layered diamonds wish for a full table, a fertile field and a home that never lacks.'],
        ['ram', 'Koçboynuzu · Ram’s Horn', 'FOUR SIDES', 'Four horns facing outward: strength protecting the abundance in every direction.'],
        ['eye', 'Göz · Evil Eye', 'CORNERS', 'Protective eyes keep envy away from what you have.'],
        ['water', 'Su Yolu · River Path', 'BORDER', 'The zigzag of flowing water — life, continuity and abundance.'],
      ]})

# ---------------------------------------------------------------- 4. Mini Nazar seti
def mini_nazar():
    gr = G(53, 53)
    sets = [
      [(9, 'RB'), (7, 'LB'), (5, 'WH'), (3, 'RB'), (1, 'BK')],
      [(9, 'NV'), (8, 'RD'), (5, 'GD'), (3, 'CR'), (1, 'NV')],
      [(9, 'TQ'), (7, 'WH'), (5, 'LB'), (3, 'RB'), (1, 'BK')],
      [(9, 'BR'), (8, 'GD'), (6, 'RD'), (3, 'WH'), (1, 'RB')],
    ]
    centers = [(13, 13), (39, 13), (13, 39), (39, 39)]
    for (c, L) in zip(centers, sets):
        gr.diamond(c[0], c[1], L)
        for (dx, dy) in [(0, -11), (0, 11), (-11, 0), (11, 0)]:
            gr.put(c[0] + dx, c[1] + dy, L[0][1])
    save('mini_nazar', gr, {
      'slug': 'mini_nazar', 'title': 'Mini Nazar<br>Evil Eye Set', 'short': 'Mini Nazar Set',
      'tagline': 'Four small evil eye motifs in classic and kilim colours — quick to stitch, perfect for cards, bookmarks and gifts.',
      'level': 'Beginner',
      'motifs': [
        ['eye', 'Nazar Boncuğu · Classic', 'TOP LEFT', 'The famous Turkish blue eye bead, said to deflect the evil eye and envy.'],
        ['eye', 'Kilim Nazar', 'TOP RIGHT', 'The same protective eye in warm kilim reds and golds.'],
        ['eye', 'Sea Nazar', 'BOTTOM LEFT', 'Turquoise and white, like the Aegean coast.'],
        ['eye', 'Earth Nazar', 'BOTTOM RIGHT', 'Brown, gold and red — Anatolian earth tones.'],
      ]})

if __name__ == '__main__':
    tree_of_life(); elibelinde(); bereket(); mini_nazar()
