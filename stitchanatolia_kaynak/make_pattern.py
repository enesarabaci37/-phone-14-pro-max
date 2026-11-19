"""Kilim motifli kanaviçe deseni üretici -> pattern.json"""
import json, math

W, H = 71, 91
CX, CY = W // 2, H // 2
g = [[None] * W for _ in range(H)]

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        g[y][x] = c

def sym4(dx, dy, c):
    for sx in (1, -1):
        for sy in (1, -1):
            put(CX + sx * dx, CY + sy * dy, c)

def stamp(tpl, x0, y0, c):
    for j, row in enumerate(tpl):
        for i, ch in enumerate(row):
            if ch == 'X':
                put(x0 + i, y0 + j, c)

def rot180(t): return [r[::-1] for r in t[::-1]]

# --- Çerçeve: kahve dış çizgi, kırmızı su yolu, lacivert iç çizgi ---
for x in range(W):
    put(x, 0, 'BR'); put(x, H - 1, 'BR')
for y in range(H):
    put(0, y, 'BR'); put(W - 1, y, 'BR')
def tri(n):
    t = n % 8
    return t if t <= 4 else 8 - t
for x in range(1, W - 1):
    o = tri(abs(x - CX))
    put(x, 2 + o, 'RD'); put(x, 3 + o, 'RD'); put(x, H - 3 - o, 'RD'); put(x, H - 4 - o, 'RD')
    if o == 4: put(x, 3, 'GD'); put(x, H - 4, 'GD')
for y in range(1, H - 1):
    o = tri(abs(y - CY))
    put(2 + o, y, 'RD'); put(3 + o, y, 'RD'); put(W - 3 - o, y, 'RD'); put(W - 4 - o, y, 'RD')
    if o == 4: put(3, y, 'GD'); put(W - 4, y, 'GD')
for x in range(8, W - 8):
    put(x, 8, 'NV'); put(x, H - 9, 'NV')
for y in range(8, H - 8):
    put(8, y, 'NV'); put(W - 9, y, 'NV')
# köşe kareleri
for (x0, y0) in [(0, 0), (W - 9, 0), (0, H - 9), (W - 9, H - 9)]:
    for j in range(9):
        for i in range(9):
            edge = i in (0, 8) or j in (0, 8)
            d = abs(i - 4) + abs(j - 4)
            put(x0 + i, y0 + j, 'BR' if edge else ('GD' if d <= 1 else ('RD' if d <= 3 else 'CR')))

# --- Orta madalyon (göz motifi) ---
R = 22
for dy in range(0, R + 1):
    for dx in range(0, R + 1):
        d = dx + dy
        if d > R: continue
        if d >= R - 1: c = 'NV'
        elif d >= 15: c = 'RD'
        elif d >= 13: c = 'GD'
        elif d >= 10: c = 'CR'
        elif d >= 8: c = 'NV'
        elif d >= 4: c = 'RD'
        elif d >= 1: c = 'GD'
        else: c = 'NV'
        sym4(dx, dy, c)
# kırmızı bant içinde küçük krem baklavalar
for (ddx, ddy) in [(9, 9)]:
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            dd = abs(dx) + abs(dy)
            if dd <= 2:
                sym4(ddx + dx, ddy + dy, 'NV' if dd == 0 else 'CR')
# yatay uçlarda turkuaz vurgular
for k in range(3):
    sym4(R - 4 - k, 0, 'TQ')

# --- Koçboynuzu (madalyonun üst ve alt ucunda) ---
KOC = ["X.....X",
       "X.....X",
       "XX...XX",
       ".XX.XX.",
       "..XXX.."]
stamp(KOC, CX - 3, CY - R - 6, 'BR')
stamp(rot180(KOC), CX - 3, CY + R + 2, 'BR')

# --- Üst/alt küçük baklava sırası ---
def small_diamond(cx, cy, r, ring, fill):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = abs(dx) + abs(dy)
            if d == r: put(cx + dx, cy + dy, ring)
            elif d <= r - 2: put(cx + dx, cy + dy, fill)
for sx in (-12, 12):
    small_diamond(CX + sx, 13, 3, 'TQ', 'GD')
    small_diamond(CX + sx, H - 14, 3, 'TQ', 'GD')

# --- Köşe yıldızları ---
STAR = ["....X....",
        "...XXX...",
        "..XX.XX..",
        "XXX...XXX",
        "XX..X..XX",
        "XXX...XXX",
        "..XX.XX..",
        "...XXX...",
        "....X...."]
for sx in (-20, 20):
    for sy in (-28, 28):
        stamp(STAR, CX + sx - 4, CY + sy - 4, 'TQ')
        put(CX + sx, CY + sy, 'RD')

COLORS = {
  'RD': {'dmc': '347', 'name': 'Salmon Very Dark (kök boya kırmızısı)', 'hex': '#B8312F', 'sym': '▲'},
  'NV': {'dmc': '311', 'name': 'Navy Blue Medium (çivit mavisi)',       'hex': '#1F3B5C', 'sym': '●'},
  'GD': {'dmc': '729', 'name': 'Old Gold Medium (aşı sarısı)',          'hex': '#CFA14A', 'sym': '◆'},
  'CR': {'dmc': '712', 'name': 'Cream (krem)',                           'hex': '#F3EBD3', 'sym': '○'},
  'BR': {'dmc': '938', 'name': 'Coffee Brown Ultra Dark (koyu kahve)',   'hex': '#3A2214', 'sym': '■'},
  'TQ': {'dmc': '3809','name': 'Turquoise Very Dark (turkuaz)',          'hex': '#3A7C82', 'sym': '★'},
}
counts = {k: sum(row.count(k) for row in g) for k in COLORS}
json.dump({'W': W, 'H': H, 'grid': g, 'colors': COLORS, 'counts': counts},
          open('pattern.json', 'w'), ensure_ascii=False)
print(counts, sum(counts.values()))
for row in g[:20]:
    print(''.join({'RD':'r','NV':'n','GD':'g','CR':'c','BR':'b','TQ':'t',None:'.'}[c] for c in row))
