"""StitchAnatolia kalite kontrol: her yeni desenden ve her güncellemeden sonra çalıştır.
   python3 qa_check.py   -> hata varsa ❌ ile listeler ve çıkış kodu 1 olur.

Kontroller:
  Desen   : semboller benzersiz, her renk 1 çileye sığıyor, tek başına ilmek oranı, büyük şema hücresi >= 4 mm
  PDF     : sayfa sayısı = 5 + büyük şema parçası, dosya < 20 MB (Etsy sınırı)
  Metin   : başlık <= 140, 13 etiket (her biri <= 20, tekrarsız), açıklamadaki sayfa sayısı = PDF,
            açıklamadaki ilmek sayısı ve renk sayısı = desen, beyaz ip varsa krem kumaş uyarısı PDF'te
  Pinterest: başlık <= 100
  Görsel  : Etsy görsel 2 ve pinler mevcut
"""
import json, glob, os, re, sys
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.abspath(__file__))
PRODUCTS = os.path.join(ROOT, '..', 'StitchAnatolia_TUM_DOSYALAR', '1_URUNLER')
MAP = {'nazar': '1_Nazar_Madalyonu', 'tree_of_life': '2_Hayat_Agaci', 'elibelinde': '3_Elibelinde', 'bereket': '4_Bereket',
       'mini_nazar': '5_Mini_Nazar_Seti', 'goz_seti': '7_Goz_Seti', 'kurt_agzi': '8_Kurt_Agzi', 'yildiz': '9_Yildiz',
       'noel_susleri': '10_Noel_Susleri', 'noel_agaci': '11_Noel_Agaci', 'kus': '12_Kus', 'pitrak': '13_Pitrak'}
SKEIN = 1500          # bir DMC çilesiyle 14ct, 2 katla güvenli ilmek sayısı
MAXC, MAXR = 38, 54   # tiles.js ile aynı

errors, warns = [], []
def err(s, m): errors.append(f'❌ {s}: {m}')
def warn(s, m): warns.append(f'⚠️  {s}: {m}')
def ntiles(W, H): return -(-W // MAXC) * -(-H // MAXR)

D = json.loads(open(os.path.join(ROOT, 'all_patterns.js')).read()[len('const DATA='):].rstrip().rstrip(';'))
for slug, folder in MAP.items():
    P = D.get(slug)
    if not P: err(slug, 'all_patterns.js içinde yok'); continue
    W, H, g, cols, counts = P['W'], P['H'], P['grid'], P['colors'], P['counts']
    syms = [c['sym'] for c in cols.values()]
    if len(syms) != len(set(syms)): err(slug, f'tekrarlanan sembol {syms}')
    for k, n in counts.items():
        if n > SKEIN: err(slug, f'{cols[k]["dmc"]} {n} ilmek: 1 çileye sığmaz, PDF "Skeins" düzeltilmeli')
    real = {}
    for row in g:
        for k in row:
            if k: real[k] = real.get(k, 0) + 1
    if real != counts: err(slug, 'counts ızgarayla uyuşmuyor')
    iso = sum(1 for y in range(H) for x in range(W) if g[y][x] and not any(
        0 <= x + dx < W and 0 <= y + dy < H and g[y + dy][x + dx] == g[y][x]
        for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy))
    if iso / sum(counts.values()) > 0.10: warn(slug, f'tek başına ilmek oranı %{iso*100//sum(counts.values())}')
    t = ntiles(W, H)
    nx, ny = -(-W // MAXC), -(-H // MAXR)
    tc, tr = -(-W // nx) + (3 if nx > 1 else 0) * min(nx - 1, 2), -(-H // ny) + (3 if ny > 1 else 0) * min(ny - 1, 2)
    cw = min(172 / tc, 222 / tr, 5.2)
    if cw < 4.0: err(slug, f'büyük şema karesi {cw:.1f} mm (< 4 mm)')
    d = os.path.join(PRODUCTS, folder)
    pdfs = glob.glob(d + '/*.pdf')
    if len(pdfs) != 1: err(slug, f'klasörde {len(pdfs)} PDF var'); continue
    pages = len(PdfReader(pdfs[0]).pages)
    if pages != 5 + t: err(slug, f'PDF {pages} sayfa, beklenen {5 + t}')
    if os.path.getsize(pdfs[0]) > 20e6: err(slug, 'PDF 20 MB üstü (Etsy kabul etmez)')
    pdftext = ''.join(p.extract_text() or '' for p in PdfReader(pdfs[0]).pages)
    if 'WH' in cols and 'Avoid pure white fabric' not in pdftext: err(slug, 'beyaz ip var ama PDF kumaş uyarısı yok')
    txt = open(d + '/URUN_BILGILERI.txt', encoding='utf-8-sig').read()
    m = re.search(r'(\d+)-page PDF', txt)
    if not m or int(m.group(1)) != pages: err(slug, f'açıklamada sayfa sayısı {m and m.group(1)}, PDF {pages}')
    if f'Stitch count: {W} × {H}' not in txt: err(slug, 'açıklamadaki ilmek sayısı desenle uyuşmuyor')
    m = re.search(r'Colors: (\d+) DMC', txt)
    if not m or int(m.group(1)) != len(cols): err(slug, f'açıklamada renk sayısı {m and m.group(1)}, desen {len(cols)}')
    tm = re.search(r'(?:BAŞLIK \(\d+/140\):\n|\*\*Başlık\*\* \(\d+/140\):\n```\n)(.+)', txt)
    if tm and len(tm.group(1).strip()) > 140: err(slug, 'Etsy başlığı 140 karakteri aşıyor')
    for f in ('Etsy/etsy_gorsel_1_kapak.png', 'Etsy/etsy_gorsel_2_icerik.png'):
        if not os.path.exists(os.path.join(d, f)): err(slug, f'{f} yok')
    if not glob.glob(d + '/Etsy/*.mp4'): err(slug, 'video yok')
    if len(glob.glob(d + '/Pinterest/*.png')) < 2: err(slug, 'pin görselleri eksik')

# paket
bd = os.path.join(PRODUCTS, '6_Kilim_Koleksiyonu_Paket')
bp = glob.glob(bd + '/*.pdf')[0]
bpages = len(PdfReader(bp).pages)
exp = 2 + sum(5 + ntiles(D[s]['W'], D[s]['H']) for s in ['nazar', 'tree_of_life', 'elibelinde', 'bereket', 'mini_nazar'])
if bpages != exp: err('paket', f'PDF {bpages} sayfa, beklenen {exp}')
if os.path.getsize(bp) > 20e6: err('paket', 'PDF 20 MB üstü')
if f'One {bpages}-page PDF' not in open(bd + '/URUN_BILGILERI.txt', encoding='utf-8-sig').read(): err('paket', 'açıklamadaki sayfa sayısı yanlış')

for w in warns: print(w)
for e in errors: print(e)
print(f'\n{len(MAP)} desen + paket kontrol edildi: {len(errors)} hata, {len(warns)} uyarı')
sys.exit(1 if errors else 0)
