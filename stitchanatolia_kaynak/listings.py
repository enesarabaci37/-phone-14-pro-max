import json

COMMON_NOTE = """━━━━━━━━━━━━━━━━━━━━
WHAT YOU GET
━━━━━━━━━━━━━━━━━━━━
A 5-page PDF (A4, also prints well on US Letter):
1. Cover with stitched preview
2. Motif meanings + DMC floss key with stitch counts
3. Full color chart with symbols
4. Printer-friendly black & white symbol chart
5. Step-by-step stitching guide

━━━━━━━━━━━━━━━━━━━━
PLEASE NOTE
━━━━━━━━━━━━━━━━━━━━
• This is a DIGITAL PATTERN. No physical item, fabric or floss will be shipped.
• Your file is available to download right after purchase.
• Colors may look slightly different depending on your screen.
• For personal use only. You may sell items you stitch yourself, but please do not share or resell the pattern file.

More Anatolian kilim patterns in my shop: StitchAnatolia 🧵
Questions? Send me a message – I'm happy to help! 💛"""

def details(W, H, dmc, level):
    s = lambda n: f"{W/n:.1f} × {H/n:.1f} in ({W/n*2.54:.1f} × {H/n*2.54:.1f} cm)"
    return f"""━━━━━━━━━━━━━━━━━━━━
PATTERN DETAILS
━━━━━━━━━━━━━━━━━━━━
• Stitch count: {W} × {H}
• Colors: {len(dmc)} DMC threads ({', '.join(dmc)})
• Full cross stitches only – no backstitch, no fractional stitches
• Skill level: {level}

Finished size:
• 14 count Aida: {s(14)}
• 16 count Aida: {s(16)}
• 18 count Aida: {s(18)}"""

L = [
 dict(slug='nazar', folder='1_Nazar_Madalyonu', tr='Nazar Madalyonu', price='5,50 $',
  title='Turkish Kilim Cross Stitch Pattern PDF, Evil Eye Nazar Medallion, Geometric Boho Embroidery Chart, Anatolian Rug Design, Instant Download',
  tags=['kilim cross stitch','turkish pattern','evil eye stitch','nazar cross stitch','cross stitch pdf','geometric pattern','boho cross stitch','ethnic embroidery','dmc pattern','modern cross stitch','turkish gift','rug cross stitch','anatolian motif'],
  intro="""Bring the warmth of a handwoven Turkish rug to your hoop. 🧵

This modern cross stitch pattern is inspired by centuries-old Anatolian kilim weaving. Every motif carries a meaning:

• GÖZ (Evil Eye) – the center medallion, woven to protect the home from envy and harm
• KOÇBOYNUZU (Ram's Horn) – strength, heroism and fertility
• SU YOLU (River Path) – the zigzag border, the flow of life and abundance
• YILDIZ (Star) – happiness and good fortune""",
  W=71, H=91, dmc=['347','311','729','712','938','3809'], level='Advanced beginner'),
 dict(slug='tree_of_life', folder='2_Hayat_Agaci', tr='Hayat Ağacı', price='5,50 $',
  title='Tree of Life Cross Stitch Pattern PDF, Turkish Kilim Embroidery Chart, Anatolian Folk Art, Boho Botanical Cross Stitch, Instant Download',
  tags=['tree of life stitch','kilim cross stitch','turkish pattern','folk art pattern','cross stitch pdf','botanical stitch','boho cross stitch','ethnic embroidery','dmc pattern','modern cross stitch','family tree gift','anatolian motif','tree cross stitch'],
  intro="""A symbol of life, family and roots — stitched in the colors of a Turkish kilim. 🌳

The Tree of Life is one of the oldest motifs in Anatolian weaving:

• HAYAT AĞACI (Tree of Life) – immortality, family roots and the hope that life goes on
• GÖZ (Evil Eye) – a protective diamond crowning the tree
• BAKLAVA (Diamond) – small wishes for protection and good luck
• SU YOLU (River Path) – the zigzag border, the flow of life and abundance

A meaningful gift for a new home, a wedding or a family celebration.""",
  W=61, H=85, dmc=['347','311','729','712','938','3809','3363'], level='Advanced beginner'),
 dict(slug='elibelinde', folder='3_Elibelinde', tr='Elibelinde', price='5,50 $',
  title='Elibelinde Cross Stitch Pattern PDF, Turkish Kilim Goddess Motif, Feminine Folk Art Embroidery Chart, Anatolian Symbol, Instant Download',
  tags=['kilim cross stitch','turkish pattern','goddess cross stitch','feminine folk art','cross stitch pdf','motherhood gift','boho cross stitch','ethnic embroidery','dmc pattern','modern cross stitch','elibelinde','anatolian motif','women symbol stitch'],
  intro="""Three "hands-on-hips" figures — the ancient Anatolian symbol of women. 🤲

ELİBELİNDE is one of the most beloved kilim motifs, woven by women for thousands of years:

• ELİBELİNDE (Hands on Hips) – motherhood, fertility and the strength of women
• KOÇBOYNUZU (Ram's Horn) – strength beside the female figure: together, a happy and fertile home
• BAKLAVA (Diamond) – small wishes for protection and good luck
• SU YOLU (River Path) – the zigzag border, the flow of life and abundance

A beautiful gift for a mother, a sister or a friend.""",
  W=57, H=89, dmc=['347','311','729','712','938','3809'], level='Advanced beginner'),
 dict(slug='bereket', folder='4_Bereket', tr='Bereket', price='5,50 $',
  title='Turkish Kilim Cross Stitch Pattern PDF, Square Medallion Pillow Design, Geometric Abundance Motif, Anatolian Rug Chart, Instant Download',
  tags=['kilim cross stitch','turkish pattern','square cross stitch','pillow cross stitch','cross stitch pdf','geometric pattern','boho cross stitch','ethnic embroidery','dmc pattern','modern cross stitch','housewarming gift','rug cross stitch','anatolian motif'],
  intro="""A square kilim medallion of abundance — perfect for a pillow, a framed piece or a housewarming gift. 🌾

BEREKET means abundance and blessing in Turkish:

• BEREKET (Abundance) – layered diamonds wishing for a full table and a home that never lacks
• KOÇBOYNUZU (Ram's Horn) – four horns facing outward, protecting the abundance
• GÖZ (Evil Eye) – protective eyes in every corner
• SU YOLU (River Path) – the zigzag border, the flow of life""",
  W=71, H=71, dmc=['347','311','729','712','938','3809'], level='Advanced beginner'),
 dict(slug='mini_nazar', folder='5_Mini_Nazar_Seti', tr='Mini Nazar Seti', price='3,50 $',
  title='Evil Eye Cross Stitch Pattern Set PDF, 4 Mini Turkish Nazar Designs, Easy Beginner Embroidery, Small Quick Stitch Gift, Instant Download',
  tags=['evil eye stitch','nazar cross stitch','mini cross stitch','beginner pattern','cross stitch pdf','small cross stitch','quick stitch','turkish pattern','evil eye gift','protection symbol','dmc pattern','bookmark pattern','easy cross stitch'],
  intro="""Four small evil eye motifs — quick, easy and full of meaning. 🧿

The NAZAR BONCUĞU (evil eye bead) is Türkiye's most famous protective symbol. This set includes 4 mini designs:

• Classic Nazar – the famous blue eye bead
• Kilim Nazar – warm reds and golds
• Sea Nazar – turquoise and white, like the Aegean coast
• Earth Nazar – Anatolian earth tones

Each motif is about 2 × 2 inches on 14 count Aida — perfect for cards, bookmarks, ornaments, keychains and small gifts. Great for beginners!""",
  W=53, H=53, dmc=['347','311','729','712','938','3809','820','3846','Blanc','310'], level='Beginner'),
]

out = ["# StitchAnatolia · 5 Ürünün Etsy İlan Metinleri\n",
       "Her ürün için: başlığı, 13 etiketi (tek tek) ve açıklamayı ilgili kutulara kopyala.\n",
       "**Ortak ayarlar (5 ürün için aynı):** Digital files · I did · Kategori: Craft Supplies & Tools → Patterns & How To → **Cross Stitch Patterns**\n"]
for it in L:
    assert len(it['title']) <= 140, (it['slug'], len(it['title']))
    assert len(it['tags']) == 13, it['slug']
    bad = [t for t in it['tags'] if len(t) > 20]; assert not bad, bad
    desc = it['intro'] + "\n\nDesigned in Taşköprü, a small town in northern Türkiye.\n\n" + details(it['W'], it['H'], it['dmc'], it['level']) + "\n\n" + COMMON_NOTE
    out.append(f"\n---\n\n## {it['folder'].split('_',1)[0]}. {it['tr']}  ·  Önerilen fiyat: **{it['price']}**\n")
    out.append(f"**Klasör:** `{it['folder']}` → PDF'i ürün dosyası olarak, 2 görseli ilan görseli olarak yükle.\n")
    out.append(f"**Başlık** ({len(it['title'])}/140):\n```\n{it['title']}\n```\n")
    out.append("**Etiketler:**\n```\n" + "\n".join(it['tags']) + "\n```\n")
    out.append("**Açıklama:**\n```\n" + desc + "\n```\n")
out.append("""
---

## ⚠️ Yayınlamadan önce
- **Yapay zekâ beyanı:** Etsy kuralları gerektiriyorsa her açıklamanın sonuna şunu ekle:
  `This pattern was designed with the help of digital and AI design tools and carefully checked by hand.`
- **Fiyat:** İlk satış ve yorumlar gelene kadar bu fiyatlarda kalalım. Sonra 1 $ artırırız.
- **Sıra:** Önce Nazar Madalyonu'nu yükle, sonra diğerlerini aynı gün içinde ekle.
""")
open('out/ETSY_5_URUN_ILAN_METINLERI.md', 'w').write('\n'.join(out))
print('ok', [ (i['slug'], len(i['title'])) for i in L])
