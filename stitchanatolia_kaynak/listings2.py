"""SA-006..008 ilan metinleri -> URUN_BILGILERI.txt (UTF-8 BOM + CRLF)"""
import os, shutil, glob
from listings import details, common_note
ROOT = '../StitchAnatolia_TUM_DOSYALAR/1_URUNLER'
PDF = {'goz_seti': 'Kilim_Goz_Evil_Eye_Sampler_Cross_Stitch_Pattern.pdf',
       'kurt_agzi': 'Anatolian_Kilim_Kurt_Agzi_Wolf_Cross_Stitch_Pattern.pdf',
       'yildiz': 'Anatolian_Kilim_Yildiz_Star_Cross_Stitch_Pattern.pdf'}
L = [
 dict(slug='goz_seti', folder='7_Goz_Seti', sku='SA-006', tr='Göz Seti', price='4,50 $', W=75, H=53, level='Beginner',
  dmc=['347','311','729','712','938','3809','820','3846','Blanc','310'],
  title='Evil Eye Cross Stitch Sampler PDF, 6 Turkish Kilim Eye Motifs, Small Nazar Amulet Designs, Boho Bookmark Embroidery, Instant Download',
  tags=['evil eye sampler','kilim cross stitch','nazar cross stitch','evil eye stitch','turkish pattern','cross stitch pdf','small cross stitch','amulet pattern','bookmark pattern','boho cross stitch','protection symbol','anatolian motif','beginner pattern'],
  intro="""Six protective eye motifs from Anatolian kilims — in one sampler. 🧿

In Turkish weaving, the GÖZ (eye) is woven in many forms, all with one wish: to turn back envy and keep the home safe. This sampler collects six of them:

• GÖZ (Classic Eye) – the layered diamond with a dot at its heart
• MUSKA (Amulet) – a triangle charm carrying an eye
• ÇENGELLİ GÖZ (Hooked Eye) – hooks that catch the evil glance
• DÖRT GÖZ (Four Eyes) – protection in every direction
• YILDIZ GÖZ (Star Eye) – an eye inside a star, for luck
• NAZAR BONCUĞU (Blue Bead) – Türkiye's famous blue eye, kilim style

Stitch the whole sampler for a frame, or stitch each motif on its own (about 1.2–1.6 in / 3–4 cm on 14 count) for cards, bookmarks, ornaments and small gifts.""",
  pin_title='Evil Eye Cross Stitch Sampler | 6 Turkish Kilim Eye Motifs PDF', board='Evil Eye Cross Stitch',
  pin_desc="Six protective eye motifs from Turkish kilims in one cross stitch sampler: classic eye, amulet (muska), hooked eye, four eyes, star eye and the blue nazar bead. Stitch them together or one by one for cards and bookmarks. 75 × 53 stitches, beginner friendly. Instant PDF download. #evileye #crossstitch #nazar #kilim #crossstitchpattern"),
 dict(slug='kurt_agzi', folder='8_Kurt_Agzi', sku='SA-007', tr='Kurt Ağzı', price='5,50 $', W=61, H=87, level='Advanced beginner',
  dmc=['347','311','729','712','938','3809'],
  title='Wolf Cross Stitch Pattern PDF, Turkish Kilim Kurt Agzi Motif, Wolf Track Folk Art Embroidery, Anatolian Rug Chart, Instant Download',
  tags=['wolf cross stitch','kilim cross stitch','turkish pattern','wolf pattern','folk art pattern','cross stitch pdf','geometric pattern','boho cross stitch','ethnic embroidery','dmc pattern','rug cross stitch','anatolian motif','modern cross stitch'],
  intro="""The wolf's mouth — an ancient Anatolian charm of protection and courage. 🐺

Shepherd families in Anatolia wove the KURT AĞZI (wolf's mouth) into their kilims to keep wolves away from the flock — and every danger away from the family:

• KURT AĞZI (Wolf's Mouth) – a toothed diamond that guards the home
• KURT İZİ (Wolf Track) – courage, freedom and the free-roaming Anatolian wolf
• GÖZ (Evil Eye) – a small protective eye between the two mouths
• SU YOLU (River Path) – the zigzag border, the flow of life and abundance

A meaningful gift for wolf lovers, a new home or anyone who needs a little protection.""",
  pin_title='Wolf Kilim Cross Stitch Pattern | Turkish Kurt Ağzı Motif PDF', board='Anatolian Symbols & Meanings',
  pin_desc="The Kurt Ağzı (wolf's mouth) is an old Anatolian kilim motif that protects the flock and the family. This modern cross stitch pattern pairs two toothed wolf medallions with wolf tracks and a zigzag river border. 61 × 87 stitches, 6 DMC colors, full stitches only. Instant PDF download. #wolf #crossstitch #kilim #folkart #crossstitchpattern"),
 dict(slug='yildiz', folder='9_Yildiz', sku='SA-008', tr='Yıldız', price='5,50 $', W=69, H=69, level='Advanced beginner',
  dmc=['347','311','729','712','938','3809'],
  title='Kilim Star Cross Stitch Pattern PDF, Turkish Eight Pointed Star, Square Pillow Embroidery Chart, Geometric Boho Design, Instant Download',
  tags=['star cross stitch','kilim cross stitch','turkish pattern','eight point star','square cross stitch','pillow cross stitch','cross stitch pdf','geometric pattern','boho cross stitch','ethnic embroidery','dmc pattern','anatolian motif','housewarming gift'],
  intro="""A bold eight-pointed kilim star — a wish for happiness and good fortune. ⭐

The YILDIZ (star) is one of the most loved motifs in Anatolian weaving. Woven into a kilim, it brings happiness and a guiding light to the home:

• YILDIZ (Star) – the large eight-pointed star medallion at the center
• KÜÇÜK YILDIZLAR (Small Stars) – four small stars, one in every corner
• BAKLAVA (Diamond) – small diamonds at the star tips for protection and luck
• SU YOLU (River Path) – the zigzag border, the flow of life

The square shape is perfect for a pillow, a framed piece or a housewarming gift.""",
  pin_title='Kilim Star Cross Stitch Pattern | Turkish 8 Pointed Star PDF', board='Turkish Kilim Cross Stitch Patterns',
  pin_desc="A bold eight-pointed star inspired by Turkish kilim weaving — the Anatolian symbol of happiness and good fortune. Square design, ideal for pillows and framed art. 69 × 69 stitches, 6 DMC colors, full stitches only. Instant PDF download with color and printer-friendly charts. #crossstitch #kilim #star #bohodecor #crossstitchpattern"),
]
def wtxt(path, s):
    open(path, 'w', encoding='utf-8-sig', newline='\r\n').write(s)
for it in L:
    assert len(it['title']) <= 140 and len(it['tags']) == 13 and all(len(t) <= 20 for t in it['tags']), it['slug']
    assert len(set(it['tags'])) == 13 and len(it['pin_title']) <= 100
    desc = it['intro'] + "\n\nDesigned in Taşköprü, a small town in northern Türkiye.\n\n" + details(it['W'], it['H'], it['dmc'], it['level']) + "\n\n" + common_note(it['W'], it['H'])
    D = f"{ROOT}/{it['folder']}"; os.makedirs(D + '/Etsy', exist_ok=True); os.makedirs(D + '/Pinterest', exist_ok=True)
    s = it['slug']
    shutil.copy(f'out/{s}/{PDF[s]}', D)
    for f in ('etsy_gorsel_1_kapak.png', 'etsy_gorsel_2_icerik.png'): shutil.copy(f'out/{s}/{f}', D + '/Etsy')
    shutil.copy(f"video_out/{it['folder']}_video.mp4", D + '/Etsy')
    for v in 'ab': shutil.copy(f'pins/pin_{s}_{v}.png', f'{D}/Pinterest/pin_{s}_{v}_dikey.png')
    txt = f"""{it['folder'].split('_',1)[0]} {it['tr']}  ·  SKU: {it['sku']}  ·  Önerilen fiyat: {it['price']}

==================== ETSY ====================

PDF -> Digital files. Etsy/ klasöründeki 2 görsel -> Photos, video -> Video.

BAŞLIK ({len(it['title'])}/140):
{it['title']}

ETİKETLER (13 adet, tek tek ekle):
""" + "\n".join(it['tags']) + f"""

AÇIKLAMA:
{desc}

==================== PINTEREST ====================
pin_{s}_a / pin_{s}_b / video -> Link: bu ürünün Etsy linki
Pano: {it['board']} (b versiyonu da aynı panoya olabilir)

BAŞLIK ({len(it['pin_title'])}/100):
{it['pin_title']}

AÇIKLAMA:
{it['pin_desc']}
"""
    wtxt(D + '/URUN_BILGILERI.txt', txt)
    print(it['sku'], s, len(it['title']), len(it['pin_title']))
