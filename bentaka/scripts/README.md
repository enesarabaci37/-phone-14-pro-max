# Bentaka varlık üretim betikleri

Bu betikler marka kitini ve içerikleri üretir. İlk oturumda geçici bir klasör (scratchpad) için yazıldıkları için dosya yollarının başında sabit değerler var. Yeniden çalıştırmadan önce `build.py` içindeki `SP`, `OUT` ve `FONTDIR` değişkenlerini kendi klasörüne göre değiştir.

## Gerekenler
- **Python paketleri:** `pip install fonttools brotli uharfbuzz cairosvg reportlab pillow numpy`
- **Node:** `playwright` (Chromium hazır kurulu olmalı)
- **Diğer:** `ffmpeg`
- **Sora fontu:** `FONTDIR` klasörüne `Sora-Regular.ttf`, `Sora-SemiBold.ttf` ve `Sora-Bold.ttf` dosyalarını indir. Google Fonts css2 API'sindeki .ttf bağlantıları kullanılabilir. Inter ve JetBrains Mono sistemde kurulu olmalı (`fonts-inter`, `fonts-jetbrains-mono`).
- **Seslendirme önizlemesi için:** `pip install piper-tts faster-whisper` ve `tr_TR-dfki-medium` modeli. Bu modelin lisansı CC BY-NC-SA, yani ticari kullanıma uygun değil.

## Dosyalar
- `build.py`: Vektör logoları üretir. Yazıları fontTools ve HarfBuzz ile vektör çizgiye çevirir. Ayrıca PNG'leri, CMYK PDF ve EPS baskı dosyalarını, sosyal medya ve web görsellerini, renk paletini (PNG, CMYK PDF, ASE, TXT) ve font zip'ini üretir.
- `guide.py` ve `print.js`: Marka kılavuzunu üretir (HTML'den Playwright ile PDF).
- `render_posts.js`: Tuvaldeki gönderi şablonlarını (.dc.html) 1080×1350 PNG'ye çevirir.
- `gta/gta.py` ve `gta/render.js`: GTA 6 gönderisini (5 sayfa) ve 18 saniyelik sessiz Reels'i üretir. Reels kare kare çekilip ffmpeg ile birleştirilir.
- `gta/reels_voice.py` ve `gta/render_reels.js`: Seslendirme sürelerine göre zamanlanmış Reels'i, ses dosyasını (voice.wav) ve seslendirme metnini üretir.

## Örnek ffmpeg komutu (kareleri ve sesi birleştirmek için)
```
ffmpeg -framerate 30 -i frames_v/f%04d.jpg -i voice.wav -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -af "highpass=f=80,acompressor=threshold=-20dB:ratio=2.5,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4
```
