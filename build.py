#!/usr/bin/env python3
"""Her şeyi tek bir dosyada toplar: VektorSihirbazi.html (çift tıklayıp açılır, internet gerekmez)."""
import pathlib
d = pathlib.Path(__file__).parent
html = (d / 'index.html').read_text(encoding='utf-8')
vec = (d / 'vectorizer.js').read_text(encoding='utf-8')
app = (d / 'app.js').read_text(encoding='utf-8')
assert '</script' not in vec and '</script' not in app
html = html.replace('<script src="vectorizer.js"></script>',
                    '<script id="vec-src">\n' + vec + '\n</script>')
html = html.replace('<script src="app.js"></script>', '<script>\n' + app + '\n</script>')
(d / 'VektorSihirbazi.html').write_text(html, encoding='utf-8')
print('VektorSihirbazi.html oluşturuldu')
