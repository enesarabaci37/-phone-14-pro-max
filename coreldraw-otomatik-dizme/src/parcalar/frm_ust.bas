Option Explicit

'=====================================================================
'  ATÖLYE ARAÇLARI - OTOMATİK DİZME (NESTING)
'  Seçili nesneleri malzeme (plaka) ölçüsüne en az fire ile dizer.
'  Tüm hesaplar milimetre ile yapılır, ekranda seçilen birim gösterilir.
'=====================================================================

Private Const EPS As Double = 0.0001
Private Const UYG As String = "AtolyeAraclari"
Private Const MAKS_ONIZLEME As Long = 1500
Private Const ARAMA_SAYISI As Long = 40
Private Const VARSAYILAN_AD As String = "Varsayılan"
Private Const VARSAYILAN_AYAR As String = "birim=1;gen=1000;yuk=700;kenar=5;bosluk=3;adet=1;dondur=1;kalite=1;baslangic=0;kontur=1;sayfa=0;cerceve=1;etiket=1;grupla=0;sayfaboyut=0;plakayer=0;plakaara=50;canli=1"
Private Const FONT_NORMAL As String = "Segoe UI"
Private Const FONT_INCE As String = "Segoe UI Semilight"
Private Const FONT_KALIN As String = "Segoe UI Semibold"

' --- MaxRects boş alan listeleri
Private fx() As Double, fy() As Double, fw() As Double, fh() As Double
Private fc As Long
Private tx() As Double, ty() As Double, tw() As Double, th() As Double
Private tc As Long

' --- Son hesap sonucu
Private hesapOK As Boolean
Private hesapMesaj As String
Private adim As String
Private secS() As Object
Private nItem As Long
Private iSrc() As Long, iKop() As Long
Private iW() As Double, iH() As Double
Private rS() As Long, rX() As Double, rY() As Double, rR() As Boolean
Private rSheets As Long
Private ortaKay() As Double
Private pMatW As Double, pMatH As Double, pKenar As Double, pGap As Double
Private pSW As Double, pSH As Double, pBasla As Long, pKontur As Boolean
Private gosterPlaka As Long

' --- Durum
Private olaylar As Collection
Private birimEtiketleri As Collection
Private yukleniyor As Boolean
Private birimCarpan As Double
Private birimIdx As Long

' --- Renkler
Private rAna As Long, rYazi As Long, rAciklama As Long, rCizgi As Long

' --- Kontroller
Private mp As MSForms.MultiPage
Private frOn As MSForms.Frame
Private lblPlaka As MSForms.Label
Private lblBilgi As MSForms.Label
Private WithEvents btnOnceki As MSForms.CommandButton
Private WithEvents btnSonraki As MSForms.CommandButton
Private WithEvents btnOnizle As MSForms.CommandButton
Private WithEvents btnUygula As MSForms.CommandButton
Private WithEvents btnTamam As MSForms.CommandButton
Private WithEvents btnIptal As MSForms.CommandButton
Private WithEvents btnTakas As MSForms.CommandButton
Private WithEvents cmbOnAyar As MSForms.ComboBox
Private WithEvents btnKaydet As MSForms.CommandButton
Private WithEvents btnSil As MSForms.CommandButton
Private WithEvents tglMm As MSForms.ToggleButton
Private WithEvents tglCm As MSForms.ToggleButton
Private WithEvents tglM As MSForms.ToggleButton

Private txtGen As MSForms.TextBox, txtYuk As MSForms.TextBox, txtKenar As MSForms.TextBox
Private txtBosluk As MSForms.TextBox, txtAdet As MSForms.TextBox, txtPlakaAra As MSForms.TextBox
Private chkSayfa As MSForms.CheckBox, chkKontur As MSForms.CheckBox
Private chkCerceve As MSForms.CheckBox, chkEtiket As MSForms.CheckBox, chkGrupla As MSForms.CheckBox
Private chkSayfaBoyut As MSForms.CheckBox, chkCanli As MSForms.CheckBox
Private cmbDondur As MSForms.ComboBox, cmbKalite As MSForms.ComboBox, cmbBasla As MSForms.ComboBox
Private cmbPlakaYer As MSForms.ComboBox

'=====================================================================
'  PENCERE OLUŞTURMA
'=====================================================================
Private Sub UserForm_Initialize()
    Dim pg As Object, lb As MSForms.Label

    yukleniyor = True
    Set olaylar = New Collection
    Set birimEtiketleri = New Collection
    birimCarpan = 1
    birimIdx = 0
    rAna = RGB(20, 169, 154)
    rYazi = RGB(45, 45, 48)
    rAciklama = RGB(130, 130, 130)
    rCizgi = RGB(222, 222, 222)

    Me.Caption = "Atölye Araçları"
    Me.Width = 768
    Me.Height = 580
    Me.BackColor = RGB(247, 247, 247)
    Me.Font.Name = FONT_NORMAL
    Me.Font.Size = 9

    ' ---------- Başlık bandı ----------
    Set lb = Etiket(Me, "", 0, 0, 780, 58)
    lb.BackStyle = fmBackStyleOpaque
    lb.BackColor = RGB(255, 255, 255)
    LogoEkle
    Set lb = Etiket(Me, "Otomatik Dizme", 60, 6, 320, 28)
    YaziStili lb, FONT_KALIN, 16, rYazi
    Set lb = Etiket(Me, "Seçili nesneleri malzemeye en az fire ile yerleştirir", 61, 33, 380, 16)
    YaziStili lb, FONT_INCE, 9, rAciklama

    Set lb = Etiket(Me, "Ölçü birimi", 548, 22, 62, 14)
    YaziStili lb, FONT_INCE, 9, rAciklama
    lb.TextAlign = fmTextAlignRight
    Set tglMm = BirimDugmesi("mm", 616)
    Set tglCm = BirimDugmesi("cm", 660)
    Set tglM = BirimDugmesi("m", 704)

    Set lb = Etiket(Me, "", 0, 58, 780, 2)
    lb.BackStyle = fmBackStyleOpaque
    lb.BackColor = rAna

    ' ---------- Önizleme ----------
    Set frOn = Me.Controls.Add("Forms.Frame.1")
    With frOn
        .Left = 12: .Top = 70: .Width = 400: .Height = 394
        .Caption = ""
        .BackColor = RGB(236, 238, 240)
        .SpecialEffect = fmSpecialEffectFlat
        .BorderStyle = fmBorderStyleSingle
        .BorderColor = rCizgi
    End With

    Set btnOnceki = Dugme(Me, ChrW(&H2039), 12, 470, 26, 22, "Önceki plaka")
    Set lblPlaka = Etiket(Me, "", 42, 473, 100, 16)
    YaziStili lblPlaka, FONT_KALIN, 9, rYazi
    lblPlaka.TextAlign = fmTextAlignCenter
    Set btnSonraki = Dugme(Me, ChrW(&H203A), 146, 470, 26, 22, "Sonraki plaka")

    RenkKutusu 190, RGB(178, 226, 220), RGB(20, 150, 135)
    Set lb = Etiket(Me, "Normal", 204, 473, 44, 14)
    YaziStili lb, FONT_INCE, 8.5, rAciklama
    RenkKutusu 252, RGB(214, 232, 160), RGB(120, 150, 30)
    Set lb = Etiket(Me, "Döndürülmüş", 266, 473, 70, 14)
    YaziStili lb, FONT_INCE, 8.5, rAciklama
    RenkKutusu 340, RGB(255, 255, 255), RGB(220, 40, 40)
    Set lb = Etiket(Me, "Plaka", 354, 473, 50, 14)
    YaziStili lb, FONT_INCE, 8.5, rAciklama

    ' ---------- Alt çubuk ----------
    Set lb = Etiket(Me, "", 0, 500, 780, 1)
    lb.BackStyle = fmBackStyleOpaque
    lb.BackColor = rCizgi
    Set lblBilgi = Etiket(Me, "", 12, 507, 404, 34)
    YaziStili lblBilgi, FONT_NORMAL, 8.5, rYazi
    lblBilgi.WordWrap = True

    Set btnOnizle = Dugme(Me, "Yenile", 424, 510, 70, 28, _
        "Seçimi yeniden okur ve önizlemeyi hesaplar (nesnelere dokunmaz)")
    Set btnUygula = Dugme(Me, "Uygula", 498, 510, 70, 28, _
        "Nesneleri önizlemedeki gibi dizer, pencere açık kalır")
    Set btnTamam = Dugme(Me, "Diz ve Kapat", 572, 510, 102, 28, _
        "Nesneleri dizer ve pencereyi kapatır")
    btnTamam.BackColor = rAna
    btnTamam.ForeColor = RGB(255, 255, 255)
    btnTamam.Font.Name = FONT_KALIN
    Set btnIptal = Dugme(Me, "Kapat", 678, 510, 70, 28, "Hiçbir şey yapmadan kapatır")
    btnIptal.Cancel = True

    ' ---------- Ön ayar ----------
    BolumBasligi Me, "ÖN AYAR", 424, 68, 324
    Set cmbOnAyar = Me.Controls.Add("Forms.ComboBox.1")
    With cmbOnAyar
        .Left = 424: .Top = 84: .Width = 170: .Height = 22
        .Style = fmStyleDropDownList
        .SpecialEffect = fmSpecialEffectFlat
        .BorderStyle = fmBorderStyleSingle
        .BorderColor = RGB(190, 190, 190)
        .Font.Name = FONT_NORMAL: .Font.Size = 9
        .ControlTipText = "Kayıtlı ayarlarınız. Seçince tüm ayarlar tek seferde yüklenir."
    End With
    Set btnKaydet = Dugme(Me, "Kaydet", 598, 83, 74, 24, _
        "Şu anki ayarları bir isimle kaydeder (örn. Folyo baskı + kesim)")
    Set btnSil = Dugme(Me, "Sil", 676, 83, 72, 24, "Seçili ön ayarı siler")
    Set lb = Etiket(Me, "Ayarlarınızı isim vererek kaydedin, sonra listeden tek tıkla seçin." & vbCrLf & _
                        "Örnek: Folyo baskı + kesim, Pleksi 3 mm, Branda", 424, 110, 326, 26)
    YaziStili lb, FONT_INCE, 8, rAciklama

    ' ---------- Sekmeler ----------
    Set mp = Me.Controls.Add("Forms.MultiPage.1")
    With mp
        .Left = 424: .Top = 138: .Width = 326: .Height = 356
        .Font.Name = FONT_NORMAL: .Font.Size = 9
    End With
    mp.Pages(0).Caption = "Ayarlar"
    mp.Pages(1).Caption = "Çıktı ve plaka"

    ' ===== SEKME 1: AYARLAR =====
    Set pg = mp.Pages(0)
    BolumBasligi pg, "MALZEME", 10, 6, 296
    Set txtGen = SayiSatiri(pg, "Genişlik", "Plaka / rulo eni", 22, True, False, 0)
    Set txtYuk = SayiSatiri(pg, "Yükseklik", "Plaka boyu", 52, True, False, 0)

    Set lb = Etiket(pg, "Yön", 10, 82, 150, 14)
    Set lb = Etiket(pg, "En ile boyu yer değiştirir", 10, 95, 156, 13)
    YaziStili lb, FONT_INCE, 7.5, rAciklama
    Set btnTakas = Dugme(pg, ChrW(&H21C4) & "  Çevir", 168, 83, 86, 22, _
        "Genişlik ile yüksekliği yer değiştirir (plakayı yatay / dikey yapar)")

    Set txtKenar = SayiSatiri(pg, "Kenar payı", "Kenarda boş kalacak pay", 112, True, False, 0)
    Set chkSayfa = OnaySatiri(pg, "Sayfa boyutunu malzeme olarak kullan", "", 142)

    BolumBasligi pg, "DİZME", 10, 166, 296
    Set txtBosluk = SayiSatiri(pg, "Boşluk", "Nesneler arası mesafe (kesim payı)", 182, True, False, 0)
    Set txtAdet = SayiSatiri(pg, "Adet", "Her nesneden kaç tane dizilsin", 212, False, True, 1)
    Set cmbDondur = ListeSatiri(pg, "Döndürme", "Yan çevirip daha az fire verir", 242, _
        "Döndürme yok|90° döndürebilir", True, _
        "Nesneler 90° çevrilebilirse plakaya daha sıkı yerleşir. Yönü önemli işlerde 'Döndürme yok' seçin.")
    Set cmbKalite = ListeSatiri(pg, "Arama", "Kaç farklı yerleşim denensin", 272, _
        "Hızlı (anında)|Dengeli (önerilen)|En az fire (yavaş)", True, _
        "Hızlı: tek denemede sonuç.  Dengeli: 30 farklı yerleşim dener.  En az fire: 200'den fazla deneme yapar, biraz bekletebilir.")
    Set cmbBasla = ListeSatiri(pg, "Başlangıç", "Dizme hangi köşeden başlasın", 302, _
        "Zemin - sol|Zemin - orta|Zemin - sağ|Üst - sol|Üst - sağ", True, _
        "Zemin: alttan başlar, yukarı doğru dolar. Orta: zemine ortalanır, sağa sola yayılır. Artan malzeme karşı tarafta toplu kalır.")

    ' ===== SEKME 2: ÇIKTI VE PLAKA =====
    Set pg = mp.Pages(1)
    BolumBasligi pg, "PLAKA ÇIKTISI", 10, 6, 296
    Set chkCerceve = OnaySatiri(pg, "Plaka çerçevesi çiz", "Plaka sınırı ince kırmızı çizgiyle çizilir", 22)
    Set chkEtiket = OnaySatiri(pg, "Plaka bilgisini yaz", "Plaka no, ölçü ve kullanım oranı altına yazılır", 54)
    Set chkGrupla = OnaySatiri(pg, "Plakaları grupla", "Her plakanın nesneleri tek grup olur", 86)
    Set chkSayfaBoyut = OnaySatiri(pg, "Sayfayı plakaya eşitle", "CorelDRAW sayfa ölçüsü plaka ölçüsü olur", 118)
    Set chkKontur = OnaySatiri(pg, "Konturu ölçüye kat", "Kalın dış çizgiler de hesaba girer", 150)

    BolumBasligi pg, "BİRDEN FAZLA PLAKA", 10, 186, 296
    Set cmbPlakaYer = ListeSatiri(pg, "Yerleşim", "Plakalar nereye konsun", 202, _
        "Yan yana (sağa)|Alt alta (aşağı)|Ayrı sayfalara", True, _
        "Tek plakaya sığmazsa yeni plakalar nereye açılsın?")
    Set txtPlakaAra = SayiSatiri(pg, "Plaka arası", "Plakalar arasındaki boşluk", 232, True, False, 0)

    BolumBasligi pg, "GÖRÜNÜM", 10, 266, 296
    Set chkCanli = OnaySatiri(pg, "Canlı önizleme", "Ayar değişince önizleme hemen yenilenir", 282)

    mp.Value = 0

    ' ---------- Ayarları yükle ----------
    OnAyarListesiDoldur
    AyarYukle GetSetting(UYG, "Genel", "Son", VARSAYILAN_AYAR)
    OnAyarSec GetSetting(UYG, "Genel", "SonOnAyar", VARSAYILAN_AD)

    yukleniyor = False
    AlanDurumlari
    Hesapla
    gosterPlaka = 1
    Ciz
End Sub

'---------------- Kontrol yardımcıları ----------------
Private Function Etiket(kap As Object, ByVal yazi As String, ByVal l As Single, ByVal t As Single, _
                        ByVal w As Single, ByVal h As Single) As MSForms.Label
    Dim lb As MSForms.Label
    Set lb = kap.Controls.Add("Forms.Label.1")
    lb.Caption = yazi
    lb.Left = l: lb.Top = t: lb.Width = w: lb.Height = h
    lb.BackStyle = fmBackStyleTransparent
    lb.Font.Name = FONT_NORMAL
    lb.Font.Size = 9
    lb.ForeColor = rYazi
    Set Etiket = lb
End Function

Private Sub YaziStili(ctl As Object, ByVal fontAdi As String, ByVal boyut As Single, ByVal renk As Long)
    ctl.Font.Name = fontAdi
    ctl.Font.Size = boyut
    ctl.ForeColor = renk
End Sub

Private Function Dugme(kap As Object, ByVal yazi As String, ByVal l As Single, ByVal t As Single, _
                       ByVal w As Single, ByVal h As Single, ByVal ipucu As String) As MSForms.CommandButton
    Dim b As MSForms.CommandButton
    Set b = kap.Controls.Add("Forms.CommandButton.1")
    b.Caption = yazi
    b.Left = l: b.Top = t: b.Width = w: b.Height = h
    b.Font.Name = FONT_NORMAL
    b.Font.Size = 9
    b.ControlTipText = ipucu
    b.TakeFocusOnClick = False
    Set Dugme = b
End Function

Private Function BirimDugmesi(ByVal yazi As String, ByVal l As Single) As MSForms.ToggleButton
    Dim b As MSForms.ToggleButton
    Set b = Me.Controls.Add("Forms.ToggleButton.1")
    b.Caption = yazi
    b.Left = l: b.Top = 17: b.Width = 42: b.Height = 24
    b.Font.Name = FONT_NORMAL
    b.Font.Size = 9
    b.ControlTipText = "Tüm ölçüler bu birimle gösterilir. Değiştirince değerler otomatik çevrilir."
    Set BirimDugmesi = b
End Function

Private Sub RenkKutusu(ByVal l As Single, ByVal ic As Long, ByVal kenar As Long)
    Dim lb As MSForms.Label
    Set lb = Etiket(Me, "", l, 475, 10, 10)
    lb.BackStyle = fmBackStyleOpaque
    lb.BackColor = ic
    lb.BorderStyle = fmBorderStyleSingle
    lb.BorderColor = kenar
End Sub

Private Sub BolumBasligi(kap As Object, ByVal metin As String, ByVal l As Single, ByVal t As Single, ByVal w As Single)
    Dim lb As MSForms.Label, x As Single
    Set lb = Etiket(kap, metin, l, t, w, 14)
    YaziStili lb, FONT_KALIN, 8, rAna
    x = l + Len(metin) * 6.2 + 8
    If x < l + w Then
        Set lb = Etiket(kap, "", x, t + 7, l + w - x, 1)
        lb.BackStyle = fmBackStyleOpaque
        lb.BackColor = rCizgi
    End If
End Sub

Private Sub LogoEkle()
    Dim im As MSForms.Image, yol As String
    On Error Resume Next
    yol = modAtolye.LogoYolu()
    If yol = "" Then Exit Sub
    Set im = Me.Controls.Add("Forms.Image.1")
    im.Left = 14: im.Top = 10: im.Width = 39: im.Height = 39
    im.BorderStyle = fmBorderStyleNone
    im.BackStyle = fmBackStyleTransparent
    im.PictureSizeMode = fmPictureSizeModeZoom
    Set im.Picture = LoadPicture(yol)
End Sub

Private Function SayiSatiri(kap As Object, ByVal yazi As String, ByVal aciklama As String, ByVal t As Single, _
                            ByVal uzunluk As Boolean, ByVal tamsayi As Boolean, ByVal minD As Double) As MSForms.TextBox
    Dim l As MSForms.Label, tb As MSForms.TextBox, sp As MSForms.SpinButton, lb As MSForms.Label, o As clsOlay

    Set l = Etiket(kap, yazi, 10, t, 150, 14)
    Set l = Etiket(kap, aciklama, 10, t + 13, 156, 13)
    YaziStili l, FONT_INCE, 7.5, rAciklama

    Set tb = kap.Controls.Add("Forms.TextBox.1")
    tb.Left = 168: tb.Top = t + 2: tb.Width = 72: tb.Height = 20
    tb.TextAlign = fmTextAlignRight
    tb.Font.Name = FONT_NORMAL: tb.Font.Size = 9.5
    tb.SpecialEffect = fmSpecialEffectFlat
    tb.BorderStyle = fmBorderStyleSingle
    tb.BorderColor = RGB(190, 190, 190)
    tb.ControlTipText = aciklama

    Set sp = kap.Controls.Add("Forms.SpinButton.1")
    sp.Left = 241: sp.Top = t + 2: sp.Width = 13: sp.Height = 20
    sp.Min = -100000: sp.Max = 100000: sp.Value = 0

    Set lb = Etiket(kap, "", 258, t + 5, 44, 14)
    YaziStili lb, FONT_INCE, 8.5, rAciklama
    If uzunluk Then
        birimEtiketleri.Add lb
        lb.Caption = "mm"
    ElseIf tamsayi Then
        lb.Caption = "adet"
    End If

    Set o = New clsOlay
    Set o.Frm = Me
    Set o.tb = tb
    Set o.sp = sp
    o.Tamsayi = tamsayi
    o.MinDeger = minD
    olaylar.Add o

    Set SayiSatiri = tb
End Function

Private Function ListeSatiri(kap As Object, ByVal yazi As String, ByVal aciklama As String, ByVal t As Single, _
                             ByVal liste As String, ByVal olayEkle As Boolean, ByVal ipucu As String) As MSForms.ComboBox
    Dim l As MSForms.Label, cb As MSForms.ComboBox, o As clsOlay, s As Variant

    Set l = Etiket(kap, yazi, 10, t, 150, 14)
    l.ControlTipText = ipucu
    Set l = Etiket(kap, aciklama, 10, t + 13, 156, 13)
    YaziStili l, FONT_INCE, 7.5, rAciklama
    l.ControlTipText = ipucu

    Set cb = kap.Controls.Add("Forms.ComboBox.1")
    cb.Left = 168: cb.Top = t + 2: cb.Width = 136: cb.Height = 20
    cb.Style = fmStyleDropDownList
    cb.SpecialEffect = fmSpecialEffectFlat
    cb.BorderStyle = fmBorderStyleSingle
    cb.BorderColor = RGB(190, 190, 190)
    cb.Font.Name = FONT_NORMAL: cb.Font.Size = 9
    cb.ControlTipText = ipucu
    For Each s In Split(liste, "|")
        cb.AddItem CStr(s)
    Next s
    cb.ListIndex = 0

    If olayEkle Then
        Set o = New clsOlay
        Set o.Frm = Me
        Set o.cb = cb
        olaylar.Add o
    End If
    Set ListeSatiri = cb
End Function

Private Function OnaySatiri(kap As Object, ByVal yazi As String, ByVal aciklama As String, _
                            ByVal t As Single) As MSForms.CheckBox
    Dim ch As MSForms.CheckBox, o As clsOlay, lb As MSForms.Label
    Set ch = kap.Controls.Add("Forms.CheckBox.1")
    ch.Caption = yazi
    ch.Left = 8: ch.Top = t: ch.Width = 296: ch.Height = 17
    ch.BackStyle = fmBackStyleTransparent
    ch.Font.Name = FONT_NORMAL: ch.Font.Size = 9
    ch.ForeColor = rYazi
    ch.ControlTipText = IIf(aciklama = "", yazi, aciklama)
    If aciklama <> "" Then
        Set lb = Etiket(kap, aciklama, 26, t + 15, 276, 13)
        YaziStili lb, FONT_INCE, 7.5, rAciklama
    End If
    Set o = New clsOlay
    Set o.Frm = Me
    Set o.ch = ch
    olaylar.Add o
    Set OnaySatiri = ch
End Function

'=====================================================================
'  SAYI / BİRİM YARDIMCILARI (clsOlay da kullanır)
'=====================================================================
Public Function SayiOku(ByVal s As String) As Double
    s = Replace(Trim$(s), ",", ".")
    SayiOku = Val(s)
End Function

Public Function SayiYaz(ByVal v As Double) As String
    Dim s As String
    s = Format(Round(v, 4), "0.####")
    If VBA.Right$(s, 1) = "," Or VBA.Right$(s, 1) = "." Then s = VBA.Left$(s, Len(s) - 1)
    SayiYaz = s
End Function

Public Function AdimBuyuklugu() As Double
    Select Case birimIdx
        Case 1: AdimBuyuklugu = 0.1
        Case 2: AdimBuyuklugu = 0.01
        Case Else: AdimBuyuklugu = 1
    End Select
End Function

Private Function BirimCarpani(ByVal idx As Long) As Double
    Select Case idx
        Case 1: BirimCarpani = 10
        Case 2: BirimCarpani = 1000
        Case Else: BirimCarpani = 1
    End Select
End Function

Private Function BirimAdi() As String
    Select Case birimIdx
        Case 1: BirimAdi = "cm"
        Case 2: BirimAdi = "m"
        Case Else: BirimAdi = "mm"
    End Select
End Function

Private Function OlcuYazi(ByVal mm As Double) As String
    OlcuYazi = SayiYaz(mm / birimCarpan)
End Function

Private Sub BirimEtiketleriniGuncelle()
    Dim lb As Variant
    For Each lb In birimEtiketleri
        lb.Caption = BirimAdi()
    Next lb
End Sub

Private Sub BirimSec(ByVal idx As Long)
    Dim yeni As Double, eski As Boolean
    If idx < 0 Or idx > 2 Then idx = 1
    yeni = BirimCarpani(idx)
    eski = yukleniyor
    yukleniyor = True
    If Not eski And idx <> birimIdx Then
        BirimCevir txtGen, yeni
        BirimCevir txtYuk, yeni
        BirimCevir txtKenar, yeni
        BirimCevir txtBosluk, yeni
        BirimCevir txtPlakaAra, yeni
    End If
    birimIdx = idx
    birimCarpan = yeni
    tglMm.Value = (idx = 0)
    tglCm.Value = (idx = 1)
    tglM.Value = (idx = 2)
    BirimDugmeRengi tglMm
    BirimDugmeRengi tglCm
    BirimDugmeRengi tglM
    BirimEtiketleriniGuncelle
    yukleniyor = eski
    AyarDegisti
End Sub

Private Sub BirimDugmeRengi(b As MSForms.ToggleButton)
    If b.Value Then
        b.BackColor = rAna
        b.ForeColor = RGB(255, 255, 255)
        b.Font.Name = FONT_KALIN
    Else
        b.BackColor = RGB(255, 255, 255)
        b.ForeColor = rYazi
        b.Font.Name = FONT_NORMAL
    End If
End Sub

Private Sub BirimCevir(tb As MSForms.TextBox, ByVal yeni As Double)
    tb.Text = SayiYaz(SayiOku(tb.Text) * birimCarpan / yeni)
End Sub

Private Sub tglMm_Click()
    If Not yukleniyor Then BirimSec 0
End Sub

Private Sub tglCm_Click()
    If Not yukleniyor Then BirimSec 1
End Sub

Private Sub tglM_Click()
    If Not yukleniyor Then BirimSec 2
End Sub

'=====================================================================
'  AYAR DEĞİŞİNCE
'=====================================================================
Public Sub AyarDegisti()
    If yukleniyor Then Exit Sub
    AlanDurumlari
    If chkCanli.Value Then
        Hesapla
        gosterPlaka = 1
        Ciz
    Else
        lblBilgi.Caption = "Ayarlar değişti. Önizlemeyi görmek için 'Yenile' düğmesine basın."
    End If
End Sub

Private Sub AlanDurumlari()
    Dim eski As Boolean, w As Double, h As Double
    eski = yukleniyor
    If chkSayfa.Value Then
        If SayfaBoyutu(w, h) Then
            yukleniyor = True
            txtGen.Text = OlcuYazi(w)
            txtYuk.Text = OlcuYazi(h)
            yukleniyor = eski
        End If
        txtGen.Enabled = False: txtYuk.Enabled = False: btnTakas.Enabled = False
    Else
        txtGen.Enabled = True: txtYuk.Enabled = True: btnTakas.Enabled = True
    End If
    txtPlakaAra.Enabled = (cmbPlakaYer.ListIndex <> 2)
End Sub

Private Function SayfaBoyutu(ByRef w As Double, ByRef h As Double) As Boolean
    Dim doc As Object, eskiBirim As Long
    On Error GoTo Yok
    Set doc = AktifBelge()
    If doc Is Nothing Then Exit Function
    eskiBirim = doc.Unit
    doc.Unit = cdrMillimeter
    w = doc.ActivePage.SizeWidth
    h = doc.ActivePage.SizeHeight
    doc.Unit = eskiBirim
    SayfaBoyutu = True
    Exit Function
Yok:
    SayfaBoyutu = False
End Function

'=====================================================================
'  DÜĞMELER
'=====================================================================
Private Sub btnOnizle_Click()
    Hesapla
    gosterPlaka = 1
    Ciz
End Sub

Private Sub btnOnceki_Click()
    gosterPlaka = gosterPlaka - 1
    Ciz
End Sub

Private Sub btnSonraki_Click()
    gosterPlaka = gosterPlaka + 1
    Ciz
End Sub

Private Sub btnTakas_Click()
    Dim s As String, eski As Boolean
    eski = yukleniyor
    yukleniyor = True
    s = txtGen.Text
    txtGen.Text = txtYuk.Text
    txtYuk.Text = s
    yukleniyor = eski
    AyarDegisti
End Sub

Private Sub btnUygula_Click()
    SonAyarlariKaydet
    Uygula
End Sub

Private Sub btnTamam_Click()
    SonAyarlariKaydet
    If Uygula() Then Unload Me
End Sub

Private Sub btnIptal_Click()
    SonAyarlariKaydet
    Unload Me
End Sub

Private Sub UserForm_QueryClose(Cancel As Integer, CloseMode As Integer)
    SonAyarlariKaydet
End Sub

'=====================================================================
'  ÖN AYARLAR (kayıt defterinde saklanır)
'=====================================================================
Private Sub OnAyarListesiDoldur()
    Dim v As Variant, i As Long, eski As Boolean
    If GetSetting(UYG, "OnAyar", VARSAYILAN_AD, "") = "" Then
        SaveSetting UYG, "OnAyar", VARSAYILAN_AD, VARSAYILAN_AYAR
    End If
    eski = yukleniyor
    yukleniyor = True
    cmbOnAyar.Clear
    v = GetAllSettings(UYG, "OnAyar")
    If IsArray(v) Then
        For i = LBound(v, 1) To UBound(v, 1)
            cmbOnAyar.AddItem CStr(v(i, 0))
        Next i
    End If
    yukleniyor = eski
End Sub

Private Sub OnAyarSec(ByVal ad As String)
    Dim i As Long, eski As Boolean
    eski = yukleniyor
    yukleniyor = True
    For i = 0 To cmbOnAyar.ListCount - 1
        If cmbOnAyar.List(i) = ad Then cmbOnAyar.ListIndex = i: Exit For
    Next i
    yukleniyor = eski
End Sub

Private Sub cmbOnAyar_Change()
    Dim s As String
    If yukleniyor Then Exit Sub
    If cmbOnAyar.ListIndex < 0 Then Exit Sub
    s = GetSetting(UYG, "OnAyar", cmbOnAyar.Text, "")
    If s = "" Then Exit Sub
    AyarYukle s
    SaveSetting UYG, "Genel", "SonOnAyar", cmbOnAyar.Text
    lblBilgi.Caption = "'" & cmbOnAyar.Text & "' ön ayarı yüklendi."
    AyarDegisti
End Sub

Private Sub btnKaydet_Click()
    Dim ad As String, onerilen As String
    onerilen = cmbOnAyar.Text
    If onerilen = VARSAYILAN_AD Then onerilen = ""
    ad = InputBox("Bu ayarlara bir isim verin:" & vbCrLf & vbCrLf & _
                  "Örnek: Folyo baskı + kesim, Pleksi 3 mm, Branda 5 m" & vbCrLf & vbCrLf & _
                  "Aynı isim varsa üzerine yazılır.", "Ön ayar kaydet", onerilen)
    ad = Trim$(Replace(ad, "\", ""))
    If ad = "" Then Exit Sub
    If GetSetting(UYG, "OnAyar", ad, "") <> "" And ad <> cmbOnAyar.Text Then
        If MsgBox("'" & ad & "' adında bir ön ayar zaten var. Üzerine yazılsın mı?", _
                  vbQuestion + vbYesNo, "Ön ayar") <> vbYes Then Exit Sub
    End If
    SaveSetting UYG, "OnAyar", ad, AyarMetni()
    SaveSetting UYG, "Genel", "SonOnAyar", ad
    OnAyarListesiDoldur
    OnAyarSec ad
    lblBilgi.Caption = "'" & ad & "' ön ayarı kaydedildi. Listeden seçerek tekrar kullanabilirsiniz."
End Sub

Private Sub btnSil_Click()
    Dim ad As String
    ad = cmbOnAyar.Text
    If ad = "" Then Exit Sub
    If ad = VARSAYILAN_AD Then
        MsgBox "Varsayılan ön ayar silinemez.", vbInformation, "Ön ayar"
        Exit Sub
    End If
    If MsgBox("'" & ad & "' ön ayarı silinsin mi?", vbQuestion + vbYesNo, "Ön ayar") <> vbYes Then Exit Sub
    On Error Resume Next
    DeleteSetting UYG, "OnAyar", ad
    On Error GoTo 0
    OnAyarListesiDoldur
    OnAyarSec VARSAYILAN_AD
End Sub

Private Sub SonAyarlariKaydet()
    On Error Resume Next
    SaveSetting UYG, "Genel", "Son", AyarMetni()
End Sub

' Ayarlar uzunluklar mm olarak, nokta ondalıkla saklanır
Private Function AyarMetni() As String
    Dim s As String
    s = "birim=" & birimIdx
    s = s & ";gen=" & MmMetin(txtGen.Text)
    s = s & ";yuk=" & MmMetin(txtYuk.Text)
    s = s & ";kenar=" & MmMetin(txtKenar.Text)
    s = s & ";bosluk=" & MmMetin(txtBosluk.Text)
    s = s & ";adet=" & CLng(SayiOku(txtAdet.Text))
    s = s & ";dondur=" & cmbDondur.ListIndex
    s = s & ";kalite=" & cmbKalite.ListIndex
    s = s & ";baslangic=" & cmbBasla.ListIndex
    s = s & ";kontur=" & IIf(chkKontur.Value, 1, 0)
    s = s & ";sayfa=" & IIf(chkSayfa.Value, 1, 0)
    s = s & ";cerceve=" & IIf(chkCerceve.Value, 1, 0)
    s = s & ";etiket=" & IIf(chkEtiket.Value, 1, 0)
    s = s & ";grupla=" & IIf(chkGrupla.Value, 1, 0)
    s = s & ";sayfaboyut=" & IIf(chkSayfaBoyut.Value, 1, 0)
    s = s & ";plakayer=" & cmbPlakaYer.ListIndex
    s = s & ";plakaara=" & MmMetin(txtPlakaAra.Text)
    s = s & ";canli=" & IIf(chkCanli.Value, 1, 0)
    AyarMetni = s
End Function

Private Function MmMetin(ByVal ekranDegeri As String) As String
    MmMetin = Trim$(Str$(Round(SayiOku(ekranDegeri) * birimCarpan, 4)))
End Function

Private Function Deger(ByVal s As String, ByVal anahtar As String, ByVal vars As Double) As Double
    Dim p As Variant, kv() As String
    Deger = vars
    For Each p In Split(s, ";")
        kv = Split(CStr(p), "=")
        If UBound(kv) = 1 Then
            If LCase$(Trim$(kv(0))) = anahtar Then Deger = Val(kv(1)): Exit Function
        End If
    Next p
End Function

Private Sub AyarYukle(ByVal s As String)
    Dim eski As Boolean
    eski = yukleniyor
    yukleniyor = True

    BirimSec CLng(Deger(s, "birim", 1))

    txtGen.Text = OlcuYazi(Deger(s, "gen", 1000))
    txtYuk.Text = OlcuYazi(Deger(s, "yuk", 700))
    txtKenar.Text = OlcuYazi(Deger(s, "kenar", 5))
    txtBosluk.Text = OlcuYazi(Deger(s, "bosluk", 3))
    txtAdet.Text = SayiYaz(Deger(s, "adet", 1))
    ListeAyarla cmbDondur, Deger(s, "dondur", 1)
    ListeAyarla cmbKalite, Deger(s, "kalite", 1)
    ListeAyarla cmbBasla, Deger(s, "baslangic", 0)
    chkKontur.Value = (Deger(s, "kontur", 1) = 1)
    chkSayfa.Value = (Deger(s, "sayfa", 0) = 1)
    chkCerceve.Value = (Deger(s, "cerceve", 1) = 1)
    chkEtiket.Value = (Deger(s, "etiket", 1) = 1)
    chkGrupla.Value = (Deger(s, "grupla", 0) = 1)
    chkSayfaBoyut.Value = (Deger(s, "sayfaboyut", 0) = 1)
    ListeAyarla cmbPlakaYer, Deger(s, "plakayer", 0)
    txtPlakaAra.Text = OlcuYazi(Deger(s, "plakaara", 50))
    chkCanli.Value = (Deger(s, "canli", 1) = 1)

    yukleniyor = eski
End Sub

Private Sub ListeAyarla(cb As MSForms.ComboBox, ByVal idx As Double)
    If idx >= 0 And idx < cb.ListCount Then
        cb.ListIndex = CLng(idx)
    Else
        cb.ListIndex = 0
    End If
End Sub

'=====================================================================
'  HESAP (CorelDRAW'daki nesnelere dokunmaz)
'=====================================================================
Private Sub Hesapla()
    Dim doc As Object, sr As Object, eskiBirim As Long
    Dim m As Long, n As Long, i As Long, c As Long, k As Long, adet As Long
    Dim bx As Double, byy As Double, bw As Double, bh As Double, sag As Double
    Dim w0() As Double, h0() As Double, aw() As Double, ah() As Double
    Dim matW As Double, matH As Double, usW As Double, usH As Double
    Dim allowRot As Boolean, kalite As Long
    Dim sh As Shape

    hesapOK = False
    rSheets = 0
    nItem = 0
    On Error GoTo Hata

    adim = "belge"
    Set doc = AktifBelge()
    If doc Is Nothing Then
        hesapMesaj = "Açık bir CorelDRAW belgesi yok."
        Exit Sub
    End If
    adim = "seçim"
    Set sr = SecimAl(doc)
    m = SecimDiziyeAl(sr)
    If m = 0 Then
        hesapMesaj = "Başlamak için dizilecek nesneleri CorelDRAW'da seçin" & vbCrLf & _
                     "ve 'Yenile' düğmesine basın." & vbCrLf & vbCrLf & _
                     "Bu pencere açıkken de seçim yapabilirsiniz."
        Exit Sub
    End If

    ' --- Parametreler (mm)
    adim = "ayarlar"
    If chkSayfa.Value Then
        If Not SayfaBoyutu(matW, matH) Then hesapMesaj = "Sayfa boyutu okunamadı.": Exit Sub
    Else
        matW = SayiOku(txtGen.Text) * birimCarpan
        matH = SayiOku(txtYuk.Text) * birimCarpan
    End If
    pKenar = SayiOku(txtKenar.Text) * birimCarpan
    pGap = SayiOku(txtBosluk.Text) * birimCarpan
    adet = CLng(SayiOku(txtAdet.Text))
    allowRot = (cmbDondur.ListIndex = 1)
    kalite = cmbKalite.ListIndex
    pBasla = cmbBasla.ListIndex
    pKontur = CBool(chkKontur.Value)

    If matW <= 0 Or matH <= 0 Then hesapMesaj = "Malzeme genişliği ve yüksekliği 0'dan büyük olmalı.": Exit Sub
    If pKenar < 0 Or pGap < 0 Then hesapMesaj = "Boşluk ve kenar payı negatif olamaz.": Exit Sub
    If adet < 1 Then hesapMesaj = "Adet en az 1 olmalı.": Exit Sub
    usW = matW - 2 * pKenar
    usH = matH - 2 * pKenar
    If usW <= 0 Or usH <= 0 Then hesapMesaj = "Kenar payı malzemeye göre çok büyük.": Exit Sub
    If m * adet > 5000 Then hesapMesaj = "En fazla 5000 nesne dizilebilir (şu an " & m * adet & ").": Exit Sub

    ' --- Nesne ölçüleri
    ReDim w0(1 To m): ReDim h0(1 To m)
    eskiBirim = doc.Unit
    doc.Unit = cdrMillimeter
    For i = 1 To m
        adim = "nesne ölçüleri " & i & "/" & m
        Set sh = secS(i)
        sh.GetBoundingBox bx, byy, bw, bh, pKontur
        w0(i) = bw: h0(i) = bh
    Next i
    doc.Unit = eskiBirim

    adim = "ayarlar"
    For i = 1 To m
        If Not ((w0(i) <= usW + EPS And h0(i) <= usH + EPS) Or _
                (allowRot And h0(i) <= usW + EPS And w0(i) <= usH + EPS)) Then
            hesapMesaj = "Bir nesne malzemeye sığmıyor:" & vbCrLf & _
                         OlcuYazi(w0(i)) & " x " & OlcuYazi(h0(i)) & " " & BirimAdi() & vbCrLf & _
                         "Kullanılabilir alan: " & OlcuYazi(usW) & " x " & OlcuYazi(usH) & " " & BirimAdi() & _
                         IIf(allowRot, "", vbCrLf & "(Döndürmeye izin vermeyi deneyin.)")
            Exit Sub
        End If
    Next i

    ' --- Parça listesi
    n = m * adet
    ReDim iSrc(1 To n): ReDim iKop(1 To n): ReDim iW(1 To n): ReDim iH(1 To n)
    ReDim aw(1 To n): ReDim ah(1 To n)
    k = 0
    For i = 1 To m
        For c = 1 To adet
            k = k + 1
            iSrc(k) = i: iKop(k) = c
            iW(k) = w0(i): iH(k) = h0(i)
            aw(k) = w0(i) + pGap: ah(k) = h0(i) + pGap
        Next c
    Next i
    nItem = n
    pMatW = matW: pMatH = matH
    pSW = usW + pGap: pSH = usH + pGap

    adim = "yerleşim hesabı"
    lblBilgi.Caption = "Hesaplanıyor..."
    DoEvents
    rSheets = EnIyiYerlesim(n, aw, ah, pSW, pSH, allowRot, kalite, ARAMA_SAYISI)
    If rSheets <= 0 Then
        hesapMesaj = "Yerleşim bulunamadı."
        Exit Sub
    End If

    ' Zemin - orta için her plakadaki kaydırma
    ReDim ortaKay(1 To rSheets)
    For k = 1 To n
        If rR(k) Then
            sag = rX(k) + ah(k)
        Else
            sag = rX(k) + aw(k)
        End If
        If sag > ortaKay(rS(k)) Then ortaKay(rS(k)) = sag
    Next k
    For c = 1 To rSheets
        ortaKay(c) = (pSW - ortaKay(c)) / 2
        If ortaKay(c) < 0 Then ortaKay(c) = 0
    Next c

    hesapOK = True
    Exit Sub

Hata:
    hesapMesaj = "Hesaplama hatası (" & adim & "): " & Err.Description & " [" & Err.Number & "]"
    hesapOK = False
End Sub

'=====================================================================
'  ÖNİZLEME ÇİZİMİ
'=====================================================================
Private Sub Ciz()
    Dim PW As Double, PH As Double, sc As Double, sx As Double, sy As Double
    Dim k As Long, c As Long, adet As Long
    Dim x As Double, y As Double, w As Double, h As Double, dolu As Double, topDolu As Double
    Dim lb As MSForms.Label

    frOn.Controls.Clear

    If Not hesapOK Then
        Set lb = frOn.Controls.Add("Forms.Label.1")
        With lb
            .Left = 30: .Top = 150: .Width = frOn.InsideWidth - 60: .Height = 110
            .Caption = hesapMesaj
            .TextAlign = fmTextAlignCenter
            .BackStyle = fmBackStyleTransparent
            .Font.Name = FONT_INCE
            .Font.Size = 10.5
            .ForeColor = RGB(110, 110, 110)
        End With
        lblPlaka.Caption = ""
        lblBilgi.Caption = ""
        btnOnceki.Enabled = False
        btnSonraki.Enabled = False
        Exit Sub
    End If

    If gosterPlaka < 1 Then gosterPlaka = 1
    If gosterPlaka > rSheets Then gosterPlaka = rSheets

    PW = frOn.InsideWidth
    PH = frOn.InsideHeight
    sc = Min2((PW - 30) / pMatW, (PH - 30) / pMatH)
    sx = (PW - pMatW * sc) / 2
    sy = (PH - pMatH * sc) / 2

    ' Gölge
    Set lb = frOn.Controls.Add("Forms.Label.1")
    With lb
        .Left = sx + 3: .Top = sy + 3: .Width = Max2(pMatW * sc, 2): .Height = Max2(pMatH * sc, 2)
        .BackColor = RGB(212, 215, 219)
    End With
    ' Plaka
    Set lb = frOn.Controls.Add("Forms.Label.1")
    With lb
        .Left = sx: .Top = sy: .Width = Max2(pMatW * sc, 2): .Height = Max2(pMatH * sc, 2)
        .BackColor = RGB(255, 255, 255)
        .BorderStyle = fmBorderStyleSingle
        .BorderColor = RGB(220, 40, 40)
    End With
    ' Kenar payı
    If pKenar > 0 Then
        Set lb = frOn.Controls.Add("Forms.Label.1")
        With lb
            .Left = sx + pKenar * sc: .Top = sy + pKenar * sc
            .Width = Max2((pMatW - 2 * pKenar) * sc, 1): .Height = Max2((pMatH - 2 * pKenar) * sc, 1)
            .BackStyle = fmBackStyleTransparent
            .BorderStyle = fmBorderStyleSingle
            .BorderColor = RGB(215, 215, 215)
        End With
    End If

    ' Nesneler
    For k = 1 To nItem
        topDolu = topDolu + iW(k) * iH(k)
        If rS(k) = gosterPlaka Then
            Konum k, x, y, w, h
            adet = adet + 1
            dolu = dolu + iW(k) * iH(k)
            If c < MAKS_ONIZLEME Then
                c = c + 1
                Set lb = frOn.Controls.Add("Forms.Label.1")
                With lb
                    .Left = sx + (pKenar + x) * sc
                    .Top = sy + (pMatH - pKenar - y - h) * sc
                    .Width = Max2(w * sc, 1)
                    .Height = Max2(h * sc, 1)
                    .BorderStyle = fmBorderStyleSingle
                    If rR(k) Then
                        .BackColor = RGB(214, 232, 160)
                        .BorderColor = RGB(120, 150, 30)
                    Else
                        .BackColor = RGB(178, 226, 220)
                        .BorderColor = RGB(20, 150, 135)
                    End If
                    .ControlTipText = "Nesne " & iSrc(k) & IIf(iKop(k) > 1, " (kopya " & iKop(k) & ")", "") & ": " & _
                                      OlcuYazi(iW(k)) & " x " & OlcuYazi(iH(k)) & " " & BirimAdi() & _
                                      IIf(rR(k), "  - 90° döndürüldü", "")
                End With
            End If
        End If
    Next k

    lblPlaka.Caption = "Plaka " & gosterPlaka & " / " & rSheets
    btnOnceki.Enabled = (gosterPlaka > 1)
    btnSonraki.Enabled = (gosterPlaka < rSheets)

    lblBilgi.Caption = "Bu plaka:  " & adet & " nesne   •   Kullanım %" & Format(100 * dolu / (pMatW * pMatH), "0.0") & _
                       "   •   Fire %" & Format(100 - 100 * dolu / (pMatW * pMatH), "0.0") & vbCrLf & _
                       "Toplam:  " & nItem & " nesne, " & rSheets & " plaka (" & OlcuYazi(pMatW) & " x " & _
                       OlcuYazi(pMatH) & " " & BirimAdi() & ")   •   Ortalama kullanım %" & _
                       Format(100 * topDolu / (rSheets * pMatW * pMatH), "0.0")
End Sub

' k. parçanın plaka içi konumu (kenar payı hariç, başlangıç noktasına göre) ve gerçek ölçüsü (mm)
Private Sub Konum(ByVal k As Long, ByRef x As Double, ByRef y As Double, ByRef w As Double, ByRef h As Double)
    If rR(k) Then
        w = iH(k): h = iW(k)
    Else
        w = iW(k): h = iH(k)
    End If
    x = rX(k)
    y = rY(k)
    Select Case pBasla
        Case 1  ' Zemin - orta
            x = x + ortaKay(rS(k))
        Case 2  ' Zemin - sağ
            x = pSW - x - (w + pGap)
        Case 3  ' Üst - sol
            y = pSH - y - (h + pGap)
        Case 4  ' Üst - sağ
            x = pSW - x - (w + pGap)
            y = pSH - y - (h + pGap)
    End Select
End Sub

