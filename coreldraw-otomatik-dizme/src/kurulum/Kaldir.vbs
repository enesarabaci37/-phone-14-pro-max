' =====================================================================
'  ATÖLYE ARAÇLARI - KALDIR
'  CorelDRAW açıkken çift tıklayın. Araçları ve araç çubuğunu kaldırır.
'  Kayıtlı ön ayarlarınız silinmez.
' =====================================================================
Option Explicit

Const BASLIK = "Atölye Araçları - Kaldır"
Const PROJE = "GlobalMacros"

Dim app, vbeObj, prj, p, adlar, i, c, cm, ilk, adet

Set app = CorelBul()
If app Is Nothing Then
    MsgBox "Açık bir CorelDRAW bulunamadı. Önce CorelDRAW'u açın.", vbExclamation, BASLIK
    WScript.Quit
End If
If MsgBox("Atölye Araçları CorelDRAW'dan kaldırılsın mı?", vbQuestion + vbYesNo, BASLIK) <> vbYes Then WScript.Quit

On Error Resume Next
app.GMSManager.RunMacro PROJE, "modAtolye.AracCubuguKaldir"
Err.Clear

Set vbeObj = app.VBE
Set prj = Nothing
For Each p In vbeObj.VBProjects
    If LCase(p.Name) = LCase(PROJE) Then Set prj = p
Next
If prj Is Nothing Then
    MsgBox "GlobalMacros projesi bulunamadı.", vbExclamation, BASLIK
    WScript.Quit
End If

' Başlangıç kodunu çıkar
Set c = Nothing
Set c = prj.VBComponents.Item("ThisMacroStorage")
If Not c Is Nothing Then
    Set cm = c.CodeModule
    Err.Clear
    ilk = cm.ProcStartLine("GlobalMacroStorage_Start", 0)
    If Err.Number = 0 Then
        adet = cm.ProcCountLines("GlobalMacroStorage_Start", 0)
        If InStr(1, cm.Lines(ilk, adet), "AracCubuguOtomatik", vbTextCompare) > 0 Then cm.DeleteLines ilk, adet
    End If
    Err.Clear
End If

adlar = Array("frmDizme", "modAtolye", "clsOlay")
For i = 0 To UBound(adlar)
    Set c = Nothing
    Set c = prj.VBComponents.Item(adlar(i))
    If Not c Is Nothing Then prj.VBComponents.Remove c
    Err.Clear
Next

Set vbeObj.ActiveVBProject = prj
vbeObj.CommandBars.FindControl(1, 3).Execute
Err.Clear

MsgBox "Atölye Araçları kaldırıldı.", vbInformation, BASLIK

Function CorelBul()
    Dim ids, k, o
    Set CorelBul = Nothing
    ids = Array("CorelDRAW.Application.27", "CorelDRAW.Application.26", "CorelDRAW.Application.25", _
                "CorelDRAW.Application.24", "CorelDRAW.Application.23", "CorelDRAW.Application.22", _
                "CorelDRAW.Application")
    On Error Resume Next
    ' 1) Çalışan CorelDRAW'a doğrudan bağlan
    For k = 0 To UBound(ids)
        Err.Clear
        Set o = Nothing
        Set o = GetObject(, ids(k))
        If Err.Number = 0 Then
            If Not o Is Nothing Then
                Set CorelBul = o
                Exit Function
            End If
        End If
    Next
    ' 2) CorelDRAW tek kopya çalışır: CreateObject açık olan pencereye bağlanır
    For k = 0 To UBound(ids)
        Err.Clear
        Set o = Nothing
        Set o = CreateObject(ids(k))
        If Err.Number = 0 Then
            If Not o Is Nothing Then
                o.Visible = True
                Err.Clear
                Set CorelBul = o
                Exit Function
            End If
        End If
    Next
End Function
