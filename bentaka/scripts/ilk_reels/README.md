# Bentaka ilk Reels: "GTA 6 için kaç saat çalışman gerekiyor?"

54 saniye, 1080×1920, 30 fps. Görseller ve müzik bu klasördeki betiklerle üretilir. Hepsi özgün olduğu için telif sorunu yok: oyun görseli, logo ya da karakter kullanılmadı.

## Dosyalar
- `reels.html`: Bütün sahneler ve animasyonlar. `window.render(t)` fonksiyonu verilen saniyedeki kareyi çizer.
- `render_reels.js`: Kareleri çeker. Kullanımı: `node render_reels.js reels.html 54 <kare_klasörü> 4.3 <kapak.png>`
- `music.py`: 120 BPM özgün müziği ve görüntüyle senkron efektleri (geçiş sesleri, darbeler, sayaç tıkları) üretir.
- Fontlar `bentaka/fonts/` klasöründen yüklenir.

## Birleştirme
```
ffmpeg -framerate 30 -i frames/f%04d.jpg -i music.wav -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart reels.mp4
```

## Sahne akışı (saniye)
| Zaman | Sahne | Ekrandaki yazı |
|---|---|---|
| 0–5 | Kanca | GTA 6 çıktı. Ama sana kaça mal oldu? |
| 5–9 | Soru | Bu oyun için kaç saat çalışman gerekiyor? |
| 9–16 | Fiyatlar | 3.999 TL · 79,99 € · 79,99 $ → "ama maaşlar değil." |
| 16–22 | Saatlik ücret | 13,90 € · 7,25 $ · 146,80 TL |
| 22–33 | Sonuç | Almanya 5,8 · ABD 11,0 · Türkiye 27,2 saat → "neredeyse 5 katı" |
| 33–39 | İş günü | 3,6 iş günü |
| 39–44 | Ultimate | 4.999 TL = 34 saat ≈ 4,5 iş günü |
| 44–49 | Çağrı | Arkadaşına gönder · Kaydet · Yorumlara yaz |
| 49–54 | Kapanış | bentaka · Future, first. · kaynaklar |

## Seslendirme metni (Higgsfield'da üretilecek)
Her satırı ayrı bir dosya olarak üret. Böylece her satırı kendi sahnesinin başına yerleştirebilirim.

1. (0,3 sn) GTA 6 nihayet çıktı. Ama sana kaça mal oldu?
2. (5,2 sn) Fiyatına değil, kaç saat çalışman gerektiğine baktık.
3. (9,4 sn) Türkiye'de üç bin dokuz yüz doksan dokuz lira. Almanya'da ve Amerika'da yetmiş dokuz doksan dokuz. Fiyatlar yakın… ama maaşlar değil.
4. (16,3 sn) Saatlik asgari ücret: Almanya'da on üç doksan euro, Amerika'da yedi yirmi beş dolar, Türkiye'de yüz kırk altı lira seksen kuruş.
5. (22,5 sn) Almanya'da beş virgül sekiz saat. Amerika'da on bir saat. Türkiye'de… yirmi yedi virgül iki saat. Almanya'nın neredeyse beş katı.
6. (33,3 sn) Bu, üç buçuk iş gününden fazla. Haftanın yarısından fazlası.
7. (39,3 sn) Ultimate sürüm mü? Otuz dört saat.
8. (44,2 sn) Bunu GTA 6 bekleyen arkadaşına gönder. Sence bu fiyata değer mi? Yorumlara yaz.
9. (49,5 sn) Bentaka. Future, first.

Sayılar yazıyla verildi, böylece seslendirme modeli onları doğru okur.

## Gönderi açıklaması (Instagram)
GTA 6 çıktı 🎮 Peki onu almak için kaç saat çalışman gerekiyor?

2026 asgari ücretiyle hesapladık:
🇩🇪 Almanya: 5,8 saat
🇺🇸 ABD: 11 saat
🇹🇷 Türkiye: 27,2 saat (3,5 iş gününden fazla)

Sence bu fiyata değer mi? Yorumlara yaz, GTA 6 bekleyen arkadaşına gönder.

Kaynak: PlayStation Store TR / DE / US (dijital, Standart 3.999 TL / 79,99 € / 79,99 $). Brüt asgari ücret: TR 33.030 TL ÷ 225 saat = 146,80 TL, DE 13,90 €, ABD federal 7,25 $.

Geleceği ilk sen gör. @bentaka

#gta6 #gta #playstation #ps5 #xbox #oyun #asgariücret #teknoloji #bentaka
