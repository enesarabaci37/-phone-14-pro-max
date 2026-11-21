"""StitchAnatolia 2. hafta Noel desenleri: SA-009 Kilim Noel Süsü Seti, SA-010 Anadolu Noel Ağacı."""
from designs import G, save, PAL
from designs2 import star, write_all as _wa
import json

PAL['XG'] = {'dmc': '699', 'name': 'Christmas Green', 'hex': '#1E6B3A', 'sym': '♠'}

HEART = ["..XX...XX..",
         ".XXXX.XXXX.",
         "XXXXXXXXXXX",
         "XXXXXXXXXXX",
         "XXXXXXXXXXX",
         ".XXXXXXXXX.",
         "..XXXXXXX..",
         "...XXXXX...",
         "....XXX....",
         ".....X....."]
BELL = ["....XXX....",
        "...XXXXX...",
        "...XXXXX...",
        "..XXXXXXX..",
        "..XXXXXXX..",
        "..XXXXXXX..",
        ".XXXXXXXXX.",
        ".XXXXXXXXX.",
        "XXXXXXXXXXX",
        "XXXXXXXXXXX",
        "....XXX....",
        ".....X....."]

def hanger(gr, cx, top):
    """Süsün üstünde altın asma ilmeği."""
    for y in range(top - 3, top):
        gr.put(cx, y, 'GD')
    gr.put(cx - 1, top - 4, 'GD'); gr.put(cx + 1, top - 4, 'GD'); gr.put(cx, top - 5, 'GD')

def tree_tiers(gr, cx, top, tiers, w0, dw, h, green, garland, orn):
    """Kademeli kilim çam ağacı; her katın alt kenarında zigzag süs bandı."""
    y = top
    for t in range(tiers):
        half0, half1 = w0 + t * dw // 2, w0 + t * dw // 2 + h
        for j in range(h):
            half = half0 + (half1 - half0) * j // max(h - 1, 1)
            for dx in range(-half, half + 1):
                gr.put(cx + dx, y + j, green)
        # alt kenar zigzag
        half = half1
        for dx in range(-half + 1, half):
            zz = (abs(dx) % 4)
            yy = y + h - 1 - (1 if zz in (1, 3) else (2 if zz == 2 else 0))
            gr.put(cx + dx, yy, garland)
        # toplar
        for dx in range(-half + 3, half - 1, 5):
            gr.put(cx + dx, y + h - 4, orn)
        y += h - 2
    return y + 2

# ---------------------------------------------------------------- SA-009 Noel Süsü Seti
def noel_susleri():
    gr = G(63, 47)
    C = [(11, 14), (31, 14), (51, 14), (11, 36), (31, 36), (51, 36)]
    # 1 · Yıldız
    cx, cy = C[0]
    star(gr, cx, cy, [(6, 'RD'), (5, 'GD'), (3, 'RD'), (1, 'CR'), (0, 'GD')])
    hanger(gr, cx, cy - 8)
    # 2 · Çam ağacı
    cx, cy = C[1]
    gr.put(cx, cy - 8, 'GD'); gr.put(cx - 1, cy - 7, 'GD'); gr.put(cx + 1, cy - 7, 'GD'); gr.put(cx, cy - 7, 'GD')
    for j in range(0, 14):
        half = [0, 1, 2, 3, 2, 3, 4, 5, 4, 5, 6, 7, 6, 7][j]
        for dx in range(-half, half + 1):
            gr.put(cx + dx, cy - 6 + j, 'XG')
    for (dx, dy) in [(0, -3), (-2, 1), (2, 1), (-4, 5), (0, 5), (4, 5)]:
        gr.put(cx + dx, cy + dy, 'RD')
    for (dx, dy) in [(-1, -1), (1, -1), (-3, 3), (3, 3), (-5, 7), (5, 7), (-2, 7), (2, 7)]:
        gr.put(cx + dx, cy + dy, 'GD')
    for dx in (-1, 0, 1):
        gr.put(cx + dx, cy + 8, 'BR'); gr.put(cx + dx, cy + 9, 'BR')
    hanger(gr, cx, cy - 9)
    # 3 · Kar tanesi baklavası
    cx, cy = C[2]
    gr.diamond(cx, cy, [(5, 'NV'), (4, 'CR'), (2, 'NV'), (0, 'GD')])
    for (dx, dy) in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        for k in range(6, 8):
            gr.put(cx + dx * k, cy + dy * k, 'NV')
        gr.put(cx + dx * 7 + dy, cy + dy * 7 + dx, 'NV'); gr.put(cx + dx * 7 - dy, cy + dy * 7 - dx, 'NV')
    for (dx, dy) in [(-4, -4), (4, -4), (-4, 4), (4, 4)]:
        gr.put(cx + dx, cy + dy, 'NV'); gr.put(cx + dx + (1 if dx > 0 else -1), cy + dy + (1 if dy > 0 else -1), 'NV')
    hanger(gr, cx, cy - 8)
    # 4 · Kalp
    cx, cy = C[3]
    gr.stamp(HEART, cx - 5, cy - 5, 'RD')
    gr.diamond(cx, cy - 1, [(2, 'GD'), (1, 'CR'), (0, 'RD')])
    for dx in (-3, 3): gr.put(cx + dx, cy - 4, 'CR')
    hanger(gr, cx, cy - 5)
    # 5 · Çan
    cx, cy = C[4]
    gr.stamp(BELL, cx - 5, cy - 6, 'GD', None)
    for dx in range(-4, 5): gr.put(cx + dx, cy + 1, 'RD')
    for dx in range(-3, 4, 2): gr.put(cx + dx, cy - 1, 'RD')
    gr.put(cx, cy + 5, 'BR')
    for (dx, dy) in [(-2, -8), (-3, -9), (2, -8), (3, -9)]:
        gr.put(cx + dx, cy + dy, 'XG')
    gr.put(cx, cy - 7, 'RD'); gr.put(cx - 1, cy - 8, 'RD'); gr.put(cx + 1, cy - 8, 'RD')
    # 6 · Göz süsü
    cx, cy = C[5]
    gr.diamond(cx, cy, [(6, 'XG'), (5, 'RD'), (3, 'GD'), (2, 'CR'), (1, 'RD'), (0, 'XG')])
    for (dx, dy) in [(0, 7), (0, 8)]:
        gr.put(cx + dx, cy + dy, 'GD')
    gr.put(cx - 1, cy + 8, 'GD'); gr.put(cx + 1, cy + 8, 'GD')
    hanger(gr, cx, cy - 7)
    save('noel_susleri', gr, {
      'slug': 'noel_susleri', 'title': 'Kilim Christmas<br>Ornament Set', 'short': 'Kilim Christmas Ornaments',
      'tagline': 'Six tiny Christmas ornaments in Turkish kilim style — quick to stitch before the holidays, made for the tree, gift tags and cards.',
      'level': 'Beginner',
      'motifs': [
        ['star', 'Yıldız · Star', 'TOP LEFT', 'The kilim star of happiness, here as a tree topper or ornament.'],
        ['xtree', 'Çam · Pine Tree', 'TOP CENTER', 'A stepped kilim pine with red and gold baubles.'],
        ['snow', 'Kar Tanesi · Snowflake', 'TOP RIGHT', 'A kilim diamond with arms — a geometric snowflake in navy and cream.'],
        ['heart', 'Kalp · Heart', 'BOTTOM LEFT', 'A red heart with a little protective diamond inside.'],
        ['bell', 'Çan · Bell', 'BOTTOM CENTER', 'A golden bell with a red kilim band and holly leaves.'],
        ['eye', 'Göz · Evil Eye', 'BOTTOM RIGHT', 'The protective eye in Christmas red and green, to keep the new year safe.'],
      ]})

# ---------------------------------------------------------------- SA-010 Anadolu Noel Ağacı
def noel_agaci():
    gr = G(61, 85); gr.frame(outer='BR', zig='RD', dot='GD', inner='XG')
    cx = gr.CX
    # tepe yıldızı
    star(gr, cx, 23, [(4, 'GD'), (2, 'RD'), (0, 'GD')])
    # katlar: her kat bir öncekinin altına girinti yaparak başlar
    y = 28; tiers = [(0, 8, 1), (3, 9, 1), (5, 10, -1), (7, 11, 1)]
    for (w0, h, dirn) in tiers:
        for j in range(h):
            half = w0 + j
            for dx in range(-half, half + 1):
                gr.put(cx + dx, y + j, 'XG')
        # çapraz altın girland
        bottom = w0 + h - 1
        for dx in range(-bottom, bottom + 1):
            gy = y + h // 2 + (dirn * dx) // 3
            j = gy - y
            if 0 <= j < h and abs(dx) <= w0 + j - 1:
                gr.put(cx + dx, gy, 'GD')
        # alt sıradaki kırmızı toplar
        for dx in range(-bottom + 2, bottom - 1, 4):
            gr.put(cx + dx, y + h - 1, 'RD')
        y += h - 2
    y += 0
    # gövde
    for yy in range(y + 2, y + 5):
        for dx in (-2, -1, 0, 1, 2):
            gr.put(cx + dx, yy, 'BR')
    # kilim saksı (kademeli)
    base = y + 5
    for i in range(5):
        for dx in range(-5 - i, 6 + i):
            gr.put(cx + dx, base + i, 'RD' if i % 2 == 0 else 'GD')
    # yan hediye kutuları
    for sx in (-1, 1):
        bx = cx + sx * 15
        for j in range(6):
            for i in range(-3, 4):
                gr.put(bx + i, base - 1 + j, 'NV' if sx < 0 else 'RD')
        for j in range(6): gr.put(bx, base - 1 + j, 'GD')
        for i in range(-3, 4): gr.put(bx + i, base + 1, 'GD')
        gr.put(bx - 1, base - 2, 'GD'); gr.put(bx + 1, base - 2, 'GD')
    # kar taneleri (küçük baklava)
    for (x, yy) in [(15, 21), (45, 21), (14, 38), (46, 38), (13, 55), (47, 55)]:
        gr.diamond(x, yy, [(1, 'NV'), (0, 'CR')])
        for (dx, dy) in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            gr.put(x + dx, yy + dy, 'NV')
    save('noel_agaci', gr, {
      'slug': 'noel_agaci', 'title': 'Anatolian Kilim<br>Christmas Tree', 'short': 'Kilim Christmas Tree',
      'tagline': 'A Christmas tree woven the Anatolian way — stepped kilim tiers, golden garlands and a star of good fortune on top.',
      'level': 'Beginner+',
      'motifs': [
        ['xtree', 'Çam · Christmas Tree', 'CENTER', 'Inspired by the kilim tree of life: long life, family and a new year full of hope.'],
        ['star', 'Yıldız · Star', 'TREE TOP', 'The eight-pointed kilim star — happiness and good fortune for the home.'],
        ['snow', 'Kar Tanesi · Snowflake', 'SIDES', 'Small kilim diamonds as falling snow, wishes for protection and luck.'],
        ['water', 'Su Yolu · River Path', 'BORDER', 'The zigzag of flowing water — life, continuity and abundance.'],
      ]})

def write_all():
    DATA = {}
    for s in ['nazar', 'tree_of_life', 'elibelinde', 'bereket', 'mini_nazar', 'goz_seti', 'kurt_agzi', 'yildiz', 'noel_susleri', 'noel_agaci']:
        t = open(f'designs/{s}/pattern.js').read()
        DATA[s] = json.loads(t[len('const P='):].rstrip().rstrip(';'))
    open('all_patterns.js', 'w').write('const DATA=' + json.dumps(DATA, ensure_ascii=False) + ';')

if __name__ == '__main__':
    noel_susleri(); noel_agaci(); write_all()
