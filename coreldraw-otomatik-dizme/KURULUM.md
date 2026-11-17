# Atölye Araçları – Otomatik Dizme (CorelDRAW)

CorelDRAW için Türkçe dizme (nesting) eklentisi.

- Kurulum paketi: `dist/AtolyeAraclari.zip`. CorelDRAW açıkken `Kurulum.vbs` dosyasına çift tıklanır.
- Kaynak: `src/` (`parcalar/frm_ust.bas` arayüz, `frmDizme_kod.txt` birleşik form kodu, `modAtolye.bas`, `clsOlay.cls`, `kurulum/*.vbs`)
- Kurulum betiği bileşenleri CorelDRAW'un VBA nesne modeli üzerinden GlobalMacros projesine yazar, ThisMacroStorage'a açılış kodunu ekler ve araç çubuğunu kurar.
