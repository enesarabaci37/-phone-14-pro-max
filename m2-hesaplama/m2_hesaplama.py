"""Arabacı Reklam - m² Hesaplama programı.

Müşteri fiyatı, malzeme maliyeti (TL / Dolar / Euro), kâr, KDV ve indirim hesapları.
Sadece Python standart kütüphanesi kullanılır (tkinter).
"""

import json
import os
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
import urllib.request
import xml.etree.ElementTree as ET
from tkinter import ttk

UYGULAMA_ADI = "Arabacı Reklam - m² Hesaplama"
SURUM = "1.0"

BIRIMLER = {"cm": 0.01, "mm": 0.001, "m": 1.0}
KDV_ORANLARI = ["0", "1", "5", "10", "15", "20"]
PARA_BIRIMLERI = ["TL", "Dolar", "Euro"]
TCMB_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"

KIRMIZI = "#d62828"
YESIL = "#1e8e3e"
GRI = "#666666"


# ---------------------------------------------------------------- hesap yardımcıları

def sayi_oku(metin):
    """'1.234,5', '1234,5', '1234.5' gibi girişleri sayıya çevirir. Boş/hatalıysa None."""
    s = (metin or "").strip().replace(" ", "").replace("%", "")
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


def para(x, birim="TL"):
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {birim}"


def sayi_yaz(x, basamak=2):
    s = f"{x:,.{basamak}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def kisa(x):
    """Tam sayıysa küsuratsız, değilse virgüllü yazar: 120 -> '120', 10.5 -> '10,5'."""
    return sayi_yaz(x, 0) if float(x).is_integer() else sayi_yaz(x, 2).rstrip("0").rstrip(",")


def m2_hesapla(en, boy, birim, adet):
    carpan = BIRIMLER[birim]
    tek = (en * carpan) * (boy * carpan)
    return tek, tek * adet


def kdv_hesapla(haric, oran):
    kdv = haric * oran / 100
    return kdv, haric + kdv


# ---------------------------------------------------------------- ayarlar

def ayar_dosyasi():
    taban = os.environ.get("APPDATA") or os.path.expanduser("~")
    klasor = os.path.join(taban, "ArabaciM2")
    os.makedirs(klasor, exist_ok=True)
    return os.path.join(klasor, "ayarlar.json")


def ayarlari_oku():
    try:
        with open(ayar_dosyasi(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def ayarlari_yaz(veri):
    try:
        with open(ayar_dosyasi(), "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def kaynak_yolu(ad):
    taban = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(taban, ad)


def tcmb_kurlari():
    """TCMB'den güncel döviz satış kurlarını döndürür: {'Dolar': .., 'Euro': .., 'tarih': ..}"""
    istek = urllib.request.Request(TCMB_URL, headers={"User-Agent": "ArabaciM2/1.0"})
    with urllib.request.urlopen(istek, timeout=10) as yanit:
        kok = ET.fromstring(yanit.read())
    sonuc = {"tarih": kok.get("Tarih", "")}
    for cur in kok.findall("Currency"):
        kod = cur.get("Kod")
        satis = cur.findtext("ForexSelling")
        if kod == "USD" and satis:
            sonuc["Dolar"] = float(satis)
        elif kod == "EUR" and satis:
            sonuc["Euro"] = float(satis)
    return sonuc


# ---------------------------------------------------------------- arayüz

class Uygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{UYGULAMA_ADI}  (v{SURUM})")
        self.minsize(1000, 800)
        self.geometry("1060x820")
        try:
            self.iconbitmap(kaynak_yolu("icon.ico"))
        except Exception:
            try:
                self.iconphoto(True, tk.PhotoImage(file=kaynak_yolu("icon.png")))
            except Exception:
                pass

        self.ayarlar = ayarlari_oku()
        self.kurlar = {"Dolar": self.ayarlar.get("kur_Dolar", ""), "Euro": self.ayarlar.get("kur_Euro", "")}
        self._stil()

        defter = ttk.Notebook(self)
        defter.pack(fill="both", expand=True, padx=10, pady=10)

        self.sayfa_fiyat = ttk.Frame(defter, padding=10)
        self.sayfa_kdv = ttk.Frame(defter, padding=10)
        self.sayfa_indirim = ttk.Frame(defter, padding=10)
        defter.add(self.sayfa_fiyat, text="  m² Fiyat ve Kâr  ")
        defter.add(self.sayfa_kdv, text="  KDV Hesaplama  ")
        defter.add(self.sayfa_indirim, text="  İndirim / İskonto  ")

        self._fiyat_sayfasi()
        self._kdv_sayfasi()
        self._indirim_sayfasi()

        self.protocol("WM_DELETE_WINDOW", self._kapat)
        self.after(200, self.kuru_guncelle)

    # ------------------------------------------------------------ görünüm
    def _stil(self):
        font_ad = "Segoe UI" if sys.platform.startswith("win") else "DejaVu Sans"
        for ad in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
            try:
                tkfont.nametofont(ad).configure(family=font_ad, size=11)
            except tk.TclError:
                pass
        s = ttk.Style(self)
        if "vista" in s.theme_names():
            s.theme_use("vista")
        elif "clam" in s.theme_names():
            s.theme_use("clam")
        s.configure("TNotebook.Tab", font=(font_ad, 11, "bold"), padding=(10, 6))
        s.configure("TLabel", font=(font_ad, 11))
        s.configure("Baslik.TLabel", font=(font_ad, 15, "bold"), foreground=KIRMIZI)
        s.configure("Not.TLabel", font=(font_ad, 9), foreground=GRI)
        s.configure("Sonuc.TLabel", font=(font_ad, 12, "bold"))
        s.configure("Buyuk.TLabel", font=(font_ad, 14, "bold"))
        s.configure("Kar.TLabel", font=(font_ad, 16, "bold"), foreground=YESIL)
        s.configure("Zarar.TLabel", font=(font_ad, 16, "bold"), foreground=KIRMIZI)
        s.configure("TLabelframe.Label", font=(font_ad, 12, "bold"), foreground=KIRMIZI)
        s.configure("TEntry", padding=4)
        s.configure("TButton", font=(font_ad, 11, "bold"), padding=(10, 5))
        self.font_ad = font_ad

    def _giris(self, ust, satir, etiket, degisken, genislik=14, sutun=0, ipucu=None):
        ttk.Label(ust, text=etiket).grid(row=satir, column=sutun, sticky="w", pady=4, padx=(16 if sutun else 0, 8))
        e = ttk.Entry(ust, textvariable=degisken, width=genislik, font=(self.font_ad, 12), justify="right")
        e.grid(row=satir, column=sutun + 1, sticky="we", pady=4)
        if ipucu:
            ttk.Label(ust, text=ipucu, style="Not.TLabel").grid(row=satir, column=sutun + 2, sticky="w", padx=6)
        return e

    def _secim(self, ust, satir, etiket, degisken, degerler, sutun=0, genislik=12, serbest=False):
        ttk.Label(ust, text=etiket).grid(row=satir, column=sutun, sticky="w", pady=4, padx=(16 if sutun else 0, 8))
        c = ttk.Combobox(ust, textvariable=degisken, values=degerler, width=genislik,
                         state="normal" if serbest else "readonly", font=(self.font_ad, 12))
        c.grid(row=satir, column=sutun + 1, sticky="we", pady=4)
        return c

    def _sonuc(self, ust, satir, etiket, stil="Sonuc.TLabel", sutun=0):
        ttk.Label(ust, text=etiket).grid(row=satir, column=sutun, sticky="w", pady=3, padx=(0, 8))
        v = tk.StringVar(value="—")
        lbl = ttk.Label(ust, textvariable=v, style=stil, anchor="e")
        lbl.grid(row=satir, column=sutun + 1, columnspan=2, sticky="e", pady=3)
        return v, lbl

    def _izle(self, fonk, *degiskenler):
        for d in degiskenler:
            d.trace_add("write", lambda *_: fonk())

    # ------------------------------------------------------------ sayfa 1: fiyat ve kâr
    def _fiyat_sayfasi(self):
        a = self.ayarlar
        p = self.sayfa_fiyat
        p.columnconfigure(0, weight=1, uniform="k")
        p.columnconfigure(1, weight=1, uniform="k")

        # --- ölçü
        olcu = ttk.LabelFrame(p, text=" 1) Ölçü ", padding=10)
        olcu.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 8))
        for i in range(8):
            olcu.columnconfigure(i, weight=1 if i in (1, 3, 5, 7) else 0)
        self.v_birim = tk.StringVar(value=a.get("birim", "cm"))
        self.v_en = tk.StringVar()
        self.v_boy = tk.StringVar()
        self.v_adet = tk.StringVar(value="1")
        self._secim(olcu, 0, "Ölçü birimi", self.v_birim, list(BIRIMLER), sutun=0, genislik=6)
        self.e_en = self._giris(olcu, 0, "En (soldan sağa)", self.v_en, sutun=2, genislik=10)
        self._giris(olcu, 0, "Boy (yukarıdan aşağı)", self.v_boy, sutun=4, genislik=10)
        self._giris(olcu, 0, "Adet", self.v_adet, sutun=6, genislik=6)
        sat2 = ttk.Frame(olcu)
        sat2.grid(row=1, column=0, columnspan=8, sticky="we", pady=(6, 0))
        self.r_tek_m2 = tk.StringVar(value="—")
        self.r_top_m2 = tk.StringVar(value="—")
        ttk.Label(sat2, text="Bir parça:").pack(side="left")
        ttk.Label(sat2, textvariable=self.r_tek_m2, style="Sonuc.TLabel").pack(side="left", padx=(4, 24))
        ttk.Label(sat2, text="Toplam:").pack(side="left")
        ttk.Label(sat2, textvariable=self.r_top_m2, style="Buyuk.TLabel", foreground=KIRMIZI).pack(side="left", padx=4)

        # --- satış
        satis = ttk.LabelFrame(p, text=" 2) Müşteri Fiyatı (Satış) ", padding=10)
        satis.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        satis.columnconfigure(1, weight=1)
        self.v_satis_m2 = tk.StringVar(value=a.get("satis_m2", ""))
        self.v_satis_kdv = tk.StringVar(value=a.get("satis_kdv", "20"))
        self._giris(satis, 0, "m² satış fiyatı (TL, KDV hariç)", self.v_satis_m2)
        self._secim(satis, 1, "KDV oranı (%)", self.v_satis_kdv, KDV_ORANLARI, serbest=True)
        ttk.Separator(satis).grid(row=2, column=0, columnspan=2, sticky="we", pady=8)
        self.r_satis_haric, _ = self._sonuc(satis, 3, "Toplam fiyat (KDV hariç)")
        self.r_satis_kdv, _ = self._sonuc(satis, 4, "KDV tutarı")
        self.r_satis_dahil, _ = self._sonuc(satis, 5, "KDV dahil toplam", stil="Buyuk.TLabel")

        # --- alış / maliyet
        alis = ttk.LabelFrame(p, text=" 3) Malzeme Maliyeti (Alış) ", padding=10)
        alis.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        alis.columnconfigure(1, weight=1)
        self.v_alis_m2 = tk.StringVar(value=a.get("alis_m2", ""))
        self.v_alis_para = tk.StringVar(value=a.get("alis_para", "Euro"))
        self.v_kur = tk.StringVar()
        self.v_fire = tk.StringVar(value=a.get("fire", "0"))
        self.v_alis_kdv = tk.StringVar(value=a.get("alis_kdv", "20"))
        self._giris(alis, 0, "m² alış fiyatı (KDV hariç)", self.v_alis_m2)
        self._secim(alis, 1, "Para birimi", self.v_alis_para, PARA_BIRIMLERI)
        self._giris(alis, 2, "Kur (1 birim = ? TL)", self.v_kur)
        ttk.Button(alis, text="↻ Güncelle", command=self.kuru_guncelle).grid(row=2, column=2, padx=(6, 0))
        self.v_kur_bilgi = tk.StringVar(value="")
        ttk.Label(alis, textvariable=self.v_kur_bilgi, style="Not.TLabel").grid(row=3, column=0, columnspan=3, sticky="w")
        self._giris(alis, 4, "Fire / kayıp payı (%)", self.v_fire)
        self._secim(alis, 5, "Alış KDV oranı (%)", self.v_alis_kdv, KDV_ORANLARI, serbest=True)
        ttk.Separator(alis).grid(row=6, column=0, columnspan=3, sticky="we", pady=8)
        self.r_alis_tl_m2, _ = self._sonuc(alis, 7, "m² maliyeti (TL)")
        self.r_alis_haric, _ = self._sonuc(alis, 8, "Toplam maliyet (KDV hariç)")
        self.r_alis_kdv, _ = self._sonuc(alis, 9, "KDV tutarı")
        self.r_alis_dahil, _ = self._sonuc(alis, 10, "KDV dahil maliyet", stil="Buyuk.TLabel")

        # --- kâr
        kar = ttk.LabelFrame(p, text=" 4) Kazanç ", padding=10)
        kar.grid(row=2, column=0, columnspan=2, sticky="we", pady=(8, 0))
        for i in range(6):
            kar.columnconfigure(i, weight=1)
        self.r_kar = tk.StringVar(value="—")
        self.r_marj = tk.StringVar(value="—")
        self.r_kar_m2 = tk.StringVar(value="—")
        ttk.Label(kar, text="Kazancınız (KDV hariç):").grid(row=0, column=0, sticky="w")
        self.l_kar = ttk.Label(kar, textvariable=self.r_kar, style="Kar.TLabel")
        self.l_kar.grid(row=0, column=1, sticky="w")
        ttk.Label(kar, text="Kâr oranı (satışa göre):").grid(row=0, column=2, sticky="w")
        ttk.Label(kar, textvariable=self.r_marj, style="Sonuc.TLabel").grid(row=0, column=3, sticky="w")
        ttk.Label(kar, text="m² başına kazanç:").grid(row=0, column=4, sticky="w")
        ttk.Label(kar, textvariable=self.r_kar_m2, style="Sonuc.TLabel").grid(row=0, column=5, sticky="w")

        # --- alt düğmeler ve notlar
        alt = ttk.Frame(p)
        alt.grid(row=3, column=0, columnspan=2, sticky="we", pady=(10, 0))
        tk.Button(alt, text="✖  Temizle", bg=KIRMIZI, fg="white", activebackground="#a61e1e",
                  activeforeground="white", relief="flat", font=(self.font_ad, 12, "bold"),
                  padx=14, pady=6, command=self.fiyat_temizle).pack(side="left")
        tk.Button(alt, text="📋  Müşteri teklifini kopyala", bg=YESIL, fg="white", activebackground="#166b2e",
                  activeforeground="white", relief="flat", font=(self.font_ad, 12, "bold"),
                  padx=14, pady=6, command=self.teklif_kopyala).pack(side="left", padx=10)
        self.v_durum = tk.StringVar(value="")
        ttk.Label(alt, textvariable=self.v_durum, foreground=YESIL).pack(side="left", padx=6)

        ttk.Label(p, style="Not.TLabel", justify="left", text=(
            "• Sonuçlar siz yazdıkça otomatik hesaplanır. Ondalık için virgül ya da nokta kullanabilirsiniz (10,5 veya 10.5).\n"
            "• Kazanç KDV hariç tutarlar üzerinden hesaplanır; KDV devlete gider, kazancınıza dahil değildir.\n"
            "• Kur, Merkez Bankası (TCMB) döviz satış kurudur. İnternet yoksa son kur kullanılır; kutuya elle de yazabilirsiniz."
        )).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self._izle(self.fiyat_hesapla, self.v_birim, self.v_en, self.v_boy, self.v_adet, self.v_satis_m2,
                   self.v_satis_kdv, self.v_alis_m2, self.v_alis_para, self.v_kur, self.v_fire, self.v_alis_kdv)
        self.v_alis_para.trace_add("write", lambda *_: self._kuru_yaz())
        self._kuru_yaz()
        self.e_en.focus_set()

    def _kuru_yaz(self):
        para_b = self.v_alis_para.get()
        if para_b == "TL":
            self.v_kur.set("1")
        else:
            kur = self.kurlar.get(para_b)
            self.v_kur.set(sayi_yaz(kur, 4) if isinstance(kur, (int, float)) and kur else "")

    def kuru_guncelle(self):
        self.v_kur_bilgi.set("Kur alınıyor…")

        def is_parcacigi():
            try:
                k = tcmb_kurlari()
                self.after(0, lambda: self._kur_geldi(k))
            except Exception:
                self.after(0, self._kur_hata)

        threading.Thread(target=is_parcacigi, daemon=True).start()

    def _kur_geldi(self, k):
        for ad in ("Dolar", "Euro"):
            if k.get(ad):
                self.kurlar[ad] = k[ad]
                self.ayarlar[f"kur_{ad}"] = k[ad]
        self.ayarlar["kur_tarih"] = k.get("tarih", "")
        self.v_kur_bilgi.set(f"TCMB {k.get('tarih', '')}  •  $ {sayi_yaz(k.get('Dolar', 0), 4)}  •  € {sayi_yaz(k.get('Euro', 0), 4)}")
        self._kuru_yaz()

    def _kur_hata(self):
        tarih = self.ayarlar.get("kur_tarih")
        self.v_kur_bilgi.set(f"Kur alınamadı. Son kayıtlı kur ({tarih}) kullanılıyor." if tarih
                             else "Kur alınamadı (internet yok?). Kuru elle yazın.")

    def fiyat_hesapla(self):
        en, boy, adet = sayi_oku(self.v_en.get()), sayi_oku(self.v_boy.get()), sayi_oku(self.v_adet.get())
        if adet is None:
            adet = 1
        sonuc_yok = [self.r_tek_m2, self.r_top_m2, self.r_satis_haric, self.r_satis_kdv, self.r_satis_dahil,
                     self.r_alis_tl_m2, self.r_alis_haric, self.r_alis_kdv, self.r_alis_dahil,
                     self.r_kar, self.r_marj, self.r_kar_m2]
        for v in sonuc_yok:
            v.set("—")
        self.v_durum.set("")

        top_m2 = None
        if en is not None and boy is not None:
            tek, top_m2 = m2_hesapla(en, boy, self.v_birim.get(), adet)
            self.r_tek_m2.set(f"{sayi_yaz(tek, 3)} m²")
            self.r_top_m2.set(f"{sayi_yaz(top_m2, 3)} m²")

        satis_haric = None
        s_m2, s_kdv = sayi_oku(self.v_satis_m2.get()), sayi_oku(self.v_satis_kdv.get()) or 0
        if top_m2 is not None and s_m2 is not None:
            satis_haric = top_m2 * s_m2
            kdv, dahil = kdv_hesapla(satis_haric, s_kdv)
            self.r_satis_haric.set(para(satis_haric))
            self.r_satis_kdv.set(para(kdv))
            self.r_satis_dahil.set(para(dahil))

        maliyet_haric = None
        a_m2, kur = sayi_oku(self.v_alis_m2.get()), sayi_oku(self.v_kur.get())
        fire, a_kdv = sayi_oku(self.v_fire.get()) or 0, sayi_oku(self.v_alis_kdv.get()) or 0
        if a_m2 is not None and kur:
            tl_m2 = a_m2 * kur
            self.r_alis_tl_m2.set(para(tl_m2))
            if top_m2 is not None:
                maliyet_haric = top_m2 * (1 + fire / 100) * tl_m2
                kdv, dahil = kdv_hesapla(maliyet_haric, a_kdv)
                self.r_alis_haric.set(para(maliyet_haric))
                self.r_alis_kdv.set(para(kdv))
                self.r_alis_dahil.set(para(dahil))

        if satis_haric is not None and maliyet_haric is not None:
            kar = satis_haric - maliyet_haric
            self.r_kar.set(para(kar))
            self.l_kar.configure(style="Kar.TLabel" if kar >= 0 else "Zarar.TLabel")
            self.r_marj.set(f"% {sayi_yaz(kar / satis_haric * 100, 1)}" if satis_haric else "—")
            self.r_kar_m2.set(para(kar / top_m2) if top_m2 else "—")

    def fiyat_temizle(self):
        for v in (self.v_en, self.v_boy):
            v.set("")
        self.v_adet.set("1")
        self.e_en.focus_set()

    def teklif_kopyala(self):
        en, boy, adet = sayi_oku(self.v_en.get()), sayi_oku(self.v_boy.get()), sayi_oku(self.v_adet.get()) or 1
        s_m2, s_kdv = sayi_oku(self.v_satis_m2.get()), sayi_oku(self.v_satis_kdv.get()) or 0
        if en is None or boy is None or s_m2 is None:
            self.v_durum.set("Önce ölçü ve m² satış fiyatını girin.")
            return
        birim = self.v_birim.get()
        _, top = m2_hesapla(en, boy, birim, adet)
        haric = top * s_m2
        kdv, dahil = kdv_hesapla(haric, s_kdv)
        adet_yazi = f" × {kisa(adet)} adet" if adet != 1 else ""
        metin = (
            "ARABACI REKLAM - Fiyat Teklifi\n"
            f"Ölçü: {kisa(en)} x {kisa(boy)} {birim}{adet_yazi} = {sayi_yaz(top, 2)} m²\n"
            f"m² fiyatı: {para(s_m2)} + KDV\n"
            f"Ara toplam: {para(haric)}\n"
            f"KDV (%{sayi_yaz(s_kdv, 0)}): {para(kdv)}\n"
            f"Genel toplam: {para(dahil)}\n"
            "Tel / WhatsApp: 0534 080 26 79"
        )
        self.clipboard_clear()
        self.clipboard_append(metin)
        self.v_durum.set("Kopyalandı ✓  WhatsApp'a yapıştırabilirsiniz.")

    # ------------------------------------------------------------ sayfa 2: KDV
    def _kdv_sayfasi(self):
        p = self.sayfa_kdv
        p.columnconfigure(1, weight=1)
        ttk.Label(p, text="KDV Hesaplama", style="Baslik.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.k_fiyat = tk.StringVar()
        self.k_oran = tk.StringVar(value="20")
        self.k_tur = tk.StringVar(value="haric")
        self._giris(p, 1, "Fiyat (TL)", self.k_fiyat, genislik=16)
        self._secim(p, 2, "KDV oranı (%)", self.k_oran, KDV_ORANLARI, serbest=True)
        tur = ttk.Frame(p)
        tur.grid(row=3, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Label(tur, text="Girdiğim fiyat:").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(tur, text="KDV hariç", value="haric", variable=self.k_tur).pack(side="left", padx=6)
        ttk.Radiobutton(tur, text="KDV dahil", value="dahil", variable=self.k_tur).pack(side="left", padx=6)
        ttk.Separator(p).grid(row=4, column=0, columnspan=2, sticky="we", pady=10)
        self.k_haric, _ = self._sonuc(p, 5, "KDV hariç tutar")
        self.k_kdv, _ = self._sonuc(p, 6, "KDV tutarı")
        self.k_dahil, _ = self._sonuc(p, 7, "KDV dahil tutar", stil="Buyuk.TLabel")
        self._izle(self.kdv_hesapla, self.k_fiyat, self.k_oran, self.k_tur)

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

    # ------------------------------------------------------------ sayfa 3: indirim
    def _indirim_sayfasi(self):
        p = self.sayfa_indirim
        p.columnconfigure(1, weight=1)
        ttk.Label(p, text="İndirim / İskonto Hesaplama", style="Baslik.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.i_fiyat = tk.StringVar()
        self.i_oran = tk.StringVar()
        self._giris(p, 1, "Fiyat (TL)", self.i_fiyat, genislik=16)
        self._giris(p, 2, "İndirim oranı (%)", self.i_oran, genislik=16)
        ttk.Separator(p).grid(row=3, column=0, columnspan=2, sticky="we", pady=10)
        self.i_tutar, _ = self._sonuc(p, 4, "Yapılan indirim")
        self.i_sonuc, _ = self._sonuc(p, 5, "İndirimli fiyat", stil="Buyuk.TLabel")
        self._izle(self.indirim_hesapla, self.i_fiyat, self.i_oran)

    def indirim_hesapla(self):
        f, o = sayi_oku(self.i_fiyat.get()), sayi_oku(self.i_oran.get())
        if f is None or o is None:
            self.i_tutar.set("—")
            self.i_sonuc.set("—")
            return
        ind = f * o / 100
        self.i_tutar.set(para(ind))
        self.i_sonuc.set(para(f - ind))

    # ------------------------------------------------------------ kapanış
    def _kapat(self):
        self.ayarlar.update({
            "birim": self.v_birim.get(),
            "satis_m2": self.v_satis_m2.get(),
            "satis_kdv": self.v_satis_kdv.get(),
            "alis_m2": self.v_alis_m2.get(),
            "alis_para": self.v_alis_para.get(),
            "fire": self.v_fire.get(),
            "alis_kdv": self.v_alis_kdv.get(),
        })
        ayarlari_yaz(self.ayarlar)
        self.destroy()


if __name__ == "__main__":
    Uygulama().mainloop()
