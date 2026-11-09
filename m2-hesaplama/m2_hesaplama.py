"""Arabacı Reklam - m² Hesaplama programı.

- Müşteri ekranı: çok kalemli teklif (m² malzemeler + hizmetler), KDV, minimum ücret, yuvarlama,
  logolu PDF teklif, WhatsApp metni.
- KDV ve İndirim ekranı.
- Şifreli Yönetim: malzemeler ve hizmetler (alış / maliyet, TL / Dolar / Euro, TCMB kuru),
  teklifin kârı, kayıtlar ve kâr raporu (PDF), firma bilgileri ve teklif notları, ayarlar.
- Veriler isteğe bağlı olarak Google Drive klasöründe tutulur (bilgisayarlar arası ortak).
"""

import datetime
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox, simpledialog, ttk

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas as pdf_canvas
    PDF_VAR = True
except ImportError:  # pragma: no cover
    PDF_VAR = False

UYGULAMA_ADI = "Arabacı Reklam - m² Hesaplama"
SURUM = "4.0"

VARSAYILAN_FIRMA = {
    "ad": "ARABACI REKLAM",
    "adres": "Tabakhane Mah., Taş Camii Sk. No: 11/A, 37400 Taşköprü / Kastamonu",
    "tel": "0534 080 26 79",
    "web": "arabacireklam.com",
    "eposta": "",
    "iban": "",
    "logo": "",
}

BIRIMLER = {"cm": 0.01, "mm": 0.001, "m": 1.0}
KDV_ORANLARI = ["0", "1", "5", "10", "15", "20"]
PARA_BIRIMLERI = ["TL", "Dolar", "Euro"]
YUVARLAMA_ADIMLARI = ["1", "5", "10", "50", "100"]
HIZMET_TIPLERI = {"Sabit": "sabit", "Adet başına": "adet", "m² başına": "m2"}
HIZMET_TIP_ADI = {v: k for k, v in HIZMET_TIPLERI.items()}
TCMB_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
VARSAYILAN_MALZEMELER = [
    "Baskı Folyo", "Branda Avrupa", "Branda Çin", "Kesim Folyo", "Şeffaf Baskı Folyosu",
    "Dekoratif Folyo", "Kanvas Baskı", "Cam Filmi", "PPF",
]
VARSAYILAN_HIZMETLER = [("Montaj", "adet"), ("Tasarım", "sabit"), ("Söküm", "adet"), ("Nakliye", "sabit")]
SIFRE_TUZ = "arabaci-m2::"
APP_ID = "ArabaciReklam.M2Hesaplama"

KIRMIZI = "#d62828"
YESIL = "#1e8e3e"
MAVI = "#1f5fbf"
GRI = "#666666"


# ================================================================ yardımcılar

def sayi_oku(metin):
    """'1.234,5', '1234,5', '1234.5' gibi girişleri sayıya çevirir. Boş/hatalıysa None."""
    s = (str(metin) if metin is not None else "").strip().replace(" ", "").replace("%", "")
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def sayi_yaz(x, basamak=2):
    return f"{x:,.{basamak}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def para(x, birim="TL"):
    return f"{sayi_yaz(x)} {birim}"


def kisa(x):
    """120 -> '120', 10.5 -> '10,5'."""
    return sayi_yaz(x, 0) if float(x).is_integer() else sayi_yaz(x, 2).rstrip("0").rstrip(",")


def m2_hesapla(en, boy, birim, adet):
    c = BIRIMLER[birim]
    tek = (en * c) * (boy * c)
    return tek, tek * adet


def kdv_hesapla(haric, oran):
    kdv = haric * oran / 100
    return kdv, haric + kdv


def yuvarla(x, adim):
    return math.floor(x / adim + 0.5) * adim


def teklif_toplami(kalemler, kdv_orani, min_tutar=0, yuvarlama_adimi=0):
    """Kalemlerden müşteri toplamını hesaplar.

    ara: kalemlerin toplamı (KDV hariç); min_fark: minimum teklif tutarına tamamlama;
    yuvarlama: genel toplam yuvarlanınca KDV hariç tutara yansıyan fark.
    """
    ara = sum(k["tutar"] for k in kalemler)
    min_fark = max(0.0, (min_tutar or 0) - ara) if kalemler else 0.0
    haric1 = ara + min_fark
    dahil1 = haric1 * (1 + kdv_orani / 100)
    if yuvarlama_adimi and dahil1 > 0:
        dahil = yuvarla(dahil1, yuvarlama_adimi)
        haric = dahil / (1 + kdv_orani / 100)
    else:
        dahil, haric = dahil1, haric1
    return {"ara": ara, "min_fark": min_fark, "yuvarlama": haric - haric1,
            "haric": haric, "kdv": dahil - haric, "dahil": dahil}


def indirim_hesapla(islem, normal=None, indirimli=None, oran=None):
    """Üç işlem: 'indirimli', 'normal', 'oran'. (normal, indirimli, oran, tutar) ya da None döner."""
    try:
        if islem == "indirimli" and normal is not None and oran is not None:
            indirimli = normal * (1 - oran / 100)
        elif islem == "normal" and indirimli is not None and oran is not None and oran < 100:
            normal = indirimli / (1 - oran / 100)
        elif islem == "oran" and normal and indirimli is not None:
            oran = (normal - indirimli) / normal * 100
        else:
            return None
    except ZeroDivisionError:
        return None
    return normal, indirimli, oran, normal - indirimli


def sifre_ozet(sifre):
    return hashlib.sha256((SIFRE_TUZ + sifre).encode("utf-8")).hexdigest()


def kaynak_yolu(ad):
    taban = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(taban, ad)


def dosya_ac(yol):
    try:
        if sys.platform.startswith("win"):
            os.startfile(yol)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", yol])
        else:
            subprocess.Popen(["xdg-open", yol], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def tcmb_kurlari():
    istek = urllib.request.Request(TCMB_URL, headers={"User-Agent": "ArabaciM2/4.0"})
    with urllib.request.urlopen(istek, timeout=10) as yanit:
        kok = ET.fromstring(yanit.read())
    sonuc = {"tarih": kok.get("Tarih", "")}
    for cur in kok.findall("Currency"):
        satis = cur.findtext("ForexSelling")
        if cur.get("Kod") == "USD" and satis:
            sonuc["Dolar"] = float(satis)
        elif cur.get("Kod") == "EUR" and satis:
            sonuc["Euro"] = float(satis)
    return sonuc


# ================================================================ veri

def yerel_klasor():
    k = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "ArabaciM2")
    os.makedirs(k, exist_ok=True)
    return k


def yerel_ayar_oku():
    """Bu bilgisayara özel ayarlar (veri klasörü, ekran seçimleri)."""
    try:
        with open(os.path.join(yerel_klasor(), "bu_bilgisayar.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def yerel_ayar_yaz(ayar):
    try:
        with open(os.path.join(yerel_klasor(), "bu_bilgisayar.json"), "w", encoding="utf-8") as f:
            json.dump(ayar, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def kayitlari_birlestir(a, b, silinen=()):
    """İki kayıt listesini kimliğe göre birleştirir, silinenleri çıkarır, numaraya göre sıralar."""
    silinen = set(silinen)
    hepsi = {}
    for k in list(a) + list(b):
        if k.get("id") and k["id"] not in silinen:
            hepsi.setdefault(k["id"], k)
    return sorted(hepsi.values(), key=lambda k: (k.get("no", 0), k.get("tarih", "")))


def eski_kaydi_cevir(k):
    """v2/v3 tek kalemli kaydı çok kalemli yapıya çevirir (yerinde)."""
    if "kalemler" in k:
        return k
    k["kalemler"] = [{
        "tur": "malzeme", "ad": k.get("malzeme") or "-", "olcu": k.get("olcu", ""), "adet": k.get("adet", 1),
        "m2": k.get("m2", 0), "fatura_m2": k.get("m2", 0), "birim_fiyat": k.get("satis_m2", 0),
        "tutar": k.get("satis_haric", 0), "maliyet": k.get("maliyet_haric"),
        "alis_fiyat": k.get("alis_fiyat", ""), "alis_para": k.get("alis_para", ""), "kur": k.get("kur"),
        "alis_tl_m2": k.get("alis_tl_m2"), "fire": k.get("fire", 0),
    }]
    k.setdefault("ara", k.get("satis_haric", 0))
    k.setdefault("min_fark", 0)
    k.setdefault("yuvarlama", 0)
    return k


class Veri:
    """Malzemeler, hizmetler, kayıtlar, kurlar, firma, ayarlar: <veri klasörü>\\veriler.json

    Veri klasörü Google Drive içinde olabilir; birden fazla bilgisayar aynı dosyayı kullanır.
    Kaydederken diskteki dosya yeniden okunur ve teklif kayıtları birleştirilir.
    """

    def __init__(self, klasor=None):
        self.klasor = klasor or yerel_klasor()
        os.makedirs(self.klasor, exist_ok=True)
        self.yol = os.path.join(self.klasor, "veriler.json")
        d = self._oku()
        if d is None:  # bozuk dosya: yedekle, boş başla
            try:
                os.replace(self.yol, self.yol + f".bozuk-{datetime.datetime.now():%Y%m%d%H%M%S}")
            except Exception:
                pass
            d = {}
        self.d = self._varsayilanlar(d)
        self._zaman = self._dosya_zamani()

    @staticmethod
    def _varsayilanlar(d):
        d.setdefault("malzemeler", [
            {"ad": ad, "alis": "", "para": "Euro", "satis": "", "fire": "0"} for ad in VARSAYILAN_MALZEMELER
        ])
        for m in d["malzemeler"]:
            m.setdefault("min_m2", "")
        d.setdefault("hizmetler", [
            {"ad": ad, "tip": tip, "satis": "", "maliyet": ""} for ad, tip in VARSAYILAN_HIZMETLER
        ])
        d.setdefault("kayitlar", [])
        d.setdefault("silinen_kayitlar", [])
        d.setdefault("kurlar", {})
        d.setdefault("son_teklif_no", 0)
        d.setdefault("sifre", None)
        d.setdefault("alis_kdv", "20")
        firma = d.setdefault("firma", {})
        for a, v in VARSAYILAN_FIRMA.items():
            firma.setdefault(a, v)
        d.setdefault("teklif_notu", "")
        ayar = d.setdefault("fiyat_kurallari", {})
        ayar.setdefault("yuvarla", True)
        ayar.setdefault("adim", "10")
        ayar.setdefault("min_tutar", "")
        d.pop("ekran", None)
        for k in d["kayitlar"]:
            k.setdefault("id", f"eski-{k.get('no')}-{k.get('tarih')}")
            eski_kaydi_cevir(k)
        return d

    def _oku(self):
        """Dosyayı okur. Yoksa {}, okunamıyorsa (yarım senkron vb.) None döner."""
        if not os.path.exists(self.yol):
            return {}
        for _ in range(3):
            try:
                with open(self.yol, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                time.sleep(0.3)
        return None

    def _dosya_zamani(self):
        try:
            return os.path.getmtime(self.yol)
        except OSError:
            return None

    def yenile(self):
        """Dosya başka bir bilgisayarda değiştiyse yeniden yükler. Değiştiyse True."""
        z = self._dosya_zamani()
        if z is None or z == self._zaman:
            return False
        d = self._oku()
        if not d:
            return False
        self.d = self._varsayilanlar(d)
        self._zaman = z
        return True

    def kaydet(self):
        disk = self._oku()
        if disk:
            disk = self._varsayilanlar(disk)
            silinen = sorted(set(self.d["silinen_kayitlar"]) | set(disk["silinen_kayitlar"]))
            self.d["silinen_kayitlar"] = silinen
            self.d["kayitlar"] = kayitlari_birlestir(self.d["kayitlar"], disk["kayitlar"], silinen)
            self.d["son_teklif_no"] = max(self.d["son_teklif_no"], disk["son_teklif_no"])
        metin = json.dumps(self.d, ensure_ascii=False, indent=2)
        gecici = self.yol + ".tmp"
        try:
            with open(gecici, "w", encoding="utf-8") as f:
                f.write(metin)
            os.replace(gecici, self.yol)
        except OSError:
            with open(self.yol, "w", encoding="utf-8") as f:
                f.write(metin)
        self._zaman = self._dosya_zamani()

    def yeni_teklif_no(self):
        self.yenile()
        enbuyuk = max([self.d["son_teklif_no"]] + [k.get("no", 0) for k in self.d["kayitlar"]])
        self.d["son_teklif_no"] = enbuyuk + 1
        return enbuyuk + 1

    def kayitlari_sil(self, kimlikler):
        kimlikler = set(kimlikler)
        self.d["silinen_kayitlar"] = sorted(set(self.d["silinen_kayitlar"]) | kimlikler)
        self.d["kayitlar"] = [k for k in self.d["kayitlar"] if k["id"] not in kimlikler]
        self.kaydet()

    @property
    def malzemeler(self):
        return self.d["malzemeler"]

    @property
    def hizmetler(self):
        return self.d["hizmetler"]

    def malzeme(self, ad):
        return next((m for m in self.malzemeler if m["ad"] == ad), None)

    def hizmet(self, ad):
        return next((h for h in self.hizmetler if h["ad"] == ad), None)

    def kur(self, para_birimi):
        if para_birimi == "TL":
            return 1.0
        return self.d["kurlar"].get(para_birimi)

    def alis_tl_m2(self, m):
        """Malzemenin bugünkü kurla TL m² alış fiyatı (KDV hariç). Fiyat ya da kur yoksa None."""
        if not m:
            return None
        fiyat, kur = sayi_oku(m.get("alis")), self.kur(m.get("para", "TL"))
        if fiyat is None or not kur:
            return None
        return fiyat * kur

    def logo_yolu(self):
        ad = self.d["firma"].get("logo")
        if ad:
            yol = os.path.join(self.klasor, ad)
            if os.path.exists(yol):
                return yol
        return kaynak_yolu("logo.png")

    def kalem_maliyeti(self, k):
        """Kaleme bugünkü alış / maliyet bilgisini ekler (yerinde) ve maliyeti döner (bilinmiyorsa None)."""
        if k["tur"] == "malzeme":
            m = self.malzeme(k["ad"])
            tl = self.alis_tl_m2(m)
            fire = (sayi_oku(m.get("fire")) or 0) if m else 0
            k.update({"alis_fiyat": m.get("alis") if m else "", "alis_para": m.get("para") if m else "",
                      "kur": self.kur(m.get("para")) if m else None, "alis_tl_m2": tl, "fire": fire})
            k["maliyet"] = k["m2"] * (1 + fire / 100) * tl if tl is not None else None
        else:
            h = self.hizmet(k["ad"])
            birim_maliyet = sayi_oku(h.get("maliyet")) if h else None
            k["birim_maliyet"] = birim_maliyet
            k["maliyet"] = (birim_maliyet or 0) * k["miktar"]
        return k["maliyet"]


# ================================================================ PDF

_FONTLAR = None


def pdf_fontlari():
    global _FONTLAR
    if _FONTLAR:
        return _FONTLAR
    adaylar = [
        (kaynak_yolu(os.path.join("fonts", "DejaVuSans.ttf")), kaynak_yolu(os.path.join("fonts", "DejaVuSans-Bold.ttf"))),
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
    ]
    for normal, kalin in adaylar:
        if os.path.exists(normal) and os.path.exists(kalin):
            pdfmetrics.registerFont(TTFont("TR", normal))
            pdfmetrics.registerFont(TTFont("TR-B", kalin))
            _FONTLAR = ("TR", "TR-B")
            return _FONTLAR
    _FONTLAR = ("Helvetica", "Helvetica-Bold")
    return _FONTLAR


def pdf_klasoru():
    k = os.path.join(os.path.expanduser("~"), "Documents", "Arabaci Reklam")
    os.makedirs(k, exist_ok=True)
    return k


def _sar(c, metin, font, boyut, genislik):
    """Metni verilen genişliğe göre satırlara böler."""
    satirlar = []
    for paragraf in str(metin).splitlines() or [""]:
        kelimeler, satir = paragraf.split(" "), ""
        for k in kelimeler:
            deneme = (satir + " " + k).strip()
            if c.stringWidth(deneme, font, boyut) <= genislik or not satir:
                satir = deneme
            else:
                satirlar.append(satir)
                satir = k
        satirlar.append(satir)
    return satirlar


def _pdf_baslik(c, baslik, sag_satirlar, logo):
    F, FB = pdf_fontlari()
    gen, yuk = A4
    if logo and os.path.exists(logo):
        try:
            c.drawImage(ImageReader(logo), 18 * mm, yuk - 38 * mm, width=62 * mm, height=17 * mm, mask="auto",
                        preserveAspectRatio=True, anchor="w")
        except Exception:
            pass
    c.setFont(FB, 18)
    c.setFillColor(colors.HexColor(KIRMIZI))
    c.drawRightString(gen - 18 * mm, yuk - 26 * mm, baslik)
    c.setFillColor(colors.black)
    c.setFont(F, 9.5)
    y = yuk - 32 * mm
    for s in sag_satirlar:
        c.drawRightString(gen - 18 * mm, y, s)
        y -= 5 * mm
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.line(18 * mm, yuk - 46 * mm, gen - 18 * mm, yuk - 46 * mm)
    return yuk - 54 * mm


def _pdf_alt(c, firma):
    F, _ = pdf_fontlari()
    gen, _ = A4
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.line(18 * mm, 22 * mm, gen - 18 * mm, 22 * mm)
    c.setFont(F, 8.5)
    c.setFillColor(colors.HexColor(GRI))
    c.drawCentredString(gen / 2, 16 * mm, "  •  ".join(x for x in (firma.get("ad"), firma.get("adres")) if x))
    iletisim = [f"Tel / WhatsApp: {firma['tel']}" if firma.get("tel") else "", firma.get("eposta", ""), firma.get("web", "")]
    c.drawCentredString(gen / 2, 11.5 * mm, "  •  ".join(x for x in iletisim if x))
    c.setFillColor(colors.black)


def _hucre(c, x, y, g, metin, hiza):
    metin = str(metin)
    if hiza == "r":
        c.drawRightString(x + g - 2 * mm, y - 1 * mm, metin)
    elif hiza == "c":
        c.drawCentredString(x + g / 2, y - 1 * mm, metin)
    else:
        c.drawString(x + 2 * mm, y - 1 * mm, metin)


def _tablo(c, x, y, sutunlar, satirlar, hizalar, genislikler, firma, kalin_son=False):
    """Basit tablo çizer, yeni y döner. Sayfa taşarsa yeni sayfa açar."""
    F, FB = pdf_fontlari()
    sat_yuk = 7.5 * mm

    def baslik_ciz(yy):
        c.setFillColor(colors.HexColor("#f1f1f1"))
        c.rect(x, yy - sat_yuk + 2 * mm, sum(genislikler), sat_yuk, stroke=0, fill=1)
        c.setFillColor(colors.black)
        c.setFont(FB, 9)
        xx = x
        for s, h, g in zip(sutunlar, hizalar, genislikler):
            _hucre(c, xx, yy, g, s, h)
            xx += g
        return yy - sat_yuk

    y = baslik_ciz(y)
    for i, satir in enumerate(satirlar):
        if y < 35 * mm:
            _pdf_alt(c, firma)
            c.showPage()
            y = baslik_ciz(A4[1] - 25 * mm)
        son = kalin_son and i == len(satirlar) - 1
        c.setFont(FB if son else F, 9)
        xx = x
        for s, h, g in zip(satir, hizalar, genislikler):
            _hucre(c, xx, y, g, s, h)
            xx += g
        c.setStrokeColor(colors.HexColor("#e2e2e2"))
        c.line(x, y - 2.5 * mm, x + sum(genislikler), y - 2.5 * mm)
        y -= sat_yuk
    return y


def kalem_satiri(k):
    """PDF / tablo için (açıklama, detay, miktar, birim fiyat, tutar)."""
    if k["tur"] == "malzeme":
        detay = f"{k['olcu']} × {kisa(k['adet'])} adet"
        miktar = f"{sayi_yaz(k['fatura_m2'], 2)} m²" + (" (min.)" if k["fatura_m2"] > k["m2"] + 1e-9 else "")
    else:
        detay = HIZMET_TIP_ADI.get(k.get("tip"), "")
        miktar = {"sabit": "1", "adet": f"{kisa(k['miktar'])} adet", "m2": f"{sayi_yaz(k['miktar'], 2)} m²"}.get(
            k.get("tip"), kisa(k["miktar"]))
    return k["ad"], detay, miktar, para(k["birim_fiyat"]), para(k["tutar"])


def musteri_pdf(kayit, yol, firma, logo, notlar=""):
    F, FB = pdf_fontlari()
    gen, _ = A4
    c = pdf_canvas.Canvas(yol, pagesize=A4)
    c.setTitle(f"Fiyat Teklifi {kayit['no']}")
    y = _pdf_baslik(c, "FİYAT TEKLİFİ", [f"Teklif No: {kayit['no']}", f"Tarih: {kayit['tarih']}"], logo)
    if kayit.get("musteri"):
        c.setFont(F, 10)
        c.drawString(18 * mm, y, "Sayın")
        c.setFont(FB, 12)
        c.drawString(18 * mm, y - 6 * mm, kayit["musteri"])
        y -= 16 * mm
    gen_ic = gen - 36 * mm
    gens = [gen_ic * o for o in (0.06, 0.25, 0.25, 0.14, 0.15, 0.15)]
    satirlar = [[str(i), *kalem_satiri(k)] for i, k in enumerate(kayit["kalemler"], 1)]
    y = _tablo(c, 18 * mm, y, ["#", "Malzeme / Hizmet", "Ölçü / Detay", "Miktar", "Birim Fiyat", "Tutar"],
               satirlar, ["c", "l", "l", "r", "r", "r"], gens, firma)
    y -= 6 * mm
    sx = gen - 18 * mm
    duzeltme = kayit.get("min_fark") or abs(kayit.get("yuvarlama") or 0) >= 0.005
    toplam_satirlari = [("Ara Toplam", para(kayit["ara"]), False)] if duzeltme else []
    if kayit.get("min_fark"):
        toplam_satirlari.append(("Minimum ücret farkı", para(kayit["min_fark"]), False))
    if abs(kayit.get("yuvarlama") or 0) >= 0.005:
        toplam_satirlari.append(("Yuvarlama", para(kayit["yuvarlama"]), False))
    toplam_satirlari += [
        ("Toplam (KDV hariç)", para(kayit["satis_haric"]), False),
        (f"KDV (%{kisa(kayit['kdv_orani'])})", para(kayit["satis_kdv"]), False),
        ("GENEL TOPLAM", para(kayit["satis_dahil"]), True),
    ]
    for etiket, deger, kalin in toplam_satirlari:
        if y < 35 * mm:
            _pdf_alt(c, firma)
            c.showPage()
            y = A4[1] - 25 * mm
        c.setFont(FB if kalin else F, 12 if kalin else 10)
        if kalin:
            c.setFillColor(colors.HexColor(KIRMIZI))
        c.drawRightString(sx - 45 * mm, y, etiket)
        c.drawRightString(sx, y, deger)
        c.setFillColor(colors.black)
        y -= 7 * mm
    y -= 6 * mm
    bilgi = []
    if notlar.strip():
        bilgi += _sar(c, notlar.strip(), F, 9.5, gen_ic)
    if firma.get("iban"):
        bilgi.append(f"IBAN: {firma['iban']}" + (f"  ({firma['ad']})" if firma.get("ad") else ""))
    if bilgi:
        c.setFont(FB, 10)
        c.drawString(18 * mm, y, "Notlar")
        y -= 6 * mm
        c.setFont(F, 9.5)
        for s in bilgi:
            if y < 30 * mm:
                _pdf_alt(c, firma)
                c.showPage()
                y = A4[1] - 25 * mm
                c.setFont(F, 9.5)
            c.drawString(18 * mm, y, s)
            y -= 5 * mm
    else:
        c.setFont(F, 9.5)
        c.setFillColor(colors.HexColor(GRI))
        c.drawString(18 * mm, y, "Bilgi ve sipariş için bizi arayabilir ya da WhatsApp'tan yazabilirsiniz.")
        c.setFillColor(colors.black)
    _pdf_alt(c, firma)
    c.save()


def kar_pdf(kayitlar, yol, firma, logo, baslik="KÂR RAPORU"):
    F, FB = pdf_fontlari()
    gen, _ = A4
    c = pdf_canvas.Canvas(yol, pagesize=A4)
    c.setTitle(baslik)
    simdi = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    y = _pdf_baslik(c, baslik, [f"Kayıt sayısı: {len(kayitlar)}", f"Rapor tarihi: {simdi}", "FİRMA İÇİ - GİZLİ"], logo)
    gen_ic = gen - 36 * mm

    if len(kayitlar) == 1:
        k = kayitlar[0]
        c.setFont(FB, 11)
        c.drawString(18 * mm, y, f"Teklif No {k['no']}  •  {k['tarih']}  •  {k.get('musteri') or 'Müşteri adı yok'}")
        y -= 9 * mm
        gens = [gen_ic * o for o in (0.22, 0.32, 0.15, 0.15, 0.16)]
        satirlar = []
        for kl in k["kalemler"]:
            ad, detay, miktar, _, tutar = kalem_satiri(kl)
            if kl["tur"] == "malzeme" and kl.get("alis_fiyat"):
                detay = f"{miktar} • alış {kl['alis_fiyat']} {kl['alis_para']}"
            elif kl["tur"] == "hizmet":
                detay = f"{miktar}"
            mal = kl.get("maliyet")
            satirlar.append([ad, detay, tutar, para(mal) if mal is not None else "-",
                             para(kl["tutar"] - mal) if mal is not None else "-"])
        y = _tablo(c, 18 * mm, y, ["Kalem", "Detay", "Satış", "Maliyet", "Kâr"], satirlar,
                   ["l", "l", "r", "r", "r"], gens, firma)
        y -= 6 * mm
        ozet = [("Kalemler toplamı (KDV hariç)", para(k["ara"]))]
        if k.get("min_fark"):
            ozet.append(("Minimum ücret farkı", para(k["min_fark"])))
        if abs(k.get("yuvarlama") or 0) >= 0.005:
            ozet.append(("Yuvarlama", para(k["yuvarlama"])))
        ozet += [
            ("Satış (KDV hariç)", para(k["satis_haric"])),
            ("Satış (KDV dahil)", para(k["satis_dahil"])),
            ("Toplam maliyet (KDV hariç)", para(k["maliyet_haric"]) if k.get("maliyet_haric") is not None else "eksik"),
            ("KAZANÇ (KDV hariç)", para(k["kar"]) if k.get("kar") is not None else "-"),
            ("Kâr oranı (satışa göre)",
             f"% {sayi_yaz(k['kar'] / k['satis_haric'] * 100, 1)}" if k.get("kar") is not None and k["satis_haric"] else "-"),
        ]
        for etiket, deger in ozet:
            vurgu = etiket.startswith("KAZANÇ")
            c.setFont(FB if vurgu else F, 12 if vurgu else 10.5)
            if vurgu:
                c.setFillColor(colors.HexColor(YESIL if (k.get("kar") or 0) >= 0 else KIRMIZI))
            c.drawString(18 * mm, y, etiket)
            c.drawRightString(gen - 18 * mm, y, deger)
            c.setFillColor(colors.black)
            c.setStrokeColor(colors.HexColor("#e2e2e2"))
            c.line(18 * mm, y - 2.5 * mm, gen - 18 * mm, y - 2.5 * mm)
            y -= 8 * mm
        if k.get("kar") is None:
            c.setFont(F, 8.5)
            c.setFillColor(colors.HexColor(GRI))
            c.drawString(18 * mm, y, "Alış fiyatı girilmemiş malzeme olduğu için kazanç hesaplanamadı.")
            c.setFillColor(colors.black)
    else:
        gens = [gen_ic * o for o in (0.07, 0.13, 0.18, 0.22, 0.13, 0.13, 0.14)]
        satirlar = []
        t_satis = t_maliyet = t_kar = t_satis_maliyetli = 0.0
        for k in kayitlar:
            t_satis += k["satis_haric"]
            if k.get("kar") is not None:
                t_maliyet += k["maliyet_haric"]
                t_kar += k["kar"]
                t_satis_maliyetli += k["satis_haric"]
            satirlar.append([k["no"], k["tarih"][:10], (k.get("musteri") or "-")[:18], (k.get("malzeme") or "-")[:24],
                             sayi_yaz(k["satis_haric"]),
                             sayi_yaz(k["maliyet_haric"]) if k.get("kar") is not None else "-",
                             sayi_yaz(k["kar"]) if k.get("kar") is not None else "-"])
        satirlar.append(["", "", "TOPLAM", "", sayi_yaz(t_satis), sayi_yaz(t_maliyet), sayi_yaz(t_kar)])
        y = _tablo(c, 18 * mm, y, ["No", "Tarih", "Müşteri", "Kalemler", "Satış TL", "Maliyet TL", "Kâr TL"],
                   satirlar, ["c", "l", "l", "l", "r", "r", "r"], gens, firma, kalin_son=True)
        y -= 4 * mm
        c.setFont(F, 8.5)
        c.setFillColor(colors.HexColor(GRI))
        c.drawString(18 * mm, y, "Tutarlar KDV hariçtir. Kâr oranı: " +
                     (f"% {sayi_yaz(t_kar / t_satis_maliyetli * 100, 1)}" if t_satis_maliyetli else "-")
                     + ("   (Maliyeti bilinmeyen kayıtlar kâra ve orana katılmadı.)" if t_satis_maliyetli != t_satis else ""))
        c.setFillColor(colors.black)
    _pdf_alt(c, firma)
    c.save()


# ================================================================ arayüz yardımcıları

class Ortak:
    """Pencerelerde ortak kullanılan form yardımcıları."""

    fa = "Segoe UI"

    def _giris(self, ust, satir, etiket, degisken, genislik=14, sutun=0, show=None, sola=False):
        ttk.Label(ust, text=etiket).grid(row=satir, column=sutun, sticky="w", pady=4, padx=(16 if sutun else 0, 8))
        e = ttk.Entry(ust, textvariable=degisken, width=genislik, font=(self.fa, 12),
                      justify="left" if sola else "right", show=show)
        e.grid(row=satir, column=sutun + 1, sticky="we", pady=4)
        return e

    def _secim(self, ust, satir, etiket, degisken, degerler, sutun=0, genislik=12, serbest=False):
        ttk.Label(ust, text=etiket).grid(row=satir, column=sutun, sticky="w", pady=4, padx=(16 if sutun else 0, 8))
        c = ttk.Combobox(ust, textvariable=degisken, values=degerler, width=genislik,
                         state="normal" if serbest else "readonly", font=(self.fa, 12))
        c.grid(row=satir, column=sutun + 1, sticky="we", pady=4)
        return c

    def _sonuc(self, ust, satir, etiket, stil="Sonuc.TLabel", sutun=0, span=1):
        el = ttk.Label(ust, text=etiket)
        el.grid(row=satir, column=sutun, sticky="w", pady=2, padx=(0, 8))
        v = tk.StringVar(value="—")
        lbl = ttk.Label(ust, textvariable=v, style=stil, anchor="e")
        lbl.grid(row=satir, column=sutun + 1, columnspan=span, sticky="e", pady=2)
        return v, lbl, el

    def _dugme(self, ust, metin, renk, komut, koyu):
        return tk.Button(ust, text=metin, bg=renk, fg="white", activebackground=koyu, activeforeground="white",
                         relief="flat", font=(self.fa, 11, "bold"), padx=12, pady=6, cursor="hand2", command=komut)

    @staticmethod
    def _not(ust, metin, **grid):
        """Pencere genişliğine göre kendini saran açıklama yazısı."""
        lbl = ttk.Label(ust, text=metin, style="Not.TLabel", justify="left")
        lbl.grid(sticky="we", **grid)
        lbl.bind("<Configure>", lambda e: lbl.configure(wraplength=max(200, e.width - 4)))
        return lbl

    @staticmethod
    def _izle(fonk, *degiskenler):
        for d in degiskenler:
            d.trace_add("write", lambda *_: fonk())

    @staticmethod
    def _tablo(ust, sutunlar, yukseklik=8, secim="browse"):
        cer = ttk.Frame(ust)
        t = ttk.Treeview(cer, columns=[s[0] for s in sutunlar], show="headings", selectmode=secim, height=yukseklik)
        for anahtar, baslik, gen, hiza in sutunlar:
            t.heading(anahtar, text=baslik)
            t.column(anahtar, width=gen, anchor=hiza, stretch=True)
        kay = ttk.Scrollbar(cer, orient="vertical", command=t.yview)
        t.configure(yscrollcommand=kay.set)
        t.pack(side="left", fill="both", expand=True)
        kay.pack(side="right", fill="y")
        return cer, t


def windows_simge_ayarla():
    """Görev çubuğunda Python tüyü yerine programın kendi simgesinin görünmesi için."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass


def simge_uygula(pencere):
    try:
        pencere.iconbitmap(default=kaynak_yolu("icon.ico"))
    except Exception:
        pass
    try:
        if not hasattr(pencere, "_simgeler"):
            buyuk = tk.PhotoImage(master=pencere, file=kaynak_yolu("icon.png"))
            pencere._simgeler = [buyuk, buyuk.subsample(4, 4)]
        pencere.iconphoto(True, *pencere._simgeler)
    except Exception:
        pass


# ================================================================ ana pencere

class Uygulama(tk.Tk, Ortak):
    def __init__(self, veri=None):
        windows_simge_ayarla()
        super().__init__()
        self.title(f"{UYGULAMA_ADI}  (v{SURUM})")
        self.minsize(960, 760)
        self.geometry("1020x820")
        simge_uygula(self)

        self.yerel = yerel_ayar_oku()
        self.veri = veri or self._veri_ac()
        self.kalemler = []
        self.hesap = None
        self.yonetim = None
        self._stil()

        defter = ttk.Notebook(self)
        defter.pack(fill="both", expand=True, padx=10, pady=10)
        self.sayfa_fiyat = ttk.Frame(defter, padding=10)
        self.sayfa_kdv = ttk.Frame(defter, padding=10)
        defter.add(self.sayfa_fiyat, text="  Teklif Hazırla  ")
        defter.add(self.sayfa_kdv, text="  KDV ve İndirim  ")

        self._teklif_sayfasi()
        self._kdv_indirim_sayfasi()

        self.protocol("WM_DELETE_WINDOW", self._kapat)
        self.after(200, self.kuru_guncelle)
        self.after(5000, self._senkron_dongu)

    def _veri_ac(self):
        k = self.yerel.get("klasor")
        while k and not os.path.isdir(k):
            self.withdraw()
            if not messagebox.askretrycancel(
                    "Veri klasörü", f"Ortak veri klasörüne ulaşılamıyor:\n{k}\n\n"
                    "Google Drive açık ve oturum açılmış mı? Açtıktan sonra “Yeniden dene”ye basın.\n\n"
                    "“İptal” derseniz bu seferlik bu bilgisayardaki yerel veriler kullanılır.", parent=self):
                k = None
        self.deiconify()
        return Veri(k)

    def _senkron_dongu(self):
        try:
            if self.veri.yenile():
                self.veri_degisti()
        except Exception:
            pass
        self.after(5000, self._senkron_dongu)

    def veri_degisti(self):
        """Veri başka bir bilgisayarda ya da klasör değişince ekranları tazeler."""
        self.listeleri_yenile()
        kurallar = self.veri.d["fiyat_kurallari"]
        if self.v_yuvarla.get() != bool(kurallar["yuvarla"]):
            self.v_yuvarla.set(bool(kurallar["yuvarla"]))
        if self.v_adim.get() != kurallar["adim"]:
            self.v_adim.set(kurallar["adim"])
        self.teklif_hesapla()
        if self.yonetim and self.yonetim.winfo_exists():
            self.yonetim.hepsini_yenile()

    # ------------------------------------------------------------ görünüm
    def _stil(self):
        fa = "Segoe UI" if sys.platform.startswith("win") else "DejaVu Sans"
        Ortak.fa = fa
        for ad in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            try:
                tkfont.nametofont(ad).configure(family=fa, size=11)
            except tk.TclError:
                pass
        s = ttk.Style(self)
        for tema in ("vista", "clam"):
            if tema in s.theme_names():
                s.theme_use(tema)
                break
        s.configure("TNotebook.Tab", font=(fa, 11, "bold"), padding=(10, 6))
        s.configure("Baslik.TLabel", font=(fa, 15, "bold"), foreground=KIRMIZI)
        s.configure("Not.TLabel", font=(fa, 9), foreground=GRI)
        s.configure("Bilgi.TLabel", font=(fa, 10), foreground=MAVI)
        s.configure("Sonuc.TLabel", font=(fa, 12, "bold"))
        s.configure("Buyuk.TLabel", font=(fa, 15, "bold"))
        s.configure("BuyukK.TLabel", font=(fa, 15, "bold"), foreground=KIRMIZI)
        s.configure("Kar.TLabel", font=(fa, 15, "bold"), foreground=YESIL)
        s.configure("Zarar.TLabel", font=(fa, 15, "bold"), foreground=KIRMIZI)
        s.configure("TLabelframe.Label", font=(fa, 12, "bold"), foreground=KIRMIZI)
        s.configure("TButton", font=(fa, 10, "bold"), padding=(8, 4))
        s.configure("Treeview", rowheight=26, font=(fa, 10))
        s.configure("Treeview.Heading", font=(fa, 10, "bold"))

    # ------------------------------------------------------------ sayfa 1: teklif
    def _teklif_sayfasi(self):
        e = self.yerel.get("ekran", {})
        p = self.sayfa_fiyat
        p.columnconfigure(0, weight=1)
        p.rowconfigure(2, weight=1)

        ust = ttk.Frame(p)
        ust.grid(row=0, column=0, sticky="we", pady=(0, 6))
        ust.columnconfigure(1, weight=1)
        self.v_musteri = tk.StringVar()
        ttk.Label(ust, text="Müşteri adı (isteğe bağlı)").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(ust, textvariable=self.v_musteri, font=(self.fa, 12)).grid(row=0, column=1, sticky="we")

        # --- 1) kalem ekle
        ek = ttk.LabelFrame(p, text=" 1) Kalem ekle ", padding=(10, 6))
        ek.grid(row=1, column=0, sticky="we", pady=(0, 6))
        ek.columnconfigure(0, weight=1)
        self.v_tur = tk.StringVar(value="malzeme")
        tur = ttk.Frame(ek)
        tur.grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(tur, text="Malzeme (m²)", value="malzeme", variable=self.v_tur).pack(side="left", padx=(0, 16))
        ttk.Radiobutton(tur, text="Hizmet (montaj, tasarım…)", value="hizmet", variable=self.v_tur).pack(side="left")

        # malzeme formu
        self.f_malz = ttk.Frame(ek)
        fm = self.f_malz
        for i in (1, 3, 5):
            fm.columnconfigure(i, weight=1)
        self.v_malzeme = tk.StringVar(value=e.get("malzeme", ""))
        self.v_birim = tk.StringVar(value=e.get("birim", "cm"))
        self.v_en, self.v_boy, self.v_adet = tk.StringVar(), tk.StringVar(), tk.StringVar(value="1")
        self.v_satis_m2 = tk.StringVar()
        self.c_malzeme = self._secim(fm, 0, "Malzeme", self.v_malzeme, [], sutun=0, genislik=22)
        self.c_malzeme.grid(columnspan=3)
        self._secim(fm, 0, "Ölçü birimi", self.v_birim, list(BIRIMLER), sutun=4, genislik=6)
        self.e_en = self._giris(fm, 1, "En (soldan sağa)", self.v_en, sutun=0, genislik=10)
        self._giris(fm, 1, "Boy (yukarıdan aşağı)", self.v_boy, sutun=2, genislik=10)
        self._giris(fm, 1, "Adet", self.v_adet, sutun=4, genislik=6)
        self._giris(fm, 2, "m² fiyatı (TL, KDV hariç)", self.v_satis_m2, sutun=0, genislik=10)

        # hizmet formu
        self.f_hiz = ttk.Frame(ek)
        fh = self.f_hiz
        for i in (1, 3, 5):
            fh.columnconfigure(i, weight=1)
        self.v_hizmet = tk.StringVar()
        self.v_miktar = tk.StringVar(value="1")
        self.v_hiz_fiyat = tk.StringVar()
        self.c_hizmet = self._secim(fh, 0, "Hizmet", self.v_hizmet, [], sutun=0, genislik=22)
        self.c_hizmet.grid(columnspan=3)
        self.l_miktar = ttk.Label(fh, text="Miktar")
        self.l_miktar.grid(row=1, column=0, sticky="w", pady=4, padx=(0, 8))
        self.e_miktar = ttk.Entry(fh, textvariable=self.v_miktar, width=10, font=(self.fa, 12), justify="right")
        self.e_miktar.grid(row=1, column=1, sticky="we", pady=4)
        self.l_hiz_fiyat = ttk.Label(fh, text="Birim fiyat (TL, KDV hariç)")
        self.l_hiz_fiyat.grid(row=1, column=2, sticky="w", pady=4, padx=(16, 8))
        ttk.Entry(fh, textvariable=self.v_hiz_fiyat, width=10, font=(self.fa, 12), justify="right").grid(
            row=1, column=3, sticky="we", pady=4)

        alt = ttk.Frame(ek)
        alt.grid(row=2, column=0, sticky="we", pady=(4, 0))
        self.v_kalem_bilgi = tk.StringVar()
        ttk.Label(alt, textvariable=self.v_kalem_bilgi, style="Bilgi.TLabel").pack(side="left")
        self._dugme(alt, "➕  Teklife ekle", MAVI, self.kalem_ekle, "#174a94").pack(side="right")

        # --- 2) teklif kalemleri
        tk_ = ttk.LabelFrame(p, text=" 2) Teklif kalemleri ", padding=(10, 6))
        tk_.grid(row=2, column=0, sticky="nsew", pady=(0, 6))
        tk_.columnconfigure(0, weight=1)
        tk_.rowconfigure(0, weight=1)
        cer, self.t_kalem = self._tablo(tk_, (
            ("no", "#", 34, "center"), ("ad", "Malzeme / Hizmet", 200, "w"), ("detay", "Ölçü / Detay", 190, "w"),
            ("miktar", "Miktar", 110, "e"), ("bf", "Birim fiyat", 110, "e"), ("tutar", "Tutar", 120, "e")), yukseklik=5)
        cer.grid(row=0, column=0, sticky="nsew")
        self.t_kalem.bind("<Double-1>", lambda _e: self.kalem_duzenle())
        self.t_kalem.bind("<Delete>", lambda _e: self.kalem_sil())
        kd = ttk.Frame(tk_)
        kd.grid(row=1, column=0, sticky="we", pady=(6, 0))
        ttk.Button(kd, text="✏ Seçili kalemi düzenle", command=self.kalem_duzenle).pack(side="left")
        ttk.Button(kd, text="🗑 Seçili kalemi sil", command=self.kalem_sil).pack(side="left", padx=6)
        ttk.Label(kd, text="(Çift tıklayınca düzenlemek için yukarı alınır)", style="Not.TLabel").pack(side="left")

        # --- 3) toplam
        top = ttk.LabelFrame(p, text=" 3) Toplam ", padding=(10, 6))
        top.grid(row=3, column=0, sticky="we")
        top.columnconfigure(1, weight=1)
        sol = ttk.Frame(top)
        sol.grid(row=0, column=0, sticky="nw", padx=(0, 20))
        self.v_kdv = tk.StringVar(value=e.get("kdv", "20"))
        self._secim(sol, 0, "KDV oranı (%)", self.v_kdv, KDV_ORANLARI, serbest=True, genislik=5)
        kur = self.veri.d["fiyat_kurallari"]
        self.v_yuvarla = tk.BooleanVar(value=bool(kur["yuvarla"]))
        self.v_adim = tk.StringVar(value=kur["adim"])
        yv = ttk.Frame(sol)
        yv.grid(row=1, column=0, columnspan=2, sticky="w", pady=4)
        ttk.Checkbutton(yv, text="Genel toplamı yuvarla:", variable=self.v_yuvarla).pack(side="left")
        ttk.Combobox(yv, textvariable=self.v_adim, values=YUVARLAMA_ADIMLARI, width=4, state="readonly",
                     font=(self.fa, 11)).pack(side="left", padx=4)
        ttk.Label(yv, text="TL").pack(side="left")
        sag = ttk.Frame(top)
        sag.grid(row=0, column=1, sticky="ne")
        sag.columnconfigure(1, minsize=170)
        self.r_ara, _, _ = self._sonuc(sag, 0, "Ara toplam")
        self.r_min, self.l_min_d, self.l_min = self._sonuc(sag, 1, "Minimum ücret farkı")
        self.r_yuv, self.l_yuv_d, self.l_yuv = self._sonuc(sag, 2, "Yuvarlama")
        self.r_haric, _, _ = self._sonuc(sag, 3, "Toplam (KDV hariç)")
        self.r_kdv, _, _ = self._sonuc(sag, 4, "KDV tutarı")
        self.r_dahil, _, _ = self._sonuc(sag, 5, "GENEL TOPLAM (KDV dahil)", stil="BuyukK.TLabel")

        # --- düğmeler
        dug = ttk.Frame(p)
        dug.grid(row=4, column=0, sticky="we", pady=(10, 0))
        self._dugme(dug, "✖  Yeni teklif", KIRMIZI, self.yeni_teklif, "#a61e1e").pack(side="left")
        self._dugme(dug, "📄  PDF Teklif", MAVI, self.pdf_teklif, "#174a94").pack(side="left", padx=(10, 0))
        self._dugme(dug, "📋  WhatsApp için kopyala", YESIL, self.teklif_kopyala, "#166b2e").pack(side="left", padx=10)
        ttk.Button(dug, text="🔒 Yönetim", command=self.yonetim_ac).pack(side="right")
        self.v_durum = tk.StringVar()
        ttk.Label(p, textvariable=self.v_durum, foreground=YESIL).grid(row=5, column=0, sticky="w", pady=(6, 0))

        self.listeleri_yenile()
        self.c_malzeme.bind("<<ComboboxSelected>>", lambda _e: self.malzeme_secildi())
        self.c_hizmet.bind("<<ComboboxSelected>>", lambda _e: self.hizmet_secildi())
        self.v_tur.trace_add("write", lambda *_: self._tur_degisti())
        self._izle(self.kalem_onizle, self.v_malzeme, self.v_birim, self.v_en, self.v_boy, self.v_adet,
                   self.v_satis_m2, self.v_hizmet, self.v_miktar, self.v_hiz_fiyat)
        self._izle(self.teklif_hesapla, self.v_kdv, self.v_adim)
        self.v_yuvarla.trace_add("write", lambda *_: self._kural_kaydet())
        self.v_adim.trace_add("write", lambda *_: self._kural_kaydet())
        for w in (self.e_en, self.e_miktar):
            w.bind("<Return>", lambda _e: self.kalem_ekle())
        self.malzeme_secildi()
        self.hizmet_secildi()
        self._tur_degisti()
        self.teklif_hesapla()
        self.e_en.focus_set()

    def _tur_degisti(self):
        if self.v_tur.get() == "malzeme":
            self.f_hiz.grid_forget()
            self.f_malz.grid(row=1, column=0, sticky="we", pady=(4, 0))
        else:
            self.f_malz.grid_forget()
            self.f_hiz.grid(row=1, column=0, sticky="we", pady=(4, 0))
        self.kalem_onizle()

    def listeleri_yenile(self):
        adlar = [m["ad"] for m in self.veri.malzemeler]
        self.c_malzeme.configure(values=adlar)
        if self.v_malzeme.get() not in adlar:
            self.v_malzeme.set(adlar[0] if adlar else "")
            self.malzeme_secildi()
        hadlar = [h["ad"] for h in self.veri.hizmetler]
        self.c_hizmet.configure(values=hadlar)
        if self.v_hizmet.get() not in hadlar:
            self.v_hizmet.set(hadlar[0] if hadlar else "")
            self.hizmet_secildi()

    def malzeme_secildi(self):
        m = self.veri.malzeme(self.v_malzeme.get())
        self.v_satis_m2.set(m.get("satis", "") if m else "")

    def hizmet_secildi(self):
        h = self.veri.hizmet(self.v_hizmet.get())
        tip = h.get("tip", "adet") if h else "adet"
        self.v_hiz_fiyat.set(h.get("satis", "") if h else "")
        self.l_miktar.configure(text={"sabit": "Miktar (sabit)", "adet": "Adet", "m2": "m²"}[tip])
        self.l_hiz_fiyat.configure(text={"sabit": "Fiyat (TL, KDV hariç)", "adet": "Adet fiyatı (TL, KDV hariç)",
                                         "m2": "m² fiyatı (TL, KDV hariç)"}[tip])
        if tip == "sabit":
            self.v_miktar.set("1")
            self.e_miktar.configure(state="disabled")
        else:
            self.e_miktar.configure(state="normal")
            if tip == "m2":
                toplam_m2 = sum(k["m2"] for k in self.kalemler if k["tur"] == "malzeme")
                if toplam_m2 and sayi_oku(self.v_miktar.get()) in (None, 1):
                    self.v_miktar.set(sayi_yaz(toplam_m2, 2))

    def _formdan_kalem(self):
        """Formdaki bilgilerden kalem oluşturur; eksikse (None, neden) döner."""
        if self.v_tur.get() == "malzeme":
            en, boy = sayi_oku(self.v_en.get()), sayi_oku(self.v_boy.get())
            adet = sayi_oku(self.v_adet.get()) or 1
            fiyat = sayi_oku(self.v_satis_m2.get())
            if en is None or boy is None:
                return None, "En ve boyu girin."
            if fiyat is None:
                return None, "m² fiyatını girin."
            _, top = m2_hesapla(en, boy, self.v_birim.get(), adet)
            m = self.veri.malzeme(self.v_malzeme.get())
            min_m2 = (sayi_oku(m.get("min_m2")) or 0) if m else 0
            fatura = max(top, min_m2)
            return {"tur": "malzeme", "ad": self.v_malzeme.get() or "Malzeme", "en": en, "boy": boy,
                    "birim": self.v_birim.get(), "olcu": f"{kisa(en)} x {kisa(boy)} {self.v_birim.get()}",
                    "adet": adet, "m2": top, "fatura_m2": fatura, "birim_fiyat": fiyat, "tutar": fatura * fiyat}, ""
        h = self.veri.hizmet(self.v_hizmet.get())
        tip = h.get("tip", "adet") if h else "adet"
        miktar = 1.0 if tip == "sabit" else sayi_oku(self.v_miktar.get())
        fiyat = sayi_oku(self.v_hiz_fiyat.get())
        if not self.v_hizmet.get():
            return None, "Hizmet seçin (Yönetim → Hizmetler'den eklenir)."
        if miktar is None:
            return None, "Miktarı girin."
        if fiyat is None:
            return None, "Fiyatı girin."
        return {"tur": "hizmet", "ad": self.v_hizmet.get(), "tip": tip, "miktar": miktar,
                "birim_fiyat": fiyat, "tutar": miktar * fiyat}, ""

    def kalem_onizle(self):
        k, neden = self._formdan_kalem()
        if not k:
            self.v_kalem_bilgi.set(neden)
            return
        if k["tur"] == "malzeme":
            ek = f"  (minimum {sayi_yaz(k['fatura_m2'], 2)} m² uygulanır)" if k["fatura_m2"] > k["m2"] + 1e-9 else ""
            self.v_kalem_bilgi.set(f"Bu kalem: {sayi_yaz(k['m2'], 3)} m²{ek}  →  {para(k['tutar'])}")
        else:
            self.v_kalem_bilgi.set(f"Bu kalem: {kalem_satiri(k)[2]} × {para(k['birim_fiyat'])}  →  {para(k['tutar'])}")

    def kalem_ekle(self):
        k, neden = self._formdan_kalem()
        if not k:
            self.v_durum.set(neden)
            return False
        self.kalemler.append(k)
        if k["tur"] == "malzeme":
            self.v_en.set("")
            self.v_boy.set("")
            self.v_adet.set("1")
            self.malzeme_secildi()
            self.e_en.focus_set()
        else:
            self.hizmet_secildi()
        self.kalem_tablosu()
        self.teklif_hesapla()
        self.v_durum.set(f"“{k['ad']}” teklife eklendi.")
        return True

    def kalem_tablosu(self):
        self.t_kalem.delete(*self.t_kalem.get_children())
        for i, k in enumerate(self.kalemler):
            self.t_kalem.insert("", "end", iid=str(i), values=(i + 1, *kalem_satiri(k)))

    def _secili_kalem(self):
        s = self.t_kalem.selection()
        return int(s[0]) if s else None

    def kalem_sil(self):
        i = self._secili_kalem()
        if i is None:
            return
        del self.kalemler[i]
        self.kalem_tablosu()
        self.teklif_hesapla()

    def kalem_duzenle(self):
        i = self._secili_kalem()
        if i is None:
            return
        k = self.kalemler.pop(i)
        if k["tur"] == "malzeme":
            self.v_tur.set("malzeme")
            self.v_malzeme.set(k["ad"])
            self.v_birim.set(k.get("birim", "cm"))
            self.v_en.set(kisa(k["en"]))
            self.v_boy.set(kisa(k["boy"]))
            self.v_adet.set(kisa(k["adet"]))
            self.v_satis_m2.set(kisa(k["birim_fiyat"]))
        else:
            self.v_tur.set("hizmet")
            self.v_hizmet.set(k["ad"])
            self.hizmet_secildi()
            self.v_miktar.set(kisa(k["miktar"]))
            self.v_hiz_fiyat.set(kisa(k["birim_fiyat"]))
        self.kalem_tablosu()
        self.teklif_hesapla()
        self.v_durum.set("Kalem düzenleme için yukarı alındı; değiştirip “Teklife ekle”ye basın.")

    def _kural_kaydet(self):
        kur = self.veri.d["fiyat_kurallari"]
        if kur["yuvarla"] != self.v_yuvarla.get() or kur["adim"] != self.v_adim.get():
            kur["yuvarla"] = self.v_yuvarla.get()
            kur["adim"] = self.v_adim.get()
            self.veri.kaydet()
        self.teklif_hesapla()

    def teklif_hesapla(self):
        for v in (self.r_ara, self.r_min, self.r_yuv, self.r_haric, self.r_kdv, self.r_dahil):
            v.set("—")
        self.hesap = None
        if self.kalemler:
            kur = self.veri.d["fiyat_kurallari"]
            oran = sayi_oku(self.v_kdv.get()) or 0
            adim = (sayi_oku(self.v_adim.get()) or 0) if self.v_yuvarla.get() else 0
            t = teklif_toplami(self.kalemler, oran, sayi_oku(kur.get("min_tutar")) or 0, adim)
            self.r_ara.set(para(t["ara"]))
            self.r_min.set(para(t["min_fark"]))
            self.r_yuv.set(para(t["yuvarlama"]))
            self.r_haric.set(para(t["haric"]))
            self.r_kdv.set(para(t["kdv"]))
            self.r_dahil.set(para(t["dahil"]))
            kalemler = [dict(k) for k in self.kalemler]
            maliyetler = [self.veri.kalem_maliyeti(k) for k in kalemler]
            maliyet = None if any(m is None for m in maliyetler) else sum(maliyetler)
            malz = [k["ad"] for k in kalemler]
            self.hesap = {
                "musteri": self.v_musteri.get().strip(), "kalemler": kalemler, "kdv_orani": oran,
                "ara": t["ara"], "min_fark": t["min_fark"], "yuvarlama": t["yuvarlama"],
                "satis_haric": t["haric"], "satis_kdv": t["kdv"], "satis_dahil": t["dahil"],
                "maliyet_haric": maliyet, "kar": t["haric"] - maliyet if maliyet is not None else None,
                "m2": sum(k["fatura_m2"] for k in kalemler if k["tur"] == "malzeme"),
                "malzeme": malz[0] + (f" +{len(malz) - 1} kalem" if len(malz) > 1 else ""),
                "olcu": next((k["olcu"] for k in kalemler if k["tur"] == "malzeme"), ""),
                "adet": 1,
            }
        goster_min = bool(self.hesap and self.hesap["min_fark"])
        goster_yuv = bool(self.hesap and abs(self.hesap["yuvarlama"]) >= 0.005)
        for gor, wl in ((goster_min, (self.l_min, self.l_min_d)), (goster_yuv, (self.l_yuv, self.l_yuv_d))):
            for w in wl:
                (w.grid if gor else w.grid_remove)()
        if self.yonetim and self.yonetim.winfo_exists():
            self.yonetim.anlik_yenile()

    def yeni_teklif(self):
        if self.kalemler and not messagebox.askyesno("Yeni teklif", "Mevcut kalemler silinsin mi?", parent=self):
            return
        self.kalemler = []
        for v in (self.v_en, self.v_boy, self.v_musteri):
            v.set("")
        self.v_adet.set("1")
        self.v_tur.set("malzeme")
        self.malzeme_secildi()
        self.kalem_tablosu()
        self.teklif_hesapla()
        self.v_durum.set("")
        self.e_en.focus_set()

    def _hazirla(self):
        """Formda eklenmemiş geçerli bir malzeme kalemi varsa onu da ekler. Teklif hazırsa True."""
        if self.v_tur.get() == "malzeme" and self.v_en.get().strip() and self._formdan_kalem()[0]:
            if not self.kalemler or messagebox.askyesno(
                    "Eklenmemiş kalem", "Formda teklife eklenmemiş bir kalem var. Eklensin mi?", parent=self):
                self.kalem_ekle()
        if not self.hesap:
            messagebox.showwarning("Eksik bilgi", "Teklife en az bir kalem ekleyin.", parent=self)
            return False
        return True

    def _kayit_olustur(self):
        k = json.loads(json.dumps(self.hesap))
        k["musteri"] = self.v_musteri.get().strip()
        k["no"] = self.veri.yeni_teklif_no()
        k["id"] = uuid.uuid4().hex
        k["tarih"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        self.veri.d["kayitlar"].append(k)
        self.veri.kaydet()
        return k

    def pdf_teklif(self):
        if not PDF_VAR:
            messagebox.showerror("PDF", "PDF kütüphanesi bulunamadı.", parent=self)
            return
        if not self._hazirla():
            return
        k = self._kayit_olustur()
        ad = "".join(ch for ch in (k["musteri"] or "musteri") if ch.isalnum() or ch in " -_").strip().replace(" ", "_")
        yol = os.path.join(pdf_klasoru(), f"Teklif_{k['no']}_{ad}_{datetime.date.today():%Y-%m-%d}.pdf")
        try:
            musteri_pdf(k, yol, self.veri.d["firma"], self.veri.logo_yolu(), self.veri.d.get("teklif_notu", ""))
        except Exception as hata:
            messagebox.showerror("PDF oluşturulamadı", str(hata), parent=self)
            return
        self.v_durum.set(f"Teklif No {k['no']} kaydedildi, PDF açılıyor: {yol}")
        dosya_ac(yol)
        if self.yonetim and self.yonetim.winfo_exists():
            self.yonetim.kayitlari_yenile()

    def teklif_kopyala(self):
        if not self._hazirla():
            return
        h = self.hesap
        firma = self.veri.d["firma"]
        satirlar = [f"{firma.get('ad') or 'Fiyat Teklifi'} - Fiyat Teklifi"]
        if self.v_musteri.get().strip():
            satirlar.append(f"Sayın {self.v_musteri.get().strip()}")
        satirlar.append("")
        for i, k in enumerate(h["kalemler"], 1):
            ad, detay, miktar, bf, tutar = kalem_satiri(k)
            if k["tur"] == "malzeme":
                satirlar.append(f"{i}) {ad}: {detay} = {miktar} × {bf} = {tutar}")
            else:
                satirlar.append(f"{i}) {ad}: {miktar} × {bf} = {tutar}")
        satirlar.append("")
        if h["min_fark"]:
            satirlar.append(f"Minimum ücret farkı: {para(h['min_fark'])}")
        if abs(h["yuvarlama"]) >= 0.005:
            satirlar.append(f"Yuvarlama: {para(h['yuvarlama'])}")
        satirlar += [f"Toplam (KDV hariç): {para(h['satis_haric'])}",
                     f"KDV (%{kisa(h['kdv_orani'])}): {para(h['satis_kdv'])}",
                     f"GENEL TOPLAM: {para(h['satis_dahil'])}"]
        if self.veri.d.get("teklif_notu", "").strip():
            satirlar += ["", self.veri.d["teklif_notu"].strip()]
        if firma.get("iban"):
            satirlar.append(f"IBAN: {firma['iban']}")
        if firma.get("tel"):
            satirlar.append(f"Tel / WhatsApp: {firma['tel']}")
        self.clipboard_clear()
        self.clipboard_append("\n".join(satirlar))
        self.v_durum.set("Kopyalandı ✓  WhatsApp'a yapıştırabilirsiniz.")

    # ------------------------------------------------------------ kur
    def kuru_guncelle(self, sonra=None):
        def is_parcacigi():
            try:
                k = tcmb_kurlari()
            except Exception:
                k = None
            self.after(0, lambda: self._kur_geldi(k, sonra))

        threading.Thread(target=is_parcacigi, daemon=True).start()

    def _kur_geldi(self, k, sonra=None):
        if k:
            for ad in ("Dolar", "Euro"):
                if k.get(ad):
                    self.veri.d["kurlar"][ad] = k[ad]
            self.veri.d["kurlar"]["tarih"] = k.get("tarih", "")
            self.veri.d["kurlar"]["kaynak"] = "TCMB"
            self.veri.kaydet()
        self.teklif_hesapla()
        if self.yonetim and self.yonetim.winfo_exists():
            self.yonetim.malz_yenile()
        if sonra:
            sonra(bool(k))

    def kur_bilgisi(self):
        k = self.veri.d["kurlar"]
        if not k.get("Dolar") and not k.get("Euro"):
            return "Kur yok. İnternet bağlantısını kontrol edin ya da kuru elle yazın."
        return (f"{k.get('kaynak', 'Elle')} {k.get('tarih', '')}  •  $ {sayi_yaz(k.get('Dolar') or 0, 4)}"
                f"  •  € {sayi_yaz(k.get('Euro') or 0, 4)}")

    # ------------------------------------------------------------ yönetim
    def yonetim_ac(self):
        if self.yonetim and self.yonetim.winfo_exists():
            self.yonetim.lift()
            return
        if not self.veri.d.get("sifre"):
            s1 = simpledialog.askstring("Yönetim - şifre belirleyin",
                                        "Yönetim ekranı için bir şifre belirleyin (en az 4 karakter):", show="•", parent=self)
            if s1 is None:
                return
            s2 = simpledialog.askstring("Yönetim - şifre belirleyin", "Şifreyi tekrar yazın:", show="•", parent=self)
            if len(s1) < 4 or s1 != s2:
                messagebox.showerror("Yönetim", "Şifreler aynı değil ya da çok kısa.", parent=self)
                return
            self.veri.d["sifre"] = sifre_ozet(s1)
            self.veri.kaydet()
            self.yonetim = Yonetim(self)
            return
        sifre = simpledialog.askstring("Yönetim", "Şifre:", show="•", parent=self)
        if sifre is None:
            return
        if sifre_ozet(sifre) != self.veri.d["sifre"]:
            messagebox.showerror("Yönetim", "Şifre yanlış.", parent=self)
            return
        self.yonetim = Yonetim(self)

    # ------------------------------------------------------------ sayfa 2: KDV ve indirim
    def _kdv_indirim_sayfasi(self):
        p = self.sayfa_kdv
        p.columnconfigure(0, weight=1, uniform="k")
        p.columnconfigure(1, weight=1, uniform="k")

        kdv = ttk.LabelFrame(p, text=" KDV Hesaplama ", padding=12)
        kdv.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        kdv.columnconfigure(1, weight=1)
        self.k_fiyat, self.k_oran, self.k_tur = tk.StringVar(), tk.StringVar(value="20"), tk.StringVar(value="haric")
        self._giris(kdv, 0, "Fiyat (TL)", self.k_fiyat)
        self._secim(kdv, 1, "KDV oranı (%)", self.k_oran, KDV_ORANLARI, serbest=True)
        tur = ttk.Frame(kdv)
        tur.grid(row=2, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Label(tur, text="Girdiğim fiyat:").pack(side="left", padx=(0, 8))
        ttk.Radiobutton(tur, text="KDV hariç", value="haric", variable=self.k_tur).pack(side="left", padx=4)
        ttk.Radiobutton(tur, text="KDV dahil", value="dahil", variable=self.k_tur).pack(side="left", padx=4)
        ttk.Separator(kdv).grid(row=3, column=0, columnspan=2, sticky="we", pady=10)
        self.k_haric = self._sonuc(kdv, 4, "KDV hariç tutar")[0]
        self.k_kdv = self._sonuc(kdv, 5, "KDV tutarı")[0]
        self.k_dahil = self._sonuc(kdv, 6, "KDV dahil tutar", stil="BuyukK.TLabel")[0]
        self._dugme(kdv, "✖  Temizle", KIRMIZI, lambda: self.k_fiyat.set(""), "#a61e1e").grid(
            row=7, column=0, sticky="w", pady=(14, 0))
        self._izle(self.kdv_hesapla, self.k_fiyat, self.k_oran, self.k_tur)

        ind = ttk.LabelFrame(p, text=" İndirim / İskonto Hesaplama ", padding=12)
        ind.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ind.columnconfigure(1, weight=1)
        self.i_islem = tk.StringVar(value="İndirimli fiyat hesaplama")
        self.i_islemler = {"İndirimli fiyat hesaplama": "indirimli", "Normal fiyat hesaplama": "normal",
                           "İndirim oranı hesaplama": "oran"}
        self._secim(ind, 0, "İşlem", self.i_islem, list(self.i_islemler), genislik=24)
        self.i_a, self.i_b = tk.StringVar(), tk.StringVar()
        self.i_la = ttk.Label(ind)
        self.i_la.grid(row=1, column=0, sticky="w", pady=4, padx=(0, 8))
        ttk.Entry(ind, textvariable=self.i_a, font=(self.fa, 12), justify="right").grid(row=1, column=1, sticky="we", pady=4)
        self.i_lb = ttk.Label(ind)
        self.i_lb.grid(row=2, column=0, sticky="w", pady=4, padx=(0, 8))
        ttk.Entry(ind, textvariable=self.i_b, font=(self.fa, 12), justify="right").grid(row=2, column=1, sticky="we", pady=4)
        ttk.Separator(ind).grid(row=3, column=0, columnspan=2, sticky="we", pady=10)
        self.i_l1 = ttk.Label(ind)
        self.i_l1.grid(row=4, column=0, sticky="w", pady=3)
        self.i_r1 = tk.StringVar(value="—")
        ttk.Label(ind, textvariable=self.i_r1, style="BuyukK.TLabel").grid(row=4, column=1, sticky="e")
        ttk.Label(ind, text="Yapılan indirim (TL)").grid(row=5, column=0, sticky="w", pady=3)
        self.i_r2 = tk.StringVar(value="—")
        ttk.Label(ind, textvariable=self.i_r2, style="Sonuc.TLabel").grid(row=5, column=1, sticky="e")
        self._dugme(ind, "✖  Temizle", KIRMIZI, lambda: (self.i_a.set(""), self.i_b.set("")), "#a61e1e").grid(
            row=6, column=0, sticky="w", pady=(14, 0))
        self.i_islem.trace_add("write", lambda *_: self._indirim_etiketleri())
        self._izle(self.indirim_hesapla, self.i_a, self.i_b)
        self._indirim_etiketleri()

    def kdv_hesapla(self):
        f, o = sayi_oku(self.k_fiyat.get()), sayi_oku(self.k_oran.get()) or 0
        if f is None:
            for v in (self.k_haric, self.k_kdv, self.k_dahil):
                v.set("—")
            return
        haric = f if self.k_tur.get() == "haric" else f / (1 + o / 100)
        kdv, dahil = kdv_hesapla(haric, o)
        self.k_haric.set(para(haric))
        self.k_kdv.set(para(kdv))
        self.k_dahil.set(para(dahil))

    def _indirim_etiketleri(self):
        islem = self.i_islemler[self.i_islem.get()]
        etiketler = {
            "indirimli": ("Normal fiyat (TL)", "İndirim oranı (%)", "İndirimli fiyat"),
            "normal": ("İndirimli fiyat (TL)", "İndirim oranı (%)", "Normal fiyat"),
            "oran": ("Normal fiyat (TL)", "İndirimli fiyat (TL)", "İndirim oranı"),
        }[islem]
        self.i_la.configure(text=etiketler[0])
        self.i_lb.configure(text=etiketler[1])
        self.i_l1.configure(text=etiketler[2])
        self.i_a.set("")
        self.i_b.set("")
        self.indirim_hesapla()

    def indirim_hesapla(self):
        islem = self.i_islemler[self.i_islem.get()]
        a, b = sayi_oku(self.i_a.get()), sayi_oku(self.i_b.get())
        if islem == "indirimli":
            r = indirim_hesapla(islem, normal=a, oran=b)
        elif islem == "normal":
            r = indirim_hesapla(islem, indirimli=a, oran=b)
        else:
            r = indirim_hesapla(islem, normal=a, indirimli=b)
        if not r:
            self.i_r1.set("—")
            self.i_r2.set("—")
            return
        normal, indirimli, oran, tutar = r
        self.i_r1.set({"indirimli": para(indirimli), "normal": para(normal), "oran": f"% {sayi_yaz(oran, 2)}"}[islem])
        self.i_r2.set(para(tutar))

    # ------------------------------------------------------------ kapanış
    def _kapat(self):
        self.yerel["ekran"] = {"malzeme": self.v_malzeme.get(), "birim": self.v_birim.get(), "kdv": self.v_kdv.get()}
        yerel_ayar_yaz(self.yerel)
        self.destroy()


# ================================================================ yönetim penceresi

class Yonetim(tk.Toplevel, Ortak):
    """Şifreli yönetim penceresi."""

    @property
    def veri(self):
        return self.ana.veri

    def __init__(self, ana):
        super().__init__(ana)
        self.ana = ana
        self.title("Yönetim - Malzemeler, Hizmetler, Kâr ve Kayıtlar")
        self.geometry("1080x700")
        self.minsize(940, 600)
        simge_uygula(self)
        d = ttk.Notebook(self)
        d.pack(fill="both", expand=True, padx=10, pady=10)
        self.s_malz, self.s_hiz, self.s_anlik, self.s_kayit, self.s_firma, self.s_ayar = (
            ttk.Frame(d, padding=10) for _ in range(6))
        d.add(self.s_malz, text=" Malzemeler ")
        d.add(self.s_hiz, text=" Hizmetler ")
        d.add(self.s_anlik, text=" Bu Teklifin Kârı ")
        d.add(self.s_kayit, text=" Kayıtlar ve Kâr Raporu ")
        d.add(self.s_firma, text=" Firma ve Teklif ")
        d.add(self.s_ayar, text=" Ayarlar ")
        self._malzemeler()
        self._hizmetler()
        self._anlik()
        self._kayitlar()
        self._firma()
        self._ayarlar()

    def hepsini_yenile(self):
        self.malz_yenile()
        self.hiz_yenile()
        self.kayitlari_yenile()
        self.anlik_yenile()
        self.firma_doldur()
        self._klasor_yaz()

    # ------------------------------------------------------------ malzemeler
    def _malzemeler(self):
        p = self.s_malz
        p.columnconfigure(0, weight=1)
        p.rowconfigure(1, weight=1)
        kur = ttk.Frame(p)
        kur.grid(row=0, column=0, sticky="we", pady=(0, 8))
        self.v_kur = tk.StringVar(value=self.ana.kur_bilgisi())
        ttk.Label(kur, textvariable=self.v_kur).pack(side="left")
        ttk.Button(kur, text="Kuru elle gir", command=self.kur_elle).pack(side="right")
        ttk.Button(kur, text="↻ Kuru güncelle (TCMB)", command=self.kur_guncelle).pack(side="right", padx=6)

        cer, self.t_malz = self._tablo(p, (
            ("ad", "Malzeme", 190, "w"), ("alis", "Alış / m²", 100, "e"), ("para", "Birim", 60, "center"),
            ("tl", "Bugün TL / m²", 110, "e"), ("satis", "Satış TL / m²", 110, "e"), ("fire", "Fire %", 60, "e"),
            ("min", "Min. m²", 70, "e"), ("kar", "m² kâr (fire dahil)", 140, "e")), yukseklik=9)
        cer.grid(row=1, column=0, sticky="nsew")
        self.t_malz.bind("<<TreeviewSelect>>", lambda _e: self._malz_secildi())

        form = ttk.LabelFrame(p, text=" Malzeme ekle / düzenle ", padding=10)
        form.grid(row=2, column=0, sticky="we", pady=(8, 0))
        for i in (1, 3, 5):
            form.columnconfigure(i, weight=1)
        self.f_ad, self.f_alis, self.f_para, self.f_satis, self.f_fire, self.f_min = (tk.StringVar() for _ in range(6))
        self.f_para.set("Euro")
        self.f_fire.set("0")
        ttk.Label(form, text="Malzeme adı").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(form, textvariable=self.f_ad, font=(self.fa, 12)).grid(row=0, column=1, columnspan=5, sticky="we", pady=4)
        self._giris(form, 1, "Alış fiyatı / m² (KDV hariç)", self.f_alis, sutun=0)
        self._secim(form, 1, "Para birimi", self.f_para, PARA_BIRIMLERI, sutun=2, genislik=7)
        self._giris(form, 1, "Fire / kayıp (%)", self.f_fire, sutun=4, genislik=6)
        self._giris(form, 2, "Satış fiyatı / m² (TL, KDV hariç)", self.f_satis, sutun=0)
        self._giris(form, 2, "Minimum m² (kalem başına)", self.f_min, sutun=2, genislik=7)
        dug = ttk.Frame(form)
        dug.grid(row=3, column=0, columnspan=6, sticky="w", pady=(8, 0))
        ttk.Button(dug, text="➕ Yeni malzeme olarak ekle", command=self.malz_ekle).pack(side="left")
        ttk.Button(dug, text="💾 Seçili malzemeyi güncelle", command=self.malz_guncelle).pack(side="left", padx=6)
        ttk.Button(dug, text="🗑 Seçili malzemeyi sil", command=self.malz_sil).pack(side="left")
        self._not(form, "Dolar / Euro fiyatlar güncel TCMB kuruyla TL'ye çevrilir; TL fiyatlar değişmez. Satış fiyatı "
                  "müşteri ekranına otomatik gelir. Minimum m²: örneğin 1 yazarsanız 0,3 m²'lik iş 1 m² sayılır "
                  "(boş = minimum yok).", row=4, column=0, columnspan=6, pady=(6, 0))
        self.malz_yenile()

    def malz_yenile(self, sec=None):
        sec = sec if sec is not None else (self.t_malz.selection() or [None])[0]
        self.t_malz.delete(*self.t_malz.get_children())
        for i, m in enumerate(self.veri.malzemeler):
            tl = self.veri.alis_tl_m2(m)
            satis = sayi_oku(m.get("satis"))
            fire = sayi_oku(m.get("fire")) or 0
            kar = satis - tl * (1 + fire / 100) if tl is not None and satis is not None else None
            alis = sayi_oku(m.get("alis"))
            mn = sayi_oku(m.get("min_m2"))
            self.t_malz.insert("", "end", iid=str(i), values=(
                m["ad"], sayi_yaz(alis) if alis is not None else "-", m.get("para", "TL"),
                sayi_yaz(tl) if tl is not None else "-", sayi_yaz(satis) if satis is not None else "-",
                kisa(fire), kisa(mn) if mn else "-", sayi_yaz(kar) if kar is not None else "-"))
        if sec is not None and str(sec) in self.t_malz.get_children():
            self.t_malz.selection_set(str(sec))
        self.v_kur.set(self.ana.kur_bilgisi())

    def _malz_secildi(self):
        s = self.t_malz.selection()
        if not s:
            return
        m = self.veri.malzemeler[int(s[0])]
        self.f_ad.set(m["ad"])
        self.f_alis.set(m.get("alis", ""))
        self.f_para.set(m.get("para", "TL"))
        self.f_satis.set(m.get("satis", ""))
        self.f_fire.set(m.get("fire", "0"))
        self.f_min.set(m.get("min_m2", ""))

    def _sayilar_gecerli(self, *alanlar):
        for etiket, v in alanlar:
            if v.get().strip() and sayi_oku(v.get()) is None:
                messagebox.showwarning("Hatalı giriş", f"{etiket} sayı olmalı.", parent=self)
                return False
        return True

    def _malz_form(self):
        ad = self.f_ad.get().strip()
        if not ad:
            messagebox.showwarning("Malzeme", "Malzeme adını yazın.", parent=self)
            return None
        if not self._sayilar_gecerli(("Alış fiyatı", self.f_alis), ("Satış fiyatı", self.f_satis),
                                     ("Fire", self.f_fire), ("Minimum m²", self.f_min)):
            return None
        return {"ad": ad, "alis": self.f_alis.get().strip(), "para": self.f_para.get(),
                "satis": self.f_satis.get().strip(), "fire": self.f_fire.get().strip() or "0",
                "min_m2": self.f_min.get().strip()}

    def _liste_kaydet(self, yenile, sec):
        self.veri.kaydet()
        yenile(sec)
        self.ana.listeleri_yenile()
        self.ana.malzeme_secildi()
        self.ana.hizmet_secildi()
        self.ana.teklif_hesapla()

    def malz_ekle(self):
        m = self._malz_form()
        if not m:
            return
        if self.veri.malzeme(m["ad"]):
            messagebox.showwarning("Malzeme", "Bu adda bir malzeme zaten var. Güncellemek için listeden seçin.", parent=self)
            return
        self.veri.malzemeler.append(m)
        self._liste_kaydet(self.malz_yenile, len(self.veri.malzemeler) - 1)

    def malz_guncelle(self):
        s = self.t_malz.selection()
        if not s:
            messagebox.showinfo("Malzeme", "Önce listeden bir malzeme seçin.", parent=self)
            return
        m = self._malz_form()
        if not m:
            return
        i = int(s[0])
        eski = self.veri.malzemeler[i]["ad"]
        if m["ad"] != eski and self.veri.malzeme(m["ad"]):
            messagebox.showwarning("Malzeme", "Bu adda bir malzeme zaten var.", parent=self)
            return
        if self.ana.v_malzeme.get() == eski:
            self.ana.v_malzeme.set(m["ad"])
        self.veri.malzemeler[i] = m
        self._liste_kaydet(self.malz_yenile, i)

    def malz_sil(self):
        s = self.t_malz.selection()
        if not s:
            return
        m = self.veri.malzemeler[int(s[0])]
        if messagebox.askyesno("Malzeme sil", f"“{m['ad']}” silinsin mi?", parent=self):
            del self.veri.malzemeler[int(s[0])]
            self.t_malz.selection_remove(*self.t_malz.selection())
            self._liste_kaydet(self.malz_yenile, None)

    def kur_guncelle(self):
        self.v_kur.set("Kur alınıyor…")

        def bitti(basarili):
            if not self.winfo_exists():
                return
            self.malz_yenile()
            if not basarili:
                self.v_kur.set("Kur alınamadı (internet?). " + self.ana.kur_bilgisi())
            self.anlik_yenile()

        self.ana.kuru_guncelle(sonra=bitti)

    def kur_elle(self):
        k = self.veri.d["kurlar"]
        for ad in ("Dolar", "Euro"):
            girdi = simpledialog.askstring("Kuru elle gir", f"1 {ad} = kaç TL?",
                                           initialvalue=sayi_yaz(k.get(ad) or 0, 4), parent=self)
            if girdi is None:
                return
            deger = sayi_oku(girdi)
            if deger:
                k[ad] = deger
        k["tarih"] = datetime.date.today().strftime("%d.%m.%Y")
        k["kaynak"] = "Elle"
        self.veri.kaydet()
        self.malz_yenile()
        self.ana.teklif_hesapla()

    # ------------------------------------------------------------ hizmetler
    def _hizmetler(self):
        p = self.s_hiz
        p.columnconfigure(0, weight=1)
        p.rowconfigure(0, weight=1)
        cer, self.t_hiz = self._tablo(p, (
            ("ad", "Hizmet", 240, "w"), ("tip", "Fiyatlama", 130, "center"), ("satis", "Satış fiyatı TL", 130, "e"),
            ("maliyet", "Maliyet TL", 130, "e"), ("kar", "Kâr TL (birim)", 130, "e")), yukseklik=10)
        cer.grid(row=0, column=0, sticky="nsew")
        self.t_hiz.bind("<<TreeviewSelect>>", lambda _e: self._hiz_secildi())

        form = ttk.LabelFrame(p, text=" Hizmet ekle / düzenle ", padding=10)
        form.grid(row=1, column=0, sticky="we", pady=(8, 0))
        for i in (1, 3):
            form.columnconfigure(i, weight=1)
        self.h_ad, self.h_tip, self.h_satis, self.h_maliyet = (tk.StringVar() for _ in range(4))
        self.h_tip.set("Adet başına")
        ttk.Label(form, text="Hizmet adı").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(form, textvariable=self.h_ad, font=(self.fa, 12)).grid(row=0, column=1, sticky="we", pady=4)
        self._secim(form, 0, "Fiyatlama", self.h_tip, list(HIZMET_TIPLERI), sutun=2, genislik=12)
        self._giris(form, 1, "Satış fiyatı (TL, KDV hariç)", self.h_satis, sutun=0)
        self._giris(form, 1, "Maliyet (TL, isteğe bağlı)", self.h_maliyet, sutun=2)
        dug = ttk.Frame(form)
        dug.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(dug, text="➕ Yeni hizmet olarak ekle", command=self.hiz_ekle).pack(side="left")
        ttk.Button(dug, text="💾 Seçili hizmeti güncelle", command=self.hiz_guncelle).pack(side="left", padx=6)
        ttk.Button(dug, text="🗑 Seçili hizmeti sil", command=self.hiz_sil).pack(side="left")
        self._not(form, "Fiyatlama: Sabit = teklife bir kez eklenir (ör. tasarım). Adet başına = montaj noktası, söküm vb. "
                  "m² başına = m² ile çarpılır (teklifteki toplam m² otomatik önerilir). Maliyet: ustaya / dışarıya "
                  "ödediğiniz tutar; boş bırakırsanız hizmetin tamamı kâr sayılır.", row=3, column=0, columnspan=4, pady=(6, 0))
        self.hiz_yenile()

    def hiz_yenile(self, sec=None):
        sec = sec if sec is not None else (self.t_hiz.selection() or [None])[0]
        self.t_hiz.delete(*self.t_hiz.get_children())
        for i, h in enumerate(self.veri.hizmetler):
            s, mlt = sayi_oku(h.get("satis")), sayi_oku(h.get("maliyet"))
            self.t_hiz.insert("", "end", iid=str(i), values=(
                h["ad"], HIZMET_TIP_ADI.get(h.get("tip"), "-"), sayi_yaz(s) if s is not None else "-",
                sayi_yaz(mlt) if mlt is not None else "-", sayi_yaz(s - (mlt or 0)) if s is not None else "-"))
        if sec is not None and str(sec) in self.t_hiz.get_children():
            self.t_hiz.selection_set(str(sec))

    def _hiz_secildi(self):
        s = self.t_hiz.selection()
        if not s:
            return
        h = self.veri.hizmetler[int(s[0])]
        self.h_ad.set(h["ad"])
        self.h_tip.set(HIZMET_TIP_ADI.get(h.get("tip"), "Adet başına"))
        self.h_satis.set(h.get("satis", ""))
        self.h_maliyet.set(h.get("maliyet", ""))

    def _hiz_form(self):
        ad = self.h_ad.get().strip()
        if not ad:
            messagebox.showwarning("Hizmet", "Hizmet adını yazın.", parent=self)
            return None
        if not self._sayilar_gecerli(("Satış fiyatı", self.h_satis), ("Maliyet", self.h_maliyet)):
            return None
        return {"ad": ad, "tip": HIZMET_TIPLERI[self.h_tip.get()], "satis": self.h_satis.get().strip(),
                "maliyet": self.h_maliyet.get().strip()}

    def hiz_ekle(self):
        h = self._hiz_form()
        if not h:
            return
        if self.veri.hizmet(h["ad"]):
            messagebox.showwarning("Hizmet", "Bu adda bir hizmet zaten var.", parent=self)
            return
        self.veri.hizmetler.append(h)
        self._liste_kaydet(self.hiz_yenile, len(self.veri.hizmetler) - 1)

    def hiz_guncelle(self):
        s = self.t_hiz.selection()
        if not s:
            messagebox.showinfo("Hizmet", "Önce listeden bir hizmet seçin.", parent=self)
            return
        h = self._hiz_form()
        if not h:
            return
        i = int(s[0])
        eski = self.veri.hizmetler[i]["ad"]
        if h["ad"] != eski and self.veri.hizmet(h["ad"]):
            messagebox.showwarning("Hizmet", "Bu adda bir hizmet zaten var.", parent=self)
            return
        if self.ana.v_hizmet.get() == eski:
            self.ana.v_hizmet.set(h["ad"])
        self.veri.hizmetler[i] = h
        self._liste_kaydet(self.hiz_yenile, i)

    def hiz_sil(self):
        s = self.t_hiz.selection()
        if not s:
            return
        h = self.veri.hizmetler[int(s[0])]
        if messagebox.askyesno("Hizmet sil", f"“{h['ad']}” silinsin mi?", parent=self):
            del self.veri.hizmetler[int(s[0])]
            self.t_hiz.selection_remove(*self.t_hiz.selection())
            self._liste_kaydet(self.hiz_yenile, None)

    # ------------------------------------------------------------ bu teklifin kârı
    def _anlik(self):
        p = self.s_anlik
        p.columnconfigure(0, weight=1)
        p.rowconfigure(1, weight=1)
        ttk.Label(p, text="Müşteri ekranındaki teklifin maliyeti ve kârı", style="Baslik.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8))
        cer, self.t_anlik = self._tablo(p, (
            ("ad", "Kalem", 190, "w"), ("detay", "Alış / maliyet bilgisi", 300, "w"), ("satis", "Satış TL", 120, "e"),
            ("maliyet", "Maliyet TL", 120, "e"), ("kar", "Kâr TL", 120, "e")), yukseklik=7, secim="none")
        cer.grid(row=1, column=0, sticky="nsew")
        oz = ttk.Frame(p)
        oz.grid(row=2, column=0, sticky="we", pady=(10, 0))
        oz.columnconfigure(1, weight=1)
        self.anlik_v = {}
        for i, (anahtar, etiket) in enumerate((
            ("ayar", "Minimum ücret farkı / yuvarlama"), ("satis", "Satış (KDV hariç / KDV dahil)"),
            ("maliyet", "Toplam maliyet (KDV hariç / alış KDV dahil)"), ("kar", "KAZANÇ (KDV hariç)"),
            ("oran", "Kâr oranı (satışa göre)"),
        )):
            ttk.Label(oz, text=etiket).grid(row=i, column=0, sticky="w", pady=2, padx=(0, 12))
            v = tk.StringVar(value="—")
            lbl = ttk.Label(oz, textvariable=v, style="Kar.TLabel" if anahtar == "kar" else "Sonuc.TLabel")
            lbl.grid(row=i, column=1, sticky="w", pady=2)
            self.anlik_v[anahtar] = (v, lbl)
        self._not(p, "Kazanç KDV hariç tutarlarla hesaplanır (KDV devlete gider). Malzeme maliyeti bugünkü kur ve fire ile, "
                  "hizmet maliyeti Hizmetler sekmesindeki maliyetle hesaplanır. Bu sayfa müşteri ekranı değiştikçe güncellenir.",
                  row=3, column=0, pady=(10, 0))
        self.anlik_yenile()

    def anlik_yenile(self):
        if not hasattr(self, "anlik_v"):
            return
        self.t_anlik.delete(*self.t_anlik.get_children())
        for v, _ in self.anlik_v.values():
            v.set("—")
        h = self.ana.hesap
        if not h:
            self.anlik_v["ayar"][0].set("Müşteri ekranında teklife henüz kalem eklenmedi.")
            return
        for k in h["kalemler"]:
            mal = k.get("maliyet")
            if k["tur"] == "malzeme":
                if k.get("alis_fiyat"):
                    kur = f" (kur {sayi_yaz(k['kur'], 2)})" if k.get("alis_para") != "TL" and k.get("kur") else ""
                    detay = (f"{sayi_yaz(k['m2'], 2)} m² • alış {k['alis_fiyat']} {k['alis_para']}{kur}"
                             f" = {para(k['alis_tl_m2'] or 0)}/m² • fire %{kisa(k.get('fire') or 0)}")
                else:
                    detay = "Alış fiyatı girilmemiş (Malzemeler sekmesi)"
            else:
                bm = k.get("birim_maliyet")
                detay = f"{kalem_satiri(k)[2]} • birim maliyet {para(bm)}" if bm is not None else "Maliyet girilmemiş (tamamı kâr)"
            self.t_anlik.insert("", "end", values=(
                k["ad"], detay, sayi_yaz(k["tutar"]), sayi_yaz(mal) if mal is not None else "-",
                sayi_yaz(k["tutar"] - mal) if mal is not None else "-"))
        a = self.anlik_v
        a["ayar"][0].set(f"{para(h['min_fark'])}  /  {para(h['yuvarlama'])}")
        a["satis"][0].set(f"{para(h['satis_haric'])}  /  {para(h['satis_dahil'])}")
        if h.get("maliyet_haric") is not None:
            _, dahil = kdv_hesapla(h["maliyet_haric"], sayi_oku(self.veri.d.get("alis_kdv")) or 0)
            a["maliyet"][0].set(f"{para(h['maliyet_haric'])}  /  {para(dahil)}")
            kar = h["kar"]
            a["kar"][0].set(para(kar))
            a["kar"][1].configure(style="Kar.TLabel" if kar >= 0 else "Zarar.TLabel")
            a["oran"][0].set(f"% {sayi_yaz(kar / h['satis_haric'] * 100, 1)}" if h["satis_haric"] else "—")
        else:
            a["maliyet"][0].set("Eksik: alış fiyatı girilmemiş malzeme var")

    # ------------------------------------------------------------ kayıtlar
    def _kayitlar(self):
        p = self.s_kayit
        p.columnconfigure(0, weight=1)
        p.rowconfigure(0, weight=1)
        cer, self.t_kayit = self._tablo(p, (
            ("no", "No", 50, "center"), ("tarih", "Tarih", 140, "w"), ("musteri", "Müşteri", 160, "w"),
            ("kalem", "Kalemler", 230, "w"), ("satis", "Satış TL", 110, "e"), ("maliyet", "Maliyet TL", 110, "e"),
            ("kar", "Kâr TL", 110, "e")), yukseklik=12, secim="extended")
        cer.grid(row=0, column=0, sticky="nsew")
        self.v_toplam = tk.StringVar()
        ttk.Label(p, textvariable=self.v_toplam, style="Sonuc.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        dug = ttk.Frame(p)
        dug.grid(row=2, column=0, sticky="w")
        ttk.Button(dug, text="📄 Seçililerin kâr raporu", command=lambda: self.rapor(True)).pack(side="left")
        ttk.Button(dug, text="📄 Tüm kayıtların raporu", command=lambda: self.rapor(False)).pack(side="left", padx=6)
        ttk.Button(dug, text="📄 Teklifi yeniden yazdır", command=self.teklif_tekrar).pack(side="left")
        ttk.Button(dug, text="🗑 Kaydı sil", command=self.kayit_sil).pack(side="left", padx=6)
        self._not(p, "Müşteri ekranında “PDF Teklif” her basıldığında buraya bir kayıt eklenir. Tutarlar KDV hariçtir. "
                  "Birden fazla kayıt seçmek için Ctrl tuşuna basılı tutun.", row=3, column=0, pady=(6, 0))
        self.kayitlari_yenile()

    def kayitlari_yenile(self):
        self.t_kayit.delete(*self.t_kayit.get_children())
        ts = tm = tk_ = 0.0
        kayitlar = self.veri.d["kayitlar"]
        for i in range(len(kayitlar) - 1, -1, -1):
            k = kayitlar[i]
            ts += k["satis_haric"]
            if k.get("kar") is not None:
                tm += k["maliyet_haric"]
                tk_ += k["kar"]
            ozet = ", ".join(kl["ad"] for kl in k.get("kalemler", []))
            self.t_kayit.insert("", "end", iid=str(i), values=(
                k["no"], k["tarih"], k.get("musteri") or "-", ozet[:60], sayi_yaz(k["satis_haric"]),
                sayi_yaz(k["maliyet_haric"]) if k.get("kar") is not None else "-",
                sayi_yaz(k["kar"]) if k.get("kar") is not None else "-"))
        self.v_toplam.set(f"{len(kayitlar)} kayıt  •  Satış: {para(ts)}  •  Maliyet: {para(tm)}  •  Kâr: {para(tk_)}")

    def _secili(self):
        return [self.veri.d["kayitlar"][int(i)] for i in sorted(self.t_kayit.selection(), key=int)
                if int(i) < len(self.veri.d["kayitlar"])]

    def rapor(self, secili):
        kayitlar = self._secili() if secili else list(self.veri.d["kayitlar"])
        if not kayitlar:
            messagebox.showinfo("Rapor", "Rapor için kayıt seçin." if secili else "Henüz kayıt yok.", parent=self)
            return
        ek = f"No{kayitlar[0]['no']}" if len(kayitlar) == 1 else f"{len(kayitlar)}_kayit"
        yol = os.path.join(pdf_klasoru(), f"Kar_Raporu_{ek}_{datetime.datetime.now():%Y-%m-%d_%H%M}.pdf")
        try:
            kar_pdf(kayitlar, yol, self.veri.d["firma"], self.veri.logo_yolu())
        except Exception as hata:
            messagebox.showerror("PDF oluşturulamadı", str(hata), parent=self)
            return
        dosya_ac(yol)

    def teklif_tekrar(self):
        s = self._secili()
        if len(s) != 1:
            messagebox.showinfo("Teklif", "Bir kayıt seçin.", parent=self)
            return
        k = s[0]
        yol = os.path.join(pdf_klasoru(), f"Teklif_{k['no']}_tekrar.pdf")
        try:
            musteri_pdf(k, yol, self.veri.d["firma"], self.veri.logo_yolu(), self.veri.d.get("teklif_notu", ""))
        except Exception as hata:
            messagebox.showerror("PDF oluşturulamadı", str(hata), parent=self)
            return
        dosya_ac(yol)

    def kayit_sil(self):
        secim = self._secili()
        if secim and messagebox.askyesno("Kayıt sil", f"{len(secim)} kayıt silinsin mi?", parent=self):
            self.veri.kayitlari_sil([k["id"] for k in secim])
            self.kayitlari_yenile()

    # ------------------------------------------------------------ firma ve teklif
    def _firma(self):
        p = self.s_firma
        p.columnconfigure(1, weight=1)
        ttk.Label(p, text="Firma bilgileri (PDF tekliflerde görünür)", style="Baslik.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
        self.firma_v = {a: tk.StringVar() for a in ("ad", "adres", "tel", "web", "eposta", "iban")}
        for i, (a, etiket) in enumerate((("ad", "Firma adı"), ("adres", "Adres"), ("tel", "Telefon / WhatsApp"),
                                         ("web", "Web sitesi"), ("eposta", "E-posta"), ("iban", "IBAN")), start=1):
            self._giris(p, i, etiket, self.firma_v[a], sola=True)
        logo = ttk.Frame(p)
        logo.grid(row=7, column=0, columnspan=2, sticky="we", pady=6)
        ttk.Label(logo, text="Logo").pack(side="left", padx=(0, 8))
        self.v_logo = tk.StringVar()
        ttk.Label(logo, textvariable=self.v_logo, style="Not.TLabel").pack(side="left")
        ttk.Button(logo, text="Varsayılan logo", command=self.logo_varsayilan).pack(side="right")
        ttk.Button(logo, text="🖼 Logo seç (PNG / JPG)…", command=self.logo_sec).pack(side="right", padx=6)

        ttk.Label(p, text="Teklif notları (PDF'in altında ve WhatsApp metninde görünür)", style="Sonuc.TLabel").grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(10, 2))
        self.t_not = tk.Text(p, height=4, font=(self.fa, 11), wrap="word", relief="solid", borderwidth=1)
        self.t_not.grid(row=9, column=0, columnspan=2, sticky="we")
        self._not(p, "Örnek: “Teklif 7 gün geçerlidir. Siparişte %50 ön ödeme alınır. Montaj süresi 3 iş günüdür.”",
                  row=10, column=0, columnspan=2, pady=(2, 0))

        ttk.Label(p, text="Fiyat kuralları", style="Sonuc.TLabel").grid(row=11, column=0, columnspan=2, sticky="w", pady=(10, 2))
        self.v_min_tutar = tk.StringVar()
        self._giris(p, 12, "Minimum teklif tutarı (TL, KDV hariç)", self.v_min_tutar, genislik=12)
        self._not(p, "Teklif bu tutarın altında kalırsa aradaki fark “Minimum ücret farkı” olarak eklenir (boş = yok). "
                  "Yuvarlama müşteri ekranındaki “Genel toplamı yuvarla” kutusundan açılıp kapatılır.",
                  row=13, column=0, columnspan=2)
        self._dugme(p, "💾  Kaydet", YESIL, self.firma_kaydet, "#166b2e").grid(row=14, column=0, sticky="w", pady=(12, 0))
        self.firma_doldur()

    def firma_doldur(self):
        f = self.veri.d["firma"]
        for a, v in self.firma_v.items():
            v.set(f.get(a, ""))
        self.v_logo.set(f"Özel logo: {f['logo']}" if f.get("logo") else "Arabacı Reklam logosu (varsayılan)")
        self.t_not.delete("1.0", "end")
        self.t_not.insert("1.0", self.veri.d.get("teklif_notu", ""))
        self.v_min_tutar.set(self.veri.d["fiyat_kurallari"].get("min_tutar", ""))

    def firma_kaydet(self):
        if not self._sayilar_gecerli(("Minimum teklif tutarı", self.v_min_tutar)):
            return
        f = self.veri.d["firma"]
        for a, v in self.firma_v.items():
            f[a] = v.get().strip()
        self.veri.d["teklif_notu"] = self.t_not.get("1.0", "end").strip()
        self.veri.d["fiyat_kurallari"]["min_tutar"] = self.v_min_tutar.get().strip()
        self.veri.kaydet()
        self.ana.teklif_hesapla()
        messagebox.showinfo("Firma ve teklif", "Kaydedildi.", parent=self)

    def logo_sec(self):
        yol = filedialog.askopenfilename(parent=self, title="Logo seçin",
                                         filetypes=[("Resim", "*.png *.jpg *.jpeg"), ("Tümü", "*.*")])
        if not yol:
            return
        uzanti = os.path.splitext(yol)[1].lower() or ".png"
        ad = f"firma_logo{uzanti}"
        try:
            shutil.copyfile(yol, os.path.join(self.veri.klasor, ad))
            if PDF_VAR:
                ImageReader(os.path.join(self.veri.klasor, ad)).getSize()
        except Exception as hata:
            messagebox.showerror("Logo", f"Logo kullanılamadı:\n{hata}", parent=self)
            return
        self.veri.d["firma"]["logo"] = ad
        self.veri.kaydet()
        self.firma_doldur()

    def logo_varsayilan(self):
        self.veri.d["firma"]["logo"] = ""
        self.veri.kaydet()
        self.firma_doldur()

    # ------------------------------------------------------------ ayarlar
    def _ayarlar(self):
        p = self.s_ayar
        p.columnconfigure(1, weight=1)
        ttk.Label(p, text="Ayarlar", style="Baslik.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.v_alis_kdv = tk.StringVar(value=self.veri.d.get("alis_kdv", "20"))
        self._secim(p, 1, "Malzeme alış KDV oranı (%)", self.v_alis_kdv, KDV_ORANLARI, serbest=True, genislik=6)
        self.v_alis_kdv.trace_add("write", lambda *_: self._alis_kdv())
        ttk.Separator(p).grid(row=2, column=0, columnspan=2, sticky="we", pady=12)
        ttk.Label(p, text="Şifre değiştir", style="Sonuc.TLabel").grid(row=3, column=0, sticky="w")
        self.s1, self.s2, self.s3 = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self._giris(p, 4, "Mevcut şifre", self.s1, show="•", genislik=20)
        self._giris(p, 5, "Yeni şifre", self.s2, show="•", genislik=20)
        self._giris(p, 6, "Yeni şifre (tekrar)", self.s3, show="•", genislik=20)
        ttk.Button(p, text="Şifreyi değiştir", command=self.sifre_degistir).grid(row=7, column=1, sticky="e", pady=6)
        ttk.Separator(p).grid(row=8, column=0, columnspan=2, sticky="we", pady=12)
        ttk.Label(p, text="Veri klasörü (Google Drive ile bilgisayarlar arası ortak kullanım)", style="Sonuc.TLabel").grid(
            row=9, column=0, columnspan=2, sticky="w")
        self.v_klasor = tk.StringVar()
        ttk.Label(p, textvariable=self.v_klasor, justify="left").grid(row=10, column=0, columnspan=2, sticky="w", pady=4)
        dug = ttk.Frame(p)
        dug.grid(row=11, column=0, columnspan=2, sticky="w")
        ttk.Button(dug, text="📁 Ortak klasör seç (Google Drive)…", command=self.klasor_sec).pack(side="left")
        ttk.Button(dug, text="💻 Bu bilgisayarın kendi klasörüne dön", command=self.yerele_don).pack(side="left", padx=6)
        self._not(p, "Her bilgisayarda Google Drive masaüstü uygulamasını aynı hesapla açın, sonra burada Google Drive'daki "
                  "aynı klasörü seçin (örn. G:\\Drive'ım). Program içinde “ArabaciM2” klasörünü kendisi oluşturur. "
                  "Malzemeler, hizmetler, fiyatlar, firma bilgileri, kayıtlar ve şifre ortak olur; değişiklikler birkaç "
                  f"saniye ile 1 dakika içinde diğer bilgisayara geçer.\nPDF klasörü (her bilgisayarda ayrı): {pdf_klasoru()}",
                  row=12, column=0, columnspan=2, pady=(6, 0))
        self._klasor_yaz()

    def _klasor_yaz(self):
        ortak = bool(self.ana.yerel.get("klasor")) and os.path.normcase(self.veri.klasor) == os.path.normcase(self.ana.yerel["klasor"])
        self.v_klasor.set(("Ortak klasör: " if ortak else "Sadece bu bilgisayar: ") + self.veri.klasor)

    def _klasore_gec(self, hedef, ortak):
        eski = self.veri
        eski.kaydet()
        vardi = os.path.exists(os.path.join(hedef, "veriler.json"))
        yeni = Veri(hedef)
        if vardi and ortak:
            silinen = sorted(set(yeni.d["silinen_kayitlar"]) | set(eski.d["silinen_kayitlar"]))
            yeni.d["kayitlar"] = kayitlari_birlestir(yeni.d["kayitlar"], eski.d["kayitlar"], silinen)
            yeni.d["silinen_kayitlar"] = silinen
            yeni.d["son_teklif_no"] = max(yeni.d["son_teklif_no"], eski.d["son_teklif_no"])
            if not yeni.d.get("sifre"):
                yeni.d["sifre"] = eski.d.get("sifre")
            if not yeni.d["kurlar"]:
                yeni.d["kurlar"] = eski.d["kurlar"]
            mesaj = ("Bu klasörde zaten veri vardı; malzemeler, fiyatlar ve şifre oradan kullanılıyor.\n"
                     "Bu bilgisayardaki teklif kayıtları da ona eklendi.")
        else:
            yeni.d = json.loads(json.dumps(eski.d))
            logo = eski.d["firma"].get("logo")
            if logo and os.path.exists(os.path.join(eski.klasor, logo)):
                shutil.copyfile(os.path.join(eski.klasor, logo), os.path.join(hedef, logo))
            mesaj = "Bu bilgisayardaki malzemeler, fiyatlar ve kayıtlar yeni klasöre kopyalandı."
        yeni.kaydet()
        self.ana.yerel["klasor"] = hedef if ortak else None
        yerel_ayar_yaz(self.ana.yerel)
        self.ana.veri = yeni
        self.ana.veri_degisti()
        self._klasor_yaz()
        messagebox.showinfo("Veri klasörü", mesaj, parent=self)

    def klasor_sec(self):
        secim = filedialog.askdirectory(parent=self, title="Google Drive'daki klasörü seçin (örn. Drive'ım)")
        if not secim:
            return
        hedef = secim if (os.path.basename(os.path.normpath(secim)).lower() == "arabacim2"
                          or os.path.exists(os.path.join(secim, "veriler.json"))) else os.path.join(secim, "ArabaciM2")
        hedef = os.path.normpath(hedef)
        if os.path.normcase(hedef) == os.path.normcase(self.veri.klasor):
            messagebox.showinfo("Veri klasörü", "Bu klasör zaten kullanılıyor.", parent=self)
            return
        try:
            self._klasore_gec(hedef, ortak=True)
        except Exception as hata:
            messagebox.showerror("Veri klasörü", f"Klasör kullanılamadı:\n{hata}", parent=self)

    def yerele_don(self):
        if not self.ana.yerel.get("klasor"):
            messagebox.showinfo("Veri klasörü", "Zaten bu bilgisayarın kendi klasörü kullanılıyor.", parent=self)
            return
        if messagebox.askyesno("Veri klasörü", "Bu bilgisayar ortak klasörü bırakıp kendi klasörünü kullansın mı?\n"
                               "Ortak klasördeki güncel veriler bu bilgisayara kopyalanır.", parent=self):
            self._klasore_gec(yerel_klasor(), ortak=False)

    def _alis_kdv(self):
        self.veri.d["alis_kdv"] = self.v_alis_kdv.get()
        self.veri.kaydet()
        self.anlik_yenile()

    def sifre_degistir(self):
        if sifre_ozet(self.s1.get()) != self.veri.d["sifre"]:
            messagebox.showerror("Şifre", "Mevcut şifre yanlış.", parent=self)
            return
        if len(self.s2.get()) < 4 or self.s2.get() != self.s3.get():
            messagebox.showerror("Şifre", "Yeni şifreler aynı değil ya da çok kısa (en az 4 karakter).", parent=self)
            return
        self.veri.d["sifre"] = sifre_ozet(self.s2.get())
        self.veri.kaydet()
        for v in (self.s1, self.s2, self.s3):
            v.set("")
        messagebox.showinfo("Şifre", "Şifre değiştirildi.", parent=self)


if __name__ == "__main__":
    Uygulama().mainloop()
