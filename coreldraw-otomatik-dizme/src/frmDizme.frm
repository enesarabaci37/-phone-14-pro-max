VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmDizme 
   Caption         =   "Otomatik Dizme (Montaj)"
   ClientHeight    =   5000
   ClientLeft      =   45
   ClientTop       =   390
   ClientWidth     =   4200
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmDizme"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

' ============================================================
'  OTOMATIK DIZME (MONTAJ / NESTING) - CorelDRAW VBA
'  Seçili nesneleri girilen malzeme ölçüsüne en az fire ile dizer.
' ============================================================

'---------------- Algoritma değişkenleri ----------------
Private Const EPS As Double = 0.0001
Private Const KURAL_SAYISI As Long = 5

' Boş alan listesi
Private fx() As Double, fy() As Double, fw() As Double, fh() As Double
Private fc As Long
' Geçici liste
Private tx() As Double, ty() As Double, tw() As Double, th() As Double
Private tc As Long

' ---- Ana işlem: formdan çağrılır, sonuç raporunu döndürür ----
'---------------- Pencere ----------------
Private WithEvents btnDiz As MSForms.CommandButton
Private WithEvents btnKapat As MSForms.CommandButton
Private txtW As MSForms.TextBox
Private txtH As MSForms.TextBox
Private txtGap As MSForms.TextBox
Private txtMargin As MSForms.TextBox
Private txtAdet As MSForms.TextBox
Private txtAra As MSForms.TextBox
Private chkRot As MSForms.CheckBox
Private chkCer As MSForms.CheckBox
Private txtSonuc As MSForms.TextBox

Private Const UYG As String = "CorelOtomatikDizme"

Private Sub UserForm_Initialize()
    Dim t As Single

    Me.Caption = "Otomatik Dizme (Montaj)"
    Me.Width = 275
    t = 10

    Set txtW = SatirEkle("Malzeme genişliği (mm):", t, Ayar("W", "1000")): t = t + 24
    Set txtH = SatirEkle("Malzeme yüksekliği (mm):", t, Ayar("H", "700")): t = t + 24
    Set txtGap = SatirEkle("Nesneler arası boşluk (mm):", t, Ayar("Gap", "3")): t = t + 24
    Set txtMargin = SatirEkle("Malzeme kenar payı (mm):", t, Ayar("Margin", "5")): t = t + 24
    Set txtAdet = SatirEkle("Her nesneden adet:", t, Ayar("Adet", "1")): t = t + 24
    Set txtAra = SatirEkle("Plakalar arası mesafe (mm):", t, Ayar("Ara", "50")): t = t + 26

    Set chkRot = Me.Controls.Add("Forms.CheckBox.1")
    With chkRot
        .Caption = "Nesneleri 90° döndürmeye izin ver"
        .Left = 10: .Top = t: .Width = 245: .Height = 18
        .Value = (Ayar("Rot", "1") = "1")
    End With
    t = t + 20

    Set chkCer = Me.Controls.Add("Forms.CheckBox.1")
    With chkCer
        .Caption = "Malzeme çerçevesi çiz (kırmızı)"
        .Left = 10: .Top = t: .Width = 245: .Height = 18
        .Value = (Ayar("Cer", "1") = "1")
    End With
    t = t + 26

    Set btnDiz = Me.Controls.Add("Forms.CommandButton.1")
    With btnDiz
        .Caption = "DİZ"
        .Left = 10: .Top = t: .Width = 150: .Height = 26
        .Font.Bold = True
        .Default = True
    End With

    Set btnKapat = Me.Controls.Add("Forms.CommandButton.1")
    With btnKapat
        .Caption = "Kapat"
        .Left = 170: .Top = t: .Width = 85: .Height = 26
        .Cancel = True
    End With
    t = t + 34

    Set txtSonuc = Me.Controls.Add("Forms.TextBox.1")
    With txtSonuc
        .Left = 10: .Top = t: .Width = 245: .Height = 100
        .MultiLine = True
        .WordWrap = True
        .ScrollBars = fmScrollBarsVertical
        .Locked = True
        .BackColor = &H8000000F
        .Text = "Nesneleri seçin, ölçüleri girin ve DİZ'e basın." & vbCrLf & _
                "Pencere açıkken seçimi değiştirebilirsiniz."
    End With
    t = t + 108

    Me.Height = t + 28
End Sub

Private Function SatirEkle(ByVal yazi As String, ByVal t As Single, ByVal deger As String) As MSForms.TextBox
    Dim l As MSForms.Label, tb As MSForms.TextBox
    Set l = Me.Controls.Add("Forms.Label.1")
    l.Caption = yazi
    l.Left = 10: l.Top = t + 3: l.Width = 160: l.Height = 16
    Set tb = Me.Controls.Add("Forms.TextBox.1")
    tb.Left = 175: tb.Top = t: tb.Width = 80: tb.Height = 18
    tb.TextAlign = fmTextAlignRight
    tb.Text = deger
    Set SatirEkle = tb
End Function

Private Sub btnDiz_Click()
    Dim sonuc As String
    AyarKaydet
    txtSonuc.Text = "Hesaplanıyor, lütfen bekleyin..."
    btnDiz.Enabled = False
    DoEvents
    sonuc = DiziYap(Sayi(txtW.Text), Sayi(txtH.Text), Sayi(txtGap.Text), Sayi(txtMargin.Text), _
                    CLng(Sayi(txtAdet.Text)), CBool(chkRot.Value), CBool(chkCer.Value), Sayi(txtAra.Text))
    btnDiz.Enabled = True
    txtSonuc.Text = sonuc
End Sub

Private Sub btnKapat_Click()
    Unload Me
End Sub

' Virgül veya nokta ile yazılan sayıları okur (12,5 veya 12.5)
Private Function Sayi(ByVal s As String) As Double
    s = Replace(Trim$(s), ",", ".")
    Sayi = Val(s)
End Function

Private Function Ayar(ByVal anahtar As String, ByVal varsayilan As String) As String
    Ayar = GetSetting(UYG, "Ayar", anahtar, varsayilan)
End Function

Private Sub AyarKaydet()
    SaveSetting UYG, "Ayar", "W", txtW.Text
    SaveSetting UYG, "Ayar", "H", txtH.Text
    SaveSetting UYG, "Ayar", "Gap", txtGap.Text
    SaveSetting UYG, "Ayar", "Margin", txtMargin.Text
    SaveSetting UYG, "Ayar", "Adet", txtAdet.Text
    SaveSetting UYG, "Ayar", "Ara", txtAra.Text
    SaveSetting UYG, "Ayar", "Rot", IIf(chkRot.Value, "1", "0")
    SaveSetting UYG, "Ayar", "Cer", IIf(chkCer.Value, "1", "0")
End Sub

'---------------- Dizme algoritması ----------------
Private Function DiziYap(ByVal matW As Double, ByVal matH As Double, ByVal gap As Double, _
                        ByVal margin As Double, ByVal adet As Long, ByVal allowRot As Boolean, _
                        ByVal cerceve As Boolean, ByVal plakaAra As Double) As String
    Dim doc As Document, sr As ShapeRange, fr As Shape, pr As Rect
    Dim oldUnit As cdrUnit, grupAcik As Boolean, msg As String
    Dim m As Long, n As Long, i As Long, j As Long, k As Long, c As Long, t As Long
    Dim bx As Double, by As Double, bw As Double, bh As Double
    Dim sw0() As Double, sh0() As Double
    Dim src() As Long, kop() As Long, ord() As Long
    Dim w() As Double, h() As Double, iw() As Double, ih() As Double
    Dim usW As Double, usH As Double, SW As Double, SH As Double
    Dim pS() As Long, pX() As Double, pY() As Double, pR() As Boolean
    Dim bS() As Long, bX() As Double, bY() As Double, bR() As Boolean
    Dim sc As Long, ext As Double, rule As Long, bestSheets As Long, bestExt As Double
    Dim shp() As Shape, ox As Double, oy As Double
    Dim dolu() As Double, adetPl() As Long, rapor As String

    ' --- Kontroller ---
    If Documents.Count = 0 Then DiziYap = "Açık belge yok.": Exit Function
    If matW <= 0 Or matH <= 0 Then DiziYap = "Malzeme ölçüleri 0'dan büyük olmalı.": Exit Function
    If gap < 0 Or margin < 0 Or plakaAra < 0 Then DiziYap = "Boşluk / kenar payı negatif olamaz.": Exit Function
    If adet < 1 Then DiziYap = "Kopya adedi en az 1 olmalı.": Exit Function

    Set doc = ActiveDocument
    Set sr = ActiveSelectionRange
    m = sr.Count
    If m = 0 Then DiziYap = "Önce dizilecek nesneleri seçin.": Exit Function

    oldUnit = doc.Unit
    doc.Unit = cdrMillimeter

    usW = matW - 2 * margin
    usH = matH - 2 * margin
    If usW <= 0 Or usH <= 0 Then
        doc.Unit = oldUnit
        DiziYap = "Kenar payı malzemeye göre çok büyük."
        Exit Function
    End If
    SW = usW + gap
    SH = usH + gap

    ' --- Seçili nesnelerin ölçüleri ve sığma kontrolü ---
    ReDim sw0(1 To m): ReDim sh0(1 To m)
    For i = 1 To m
        sr(i).GetBoundingBox bx, by, bw, bh, True
        sw0(i) = bw: sh0(i) = bh
        If Not ((bw <= usW + EPS And bh <= usH + EPS) Or _
                (allowRot And bh <= usW + EPS And bw <= usH + EPS)) Then
            doc.Unit = oldUnit
            DiziYap = "Bir nesne malzemeye sığmıyor: " & Format(bw, "0.0") & " x " & Format(bh, "0.0") & " mm" & _
                      vbCrLf & "Kullanılabilir alan: " & Format(usW, "0.0") & " x " & Format(usH, "0.0") & " mm"
            Exit Function
        End If
    Next i

    ' --- Kopyalarla birlikte parça listesi ---
    n = m * adet
    ReDim src(1 To n): ReDim kop(1 To n)
    ReDim w(1 To n): ReDim h(1 To n): ReDim iw(1 To n): ReDim ih(1 To n)
    k = 0
    For i = 1 To m
        For c = 1 To adet
            k = k + 1
            src(k) = i: kop(k) = c
            w(k) = sw0(i): h(k) = sh0(i)
            iw(k) = w(k) + gap: ih(k) = h(k) + gap
        Next c
    Next i

    ' --- Büyükten küçüğe sırala ---
    ReDim ord(1 To n)
    For k = 1 To n: ord(k) = k: Next k
    For i = 2 To n
        t = ord(i)
        j = i - 1
        Do While j >= 1
            If Buyuk(t, ord(j), iw, ih) Then
                ord(j + 1) = ord(j)
                j = j - 1
            Else
                Exit Do
            End If
        Loop
        ord(j + 1) = t
    Next i

    ' --- Tüm kuralları dene, en iyisini seç ---
    bestSheets = 0
    For rule = 0 To KURAL_SAYISI - 1
        sc = PackRun(rule, n, iw, ih, ord, SW, SH, allowRot, pS, pX, pY, pR, ext)
        If sc > 0 Then
            If bestSheets = 0 Or sc < bestSheets Or (sc = bestSheets And ext < bestExt - EPS) Then
                bestSheets = sc: bestExt = ext
                bS = pS: bX = pX: bY = pY: bR = pR
            End If
        End If
        DoEvents
    Next rule
    If bestSheets = 0 Then
        doc.Unit = oldUnit
        DiziYap = "Yerleşim bulunamadı."
        Exit Function
    End If

    ' --- Uygula ---
    On Error GoTo Hata
    doc.BeginCommandGroup "Otomatik Dizme"
    grupAcik = True
    Optimization = True

    ' Önce kopyaları oluştur (orijinaller henüz yerinde)
    ReDim shp(1 To n)
    For k = 1 To n
        If kop(k) = 1 Then
            Set shp(k) = sr(src(k))
        Else
            Set shp(k) = sr(src(k)).Duplicate
        End If
    Next k

    Set pr = doc.ActivePage.BoundingBox
    oy = pr.y
    ReDim dolu(1 To bestSheets): ReDim adetPl(1 To bestSheets)
    For k = 1 To n
        If bR(k) Then shp(k).Rotate 90
        shp(k).GetBoundingBox bx, by, bw, bh, True
        ox = pr.x + (bS(k) - 1) * (matW + plakaAra)
        shp(k).Move (ox + margin + bX(k)) - bx, (oy + margin + bY(k)) - by
        dolu(bS(k)) = dolu(bS(k)) + w(k) * h(k)
        adetPl(bS(k)) = adetPl(bS(k)) + 1
    Next k

    If cerceve Then
        For k = 1 To bestSheets
            ox = pr.x + (k - 1) * (matW + plakaAra)
            Set fr = doc.ActiveLayer.CreateRectangle2(ox, oy, matW, matH)
            fr.Fill.ApplyNoFill
            fr.Outline.Width = 0.25
            fr.Outline.Color.RGBAssign 255, 0, 0
            fr.Name = "Plaka " & k
            fr.OrderToBack
        Next k
    End If

    Optimization = False
    doc.EndCommandGroup
    grupAcik = False
    doc.Unit = oldUnit
    ActiveWindow.Refresh

    ' --- Rapor ---
    rapor = "Tamamlandı. " & n & " nesne, " & bestSheets & " plaka (" & _
            Format(matW, "0.##") & " x " & Format(matH, "0.##") & " mm)" & vbCrLf
    For k = 1 To bestSheets
        rapor = rapor & "Plaka " & k & ": " & adetPl(k) & " adet, doluluk %" & _
                Format(100 * dolu(k) / (matW * matH), "0.0") & ", fire %" & _
                Format(100 - 100 * dolu(k) / (matW * matH), "0.0") & vbCrLf
    Next k
    rapor = rapor & "Geri almak için Ctrl+Z."
    DiziYap = rapor
    Exit Function

Hata:
    msg = Err.Description
    On Error Resume Next
    Optimization = False
    If grupAcik Then doc.EndCommandGroup
    doc.Unit = oldUnit
    ActiveWindow.Refresh
    DiziYap = "Hata: " & msg
End Function

' a parçası b'den önce mi gelmeli? (uzun kenar, sonra alan büyük olan önce)
Private Function Buyuk(ByVal a As Long, ByVal b As Long, iw() As Double, ih() As Double) As Boolean
    Dim ma As Double, mb As Double
    ma = Max2(iw(a), ih(a))
    mb = Max2(iw(b), ih(b))
    If ma > mb + EPS Then
        Buyuk = True
    ElseIf Abs(ma - mb) <= EPS Then
        Buyuk = (iw(a) * ih(a) > iw(b) * ih(b) + EPS)
    Else
        Buyuk = False
    End If
End Function

' ---- Tek bir kural ile yerleşim; plaka sayısını döndürür (-1 = başarısız) ----
Private Function PackRun(ByVal rule As Long, ByVal n As Long, iw() As Double, ih() As Double, ord() As Long, _
        ByVal SW As Double, ByVal SH As Double, ByVal allowRot As Boolean, _
        pS() As Long, pX() As Double, pY() As Double, pR() As Boolean, ByRef ext As Double) As Long
    Dim placed() As Boolean, remaining As Long, sheet As Long, onSheet As Long
    Dim k As Long, i As Long, r As Long, o As Long
    Dim bi As Long, bxp As Double, byp As Double, bRot As Boolean, b1 As Double, b2 As Double
    Dim w As Double, h As Double, s1 As Double, s2 As Double
    Dim lw As Double, lh As Double, mx As Double, my As Double

    ReDim placed(1 To n): ReDim pS(1 To n): ReDim pX(1 To n): ReDim pY(1 To n): ReDim pR(1 To n)
    remaining = n: sheet = 1: onSheet = 0
    FreeInit SW, SH

    Do While remaining > 0
        bi = 0: b1 = 1E+300: b2 = 1E+300
        lw = -1: lh = -1
        For k = 1 To n
            i = ord(k)
            If Not placed(i) Then
                ' Aynı ölçüdeki parçaları tekrar hesaplama (hız için)
                If Not (Abs(iw(i) - lw) < EPS And Abs(ih(i) - lh) < EPS) Then
                    lw = iw(i): lh = ih(i)
                    For o = 0 To 1
                        If o = 0 Then
                            w = iw(i): h = ih(i)
                        Else
                            w = ih(i): h = iw(i)
                        End If
                        If o = 0 Or (allowRot And Abs(w - h) > EPS) Then
                            For r = 1 To fc
                                If w <= fw(r) + EPS And h <= fh(r) + EPS Then
                                    Score rule, r, w, h, s1, s2
                                    If s1 < b1 - EPS Or (Abs(s1 - b1) <= EPS And s2 < b2 - EPS) Then
                                        bi = i: b1 = s1: b2 = s2
                                        bxp = fx(r): byp = fy(r): bRot = (o = 1)
                                    End If
                                End If
                            Next r
                        End If
                    Next o
                End If
            End If
        Next k

        If bi = 0 Then
            If onSheet = 0 Then PackRun = -1: Exit Function
            sheet = sheet + 1: onSheet = 0
            FreeInit SW, SH
        Else
            If bRot Then
                w = ih(bi): h = iw(bi)
            Else
                w = iw(bi): h = ih(bi)
            End If
            placed(bi) = True
            remaining = remaining - 1
            onSheet = onSheet + 1
            pS(bi) = sheet: pX(bi) = bxp: pY(bi) = byp: pR(bi) = bRot
            PlaceRect bxp, byp, w, h
        End If
    Loop

    ' Son plakada kullanılan alan (küçük olan daha iyi: kalan malzeme toplu kalır)
    mx = 0: my = 0
    For i = 1 To n
        If pS(i) = sheet Then
            If pR(i) Then
                w = ih(i): h = iw(i)
            Else
                w = iw(i): h = ih(i)
            End If
            If pX(i) + w > mx Then mx = pX(i) + w
            If pY(i) + h > my Then my = pY(i) + h
        End If
    Next i
    ext = mx * my
    PackRun = sheet
End Function

Private Sub Score(ByVal rule As Long, ByVal r As Long, ByVal w As Double, ByVal h As Double, _
                  ByRef s1 As Double, ByRef s2 As Double)
    Dim lw As Double, lh As Double
    lw = fw(r) - w
    lh = fh(r) - h
    Select Case rule
        Case 0  ' En iyi kısa kenar uyumu
            s1 = Min2(lw, lh): s2 = Max2(lw, lh)
        Case 1  ' En iyi uzun kenar uyumu
            s1 = Max2(lw, lh): s2 = Min2(lw, lh)
        Case 2  ' En iyi alan uyumu
            s1 = fw(r) * fh(r) - w * h: s2 = Min2(lw, lh)
        Case 3  ' Alttan-sola (satır satır)
            s1 = fy(r) + h: s2 = fx(r)
        Case Else  ' Soldan-alta (sütun sütun)
            s1 = fx(r) + w: s2 = fy(r)
    End Select
End Sub

' ---- Boş alan yönetimi (MaxRects) ----
Private Sub FreeInit(ByVal W As Double, ByVal H As Double)
    ReDim fx(1 To 1): ReDim fy(1 To 1): ReDim fw(1 To 1): ReDim fh(1 To 1)
    fx(1) = 0: fy(1) = 0: fw(1) = W: fh(1) = H
    fc = 1
End Sub

Private Sub TAdd(ByVal x As Double, ByVal y As Double, ByVal w As Double, ByVal h As Double)
    If w <= EPS Or h <= EPS Then Exit Sub
    tc = tc + 1
    tx(tc) = x: ty(tc) = y: tw(tc) = w: th(tc) = h
End Sub

' i dikdörtgeni j'nin içinde mi?
Private Function TIn(ByVal i As Long, ByVal j As Long) As Boolean
    TIn = (tx(i) >= tx(j) - EPS And ty(i) >= ty(j) - EPS And _
           tx(i) + tw(i) <= tx(j) + tw(j) + EPS And ty(i) + th(i) <= ty(j) + th(j) + EPS)
End Function

Private Sub PlaceRect(ByVal x As Double, ByVal y As Double, ByVal w As Double, ByVal h As Double)
    Dim i As Long, j As Long, cnt As Long, keep() As Boolean
    Dim ax As Double, ay As Double, aw As Double, ah As Double

    tc = 0
    ReDim tx(1 To fc * 4 + 4): ReDim ty(1 To fc * 4 + 4)
    ReDim tw(1 To fc * 4 + 4): ReDim th(1 To fc * 4 + 4)

    For i = 1 To fc
        ax = fx(i): ay = fy(i): aw = fw(i): ah = fh(i)
        If x >= ax + aw - EPS Or x + w <= ax + EPS Or y >= ay + ah - EPS Or y + h <= ay + EPS Then
            TAdd ax, ay, aw, ah                              ' kesişmiyor
        Else
            If x > ax + EPS Then TAdd ax, ay, x - ax, ah                         ' sol
            If x + w < ax + aw - EPS Then TAdd x + w, ay, ax + aw - x - w, ah    ' sağ
            If y > ay + EPS Then TAdd ax, ay, aw, y - ay                         ' alt
            If y + h < ay + ah - EPS Then TAdd ax, y + h, aw, ay + ah - y - h    ' üst
        End If
    Next i

    If tc = 0 Then fc = 0: Exit Sub

    ' Başka bir boş alanın içinde kalanları at
    ReDim keep(1 To tc)
    For i = 1 To tc: keep(i) = True: Next i
    For i = 1 To tc
        For j = 1 To tc
            If i <> j And keep(j) Then
                If TIn(i, j) Then
                    If (Not TIn(j, i)) Or j < i Then keep(i) = False: Exit For
                End If
            End If
        Next j
    Next i

    ReDim fx(1 To tc): ReDim fy(1 To tc): ReDim fw(1 To tc): ReDim fh(1 To tc)
    cnt = 0
    For i = 1 To tc
        If keep(i) Then
            cnt = cnt + 1
            fx(cnt) = tx(i): fy(cnt) = ty(i): fw(cnt) = tw(i): fh(cnt) = th(i)
        End If
    Next i
    fc = cnt
End Sub

Private Function Min2(ByVal a As Double, ByVal b As Double) As Double
    If a < b Then Min2 = a Else Min2 = b
End Function

Private Function Max2(ByVal a As Double, ByVal b As Double) As Double
    If a > b Then Max2 = a Else Max2 = b
End Function
