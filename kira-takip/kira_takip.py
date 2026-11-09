"""Kira Takip - Windows masaüstü programı.

Binalar ve daireler (ev sahibi, tapu, abonelikler, DASK), kiracılar (kimlik, iletişim, acil durum kişisi,
belgeler), kira sözleşmesi ve depozito, TÜFE ile kira artışı, kira ödeme takibi, hatırlatmalar,
yıllık kira geliri ve PDF raporlar. Şifreli giriş; veriler isteğe bağlı olarak Google Drive klasöründe.
"""

import calendar
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import tkinter as tk
import tkinter.font as tkfont
import urllib.parse
import uuid
import webbrowser
from tkinter import filedialog, messagebox, ttk

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    PDF_VAR = True
except ImportError:  # pragma: no cover
    PDF_VAR = False

UYGULAMA_ADI = "Kira Takip"
SURUM = "1.0"
SIFRE_TUZ = "kira-takip::"
APP_ID = "ArabaciReklam.KiraTakip"
TABLOLAR = ["binalar", "daireler", "kiracilar", "artislar", "borclar", "odemeler"]
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

KIRMIZI = "#d62828"
YESIL = "#1e8e3e"
MAVI = "#1f5fbf"
GRI = "#666666"
TURUNCU = "#c76a00"


def tc_gecerli(tc):
    """TC kimlik numarası algoritma kontrolü."""
    if len(tc) != 11 or not tc.isdigit() or tc[0] == "0":
        return False
    r = [int(c) for c in tc]
    if ((sum(r[0:9:2]) * 7 - sum(r[1:8:2])) % 10) != r[9]:
        return False
    return sum(r[:10]) % 10 == r[10]


# ================================================================ yardımcılar

def sayi_oku(metin):
    s = (str(metin) if metin is not None else "").strip().replace(" ", "").replace("TL", "").replace("%", "")
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


def yuv(x):
    return round(x + 0.0, 2)


def sayi_yaz(x, basamak=2):
    return f"{x:,.{basamak}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def para(x):
    return f"{sayi_yaz(yuv(x))} TL"


def para_kisa(x):
    x = yuv(x)
    return f"{sayi_yaz(x, 0)} TL" if float(x).is_integer() else f"{sayi_yaz(x)} TL"


def bugun():
    return datetime.date.today().isoformat()


def bu_donem():
    return bugun()[:7]


def donem_adi(d):
    if not d:
        return ""
    y, a = d.split("-")
    return f"{AYLAR[int(a) - 1]} {y}"


def donem_kaydir(d, n):
    y, a = map(int, d.split("-"))
    a = a - 1 + n
    y += a // 12
    a = a % 12
    return f"{y}-{a + 1:02d}"


def donemler(bas, son):
    r, d = [], bas
    while d <= son:
        r.append(d)
        d = donem_kaydir(d, 1)
    return r


def ay_son_gunu(d):
    y, a = map(int, d.split("-"))
    return f"{d}-{calendar.monthrange(y, a)[1]:02d}"


def tarih_yaz(t):
    if not t:
        return ""
    y, a, g = t.split("-")
    return f"{g}.{a}.{y}"


def tarih_oku(metin):
    """'09.11.2026', '9.11.2026', '2026-11-09' -> '2026-11-09'. Hatalıysa None."""
    s = (metin or "").strip()
    try:
        if "-" in s:
            return datetime.date.fromisoformat(s).isoformat()
        g, a, y = s.replace("/", ".").split(".")
        return datetime.date(int(y), int(a), int(g)).isoformat()
    except Exception:
        return None


def uid():
    return uuid.uuid4().hex[:10]


def sifre_ozet(s):
    return hashlib.sha256((SIFRE_TUZ + s).encode("utf-8")).hexdigest()


def tel_no(t):
    s = "".join(ch for ch in str(t or "") if ch.isdigit())
    if not s:
        return ""
    if s.startswith("90") and len(s) == 12:
        return s
    if s.startswith("0"):
        s = s[1:]
    return "90" + s if len(s) == 10 else s


def wa_ac(tel, metin):
    adres = "https://wa.me/" + tel_no(tel) + "?text=" + urllib.parse.quote(metin)
    webbrowser.open(adres)


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


def yerel_klasor():
    k = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "KiraTakip")
    os.makedirs(k, exist_ok=True)
    return k


def yerel_ayar_oku():
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


def pdf_klasoru():
    k = os.path.join(os.path.expanduser("~"), "Documents", "Kira Takip")
    os.makedirs(k, exist_ok=True)
    return k


# ================================================================ veri

def birlestir(a, b):
    """İki veri kopyasını birleştirir: kayıtlarda en son değiştirilen kazanır, silinenler geri gelmez."""
    if not b:
        return a
    if not a:
        return b
    sonuc = {"surum": 1}
    silinen = {}
    for kaynak in (a, b):
        for t, ids in kaynak.get("_silinen", {}).items():
            hedef = silinen.setdefault(t, {})
            for i, z in ids.items():
                hedef[i] = max(z, hedef.get(i, 0))
    sonuc["_silinen"] = silinen
    for t in TABLOLAR:
        hepsi = {}
        for kaynak in (a, b):
            for k in kaynak.get(t, []):
                eski = hepsi.get(k["id"])
                if eski is None or k.get("_z", 0) > eski.get("_z", 0):
                    hepsi[k["id"]] = k
        sil = silinen.get(t, {})
        sonuc[t] = [k for i, k in hepsi.items() if i not in sil]
    for alan in ("ayarlar", "sifre"):
        za, zb = a.get(alan + "_z", 0), b.get(alan + "_z", 0)
        kazanan = a if za >= zb else b
        sonuc[alan] = kazanan.get(alan)
        sonuc[alan + "_z"] = max(za, zb)
    return sonuc



class Veri:
    """Bütün kayıtlar: <veri klasörü>\\kira.json; belgeler: <veri klasörü>\\belgeler\\"""

    def __init__(self, klasor=None):
        self.klasor = klasor or yerel_klasor()
        os.makedirs(self.klasor, exist_ok=True)
        self.yol = os.path.join(self.klasor, "kira.json")
        d = self._oku()
        if d is None:
            try:
                os.replace(self.yol, self.yol + f".bozuk-{datetime.datetime.now():%Y%m%d%H%M%S}")
            except Exception:
                pass
            d = {}
        self.d = self._tamamla(d)
        self._zaman = self._dosya_zamani()

    @staticmethod
    def _tamamla(d):
        for t in TABLOLAR:
            d.setdefault(t, [])
        d.setdefault("_silinen", {})
        d.setdefault("ayarlar", {})
        d.setdefault("ayarlar_z", 0)
        d.setdefault("sifre", None)
        d.setdefault("sifre_z", 0)
        return d

    def _oku(self):
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

    @property
    def kurulu(self):
        return bool(self.d.get("sifre"))

    def yenile(self):
        z = self._dosya_zamani()
        if z is None or z == self._zaman:
            return False
        disk = self._oku()
        if not disk:
            return False
        self.d = self._tamamla(birlestir(self.d, self._tamamla(disk)))
        self._zaman = z
        return True

    def kaydet(self):
        disk = self._oku()
        if disk:
            self.d = self._tamamla(birlestir(self.d, self._tamamla(disk)))
        metin = json.dumps(self.d, ensure_ascii=False, indent=1)
        gecici = self.yol + ".tmp"
        try:
            with open(gecici, "w", encoding="utf-8") as f:
                f.write(metin)
            os.replace(gecici, self.yol)
        except OSError:
            with open(self.yol, "w", encoding="utf-8") as f:
                f.write(metin)
        self._zaman = self._dosya_zamani()

    def yaz(self, tablo, kayit, kaydet=True):
        kayit = dict(kayit)
        kayit.setdefault("id", uid())
        kayit["_z"] = time.time()
        liste = self.d[tablo]
        for i, k in enumerate(liste):
            if k["id"] == kayit["id"]:
                liste[i] = kayit
                break
        else:
            liste.append(kayit)
        if kaydet:
            self.kaydet()
        return kayit

    def sil(self, tablo, kimlik, kaydet=True):
        self.d[tablo] = [k for k in self.d[tablo] if k["id"] != kimlik]
        self.d["_silinen"].setdefault(tablo, {})[kimlik] = time.time()
        if kaydet:
            self.kaydet()

    def ayar(self, ad, varsayilan=""):
        v = self.d["ayarlar"].get(ad)
        return varsayilan if v in (None, "") else v

    def ayarlari_yaz(self, yeni):
        self.d["ayarlar"] = dict(self.d["ayarlar"], **yeni)
        self.d["ayarlar_z"] = time.time()
        self.kaydet()

    def sifre_yaz(self, sifre):
        self.d["sifre"] = sifre_ozet(sifre)
        self.d["sifre_z"] = time.time()
        self.kaydet()

    def sifre_dogru(self, sifre):
        return sifre_ozet(sifre) == self.d.get("sifre")

    def bul(self, tablo, kimlik):
        return next((k for k in self.d[tablo] if k["id"] == kimlik), None) if kimlik else None

    # ---------------------------------------------------------------- binalar ve daireler
    @staticmethod
    def _no_sira(no):
        try:
            return (0, float(no), "")
        except (TypeError, ValueError):
            return (1, 0, str(no))

    def binalar(self):
        return sorted(self.d["binalar"], key=lambda b: b["ad"].lower())

    def bina_daireleri(self, bina_id, pasif=False):
        return sorted([d for d in self.d["daireler"] if d["bina_id"] == bina_id and (pasif or d.get("aktif", True))],
                      key=lambda d: self._no_sira(d["no"]))

    def daire_adi(self, d, kisa=False):
        if not d:
            return "?"
        b = self.bul("binalar", d["bina_id"])
        return f"Daire {d['no']}" if kisa or not b else f"{b['ad']} – Daire {d['no']}"

    def aktif_kiraci(self, daire_id):
        l = [k for k in self.d["kiracilar"] if k["daire_id"] == daire_id and not k.get("cikis")]
        l.sort(key=lambda k: k.get("giris", ""), reverse=True)
        return l[0] if l else None

    def daire_kiracilari(self, daire_id):
        return sorted([k for k in self.d["kiracilar"] if k["daire_id"] == daire_id], key=lambda k: k.get("giris", ""), reverse=True)

    # ---------------------------------------------------------------- kira
    def kira_gecmisi(self, kiraci_id):
        return sorted([a for a in self.d["artislar"] if a["kiraci_id"] == kiraci_id], key=lambda a: a["tarih"])

    def kira_tutari(self, k, donem):
        """Kiracının o aydaki kirası (artışlar dahil)."""
        tutar = k.get("ilk_kira") or 0
        for a in self.kira_gecmisi(k["id"]):
            if a["tarih"][:7] <= donem:
                tutar = a["yeni_kira"]
        return tutar

    def guncel_kira(self, k):
        return self.kira_tutari(k, "9999-12")

    @staticmethod
    def kira_aylari(k, son=None):
        """Kiracının oturduğu aylar (taşınma ayından çıkış ayına ya da bu aya kadar)."""
        if not k.get("giris"):
            return []
        bitis = k["cikis"][:7] if k.get("cikis") else (son or bu_donem())
        return donemler(k["giris"][:7], min(bitis, son or "9999-12"))

    @property
    def takip(self):
        return bool(self.ayar("kira_takibi", True))

    def kiralari_yaz(self):
        """Taşınma ayından bu aya kadar yazılmamış kira borçlarını yazar."""
        if not self.takip:
            return []
        yazilan = set()
        for k in self.d["kiracilar"]:
            for m in self.kira_aylari(k, bu_donem()):
                kimlik = f"kira-{k['id']}-{m}"
                if self.bul("borclar", kimlik) or kimlik in self.d["_silinen"].get("borclar", {}):
                    continue
                tutar = self.kira_tutari(k, m)
                if not tutar or tutar <= 0:
                    continue
                gun = min(int(k.get("odeme_gunu") or 1), 28)
                self.yaz("borclar", {"id": kimlik, "kiraci_id": k["id"], "daire_id": k["daire_id"], "donem": m,
                                     "baslik": f"{donem_adi(m)} kirası", "tutar": tutar, "tarih": f"{m}-{gun:02d}"}, False)
                yazilan.add(m)
        if yazilan:
            self.kaydet()
        return sorted(yazilan)

    def hesap(self, kiraci_id):
        """Kiracının kira hesabı. bakiye < 0 borç, > 0 fazla ödeme."""
        borclar = sorted([dict(b, kalan=b["tutar"]) for b in self.d["borclar"] if b["kiraci_id"] == kiraci_id], key=lambda b: b["donem"])
        odenen = sum(o["tutar"] for o in self.d["odemeler"] if o["kiraci_id"] == kiraci_id)
        kalan = odenen
        for b in borclar:
            p = max(0.0, min(b["kalan"], kalan))
            b["kalan"] = yuv(b["kalan"] - p)
            kalan -= p
        acik = [b for b in borclar if b["kalan"] > 0.004]
        geciken = [b for b in acik if b["tarih"] < bugun()]
        return {"bakiye": yuv(odenen - sum(b["tutar"] for b in borclar)), "acik": acik, "geciken": geciken}

    def hareketler(self, kiraci_id):
        l = [{"tarih": b["tarih"], "sira": 0, "ad": b["baslik"], "tutar": -b["tutar"], "borc": b}
             for b in self.d["borclar"] if b["kiraci_id"] == kiraci_id]
        l += [{"tarih": o["tarih"], "sira": 1, "ad": ("İade" if o["tutar"] < 0 else f"Ödeme ({o['yontem']})") + (f" – {o['aciklama']}" if o.get("aciklama") else ""),
               "tutar": o["tutar"], "odeme": o} for o in self.d["odemeler"] if o["kiraci_id"] == kiraci_id]
        l.sort(key=lambda x: (x["tarih"], x["sira"]))
        bakiye = 0.0
        for x in l:
            bakiye = yuv(bakiye + x["tutar"])
            x["bakiye"] = bakiye
        return l

    def yillik_kira(self, yil):
        """{daire_id: {donem: (tutar, kiraci, gelecek_mi)}} – o yıl her ay hangi kiracı kaça oturdu (ya da oturacak)."""
        sonuc = {}
        aylar = [f"{yil}-{a:02d}" for a in range(1, 13)]
        for k in self.d["kiracilar"]:
            if not k.get("giris"):
                continue
            bas = k["giris"][:7]
            son = k["cikis"][:7] if k.get("cikis") else f"{yil}-12"
            for m in aylar:
                if bas <= m <= son:
                    sonuc.setdefault(k["daire_id"], {})[m] = (self.kira_tutari(k, m), k, m > bu_donem())
        return sonuc

    # ---------------------------------------------------------------- uyarılar
    @staticmethod
    def sonraki_yildonumu(baslangic):
        """Sözleşme başlangıcının bugünden sonraki (ya da bugünkü) yıldönümü."""
        if not baslangic:
            return None
        b = datetime.date.fromisoformat(baslangic)
        bu = datetime.date.today()
        for y in range(bu.year, bu.year + 2):
            try:
                t = b.replace(year=y)
            except ValueError:
                t = b.replace(year=y, day=28)
            if t >= bu and y > b.year:
                return t.isoformat()
        return None

    def uyarilar(self):
        """[(önem, tür, nesne_türü, nesne_id, yer, kişi, açıklama, tarih)]"""
        l, bu = [], datetime.date.today()
        sozlesme_gun = int(self.ayar("uyari_sozlesme_gun", 60))
        artis_gun = int(self.ayar("uyari_artis_gun", 30))
        for k in self.d["kiracilar"]:
            if k.get("cikis"):
                continue
            d = self.bul("daireler", k["daire_id"])
            yer = self.daire_adi(d)
            if k.get("sozlesme_bitis"):
                kalan = (datetime.date.fromisoformat(k["sozlesme_bitis"]) - bu).days
                if kalan < 0:
                    l.append((1, "Sözleşme süresi doldu", "kiraci", k["id"], yer, k["ad"],
                              f"{-kalan} gün önce doldu. Yeni sözleşme yapın ya da bitiş tarihini güncelleyin (kiracı çıkmazsa sözleşme aynı şartlarla 1 yıl uzar).",
                              k["sozlesme_bitis"]))
                elif kalan <= sozlesme_gun:
                    l.append((2, "Sözleşme bitiyor", "kiraci", k["id"], yer, k["ad"], f"{kalan} gün kaldı.", k["sozlesme_bitis"]))
            yd = self.sonraki_yildonumu(k.get("sozlesme_bas") or k.get("giris"))
            if yd:
                kalan = (datetime.date.fromisoformat(yd) - bu).days
                son_artis = self.kira_gecmisi(k["id"])
                yapildi = son_artis and son_artis[-1]["tarih"] >= (datetime.date.fromisoformat(yd) - datetime.timedelta(days=60)).isoformat()
                if kalan <= artis_gun and not yapildi:
                    l.append((2, "Kira artış zamanı", "kiraci", k["id"], yer, k["ad"],
                              f"Sözleşme yıldönümü {tarih_yaz(yd)} ({kalan} gün). TÜFE ile kira artışını hesaplayın.", yd))
            if self.takip:
                h = self.hesap(k["id"])
                if h["geciken"]:
                    l.append((1, "Kira gecikti", "kiraci", k["id"], yer, k["ad"],
                              ", ".join(b["baslik"] for b in h["geciken"]) + f" – toplam {para_kisa(sum(b['kalan'] for b in h['geciken']))}",
                              h["geciken"][0]["tarih"]))
        for d in self.d["daireler"]:
            if d.get("aktif", True) and d.get("dask_bitis"):
                kalan = (datetime.date.fromisoformat(d["dask_bitis"]) - bu).days
                if kalan <= 30:
                    l.append((1 if kalan < 0 else 2, "DASK " + ("süresi doldu" if kalan < 0 else "bitiyor"), "daire", d["id"], self.daire_adi(d),
                              d.get("sahip_ad", ""), f"{abs(kalan)} gün {'önce doldu' if kalan < 0 else 'kaldı'}. Poliçeyi yenileyin.", d["dask_bitis"]))
        l.sort(key=lambda x: (x[0], x[7]))
        return l

    def hatirlatma_metni(self, k):
        h = self.hesap(k["id"])
        d = self.bul("daireler", k["daire_id"])
        t = f"Merhaba {k['ad']},\n{self.daire_adi(d)} kira bilginiz:\n\n"
        if h["bakiye"] < -0.004:
            for b in h["acik"]:
                t += f"• {b['baslik']}: {para_kisa(b['kalan'])}\n"
            t += f"\nToplam ödenecek: {para(-h['bakiye'])}\n"
            if self.ayar("iban"):
                t += f"\nIBAN: {self.ayar('iban')}" + (f"\nAlıcı: {self.ayar('iban_ad')}" if self.ayar("iban_ad") else "") + "\n"
        elif h["bakiye"] > 0.004:
            t += f"Fazla / peşin ödemeniz: +{para(h['bakiye'])}. Sonraki kiralardan düşülecektir.\n"
        else:
            t += "Kira borcunuz bulunmamaktadır, teşekkür ederiz.\n"
        return t + f"\nİyi günler,\n{self.ayar('ad_soyad', '')}".rstrip()


# ================================================================ PDF

_FONT = None


def fontlar():
    global _FONT
    if _FONT:
        return _FONT
    for normal, kalin in ((kaynak_yolu("fonts/DejaVuSans.ttf"), kaynak_yolu("fonts/DejaVuSans-Bold.ttf")),
                          (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf")):
        if os.path.exists(normal) and os.path.exists(kalin):
            pdfmetrics.registerFont(TTFont("TR", normal))
            pdfmetrics.registerFont(TTFont("TR-B", kalin))
            pdfmetrics.registerFontFamily("TR", normal="TR", bold="TR-B", italic="TR", boldItalic="TR-B")
            _FONT = ("TR", "TR-B")
            return _FONT
    _FONT = ("Helvetica", "Helvetica-Bold")
    return _FONT


class Rapor:
    def __init__(self, veri, baslik, alt=""):
        F, FB = fontlar()
        self.v = veri
        self.st = {
            "baslik": ParagraphStyle("b", fontName=FB, fontSize=17, leading=21, textColor=colors.HexColor(MAVI)),
            "alt": ParagraphStyle("a", fontName=F, fontSize=9.5, textColor=colors.HexColor(GRI), spaceAfter=8),
            "h2": ParagraphStyle("h", fontName=FB, fontSize=12, leading=15, spaceBefore=12, spaceAfter=4, textColor=colors.HexColor(MAVI)),
            "p": ParagraphStyle("p", fontName=F, fontSize=9.5, leading=13),
            "kutu": ParagraphStyle("k", fontName=F, fontSize=10, leading=15, backColor=colors.HexColor("#f4f7fb"),
                                   borderColor=colors.HexColor("#d9e2ef"), borderWidth=0.7, borderPadding=8, spaceBefore=4, spaceAfter=10),
            "not": ParagraphStyle("n", fontName=F, fontSize=8.5, leading=11, textColor=colors.HexColor(GRI), spaceBefore=3),
            "hucre": ParagraphStyle("c", fontName=F, fontSize=9, leading=11.5),
            "hucre_r": ParagraphStyle("cr", fontName=F, fontSize=9, leading=11.5, alignment=TA_RIGHT),
            "hucre_b": ParagraphStyle("cb", fontName=FB, fontSize=9, leading=11.5),
            "hucre_br": ParagraphStyle("cbr", fontName=FB, fontSize=9, leading=11.5, alignment=TA_RIGHT),
        }
        self.ogeler = [Paragraph(esc(baslik), self.st["baslik"]), Paragraph(esc(alt), self.st["alt"])]

    def kutu(self, html):
        self.ogeler.append(Paragraph(html, self.st["kutu"]))

    def h2(self, metin):
        self.ogeler.append(Paragraph(esc(metin), self.st["h2"]))

    def p(self, html, stil="p"):
        self.ogeler.append(Paragraph(html, self.st[stil]))

    def tablo(self, basliklar, satirlar, hizalar, genislikler, toplam=None):
        def h(m, i, kalin=False):
            s = ("hucre_b" if kalin else "hucre") + ("r" if hizalar[i] == "r" else "")
            s = {"hucre_br": "hucre_br", "hucre_b": "hucre_b", "hucrer": "hucre_r", "hucre": "hucre"}[s]
            return Paragraph(str(m), self.st[s])
        veri = [[h(b, i, True) for i, b in enumerate(basliklar)]]
        veri += [[h(c, i) for i, c in enumerate(s)] for s in satirlar]
        if toplam:
            veri.append([h(c, i, True) for i, c in enumerate(toplam)])
        toplam_gen = getattr(self, "genislik", 174 * mm)
        t = Table(veri, colWidths=[toplam_gen * g for g in genislikler], repeatRows=1)
        stil = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f8")),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#e3e6eb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
        if toplam:
            stil.append(("LINEABOVE", (0, -1), (-1, -1), 1.2, colors.HexColor("#1d2330")))
        t.setStyle(TableStyle(stil))
        self.ogeler.append(t)

    def kaydet(self, yol):
        v = self.v
        alt = []
        if v.ayar("ad_soyad"):
            alt.append(esc(v.ayar("ad_soyad")))
        alt.append(f"Rapor tarihi: {tarih_yaz(bugun())}")
        self.ogeler.append(Spacer(1, 14))
        self.ogeler.append(Paragraph("<br/>".join(alt), self.st["not"]))
        doc = SimpleDocTemplate(yol, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                                title=os.path.splitext(os.path.basename(yol))[0])
        doc.build(self.ogeler)


def esc(s):
    return (str(s if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def k_(m):
    return f'<font color="{KIRMIZI}">{m}</font>'


def y_(m):
    return f'<font color="{YESIL}">{m}</font>'


def durum_html(bakiye):
    if bakiye < -0.004:
        return k_(f"Borç {para(-bakiye)}")
    if bakiye > 0.004:
        return y_(f"Ön ödeme +{para(bakiye)}")
    return y_("Borcu yok ✓")



def _yatay_kaydet(r, yol):
    """Rapor'u yatay A4 olarak kaydeder (geniş tablolar için)."""
    from reportlab.lib.pagesizes import landscape
    alt = [f"Rapor tarihi: {tarih_yaz(bugun())}"]
    if r.v.ayar("ad_soyad"):
        alt.insert(0, esc(r.v.ayar("ad_soyad")))
    r.ogeler.append(Spacer(1, 10))
    r.ogeler.append(Paragraph(" · ".join(alt), r.st["not"]))
    doc = SimpleDocTemplate(yol, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm, topMargin=12 * mm, bottomMargin=12 * mm,
                            title=os.path.splitext(os.path.basename(yol))[0])
    doc.build(r.ogeler)


def rapor_yillik_kira(v, yil, yol):
    yil = str(yil)
    veri = v.yillik_kira(yil)
    r = Rapor(v, f"{yil} Yılı Kira Geliri", "Daire daire, ay ay kira tutarları (artışlar dahil)")
    aylar = [f"{yil}-{a:02d}" for a in range(1, 13)]
    satirlar, ay_top = [], [0.0] * 12
    genel = gelecek_top = 0.0
    for b in v.binalar():
        for d in v.bina_daireleri(b["id"], pasif=True):
            aylik = veri.get(d["id"], {})
            if not aylik:
                continue
            hucreler, toplam = [], 0.0
            for i, m in enumerate(aylar):
                if m in aylik:
                    t, _k, gelecek = aylik[m]
                    toplam += t
                    ay_top[i] += t
                    if gelecek:
                        gelecek_top += t
                    hucreler.append(f"<font color='{GRI}'>{sayi_yaz(t, 0)}</font>" if gelecek else sayi_yaz(t, 0))
                else:
                    hucreler.append("-")
            genel += toplam
            kiracilar = []
            for m in aylar:
                if m in aylik and aylik[m][1]["ad"] not in kiracilar:
                    kiracilar.append(aylik[m][1]["ad"])
            satirlar.append([f"{esc(b['ad'])}<br/>Daire {esc(d['no'])}", esc(", ".join(kiracilar))] + hucreler + [f"<b>{sayi_yaz(toplam, 0)}</b>"])
    gerceklesen = genel - gelecek_top
    ozet = (f"<b>Kısaca:</b> {yil} yılında toplam kira geliri <b>{para(genel)}</b>"
            + (f" (bugüne kadar gerçekleşen <b>{para(gerceklesen)}</b>, yıl sonuna kadar beklenen {para(gelecek_top)})" if gelecek_top else "") + ".")
    if v.takip:
        tahsil = sum(o["tutar"] for o in v.d["odemeler"] if o["tarih"][:4] == yil)
        ozet += f" Yıl içinde kiracılardan alınan ödemeler toplamı <b>{para(tahsil)}</b>."
    r.kutu(ozet)
    r.genislik = 273 * mm
    gen = [0.10, 0.11] + [0.058] * 12 + [0.094]
    r.tablo(["Daire", "Kiracı"] + [a[:3] for a in AYLAR] + ["Toplam"], satirlar, ["", ""] + ["r"] * 13, gen,
            ["Toplam", ""] + [sayi_yaz(x, 0) for x in ay_top] + [sayi_yaz(genel, 0)])
    r.p("Tutarlar TL'dir. Gri yazılan aylar henüz gelmemiş aylardır; güncel kira üzerinden tahmin edilmiştir (ileride yapılacak artışlar dahil değildir).", "not")
    r.p("Kira geliri beyannamesi her yıl mart ayında verilir; bu tablo beyan için yardımcıdır, kesin beyan için muhasebecinize danışın.", "not")
    _yatay_kaydet(r, yol)


def rapor_kiraci_karti(v, kiraci_id, yol):
    k = v.bul("kiracilar", kiraci_id)
    d = v.bul("daireler", k["daire_id"])
    r = Rapor(v, f"Kiracı Kartı – {k['ad']}", v.daire_adi(d) + ("" if not k.get("cikis") else f" (çıkış: {tarih_yaz(k['cikis'])})"))
    r.h2("Kişisel bilgiler")
    r.tablo(["", ""], [["Ad soyad", esc(k["ad"])], ["TC kimlik no", esc(k.get("tc", ""))], ["Telefon", esc(k.get("tel", ""))],
                       ["E-posta", esc(k.get("eposta", ""))],
                       ["Acil durumda aranacak", esc(" · ".join(x for x in (k.get("acil_ad", ""), k.get("acil_yakinlik", ""), k.get("acil_tel", "")) if x))]],
            ["", ""], [0.35, 0.65])
    r.h2("Kira ve sözleşme")
    r.tablo(["", ""], [["Taşınma tarihi", tarih_yaz(k.get("giris", ""))], ["Sözleşme başlangıcı", tarih_yaz(k.get("sozlesme_bas", ""))],
                       ["Sözleşme bitişi", tarih_yaz(k.get("sozlesme_bitis", ""))], ["İlk kira (taşındığında)", para(k.get("ilk_kira") or 0)],
                       ["Güncel aylık kira", f"<b>{para(v.guncel_kira(k))}</b>"], ["Kira ödeme günü", f"Her ayın {k.get('odeme_gunu') or 1}. günü"],
                       ["Depozito", para(k.get("depozito") or 0) + (f" (iade: {para(k.get('depozito_iade') or 0)}, {tarih_yaz(k.get('depozito_iade_tarih', ''))})" if k.get("cikis") else "")],
                       ["Çıkış tarihi", tarih_yaz(k.get("cikis", "")) or "-"]],
            ["", ""], [0.35, 0.65])
    gecmis = v.kira_gecmisi(k["id"])
    if gecmis:
        r.h2("Kira artışları")
        r.tablo(["Geçerlilik", "Eski kira", "Yeni kira", "Oran", "Açıklama"],
                [[tarih_yaz(a["tarih"]), para(a["eski_kira"]), para(a["yeni_kira"]), f"%{sayi_yaz(a.get('oran') or 0)}", esc(a.get("aciklama", ""))] for a in gecmis],
                ["", "r", "r", "r", ""], [0.15, 0.17, 0.17, 0.11, 0.4])
    if v.takip:
        h = v.hesap(k["id"])
        r.h2("Kira ödeme durumu")
        r.p(("Borç: " + k_(para(-h["bakiye"])) + " (" + esc(", ".join(b["baslik"] for b in h["acik"])) + ")") if h["bakiye"] < -0.004
            else (y_(f"Fazla ödeme +{para(h['bakiye'])}") if h["bakiye"] > 0.004 else y_("Kira borcu yok ✓")))
    belgeler = k.get("belgeler", [])
    r.h2("Belgeler")
    if belgeler:
        r.tablo(["Tür", "Dosya", "Eklenme"], [[esc(b["tur"]), esc(b["ad"]), tarih_yaz(b.get("tarih", ""))] for b in belgeler], ["", "", ""], [0.25, 0.55, 0.2])
    else:
        r.p("Kayıtlı belge yok.", "not")
    if k.get("esya_notu") or k.get("not"):
        r.h2("Notlar")
        if k.get("esya_notu"):
            r.p("<b>Eşya / teslim notu:</b> " + esc(k["esya_notu"]).replace("\n", "<br/>"))
        if k.get("not"):
            r.p(esc(k["not"]).replace("\n", "<br/>"))
    r.h2("Daire ve ev sahibi")
    r.tablo(["", ""], [["Daire", esc(v.daire_adi(d))], ["Ev sahibi", esc(d.get("sahip_ad", ""))], ["Ev sahibi telefonu", esc(d.get("sahip_tel", ""))]],
            ["", ""], [0.35, 0.65])
    r.kaydet(yol)


def rapor_kiraci_listesi(v, yol):
    r = Rapor(v, "Kiracı Listesi", f"{tarih_yaz(bugun())} itibarıyla")
    satirlar, toplam = [], 0.0
    for b in v.binalar():
        for d in v.bina_daireleri(b["id"]):
            k = v.aktif_kiraci(d["id"])
            if k:
                kira = v.guncel_kira(k)
                toplam += kira
                durum = ""
                if v.takip:
                    h = v.hesap(k["id"])
                    durum = k_(f"Borç {para(-h['bakiye'])}") if h["bakiye"] < -0.004 else y_("Ödendi ✓")
                satirlar.append([f"{esc(b['ad'])} – {esc(d['no'])}", esc(k["ad"]), esc(k.get("tel", "")), tarih_yaz(k.get("giris", "")),
                                 tarih_yaz(k.get("sozlesme_bitis", "")), para(kira), durum])
            else:
                satirlar.append([f"{esc(b['ad'])} – {esc(d['no'])}", f"<font color='{GRI}'>Boş</font>", "", "", "", "", ""])
    r.kutu(f"Toplam {len(satirlar)} daire, {sum(1 for s in satirlar if s[2] or s[5])} dolu. Aylık toplam kira <b>{para(toplam)}</b>, yıllık yaklaşık <b>{para(toplam * 12)}</b>.")
    r.tablo(["Daire", "Kiracı", "Telefon", "Taşınma", "Sözleşme bitişi", "Kira", "Durum"], satirlar,
            ["", "", "", "", "", "r", "r"], [0.18, 0.18, 0.14, 0.11, 0.12, 0.13, 0.14])
    r.kaydet(yol)


def guvenli_ad(s):
    return "".join(ch if ch.isalnum() or ch in " -_." else "_" for ch in s).strip()


# ================================================================ arayüz yardımcıları

def windows_simge_ayarla():
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass


def simge_uygula(p):
    try:
        p.iconbitmap(default=kaynak_yolu("icon.ico"))
    except Exception:
        pass
    try:
        if not hasattr(p, "_simge"):
            p._simge = tk.PhotoImage(master=p, file=kaynak_yolu("icon.png"))
        p.iconphoto(True, p._simge)
    except Exception:
        pass


class Form(tk.Toplevel):
    """Basit form penceresi."""

    def __init__(self, ana, baslik, genislik=520):
        super().__init__(ana)
        self.ana = ana
        self.title(baslik)
        if ana.winfo_viewable():
            self.transient(ana)  # ana pencere gizliyken (giriş / kurulum) bağlanırsa Windows formu göstermez
        self.resizable(True, True)
        simge_uygula(self)
        self.govde = ttk.Frame(self, padding=16)
        self.govde.pack(fill="both", expand=True)
        self.govde.columnconfigure(1, weight=1)
        self.satir = 0
        self.minsize(genislik, 100)
        self.bind("<Escape>", lambda _e: self.destroy())

    def etiket(self, metin, stil="Baslik.TLabel"):
        ttk.Label(self.govde, text=metin, style=stil).grid(row=self.satir, column=0, columnspan=3, sticky="w", pady=(4, 6))
        self.satir += 1

    def giris(self, etiket, deger="", sag=False, show=None, genislik=28):
        v = tk.StringVar(value=deger)
        ttk.Label(self.govde, text=etiket).grid(row=self.satir, column=0, sticky="w", pady=4, padx=(0, 10))
        e = ttk.Entry(self.govde, textvariable=v, width=genislik, font=(self.ana.fa, 11), justify="right" if sag else "left", show=show)
        e.grid(row=self.satir, column=1, columnspan=2, sticky="we", pady=4)
        self.satir += 1
        v.entry = e
        return v

    def secim(self, etiket, degerler, deger="", serbest=False, genislik=26):
        v = tk.StringVar(value=deger)
        ttk.Label(self.govde, text=etiket).grid(row=self.satir, column=0, sticky="w", pady=4, padx=(0, 10))
        c = ttk.Combobox(self.govde, textvariable=v, values=degerler, state="normal" if serbest else "readonly", width=genislik, font=(self.ana.fa, 11))
        c.grid(row=self.satir, column=1, columnspan=2, sticky="we", pady=4)
        self.satir += 1
        v.combo = c
        return v

    def radyo(self, etiket, secenekler, deger):
        v = tk.StringVar(value=deger)
        ttk.Label(self.govde, text=etiket).grid(row=self.satir, column=0, sticky="w", pady=4, padx=(0, 10))
        f = ttk.Frame(self.govde)
        f.grid(row=self.satir, column=1, columnspan=2, sticky="w", pady=4)
        for s in secenekler:
            ttk.Radiobutton(f, text=s, value=s, variable=v).pack(side="left", padx=(0, 12))
        self.satir += 1
        return v

    def onay(self, metin, deger=True):
        v = tk.BooleanVar(value=deger)
        ttk.Checkbutton(self.govde, text=metin, variable=v).grid(row=self.satir, column=0, columnspan=3, sticky="w", pady=4)
        self.satir += 1
        return v

    def metin(self, etiket, deger="", yukseklik=4):
        ttk.Label(self.govde, text=etiket).grid(row=self.satir, column=0, sticky="nw", pady=4, padx=(0, 10))
        t = tk.Text(self.govde, height=yukseklik, width=40, font=(self.ana.fa, 11), wrap="word", relief="solid", borderwidth=1)
        t.insert("1.0", deger)
        t.grid(row=self.satir, column=1, columnspan=2, sticky="we", pady=4)
        self.satir += 1
        return t

    def not_(self, metin):
        l = ttk.Label(self.govde, text=metin, style="Not.TLabel", justify="left", wraplength=460)
        l.grid(row=self.satir, column=0, columnspan=3, sticky="w", pady=(0, 6))
        self.satir += 1
        return l

    def dugmeler(self, *dugmeler):
        f = ttk.Frame(self.govde)
        f.grid(row=self.satir, column=0, columnspan=3, sticky="we", pady=(12, 0))
        for metin, komut, renk in dugmeler:
            if renk:
                self.ana.renkli(f, metin, renk, komut).pack(side="left", padx=(0, 8))
            else:
                ttk.Button(f, text=metin, command=komut).pack(side="left", padx=(0, 8))
        self.satir += 1
        return f

    def ac(self):
        self.update_idletasks()
        if self.ana.winfo_viewable():
            x = self.ana.winfo_rootx() + max(0, (self.ana.winfo_width() - self.winfo_width()) // 2)
            y = self.ana.winfo_rooty() + 40
        else:
            x = max(0, (self.winfo_screenwidth() - self.winfo_width()) // 2)
            y = max(0, (self.winfo_screenheight() - self.winfo_height()) // 3)
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(300, lambda: self.winfo_exists() and self.attributes("-topmost", False))
        try:
            self.grab_set()
        except tk.TclError:
            pass
        self.focus_force()


def sayi_al(v, etiket, bos_olabilir=False, pozitif=True, ebeveyn=None):
    s = v.get().strip()
    if not s and bos_olabilir:
        return None
    n = sayi_oku(s)
    if n is None or (pozitif and n < 0):
        messagebox.showwarning("Hatalı giriş", f"{etiket} için geçerli bir sayı yazın.", parent=ebeveyn)
        raise ValueError
    return n



# ================================================================ ana pencere

BELGE_TURLERI_KIRACI = ["Kimlik fotoğrafı", "Kimlik fotokopisi", "Kira sözleşmesi", "Kefil belgesi", "Diğer"]
BELGE_TURLERI_DAIRE = ["Tapu", "DASK poliçesi", "Diğer"]


class Uygulama(tk.Tk):
    def __init__(self, veri=None):
        windows_simge_ayarla()
        super().__init__()
        self.withdraw()
        self.title(f"{UYGULAMA_ADI}  (v{SURUM})")
        simge_uygula(self)
        self._stil()
        self.yerel = yerel_ayar_oku()
        self.v = veri or self._veri_ac()
        if not self.v.kurulu:
            if not self._kurulum():
                self.destroy()
                return
        elif not self._giris():
            self.destroy()
            return
        self.geometry("1220x800")
        self.minsize(1080, 700)
        self._arayuz()
        self.deiconify()
        self.after(200, self.otomatik)
        self.after(5000, self._senkron)
        self.protocol("WM_DELETE_WINDOW", self._kapat)

    # ------------------------------------------------------------ açılış
    def _veri_ac(self):
        k = self.yerel.get("klasor")
        while k and not os.path.isdir(k):
            if not messagebox.askretrycancel(
                    "Veri klasörü", f"Ortak veri klasörüne ulaşılamıyor:\n{k}\n\nGoogle Drive açık mı? Açtıktan sonra “Yeniden dene”ye basın.\n\n"
                    "“İptal” derseniz bu seferlik bu bilgisayardaki yerel veriler kullanılır."):
                k = None
        return Veri(k)

    def _giris(self):
        f = Form(self, UYGULAMA_ADI, 380)
        f.etiket("🏠 Kira Takip")
        sifre = f.giris("Şifre", show="•", genislik=22)
        v_hata = tk.StringVar()
        ttk.Label(f.govde, textvariable=v_hata, foreground=KIRMIZI).grid(row=f.satir, column=0, columnspan=3, sticky="w")
        f.satir += 1
        sonuc = {"tamam": False, "deneme": 0}

        def dene(_e=None):
            if self.v.sifre_dogru(sifre.get()):
                sonuc["tamam"] = True
                f.destroy()
                return
            sonuc["deneme"] += 1
            sifre.set("")
            v_hata.set("Şifre yanlış.")
            if sonuc["deneme"] >= 5:
                f.destroy()

        f.dugmeler(("Giriş", dene, MAVI), ("Çıkış", f.destroy, None))
        sifre.entry.bind("<Return>", dene)
        f.ac()
        sifre.entry.focus_set()
        self.wait_window(f)
        return sonuc["tamam"]

    def _kurulum(self):
        f = Form(self, f"{UYGULAMA_ADI} – İlk kurulum", 520)
        f.etiket("🏠 Kira Takip – ilk kurulum")
        f.not_("Kiracı bilgileri, kimlik ve sözleşmeler bu programda saklanacağı için program şifreyle korunur. Bilgileri sonradan Ayarlar'dan değiştirebilirsiniz.")
        ad = f.giris("Adınız soyadınız (mesajlarda görünür)")
        iban = f.giris("Kira için IBAN (isteğe bağlı)")
        iban_ad = f.giris("IBAN hesap sahibi")
        s1 = f.giris("Program şifresi (en az 4 karakter)", show="•")
        s2 = f.giris("Şifre (tekrar)", show="•")
        sonuc = {"tamam": False}

        def kaydet():
            if len(s1.get()) < 4 or s1.get() != s2.get():
                return messagebox.showwarning("Şifre", "Şifreler aynı değil ya da çok kısa (en az 4 karakter).", parent=f)
            self.v.d["ayarlar"] = {"ad_soyad": ad.get().strip(), "iban": iban.get().strip(), "iban_ad": iban_ad.get().strip(),
                                   "kira_takibi": True, "uyari_sozlesme_gun": 60, "uyari_artis_gun": 30}
            self.v.d["ayarlar_z"] = time.time()
            self.v.sifre_yaz(s1.get())
            sonuc["tamam"] = True
            f.destroy()

        f.dugmeler(("Kurulumu tamamla", kaydet, MAVI))
        f.ac()
        self.wait_window(f)
        return sonuc["tamam"]

    def otomatik(self):
        yazilan = self.v.kiralari_yaz()
        if yazilan:
            self.durum(", ".join(donem_adi(m) for m in yazilan) + " kiraları yazıldı.")
        self.ciz()

    def _senkron(self):
        try:
            if self.v.yenile():
                self.v.kiralari_yaz()
                self.ciz()
        except Exception:
            pass
        self.after(5000, self._senkron)

    def _kapat(self):
        yerel_ayar_yaz(self.yerel)
        self.destroy()

    # ------------------------------------------------------------ görünüm
    def _stil(self):
        fa = "Segoe UI" if sys.platform.startswith("win") else "DejaVu Sans"
        self.fa = fa
        for ad in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            try:
                tkfont.nametofont(ad).configure(family=fa, size=10)
            except tk.TclError:
                pass
        s = ttk.Style(self)
        for tema in ("vista", "clam"):
            if tema in s.theme_names():
                s.theme_use(tema)
                break
        s.configure("TNotebook.Tab", font=(fa, 11, "bold"), padding=(14, 7))
        s.configure("Ic.TNotebook.Tab", font=(fa, 10), padding=(10, 4))
        s.configure("Baslik.TLabel", font=(fa, 14, "bold"), foreground=MAVI)
        s.configure("Not.TLabel", font=(fa, 9), foreground=GRI)
        s.configure("Sonuc.TLabel", font=(fa, 11, "bold"))
        s.configure("Buyuk.TLabel", font=(fa, 20, "bold"))
        s.configure("BuyukK.TLabel", font=(fa, 15, "bold"), foreground=KIRMIZI)
        s.configure("BuyukY.TLabel", font=(fa, 15, "bold"), foreground=YESIL)
        s.configure("BuyukG.TLabel", font=(fa, 15, "bold"), foreground=GRI)
        s.configure("Uyari.TLabel", foreground=TURUNCU, font=(fa, 10, "bold"))
        s.configure("TLabelframe.Label", font=(fa, 11, "bold"), foreground=MAVI)
        s.configure("TButton", font=(fa, 10), padding=(8, 4))
        s.configure("Treeview", rowheight=26, font=(fa, 10))
        s.configure("Treeview.Heading", font=(fa, 10, "bold"))

    def renkli(self, ust, metin, renk, komut):
        koyu = {MAVI: "#174a94", YESIL: "#166b2e", KIRMIZI: "#a61e1e"}.get(renk, renk)
        return tk.Button(ust, text=metin, bg=renk, fg="white", activebackground=koyu, activeforeground="white", relief="flat",
                         font=(self.fa, 10, "bold"), padx=12, pady=5, cursor="hand2", command=komut)

    def tablo(self, ust, sutunlar, yukseklik=8, agac=False):
        cer = ttk.Frame(ust)
        t = ttk.Treeview(cer, columns=[s[0] for s in sutunlar], show="tree headings" if agac else "headings", height=yukseklik, selectmode="browse")
        for a, b, g, h in sutunlar:
            t.heading(a, text=b)
            t.column(a, width=g, anchor=h, stretch=True)
        kay = ttk.Scrollbar(cer, orient="vertical", command=t.yview)
        t.configure(yscrollcommand=kay.set)
        t.pack(side="left", fill="both", expand=True)
        kay.pack(side="right", fill="y")
        for e, r in (("borc", KIRMIZI), ("alacak", YESIL), ("soluk", GRI), ("uyari", TURUNCU)):
            t.tag_configure(e, foreground=r)
        t.tag_configure("bina", font=(self.fa, 10, "bold"))
        return cer, t

    @staticmethod
    def _sec(t):
        s = t.selection()
        return s[0] if s else None

    def durum(self, mesaj):
        self.v_durum.set(mesaj)

    def _arayuz(self):
        ust = tk.Frame(self, bg=YESIL)
        ust.pack(fill="x")
        tk.Label(ust, text="🏠 Kira Takip", bg=YESIL, fg="white", font=(self.fa, 15, "bold"), padx=16, pady=10).pack(side="left")
        tk.Button(ust, text="↻ Yenile", command=self.yenile, bg="#2ea152", fg="white", relief="flat", font=(self.fa, 10), padx=10,
                  activebackground="#166b2e", activeforeground="white").pack(side="right", padx=12, pady=8)
        self.defter = ttk.Notebook(self)
        self.defter.pack(fill="both", expand=True, padx=10, pady=(8, 0))
        self.sayfalar = {}
        for anahtar, ad in (("ozet", "  🏠 Özet  "), ("binalar", "  🏢 Binalar ve Daireler  "), ("kiracilar", "  👤 Kiracılar  "),
                            ("raporlar", "  📄 Raporlar  "), ("ayarlar", "  ⚙ Ayarlar  ")):
            f = ttk.Frame(self.defter, padding=12)
            self.defter.add(f, text=ad)
            self.sayfalar[anahtar] = f
        self.v_durum = tk.StringVar()
        ttk.Label(self, textvariable=self.v_durum, foreground=YESIL, padding=(14, 4)).pack(fill="x")
        self._ozet_kur()
        self._binalar_kur()
        self._kiracilar_kur()
        self._raporlar_kur()
        self._ayarlar_kur()
        self.defter.bind("<<NotebookTabChanged>>", lambda _e: self.ciz(), add="+")

    def yenile(self):
        self.v.yenile()
        self.otomatik()
        self.durum("Güncellendi.")

    def ciz(self):
        if not hasattr(self, "defter"):
            return
        self.ozet_ciz()
        self.binalar_ciz()
        self.kiracilar_ciz()
        self.raporlar_ciz()
        self.ayarlari_doldur()

    # ------------------------------------------------------------ özet
    def _ozet_kur(self):
        p = self.sayfalar["ozet"]
        p.columnconfigure(0, weight=1)
        p.rowconfigure(2, weight=1)
        kartlar = ttk.Frame(p)
        kartlar.grid(row=0, column=0, sticky="we")
        self.ozet_v = {}
        for i, (a, b) in enumerate((("daire", "Daireler"), ("kira", "Aylık toplam kira"), ("yil", f"{bu_donem()[:4]} kira geliri"), ("borc", "Ödenmemiş kira"))):
            kartlar.columnconfigure(i, weight=1)
            f = ttk.LabelFrame(kartlar, text=f" {b} ", padding=10)
            f.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 0))
            v1, v2 = tk.StringVar(), tk.StringVar()
            l = ttk.Label(f, textvariable=v1, style="Buyuk.TLabel")
            l.pack(anchor="w")
            ttk.Label(f, textvariable=v2, style="Not.TLabel").pack(anchor="w")
            self.ozet_v[a] = (v1, v2, l)
        dug = ttk.Frame(p)
        dug.grid(row=1, column=0, sticky="w", pady=10)
        self.renkli(dug, "🏢 Bina ekle", MAVI, lambda: self.bina_formu()).pack(side="left")
        self.renkli(dug, "👤 Kiracı yerleştir", YESIL, lambda: self.kiraci_formu()).pack(side="left", padx=8)
        self.b_odeme = self.renkli(dug, "💰 Kira ödemesi al", MAVI, lambda: self.odeme_formu())
        self.b_odeme.pack(side="left")
        u = ttk.LabelFrame(p, text=" Hatırlatmalar (çift tıklayınca ilgili kayıt açılır) ", padding=8)
        u.grid(row=2, column=0, sticky="nsew")
        u.columnconfigure(0, weight=1)
        u.rowconfigure(0, weight=1)
        cer, self.t_uyari = self.tablo(u, (("tur", "Ne", 170, "w"), ("yer", "Daire", 200, "w"), ("kisi", "Kiracı / sahip", 160, "w"),
                                           ("aciklama", "Açıklama", 420, "w"), ("tarih", "Tarih", 90, "w")), yukseklik=14)
        cer.grid(row=0, column=0, sticky="nsew")
        self.t_uyari.bind("<Double-1>", lambda _e: self._uyariya_git())
        self._uyari_nesne = {}

    def ozet_ciz(self):
        v = self.v
        daireler = [d for d in v.d["daireler"] if d.get("aktif", True)]
        dolu = [d for d in daireler if v.aktif_kiraci(d["id"])]
        self.ozet_v["daire"][0].set(f"{len(dolu)} / {len(daireler)} dolu")
        self.ozet_v["daire"][1].set(f"{len(v.d['binalar'])} bina · {len(daireler) - len(dolu)} boş daire")
        aylik = sum(v.guncel_kira(v.aktif_kiraci(d["id"])) for d in dolu)
        self.ozet_v["kira"][0].set(para_kisa(aylik))
        self.ozet_v["kira"][1].set(f"Yıllık yaklaşık {para_kisa(aylik * 12)}")
        yk = v.yillik_kira(bu_donem()[:4])
        toplam = sum(t for d in yk.values() for t, _k, _g in d.values())
        gelecek = sum(t for d in yk.values() for t, _k, g in d.values() if g)
        self.ozet_v["yil"][0].set(para_kisa(toplam))
        self.ozet_v["yil"][1].set(f"Bugüne kadar {para_kisa(toplam - gelecek)} · yıl sonuna kadar {para_kisa(gelecek)}")
        if v.takip:
            borc = sum(-v.hesap(k["id"])["bakiye"] for k in v.d["kiracilar"] if v.hesap(k["id"])["bakiye"] < 0)
            geciken = sum(1 for k in v.d["kiracilar"] if not k.get("cikis") and v.hesap(k["id"])["geciken"])
            self.ozet_v["borc"][0].set(para_kisa(borc))
            self.ozet_v["borc"][2].configure(style="BuyukK.TLabel" if borc > 0.004 else "BuyukY.TLabel")
            self.ozet_v["borc"][1].set(f"{geciken} kiracının ödemesi gecikmiş")
            self.b_odeme.pack(side="left")
        else:
            self.ozet_v["borc"][0].set("—")
            self.ozet_v["borc"][1].set("Kira ödeme takibi kapalı (Ayarlar)")
            self.b_odeme.pack_forget()
        self.t_uyari.delete(*self.t_uyari.get_children())
        self._uyari_nesne = {}
        for n, (onem, tur, nt, nid, yer, kisi, aciklama, tarih) in enumerate(v.uyarilar()):
            iid = f"u{n}"
            self._uyari_nesne[iid] = (nt, nid)
            self.t_uyari.insert("", "end", iid=iid, tags=("borc" if onem == 1 else "uyari",), values=(tur, yer, kisi, aciklama, tarih_yaz(tarih)))
        if not v.d["binalar"]:
            self.t_uyari.insert("", "end", values=("Başlarken", "", "", "Önce “Bina ekle” ile binanızı, sonra dairelerini ekleyin.", ""))
        elif not self.t_uyari.get_children():
            self.t_uyari.insert("", "end", tags=("alacak",), values=("Her şey yolunda", "", "", "Yaklaşan sözleşme bitişi, kira artışı ya da gecikme yok.", ""))

    def _uyariya_git(self):
        s = self._sec(self.t_uyari)
        if s in self._uyari_nesne:
            nt, nid = self._uyari_nesne[s]
            self.git(nt, nid)

    def git(self, nesne_turu, nid):
        if nesne_turu == "kiraci":
            k = self.v.bul("kiracilar", nid)
            if k and k.get("cikis"):
                self.v_kfiltre.set("Tümü")
            self.defter.select(self.sayfalar["kiracilar"])
            self.kiracilar_ciz()
            if self.t_kiraci.exists(nid):
                self.t_kiraci.selection_set(nid)
                self.t_kiraci.see(nid)
        else:
            self.defter.select(self.sayfalar["binalar"])
            self.binalar_ciz()
            if self.t_bina.exists("d-" + nid):
                self.t_bina.selection_set("d-" + nid)
                self.t_bina.see("d-" + nid)

    # ------------------------------------------------------------ binalar ve daireler
    def _binalar_kur(self):
        p = self.sayfalar["binalar"]
        p.columnconfigure(0, weight=2)
        p.columnconfigure(1, weight=3)
        p.rowconfigure(0, weight=1)
        sol = ttk.Frame(p)
        sol.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        sol.rowconfigure(0, weight=1)
        sol.columnconfigure(0, weight=1)
        cer, self.t_bina = self.tablo(sol, (("durum", "Durum", 70, "w"), ("kiraci", "Kiracı", 160, "w"), ("kira", "Kira", 100, "e")),
                                      yukseklik=18, agac=True)
        self.t_bina.heading("#0", text="Bina / daire")
        self.t_bina.column("#0", width=210)
        cer.grid(row=0, column=0, sticky="nsew")
        self.t_bina.bind("<<TreeviewSelect>>", lambda _e: self.bina_detay_ciz())
        d = ttk.Frame(sol)
        d.grid(row=1, column=0, sticky="we", pady=(8, 0))
        self.renkli(d, "🏢 Bina ekle", MAVI, lambda: self.bina_formu()).pack(side="left")
        ttk.Button(d, text="➕ Daire ekle", command=lambda: self.daire_formu(bina_id=self._secili_bina())).pack(side="left", padx=6)
        self.v_bpasif = tk.BooleanVar(value=False)
        ttk.Checkbutton(d, text="Çıkarılan daireler", variable=self.v_bpasif, command=self.binalar_ciz).pack(side="left")

        self.f_bdetay = ttk.Frame(p)
        self.f_bdetay.grid(row=0, column=1, sticky="nsew")
        self.f_bdetay.columnconfigure(0, weight=1)
        self.f_bdetay.rowconfigure(3, weight=1)
        self.v_bd_baslik, self.v_bd_alt = tk.StringVar(), tk.StringVar()
        ttk.Label(self.f_bdetay, textvariable=self.v_bd_baslik, style="Baslik.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(self.f_bdetay, textvariable=self.v_bd_alt, wraplength=640, justify="left").grid(row=1, column=0, sticky="w", pady=(2, 6))
        self.f_bd_dug = ttk.Frame(self.f_bdetay)
        self.f_bd_dug.grid(row=2, column=0, sticky="we", pady=(0, 8))
        self.f_bd_alt = ttk.Frame(self.f_bdetay)
        self.f_bd_alt.grid(row=3, column=0, sticky="nsew")
        self.f_bd_alt.columnconfigure(0, weight=1)
        self.f_bd_alt.rowconfigure(1, weight=1)

    def _secili_bina(self):
        s = self._sec(self.t_bina) if hasattr(self, "t_bina") else None
        if not s:
            return None
        if s.startswith("b-"):
            return s[2:]
        d = self.v.bul("daireler", s[2:])
        return d["bina_id"] if d else None

    def _secili_daire(self):
        s = self._sec(self.t_bina)
        return s[2:] if s and s.startswith("d-") else None

    def binalar_ciz(self):
        v, sec = self.v, self._sec(self.t_bina)
        acik = {i for i in self.t_bina.get_children() if self.t_bina.item(i, "open")}
        self.t_bina.delete(*self.t_bina.get_children())
        for b in v.binalar():
            dl = v.bina_daireleri(b["id"], pasif=self.v_bpasif.get())
            dolu = sum(1 for d in dl if d.get("aktif", True) and v.aktif_kiraci(d["id"]))
            iid = "b-" + b["id"]
            self.t_bina.insert("", "end", iid=iid, text=f"🏢 {b['ad']}", tags=("bina",), open=(iid in acik or not acik),
                               values=(f"{dolu}/{len([d for d in dl if d.get('aktif', True)])} dolu", "", ""))
            for d in dl:
                k = v.aktif_kiraci(d["id"])
                etiket = "soluk" if not d.get("aktif", True) else ""
                if k and v.takip and v.hesap(k["id"])["geciken"]:
                    etiket = "borc"
                self.t_bina.insert(iid, "end", iid="d-" + d["id"], text=f"Daire {d['no']}", tags=(etiket,),
                                   values=("Çıkarıldı" if not d.get("aktif", True) else ("Dolu" if k else "Boş"), k["ad"] if k else "",
                                           para_kisa(v.guncel_kira(k)) if k else ""))
        if sec and self.t_bina.exists(sec):
            self.t_bina.selection_set(sec)
        elif self.t_bina.get_children():
            self.t_bina.selection_set(self.t_bina.get_children()[0])
        self.bina_detay_ciz()

    def bina_detay_ciz(self):
        v = self.v
        for w in self.f_bd_dug.winfo_children() + self.f_bd_alt.winfo_children():
            w.destroy()
        s = self._sec(self.t_bina)
        if not s:
            self.v_bd_baslik.set("Henüz bina yok")
            self.v_bd_alt.set("Soldaki “Bina ekle” düğmesiyle başlayın (örn. Arabacı Apartmanı), sonra dairelerini ekleyin.")
            return
        if s.startswith("b-"):
            b = v.bul("binalar", s[2:])
            self.v_bd_baslik.set(f"🏢 {b['ad']}")
            self.v_bd_alt.set("\n".join(x for x in (b.get("adres", ""), f"Ada / parsel: {b['ada_parsel']}" if b.get("ada_parsel") else "",
                                                     b.get("not", "")) if x))
            ttk.Button(self.f_bd_dug, text="➕ Bu binaya daire ekle", command=lambda: self.daire_formu(bina_id=b["id"])).pack(side="left")
            ttk.Button(self.f_bd_dug, text="✏ Bina bilgisi", command=lambda: self.bina_formu(b["id"])).pack(side="left", padx=6)
            ttk.Button(self.f_bd_dug, text="🗑 Binayı sil", command=lambda: self.bina_sil(b["id"])).pack(side="left")
            ttk.Label(self.f_bd_alt, text="Daireler", style="Sonuc.TLabel").grid(row=0, column=0, sticky="w")
            cer, t = self.tablo(self.f_bd_alt, (("daire", "Daire", 70, "w"), ("sahip", "Ev sahibi", 150, "w"), ("kiraci", "Kiracı", 150, "w"),
                                                ("giris", "Taşınma", 90, "w"), ("bitis", "Sözleşme bitişi", 110, "w"), ("kira", "Kira", 100, "e")), yukseklik=12)
            cer.grid(row=1, column=0, sticky="nsew")
            for d in v.bina_daireleri(b["id"]):
                k = v.aktif_kiraci(d["id"])
                t.insert("", "end", iid=d["id"], values=(f"Daire {d['no']}", d.get("sahip_ad", ""), k["ad"] if k else "Boş",
                                                         tarih_yaz(k.get("giris", "")) if k else "", tarih_yaz(k.get("sozlesme_bitis", "")) if k else "",
                                                         para_kisa(v.guncel_kira(k)) if k else ""))
            t.bind("<Double-1>", lambda _e, t=t: self._sec(t) and self.git("daire", self._sec(t)))
            return
        d = v.bul("daireler", s[2:])
        k = v.aktif_kiraci(d["id"])
        self.v_bd_baslik.set(v.daire_adi(d) + ("" if d.get("aktif", True) else " (çıkarıldı)"))
        bilgi = [x for x in (
            " · ".join(x for x in (f"Kat: {d['kat']}" if d.get("kat") else "", f"{d['m2']} m²" if d.get("m2") else "",
                                   f"{d['oda']}" if d.get("oda") else "") if x),
            f"Ev sahibi: {d.get('sahip_ad', '-')}" + (f"  ☎ {d['sahip_tel']}" if d.get("sahip_tel") else "") + (f"  · TC {d['sahip_tc']}" if d.get("sahip_tc") else ""),
            " · ".join(x for x in (f"Elektrik: {d['elektrik_no']}" if d.get("elektrik_no") else "", f"Su: {d['su_no']}" if d.get("su_no") else "",
                                   f"Doğalgaz: {d['dogalgaz_no']}" if d.get("dogalgaz_no") else "") if x),
            (f"DASK: {d.get('dask_no', '')}  bitiş {tarih_yaz(d['dask_bitis'])}" if d.get("dask_bitis") else ""),
            (f"Eşya notu: {d['esya_notu']}" if d.get("esya_notu") else ""), d.get("not", "")) if x]
        bilgi.append(f"Şu anki kiracı: {k['ad']} · {para(v.guncel_kira(k))} / ay" if k else "Daire şu an boş.")
        self.v_bd_alt.set("\n".join(bilgi))
        if d.get("aktif", True):
            if k:
                self.renkli(self.f_bd_dug, "👤 Kiracıya git", YESIL, lambda: self.git("kiraci", k["id"])).pack(side="left")
            else:
                self.renkli(self.f_bd_dug, "👤 Kiracı yerleştir", YESIL, lambda: self.kiraci_formu(daire_id=d["id"])).pack(side="left")
        ttk.Button(self.f_bd_dug, text="✏ Daire ve ev sahibi bilgisi", command=lambda: self.daire_formu(d["id"])).pack(side="left", padx=6)
        ttk.Button(self.f_bd_dug, text="🗑 Daireyi çıkar" if d.get("aktif", True) else "↩ Geri ekle", command=lambda: self.daire_cikar(d["id"])).pack(side="left")
        ic = ttk.Notebook(self.f_bd_alt, style="Ic.TNotebook")
        ic.grid(row=1, column=0, sticky="nsew")
        f1 = ttk.Frame(ic, padding=6)
        ic.add(f1, text=" Tapu ve belgeler ")
        self._belge_paneli(f1, "daireler", d["id"], BELGE_TURLERI_DAIRE)
        f2 = ttk.Frame(ic, padding=6)
        ic.add(f2, text=" Kiracı geçmişi ")
        f2.columnconfigure(0, weight=1)
        f2.rowconfigure(0, weight=1)
        cer, t = self.tablo(f2, (("ad", "Kiracı", 170, "w"), ("giris", "Taşınma", 90, "w"), ("cikis", "Çıkış", 90, "w"), ("ilk", "İlk kira", 100, "e"),
                                 ("son", "Son kira", 100, "e")), yukseklik=8)
        cer.grid(row=0, column=0, sticky="nsew")
        for kk in v.daire_kiracilari(d["id"]):
            t.insert("", "end", iid=kk["id"], values=(kk["ad"], tarih_yaz(kk.get("giris", "")), tarih_yaz(kk.get("cikis", "")) or "oturuyor",
                                                      para_kisa(kk.get("ilk_kira") or 0), para_kisa(v.guncel_kira(kk))))
        t.bind("<Double-1>", lambda _e, t=t: self._sec(t) and self.git("kiraci", self._sec(t)))
        ttk.Label(f2, text="Çift tıklayınca kiracı kartı açılır.", style="Not.TLabel").grid(row=1, column=0, sticky="w")

    def bina_formu(self, bina_id=None):
        v = self.v
        b = v.bul("binalar", bina_id)
        f = Form(self, "Bina bilgisi" if b else "Yeni bina")
        ad = f.giris("Bina adı", b["ad"] if b else "")
        adres = f.giris("Adres", b.get("adres", "") if b else "")
        ada = f.giris("Ada / parsel (isteğe bağlı)", b.get("ada_parsel", "") if b else "")
        if not b:
            sayi = f.giris("Kaç daire eklensin? (sonra da eklenebilir)", "8", sag=True)
        n = f.metin("Not", b.get("not", "") if b else "", 3)

        def kaydet():
            if not ad.get().strip():
                return messagebox.showwarning("Eksik", "Bina adını yazın.", parent=f)
            k = v.yaz("binalar", dict(b or {}, ad=ad.get().strip(), adres=adres.get().strip(), ada_parsel=ada.get().strip(),
                                      **{"not": n.get("1.0", "end").strip()}), False)
            if not b:
                adet = int(sayi_oku(sayi.get()) or 0)
                for i in range(1, min(adet, 300) + 1):
                    v.yaz("daireler", {"bina_id": k["id"], "no": str(i), "aktif": True, "belgeler": []}, False)
            v.kaydet()
            f.destroy()
            self.ciz()
            self.defter.select(self.sayfalar["binalar"])
            self.t_bina.selection_set("b-" + k["id"])
            self.durum("Bina kaydedildi.")

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def bina_sil(self, bina_id):
        v = self.v
        b = v.bul("binalar", bina_id)
        dl = v.bina_daireleri(bina_id, pasif=True)
        if any(v.daire_kiracilari(d["id"]) for d in dl):
            return messagebox.showwarning("Bina", "Bu binada kiracı kaydı olan daireler var; bina silinemez.\n"
                                          "Kayıtların korunması için daireleri tek tek “çıkar”abilirsiniz.", parent=self)
        if messagebox.askyesno("Bina sil", f"“{b['ad']}” ve {len(dl)} dairesi silinsin mi?", parent=self):
            for d in dl:
                v.sil("daireler", d["id"], False)
            v.sil("binalar", bina_id)
            self.ciz()

    def daire_formu(self, daire_id=None, bina_id=None):
        v = self.v
        d = v.bul("daireler", daire_id)
        if not d and not v.d["binalar"]:
            return messagebox.showinfo("Daire", "Önce bir bina ekleyin.", parent=self)
        binalar = v.binalar()
        bina_id = d["bina_id"] if d else (bina_id or binalar[0]["id"])
        f = Form(self, f"{v.daire_adi(d)} bilgisi" if d else "Yeni daire", 560)
        bina = f.secim("Bina", [b["ad"] for b in binalar], v.bul("binalar", bina_id)["ad"])
        mevcut = [x["no"] for x in v.bina_daireleri(bina_id, pasif=True)]
        yeni_no = str(int(max([sayi_oku(x) or 0 for x in mevcut] + [0])) + 1)
        no = f.giris("Daire numarası", d["no"] if d else yeni_no)
        kat = f.giris("Kat", d.get("kat", "") if d else "")
        m2 = f.giris("Net m² (isteğe bağlı)", d.get("m2", "") if d else "")
        oda = f.giris("Oda sayısı (örn. 3+1)", d.get("oda", "") if d else "")
        f.etiket("Ev sahibi (tapu sahibi)", "Sonuc.TLabel")
        sahip = f.giris("Ad soyad", d.get("sahip_ad", "") if d else "")
        sahip_tc = f.giris("TC kimlik no", d.get("sahip_tc", "") if d else "")
        sahip_tel = f.giris("Telefon", d.get("sahip_tel", "") if d else "")
        f.etiket("Abonelikler ve DASK", "Sonuc.TLabel")
        el = f.giris("Elektrik tesisat no", d.get("elektrik_no", "") if d else "")
        su = f.giris("Su abone no", d.get("su_no", "") if d else "")
        dg = f.giris("Doğalgaz tesisat no", d.get("dogalgaz_no", "") if d else "")
        dask = f.giris("DASK poliçe no", d.get("dask_no", "") if d else "")
        dask_b = f.giris("DASK bitiş tarihi (gg.aa.yyyy)", tarih_yaz(d.get("dask_bitis", "")) if d else "")
        esya = f.metin("Dairedeki eşyalar / not", d.get("esya_notu", "") if d else "", 2)
        n = f.metin("Diğer not", d.get("not", "") if d else "", 2)
        f.not_("Tapu ve DASK poliçesi gibi belgeleri kaydettikten sonra dairenin “Tapu ve belgeler” bölümünden ekleyebilirsiniz.")

        def kaydet():
            if not no.get().strip():
                return messagebox.showwarning("Eksik", "Daire numarasını yazın.", parent=f)
            db = tarih_oku(dask_b.get()) if dask_b.get().strip() else ""
            if db is None:
                return messagebox.showwarning("Tarih", "DASK bitiş tarihini gg.aa.yyyy şeklinde yazın.", parent=f)
            if sahip_tc.get().strip() and not tc_gecerli(sahip_tc.get().strip()) and not messagebox.askyesno(
                    "TC kimlik no", "Ev sahibinin TC kimlik numarası geçerli görünmüyor. Yine de kaydedilsin mi?", parent=f):
                return
            b = binalar[[x["ad"] for x in binalar].index(bina.get())]
            k = v.yaz("daireler", dict(d or {"aktif": True, "belgeler": []}, bina_id=b["id"], no=no.get().strip(), kat=kat.get().strip(),
                                       m2=m2.get().strip(), oda=oda.get().strip(), sahip_ad=sahip.get().strip(), sahip_tc=sahip_tc.get().strip(),
                                       sahip_tel=sahip_tel.get().strip(), elektrik_no=el.get().strip(), su_no=su.get().strip(), dogalgaz_no=dg.get().strip(),
                                       dask_no=dask.get().strip(), dask_bitis=db, esya_notu=esya.get("1.0", "end").strip(),
                                       **{"not": n.get("1.0", "end").strip()}))
            f.destroy()
            self.ciz()
            self.git("daire", k["id"])
            self.durum("Daire kaydedildi.")

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def daire_cikar(self, daire_id):
        v = self.v
        d = v.bul("daireler", daire_id)
        if not d.get("aktif", True):
            v.yaz("daireler", dict(d, aktif=True))
            return self.ciz()
        if v.aktif_kiraci(daire_id):
            return messagebox.showwarning("Daire", "Bu dairede oturan kiracı var. Önce kiracının çıkışını kaydedin.", parent=self)
        if not v.daire_kiracilari(daire_id):
            if messagebox.askyesno("Daire sil", f"{v.daire_adi(d)} tamamen silinsin mi?", parent=self):
                v.sil("daireler", daire_id)
        elif messagebox.askyesno("Daire çıkar", f"{v.daire_adi(d)} listeden çıkarılsın mı?\nEski kiracı kayıtları silinmez.", parent=self):
            v.yaz("daireler", dict(d, aktif=False))
        self.ciz()

    # ------------------------------------------------------------ belgeler
    def _belge_paneli(self, ust, tablo, kimlik, turler):
        ust.columnconfigure(0, weight=1)
        ust.rowconfigure(0, weight=1)
        cer, t = self.tablo(ust, (("tur", "Tür", 140, "w"), ("ad", "Dosya", 260, "w"), ("tarih", "Eklenme", 90, "w")), yukseklik=6)
        cer.grid(row=0, column=0, sticky="nsew")
        kayit = self.v.bul(tablo, kimlik)
        for b in kayit.get("belgeler", []):
            t.insert("", "end", iid=b["id"], values=(b["tur"], b["ad"], tarih_yaz(b.get("tarih", ""))))
        t.bind("<Double-1>", lambda _e: self.belge_ac(tablo, kimlik, self._sec(t)))
        d = ttk.Frame(ust)
        d.grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Button(d, text="📎 Belge ekle…", command=lambda: self.belge_ekle(tablo, kimlik, turler)).pack(side="left")
        ttk.Button(d, text="📂 Aç", command=lambda: self.belge_ac(tablo, kimlik, self._sec(t))).pack(side="left", padx=6)
        ttk.Button(d, text="🗑 Sil", command=lambda: self.belge_sil(tablo, kimlik, self._sec(t))).pack(side="left")
        ttk.Label(ust, text="Fotoğraf, taranmış PDF ya da başka dosya ekleyebilirsiniz. Dosyanın bir kopyası programın veri klasörüne alınır.",
                  style="Not.TLabel").grid(row=2, column=0, sticky="w")

    def belge_ekle(self, tablo, kimlik, turler):
        v = self.v
        f = Form(self, "Belge ekle", 460)
        tur = f.secim("Belge türü", turler, turler[0], serbest=True)
        yol = {"y": None}
        v_dosya = tk.StringVar(value="Dosya seçilmedi")
        ff = ttk.Frame(f.govde)
        ttk.Label(f.govde, text="Dosya").grid(row=f.satir, column=0, sticky="w")
        ff.grid(row=f.satir, column=1, columnspan=2, sticky="w", pady=4)
        f.satir += 1

        def sec():
            y = filedialog.askopenfilename(parent=f, title="Belge seçin",
                                           filetypes=[("Resim / PDF", "*.jpg *.jpeg *.png *.pdf *.heic"), ("Tümü", "*.*")])
            if y:
                yol["y"] = y
                v_dosya.set(os.path.basename(y))

        ttk.Button(ff, text="📎 Dosya seç…", command=sec).pack(side="left")
        ttk.Label(ff, textvariable=v_dosya, style="Not.TLabel").pack(side="left", padx=8)

        def kaydet():
            if not yol["y"]:
                return messagebox.showwarning("Belge", "Dosya seçin.", parent=f)
            kayit = v.bul(tablo, kimlik)
            klasor = os.path.join(v.klasor, "belgeler", kimlik)
            os.makedirs(klasor, exist_ok=True)
            bid = uid()
            ad = f"{guvenli_ad(tur.get())}_{bid}{os.path.splitext(yol['y'])[1].lower()}"
            shutil.copyfile(yol["y"], os.path.join(klasor, ad))
            belgeler = list(kayit.get("belgeler", [])) + [{"id": bid, "tur": tur.get().strip() or "Diğer", "ad": os.path.basename(yol["y"]),
                                                           "dosya": ad, "tarih": bugun()}]
            v.yaz(tablo, dict(kayit, belgeler=belgeler))
            f.destroy()
            self.ciz()
            self.durum("Belge eklendi.")

        f.dugmeler(("Ekle", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def belge_ac(self, tablo, kimlik, belge_id):
        kayit = self.v.bul(tablo, kimlik)
        b = next((x for x in kayit.get("belgeler", []) if x["id"] == belge_id), None)
        if not b:
            return
        yol = os.path.join(self.v.klasor, "belgeler", kimlik, b["dosya"])
        if os.path.exists(yol):
            dosya_ac(yol)
        else:
            messagebox.showwarning("Belge", "Dosya bulunamadı (Google Drive henüz eşitlememiş olabilir).", parent=self)

    def belge_sil(self, tablo, kimlik, belge_id):
        kayit = self.v.bul(tablo, kimlik)
        b = next((x for x in kayit.get("belgeler", []) if x["id"] == belge_id), None)
        if b and messagebox.askyesno("Belge sil", f"“{b['ad']}” silinsin mi?", parent=self):
            self.v.yaz(tablo, dict(kayit, belgeler=[x for x in kayit["belgeler"] if x["id"] != belge_id]))
            try:
                os.remove(os.path.join(self.v.klasor, "belgeler", kimlik, b["dosya"]))
            except OSError:
                pass
            self.ciz()

    # ------------------------------------------------------------ kiracılar
    def _kiracilar_kur(self):
        p = self.sayfalar["kiracilar"]
        p.columnconfigure(0, weight=2)
        p.columnconfigure(1, weight=3)
        p.rowconfigure(1, weight=1)
        ust = ttk.Frame(p)
        ust.grid(row=0, column=0, sticky="we", pady=(0, 6))
        self.v_kfiltre = tk.StringVar(value="Oturanlar")
        for s in ("Oturanlar", "Çıkanlar", "Tümü"):
            ttk.Radiobutton(ust, text=s, value=s, variable=self.v_kfiltre, command=self.kiracilar_ciz).pack(side="left", padx=(0, 10))
        self.v_kara = tk.StringVar()
        e = ttk.Entry(ust, textvariable=self.v_kara, width=18)
        e.pack(side="right")
        ttk.Label(ust, text="Ara:").pack(side="right", padx=4)
        self.v_kara.trace_add("write", lambda *_: self.kiracilar_ciz())
        cer, self.t_kiraci = self.tablo(p, (("ad", "Kiracı", 150, "w"), ("daire", "Daire", 170, "w"), ("kira", "Kira", 90, "e"),
                                            ("bitis", "Sözleşme bitişi", 100, "w")), yukseklik=18)
        cer.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.t_kiraci.bind("<<TreeviewSelect>>", lambda _e: self.kiraci_detay_ciz())
        d = ttk.Frame(p)
        d.grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.renkli(d, "👤 Kiracı yerleştir", YESIL, lambda: self.kiraci_formu()).pack(side="left")

        sag = ttk.Frame(p)
        sag.grid(row=0, column=1, rowspan=3, sticky="nsew")
        sag.columnconfigure(0, weight=1)
        sag.rowconfigure(4, weight=1)
        self.v_k_baslik, self.v_k_alt, self.v_k_durum = tk.StringVar(), tk.StringVar(), tk.StringVar()
        ttk.Label(sag, textvariable=self.v_k_baslik, style="Baslik.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(sag, textvariable=self.v_k_alt).grid(row=1, column=0, sticky="w")
        self.l_k_durum = ttk.Label(sag, textvariable=self.v_k_durum, style="BuyukG.TLabel")
        self.l_k_durum.grid(row=2, column=0, sticky="w", pady=(4, 6))
        self.f_k_dug = ttk.Frame(sag)
        self.f_k_dug.grid(row=3, column=0, sticky="we", pady=(0, 8))
        self.f_k_alt = ttk.Frame(sag)
        self.f_k_alt.grid(row=4, column=0, sticky="nsew")
        self.f_k_alt.columnconfigure(0, weight=1)
        self.f_k_alt.rowconfigure(0, weight=1)
        self._k_sekme = 0

    def kiracilar_ciz(self):
        v, sec = self.v, self._sec(self.t_kiraci)
        filtre, ara = self.v_kfiltre.get(), self.v_kara.get().strip().lower()
        self.t_kiraci.delete(*self.t_kiraci.get_children())
        liste = sorted(v.d["kiracilar"], key=lambda k: (bool(k.get("cikis")), k["ad"].lower()))
        for k in liste:
            if (filtre == "Oturanlar" and k.get("cikis")) or (filtre == "Çıkanlar" and not k.get("cikis")):
                continue
            d = v.bul("daireler", k["daire_id"])
            if ara and ara not in (k["ad"] + " " + k.get("tel", "") + " " + v.daire_adi(d)).lower():
                continue
            etiket = "soluk" if k.get("cikis") else ("borc" if v.takip and v.hesap(k["id"])["geciken"] else "")
            self.t_kiraci.insert("", "end", iid=k["id"], tags=(etiket,), values=(k["ad"], v.daire_adi(d), para_kisa(v.guncel_kira(k)),
                                                                                 tarih_yaz(k.get("sozlesme_bitis", ""))))
        if sec and self.t_kiraci.exists(sec):
            self.t_kiraci.selection_set(sec)
        elif self.t_kiraci.get_children():
            self.t_kiraci.selection_set(self.t_kiraci.get_children()[0])
        self.kiraci_detay_ciz()

    def kiraci_detay_ciz(self):
        v = self.v
        for w in self.f_k_dug.winfo_children() + self.f_k_alt.winfo_children():
            if isinstance(w, ttk.Notebook):
                try:
                    self._k_sekme = w.index(w.select())
                except tk.TclError:
                    pass
            w.destroy()
        k = v.bul("kiracilar", self._sec(self.t_kiraci))
        if not k:
            self.v_k_baslik.set("Kiracı seçilmedi")
            self.v_k_alt.set("“Kiracı yerleştir” ile yeni kiracı ekleyin.")
            self.v_k_durum.set("")
            return
        d = v.bul("daireler", k["daire_id"])
        self.v_k_baslik.set(f"👤 {k['ad']}")
        self.v_k_alt.set(v.daire_adi(d) + (f"   ·   çıkış: {tarih_yaz(k['cikis'])}" if k.get("cikis") else f"   ·   {tarih_yaz(k.get('giris', ''))} tarihinden beri"))
        kira = v.guncel_kira(k)
        if v.takip and not k.get("cikis"):
            h = v.hesap(k["id"])
            if h["bakiye"] < -0.004:
                self.v_k_durum.set(f"Aylık {para_kisa(kira)}  ·  Borç {para(-h['bakiye'])}")
                self.l_k_durum.configure(style="BuyukK.TLabel")
            else:
                self.v_k_durum.set(f"Aylık {para_kisa(kira)}  ·  " + (f"Fazla ödeme +{para(h['bakiye'])}" if h["bakiye"] > 0.004 else "Kira borcu yok ✓"))
                self.l_k_durum.configure(style="BuyukY.TLabel")
        else:
            self.v_k_durum.set(f"Aylık kira {para(kira)}")
            self.l_k_durum.configure(style="BuyukG.TLabel")
        if not k.get("cikis"):
            if v.takip:
                self.renkli(self.f_k_dug, "💰 Ödeme al", MAVI, lambda: self.odeme_formu(k["id"])).pack(side="left")
                self.renkli(self.f_k_dug, "💬 WhatsApp", YESIL, lambda: self.mesaj_penceresi("WhatsApp mesajı", v.hatirlatma_metni(k), k.get("tel"))).pack(side="left", padx=6)
            self.renkli(self.f_k_dug, "📈 TÜFE ile kira artışı", YESIL if not v.takip else MAVI, lambda: self.artis_formu(k["id"])).pack(side="left", padx=(0, 6))
        for metin, komut in (("✏ Bilgileri düzenle", lambda: self.kiraci_formu(kiraci_id=k["id"])),
                             ("📄 Kiracı kartı (PDF)", lambda: self.pdf(lambda y: rapor_kiraci_karti(v, k["id"], y), f"Kiraci Karti {k['ad']}"))):
            ttk.Button(self.f_k_dug, text=metin, command=komut).pack(side="left", padx=(0, 4))
        if not k.get("cikis"):
            ttk.Button(self.f_k_dug, text="🚪 Çıkış yaptı", command=lambda: self.cikis_formu(k["id"])).pack(side="left")
        else:
            ttk.Button(self.f_k_dug, text="🗑 Kaydı sil", command=lambda: self.kiraci_sil(k["id"])).pack(side="left")

        ic = ttk.Notebook(self.f_k_alt, style="Ic.TNotebook")
        ic.grid(row=0, column=0, sticky="nsew")
        # bilgiler
        f1 = ttk.Frame(ic, padding=8)
        ic.add(f1, text=" Bilgiler ")
        f1.columnconfigure(1, weight=1)
        satirlar = [("TC kimlik no", k.get("tc", "")), ("Telefon", k.get("tel", "")), ("E-posta", k.get("eposta", "")),
                    ("Acil durumda aranacak", " · ".join(x for x in (k.get("acil_ad", ""), k.get("acil_yakinlik", ""), k.get("acil_tel", "")) if x)),
                    ("Taşınma tarihi", tarih_yaz(k.get("giris", ""))),
                    ("Sözleşme", f"{tarih_yaz(k.get('sozlesme_bas', ''))} – {tarih_yaz(k.get('sozlesme_bitis', ''))}"),
                    ("İlk kira (taşındığında)", para(k.get("ilk_kira") or 0)), ("Güncel aylık kira", para(kira)),
                    ("Kira ödeme günü", f"Her ayın {k.get('odeme_gunu') or 1}. günü"), ("Depozito", para(k.get("depozito") or 0))]
        if k.get("cikis"):
            satirlar.append(("Depozito iadesi", f"{para(k.get('depozito_iade') or 0)}  ({tarih_yaz(k.get('depozito_iade_tarih', ''))})"
                             + (f" – {k['depozito_not']}" if k.get("depozito_not") else "")))
        yd = v.sonraki_yildonumu(k.get("sozlesme_bas") or k.get("giris")) if not k.get("cikis") else None
        if yd:
            satirlar.append(("Sonraki kira artışı", tarih_yaz(yd)))
        if k.get("esya_notu"):
            satirlar.append(("Eşya / teslim notu", k["esya_notu"]))
        if k.get("not"):
            satirlar.append(("Not", k["not"]))
        for n, (a, b) in enumerate(satirlar):
            ttk.Label(f1, text=a, foreground=GRI).grid(row=n, column=0, sticky="nw", padx=(0, 14), pady=2)
            ttk.Label(f1, text=b, wraplength=460, justify="left").grid(row=n, column=1, sticky="w", pady=2)
        # belgeler
        f2 = ttk.Frame(ic, padding=6)
        ic.add(f2, text=f" Belgeler ({len(k.get('belgeler', []))}) ")
        self._belge_paneli(f2, "kiracilar", k["id"], BELGE_TURLERI_KIRACI)
        # kira geçmişi
        f3 = ttk.Frame(ic, padding=6)
        ic.add(f3, text=" Kira geçmişi ")
        f3.columnconfigure(0, weight=1)
        f3.rowconfigure(0, weight=1)
        cer, t = self.tablo(f3, (("tarih", "Geçerlilik", 100, "w"), ("eski", "Eski kira", 110, "e"), ("yeni", "Yeni kira", 110, "e"),
                                 ("oran", "Oran", 70, "e"), ("ac", "Açıklama", 200, "w")), yukseklik=7)
        cer.grid(row=0, column=0, sticky="nsew")
        t.insert("", "end", values=(tarih_yaz(k.get("giris", "")), "", para_kisa(k.get("ilk_kira") or 0), "", "Taşınırken ilk kira"))
        for a in v.kira_gecmisi(k["id"]):
            t.insert("", "end", iid=a["id"], values=(tarih_yaz(a["tarih"]), para_kisa(a["eski_kira"]), para_kisa(a["yeni_kira"]),
                                                     f"%{sayi_yaz(a.get('oran') or 0)}", a.get("aciklama", "")))
        ttk.Button(f3, text="🗑 Seçili artışı geri al", command=lambda: self.artis_sil(self._sec(t))).grid(row=1, column=0, sticky="w", pady=(6, 0))
        # ödemeler
        if v.takip:
            f4 = ttk.Frame(ic, padding=6)
            ic.add(f4, text=" Kira ödemeleri ")
            f4.columnconfigure(0, weight=1)
            f4.rowconfigure(0, weight=1)
            cer, t4 = self.tablo(f4, (("tarih", "Tarih", 90, "w"), ("ad", "Açıklama", 240, "w"), ("tutar", "Tutar", 100, "e"), ("bakiye", "Bakiye", 100, "e")),
                                 yukseklik=7)
            cer.grid(row=0, column=0, sticky="nsew")
            for x in reversed(v.hareketler(k["id"])):
                t4.insert("", "end", iid=(x["odeme"]["id"] if "odeme" in x else "b-" + x["borc"]["id"]), tags=("alacak" if x["tutar"] > 0 else "borc",),
                          values=(tarih_yaz(x["tarih"]), x["ad"], ("+" if x["tutar"] > 0 else "") + para_kisa(x["tutar"]),
                                  ("+" if x["bakiye"] > 0 else "") + para_kisa(x["bakiye"])))
            t4.bind("<Double-1>", lambda _e: (self._sec(t4) or "b-").startswith("b-") or self.odeme_formu(odeme_id=self._sec(t4)))
            ttk.Label(f4, text="Ödeme satırına çift tıklayınca düzenlenir / silinir. Bakiye: eksi borç, artı fazla ödeme.", style="Not.TLabel").grid(row=1, column=0, sticky="w")
        try:
            ic.select(min(self._k_sekme, len(ic.tabs()) - 1))
        except tk.TclError:
            pass

    def kiraci_formu(self, kiraci_id=None, daire_id=None):
        v = self.v
        k = v.bul("kiracilar", kiraci_id)
        bos = [d for b in v.binalar() for d in v.bina_daireleri(b["id"]) if not v.aktif_kiraci(d["id"])]
        if k:
            daireler = [v.bul("daireler", k["daire_id"])]
        else:
            if daire_id is None:
                daire_id = self._secili_daire() if self.defter.select() == str(self.sayfalar["binalar"]) else None
            daireler = bos
            if not daireler:
                return messagebox.showinfo("Kiracı", "Boş daire yok. Önce “Binalar ve Daireler” bölümünden bina / daire ekleyin.", parent=self)
        adlar = [v.daire_adi(d) for d in daireler]
        f = Form(self, f"{k['ad']} – bilgiler" if k else "Kiracı yerleştir", 600)
        sec = next((v.daire_adi(d) for d in daireler if d["id"] == (k["daire_id"] if k else daire_id)), adlar[0])
        daire = f.secim("Daire", adlar, sec)
        if k:
            daire.combo.configure(state="disabled")
        f.etiket("Kişisel bilgiler", "Sonuc.TLabel")
        ad = f.giris("Ad soyad", k["ad"] if k else "")
        tc = f.giris("TC kimlik no", k.get("tc", "") if k else "")
        tel = f.giris("Telefon (WhatsApp)", k.get("tel", "") if k else "")
        ep = f.giris("E-posta", k.get("eposta", "") if k else "")
        acil = f.giris("Acil durumda aranacak kişi", k.get("acil_ad", "") if k else "")
        acil_y = f.giris("Yakınlığı (anne, eş…)", k.get("acil_yakinlik", "") if k else "")
        acil_t = f.giris("Acil durum telefonu", k.get("acil_tel", "") if k else "")
        f.etiket("Kira ve sözleşme", "Sonuc.TLabel")
        giris = f.giris("Taşınma tarihi (gg.aa.yyyy)", tarih_yaz(k.get("giris", "") if k else bugun()))
        sbas = f.giris("Sözleşme başlangıcı", tarih_yaz(k.get("sozlesme_bas", "")) if k else tarih_yaz(bugun()))
        sbit = f.giris("Sözleşme bitişi", tarih_yaz(k.get("sozlesme_bitis", "")) if k else "")
        ilk = f.giris("Taşındığındaki aylık kira (TL)", sayi_yaz(k.get("ilk_kira") or 0) if k else "", sag=True)
        gun = f.giris("Kira ödeme günü (her ayın kaçı)", str(k.get("odeme_gunu", 1)) if k else "1", sag=True)
        dep = f.giris("Depozito (TL)", sayi_yaz(k.get("depozito") or 0) if k else "", sag=True)
        if k and v.kira_gecmisi(k["id"]):
            f.not_(f"Güncel kira {para(v.guncel_kira(k))} (artışlarla). Kira artışları “TÜFE ile kira artışı” düğmesiyle yapılır.")
        esya = f.metin("Eşya / teslim notu", k.get("esya_notu", "") if k else "", 2)
        n = f.metin("Not", k.get("not", "") if k else "", 2)
        if not k:
            f.not_("Kaydettikten sonra kimlik fotoğrafı, kimlik fotokopisi ve taranmış sözleşmeyi kiracının “Belgeler” bölümünden ekleyin.")

        def otomatik_bitis(*_):
            b = tarih_oku(sbas.get())
            if b and not sbit.get().strip():
                bd = datetime.date.fromisoformat(b)
                try:
                    sbit.set(tarih_yaz(bd.replace(year=bd.year + 1).isoformat()))
                except ValueError:
                    sbit.set(tarih_yaz(bd.replace(year=bd.year + 1, day=28).isoformat()))

        if not k:
            sbas.entry.bind("<FocusOut>", otomatik_bitis)

        def kaydet():
            if not ad.get().strip():
                return messagebox.showwarning("Eksik", "Ad soyad yazın.", parent=f)
            g, sb, sbt = tarih_oku(giris.get()), tarih_oku(sbas.get()) if sbas.get().strip() else "", tarih_oku(sbit.get()) if sbit.get().strip() else ""
            if not g or sb is None or sbt is None:
                return messagebox.showwarning("Tarih", "Tarihleri gg.aa.yyyy şeklinde yazın (taşınma tarihi zorunlu).", parent=f)
            if (sb or g) and not sbt and not k:
                bd = datetime.date.fromisoformat(sb or g)
                try:
                    sbt = bd.replace(year=bd.year + 1).isoformat()
                except ValueError:
                    sbt = bd.replace(year=bd.year + 1, day=28).isoformat()
            try:
                kira = sayi_al(ilk, "Kira", ebeveyn=f)
                dp = sayi_al(dep, "Depozito", bos_olabilir=True, ebeveyn=f)
                og = int(sayi_al(gun, "Ödeme günü", bos_olabilir=True, ebeveyn=f) or 1)
            except ValueError:
                return
            if not kira:
                return messagebox.showwarning("Eksik", "Aylık kirayı yazın.", parent=f)
            if tc.get().strip() and not tc_gecerli(tc.get().strip()) and not messagebox.askyesno(
                    "TC kimlik no", "TC kimlik numarası geçerli görünmüyor. Yine de kaydedilsin mi?", parent=f):
                return
            d = daireler[adlar.index(daire.get())]
            yeni = dict(k or {"belgeler": [], "cikis": ""}, daire_id=d["id"], ad=ad.get().strip(), tc=tc.get().strip(), tel=tel.get().strip(),
                        eposta=ep.get().strip(), acil_ad=acil.get().strip(), acil_yakinlik=acil_y.get().strip(), acil_tel=acil_t.get().strip(),
                        giris=g, sozlesme_bas=sb, sozlesme_bitis=sbt, ilk_kira=kira, odeme_gunu=min(28, max(1, og)), depozito=dp or 0,
                        esya_notu=esya.get("1.0", "end").strip(), **{"not": n.get("1.0", "end").strip()})
            kayit = v.yaz("kiracilar", yeni, False)
            if k:
                # ilk kira / giriş değiştiyse yazılmış kiraları güncelle, artık geçersiz ayları sil
                aylar = set(v.kira_aylari(kayit, bu_donem()))
                for b in [b for b in v.d["borclar"] if b["kiraci_id"] == kayit["id"]]:
                    if b["donem"] not in aylar:
                        v.sil("borclar", b["id"], False)
                    else:
                        v.yaz("borclar", dict(b, tutar=v.kira_tutari(kayit, b["donem"]),
                                              tarih=f"{b['donem']}-{min(int(kayit['odeme_gunu']), 28):02d}"), False)
            v.kaydet()
            f.destroy()
            self.otomatik()
            self.git("kiraci", kayit["id"])
            self.durum("Kiracı kaydedildi." + ("" if k else " Şimdi “Belgeler” bölümünden kimlik ve sözleşmeyi ekleyebilirsiniz."))

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def artis_formu(self, kiraci_id):
        v = self.v
        k = v.bul("kiracilar", kiraci_id)
        eski = v.guncel_kira(k)
        yd = v.sonraki_yildonumu(k.get("sozlesme_bas") or k.get("giris")) or bugun()
        f = Form(self, f"{k['ad']} – TÜFE ile kira artışı", 520)
        f.etiket(f"Şu anki kira: {para(eski)}", "Sonuc.TLabel")
        oran = f.giris("Artış oranı (%)", "", sag=True)
        f.not_("Konut kiralarında yasal üst sınır, TÜİK'in açıkladığı son 12 aylık TÜFE ortalamasıdır. Oranı TÜİK'in sitesinden ya da "
               "haberlerden bakıp yazın. Taraflar daha düşük bir oranda da anlaşabilir.")
        yuvarla = f.secim("Yeni kirayı yuvarla", ["Yuvarlama", "10 TL'ye", "50 TL'ye", "100 TL'ye"], "Yuvarlama")
        yeni = f.giris("Yeni aylık kira (TL)", "", sag=True)
        tarih = f.giris("Hangi tarihten geçerli? (gg.aa.yyyy)", tarih_yaz(yd))
        ac = f.giris("Açıklama", f"{bu_donem()[:4]} TÜFE artışı")

        def hesapla(*_):
            o = sayi_oku(oran.get())
            if o is None:
                return
            t = eski * (1 + o / 100)
            adim = {"10 TL'ye": 10, "50 TL'ye": 50, "100 TL'ye": 100}.get(yuvarla.get())
            if adim:
                t = round(t / adim) * adim
            yeni.set(sayi_yaz(t))

        oran.trace_add("write", hesapla)
        yuvarla.trace_add("write", hesapla)

        def kaydet():
            try:
                y = sayi_al(yeni, "Yeni kira", ebeveyn=f)
            except ValueError:
                return
            tr = tarih_oku(tarih.get())
            if not y or not tr:
                return messagebox.showwarning("Eksik", "Yeni kirayı ve geçerlilik tarihini yazın.", parent=f)
            o = sayi_oku(oran.get())
            if o is None:
                o = (y / eski - 1) * 100 if eski else 0
            v.yaz("artislar", {"kiraci_id": k["id"], "tarih": tr, "eski_kira": eski, "yeni_kira": y, "oran": yuv(o), "aciklama": ac.get().strip()}, False)
            for b in [b for b in v.d["borclar"] if b["kiraci_id"] == k["id"] and b["donem"] >= tr[:7]]:
                v.yaz("borclar", dict(b, tutar=v.kira_tutari(k, b["donem"])), False)
            v.kaydet()
            f.destroy()
            self.ciz()
            self.durum(f"Kira {tarih_yaz(tr)} tarihinden itibaren {para(y)} oldu.")

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def artis_sil(self, artis_id):
        v = self.v
        a = v.bul("artislar", artis_id)
        if not a:
            return messagebox.showinfo("Kira artışı", "Listeden geri alınacak artışı seçin.", parent=self)
        if messagebox.askyesno("Kira artışı", f"{tarih_yaz(a['tarih'])} tarihli artış ({para(a['yeni_kira'])}) geri alınsın mı?", parent=self):
            v.sil("artislar", artis_id, False)
            k = v.bul("kiracilar", a["kiraci_id"])
            for b in [b for b in v.d["borclar"] if b["kiraci_id"] == k["id"] and b["donem"] >= a["tarih"][:7]]:
                v.yaz("borclar", dict(b, tutar=v.kira_tutari(k, b["donem"])), False)
            v.kaydet()
            self.ciz()

    def cikis_formu(self, kiraci_id):
        v = self.v
        k = v.bul("kiracilar", kiraci_id)
        f = Form(self, f"{k['ad']} – çıkış", 500)
        f.not_("Kiracı arşive taşınır; bilgileri ve belgeleri silinmez. Daire boş görünür ve yeni kiracı yerleştirilebilir.")
        tarih = f.giris("Çıkış tarihi (gg.aa.yyyy)", tarih_yaz(bugun()))
        iade = f.giris("İade edilen depozito (TL)", sayi_yaz(k.get("depozito") or 0), sag=True)
        iade_t = f.giris("İade tarihi", tarih_yaz(bugun()))
        notu = f.giris("Kesinti / not (örn. boya için kesildi)", "")

        def kaydet():
            tr, it = tarih_oku(tarih.get()), tarih_oku(iade_t.get()) if iade_t.get().strip() else ""
            if not tr or it is None:
                return messagebox.showwarning("Tarih", "Tarihleri gg.aa.yyyy şeklinde yazın.", parent=f)
            try:
                dp = sayi_al(iade, "Depozito iadesi", bos_olabilir=True, ebeveyn=f)
            except ValueError:
                return
            yeni = v.yaz("kiracilar", dict(k, cikis=tr, depozito_iade=dp or 0, depozito_iade_tarih=it, depozito_not=notu.get().strip()), False)
            for b in [b for b in v.d["borclar"] if b["kiraci_id"] == k["id"] and b["donem"] > tr[:7]]:
                v.sil("borclar", b["id"], False)
            v.kaydet()
            f.destroy()
            self.v_kfiltre.set("Tümü")
            self.ciz()
            self.git("kiraci", yeni["id"])
            h = v.hesap(k["id"]) if v.takip else None
            self.durum(f"{k['ad']} çıkış yaptı." + (f" Dikkat: kira hesabında {para(-h['bakiye'])} borç var." if h and h["bakiye"] < -0.004 else ""))

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def kiraci_sil(self, kiraci_id):
        v = self.v
        k = v.bul("kiracilar", kiraci_id)
        if not messagebox.askyesno("Kaydı sil", f"{k['ad']} kaydı, belgeleri, kira ödemeleri ve artış geçmişi kalıcı olarak silinsin mi?\n\n"
                                   "Eski kiracıları arşivde tutmak genelde daha iyidir (yıllık kira raporu için).", parent=self):
            return
        for t in ("borclar", "odemeler", "artislar"):
            for x in [x for x in v.d[t] if x["kiraci_id"] == kiraci_id]:
                v.sil(t, x["id"], False)
        v.sil("kiracilar", kiraci_id)
        shutil.rmtree(os.path.join(v.klasor, "belgeler", kiraci_id), ignore_errors=True)
        self.ciz()

    # ------------------------------------------------------------ ödeme
    def odeme_formu(self, kiraci_id=None, odeme_id=None):
        v = self.v
        o = v.bul("odemeler", odeme_id)
        kiraci_id = o["kiraci_id"] if o else (kiraci_id or self._sec(self.t_kiraci))
        kiracilar = [k for k in sorted(v.d["kiracilar"], key=lambda k: k["ad"].lower()) if not k.get("cikis") or k["id"] == kiraci_id]
        if not kiracilar:
            return messagebox.showinfo("Ödeme", "Kayıtlı kiracı yok.", parent=self)
        adlar = [f"{k['ad']} – {v.daire_adi(v.bul('daireler', k['daire_id']))}" for k in kiracilar]
        f = Form(self, "Ödemeyi düzenle" if o else "Kira ödemesi al", 560)
        sec = next((adlar[i] for i, k in enumerate(kiracilar) if k["id"] == kiraci_id), adlar[0])
        kv = f.secim("Kiracı", adlar, sec)
        v_bilgi = tk.StringVar()
        ttk.Label(f.govde, textvariable=v_bilgi, style="Not.TLabel").grid(row=f.satir, column=1, columnspan=2, sticky="w")
        f.satir += 1
        tur = f.radyo("İşlem", ["Ödeme alındı", "Para iade edildi"], "Para iade edildi" if o and o["tutar"] < 0 else "Ödeme alındı")
        tutar = f.giris("Tutar (TL)", sayi_yaz(abs(o["tutar"])) if o else "", sag=True)
        hizli = ttk.Frame(f.govde)
        hizli.grid(row=f.satir, column=1, columnspan=2, sticky="w")
        f.satir += 1
        yontem = f.radyo("Nasıl?", ["Havale", "Nakit"], o["yontem"] if o else "Havale")
        tarih = f.giris("Tarih (gg.aa.yyyy)", tarih_yaz(o["tarih"] if o else bugun()))
        ac = f.giris("Açıklama (isteğe bağlı)", o.get("aciklama", "") if o else "")

        def guncelle(*_):
            k = kiracilar[adlar.index(kv.get())]
            h = v.hesap(k["id"])
            kira = v.guncel_kira(k)
            v_bilgi.set(("Borç " + para(-h["bakiye"])) if h["bakiye"] < -0.004 else (f"Fazla ödeme +{para(h['bakiye'])}" if h["bakiye"] > 0.004 else "Borcu yok"))
            for w in hizli.winfo_children():
                w.destroy()
            if h["bakiye"] < -0.004:
                ttk.Button(hizli, text=f"Borcun tamamı {para_kisa(-h['bakiye'])}", command=lambda: tutar.set(sayi_yaz(-h["bakiye"]))).pack(side="left", padx=(0, 4))
            for n in (1, 3, 6, 12):
                ttk.Button(hizli, text=f"{n} ay {para_kisa(kira * n)}", command=lambda n=n: tutar.set(sayi_yaz(kira * n))).pack(side="left", padx=(0, 4))
            if not o and not tutar.get() and h["bakiye"] < -0.004:
                tutar.set(sayi_yaz(-h["bakiye"]))

        kv.trace_add("write", guncelle)
        guncelle()

        def kaydet():
            try:
                t = sayi_al(tutar, "Tutar", ebeveyn=f)
            except ValueError:
                return
            tr = tarih_oku(tarih.get())
            if not t or not tr:
                return messagebox.showwarning("Eksik", "Tutarı ve tarihi yazın.", parent=f)
            k = kiracilar[adlar.index(kv.get())]
            v.yaz("odemeler", dict(o or {}, kiraci_id=k["id"], daire_id=k["daire_id"], tarih=tr, tutar=-t if tur.get() == "Para iade edildi" else t,
                                   yontem=yontem.get(), aciklama=ac.get().strip()))
            f.destroy()
            self.ciz()
            self.git("kiraci", k["id"])
            h = v.hesap(k["id"])
            self.durum(f"Ödeme kaydedildi. {k['ad']}: " + (f"borç {para(-h['bakiye'])}" if h["bakiye"] < -0.004 else "kira borcu yok."))

        def sil():
            if messagebox.askyesno("Sil", "Bu ödeme kaydı silinsin mi?", parent=f):
                v.sil("odemeler", o["id"])
                f.destroy()
                self.ciz()

        dug = [("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None)]
        if o:
            dug.insert(1, ("Sil", sil, KIRMIZI))
        f.dugmeler(*dug)
        f.ac()

    def mesaj_penceresi(self, baslik, metin, tel=None):
        f = Form(self, baslik, 560)
        t = f.metin("Mesaj", metin, 12)

        def kopyala():
            self.clipboard_clear()
            self.clipboard_append(t.get("1.0", "end").strip())
            self.durum("Mesaj kopyalandı.")

        f.dugmeler(("💬 WhatsApp'ta aç", lambda: (wa_ac(tel or "", t.get("1.0", "end").strip()), f.destroy()), YESIL),
                   ("📋 Kopyala", kopyala, None), ("Kapat", f.destroy, None))
        f.ac()

    # ------------------------------------------------------------ raporlar
    def _raporlar_kur(self):
        p = self.sayfalar["raporlar"]
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)

        def kart(satir, sutun, baslik, aciklama):
            f = ttk.LabelFrame(p, text=f" {baslik} ", padding=12)
            f.grid(row=satir, column=sutun, sticky="nsew", padx=6, pady=6)
            ttk.Label(f, text=aciklama, style="Not.TLabel", wraplength=480, justify="left").pack(anchor="w", pady=(0, 8))
            return f

        f = kart(0, 0, "📆 Yıllık kira geliri", "Daire daire, ay ay kira tutarları (artışlar dahil) ve yıl toplamı. Kira geliri beyannamesi için yardımcı.")
        self.v_r_yil = tk.StringVar(value=bu_donem()[:4])
        self.c_r_yil = ttk.Combobox(f, textvariable=self.v_r_yil, state="readonly", width=8, font=(self.fa, 11))
        self.c_r_yil.pack(side="left")
        self.renkli(f, "PDF oluştur", MAVI, lambda: self.pdf(lambda y: rapor_yillik_kira(self.v, self.v_r_yil.get(), y),
                                                             f"{self.v_r_yil.get()} Kira Geliri")).pack(side="left", padx=8)
        self.v_r_yil_ozet = tk.StringVar()
        ttk.Label(p, textvariable=self.v_r_yil_ozet, style="Sonuc.TLabel").grid(row=1, column=0, sticky="w", padx=12)
        f = kart(0, 1, "👥 Kiracı listesi", "Bütün dairelerin güncel kiracısı, telefonu, sözleşme bitişi ve kirası.")
        self.renkli(f, "PDF oluştur", MAVI, lambda: self.pdf(lambda y: rapor_kiraci_listesi(self.v, y), f"Kiraci Listesi {bugun()}")).pack(anchor="w")
        f = kart(2, 0, "👤 Kiracı kartı", "Bir kiracının bütün bilgileri, sözleşmesi, kira geçmişi ve belgelerinin listesi.")
        self.v_r_kiraci = tk.StringVar()
        self.c_r_kiraci = ttk.Combobox(f, textvariable=self.v_r_kiraci, state="readonly", width=34, font=(self.fa, 11))
        self.c_r_kiraci.pack(side="left")
        self.renkli(f, "PDF oluştur", MAVI, self.r_kart).pack(side="left", padx=8)
        f = kart(2, 1, "📁 Rapor klasörü", f"PDF'ler bu bilgisayarda şu klasöre kaydedilir:\n{pdf_klasoru()}")
        ttk.Button(f, text="Klasörü aç", command=lambda: dosya_ac(pdf_klasoru())).pack(anchor="w")

    def raporlar_ciz(self):
        v = self.v
        yillar = sorted({k["giris"][:4] for k in v.d["kiracilar"] if k.get("giris")} | {bu_donem()[:4]}, reverse=True)
        yillar = [str(y) for y in range(int(yillar[-1]), int(bu_donem()[:4]) + 1)][::-1]
        self.c_r_yil.configure(values=yillar)
        if self.v_r_yil.get() not in yillar:
            self.v_r_yil.set(yillar[0])
        yk = v.yillik_kira(self.v_r_yil.get())
        toplam = sum(t for d in yk.values() for t, _k, _g in d.values())
        self.v_r_yil_ozet.set(f"{self.v_r_yil.get()} yılı toplam kira geliri: {para(toplam)}")
        self._r_kiracilar = sorted(v.d["kiracilar"], key=lambda k: (bool(k.get("cikis")), k["ad"].lower()))
        self.c_r_kiraci.configure(values=[f"{k['ad']} – {v.daire_adi(v.bul('daireler', k['daire_id']))}" + (" (çıktı)" if k.get("cikis") else "")
                                          for k in self._r_kiracilar])
        if self.v_r_kiraci.get() not in self.c_r_kiraci["values"] and self._r_kiracilar:
            self.v_r_kiraci.set(self.c_r_kiraci["values"][0])
        self.c_r_yil.bind("<<ComboboxSelected>>", lambda _e: self.raporlar_ciz())

    def r_kart(self):
        if not self._r_kiracilar:
            return
        k = self._r_kiracilar[list(self.c_r_kiraci["values"]).index(self.v_r_kiraci.get())]
        self.pdf(lambda y: rapor_kiraci_karti(self.v, k["id"], y), f"Kiraci Karti {k['ad']}")

    def pdf(self, uret, ad):
        if not PDF_VAR:
            return messagebox.showerror("PDF", "PDF kütüphanesi bulunamadı.", parent=self)
        yol = os.path.join(pdf_klasoru(), guvenli_ad(ad) + ".pdf")
        try:
            uret(yol)
        except PermissionError:
            return messagebox.showerror("PDF", "PDF yazılamadı. Aynı dosya açıksa kapatıp tekrar deneyin.", parent=self)
        except Exception as hata:
            return messagebox.showerror("PDF oluşturulamadı", str(hata), parent=self)
        self.durum(f"PDF oluşturuldu: {yol}")
        dosya_ac(yol)

    # ------------------------------------------------------------ ayarlar
    def _ayarlar_kur(self):
        p = self.sayfalar["ayarlar"]
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        sol = ttk.LabelFrame(p, text=" Genel ", padding=12)
        sol.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        sol.columnconfigure(1, weight=1)
        self.ay = {}
        for n, (a, e) in enumerate((("ad_soyad", "Adınız soyadınız"), ("iban", "Kira IBAN"), ("iban_ad", "IBAN hesap sahibi"),
                                    ("uyari_sozlesme_gun", "Sözleşme bitişini kaç gün önce hatırlat"),
                                    ("uyari_artis_gun", "Kira artışını kaç gün önce hatırlat"))):
            ttk.Label(sol, text=e).grid(row=n, column=0, sticky="w", pady=3, padx=(0, 10))
            self.ay[a] = tk.StringVar()
            ttk.Entry(sol, textvariable=self.ay[a], font=(self.fa, 11)).grid(row=n, column=1, sticky="we", pady=3)
        self.ay_takip = tk.BooleanVar(value=True)
        ttk.Checkbutton(sol, text="Kira ödemelerini takip et (her ay kira borcu yazılır, gecikmeler hatırlatılır)",
                        variable=self.ay_takip).grid(row=6, column=0, columnspan=2, sticky="w", pady=6)
        self.renkli(sol, "💾 Kaydet", MAVI, self.ayar_kaydet).grid(row=7, column=0, sticky="w", pady=(8, 0))
        sag = ttk.LabelFrame(p, text=" Şifre ve veriler ", padding=12)
        sag.grid(row=0, column=1, sticky="nsew")
        sag.columnconfigure(0, weight=1)
        ttk.Button(sag, text="🔑 Şifreyi değiştir", command=self.sifre_degistir).grid(row=0, column=0, sticky="w")
        self.v_klasor = tk.StringVar()
        ttk.Label(sag, textvariable=self.v_klasor, wraplength=480, justify="left").grid(row=1, column=0, sticky="w", pady=(10, 4))
        d = ttk.Frame(sag)
        d.grid(row=2, column=0, sticky="w")
        ttk.Button(d, text="📁 Ortak klasör seç (Google Drive)…", command=self.klasor_sec).pack(side="left")
        ttk.Button(d, text="💻 Bu bilgisayarın klasörüne dön", command=self.yerele_don).pack(side="left", padx=6)
        ttk.Label(sag, text="İki bilgisayarda kullanmak için her ikisinde de Google Drive masaüstü uygulamasını aynı hesapla açın, sonra burada "
                  "Google Drive'daki aynı klasörü seçin (örn. G:\\Drive'ım). Program içinde “KiraTakip” klasörünü kendisi oluşturur; belgeler de "
                  "oraya taşınır.\n\nKimlik ve sözleşme gibi kişisel bilgiler bu klasörde durur; Drive klasörünü başkalarıyla paylaşmayın.",
                  style="Not.TLabel", wraplength=480, justify="left").grid(row=3, column=0, sticky="w", pady=(6, 0))

    def ayarlari_doldur(self):
        if self.defter.select() != str(self.sayfalar["ayarlar"]):
            return
        v = self.v
        for a, x in self.ay.items():
            x.set(str(v.ayar(a, {"uyari_sozlesme_gun": 60, "uyari_artis_gun": 30}.get(a, ""))))
        self.ay_takip.set(v.takip)
        self.v_klasor.set(("Ortak klasör: " if self.yerel.get("klasor") else "Veriler sadece bu bilgisayarda: ") + v.klasor)

    def ayar_kaydet(self):
        try:
            g1 = int(sayi_oku(self.ay["uyari_sozlesme_gun"].get()) or 60)
            g2 = int(sayi_oku(self.ay["uyari_artis_gun"].get()) or 30)
        except ValueError:
            return
        yeni = {a: x.get().strip() for a, x in self.ay.items()}
        yeni.update(uyari_sozlesme_gun=g1, uyari_artis_gun=g2, kira_takibi=self.ay_takip.get())
        self.v.ayarlari_yaz(yeni)
        self.otomatik()
        self.durum("Ayarlar kaydedildi.")

    def sifre_degistir(self):
        f = Form(self, "Şifreyi değiştir")
        s1 = f.giris("Mevcut şifre", show="•")
        s2 = f.giris("Yeni şifre", show="•")
        s3 = f.giris("Yeni şifre (tekrar)", show="•")

        def kaydet():
            if not self.v.sifre_dogru(s1.get()):
                return messagebox.showerror("Şifre", "Mevcut şifre yanlış.", parent=f)
            if len(s2.get()) < 4 or s2.get() != s3.get():
                return messagebox.showerror("Şifre", "Yeni şifreler aynı değil ya da çok kısa (en az 4 karakter).", parent=f)
            self.v.sifre_yaz(s2.get())
            f.destroy()
            self.durum("Şifre değiştirildi.")

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def _klasore_gec(self, hedef, ortak):
        eski = self.v
        eski.kaydet()
        vardi = os.path.exists(os.path.join(hedef, "kira.json"))
        yeni = Veri(hedef)
        if vardi and ortak:
            yeni.d = yeni._tamamla(birlestir(yeni.d, eski.d))
            mesaj = "Bu klasörde zaten veri vardı; iki taraftaki kayıtlar birleştirildi."
        else:
            yeni.d = json.loads(json.dumps(eski.d))
            mesaj = "Veriler ve belgeler yeni klasöre kopyalandı."
        kaynak = os.path.join(eski.klasor, "belgeler")
        if os.path.isdir(kaynak):
            shutil.copytree(kaynak, os.path.join(hedef, "belgeler"), dirs_exist_ok=True)
        yeni.kaydet()
        self.yerel["klasor"] = hedef if ortak else None
        yerel_ayar_yaz(self.yerel)
        self.v = yeni
        self.otomatik()
        messagebox.showinfo("Veri klasörü", mesaj, parent=self)

    def klasor_sec(self):
        s = filedialog.askdirectory(parent=self, title="Google Drive'daki klasörü seçin (örn. Drive'ım)")
        if not s:
            return
        hedef = s if (os.path.basename(os.path.normpath(s)).lower() == "kiratakip" or os.path.exists(os.path.join(s, "kira.json"))) \
            else os.path.join(s, "KiraTakip")
        hedef = os.path.normpath(hedef)
        if os.path.normcase(hedef) == os.path.normcase(self.v.klasor):
            return messagebox.showinfo("Veri klasörü", "Bu klasör zaten kullanılıyor.", parent=self)
        try:
            self._klasore_gec(hedef, True)
        except Exception as hata:
            messagebox.showerror("Veri klasörü", f"Klasör kullanılamadı:\n{hata}", parent=self)

    def yerele_don(self):
        if not self.yerel.get("klasor"):
            return messagebox.showinfo("Veri klasörü", "Zaten bu bilgisayarın kendi klasörü kullanılıyor.", parent=self)
        if messagebox.askyesno("Veri klasörü", "Bu bilgisayar ortak klasörü bırakıp kendi klasörünü kullansın mı?\n"
                               "Ortak klasördeki güncel veriler bu bilgisayara kopyalanır.", parent=self):
            self._klasore_gec(yerel_klasor(), False)


if __name__ == "__main__":
    uyg = Uygulama()
    try:
        if uyg.winfo_exists():
            uyg.mainloop()
    except tk.TclError:
        pass
