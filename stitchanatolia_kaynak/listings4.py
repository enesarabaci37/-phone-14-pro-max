"""SA-011..012 ilan metinleri -> URUN_BILGILERI.txt (UTF-8 BOM + CRLF)"""
import os, shutil, glob
from listings import details, common_note
ROOT = '../StitchAnatolia_TUM_DOSYALAR/1_URUNLER'
PDF = {'kus': 'Anatolian_Kilim_Kus_Birds_Cross_Stitch_Pattern.pdf',
       'pitrak': 'Anatolian_Kilim_Pitrak_Cross_Stitch_Pattern.pdf'}
L = [
 dict(slug='kus', folder='12_Kus', sku='SA-011', tr='Kuş', price='5,50 $', W=61, H=85, level='Advanced beginner',
  dmc=['347','311','729','712','938','3809','3363'],
  title='Folk Bird Cross Stitch Pattern PDF, Turkish Kilim Birds and Tree of Life, Boho Embroidery Chart, Anatolian Folk Art, Instant Download',
  tags=['bird cross stitch','folk bird pattern','kilim cross stitch','turkish pattern','tree of life stitch','folk art pattern','cross stitch pdf','boho cross stitch','ethnic embroidery','dmc pattern','modern cross stitch','anatolian motif','love birds gift'],
  intro="""Three pairs of kilim birds gathered around a tree of life. 🐦

In Anatolian weaving the KUŞ (bird) is a messenger of joy. Birds bring happiness and good news, and a pair of birds facing each other stands for love and a happy home:

• KUŞ (Bird) – happiness, joy, good news; a pair of birds means love and togetherness
• HAYAT AĞACI (Tree of Life) – family roots and long life
• BAKLAVA (Diamond) – small wishes for protection and good luck
• SU YOLU (River Path) – the turquoise zigzag border, the flow of life

A sweet gift for a wedding, an anniversary, a new home or anyone who loves folk art birds.""",
  pin_title='Folk Bird Cross Stitch Pattern | Turkish Kilim Love Birds PDF', board='Anatolian Symbols & Meanings',
  pin_desc="In Turkish kilims, birds bring happiness and good news, and a pair of birds means love. This folk art cross stitch pattern shows three pairs of kilim birds around a tree of life, framed by a turquoise river border. 61 × 85 stitches, 7 DMC colors, full stitches only. Instant PDF download. #folkart #birdcrossstitch #crossstitch #kilim #crossstitchpattern"),
 dict(slug='pitrak', folder='13_Pitrak', sku='SA-012', tr='Pıtrak', price='5,50 $', W=71, H=71, level='Advanced beginner',
  dmc=['347','311','729','712','938','3809'],
  title='Turkish Kilim Cross Stitch Pattern PDF, Pitrak Burdock Medallion, Square Geometric Pillow Design, Boho Evil Eye Chart, Instant Download',
  tags=['kilim cross stitch','turkish pattern','geometric pattern','square cross stitch','pillow cross stitch','medallion pattern','cross stitch pdf','boho cross stitch','ethnic embroidery','dmc pattern','evil eye stitch','anatolian motif','modern cross stitch'],
  intro="""A spiky burdock medallion — the kilim charm that clings to good luck. 🌟

PITRAK is the burdock seed that sticks to everything it touches. Anatolian weavers wove it into their kilims to keep the evil eye away and to make abundance stay at home:

• PITRAK (Burdock) – protection from the evil eye, and abundance that stays
• KÜÇÜK PITRAKLAR (Small Burrs) – four smaller burrs guarding every corner
• GÖZ (Evil Eye) – a protective eye at the heart of the medallion
• SU YOLU (River Path) – the zigzag border, the flow of life

The square shape is perfect for a pillow, a framed piece or a housewarming gift.""",
  pin_title='Kilim Medallion Cross Stitch Pattern | Turkish Pıtrak Burdock PDF', board='Turkish Kilim Cross Stitch Patterns',
  pin_desc="Pıtrak (burdock) is an Anatolian kilim charm: like the burr that sticks to everything, it keeps the evil eye away and makes good luck stay. A bold square medallion for pillows and framed art. 71 × 71 stitches, 6 DMC colors, full stitches only. Instant PDF download. #kilim #crossstitch #evileye #bohodecor #crossstitchpattern"),
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
