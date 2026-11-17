VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "clsOlay"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
Option Explicit

' Atölye Araçlarý - pencere kontrollerinin olaylarýný yakalar
' (sayý kutusu + yukarý/aþaðý oklarý, açýlýr liste, onay kutusu)

Public WithEvents tb As MSForms.TextBox
Attribute tb.VB_VarHelpID = -1
Public WithEvents sp As MSForms.SpinButton
Attribute sp.VB_VarHelpID = -1
Public WithEvents cb As MSForms.ComboBox
Attribute cb.VB_VarHelpID = -1
Public WithEvents ch As MSForms.CheckBox
Attribute ch.VB_VarHelpID = -1

Public Frm As Object
Public Tamsayi As Boolean
Public MinDeger As Double

Private Sub sp_SpinUp()
    Adim 1
End Sub

Private Sub sp_SpinDown()
    Adim -1
End Sub

Private Sub Adim(ByVal yon As Long)
    Dim v As Double, st As Double
    v = Frm.SayiOku(tb.Text)
    If Tamsayi Then
        st = 1
    Else
        st = Frm.AdimBuyuklugu()
    End If
    v = Round(v + yon * st, 4)
    If v < MinDeger Then v = MinDeger
    tb.Text = Frm.SayiYaz(v)
End Sub

Private Sub tb_Change()
    Frm.AyarDegisti
End Sub

Private Sub cb_Change()
    Frm.AyarDegisti
End Sub

Private Sub ch_Click()
    Frm.AyarDegisti
End Sub
