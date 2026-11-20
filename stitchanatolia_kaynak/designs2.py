"""StitchAnatolia 1. hafta yeni desenler: SA-006 Göz Seti, SA-007 Kurt Ağzı, SA-008 Yıldız."""
import json
from designs import G, save, KOC, rot

def star_dist(dx, dy):
    """8 köşeli Anadolu yıldızı: kare + 45° döndürülmüş kare birleşimi."""
    return min(max(abs(dx), abs(dy)), (abs(dx) + abs(dy)) / 1.4142)

def star(gr, cx, cy, layers):
    R = int(layers[0][0] * 1.42) + 1
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            d = star_dist(dx, dy); col = None
            for (md, c) in layers:
                if d <= md + 0.25: col = c
            if col: gr.put(cx + dx, cy + dy, col)

def hooked_diamond(gr, cx, cy, R, out, fill, hook):
    """Kenarlarından dışa doğru çengeller çıkan baklava (kilim 'çengel' motifi)."""
    gr.diamond(cx, cy, [(R, out), (R - 1, fill)])
    for sx in (1, -1):
        for sy in (1, -1):
            # her kenarın ortasından dışa çengel
            mx, my = cx + sx * (R // 2 + 1), cy + sy * (R - R // 2)
            for k in range(1, 3):
                gr.put(mx + sx * k, my + sy * k, hook)
            gr.put(mx + sx * 2 + sx, my + sy * 2 - sy, hook)

# ---------------------------------------------------------------- SA-006 Göz Seti
def goz_seti():
    """6 farklı kilim göz motifi, 3 × 2 sampler; her biri yer imi / kart için ayrı işlenebilir."""
    gr = G(75, 53)
    # ince dış çerçeve + köşe noktaları
    for x in range(gr.W):
        gr.put(x, 0, 'NV'); gr.put(x, gr.H - 1, 'NV')
    for y in range(gr.H):
        gr.put(0, y, 'NV'); gr.put(gr.W - 1, y, 'NV')
    for x in range(2, gr.W - 2, 2):
        gr.put(x, 2, 'GD'); gr.put(x, gr.H - 3, 'GD')
    for y in range(4, gr.H - 3, 2):
        gr.put(2, y, 'GD'); gr.put(gr.W - 3, y, 'GD')
    C = [(13, 14), (37, 14), (61, 14), (13, 38), (37, 38), (61, 38)]
    # 1 · Klasik göz: katmanlı baklava, ortada nokta
    gr.diamond(*C[0], [(9, 'NV'), (8, 'RD'), (5, 'GD'), (3, 'CR'), (1, 'NV')])
    # 2 · Muska göz: üçgen muska içinde göz
    cx, cy = C[1]
    for j in range(0, 17):
        half = j // 2 + 1 if j < 16 else 9
        for dx in range(-half, half + 1):
            edge = abs(dx) >= half - 0 or j >= 15
            gr.put(cx + dx, cy - 8 + j, 'BR' if edge else 'CR')
    gr.diamond(cx, cy + 2, [(4, 'RD'), (2, 'GD'), (0, 'NV')])
    for dx in (-6, 0, 6):
        gr.put(cx + dx, cy + 10, 'RD'); gr.put(cx + dx, cy + 11, 'RD')
    gr.put(cx, cy - 10, 'RD'); gr.put(cx, cy - 11, 'GD')
    # 3 · Çengelli göz: dışa çengelli baklava
    cx, cy = C[2]
    gr.diamond(cx, cy, [(7, 'TQ'), (6, 'CR'), (4, 'NV'), (2, 'GD'), (0, 'RD')])
    for sx in (1, -1):
        for sy in (1, -1):
            bx, by = cx + sx * 4, cy + sy * 4
            gr.put(bx, by, 'TQ'); gr.put(bx + sx, by + sy, 'TQ'); gr.put(bx + 2 * sx, by + 2 * sy, 'TQ')
            gr.put(bx + 2 * sx, by + sy, 'TQ'); gr.put(bx + 2 * sx, by, 'TQ')
    for (dx, dy) in [(0, -9), (0, 9), (-9, 0), (9, 0)]:
        gr.put(cx + dx, cy + dy, 'TQ')
    # 4 · Dört göz: dört küçük göz ve merkez
    cx, cy = C[3]
    for (dx, dy) in [(0, -5), (0, 5), (-5, 0), (5, 0)]:
        gr.diamond(cx + dx, cy + dy, [(3, 'RD'), (1, 'GD'), (0, 'NV')])
    gr.diamond(cx, cy, [(1, 'NV')])
    for (dx, dy) in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
        gr.diamond(cx + dx, cy + dy, [(1, 'TQ')])
    # 5 · Yıldız göz: 8 köşeli yıldız ortasında göz
    cx, cy = C[4]
    star(gr, cx, cy, [(7, 'NV'), (6, 'GD'), (4, 'CR')])
    gr.diamond(cx, cy, [(3, 'RD'), (1, 'NV')])
    # 6 · Nazar boncuğu (kilim çizgisinde)
    cx, cy = C[5]
    gr.diamond(cx, cy, [(9, 'RB'), (7, 'LB'), (5, 'WH'), (3, 'RB'), (1, 'BK')])
    for (dx, dy) in [(0, -11), (0, 11), (-11, 0), (11, 0)]:
        gr.put(cx + dx, cy + dy, 'RB')
    # ara noktalar
    for y in (14, 38):
        for x in (25, 49):
            gr.put(x, y, 'GD')
    for x in (13, 37, 61):
        gr.put(x, 26, 'GD')
    save('goz_seti', gr, {
      'slug': 'goz_seti', 'title': 'Kilim “Göz”<br>Evil Eye Sampler', 'short': 'Göz Evil Eye Sampler',
      'tagline': 'Six protective eye motifs from Anatolian kilims in one sampler — stitch them all together, or one by one for cards, bookmarks and ornaments.',
      'level': 'Beginner',
      'motifs': [
        ['eye', 'Göz · Classic Eye', 'TOP LEFT', 'The layered diamond with a dot at its heart: the oldest kilim eye, woven to turn back envy.'],
        ['amulet', 'Muska · Amulet', 'TOP CENTER', 'A triangle amulet carrying an eye — a charm once sewn into clothes and hung in doorways.'],
        ['hook', 'Çengelli Göz · Hooked Eye', 'TOP RIGHT', 'Hooks reaching outward catch the evil glance before it reaches the home.'],
        ['diamond', 'Dört Göz · Four Eyes', 'BOTTOM LEFT', 'Four eyes looking in four directions: protection on every side.'],
        ['star', 'Yıldız Göz · Star Eye', 'BOTTOM CENTER', 'An eye inside a star — protection joined with happiness and luck.'],
        ['eye', 'Nazar Boncuğu · Blue Bead', 'BOTTOM RIGHT', 'Türkiye’s famous blue glass bead, here in kilim style.'],
      ]})

# ---------------------------------------------------------------- SA-007 Kurt Ağzı
def kurt_agzi():
    """Üst üste üç 'kurt ağzı' madalyonu: dişli baklava, kenarlarda kurt izi."""
    gr = G(61, 87); gr.frame(zig='RD', dot='GD', inner='BR')
    cx = gr.CX
    def wolf(cy, R, out, tooth, inner, core):
        # dış lacivert bant + içe bakan üçgen dişler (kurt ağzı)
        for dy in range(-R, R + 1):
            for dx in range(-R, R + 1):
                d = abs(dx) + abs(dy)
                if d > R: continue
                v = abs(abs(dx) - abs(dy))          # kenar boyunca konum
                t = v % 6; h = t if t <= 3 else 6 - t  # üçgen dalga 0..3
                if d >= R - 1: c = out
                elif d >= R - 2 - (3 - h): c = tooth
                elif d >= R - 6: c = 'CR'
                else: c = None
                if c: gr.put(cx + dx, cy + dy, c)
        gr.diamond(cx, cy, [(R - 7, inner), (R - 8, 'GD'), (R - 9, 'CR'), (3, core), (1, 'GD'), (0, inner)])
        # sağ-sol uçlarda çengel
        for sx in (1, -1):
            x = cx + sx * (R + 1)
            gr.put(x, cy, out); gr.put(x + sx, cy, out)
            for k in (1, 2):
                gr.put(x + sx, cy - k, out); gr.put(x + sx, cy + k, out)
            gr.put(x, cy - 2, out); gr.put(x, cy + 2, out)
    wolf(24, 13, 'NV', 'RD', 'NV', 'TQ')
    wolf(62, 13, 'NV', 'RD', 'NV', 'TQ')
    # orta küçük madalyon
    gr.diamond(cx, 43, [(5, 'RD'), (4, 'GD'), (2, 'NV'), (0, 'CR')])
    for sx in (1, -1):
        for k in range(1, 6):
            gr.put(cx + sx * (5 + k), 43, 'BR')
        gr.diamond(cx + sx * 13, 43, [(2, 'TQ'), (0, 'GD')])
    # kurt izi: üç parmak + taban, kenarlarda
    PAW = [".X.X.X.",
           ".......",
           "..XXX..",
           ".XXXXX.",
           "..XXX.."]
    for y0 in (12, 31, 50, 69):
        gr.stamp(PAW, 11, y0, 'BR'); gr.stamp(PAW, gr.W - 18, y0, 'BR')
    save('kurt_agzi', gr, {
      'slug': 'kurt_agzi', 'title': 'Anatolian Kilim<br>“Kurt Ağzı”', 'short': 'Kurt Ağzı · Wolf’s Mouth',
      'tagline': 'Two “wolf’s mouth” medallions with serrated teeth and wolf tracks — the kilim charm that guards the flock and the family.',
      'level': 'Beginner+',
      'motifs': [
        ['wolf', 'Kurt Ağzı · Wolf’s Mouth', 'TOP & BOTTOM', 'A toothed diamond, woven by shepherd families to keep wolves — and every danger — away.'],
        ['paw', 'Kurt İzi · Wolf Track', 'SIDES', 'The wolf’s footprint: courage, freedom and the power of the free-roaming Anatolian wolf.'],
        ['eye', 'Göz · Evil Eye', 'CENTER', 'A small protective eye between the two mouths, guarding the middle of the home.'],
        ['water', 'Su Yolu · River Path', 'BORDER', 'The zigzag of flowing water — life, continuity and abundance.'],
      ]})

# ---------------------------------------------------------------- SA-008 Yıldız
def yildiz():
    """Kare kilim yıldızı: büyük 8 köşeli yıldız madalyonu, köşelerde küçük yıldızlar."""
    gr = G(69, 69); gr.frame(zig='NV', dot='GD', inner='RD')
    cx, cy = gr.CX, gr.CY
    star(gr, cx, cy, [(17, 'NV'), (16, 'GD'), (14, 'RD'), (10, 'CR'), (8, 'NV'), (7, 'TQ'), (4, 'GD'), (2, 'RD'), (0, 'CR')])
    for (dx, dy) in [(-19, -19), (19, -19), (-19, 19), (19, 19)]:
        star(gr, cx + dx, cy + dy, [(4, 'RD'), (3, 'GD'), (1, 'NV')])
    # yıldız uçlarına küçük baklava ışınlar
    for (dx, dy) in [(0, -22), (0, 22), (-22, 0), (22, 0)]:
        gr.diamond(cx + dx, cy + dy, [(2, 'TQ'), (0, 'GD')])
    save('yildiz', gr, {
      'slug': 'yildiz', 'title': 'Anatolian Kilim<br>“Yıldız” Star', 'short': 'Yıldız · Kilim Star',
      'tagline': 'A bold eight-pointed kilim star in a square frame — a wish for happiness and good fortune, made for pillows and framed art.',
      'level': 'Beginner+',
      'motifs': [
        ['star', 'Yıldız · Star', 'CENTER', 'The eight-pointed star: happiness, good fortune and a guiding light for the household.'],
        ['star', 'Küçük Yıldızlar · Small Stars', 'CORNERS', 'Four small stars carry the same wish to every corner of the home.'],
        ['diamond', 'Baklava · Diamond', 'STAR TIPS', 'Small diamonds woven as wishes for protection and good luck.'],
        ['water', 'Su Yolu · River Path', 'BORDER', 'The zigzag of flowing water — life, continuity and abundance.'],
      ]})

def write_all():
    import re
    DATA = {}
    for s in ['nazar', 'tree_of_life', 'elibelinde', 'bereket', 'mini_nazar', 'goz_seti', 'kurt_agzi', 'yildiz']:
        t = open(f'designs/{s}/pattern.js').read()
        DATA[s] = json.loads(t[len('const P='):].rstrip().rstrip(';'))
    open('all_patterns.js', 'w').write('const DATA=' + json.dumps(DATA, ensure_ascii=False) + ';')

if __name__ == '__main__':
    goz_seti(); kurt_agzi(); yildiz(); write_all()
