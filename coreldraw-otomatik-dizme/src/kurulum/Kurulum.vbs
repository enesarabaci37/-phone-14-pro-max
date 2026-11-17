' =====================================================================
'  ATÖLYE ARAÇLARI - KURULUM
'  CorelDRAW açıkken bu dosyaya çift tıklayın.
'  Araçları CorelDRAW'a (GlobalMacros) kurar ve üst bara düğmeyi ekler.
' =====================================================================
Option Explicit

Const BASLIK = "Atölye Araçları - Kurulum"
Const PROJE = "GlobalMacros"

Dim fso, klasor, app, vbeObj, prj, rapor, hataVar
Set fso = CreateObject("Scripting.FileSystemObject")
klasor = fso.GetParentFolderName(WScript.ScriptFullName) & "\dosyalar"
rapor = ""
hataVar = False

If Not fso.FolderExists(klasor) Then
    MsgBox "'dosyalar' klasörü bulunamadı." & vbCrLf & _
           "ZIP dosyasını tamamen çıkardığınızdan emin olun.", vbExclamation, BASLIK
    WScript.Quit
End If

' --- 1) Açık CorelDRAW'u bul
Set app = CorelBul()
If app Is Nothing Then
    MsgBox "Açık bir CorelDRAW bulunamadı." & vbCrLf & vbCrLf & _
           "Önce CorelDRAW'u açın, sonra Kurulum'a tekrar çift tıklayın.", vbExclamation, BASLIK
    WScript.Quit
End If

If MsgBox("Atölye Araçları CorelDRAW'a kurulacak." & vbCrLf & vbCrLf & _
          "Başlamadan önce CorelDRAW'da açık olan Otomatik Dizme penceresini kapatın." & vbCrLf & vbCrLf & _
          "Devam edilsin mi?", vbQuestion + vbOKCancel, BASLIK) <> vbOK Then WScript.Quit

' --- 2) VBA projesine eriş
On Error Resume Next
Set vbeObj = Nothing
Set vbeObj = app.VBE
If Err.Number <> 0 Or vbeObj Is Nothing Then
    Bitir "CorelDRAW'un VBA bölümüne erişilemedi (" & Err.Description & ")." & vbCrLf & vbCrLf & _
          "CorelDRAW kurulumunda 'Visual Basic for Applications' bileşeninin yüklü olduğundan emin olun.", True
End If
Err.Clear

Set prj = Nothing
Dim p
For Each p In vbeObj.VBProjects
    If LCase(p.Name) = LCase(PROJE) Then Set prj = p
Next
If prj Is Nothing Then
    Bitir "CorelDRAW'da '" & PROJE & "' projesi bulunamadı.", True
End If

' --- 3) Bileşenleri kur / güncelle
BilesenKur "clsOlay", 2, "clsOlay.txt"
BilesenKur "modAtolye", 1, "modAtolye.txt"
BilesenKur "frmDizme", 3, "frmDizme.txt"
BaslangicKur

' --- 4) Kaydet
Err.Clear
Set vbeObj.ActiveVBProject = prj
Dim kaydet
Set kaydet = Nothing
Set kaydet = vbeObj.CommandBars.FindControl(1, 3)
If Not kaydet Is Nothing Then kaydet.Execute
If Err.Number <> 0 Then
    rapor = rapor & "• Proje otomatik kaydedilemedi; CorelDRAW kapanırken kaydedilecek." & vbCrLf
    Err.Clear
Else
    rapor = rapor & "• Proje kaydedildi." & vbCrLf
End If

' --- 5) Araç çubuğunu kur
If Not hataVar Then
    Err.Clear
    app.GMSManager.RunMacro PROJE, "modAtolye.AracCubuguOtomatik"
    If Err.Number <> 0 Then
        rapor = rapor & "• Araç çubuğu otomatik eklenemedi (" & Err.Description & ")." & vbCrLf & _
                "  Araçlar > Betikler > Betikler > GlobalMacros > modAtolye > AracCubuguKur ile ekleyin." & vbCrLf
        Err.Clear
    Else
        rapor = rapor & "• 'Atölye Araçları' araç çubuğu eklendi." & vbCrLf
    End If
End If

If hataVar Then
    Bitir "Kurulum tamamlanamadı:" & vbCrLf & vbCrLf & rapor, True
Else
    Bitir "Kurulum tamamlandı." & vbCrLf & vbCrLf & rapor & vbCrLf & _
          "Kullanım: nesneleri seçin, üst bardaki logolu düğmeye basın." & vbCrLf & _
          "Araç çubuğunu görmüyorsanız: Pencere > Araç Çubukları > Atölye Araçları", False
End If

' =====================================================================
Sub BilesenKur(adi, tur, dosya)
    On Error Resume Next
    Dim c, cm, kod
    kod = KodOku(klasor & "\" & dosya)
    If kod = "" Then
        rapor = rapor & "• " & adi & ": '" & dosya & "' okunamadı." & vbCrLf
        hataVar = True
        Exit Sub
    End If

    Err.Clear
    Set c = Nothing
    Set c = prj.VBComponents.Item(adi)
    Err.Clear
    If c Is Nothing Then
        Set c = prj.VBComponents.Add(tur)
        If Err.Number <> 0 Or c Is Nothing Then
            rapor = rapor & "• " & adi & " eklenemedi (" & Err.Description & ")." & vbCrLf
            hataVar = True
            Err.Clear
            Exit Sub
        End If
        c.Name = adi
        If Err.Number <> 0 Then
            rapor = rapor & "• " & adi & " adı verilemedi (" & Err.Description & ")." & vbCrLf & _
                    "  CorelDRAW'u kapatıp açın ve Kurulum'u tekrar çalıştırın." & vbCrLf
            prj.VBComponents.Remove c
            hataVar = True
            Err.Clear
            Exit Sub
        End If
    End If

    Set cm = c.CodeModule
    If cm.CountOfLines > 0 Then cm.DeleteLines 1, cm.CountOfLines
    cm.AddFromString kod
    If Err.Number <> 0 Then
        rapor = rapor & "• " & adi & " kodu yazılamadı (" & Err.Description & ")." & vbCrLf
        hataVar = True
        Err.Clear
    Else
        rapor = rapor & "• " & adi & " kuruldu." & vbCrLf
    End If
End Sub

Sub BaslangicKur()
    On Error Resume Next
    Dim c, cm, mevcut, kod
    Err.Clear
    Set c = Nothing
    Set c = prj.VBComponents.Item("ThisMacroStorage")
    If c Is Nothing Then
        rapor = rapor & "• Otomatik başlatma eklenemedi (ThisMacroStorage yok)." & vbCrLf
        Err.Clear
        Exit Sub
    End If
    Set cm = c.CodeModule
    mevcut = ""
    If cm.CountOfLines > 0 Then mevcut = cm.Lines(1, cm.CountOfLines)
    If InStr(1, mevcut, "AracCubuguOtomatik", vbTextCompare) > 0 Then
        rapor = rapor & "• Otomatik başlatma zaten var." & vbCrLf
        Exit Sub
    End If
    If InStr(1, mevcut, "GlobalMacroStorage_Start", vbTextCompare) > 0 Then
        rapor = rapor & "• ThisMacroStorage içinde başka bir başlangıç kodu var; otomatik başlatma eklenmedi." & vbCrLf
        Exit Sub
    End If
    kod = KodOku(klasor & "\baslangic.txt")
    cm.AddFromString kod
    If Err.Number <> 0 Then
        rapor = rapor & "• Otomatik başlatma eklenemedi (" & Err.Description & ")." & vbCrLf
        Err.Clear
    Else
        rapor = rapor & "• CorelDRAW açılışında araç çubuğu otomatik gelecek." & vbCrLf
    End If
End Sub

Function KodOku(yol)
    On Error Resume Next
    Dim st, s
    KodOku = ""
    If Not fso.FileExists(yol) Then Exit Function
    Set st = CreateObject("ADODB.Stream")
    st.Type = 2
    st.Charset = "utf-8"
    st.Open
    st.LoadFromFile yol
    s = st.ReadText
    st.Close
    If Len(s) > 0 Then
        If AscW(Left(s, 1)) = &HFEFF Then s = Mid(s, 2)
    End If
    KodOku = s
End Function

Function CorelBul()
    Dim ids, i, o
    Set CorelBul = Nothing
    ids = Array("CorelDRAW.Application.27", "CorelDRAW.Application.26", "CorelDRAW.Application.25", _
                "CorelDRAW.Application.24", "CorelDRAW.Application.23", "CorelDRAW.Application.22", _
                "CorelDRAW.Application")
    On Error Resume Next
    For i = 0 To UBound(ids)
        Err.Clear
        Set o = Nothing
        Set o = GetObject(, ids(i))
        If Err.Number = 0 Then
            If Not o Is Nothing Then
                Set CorelBul = o
                Exit Function
            End If
        End If
    Next
End Function

Sub Bitir(mesaj, hata)
    If hata Then
        MsgBox mesaj, vbExclamation, BASLIK
    Else
        MsgBox mesaj, vbInformation, BASLIK
    End If
    WScript.Quit
End Sub
