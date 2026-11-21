"""StitchAnatolia 2. hafta kilim desenleri: SA-011 Kuş, SA-012 Pıtrak."""
from designs import G, save, PAL
from designs2 import star
import designs3  # XG rengini PAL'e ekler
import json

BIRD = ["........XX..",
        ".......XAXB.",
        "X......XXX..",
        "XX....XXXX..",
        "XXX.XXXXXX..",
        ".XXXXAAAXX..",
        "..XXXAAXXX..",
        "...XXXXXX...",
        ".....L.L....",
        "....LL.LL..."]

def bird(gr, x0, y0, body, acc, beak='GD', left=False):
    t = [r[::-1] for r in BIRD] if left else BIRD
    gr.stamp(t, x0, y0, body, {'A': acc, 'B': beak, 'L': 'BR'})

# ---------------------------------------------------------------- SA-011 Kuş
def kus():
    gr = G(61, 85); gr.frame(zig='TQ', dot='GD', inner='NV')
    cx = gr.CX
    # orta hayat ağacı gövdesi
    for y in range(16, 70):
        gr.put(cx, y, 'BR')
    for (y, L) in [(24, 4), (36, 5), (48, 5), (60, 4)]:
        for k in range(1, L + 1):
            gr.mirx(cx + k, y - k // 2, 'GN')
        gr.diamond(cx, y, [(1, 'RD'), (0, 'GD')])
    gr.diamond(cx, 15, [(3, 'RD'), (2, 'GD'), (0, 'NV')])
    # karşılıklı kuş çiftleri
    rows = [(18, 'RD', 'NV'), (42, 'NV', 'RD'), (60, 'RD', 'NV')]
    for (y0, body, acc) in rows:
        bird(gr, cx - 18, y0, body, acc)              # sağa bakan, solda
        bird(gr, cx + 7, y0, body, acc, left=True)    # sola bakan, sağda
    # kuşlar arası küçük baklavalar
    for y in (31, 53):
        for dx in (-14, 14):
            gr.diamond(cx + dx, y, [(2, 'TQ'), (0, 'GD')])
    # taban
    for i in range(4):
        for dx in range(-3 - i * 2, 4 + i * 2):
            gr.put(cx + dx, 70 + i, 'RD' if i % 2 == 0 else 'GD')
    save('kus', gr, {
      'slug': 'kus', 'title': 'Anatolian Kilim<br>“Kuş” Birds', 'short': 'Kuş · Kilim Birds',
      'tagline': 'Three pairs of kilim birds facing a tree of life — the Anatolian symbol of happiness, love and good news.',
      'level': 'Beginner+',
      'motifs': [
        ['bird', 'Kuş · Bird', 'BOTH SIDES', 'Birds bring happiness, joy and good news; a pair of birds stands for love and togetherness.'],
        ['tree', 'Hayat Ağacı · Tree of Life', 'CENTER', 'The tree the birds gather around: family, roots and long life.'],
        ['diamond', 'Baklava · Diamond', 'BETWEEN', 'Small diamonds woven as wishes for protection and good luck.'],
        ['water', 'Su Yolu · River Path', 'BORDER', 'The zigzag of flowing water — life, continuity and abundance.'],
      ]})

# ---------------------------------------------------------------- SA-012 Pıtrak
def pitrak_motif(gr, cx, cy, R, arm, tip, core, mid):
    """Pıtrak (dikenli tohum): merkez baklava, dört kol, uçlarda çatal dikenler."""
    gr.diamond(cx, cy, [(R, arm), (R - 1, tip), (R - 3, mid), (R - 4, arm), (R - 5, core), (R - 7, tip), (R - 9, mid), (0, arm)])
    L = R + 5
    for (dx, dy) in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        for k in range(R + 1, L + 1):
            gr.put(cx + dx * k, cy + dy * k, arm)
            gr.put(cx + dx * k + dy, cy + dy * k + dx, arm); gr.put(cx + dx * k - dy, cy + dy * k - dx, arm)  # kalın kol
        ex, ey = cx + dx * L, cy + dy * L
        # çatal diken
        for s in (1, -1):
            px, py = (dy * s, dx * s)
            for k in range(1, 4):
                gr.put(ex + px * (k + 1) + dx * k, ey + py * (k + 1) + dy * k, tip)
        gr.diamond(ex + dx * 2, ey + dy * 2, [(1, tip), (0, core)])
    # köşegen dikenler
    for (dx, dy) in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        for k in range(R // 2 + 2, R // 2 + 5):
            gr.put(cx + dx * k, cy + dy * k, tip)

def pitrak():
    gr = G(71, 71); gr.frame(zig='RD', dot='GD', inner='NV')
    cx, cy = gr.CX, gr.CY
    pitrak_motif(gr, cx, cy, 11, 'NV', 'RD', 'GD', 'CR')
    for (dx, dy) in [(-18, -18), (18, -18), (-18, 18), (18, 18)]:
        x, y = cx + dx, cy + dy
        gr.diamond(x, y, [(4, 'TQ'), (3, 'CR'), (2, 'RD'), (0, 'GD')])
        for (ax, ay) in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            gr.put(x + ax * 5, y + ay * 5, 'TQ'); gr.put(x + ax * 6, y + ay * 6, 'TQ')
            gr.put(x + ax * 6 + ay, y + ay * 6 + ax, 'TQ'); gr.put(x + ax * 6 - ay, y + ay * 6 - ax, 'TQ')
    save('pitrak', gr, {
      'slug': 'pitrak', 'title': 'Anatolian Kilim<br>“Pıtrak”', 'short': 'Pıtrak · Burdock',
      'tagline': 'A spiky burdock medallion — the kilim charm that clings to good luck and keeps the evil eye away.',
      'level': 'Beginner+',
      'motifs': [
        ['burr', 'Pıtrak · Burdock', 'CENTER', 'The burr seed that sticks to everything: protection from the evil eye, and abundance that stays.'],
        ['burr', 'Küçük Pıtraklar · Small Burrs', 'CORNERS', 'Four smaller burrs guard every corner of the home.'],
        ['eye', 'Göz · Evil Eye', 'HEART', 'A protective eye at the very center of the burr.'],
        ['water', 'Su Yolu · River Path', 'BORDER', 'The zigzag of flowing water — life, continuity and abundance.'],
      ]})

def write_all():
    DATA = {}
    for s in ['nazar', 'tree_of_life', 'elibelinde', 'bereket', 'mini_nazar', 'goz_seti', 'kurt_agzi', 'yildiz', 'noel_susleri', 'noel_agaci', 'kus', 'pitrak']:
        t = open(f'designs/{s}/pattern.js').read()
        DATA[s] = json.loads(t[len('const P='):].rstrip().rstrip(';'))
    open('all_patterns.js', 'w').write('const DATA=' + json.dumps(DATA, ensure_ascii=False) + ';')

if __name__ == '__main__':
    kus(); pitrak(); write_all()
