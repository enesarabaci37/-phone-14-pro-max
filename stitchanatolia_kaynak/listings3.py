"""SA-009..010 ilan metinleri -> URUN_BILGILERI.txt (UTF-8 BOM + CRLF)"""
import os, shutil, glob
from listings import details, common_note
ROOT = '../StitchAnatolia_TUM_DOSYALAR/1_URUNLER'
PDF = {'noel_susleri': 'Kilim_Christmas_Ornaments_Cross_Stitch_Pattern.pdf',
       'noel_agaci': 'Anatolian_Kilim_Christmas_Tree_Cross_Stitch_Pattern.pdf'}
L = [
 dict(slug='noel_susleri', folder='10_Noel_Susleri', sku='SA-009', tr='Noel Süsü Seti', price='3,50 $', W=63, H=47, level='Beginner',
  dmc=['347','311','729','712','938','699'],
  title='Christmas Ornament Cross Stitch Pattern PDF, 6 Mini Kilim Designs, Star Tree Snowflake Bell, Easy Holiday Embroidery, Instant Download',
  tags=['christmas ornament','xmas cross stitch','ornament pattern','mini cross stitch','holiday stitch','christmas pattern','snowflake stitch','christmas tree','easy cross stitch','cross stitch pdf','gift tag pattern','kilim cross stitch','beginner pattern'],
  intro="""Six tiny Christmas ornaments in Turkish kilim style — quick to stitch before the holidays. 🎄

Each ornament is about 1 inch wide and 1.1–1.7 inches tall (2.5 × 3–4.5 cm) on 14 count Aida, including the hanging loop, so you can finish one in an evening. Stitch them for the tree, gift tags, Christmas cards or little gifts for friends:

• YILDIZ (Star) – the kilim star of happiness and good fortune
• ÇAM (Pine Tree) – a stepped kilim pine with red and gold baubles
• KAR TANESİ (Snowflake) – a geometric kilim snowflake in navy and cream
• KALP (Heart) – a red heart with a little protective diamond
• ÇAN (Bell) – a golden bell with holly leaves
• GÖZ (Evil Eye) – the protective eye in Christmas red and green, to keep the new year safe

Each design has a small golden loop on top, ready to hang. Great for beginners!""",
  pin_title='Christmas Ornament Cross Stitch Patterns | 6 Mini Kilim Designs PDF', board='Boho Cross Stitch Ideas',
  pin_desc="Six tiny Christmas ornaments in Turkish kilim style: star, pine tree, snowflake, heart, bell and evil eye. About 1 inch wide each — quick to stitch for the tree, gift tags and cards. Beginner friendly, 6 DMC colors. Instant PDF download. #christmascrossstitch #christmasornaments #crossstitch #xmas #handmadechristmas"),
 dict(slug='noel_agaci', folder='11_Noel_Agaci', sku='SA-010', tr='Noel Ağacı', price='5,50 $', W=61, H=85, level='Advanced beginner',
  dmc=['347','311','729','712','938','699'],
  title='Christmas Tree Cross Stitch Pattern PDF, Turkish Kilim Holiday Design, Boho Xmas Embroidery Chart, Folk Art Holiday Decor, Instant Download',
  tags=['christmas tree','xmas cross stitch','christmas pattern','holiday stitch','kilim cross stitch','boho christmas','folk art christmas','cross stitch pdf','christmas decor','turkish pattern','dmc pattern','modern cross stitch','christmas gift'],
  intro="""A Christmas tree woven the Anatolian way. 🎄⭐

This holiday cross stitch pattern brings together the Christmas tree and the colors and border of a Turkish kilim:

• ÇAM (Christmas Tree) – stepped kilim tiers with golden garlands and red baubles, inspired by the kilim tree of life: long life and a new year full of hope
• YILDIZ (Star) – the eight-pointed kilim star on top, for happiness and good fortune
• KAR TANESİ (Snowflakes) – small kilim diamonds falling like snow
• SU YOLU (River Path) – the zigzag border, the flow of life

Wrapped gifts under the tree complete the scene. Frame it for your holiday decor or stitch it as a handmade Christmas gift.""",
  pin_title='Kilim Christmas Tree Cross Stitch Pattern | Boho Holiday PDF', board='Turkish Kilim Cross Stitch Patterns',
  pin_desc="A Christmas tree woven the Anatolian way: stepped kilim tiers, golden garlands, a kilim star on top and a zigzag river border. A boho folk art cross stitch for your holiday decor or a handmade gift. 61 × 85 stitches, 6 DMC colors, full stitches only. Instant PDF download. #christmascrossstitch #christmastree #crossstitch #bohochristmas #kilim"),
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
