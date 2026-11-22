"""Kayıpsız PDF küçültme (Etsy dosya sınırı 20 MB)."""
import sys, os
from pypdf import PdfWriter
for f in sys.argv[1:]:
    w = PdfWriter(clone_from=f)
    for p in w.pages: p.compress_content_streams(level=9)
    w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    tmp = f + '.tmp'; w.write(tmp); b0 = os.path.getsize(f); os.replace(tmp, f)
    print(f'{os.path.basename(f)}: {b0/1e6:.1f} -> {os.path.getsize(f)/1e6:.1f} MB, {len(w.pages)} pages')
