"""Apartman Yönetimi - Windows masaüstü programı.

Daireler ve kiracılar, sabit aylık aidat ve ön ödeme, tahsilat, giderler ve düzenli giderler,
ek toplama paylaştırma, kasa, PDF raporlar, WhatsApp mesajları. Şifreli giriş.
Veriler isteğe bağlı olarak Google Drive klasöründe tutulur (bilgisayarlar arası ortak).
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

UYGULAMA_ADI = "Apartman Yönetimi"
SURUM = "1.0.1"
SIFRE_TUZ = "apartman-yonetimi::"
APP_ID = "ArabaciReklam.ApartmanYonetimi"
TABLOLAR = ["daireler", "sakinler", "tarifeler", "borclar", "odemeler", "giderler", "ekler", "duzenliler", "kategoriler"]
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
VARSAYILAN_KATEGORILER = ["Temizlikçi", "Asansör bakımı", "Asansör tamiri", "Ortak elektrik", "Ortak su",
                          "Temizlik malzemesi", "Tamirat", "Diğer"]

KIRMIZI = "#d62828"
YESIL = "#1e8e3e"
MAVI = "#1f5fbf"
GRI = "#666666"
TURUNCU = "#c76a00"


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
    k = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "ApartmanYonetimi")
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
    k = os.path.join(os.path.expanduser("~"), "Documents", "Apartman Yonetimi")
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
    """Bütün kayıtlar: <veri klasörü>\\apartman.json"""

    def __init__(self, klasor=None):
        self.klasor = klasor or yerel_klasor()
        os.makedirs(self.klasor, exist_ok=True)
        self.yol = os.path.join(self.klasor, "apartman.json")
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

    # ---------------------------------------------------------------- kayıt işlemleri
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

    def kurulum(self, v):
        self.d["ayarlar"] = {
            "apartman_adi": v["apartman_adi"], "adres": v.get("adres", ""), "yonetici_ad": v.get("yonetici_ad", ""),
            "yonetici_tel": v.get("yonetici_tel", ""), "iban": v.get("iban", ""), "iban_ad": v.get("iban_ad", ""),
            "baslangic_donem": v["baslangic_donem"], "son_odeme_gunu": v.get("son_odeme_gunu", "10"),
            "acilis_banka": 0, "acilis_nakit": 0, "rapor_borc_tablosu": True,
        }
        self.d["ayarlar_z"] = time.time()
        self.yaz("tarifeler", {"baslangic_donem": v["baslangic_donem"], "tutar": v["aidat"], "aciklama": "İlk aidat"}, False)
        for i in range(1, int(v["daire_sayisi"]) + 1):
            self.yaz("daireler", {"no": str(i), "kat": "", "aktif": True, "baslangic_donem": v["baslangic_donem"],
                                  "ozel_aidat": None, "pay_orani": 1, "ev_sahibi_ad": "", "ev_sahibi_tel": "", "not": ""}, False)
        for k in VARSAYILAN_KATEGORILER:
            self.yaz("kategoriler", {"ad": k}, False)
        self.d["sifre"] = sifre_ozet(v["sifre"])
        self.d["sifre_z"] = time.time()
        self.kaydet()

    # ---------------------------------------------------------------- sorgular
    def bul(self, tablo, kimlik):
        return next((k for k in self.d[tablo] if k["id"] == kimlik), None)

    @staticmethod
    def _daire_sira(d):
        try:
            return (0, float(d["no"]), "")
        except ValueError:
            return (1, 0, d["no"])

    def tum_daireler(self):
        return sorted(self.d["daireler"], key=self._daire_sira)

    def aktif_daireler(self):
        return [d for d in self.tum_daireler() if d.get("aktif")]

    def aktif_sakin(self, daire_id):
        l = [s for s in self.d["sakinler"] if s["daire_id"] == daire_id and not s.get("cikis")]
        l.sort(key=lambda s: s.get("giris", ""), reverse=True)
        return l[0] if l else None

    def odeyen_adi(self, sakin_id, daire):
        s = self.bul("sakinler", sakin_id) if sakin_id else None
        if s:
            return s["ad"]
        if daire and daire.get("ev_sahibi_ad"):
            return daire["ev_sahibi_ad"] + " (ev sahibi)"
        return "Boş daire / ev sahibi"

    def oturan_adi(self, d):
        s = self.aktif_sakin(d["id"])
        if s:
            return s["ad"]
        return d["ev_sahibi_ad"] + " (boş, ev sahibi)" if d.get("ev_sahibi_ad") else "Boş"

    def oturan_tel(self, d):
        s = self.aktif_sakin(d["id"])
        return s.get("tel", "") if s else d.get("ev_sahibi_tel", "")

    def tarife_tutari(self, donem):
        hepsi = sorted(self.d["tarifeler"], key=lambda t: t["baslangic_donem"])
        once = [t for t in hepsi if t["baslangic_donem"] <= donem]
        if once:
            return once[-1]["tutar"]
        return hepsi[0]["tutar"] if hepsi else 0

    def aidat_tutari(self, donem, d):
        if d.get("ozel_aidat") is not None:
            return d["ozel_aidat"]
        return self.tarife_tutari(donem)

    def hesap(self, daire_id):
        """Dairenin hesabı. Ödemeler aynı kişinin borçlarına eskiden yeniye dağıtılır.
        bakiye > 0: alacaklı (ön ödeme), < 0: borçlu."""
        borclar = [dict(b, kalan=b["tutar"]) for b in self.d["borclar"] if b["daire_id"] == daire_id]
        odemeler = [o for o in self.d["odemeler"] if o["daire_id"] == daire_id]
        kisiler = {}
        for b in borclar:
            k = kisiler.setdefault(b.get("sakin_id", ""), {"borc": 0.0, "odeme": 0.0, "borclar": []})
            k["borc"] += b["tutar"]
            k["borclar"].append(b)
        for o in odemeler:
            k = kisiler.setdefault(o.get("sakin_id", ""), {"borc": 0.0, "odeme": 0.0, "borclar": []})
            k["odeme"] += o["tutar"]
        for k in kisiler.values():
            k["borclar"].sort(key=lambda b: (b["donem"], b.get("tarih", ""), 0 if b["tur"] == "Aidat" else 1))
            kalan = k["odeme"]
            for b in k["borclar"]:
                p = max(0.0, min(b["kalan"], kalan))
                b["kalan"] = yuv(b["kalan"] - p)
                kalan -= p
            k["bakiye"] = yuv(k["odeme"] - k["borc"])
            k["acik"] = [b for b in k["borclar"] if b["kalan"] > 0.004]
        s = self.aktif_sakin(daire_id)
        aktif_id = s["id"] if s else ""
        ana = kisiler.get(aktif_id, {"bakiye": 0.0, "acik": [], "borclar": []})
        d = self.bul("daireler", daire_id)
        eskiler = [{"sakin_id": i, "ad": self.odeyen_adi(i, d), "bakiye": k["bakiye"], "acik": k["acik"]}
                   for i, k in kisiler.items() if i != aktif_id and abs(k["bakiye"]) > 0.004]
        toplam = yuv(sum(o["tutar"] for o in odemeler) - sum(b["tutar"] for b in borclar))
        tum_acik = [b for k in kisiler.values() for b in k["acik"]]
        return {"bakiye": ana["bakiye"], "acik": ana["acik"], "eskiler": eskiler, "toplam": toplam,
                "aktif_sakin_id": aktif_id, "tum_acik": tum_acik}

    def kasa(self, son_tarih=None):
        banka = sayi_oku(self.ayar("acilis_banka", 0)) or 0
        nakit = sayi_oku(self.ayar("acilis_nakit", 0)) or 0
        for o in self.d["odemeler"]:
            if son_tarih and o["tarih"] > son_tarih:
                continue
            if o["yontem"] == "Nakit":
                nakit += o["tutar"]
            else:
                banka += o["tutar"]
        for g in self.d["giderler"]:
            if son_tarih and g["tarih"] > son_tarih:
                continue
            if g["odeme"] == "Nakit":
                nakit -= g["tutar"]
            else:
                banka -= g["tutar"]
        return {"banka": yuv(banka), "nakit": yuv(nakit), "toplam": yuv(banka + nakit)}

    def donem_ozeti(self, donem):
        borclar = [b for b in self.d["borclar"] if b["donem"] == donem]
        odemeler = [o for o in self.d["odemeler"] if o["tarih"][:7] == donem]
        giderler = [g for g in self.d["giderler"] if g["tarih"][:7] == donem]
        return {
            "aidat_istenen": yuv(sum(b["tutar"] for b in borclar if b["tur"] == "Aidat")),
            "ek_istenen": yuv(sum(b["tutar"] for b in borclar if b["tur"] != "Aidat")),
            "toplanan": yuv(sum(o["tutar"] for o in odemeler)),
            "harcanan": yuv(sum(g["tutar"] for g in giderler)),
            "odemeler": odemeler, "giderler": giderler, "borclar": borclar,
        }

    def donem_tahsilat(self, donem):
        istenen = kalan = 0.0
        hesaplar = {}
        for b in self.d["borclar"]:
            if b["donem"] != donem:
                continue
            istenen += b["tutar"]
            h = hesaplar.get(b["daire_id"]) or hesaplar.setdefault(b["daire_id"], self.hesap(b["daire_id"]))
            ac = next((x for x in h["tum_acik"] if x["id"] == b["id"]), None)
            kalan += ac["kalan"] if ac else 0
        return {"istenen": yuv(istenen), "odenen": yuv(istenen - kalan), "kalan": yuv(kalan)}

    def aidatlari_yaz(self):
        """Başlangıçtan bu aya kadar yazılmamış aidatları yazar. Yazılan ay adlarını döner."""
        bas, son, yazilan = self.ayar("baslangic_donem", bu_donem()), bu_donem(), set()
        for d in self.aktif_daireler():
            b = max(bas, d.get("baslangic_donem") or bas)
            for m in donemler(b, son):
                kimlik = f"aidat-{d['id']}-{m}"
                if self.bul("borclar", kimlik) or kimlik in self.d["_silinen"].get("borclar", {}):
                    continue
                tutar = self.aidat_tutari(m, d)
                if not tutar or tutar <= 0:
                    continue
                s = self.aktif_sakin(d["id"])
                self.yaz("borclar", {"id": kimlik, "daire_id": d["id"], "sakin_id": s["id"] if s else "", "donem": m,
                                     "tur": "Aidat", "baslik": f"{donem_adi(m)} aidatı", "tutar": tutar, "ek_id": "",
                                     "tarih": m + "-01"}, False)
                yazilan.add(m)
        if yazilan:
            self.kaydet()
        return sorted(yazilan)

    def bekleyen_duzenliler(self):
        m, gun = bu_donem(), datetime.date.today().day
        return [z for z in self.d["duzenliler"] if z.get("aktif") and gun >= int(z.get("gun") or 1)
                and not any(g.get("duzenli_id") == z["id"] and g["tarih"][:7] == m for g in self.d["giderler"])]

    def hareketler(self, daire_id):
        """Dairenin bütün hareketleri, eskiden yeniye, yürüyen bakiyeyle."""
        l = []
        for b in self.d["borclar"]:
            if b["daire_id"] == daire_id:
                l.append({"tarih": b.get("tarih") or b["donem"] + "-01", "sira": 0, "ad": b["baslik"], "tutar": -b["tutar"],
                          "kisi": b.get("sakin_id", ""), "borc": b})
        for o in self.d["odemeler"]:
            if o["daire_id"] == daire_id:
                ad = ("İade" if o["tutar"] < 0 else f"Ödeme ({o['yontem']})") + (f" – {o['aciklama']}" if o.get("aciklama") else "")
                l.append({"tarih": o["tarih"], "sira": 1, "ad": ad, "tutar": o["tutar"], "kisi": o.get("sakin_id", ""), "odeme": o})
        l.sort(key=lambda x: (x["tarih"], x["sira"]))
        bakiye = 0.0
        for x in l:
            bakiye = yuv(bakiye + x["tutar"])
            x["bakiye"] = bakiye
        return l

    # ---------------------------------------------------------------- metinler
    def durum_yazi(self, bakiye):
        if bakiye < -0.004:
            return f"Borç {para(-bakiye)}"
        if bakiye > 0.004:
            return f"Ön ödeme +{para(bakiye)}"
        return "Borcu yok"

    def hatirlatma_metni(self, d):
        h, s = self.hesap(d["id"]), self.aktif_sakin(d["id"])
        ad = s["ad"] if s else d.get("ev_sahibi_ad", "")
        t = f"Merhaba{' ' + ad if ad else ''},\n{self.ayar('apartman_adi', 'Apartman')} Daire {d['no']} aidat bilginiz:\n\n"
        if h["bakiye"] < -0.004:
            for b in h["acik"]:
                t += f"• {b['baslik']}: {para_kisa(b['kalan'])}\n"
            t += f"\nToplam ödenecek: {para(-h['bakiye'])}\n"
            if self.ayar("iban"):
                t += f"\nIBAN: {self.ayar('iban')}" + (f"\nAlıcı: {self.ayar('iban_ad')}" if self.ayar("iban_ad") else "")
                t += f"\nAçıklamaya \"Daire {d['no']}\" yazmanızı rica ederim.\n"
        elif h["bakiye"] > 0.004:
            a = self.aidat_tutari(bu_donem(), d)
            ay = f" (yaklaşık {int(h['bakiye'] // a)} aylık aidat)" if a else ""
            t += f"Ön ödeme bakiyeniz: +{para(h['bakiye'])}{ay}.\nHer ay aidat bu bakiyeden düşülmektedir.\n"
        else:
            t += "Borcunuz bulunmamaktadır, teşekkür ederiz.\n"
        return t + f"\nTeşekkürler,\n{self.ayar('yonetici_ad', 'Apartman Yönetimi')}"

    def ek_duyuru_metni(self, e):
        bl = [b for b in self.d["borclar"] if b.get("ek_id") == e["id"]]
        esit = bl and all(abs(b["tutar"] - bl[0]["tutar"]) < 0.01 for b in bl)
        t = f"Sayın {self.ayar('apartman_adi', 'apartman')} sakinleri,\n\n{e['baslik']} için toplam {para(e['toplam'])} gerekmektedir.\n"
        if e.get("aciklama"):
            t += e["aciklama"] + "\n"
        if esit:
            t += f"\nDaire başına düşen pay: {para(bl[0]['tutar'])}\n"
        else:
            t += "\n" + "\n".join(f"Daire {self.bul('daireler', b['daire_id'])['no']}: {para_kisa(b['tutar'])}" for b in bl) + "\n"
        t += f"Bu tutar {donem_adi(e['donem'])} aidatıyla birlikte hesabınıza yazılmıştır.\n"
        if self.ayar("iban"):
            t += f"\nIBAN: {self.ayar('iban')}" + (f" ({self.ayar('iban_ad')})" if self.ayar("iban_ad") else "") + "\n"
        return t + f"\nTeşekkürler,\n{self.ayar('yonetici_ad', 'Apartman Yönetimi')}"


def ek_dagit(veri, daire_idler, tutar, oranli, daire_basi):
    """Ek toplamayı dairelere böler: (toplam, [(daire_id, tutar)])"""
    if not daire_idler or not tutar or tutar <= 0:
        return None
    paylar = []
    for i in daire_idler:
        d = veri.bul("daireler", i)
        p = d.get("pay_orani", 1) if oranli else 1
        paylar.append(p if p is not None and p >= 0 else 1)
    toplam_pay = sum(paylar)
    if toplam_pay <= 0:
        return None
    toplam = yuv(tutar * (toplam_pay if oranli else len(daire_idler))) if daire_basi else tutar
    dagilim, dagitilan = [], 0.0
    for n, (i, p) in enumerate(zip(daire_idler, paylar)):
        t = yuv(toplam - dagitilan) if n == len(daire_idler) - 1 else yuv(toplam * p / toplam_pay)
        dagitilan = yuv(dagitilan + t)
        dagilim.append((i, t))
    return toplam, dagilim


# ================================================================ PDF raporlar

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
        toplam_gen = 174 * mm
        t = Table(veri, colWidths=[toplam_gen * g for g in genislikler], repeatRows=1)
        stil = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f8")),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#e3e6eb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
        if toplam:
            stil.append(("LINEABOVE", (0, -1), (-1, -1), 1.2, colors.HexColor("#1d2330")))
        t.setStyle(TableStyle(stil))
        self.ogeler.append(t)

    def kaydet(self, yol):
        v = self.v
        alt = []
        if v.ayar("yonetici_ad"):
            alt.append(f"Yönetici: {esc(v.ayar('yonetici_ad'))}" + (f" · {esc(v.ayar('yonetici_tel'))}" if v.ayar("yonetici_tel") else ""))
        if v.ayar("iban"):
            alt.append(f"Aidat IBAN: {esc(v.ayar('iban'))}" + (f" ({esc(v.ayar('iban_ad'))})" if v.ayar("iban_ad") else ""))
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


def rapor_aylik(v, donem, yol):
    ap = v.ayar("apartman_adi", "Apartman")
    o, t = v.donem_ozeti(donem), v.donem_tahsilat(donem)
    onceki, sonra = v.kasa(ay_son_gunu(donem_kaydir(donem, -1))), v.kasa(ay_son_gunu(donem))
    aktif = v.aktif_daireler()
    aidat = v.aidat_tutari(donem, aktif[0]) if aktif else 0
    ekler = [e for e in v.d["ekler"] if e["donem"] == donem]
    kat = {}
    for g in o["giderler"]:
        kat[g["kategori"]] = kat.get(g["kategori"], 0) + g["tutar"]
    sirali = sorted(kat, key=lambda k: -kat[k])
    r = Rapor(v, f"{ap} – {donem_adi(donem)} Gelir-Gider Raporu", v.ayar("adres"))
    ozet = (f"<b>Kısaca:</b> {donem_adi(donem)} ayında her daireden <b>{para(aidat)}</b> aidat istendi"
            + (f", ayrıca ek toplama olarak toplam <b>{para(o['ek_istenen'])}</b> paylaştırıldı" if o["ek_istenen"] else "") + ". "
            + f"Bu ay dairelerden istenen tutarın <b>{para(t['odenen'])}</b> kadarı ödendi"
            + (f", <b>{k_(para(t['kalan']))}</b> henüz ödenmedi" if t["kalan"] > 0.004 else ", tamamı ödendi") + ". "
            + f"Ay içinde kasaya toplam <b>{para(o['toplanan'])}</b> girdi, apartman için <b>{para(o['harcanan'])}</b> harcandı"
            + (f" (en büyük kalem: {esc(sirali[0])} {para(kat[sirali[0]])})" if sirali else "") + ". "
            + f"Ay sonunda kasada <b>{para(sonra['toplam'])}</b> bulunuyor.")
    r.kutu(ozet)
    r.h2("1. Kasa")
    r.tablo(["", "Tutar"], [["Önceki aydan devreden", para(onceki["toplam"])],
                            ["Bu ay kasaya giren (ödemeler)", y_("+" + para(o["toplanan"]))],
                            ["Bu ay harcanan (giderler)", k_("-" + para(o["harcanan"]))]],
            ["", "r"], [0.7, 0.3], ["Ay sonu kasa", para(sonra["toplam"])])
    r.p(f"Ay sonu kasanın {para(sonra['banka'])} tutarı bankada, {para(sonra['nakit'])} tutarı nakit olarak duruyor.", "not")
    r.h2("2. Harcamalar")
    if o["giderler"]:
        r.tablo(["Tarih", "Ne için", "Açıklama", "Tutar"],
                [[tarih_yaz(g["tarih"]), esc(g["kategori"]), esc(g.get("aciklama", "")), para(g["tutar"])]
                 for g in sorted(o["giderler"], key=lambda g: g["tarih"])],
                ["", "", "", "r"], [0.15, 0.25, 0.4, 0.2], ["", "Toplam", "", para(o["harcanan"])])
        if len(sirali) > 1:
            r.p("Harcamaların dağılımı: " + " · ".join(f"{esc(k)} {para(kat[k])} (%{round(kat[k] / o['harcanan'] * 100)})" for k in sirali), "not")
    else:
        r.p("Bu ay harcama yapılmadı.", "not")
    n = 3
    if ekler:
        r.h2(f"{n}. Ek toplamalar")
        n += 1
        for e in ekler:
            bl = [b for b in v.d["borclar"] if b.get("ek_id") == e["id"]]
            esit = bl and all(abs(b["tutar"] - bl[0]["tutar"]) < 0.01 for b in bl)
            r.p(f"<b>{esc(e['baslik'])}</b>: toplam {para(e['toplam'])}, {len(bl)} daireye "
                + ("pay oranına göre" if e.get("dagitim") == "oran" else "eşit") + " bölündü"
                + (f" (daire başı {para(bl[0]['tutar'])})" if esit else "") + "."
                + (f"<br/><font color='{GRI}'>{esc(e['aciklama'])}</font>" if e.get("aciklama") else ""))
    if v.ayar("rapor_borc_tablosu", True):
        r.h2(f"{n}. Dairelerin durumu")
        satirlar = []
        for d in v.tum_daireler():
            bu = sum(b["tutar"] for b in v.d["borclar"] if b["daire_id"] == d["id"] and b["donem"] == donem)
            if not d.get("aktif") and not bu:
                continue
            od = sum(x["tutar"] for x in v.d["odemeler"] if x["daire_id"] == d["id"] and x["tarih"][:7] == donem)
            satirlar.append([f"Daire {esc(d['no'])}", esc(v.oturan_adi(d)), para(bu), para(od) if od else "-", durum_html(v.hesap(d["id"])["toplam"])])
        r.tablo(["Daire", "Oturan", "Bu ay istenen", "Bu ay ödenen", "Güncel durum"], satirlar,
                ["", "", "r", "r", "r"], [0.12, 0.28, 0.18, 0.18, 0.24])
        r.p("\"Ön ödeme\" peşin ödenmiş ve sonraki aylardan düşülecek parayı gösterir. Durum bilgisi rapor tarihindeki günceldir.", "not")
    r.kaydet(yol)


def rapor_yillik(v, yil, yol):
    ap = v.ayar("apartman_adi", "Apartman")
    satirlar, top_t, top_h, son_ay = [], 0.0, 0.0, None
    for i in range(1, 13):
        d = f"{yil}-{i:02d}"
        if d > bu_donem():
            break
        o = v.donem_ozeti(d)
        top_t += o["toplanan"]
        top_h += o["harcanan"]
        son_ay = d
        satirlar.append([AYLAR[i - 1], para(o["aidat_istenen"] + o["ek_istenen"]), para(o["toplanan"]), para(o["harcanan"]),
                         para(v.kasa(ay_son_gunu(d))["toplam"])])
    bas = v.kasa(ay_son_gunu(donem_kaydir(f"{yil}-01", -1)))
    son = v.kasa(ay_son_gunu(son_ay)) if son_ay else bas
    r = Rapor(v, f"{ap} – {yil} Yıllık Gelir-Gider Raporu", v.ayar("adres"))
    r.kutu(f"<b>Kısaca:</b> {yil} yılında kasaya toplam <b>{para(top_t)}</b> girdi, apartman için <b>{para(top_h)}</b> harcandı. "
           f"Yıl başında kasada {para(bas['toplam'])} vardı, {'bugün itibarıyla' if len(satirlar) < 12 else 'yıl sonunda'} "
           f"kasada <b>{para(son['toplam'])}</b> bulunuyor.")
    r.h2("1. Ay ay gelir ve gider")
    r.tablo(["Ay", "İstenen (aidat + ek)", "Toplanan", "Harcanan", "Ay sonu kasa"], satirlar, ["", "r", "r", "r", "r"],
            [0.16, 0.22, 0.2, 0.2, 0.22], ["Toplam", "", para(top_t), para(top_h), ""])
    kat = {}
    for g in v.d["giderler"]:
        if g["tarih"][:4] == str(yil):
            kat[g["kategori"]] = kat.get(g["kategori"], 0) + g["tutar"]
    r.h2("2. Paranın harcandığı yerler")
    if kat:
        r.tablo(["Kalem", "Tutar", "Pay"], [[esc(k), para(kat[k]), f"%{round(kat[k] / top_h * 100)}"] for k in sorted(kat, key=lambda k: -kat[k])],
                ["", "r", "r"], [0.6, 0.25, 0.15], ["Toplam", para(top_h), "%100"])
    else:
        r.p("Harcama yok.", "not")
    ekler = [e for e in v.d["ekler"] if e["donem"][:4] == str(yil)]
    n = 3
    if ekler:
        r.h2(f"{n}. Ek toplamalar")
        n += 1
        r.tablo(["Ay", "Ne için", "Toplam"], [[donem_adi(e["donem"]), esc(e["baslik"]) + (f"<br/><font color='{GRI}'>{esc(e['aciklama'])}</font>" if e.get("aciklama") else ""),
                                              para(e["toplam"])] for e in ekler], ["", "", "r"], [0.18, 0.6, 0.22])
    if v.ayar("rapor_borc_tablosu", True):
        r.h2(f"{n}. Daireler")
        sat = []
        for d in v.tum_daireler():
            ist = sum(b["tutar"] for b in v.d["borclar"] if b["daire_id"] == d["id"] and b["donem"][:4] == str(yil))
            if not d.get("aktif") and not ist:
                continue
            od = sum(x["tutar"] for x in v.d["odemeler"] if x["daire_id"] == d["id"] and x["tarih"][:4] == str(yil))
            sat.append([f"Daire {esc(d['no'])}", esc(v.oturan_adi(d)), para(ist), para(od), durum_html(v.hesap(d["id"])["toplam"])])
        r.tablo(["Daire", "Oturan", "Yıl içinde istenen", "Yıl içinde ödenen", "Güncel durum"], sat, ["", "", "r", "r", "r"],
                [0.12, 0.26, 0.19, 0.19, 0.24])
    r.kaydet(yol)


def rapor_dokum(v, daire_id, yol):
    d, h = v.bul("daireler", daire_id), v.hesap(daire_id)
    r = Rapor(v, f"{v.ayar('apartman_adi', 'Apartman')} – Daire {d['no']} Hesap Dökümü", f"{tarih_yaz(bugun())} itibarıyla")
    if h["toplam"] < -0.004:
        durum = k_(f"{para(-h['toplam'])} borç") + (f" ({esc(', '.join(b['baslik'] for b in h['tum_acik']))})" if h["tum_acik"] else "")
    elif h["toplam"] > 0.004:
        durum = y_(f"+{para(h['toplam'])} ön ödeme") + " – sonraki aidatlar bu tutardan düşülecek."
    else:
        durum = y_("Borç yok")
    r.kutu(f"<b>Oturan:</b> {esc(v.oturan_adi(d))}<br/><b>Güncel durum:</b> {durum}")
    for e in h["eskiler"]:
        r.p(f"Eski oturan {esc(e['ad'])}: {esc(v.durum_yazi(e['bakiye']))}", "not")
    r.h2("Hesap hareketleri")
    r.tablo(["Tarih", "Açıklama", "Kişi", "Borç", "Ödeme", "Bakiye"],
            [[tarih_yaz(x["tarih"]), esc(x["ad"]), esc(v.odeyen_adi(x["kisi"], d)), para(-x["tutar"]) if x["tutar"] < 0 else "",
              para(x["tutar"]) if x["tutar"] > 0 else "", (k_ if x["bakiye"] < -0.004 else y_)(("+" if x["bakiye"] > 0 else "") + para(x["bakiye"]))]
             for x in v.hareketler(daire_id)],
            ["", "", "", "r", "r", "r"], [0.13, 0.3, 0.17, 0.13, 0.13, 0.14])
    r.p("Bakiye: eksi (–) borcu, artı (+) peşin ödenmiş ve sonraki aylardan düşülecek tutarı gösterir.", "not")
    r.kaydet(yol)


def rapor_borclar(v, yol):
    satirlar, toplam = [], 0.0
    for d in v.aktif_daireler():
        h = v.hesap(d["id"])
        if h["toplam"] < 0:
            toplam -= h["toplam"]
        satirlar.append([f"Daire {esc(d['no'])}", esc(v.oturan_adi(d)), esc(", ".join(b["baslik"] for b in h["tum_acik"])) or "-", durum_html(h["toplam"])])
    r = Rapor(v, f"{v.ayar('apartman_adi', 'Apartman')} – Aidat Borç Durumu", tarih_yaz(bugun()))
    r.kutu(f"{tarih_yaz(bugun())} itibarıyla dairelerin toplam ödenmemiş borcu <b>{para(toplam)}</b>.")
    r.tablo(["Daire", "Oturan", "Ödenmeyenler", "Durum"], satirlar, ["", "", "", "r"], [0.12, 0.25, 0.38, 0.25])
    r.kaydet(yol)


def rapor_makbuz(v, odeme_id, yol):
    o = v.bul("odemeler", odeme_id)
    d, h = v.bul("daireler", o["daire_id"]), v.hesap(o["daire_id"])
    r = Rapor(v, f"{v.ayar('apartman_adi', 'Apartman')} – Tahsilat Makbuzu", v.ayar("adres"))
    sat = [["Makbuz no", o["id"].upper()], ["Tarih", tarih_yaz(o["tarih"])], ["Daire", f"Daire {esc(d['no'])}"],
           ["Ödeyen", esc(v.odeyen_adi(o.get("sakin_id"), d))], ["Ödeme şekli", esc(o["yontem"])]]
    if o.get("aciklama"):
        sat.append(["Açıklama", esc(o["aciklama"])])
    r.tablo(["", ""], sat, ["", "r"], [0.5, 0.5], ["Alınan tutar", para(o["tutar"])])
    r.kutu(f"Yukarıdaki tutar {esc(v.ayar('apartman_adi', 'apartman'))} aidat / ortak gider ödemesi olarak teslim alınmıştır.<br/>"
           f"Güncel hesap durumu: <b>{esc(v.durum_yazi(h['bakiye']))}</b>")
    r.ogeler.append(Spacer(1, 30))
    r.p(f"Teslim alan: {esc(v.ayar('yonetici_ad'))}<br/><font color='{GRI}'>İmza</font>")
    r.kaydet(yol)


def rapor_ek(v, ek_id, yol):
    e = v.bul("ekler", ek_id)
    bl = [b for b in v.d["borclar"] if b.get("ek_id") == ek_id]
    r = Rapor(v, f"{v.ayar('apartman_adi', 'Apartman')} – Ek Toplama Duyurusu", donem_adi(e["donem"]))
    r.kutu(f"<b>{esc(e['baslik'])}</b> için toplam <b>{para(e['toplam'])}</b> gerekmektedir. Bu tutar {len(bl)} daireye "
           + ("pay oranına göre" if e.get("dagitim") == "oran" else "eşit olarak") + f" bölünmüş ve {donem_adi(e['donem'])} ayında hesaplara yazılmıştır."
           + (f"<br/><br/>{esc(e['aciklama'])}" if e.get("aciklama") else ""))
    r.tablo(["Daire", "Oturan", "Payı"], [[f"Daire {esc(v.bul('daireler', b['daire_id'])['no'])}", esc(v.odeyen_adi(b.get('sakin_id'), v.bul('daireler', b['daire_id']))),
                                          para(b["tutar"])] for b in bl], ["", "", "r"], [0.2, 0.55, 0.25], ["Toplam", "", para(e["toplam"])])
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
        if self.v is None:
            self.destroy()
            return
        if not self.v.kurulu:
            if not self._kurulum():
                self.destroy()
                return
        elif not self._giris():
            self.destroy()
            return
        self.geometry("1180x780")
        self.minsize(1040, 700)
        self.secili_donem = bu_donem()
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
        f.etiket(f"🏢 {self.v.ayar('apartman_adi', 'Apartman')}")
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
        f = Form(self, "Apartman Yönetimi – İlk kurulum", 560)
        f.etiket("🏢 İlk kurulum")
        f.not_("Bu bilgilerin hepsini sonradan Ayarlar'dan değiştirebilirsiniz.")
        ad = f.giris("Apartman adı")
        adres = f.giris("Adres")
        yon = f.giris("Yönetici adı soyadı")
        tel = f.giris("Yönetici telefonu")
        iban = f.giris("Aidatın yatırılacağı IBAN")
        iban_ad = f.giris("IBAN hesap sahibi")
        daire = f.giris("Daire sayısı", "8", sag=True)
        aidat = f.giris("Aylık aidat (TL, her daire)", "", sag=True)
        aylar = [donem_kaydir(bu_donem(), i) for i in range(-12, 4)]
        bas = f.secim("Aidat hangi aydan başlıyor?", [donem_adi(a) for a in aylar], donem_adi(bu_donem()))
        gun = f.giris("Son ödeme günü (her ayın kaçı)", "10", sag=True)
        s1 = f.giris("Program şifresi (en az 4 karakter)", show="•")
        s2 = f.giris("Şifre (tekrar)", show="•")
        sonuc = {"tamam": False}

        def kaydet():
            try:
                ds = int(sayi_al(daire, "Daire sayısı", ebeveyn=f))
                a = sayi_al(aidat, "Aylık aidat", ebeveyn=f)
            except ValueError:
                return
            if not ad.get().strip():
                return messagebox.showwarning("Eksik", "Apartman adını yazın.", parent=f)
            if not 1 <= ds <= 200:
                return messagebox.showwarning("Eksik", "Daire sayısı 1 ile 200 arasında olmalı.", parent=f)
            if len(s1.get()) < 4 or s1.get() != s2.get():
                return messagebox.showwarning("Şifre", "Şifreler aynı değil ya da çok kısa (en az 4 karakter).", parent=f)
            self.v.kurulum({"apartman_adi": ad.get().strip(), "adres": adres.get().strip(), "yonetici_ad": yon.get().strip(),
                            "yonetici_tel": tel.get().strip(), "iban": iban.get().strip(), "iban_ad": iban_ad.get().strip(),
                            "daire_sayisi": ds, "aidat": a, "baslangic_donem": aylar[[donem_adi(x) for x in aylar].index(bas.get())],
                            "son_odeme_gunu": gun.get().strip() or "10", "sifre": s1.get()})
            sonuc["tamam"] = True
            f.destroy()

        f.dugmeler(("Kurulumu tamamla", kaydet, MAVI))
        f.protocol("WM_DELETE_WINDOW", f.destroy)
        f.ac()
        self.wait_window(f)
        return sonuc["tamam"]

    def otomatik(self):
        yazilan = self.v.aidatlari_yaz()
        if yazilan:
            self.durum(", ".join(donem_adi(m) for m in yazilan) + " aidatları dairelere yazıldı.")
        self.ciz()

    def _senkron(self):
        try:
            if self.v.yenile():
                self.v.aidatlari_yaz()
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
        s.configure("Baslik.TLabel", font=(fa, 14, "bold"), foreground=MAVI)
        s.configure("Not.TLabel", font=(fa, 9), foreground=GRI)
        s.configure("Sonuc.TLabel", font=(fa, 11, "bold"))
        s.configure("Buyuk.TLabel", font=(fa, 20, "bold"))
        s.configure("BuyukK.TLabel", font=(fa, 16, "bold"), foreground=KIRMIZI)
        s.configure("BuyukY.TLabel", font=(fa, 16, "bold"), foreground=YESIL)
        s.configure("BuyukG.TLabel", font=(fa, 16, "bold"), foreground=GRI)
        s.configure("Uyari.TLabel", foreground=TURUNCU, font=(fa, 10, "bold"))
        s.configure("TLabelframe.Label", font=(fa, 11, "bold"), foreground=MAVI)
        s.configure("TButton", font=(fa, 10), padding=(8, 4))
        s.configure("Treeview", rowheight=26, font=(fa, 10))
        s.configure("Treeview.Heading", font=(fa, 10, "bold"))

    def renkli(self, ust, metin, renk, komut):
        koyu = {MAVI: "#174a94", YESIL: "#166b2e", KIRMIZI: "#a61e1e"}.get(renk, renk)
        return tk.Button(ust, text=metin, bg=renk, fg="white", activebackground=koyu, activeforeground="white", relief="flat",
                         font=(self.fa, 10, "bold"), padx=12, pady=5, cursor="hand2", command=komut)

    def tablo(self, ust, sutunlar, yukseklik=8, secim="browse"):
        cer = ttk.Frame(ust)
        t = ttk.Treeview(cer, columns=[s[0] for s in sutunlar], show="headings", height=yukseklik, selectmode=secim)
        for a, b, g, h in sutunlar:
            t.heading(a, text=b)
            t.column(a, width=g, anchor=h, stretch=True)
        kay = ttk.Scrollbar(cer, orient="vertical", command=t.yview)
        t.configure(yscrollcommand=kay.set)
        t.pack(side="left", fill="both", expand=True)
        kay.pack(side="right", fill="y")
        t.tag_configure("borc", foreground=KIRMIZI)
        t.tag_configure("alacak", foreground=YESIL)
        t.tag_configure("soluk", foreground=GRI)
        return cer, t

    def durum(self, mesaj):
        self.v_durum.set(mesaj)

    def _arayuz(self):
        ust = tk.Frame(self, bg=MAVI)
        ust.pack(fill="x")
        self.v_baslik = tk.StringVar()
        tk.Label(ust, textvariable=self.v_baslik, bg=MAVI, fg="white", font=(self.fa, 15, "bold"), padx=16, pady=10).pack(side="left")
        tk.Button(ust, text="↻ Yenile", command=self.yenile, bg="#3a73cc", fg="white", relief="flat", font=(self.fa, 10), padx=10,
                  activebackground="#174a94", activeforeground="white").pack(side="right", padx=12, pady=8)
        self.defter = ttk.Notebook(self)
        self.defter.pack(fill="both", expand=True, padx=10, pady=(8, 0))
        self.sayfalar = {}
        for anahtar, ad in (("ozet", "  🏠 Özet  "), ("daireler", "  🚪 Daireler  "), ("giderler", "  🧾 Giderler  "),
                            ("aidat", "  💰 Aidat ve Ek Toplama  "), ("raporlar", "  📄 Raporlar  "), ("ayarlar", "  ⚙ Ayarlar  ")):
            f = ttk.Frame(self.defter, padding=12)
            self.defter.add(f, text=ad)
            self.sayfalar[anahtar] = f
        self.v_durum = tk.StringVar()
        ttk.Label(self, textvariable=self.v_durum, foreground=YESIL, padding=(14, 4)).pack(fill="x")
        self._ozet_kur()
        self._daireler_kur()
        self._giderler_kur()
        self._aidat_kur()
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
        self.v_baslik.set(self.v.ayar("apartman_adi", UYGULAMA_ADI))
        self.ozet_ciz()
        self.daireler_ciz()
        self.giderler_ciz()
        self.aidat_ciz()

    # ------------------------------------------------------------ özet
    def _ozet_kur(self):
        p = self.sayfalar["ozet"]
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        p.rowconfigure(3, weight=1)
        self.f_uyari = ttk.Frame(p)
        self.f_uyari.grid(row=0, column=0, columnspan=2, sticky="we")
        k = ttk.LabelFrame(p, text=" Kasa ", padding=12)
        k.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
        self.v_kasa, self.v_kasa_alt = tk.StringVar(), tk.StringVar()
        self.l_kasa = ttk.Label(k, textvariable=self.v_kasa, style="Buyuk.TLabel")
        self.l_kasa.pack(anchor="w")
        ttk.Label(k, textvariable=self.v_kasa_alt).pack(anchor="w")
        a = ttk.LabelFrame(p, text=" Bu ay ", padding=12)
        a.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
        self.v_ay_baslik, self.v_ay1, self.v_ay2 = tk.StringVar(), tk.StringVar(), tk.StringVar()
        ttk.Label(a, textvariable=self.v_ay_baslik, style="Sonuc.TLabel").pack(anchor="w")
        self.pb = ttk.Progressbar(a, maximum=100, length=300)
        self.pb.pack(fill="x", pady=6)
        ttk.Label(a, textvariable=self.v_ay1).pack(anchor="w")
        ttk.Label(a, textvariable=self.v_ay2, style="Not.TLabel").pack(anchor="w")
        dug = ttk.Frame(p)
        dug.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.renkli(dug, "💰 Ödeme al", MAVI, lambda: self.odeme_formu()).pack(side="left")
        self.renkli(dug, "🧾 Gider ekle", KIRMIZI, lambda: self.gider_formu()).pack(side="left", padx=8)
        self.renkli(dug, "➕ Ek toplama", YESIL, lambda: self.ek_formu()).pack(side="left")
        b = ttk.LabelFrame(p, text=" Borçlu daireler (çift tıklayınca daire açılır) ", padding=8)
        b.grid(row=3, column=0, sticky="nsew", padx=(0, 6))
        cer, self.t_borclu = self.tablo(b, (("daire", "Daire", 70, "w"), ("oturan", "Oturan", 160, "w"),
                                            ("ne", "Ödenmeyenler", 220, "w"), ("tutar", "Borç", 110, "e")))
        cer.pack(fill="both", expand=True)
        self.t_borclu.bind("<Double-1>", lambda _e: self._daireye_git(self.t_borclu))
        s = ttk.LabelFrame(p, text=" Son hareketler ", padding=8)
        s.grid(row=3, column=1, sticky="nsew", padx=(6, 0))
        cer, self.t_son = self.tablo(s, (("tarih", "Tarih", 90, "w"), ("ne", "Hareket", 300, "w"), ("tutar", "Tutar", 110, "e")))
        cer.pack(fill="both", expand=True)

    def ozet_ciz(self):
        v = self.v
        for w in self.f_uyari.winfo_children():
            w.destroy()
        for z in v.bekleyen_duzenliler():
            f = ttk.Frame(self.f_uyari, padding=(0, 0, 0, 6))
            f.pack(fill="x")
            ttk.Label(f, text=f"⚠ Bu ayın düzenli gideri henüz eklenmedi: {z['kategori']} – {para_kisa(z['tutar'])}", style="Uyari.TLabel").pack(side="left")
            ttk.Button(f, text="Gider olarak ekle", command=lambda z=z: self.duzenli_ekle(z)).pack(side="left", padx=10)
        k = v.kasa()
        self.v_kasa.set(para(k["toplam"]))
        self.v_kasa_alt.set(f"🏦 Banka: {para(k['banka'])}     💵 Nakit: {para(k['nakit'])}")
        m = bu_donem()
        t, o = v.donem_tahsilat(m), v.donem_ozeti(m)
        self.v_ay_baslik.set(f"{donem_adi(m)} – dairelerden istenen {para_kisa(t['istenen'])}")
        self.pb["value"] = (t["odenen"] / t["istenen"] * 100) if t["istenen"] else 0
        self.v_ay1.set(f"Ödenen: {para_kisa(t['odenen'])}     Kalan: {para_kisa(t['kalan'])}")
        self.v_ay2.set(f"Bu ay kasaya giren: {para_kisa(o['toplanan'])}  ·  Bu ay harcanan: {para_kisa(o['harcanan'])}")
        self.t_borclu.delete(*self.t_borclu.get_children())
        borclular = [(d, v.hesap(d["id"])) for d in v.aktif_daireler()]
        for d, h in sorted([x for x in borclular if x[1]["bakiye"] < -0.004], key=lambda x: x[1]["bakiye"]):
            self.t_borclu.insert("", "end", iid=d["id"], tags=("borc",),
                                 values=(f"Daire {d['no']}", v.oturan_adi(d), ", ".join(b["baslik"] for b in h["acik"]), para(-h["bakiye"])))
        self.t_son.delete(*self.t_son.get_children())
        l = [(o["tarih"], f"💰 Daire {(v.bul('daireler', o['daire_id']) or {'no': '?'})['no']} – {v.odeyen_adi(o.get('sakin_id'), v.bul('daireler', o['daire_id']))} ({o['yontem']})",
              o["tutar"]) for o in v.d["odemeler"]]
        l += [(g["tarih"], f"🧾 {g['kategori']}" + (f" – {g['aciklama']}" if g.get("aciklama") else ""), -g["tutar"]) for g in v.d["giderler"]]
        for tarih, ne, tutar in sorted(l, key=lambda x: x[0], reverse=True)[:40]:
            self.t_son.insert("", "end", values=(tarih_yaz(tarih), ne, ("+" if tutar > 0 else "") + para_kisa(tutar)),
                              tags=("alacak" if tutar > 0 else "borc",))

    def _daireye_git(self, t):
        s = t.selection()
        if s:
            self.defter.select(self.sayfalar["daireler"])
            self.t_daire.selection_set(s[0])
            self.t_daire.see(s[0])

    # ------------------------------------------------------------ daireler
    def _daireler_kur(self):
        p = self.sayfalar["daireler"]
        p.columnconfigure(0, weight=2)
        p.columnconfigure(1, weight=3)
        p.rowconfigure(0, weight=1)
        sol = ttk.Frame(p)
        sol.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        sol.rowconfigure(0, weight=1)
        sol.columnconfigure(0, weight=1)
        cer, self.t_daire = self.tablo(sol, (("no", "Daire", 64, "w"), ("oturan", "Oturan", 150, "w"), ("tip", "Durum", 70, "w"),
                                             ("bakiye", "Hesap", 140, "e")), yukseklik=16)
        cer.grid(row=0, column=0, sticky="nsew")
        self.t_daire.bind("<<TreeviewSelect>>", lambda _e: self.daire_detay_ciz())
        d = ttk.Frame(sol)
        d.grid(row=1, column=0, sticky="we", pady=(8, 0))
        ttk.Button(d, text="➕ Daire ekle", command=self.daire_formu).pack(side="left")
        self.v_pasif = tk.BooleanVar(value=False)
        ttk.Checkbutton(d, text="Çıkarılan daireleri de göster", variable=self.v_pasif, command=self.daireler_ciz).pack(side="left", padx=10)

        sag = ttk.Frame(p)
        sag.grid(row=0, column=1, sticky="nsew")
        sag.columnconfigure(0, weight=1)
        sag.rowconfigure(7, weight=1)
        self.v_d_baslik, self.v_d_oturan, self.v_d_durum, self.v_d_acik, self.v_d_eski = (tk.StringVar() for _ in range(5))
        ttk.Label(sag, textvariable=self.v_d_baslik, style="Baslik.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(sag, textvariable=self.v_d_oturan).grid(row=1, column=0, sticky="w")
        self.l_d_durum = ttk.Label(sag, textvariable=self.v_d_durum, style="BuyukG.TLabel")
        self.l_d_durum.grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(sag, textvariable=self.v_d_acik, wraplength=560, justify="left").grid(row=3, column=0, sticky="w")
        ttk.Label(sag, textvariable=self.v_d_eski, style="Uyari.TLabel", wraplength=560, justify="left").grid(row=4, column=0, sticky="w")
        dug = ttk.Frame(sag)
        dug.grid(row=5, column=0, sticky="we", pady=(8, 4))
        self.renkli(dug, "💰 Ödeme al", MAVI, lambda: self.odeme_formu(self._secili_daire())).pack(side="left")
        self.renkli(dug, "💬 WhatsApp hatırlat", YESIL, self.daire_whatsapp).pack(side="left", padx=6)
        ttk.Button(dug, text="📄 Hesap dökümü (PDF)", command=self.daire_dokum).pack(side="left")
        dug2 = ttk.Frame(sag)
        dug2.grid(row=6, column=0, sticky="we", pady=(0, 8))
        for metin, komut in (("🔁 Kiracı değiştir / oturan ekle", self.sakin_formu), ("✏ Oturan bilgisi", self.sakin_duzenle),
                             ("⚙ Daire bilgisi", lambda: self.daire_formu(self._secili_daire())), ("🗑 Daireyi çıkar", self.daire_cikar)):
            ttk.Button(dug2, text=metin, command=komut).pack(side="left", padx=(0, 4))
        cer, self.t_hareket = self.tablo(sag, (("tarih", "Tarih", 90, "w"), ("ad", "Açıklama", 230, "w"), ("kisi", "Kişi", 130, "w"),
                                               ("tutar", "Tutar", 100, "e"), ("bakiye", "Bakiye", 110, "e")), yukseklik=12)
        cer.grid(row=7, column=0, sticky="nsew")
        self.t_hareket.bind("<Double-1>", lambda _e: self._hareket_duzenle())
        ttk.Label(sag, text="Ödeme satırına çift tıklayınca ödeme düzenlenir / silinir. Bakiye: eksi borç, artı ön ödeme.",
                  style="Not.TLabel").grid(row=8, column=0, sticky="w", pady=(4, 0))

    def _secili_daire(self):
        s = self.t_daire.selection() if hasattr(self, "t_daire") else ()
        return s[0] if s else None

    def daireler_ciz(self):
        v, sec = self.v, self._secili_daire()
        self.t_daire.delete(*self.t_daire.get_children())
        for d in (v.tum_daireler() if self.v_pasif.get() else v.aktif_daireler()):
            h, s = v.hesap(d["id"]), v.aktif_sakin(d["id"])
            b = h["bakiye"] if d.get("aktif") else h["toplam"]
            etiket = "borc" if b < -0.004 else ("alacak" if b > 0.004 else "")
            if not d.get("aktif"):
                etiket = "soluk"
            self.t_daire.insert("", "end", iid=d["id"], tags=(etiket,), values=(
                f"Daire {d['no']}", v.oturan_adi(d) + (" ⚠" if h["eskiler"] else ""),
                ("Çıkarıldı" if not d.get("aktif") else (s["tip"] if s else "Boş")), v.durum_yazi(b)))
        if sec and self.t_daire.exists(sec):
            self.t_daire.selection_set(sec)
        elif self.t_daire.get_children():
            self.t_daire.selection_set(self.t_daire.get_children()[0])
        self.daire_detay_ciz()

    def daire_detay_ciz(self):
        v, i = self.v, self._secili_daire()
        self.t_hareket.delete(*self.t_hareket.get_children())
        if not i:
            for x in (self.v_d_baslik, self.v_d_oturan, self.v_d_durum, self.v_d_acik, self.v_d_eski):
                x.set("")
            return
        d, h, s = v.bul("daireler", i), v.hesap(i), v.aktif_sakin(i)
        self.v_d_baslik.set(f"Daire {d['no']}" + (f" · {d['kat']}" if d.get("kat") else "") + ("" if d.get("aktif") else " (çıkarıldı)"))
        tel = v.oturan_tel(d)
        self.v_d_oturan.set((f"{s['tip']}: " if s else "") + v.oturan_adi(d) + (f"   ☎ {tel}" if tel else "") +
                            (f"   ·   Ev sahibi: {d['ev_sahibi_ad']}" if s and d.get("ev_sahibi_ad") else ""))
        b = h["bakiye"]
        self.v_d_durum.set(v.durum_yazi(b))
        self.l_d_durum.configure(style="BuyukK.TLabel" if b < -0.004 else ("BuyukY.TLabel" if b > 0.004 else "BuyukG.TLabel"))
        acik = ""
        if h["acik"]:
            acik = "Ödenmemiş: " + ", ".join(x["baslik"] + (f" (kalan {para_kisa(x['kalan'])})" if x["kalan"] < x["tutar"] else "") for x in h["acik"])
        elif b > 0.004:
            a = v.aidat_tutari(bu_donem(), d)
            if a:
                acik = f"Ön ödeme yaklaşık {int(b // a)} aylık aidata yetiyor; her ay aidat bundan düşülür."
        self.v_d_acik.set(acik)
        self.v_d_eski.set("\n".join(f"Eski oturan {e['ad']}: {v.durum_yazi(e['bakiye'])}" for e in h["eskiler"]))
        for x in reversed(v.hareketler(i)):
            self.t_hareket.insert("", "end", iid=(x["odeme"]["id"] if "odeme" in x else "b-" + x["borc"]["id"]),
                                  tags=("alacak" if x["tutar"] > 0 else "borc",),
                                  values=(tarih_yaz(x["tarih"]), x["ad"], v.odeyen_adi(x["kisi"], d),
                                          ("+" if x["tutar"] > 0 else "") + para_kisa(x["tutar"]), ("+" if x["bakiye"] > 0 else "") + para_kisa(x["bakiye"])))

    def _hareket_duzenle(self):
        s = self.t_hareket.selection()
        if s and not s[0].startswith("b-"):
            self.odeme_formu(odeme_id=s[0])

    def _daire_gerekli(self):
        i = self._secili_daire()
        if not i:
            messagebox.showinfo("Daire", "Önce soldaki listeden bir daire seçin.", parent=self)
        return i

    def daire_whatsapp(self):
        i = self._daire_gerekli()
        if not i:
            return
        d = self.v.bul("daireler", i)
        self.mesaj_penceresi(f"Daire {d['no']} – WhatsApp mesajı", self.v.hatirlatma_metni(d), self.v.oturan_tel(d))

    def mesaj_penceresi(self, baslik, metin, tel=None):
        f = Form(self, baslik, 560)
        f.not_("Mesajı düzenleyebilirsiniz. “WhatsApp'ta aç” WhatsApp'ı " + ("bu kişiyle" if tel else "kişi seçerek") + " açar.")
        t = f.metin("Mesaj", metin, 14)

        def kopyala():
            self.clipboard_clear()
            self.clipboard_append(t.get("1.0", "end").strip())
            self.durum("Mesaj kopyalandı.")

        f.dugmeler(("💬 WhatsApp'ta aç", lambda: (wa_ac(tel or "", t.get("1.0", "end").strip()), f.destroy()), YESIL),
                   ("📋 Kopyala", kopyala, None), ("Kapat", f.destroy, None))
        if not tel:
            f.not_("Telefon numarası kayıtlı değil; WhatsApp açılınca kişiyi ya da grubu siz seçersiniz.")
        f.ac()

    def daire_dokum(self):
        i = self._daire_gerekli()
        if i:
            d = self.v.bul("daireler", i)
            self.pdf(lambda y: rapor_dokum(self.v, i, y), f"Daire {d['no']} Hesap Dokumu {bugun()}")

    def daire_formu(self, daire_id=None):
        v = self.v
        d = v.bul("daireler", daire_id) if daire_id else None
        yeni_no = str(int(max([sayi_oku(x["no"]) or 0 for x in v.aktif_daireler()] + [0])) + 1)
        f = Form(self, f"Daire {d['no']} bilgisi" if d else "Yeni daire")
        no = f.giris("Daire numarası / adı", d["no"] if d else yeni_no)
        kat = f.giris("Kat (isteğe bağlı)", d.get("kat", "") if d else "")
        sahip = f.giris("Ev sahibi adı", d.get("ev_sahibi_ad", "") if d else "")
        sahip_tel = f.giris("Ev sahibi telefonu", d.get("ev_sahibi_tel", "") if d else "")
        oz = f.giris("Bu daireye özel aylık aidat (TL)", "" if not d or d.get("ozel_aidat") is None else sayi_yaz(d["ozel_aidat"]), sag=True)
        f.not_(f"Boş bırakılırsa normal aidat ({para_kisa(v.tarife_tutari(bu_donem()))}) uygulanır. 0 yazılırsa bu daireye aidat yazılmaz.")
        pay = f.giris("Ek toplamalarda pay oranı", sayi_yaz(d.get("pay_orani", 1)) if d else "1", sag=True)
        f.not_("Ek toplama \"pay oranına göre\" bölünürse kullanılır. Hepsi 1 ise eşit bölünür; 0,5 yazılan daire yarım pay öder.")
        if not d:
            aylar = [donem_kaydir(bu_donem(), i) for i in range(-12, 4)]
            bas = f.secim("Aidat hangi aydan başlasın?", [donem_adi(a) for a in aylar], donem_adi(bu_donem()))
        not_ = f.metin("Not", d.get("not", "") if d else "", 3)

        def kaydet():
            try:
                ozel = sayi_al(oz, "Özel aidat", bos_olabilir=True, ebeveyn=f)
                p = sayi_al(pay, "Pay oranı", bos_olabilir=True, ebeveyn=f)
            except ValueError:
                return
            if not no.get().strip():
                return messagebox.showwarning("Eksik", "Daire numarasını yazın.", parent=f)
            k = dict(d or {}, no=no.get().strip(), kat=kat.get().strip(), ev_sahibi_ad=sahip.get().strip(), ev_sahibi_tel=sahip_tel.get().strip(),
                     ozel_aidat=ozel, pay_orani=1 if p is None else p, not_metni=None, aktif=d["aktif"] if d else True)
            k.pop("not_metni")
            k["not"] = not_.get("1.0", "end").strip()
            if not d:
                k["baslangic_donem"] = aylar[[donem_adi(x) for x in aylar].index(bas.get())]
            k = v.yaz("daireler", k, False)
            if d and d.get("ozel_aidat") != ozel:
                for b in [b for b in v.d["borclar"] if b["daire_id"] == d["id"] and b["tur"] == "Aidat" and b["donem"] >= bu_donem()]:
                    v.yaz("borclar", dict(b, tutar=v.aidat_tutari(b["donem"], k)), False)
            v.kaydet()
            f.destroy()
            self.otomatik()
            self.t_daire.selection_set(k["id"])
            self.durum("Daire kaydedildi.")

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def daire_cikar(self):
        v, i = self.v, self._daire_gerekli()
        if not i:
            return
        d, h = v.bul("daireler", i), v.hesap(i)
        if not d.get("aktif"):
            if messagebox.askyesno("Daire", f"Daire {d['no']} yeniden listeye eklensin mi?", parent=self):
                v.yaz("daireler", dict(d, aktif=True, baslangic_donem=bu_donem()))
                self.otomatik()
            return
        if not any(o["daire_id"] == i for o in v.d["odemeler"]):
            if not messagebox.askyesno("Daire sil", f"Daire {d['no']} tamamen silinsin mi?\n\nBu daireden hiç ödeme alınmamış; daire, oturan bilgisi "
                                       "ve yazılmış aidat / ek toplama payları silinir.", parent=self):
                return
            for s in [s for s in v.d["sakinler"] if s["daire_id"] == i]:
                v.sil("sakinler", s["id"], False)
            for b in [b for b in v.d["borclar"] if b["daire_id"] == i]:
                v.sil("borclar", b["id"], False)
            v.sil("daireler", i)
        else:
            if not messagebox.askyesno("Daire çıkar", f"Daire {d['no']} listeden çıkarılsın mı?\n\nGeçmiş kayıtları silinmez, raporlarda görünmeye "
                                       "devam eder. Bundan sonra aidat yazılmaz." +
                                       (f"\n\nDikkat: hesabında {v.durum_yazi(h['toplam'])} var." if abs(h["toplam"]) > 0.004 else ""), parent=self):
                return
            v.yaz("daireler", dict(d, aktif=False))
        self.ciz()

    def sakin_formu(self):
        v, i = self.v, self._daire_gerekli()
        if not i:
            return
        d, eski = v.bul("daireler", i), v.aktif_sakin(i)
        f = Form(self, f"Daire {d['no']} – " + ("Kiracı değiştir" if eski else "Oturan ekle"))
        if eski:
            f.not_(f"{eski['ad']} çıkış yapmış olarak kaydedilecek. Eski hesabı (borç ya da ön ödeme) kendi adıyla ayrı görünmeye devam eder; yeni oturan temiz başlar.")
        tip = f.radyo("Oturan", ["Kiracı", "Ev sahibi", "Daire boş"], "Kiracı")
        ad = f.giris("Ad soyad")
        tel = f.giris("Telefon (WhatsApp)")
        tarih = f.giris("Taşınma tarihi (gg.aa.yyyy)", tarih_yaz(bugun()))
        if eski:
            aidat = f.onay("Bu ayın aidatı yeni oturana yazılsın", True)
            f.not_("İşaretli değilse bu ayın aidatı eski oturanın hesabında kalır.")
        else:
            aidat = f.onay("Bu daireye daha önce yazılmış (kimseye ait olmayan) borçlar da bu kişiye yazılsın", True)
            f.not_("Kurulumdan sonra ilk kez oturan ekliyorsanız işaretli bırakın. Daire gerçekten boş durduysa ve o aylar ev sahibine aitse işareti kaldırın.")

        def kaydet():
            t = tarih_oku(tarih.get())
            if not t:
                return messagebox.showwarning("Tarih", "Tarihi gg.aa.yyyy şeklinde yazın.", parent=f)
            if tip.get() != "Daire boş" and not ad.get().strip():
                return messagebox.showwarning("Eksik", "Ad soyad yazın.", parent=f)
            if eski:
                v.yaz("sakinler", dict(eski, cikis=t), False)
            yeni_id = ""
            if tip.get() != "Daire boş":
                yeni_id = v.yaz("sakinler", {"daire_id": i, "tip": tip.get(), "ad": ad.get().strip(), "tel": tel.get().strip(),
                                             "giris": t, "cikis": "", "not": ""}, False)["id"]
            if aidat.get():
                if eski:
                    tasinacak = [b for b in v.d["borclar"] if b["daire_id"] == i and b["tur"] == "Aidat" and b["donem"] >= t[:7]]
                else:
                    tasinacak = [b for b in v.d["borclar"] if b["daire_id"] == i and not b.get("sakin_id")]
                    for o in [o for o in v.d["odemeler"] if o["daire_id"] == i and not o.get("sakin_id")]:
                        v.yaz("odemeler", dict(o, sakin_id=yeni_id), False)
                for b in tasinacak:
                    v.yaz("borclar", dict(b, sakin_id=yeni_id), False)
            v.kaydet()
            f.destroy()
            self.ciz()
            self.durum("Kaydedildi.")

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def sakin_duzenle(self):
        v, i = self.v, self._daire_gerekli()
        if not i:
            return
        s = v.aktif_sakin(i)
        if not s:
            return messagebox.showinfo("Oturan", "Bu dairede kayıtlı oturan yok. “Kiracı değiştir / oturan ekle” ile ekleyin.", parent=self)
        f = Form(self, "Oturan bilgisi")
        ad = f.giris("Ad soyad", s["ad"])
        tel = f.giris("Telefon (WhatsApp)", s.get("tel", ""))
        tip = f.radyo("Durum", ["Kiracı", "Ev sahibi"], s.get("tip", "Kiracı"))
        n = f.metin("Not", s.get("not", ""), 3)

        def kaydet():
            if not ad.get().strip():
                return messagebox.showwarning("Eksik", "Ad soyad yazın.", parent=f)
            v.yaz("sakinler", dict(s, ad=ad.get().strip(), tel=tel.get().strip(), tip=tip.get(), **{"not": n.get("1.0", "end").strip()}))
            f.destroy()
            self.ciz()

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    # ------------------------------------------------------------ ödeme
    def odeme_formu(self, daire_id=None, odeme_id=None, sakin_id=None):
        v = self.v
        o = v.bul("odemeler", odeme_id) if odeme_id else None
        daire_id = o["daire_id"] if o else daire_id
        daireler = [d for d in v.tum_daireler() if d.get("aktif") or d["id"] == daire_id]
        adlar = [f"Daire {d['no']} – {v.oturan_adi(d)}" for d in daireler]
        f = Form(self, "Ödemeyi düzenle" if o else "Ödeme al", 560)
        secilen = next((n for n, d in enumerate(daireler) if d["id"] == daire_id), 0)
        dv = f.secim("Daire", adlar, adlar[secilen] if adlar else "")
        v_kisi = tk.StringVar()
        ttk.Label(f.govde, textvariable=v_kisi, style="Not.TLabel").grid(row=f.satir, column=1, columnspan=2, sticky="w")
        f.satir += 1
        tur = f.radyo("İşlem", ["Ödeme alındı", "Para iade edildi"], "Para iade edildi" if o and o["tutar"] < 0 else "Ödeme alındı")
        tutar = f.giris("Tutar (TL)", sayi_yaz(abs(o["tutar"])) if o else "", sag=True)
        hizli = ttk.Frame(f.govde)
        hizli.grid(row=f.satir, column=1, columnspan=2, sticky="w")
        f.satir += 1
        yontem = f.radyo("Nasıl?", ["Havale", "Nakit"], o["yontem"] if o else "Havale")
        tarih = f.giris("Tarih (gg.aa.yyyy)", tarih_yaz(o["tarih"] if o else bugun()))
        aciklama = f.giris("Açıklama (isteğe bağlı)", o.get("aciklama", "") if o else "")
        kisi = {"id": o.get("sakin_id", "") if o else (sakin_id or None)}

        def guncelle(*_):
            if not daireler:
                return
            d = daireler[adlar.index(dv.get())]
            h = v.hesap(d["id"])
            sid = kisi["id"] if kisi["id"] is not None and (o or sakin_id) else h["aktif_sakin_id"]
            eski = next((e for e in h["eskiler"] if e["sakin_id"] == sid), None)
            bakiye = eski["bakiye"] if eski else (h["bakiye"] if sid == h["aktif_sakin_id"] else 0)
            v_kisi.set(f"Ödeyen: {v.odeyen_adi(sid, d)}  ·  {v.durum_yazi(bakiye)}")
            for w in hizli.winfo_children():
                w.destroy()
            a = v.aidat_tutari(bu_donem(), d)
            if bakiye < -0.004:
                ttk.Button(hizli, text=f"Borcun tamamı {para_kisa(-bakiye)}", command=lambda: tutar.set(sayi_yaz(-bakiye))).pack(side="left", padx=(0, 4))
            if a:
                for n in (1, 3, 6, 12):
                    ttk.Button(hizli, text=f"{n} ay {para_kisa(a * n)}", command=lambda n=n: tutar.set(sayi_yaz(a * n))).pack(side="left", padx=(0, 4))
            if not o and not tutar.get() and bakiye < -0.004:
                tutar.set(sayi_yaz(-bakiye))

        dv.trace_add("write", lambda *_: (kisi.update(id=None), guncelle()))
        guncelle()

        def kaydet():
            try:
                t = sayi_al(tutar, "Tutar", ebeveyn=f)
            except ValueError:
                return
            tr = tarih_oku(tarih.get())
            if not t or not tr:
                return messagebox.showwarning("Eksik", "Tutarı ve tarihi (gg.aa.yyyy) yazın.", parent=f)
            d = daireler[adlar.index(dv.get())]
            sid = kisi["id"] if kisi["id"] is not None and (o or sakin_id) else v.hesap(d["id"])["aktif_sakin_id"]
            iade = tur.get() == "Para iade edildi"
            k = v.yaz("odemeler", dict(o or {}, daire_id=d["id"], sakin_id=sid, tarih=tr, tutar=-t if iade else t,
                                       yontem=yontem.get(), aciklama=aciklama.get().strip()))
            f.destroy()
            self.ciz()
            self.t_daire.selection_set(d["id"])
            if not o and not iade:
                self.odeme_sonrasi(k)
            else:
                self.durum("Ödeme kaydedildi.")

        def sil():
            if messagebox.askyesno("Sil", f"{para(abs(o['tutar']))} tutarındaki kayıt silinsin mi?", parent=f):
                v.sil("odemeler", o["id"])
                f.destroy()
                self.ciz()

        dug = [("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None)]
        if o:
            dug.insert(1, ("Bu ödemeyi sil", sil, KIRMIZI))
        f.dugmeler(*dug)
        f.ac()

    def odeme_sonrasi(self, o):
        v = self.v
        d, h = v.bul("daireler", o["daire_id"]), v.hesap(o["daire_id"])
        s = v.bul("sakinler", o.get("sakin_id")) if o.get("sakin_id") else None
        metin = (f"Merhaba{' ' + s['ad'] if s else ''},\n{v.ayar('apartman_adi')} Daire {d['no']} için {tarih_yaz(o['tarih'])} tarihli "
                 f"{para(o['tutar'])} ödemeniz alınmıştır. Teşekkür ederiz.\nGüncel durum: {v.durum_yazi(h['bakiye'])}\n\n{v.ayar('yonetici_ad', 'Apartman Yönetimi')}")
        f = Form(self, "Ödeme kaydedildi", 480)
        f.etiket(f"✅ {para(o['tutar'])}")
        ttk.Label(f.govde, text=f"Daire {d['no']} · {v.odeyen_adi(o.get('sakin_id'), d)}\nGüncel durum: {v.durum_yazi(h['bakiye'])}").grid(
            row=f.satir, column=0, columnspan=3, sticky="w")
        f.satir += 1
        f.dugmeler(("💬 Teşekkür mesajı", lambda: (f.destroy(), self.mesaj_penceresi("Teşekkür mesajı", metin, v.oturan_tel(d))), YESIL),
                   ("🧾 Makbuz (PDF)", lambda: self.pdf(lambda y: rapor_makbuz(v, o["id"], y), f"Makbuz Daire {d['no']} {o['tarih']}"), None),
                   ("Tamam", f.destroy, None))
        f.ac()

    # ------------------------------------------------------------ giderler
    def _giderler_kur(self):
        p = self.sayfalar["giderler"]
        p.columnconfigure(0, weight=3)
        p.columnconfigure(1, weight=2)
        p.rowconfigure(1, weight=1)
        ust = ttk.Frame(p)
        ust.grid(row=0, column=0, sticky="we", pady=(0, 8))
        ttk.Button(ust, text="‹", width=3, command=lambda: self._ay(-1)).pack(side="left")
        self.v_g_ay = tk.StringVar()
        ttk.Label(ust, textvariable=self.v_g_ay, style="Baslik.TLabel", width=16, anchor="center").pack(side="left", padx=6)
        ttk.Button(ust, text="›", width=3, command=lambda: self._ay(1)).pack(side="left")
        self.v_g_toplam = tk.StringVar()
        ttk.Label(ust, textvariable=self.v_g_toplam, style="BuyukK.TLabel").pack(side="right")
        cer, self.t_gider = self.tablo(p, (("tarih", "Tarih", 90, "w"), ("kat", "Ne için", 150, "w"), ("aciklama", "Açıklama", 260, "w"),
                                           ("odeme", "Nereden", 80, "w"), ("fis", "Fiş", 40, "center"), ("tutar", "Tutar", 110, "e")), yukseklik=14)
        cer.grid(row=1, column=0, sticky="nsew")
        self.t_gider.bind("<Double-1>", lambda _e: self.gider_formu(self._sec(self.t_gider)))
        d = ttk.Frame(p)
        d.grid(row=2, column=0, sticky="we", pady=(8, 0))
        self.renkli(d, "➕ Gider ekle", KIRMIZI, lambda: self.gider_formu()).pack(side="left")
        ttk.Button(d, text="✏ Düzenle / sil", command=lambda: self.gider_formu(self._sec(self.t_gider))).pack(side="left", padx=6)
        ttk.Button(d, text="📎 Fişi aç", command=self.fis_ac).pack(side="left")
        self.v_g_kat = tk.StringVar()
        ttk.Label(p, textvariable=self.v_g_kat, style="Not.TLabel", wraplength=600, justify="left").grid(row=3, column=0, sticky="w", pady=(6, 0))
        sag = ttk.LabelFrame(p, text=" Düzenli giderler (her ay hatırlatılır) ", padding=8)
        sag.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(12, 0))
        sag.rowconfigure(0, weight=1)
        sag.columnconfigure(0, weight=1)
        cer, self.t_duzenli = self.tablo(sag, (("kat", "Ne için", 140, "w"), ("gun", "Gün", 50, "center"), ("tutar", "Tutar", 100, "e"),
                                               ("aktif", "Durum", 80, "w")), yukseklik=10)
        cer.grid(row=0, column=0, sticky="nsew")
        self.t_duzenli.bind("<Double-1>", lambda _e: self.duzenli_formu(self._sec(self.t_duzenli)))
        d2 = ttk.Frame(sag)
        d2.grid(row=1, column=0, sticky="we", pady=(8, 0))
        ttk.Button(d2, text="➕ Ekle", command=lambda: self.duzenli_formu()).pack(side="left")
        ttk.Button(d2, text="✏ Düzenle / sil", command=lambda: self.duzenli_formu(self._sec(self.t_duzenli))).pack(side="left", padx=6)
        ttk.Label(sag, text="Temizlikçi, asansör bakımı gibi her ay tekrarlanan giderler. Zamanı gelince Özet ekranında “Gider olarak ekle” "
                  "düğmesi çıkar.", style="Not.TLabel", wraplength=380, justify="left").grid(row=2, column=0, sticky="w", pady=(6, 0))

    @staticmethod
    def _sec(t):
        s = t.selection()
        return s[0] if s else None

    def _ay(self, n):
        self.secili_donem = donem_kaydir(self.secili_donem, n)
        self.giderler_ciz()

    def giderler_ciz(self):
        v, m = self.v, self.secili_donem
        o = v.donem_ozeti(m)
        self.v_g_ay.set(donem_adi(m))
        self.v_g_toplam.set(f"Toplam: {para(o['harcanan'])}")
        self.t_gider.delete(*self.t_gider.get_children())
        kat = {}
        for g in sorted(o["giderler"], key=lambda g: g["tarih"], reverse=True):
            kat[g["kategori"]] = kat.get(g["kategori"], 0) + g["tutar"]
            self.t_gider.insert("", "end", iid=g["id"], values=(tarih_yaz(g["tarih"]), g["kategori"], g.get("aciklama", ""), g["odeme"],
                                                                "📎" if g.get("fis") else "", para_kisa(g["tutar"])))
        self.v_g_kat.set("Dağılım: " + " · ".join(f"{k} {para_kisa(t)}" for k, t in sorted(kat.items(), key=lambda x: -x[1])) if kat else "Bu ay gider yok.")
        self.t_duzenli.delete(*self.t_duzenli.get_children())
        for z in v.d["duzenliler"]:
            self.t_duzenli.insert("", "end", iid=z["id"], tags=("" if z.get("aktif") else "soluk",),
                                  values=(z["kategori"] + (f" – {z['aciklama']}" if z.get("aciklama") else ""), z.get("gun", 1),
                                          para_kisa(z["tutar"]), "Aktif" if z.get("aktif") else "Durduruldu"))

    def gider_formu(self, gider_id=None):
        v = self.v
        g = v.bul("giderler", gider_id) if gider_id else None
        kategoriler = [k["ad"] for k in v.d["kategoriler"]]
        if g and g["kategori"] not in kategoriler:
            kategoriler.append(g["kategori"])
        f = Form(self, "Gideri düzenle" if g else "Gider ekle")
        kat = f.secim("Ne için?", kategoriler, g["kategori"] if g else (kategoriler[0] if kategoriler else ""), serbest=True)
        ac = f.giris("Açıklama", g.get("aciklama", "") if g else "")
        tutar = f.giris("Tutar (TL)", sayi_yaz(g["tutar"]) if g else "", sag=True)
        odeme = f.radyo("Nereden ödendi?", ["Banka", "Nakit"], g["odeme"] if g else "Banka")
        tarih = f.giris("Tarih (gg.aa.yyyy)", tarih_yaz(g["tarih"] if g else bugun()))
        fis = {"yol": None}
        v_fis = tk.StringVar(value=("Kayıtlı fiş var" if g and g.get("fis") else "Fiş eklenmedi"))
        ff = ttk.Frame(f.govde)
        ff.grid(row=f.satir, column=1, columnspan=2, sticky="w", pady=4)
        ttk.Label(f.govde, text="Fiş / fatura (isteğe bağlı)").grid(row=f.satir, column=0, sticky="w")
        f.satir += 1

        def fis_sec():
            y = filedialog.askopenfilename(parent=f, title="Fiş / fatura seçin", filetypes=[("Resim / PDF", "*.jpg *.jpeg *.png *.pdf"), ("Tümü", "*.*")])
            if y:
                fis["yol"] = y
                v_fis.set(os.path.basename(y))

        ttk.Button(ff, text="📎 Dosya seç…", command=fis_sec).pack(side="left")
        ttk.Label(ff, textvariable=v_fis, style="Not.TLabel").pack(side="left", padx=8)

        def kaydet():
            try:
                t = sayi_al(tutar, "Tutar", ebeveyn=f)
            except ValueError:
                return
            tr = tarih_oku(tarih.get())
            if not t or not tr or not kat.get().strip():
                return messagebox.showwarning("Eksik", "Ne için, tutar ve tarihi (gg.aa.yyyy) yazın.", parent=f)
            k = dict(g or {}, kategori=kat.get().strip(), aciklama=ac.get().strip(), tutar=t, odeme=odeme.get(), tarih=tr)
            k.setdefault("id", uid())
            if fis["yol"]:
                klasor = os.path.join(v.klasor, "fisler")
                os.makedirs(klasor, exist_ok=True)
                ad = f"{tr}_{guvenli_ad(k['kategori'])}_{k['id']}{os.path.splitext(fis['yol'])[1].lower()}"
                shutil.copyfile(fis["yol"], os.path.join(klasor, ad))
                k["fis"] = ad
            if kat.get().strip() not in [x["ad"] for x in v.d["kategoriler"]]:
                v.yaz("kategoriler", {"ad": kat.get().strip()}, False)
            v.yaz("giderler", k)
            f.destroy()
            self.secili_donem = tr[:7]
            self.ciz()
            self.durum("Gider kaydedildi.")

        def sil():
            if messagebox.askyesno("Sil", "Bu gider silinsin mi?", parent=f):
                v.sil("giderler", g["id"])
                f.destroy()
                self.ciz()

        dug = [("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None)]
        if g:
            dug.insert(1, ("Gideri sil", sil, KIRMIZI))
        f.dugmeler(*dug)
        f.ac()

    def fis_ac(self):
        g = self.v.bul("giderler", self._sec(self.t_gider) or "")
        if not g or not g.get("fis"):
            return messagebox.showinfo("Fiş", "Seçili giderin kayıtlı fişi yok.", parent=self)
        yol = os.path.join(self.v.klasor, "fisler", g["fis"])
        if os.path.exists(yol):
            dosya_ac(yol)
        else:
            messagebox.showwarning("Fiş", "Fiş dosyası bulunamadı (Google Drive henüz eşitlememiş olabilir).", parent=self)

    def duzenli_formu(self, zid=None):
        v = self.v
        z = v.bul("duzenliler", zid) if zid else None
        kategoriler = [k["ad"] for k in v.d["kategoriler"]]
        f = Form(self, "Düzenli gider")
        kat = f.secim("Ne için?", kategoriler, z["kategori"] if z else ("Temizlikçi" if "Temizlikçi" in kategoriler else ""), serbest=True)
        ac = f.giris("Açıklama", z.get("aciklama", "") if z else "")
        tutar = f.giris("Aylık tutar (TL)", sayi_yaz(z["tutar"]) if z else "", sag=True)
        gun = f.giris("Her ayın kaçında ödeniyor?", str(z.get("gun", 1)) if z else "1", sag=True)
        odeme = f.radyo("Nereden ödeniyor?", ["Banka", "Nakit"], z["odeme"] if z else "Banka")
        aktif = f.onay("Aktif (her ay hatırlat)", z.get("aktif", True) if z else True)

        def kaydet():
            try:
                t = sayi_al(tutar, "Tutar", ebeveyn=f)
                gn = int(sayi_al(gun, "Gün", ebeveyn=f) or 1)
            except ValueError:
                return
            if not t or not kat.get().strip():
                return messagebox.showwarning("Eksik", "Ne için ve tutarı yazın.", parent=f)
            v.yaz("duzenliler", dict(z or {}, kategori=kat.get().strip(), aciklama=ac.get().strip(), tutar=t, gun=min(28, max(1, gn)),
                                     odeme=odeme.get(), aktif=aktif.get()))
            f.destroy()
            self.ciz()

        def sil():
            if messagebox.askyesno("Sil", "Düzenli gider silinsin mi? (Daha önce eklenmiş giderler silinmez.)", parent=f):
                v.sil("duzenliler", z["id"])
                f.destroy()
                self.ciz()

        dug = [("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None)]
        if z:
            dug.insert(1, ("Sil", sil, KIRMIZI))
        f.dugmeler(*dug)
        f.ac()

    def duzenli_ekle(self, z):
        self.v.yaz("giderler", {"kategori": z["kategori"], "aciklama": z.get("aciklama") or f"{donem_adi(bu_donem())} {z['kategori'].lower()}",
                                "tutar": z["tutar"], "tarih": bugun(), "odeme": z["odeme"], "duzenli_id": z["id"]})
        self.ciz()
        self.durum(f"{z['kategori']} gideri eklendi.")

    # ------------------------------------------------------------ aidat ve ek toplama
    def _aidat_kur(self):
        p = self.sayfalar["aidat"]
        p.columnconfigure(0, weight=2)
        p.columnconfigure(1, weight=3)
        p.rowconfigure(1, weight=1)
        sol = ttk.LabelFrame(p, text=" Aylık aidat ", padding=12)
        sol.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        sol.columnconfigure(0, weight=1)
        sol.rowconfigure(4, weight=1)
        self.v_aidat, self.v_aidat_alt = tk.StringVar(), tk.StringVar()
        ttk.Label(sol, textvariable=self.v_aidat, style="Buyuk.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(sol, textvariable=self.v_aidat_alt, style="Uyari.TLabel", wraplength=380, justify="left").grid(row=1, column=0, sticky="w")
        ttk.Label(sol, text="Aidatlar her ay başında, program açıldığında bütün dairelere kendiliğinden yazılır. Ön ödemesi olan dairelerde "
                  "bakiyeden düşer.", style="Not.TLabel", wraplength=380, justify="left").grid(row=2, column=0, sticky="w", pady=6)
        self.renkli(sol, "Aidatı değiştir", MAVI, self.tarife_formu).grid(row=3, column=0, sticky="w")
        cer, self.t_tarife = self.tablo(sol, (("ay", "Hangi aydan itibaren", 170, "w"), ("tutar", "Tutar", 100, "e"), ("ac", "Açıklama", 140, "w")), yukseklik=8)
        cer.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        sag = ttk.LabelFrame(p, text=" Ek toplamalar ", padding=12)
        sag.grid(row=0, column=1, rowspan=2, sticky="nsew")
        sag.columnconfigure(0, weight=1)
        sag.rowconfigure(2, weight=1)
        sag.rowconfigure(4, weight=1)
        ttk.Label(sag, text="Asansör tamiri, boya, kapı değişimi gibi aidatın karşılamadığı işler için dairelerden ayrıca para toplamak için "
                  "kullanın. Tutar dairelere bölünür ve hesaplarına borç olarak yazılır; ön ödemesi olandan düşer.", style="Not.TLabel",
                  wraplength=600, justify="left").grid(row=0, column=0, sticky="w")
        d = ttk.Frame(sag)
        d.grid(row=1, column=0, sticky="w", pady=8)
        self.renkli(d, "➕ Yeni ek toplama", YESIL, lambda: self.ek_formu()).pack(side="left")
        for metin, komut in (("✏ Düzenle", lambda: self.ek_formu(self._sec(self.t_ek))), ("📄 Duyuru PDF", self.ek_pdf),
                             ("💬 Gruba duyur", self.ek_whatsapp), ("🗑 Sil", self.ek_sil)):
            ttk.Button(d, text=metin, command=komut).pack(side="left", padx=(6, 0))
        cer, self.t_ek = self.tablo(sag, (("ay", "Ay", 110, "w"), ("baslik", "Ne için", 260, "w"), ("daire", "Daire", 60, "center"),
                                          ("toplam", "Toplam", 110, "e")), yukseklik=7)
        cer.grid(row=2, column=0, sticky="nsew")
        self.t_ek.bind("<<TreeviewSelect>>", lambda _e: self.ek_detay_ciz())
        ttk.Label(sag, text="Seçili ek toplamada dairelerin durumu", style="Sonuc.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 4))
        cer, self.t_ek_detay = self.tablo(sag, (("daire", "Daire", 80, "w"), ("kisi", "Kişi", 200, "w"), ("pay", "Payı", 100, "e"),
                                                ("durum", "Durum", 140, "e")), yukseklik=7)
        cer.grid(row=4, column=0, sticky="nsew")

    def aidat_ciz(self):
        v = self.v
        self.v_aidat.set(para(v.tarife_tutari(bu_donem())))
        gelecek = sorted([t for t in v.d["tarifeler"] if t["baslangic_donem"] > bu_donem()], key=lambda t: t["baslangic_donem"])
        ozel = [d for d in v.aktif_daireler() if d.get("ozel_aidat") is not None]
        alt = []
        if gelecek:
            alt.append(f"{donem_adi(gelecek[0]['baslangic_donem'])} itibarıyla {para_kisa(gelecek[0]['tutar'])} olacak.")
        if ozel:
            alt.append("Özel aidatlı daireler: " + ", ".join(f"Daire {d['no']} {para_kisa(d['ozel_aidat'])}" for d in ozel))
        self.v_aidat_alt.set("\n".join(alt))
        self.t_tarife.delete(*self.t_tarife.get_children())
        for t in sorted(v.d["tarifeler"], key=lambda t: t["baslangic_donem"], reverse=True):
            self.t_tarife.insert("", "end", values=(donem_adi(t["baslangic_donem"]), para_kisa(t["tutar"]), t.get("aciklama", "")))
        sec = self._sec(self.t_ek)
        self.t_ek.delete(*self.t_ek.get_children())
        for e in sorted(v.d["ekler"], key=lambda e: e["tarih"], reverse=True):
            n = len([b for b in v.d["borclar"] if b.get("ek_id") == e["id"]])
            self.t_ek.insert("", "end", iid=e["id"], values=(donem_adi(e["donem"]), e["baslik"], n, para_kisa(e["toplam"])))
        if sec and self.t_ek.exists(sec):
            self.t_ek.selection_set(sec)
        self.ek_detay_ciz()

    def ek_detay_ciz(self):
        v = self.v
        self.t_ek_detay.delete(*self.t_ek_detay.get_children())
        e = v.bul("ekler", self._sec(self.t_ek) or "")
        if not e:
            return
        for b in [b for b in v.d["borclar"] if b.get("ek_id") == e["id"]]:
            d, h = v.bul("daireler", b["daire_id"]), v.hesap(b["daire_id"])
            ac = next((x for x in h["tum_acik"] if x["id"] == b["id"]), None)
            self.t_ek_detay.insert("", "end", tags=("borc" if ac else "alacak",), values=(
                f"Daire {d['no']}", v.odeyen_adi(b.get("sakin_id"), d), para_kisa(b["tutar"]), f"kalan {para_kisa(ac['kalan'])}" if ac else "ödendi ✓"))

    def tarife_formu(self):
        v = self.v
        f = Form(self, "Aidatı değiştir")
        tutar = f.giris("Yeni aylık aidat (TL)", "", sag=True)
        aylar = [donem_kaydir(bu_donem(), i) for i in range(-12, 13)]
        ay = f.secim("Hangi aydan itibaren?", [donem_adi(a) for a in aylar], donem_adi(donem_kaydir(bu_donem(), 1)))
        ac = f.giris("Açıklama (isteğe bağlı)", "", genislik=28)
        f.not_("Seçtiğiniz aydan önceki aidatlar değişmez. Seçilen ay zaten yazılmışsa o ayın aidatları da yeni tutara güncellenir "
               "(özel aidatlı daireler hariç).")

        def kaydet():
            try:
                t = sayi_al(tutar, "Tutar", ebeveyn=f)
            except ValueError:
                return
            if t is None:
                return
            donem = aylar[[donem_adi(x) for x in aylar].index(ay.get())]
            ayni = next((x for x in v.d["tarifeler"] if x["baslangic_donem"] == donem), None)
            v.yaz("tarifeler", dict(ayni or {}, baslangic_donem=donem, tutar=t, aciklama=ac.get().strip()), False)
            sonra = sorted(x["baslangic_donem"] for x in v.d["tarifeler"] if x["baslangic_donem"] > donem)
            for b in v.d["borclar"]:
                if b["tur"] == "Aidat" and b["donem"] >= donem and (not sonra or b["donem"] < sonra[0]):
                    d = v.bul("daireler", b["daire_id"])
                    if d and d.get("ozel_aidat") is None:
                        v.yaz("borclar", dict(b, tutar=t), False)
            v.kaydet()
            f.destroy()
            self.otomatik()
            self.durum("Aidat güncellendi.")

        f.dugmeler(("Kaydet", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def ek_formu(self, ek_id=None):
        v = self.v
        e = v.bul("ekler", ek_id) if ek_id else None
        secili = set(e["daireler"]) if e else {d["id"] for d in v.aktif_daireler()}
        f = Form(self, "Ek toplamayı düzenle" if e else "Yeni ek toplama", 600)
        baslik = f.giris("Ne için?", e["baslik"] if e else "")
        ac = f.metin("Açıklama (raporda görünür)", e.get("aciklama", "") if e else "", 3)
        giris = f.radyo("Tutar nasıl girilsin?", ["Toplam tutar", "Daire başı tutar"], "Toplam tutar")
        tutar = f.giris("Tutar (TL)", sayi_yaz(e["toplam"]) if e else "", sag=True)
        dagitim = f.radyo("Nasıl bölünsün?", ["Eşit", "Pay oranına göre"], "Pay oranına göre" if e and e.get("dagitim") == "oran" else "Eşit")
        aylar = [donem_kaydir(bu_donem(), i) for i in range(-12, 4)]
        ay = f.secim("Hangi aya yazılsın?", [donem_adi(a) for a in aylar], donem_adi(e["donem"] if e else bu_donem()))
        ttk.Label(f.govde, text="Katılan daireler").grid(row=f.satir, column=0, sticky="nw", pady=4)
        kutu = ttk.Frame(f.govde)
        kutu.grid(row=f.satir, column=1, columnspan=2, sticky="w")
        f.satir += 1
        secimler = {}
        for n, d in enumerate([d for d in v.tum_daireler() if d.get("aktif") or d["id"] in secili]):
            secimler[d["id"]] = tk.BooleanVar(value=d["id"] in secili)
            ttk.Checkbutton(kutu, text=f"Daire {d['no']}", variable=secimler[d["id"]]).grid(row=n // 4, column=n % 4, sticky="w", padx=(0, 12))
        v_on = tk.StringVar()
        ttk.Label(f.govde, textvariable=v_on, style="Not.TLabel", wraplength=520, justify="left").grid(row=f.satir, column=0, columnspan=3, sticky="w", pady=6)
        f.satir += 1

        def hesapla():
            t = sayi_oku(tutar.get())
            idler = [i for i, b in secimler.items() if b.get()]
            return ek_dagit(v, idler, t, dagitim.get() == "Pay oranına göre", giris.get() == "Daire başı tutar")

        def onizle(*_):
            r = hesapla()
            if not r:
                v_on.set("Tutarı yazın ve en az bir daire seçin.")
                return
            v_on.set(f"Toplam {para(r[0])}  →  " + "  ·  ".join(f"Daire {v.bul('daireler', i)['no']}: {para_kisa(t)}" for i, t in r[1]))

        for x in (tutar, giris, dagitim):
            x.trace_add("write", onizle)
        for b in secimler.values():
            b.trace_add("write", onizle)
        onizle()

        def kaydet():
            r = hesapla()
            if not baslik.get().strip():
                return messagebox.showwarning("Eksik", "Ne için toplandığını yazın.", parent=f)
            if not r:
                return messagebox.showwarning("Eksik", "Tutarı yazın ve en az bir daire seçin.", parent=f)
            donem = aylar[[donem_adi(x) for x in aylar].index(ay.get())]
            kayit = v.yaz("ekler", dict(e or {}, tarih=e["tarih"] if e else bugun(), donem=donem, baslik=baslik.get().strip(),
                                        aciklama=ac.get("1.0", "end").strip(), toplam=r[0], dagitim="oran" if dagitim.get() == "Pay oranına göre" else "esit",
                                        daireler=[i for i, _ in r[1]]), False)
            yeni = {i for i, _ in r[1]}
            for b in [b for b in v.d["borclar"] if b.get("ek_id") == kayit["id"] and b["daire_id"] not in yeni]:
                v.sil("borclar", b["id"], False)
            for i, t in r[1]:
                kimlik = f"ek-{kayit['id']}-{i}"
                eski = v.bul("borclar", kimlik)
                s = v.aktif_sakin(i)
                v.yaz("borclar", {"id": kimlik, "daire_id": i, "sakin_id": eski["sakin_id"] if eski else (s["id"] if s else ""), "donem": donem,
                                  "tur": "Ek toplama", "baslik": kayit["baslik"], "tutar": t, "ek_id": kayit["id"],
                                  "tarih": eski["tarih"] if eski else bugun()}, False)
            v.kaydet()
            f.destroy()
            self.ciz()
            self.defter.select(self.sayfalar["aidat"])
            self.t_ek.selection_set(kayit["id"])
            self.durum("Ek toplama dairelere paylaştırıldı.")

        f.dugmeler(("Güncelle" if e else "Dairelere paylaştır", kaydet, MAVI), ("Vazgeç", f.destroy, None))
        f.ac()

    def _secili_ek(self):
        e = self.v.bul("ekler", self._sec(self.t_ek) or "")
        if not e:
            messagebox.showinfo("Ek toplama", "Önce listeden bir ek toplama seçin.", parent=self)
        return e

    def ek_pdf(self):
        e = self._secili_ek()
        if e:
            self.pdf(lambda y: rapor_ek(self.v, e["id"], y), f"Ek Toplama {e['baslik']}")

    def ek_whatsapp(self):
        e = self._secili_ek()
        if e:
            self.mesaj_penceresi("Ek toplama duyurusu", self.v.ek_duyuru_metni(e))

    def ek_sil(self):
        e = self._secili_ek()
        if e and messagebox.askyesno("Sil", "Bu ek toplama ve dairelere yazılan payları silinsin mi?\n(Alınmış ödemeler silinmez, dairelerin "
                                     "bakiyesine alacak olarak geçer.)", parent=self):
            for b in [b for b in self.v.d["borclar"] if b.get("ek_id") == e["id"]]:
                self.v.sil("borclar", b["id"], False)
            self.v.sil("ekler", e["id"])
            self.ciz()

    # ------------------------------------------------------------ raporlar
    def _raporlar_kur(self):
        p = self.sayfalar["raporlar"]
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        ttk.Label(p, text="Raporlar herkesin anlayacağı sade bir dille hazırlanır. PDF oluşturulup açılır; WhatsApp grubuna dosya olarak "
                  "gönderebilirsiniz.", style="Not.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        def kart(satir, sutun, baslik, aciklama):
            f = ttk.LabelFrame(p, text=f" {baslik} ", padding=12)
            f.grid(row=satir, column=sutun, sticky="nsew", padx=6, pady=6)
            ttk.Label(f, text=aciklama, style="Not.TLabel", wraplength=480, justify="left").pack(anchor="w", pady=(0, 8))
            return f

        f = kart(1, 0, "📅 Aylık rapor", "O ay ne toplandı, ne harcandı, kasada ne kaldı, hangi daire ödedi.")
        self.v_r_ay = tk.StringVar()
        self.c_r_ay = ttk.Combobox(f, textvariable=self.v_r_ay, state="readonly", width=20, font=(self.fa, 11))
        self.c_r_ay.pack(side="left")
        self.renkli(f, "PDF oluştur", MAVI, self.r_aylik).pack(side="left", padx=8)
        f = kart(1, 1, "📆 Yıllık rapor", "Ay ay gelir-gider, harcamaların dağılımı, daire bazında yıllık durum. Yıllık toplantı için.")
        self.v_r_yil = tk.StringVar()
        self.c_r_yil = ttk.Combobox(f, textvariable=self.v_r_yil, state="readonly", width=10, font=(self.fa, 11))
        self.c_r_yil.pack(side="left")
        self.renkli(f, "PDF oluştur", MAVI, lambda: self.pdf(lambda y: rapor_yillik(self.v, self.v_r_yil.get(), y),
                                                             f"{self.v_r_yil.get()} Yillik Rapor")).pack(side="left", padx=8)
        f = kart(2, 0, "🚪 Daire hesap dökümü", "Bir dairenin bütün aidat, ödeme ve bakiye geçmişi.")
        self.v_r_daire = tk.StringVar()
        self.c_r_daire = ttk.Combobox(f, textvariable=self.v_r_daire, state="readonly", width=30, font=(self.fa, 11))
        self.c_r_daire.pack(side="left")
        self.renkli(f, "PDF oluştur", MAVI, self.r_dokum).pack(side="left", padx=8)
        f = kart(2, 1, "⚠ Borç durumu", "Bütün dairelerin güncel borç / ön ödeme durumu.")
        self.renkli(f, "PDF oluştur", MAVI, lambda: self.pdf(lambda y: rapor_borclar(self.v, y), f"Borc Durumu {bugun()}")).pack(anchor="w")
        f = kart(3, 0, "📢 Duyuru", "Apartman grubuna gönderilecek hazır mesajlar (aidat hatırlatma, toplantı, kesinti…).")
        ttk.Button(f, text="Duyuru hazırla", command=self.duyuru).pack(anchor="w")
        f = kart(3, 1, "📁 Rapor klasörü", f"PDF'ler bu bilgisayarda şu klasöre kaydedilir:\n{pdf_klasoru()}")
        ttk.Button(f, text="Klasörü aç", command=lambda: dosya_ac(pdf_klasoru())).pack(anchor="w")
        self.defter.bind("<<NotebookTabChanged>>", lambda _e: self._rapor_listeleri(), add="+")

    def _rapor_listeleri(self):
        v = self.v
        bas = v.ayar("baslangic_donem", bu_donem())
        aylar = list(reversed(donemler(min(bas, bu_donem()), bu_donem())))
        self._r_aylar = aylar
        self.c_r_ay.configure(values=[donem_adi(a) for a in aylar])
        if self.v_r_ay.get() not in self.c_r_ay["values"]:
            self.v_r_ay.set(donem_adi(aylar[0]))
        yillar = sorted({a[:4] for a in aylar}, reverse=True)
        self.c_r_yil.configure(values=yillar)
        if self.v_r_yil.get() not in yillar:
            self.v_r_yil.set(yillar[0])
        self._r_daireler = v.tum_daireler()
        self.c_r_daire.configure(values=[f"Daire {d['no']} – {v.oturan_adi(d)}" for d in self._r_daireler])
        if self.v_r_daire.get() not in self.c_r_daire["values"] and self._r_daireler:
            self.v_r_daire.set(self.c_r_daire["values"][0])

    def r_aylik(self):
        m = self._r_aylar[list(self.c_r_ay["values"]).index(self.v_r_ay.get())]
        self.pdf(lambda y: rapor_aylik(self.v, m, y), f"{donem_adi(m)} Raporu")

    def r_dokum(self):
        d = self._r_daireler[list(self.c_r_daire["values"]).index(self.v_r_daire.get())]
        self.pdf(lambda y: rapor_dokum(self.v, d["id"], y), f"Daire {d['no']} Hesap Dokumu {bugun()}")

    def pdf(self, uret, ad):
        if not PDF_VAR:
            return messagebox.showerror("PDF", "PDF kütüphanesi bulunamadı.", parent=self)
        yol = os.path.join(pdf_klasoru(), guvenli_ad(f"{self.v.ayar('apartman_adi', 'Apartman')} - {ad}") + ".pdf")
        try:
            uret(yol)
        except PermissionError:
            return messagebox.showerror("PDF", "PDF yazılamadı. Aynı dosya açıksa kapatıp tekrar deneyin.", parent=self)
        except Exception as hata:
            return messagebox.showerror("PDF oluşturulamadı", str(hata), parent=self)
        self.durum(f"PDF oluşturuldu: {yol}")
        dosya_ac(yol)

    def duyuru(self):
        v, m = self.v, bu_donem()
        ap, yon = v.ayar("apartman_adi", "Apartman"), v.ayar("yonetici_ad")
        iban = (f"\n\nIBAN: {v.ayar('iban')}" + (f" ({v.ayar('iban_ad')})" if v.ayar("iban_ad") else "") +
                "\nAçıklamaya daire numaranızı yazmanızı rica ederim.") if v.ayar("iban") else ""
        sablonlar = {
            "Aidat hatırlatma": f"Sayın {ap} sakinleri,\n\n{donem_adi(m)} aidatının ({para_kisa(v.tarife_tutari(m))}) en geç ayın "
                                f"{v.ayar('son_odeme_gunu', '10')}'una kadar ödenmesini rica ederim.{iban}\n\nTeşekkürler,\n{yon}",
            "Aylık rapor yayınlandı": f"Sayın {ap} sakinleri,\n\n{donem_adi(donem_kaydir(m, -1))} ayı gelir-gider raporu ektedir. "
                                      f"Sorularınız için bana ulaşabilirsiniz.\n\nTeşekkürler,\n{yon}",
            "Su / elektrik kesintisi": f"Sayın {ap} sakinleri,\n\n... tarihinde ... saatleri arasında ... kesintisi olacaktır. Bilginize sunarım.\n\n{yon}",
            "Toplantı çağrısı": f"Sayın {ap} sakinleri,\n\nApartman toplantısı ... tarihinde saat ...'da ... yapılacaktır. Gündem: ...\n"
                                f"Katılımınızı rica ederim.\n\n{yon}",
            "Boş mesaj": "",
        }
        f = Form(self, "Duyuru", 600)
        s = f.secim("Hazır mesaj", list(sablonlar), "Aidat hatırlatma")
        t = f.metin("Mesaj", sablonlar["Aidat hatırlatma"], 14)
        s.trace_add("write", lambda *_: (t.delete("1.0", "end"), t.insert("1.0", sablonlar[s.get()])))

        def kopyala():
            self.clipboard_clear()
            self.clipboard_append(t.get("1.0", "end").strip())
            self.durum("Duyuru kopyalandı.")

        f.dugmeler(("💬 WhatsApp'ta aç", lambda: wa_ac("", t.get("1.0", "end").strip()), YESIL), ("📋 Kopyala", kopyala, None), ("Kapat", f.destroy, None))
        f.not_("WhatsApp açılınca apartman grubunu seçin.")
        f.ac()

    # ------------------------------------------------------------ ayarlar
    def _ayarlar_kur(self):
        p = self.sayfalar["ayarlar"]
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        sol = ttk.LabelFrame(p, text=" Apartman ve yönetici ", padding=12)
        sol.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))
        sol.columnconfigure(1, weight=1)
        self.ay = {}
        for n, (a, e) in enumerate((("apartman_adi", "Apartman adı"), ("adres", "Adres"), ("yonetici_ad", "Yönetici adı soyadı"),
                                    ("yonetici_tel", "Yönetici telefonu"), ("iban", "Aidat IBAN"), ("iban_ad", "IBAN hesap sahibi"),
                                    ("son_odeme_gunu", "Son ödeme günü"), ("acilis_banka", "Açılış kasası – banka (TL)"),
                                    ("acilis_nakit", "Açılış kasası – nakit (TL)"))):
            ttk.Label(sol, text=e).grid(row=n, column=0, sticky="w", pady=3, padx=(0, 10))
            self.ay[a] = tk.StringVar()
            ttk.Entry(sol, textvariable=self.ay[a], font=(self.fa, 11)).grid(row=n, column=1, sticky="we", pady=3)
        n = 9
        ttk.Label(sol, text="Aidatların başladığı ay").grid(row=n, column=0, sticky="w", pady=3)
        self.ay_bas = tk.StringVar()
        self.c_bas = ttk.Combobox(sol, textvariable=self.ay_bas, state="readonly", font=(self.fa, 11))
        self.c_bas.grid(row=n, column=1, sticky="we", pady=3)
        self.ay_tablo = tk.BooleanVar()
        ttk.Checkbutton(sol, text="Raporlarda dairelerin borç durumu tablosu gösterilsin", variable=self.ay_tablo).grid(row=n + 1, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Label(sol, text="Açılış kasası: programa başlarken kasada / bankada para varsa yazın; sıfırdan başlıyorsanız 0 bırakın.",
                  style="Not.TLabel", wraplength=460, justify="left").grid(row=n + 2, column=0, columnspan=2, sticky="w")
        self.renkli(sol, "💾 Kaydet", MAVI, self.ayar_kaydet).grid(row=n + 3, column=0, sticky="w", pady=(10, 0))

        sag = ttk.LabelFrame(p, text=" Gider kategorileri ", padding=12)
        sag.grid(row=0, column=1, sticky="nsew")
        sag.columnconfigure(0, weight=1)
        self.lb_kat = tk.Listbox(sag, height=8, font=(self.fa, 10))
        self.lb_kat.grid(row=0, column=0, columnspan=3, sticky="we")
        self.v_yeni_kat = tk.StringVar()
        ttk.Entry(sag, textvariable=self.v_yeni_kat, font=(self.fa, 11)).grid(row=1, column=0, sticky="we", pady=6)
        ttk.Button(sag, text="Ekle", command=self.kategori_ekle).grid(row=1, column=1, padx=4)
        ttk.Button(sag, text="Seçiliyi sil", command=self.kategori_sil).grid(row=1, column=2)

        alt = ttk.LabelFrame(p, text=" Şifre ve veriler ", padding=12)
        alt.grid(row=1, column=1, sticky="nsew", pady=(8, 0))
        alt.columnconfigure(0, weight=1)
        ttk.Button(alt, text="🔑 Şifreyi değiştir", command=self.sifre_degistir).grid(row=0, column=0, sticky="w")
        self.v_klasor = tk.StringVar()
        ttk.Label(alt, textvariable=self.v_klasor, wraplength=460, justify="left").grid(row=1, column=0, sticky="w", pady=(10, 4))
        d = ttk.Frame(alt)
        d.grid(row=2, column=0, sticky="w")
        ttk.Button(d, text="📁 Ortak klasör seç (Google Drive)…", command=self.klasor_sec).pack(side="left")
        ttk.Button(d, text="💻 Bu bilgisayarın klasörüne dön", command=self.yerele_don).pack(side="left", padx=6)
        ttk.Label(alt, text="İki bilgisayarda kullanmak için her ikisinde de Google Drive masaüstü uygulamasını aynı hesapla açın, sonra burada "
                  "Google Drive'daki aynı klasörü seçin (örn. G:\\Drive'ım). Program içinde “ApartmanYonetimi” klasörünü kendisi oluşturur.",
                  style="Not.TLabel", wraplength=460, justify="left").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.defter.bind("<<NotebookTabChanged>>", lambda _e: self.ayarlari_doldur(), add="+")

    def ayarlari_doldur(self):
        if self.defter.select() != str(self.sayfalar["ayarlar"]):
            return
        v = self.v
        for a, x in self.ay.items():
            deger = v.ayar(a, "")
            x.set(sayi_yaz(sayi_oku(deger) or 0) if a.startswith("acilis") else str(deger))
        aylar = [donem_kaydir(bu_donem(), i) for i in range(-24, 4)]
        self._bas_aylar = aylar
        self.c_bas.configure(values=[donem_adi(a) for a in aylar])
        self.ay_bas.set(donem_adi(v.ayar("baslangic_donem", bu_donem())))
        self.ay_tablo.set(bool(v.ayar("rapor_borc_tablosu", True)))
        self.lb_kat.delete(0, "end")
        for k in v.d["kategoriler"]:
            self.lb_kat.insert("end", k["ad"])
        ortak = bool(self.yerel.get("klasor"))
        self.v_klasor.set(("Ortak klasör: " if ortak else "Veriler sadece bu bilgisayarda: ") + v.klasor)

    def ayar_kaydet(self):
        v = self.v
        b, n = sayi_oku(self.ay["acilis_banka"].get()), sayi_oku(self.ay["acilis_nakit"].get())
        if b is None and self.ay["acilis_banka"].get().strip() or n is None and self.ay["acilis_nakit"].get().strip():
            return messagebox.showwarning("Hatalı giriş", "Açılış kasası sayı olmalı.", parent=self)
        if not self.ay["apartman_adi"].get().strip():
            return messagebox.showwarning("Eksik", "Apartman adını yazın.", parent=self)
        yeni_bas = self._bas_aylar[[donem_adi(a) for a in self._bas_aylar].index(self.ay_bas.get())]
        eski_bas = v.ayar("baslangic_donem", bu_donem())
        if yeni_bas > eski_bas and any(x["tur"] == "Aidat" and x["donem"] < yeni_bas for x in v.d["borclar"]):
            if not messagebox.askyesno("Başlangıç ayı", "Başlangıç ayını ileri aldınız. Daha önce yazılmış aidatlar silinmez. Devam edilsin mi?", parent=self):
                return
        yeni = {a: x.get().strip() for a, x in self.ay.items()}
        yeni.update(acilis_banka=b or 0, acilis_nakit=n or 0, baslangic_donem=yeni_bas, rapor_borc_tablosu=self.ay_tablo.get())
        if yeni_bas < eski_bas:
            for d in v.d["daireler"]:
                if d.get("baslangic_donem") == eski_bas:
                    v.yaz("daireler", dict(d, baslangic_donem=yeni_bas), False)
        v.ayarlari_yaz(yeni)
        self.otomatik()
        self.durum("Ayarlar kaydedildi.")

    def kategori_ekle(self):
        ad = self.v_yeni_kat.get().strip()
        if ad and ad not in [k["ad"] for k in self.v.d["kategoriler"]]:
            self.v.yaz("kategoriler", {"ad": ad})
            self.v_yeni_kat.set("")
            self.ayarlari_doldur()

    def kategori_sil(self):
        s = self.lb_kat.curselection()
        if s:
            k = self.v.d["kategoriler"][s[0]]
            if messagebox.askyesno("Kategori", f"“{k['ad']}” silinsin mi? (Bu kategorideki eski giderler silinmez.)", parent=self):
                self.v.sil("kategoriler", k["id"])
                self.ayarlari_doldur()

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
        vardi = os.path.exists(os.path.join(hedef, "apartman.json"))
        yeni = Veri(hedef)
        if vardi and ortak:
            yeni.d = yeni._tamamla(birlestir(yeni.d, eski.d))
            mesaj = "Bu klasörde zaten veri vardı; iki taraftaki kayıtlar birleştirildi."
        else:
            yeni.d = json.loads(json.dumps(eski.d))
            mesaj = "Veriler yeni klasöre kopyalandı."
        kaynak_fis = os.path.join(eski.klasor, "fisler")
        if os.path.isdir(kaynak_fis):
            os.makedirs(os.path.join(hedef, "fisler"), exist_ok=True)
            for ad in os.listdir(kaynak_fis):
                h = os.path.join(hedef, "fisler", ad)
                if not os.path.exists(h):
                    shutil.copyfile(os.path.join(kaynak_fis, ad), h)
        yeni.kaydet()
        self.yerel["klasor"] = hedef if ortak else None
        yerel_ayar_yaz(self.yerel)
        self.v = yeni
        self.otomatik()
        self.ayarlari_doldur()
        messagebox.showinfo("Veri klasörü", mesaj, parent=self)

    def klasor_sec(self):
        s = filedialog.askdirectory(parent=self, title="Google Drive'daki klasörü seçin (örn. Drive'ım)")
        if not s:
            return
        hedef = s if (os.path.basename(os.path.normpath(s)).lower() == "apartmanyonetimi" or os.path.exists(os.path.join(s, "apartman.json"))) \
            else os.path.join(s, "ApartmanYonetimi")
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
