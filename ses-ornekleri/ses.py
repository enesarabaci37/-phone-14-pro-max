"""Azure Speech ile Türkçe seslendirme.

Kullanım:  python3 ses.py            -> örnek sesleri üretir
Kodda:     from ses import seslendir; seslendir(metin, "cikti.mp3", ses="tr-TR-AhmetNeural")
Gerekli ortam değişkenleri: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
"""
import os, sys, urllib.request, urllib.error
from xml.sax.saxutils import escape

def seslendir(metin, cikti, ses="tr-TR-AhmetNeural", stil=None, hiz="0%"):
    anahtar = os.environ["AZURE_SPEECH_KEY"]
    bolge = os.environ.get("AZURE_SPEECH_REGION", "northeurope")
    icerik = f'<prosody rate="{hiz}">{escape(metin)}</prosody>'
    if stil:
        icerik = f'<mstts:express-as style="{stil}">{icerik}</mstts:express-as>'
    ssml = ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="tr-TR">'
            f'<voice name="{ses}">{icerik}</voice></speak>')
    istek = urllib.request.Request(
        f"https://{bolge}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={"Ocp-Apim-Subscription-Key": anahtar,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "audio-48khz-192kbitrate-mono-mp3",
                 "User-Agent": "arabaci-reklam-ses"})
    with urllib.request.urlopen(istek, timeout=60) as yanit:
        veri = yanit.read()
    with open(cikti, "wb") as f:
        f.write(veri)
    return len(veri)

METIN = ("Merhaba, ben Enes. Bugün yeni 3D yazıcımla, kutu oyunları için "
         "özel bir düzenleyici basıyoruz. Parçalar tek seferde, dört renk birden çıkıyor. "
         "Sonucu videonun sonunda göreceksiniz, kanala abone olmayı unutmayın!")

ORNEKLER = [
    ("1-ahmet-klasik",       "tr-TR-AhmetNeural", None),
    ("2-emel-klasik",        "tr-TR-EmelNeural", None),
    ("3-aydin-samimi",       "tr-TR-Aydin:MAI-Voice-2.1-Flash", "friendlycheerful"),
    ("4-elif-samimi",        "tr-TR-Elif:MAI-Voice-2.1-Flash", "friendlycheerful"),
    ("5-grant-anlatici",     "tr-TR-Grant:MAI-Voice-2.1-Flash", "narrator"),
]

if __name__ == "__main__":
    klasor = os.path.dirname(os.path.abspath(__file__))
    for ad, ses, stil in ORNEKLER:
        try:
            n = seslendir(METIN, os.path.join(klasor, ad + ".mp3"), ses, stil)
            print(f"OK   {ad}  ({n//1024} KB)")
        except urllib.error.HTTPError as e:
            print(f"HATA {ad}  HTTP {e.code} {e.read()[:200]!r}", file=sys.stderr)
