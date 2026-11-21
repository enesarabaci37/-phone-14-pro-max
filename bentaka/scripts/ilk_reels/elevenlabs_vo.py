#!/usr/bin/env python3
"""ElevenLabs ile Türkçe seslendirme (v4). Anahtar ortamın Network secrets bölümünde, proxy ekler.
Kullanım: python3 elevenlabs_vo.py <voice_id>   (Fatih Yıldırım: 7VqWGAWwo2HMrylfKrcm). Çıktı: l*.mp3, t*.wav (bulunulan klasöre)
Ardından: python3 retime.py <bu_klasör> 1.05 → music.py → render_overlay.js → compose.py
"""
import json, subprocess, sys, urllib.request
VOICE = sys.argv[1]
L = [
 "Geta altı nihayet çıktı. Ama sana kaça mal oldu?",
 "Fiyatına değil; kaç saat çalışman gerektiğine baktık.",
 "Türkiye'de üç bin dokuz yüz doksan dokuz lira. Almanya'da ve Amerika'da yetmiş dokuz doksan dokuz. Fiyatlar yakın… ama maaşlar değil.",
 "Saatlik asgari ücret: Almanya'da on üç doksan avro, Amerika'da yedi yirmi beş dolar, Türkiye'de yüz kırk altı lira seksen kuruş.",
 "Almanya'da beş virgül sekiz saat. Amerika'da on bir saat. Türkiye'de… yirmi yedi virgül iki saat. Almanya'nın neredeyse beş katı!",
 "Bu, üç buçuk iş gününden fazla. Haftanın yarısından fazlası.",
 "Altimit sürüm mü? Otuz dört saat.",
 "Bunu Geta altı bekleyen arkadaşına gönder. Sence bu fiyata değer mi? Yorumlara yaz.",
 "Bentaka. Fyuçır, först.",
]
for i, t in enumerate(L, 1):
    body = {"text": t, "model_id": "eleven_v4", "language_code": "tr",
            "previous_text": L[i-2] if i > 1 else None, "next_text": L[i] if i < len(L) else None,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True, "speed": 1.05}}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    open(f"l{i}.mp3", "wb").write(urllib.request.urlopen(req).read())
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",f"l{i}.mp3","-af",
      "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
      "-ar","48000","-ac","1",f"t{i}.wav"], check=True)
    d = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"t{i}.wav"]).decode().strip()
    print(f"t{i} {d}")
