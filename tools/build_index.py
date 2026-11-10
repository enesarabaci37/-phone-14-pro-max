#!/usr/bin/env python3
"""ders-bahcesi.html (Claude Artifact sürümü) dosyasından GitHub Pages için bağımsız index.html üretir."""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
body = (root / "ders-bahcesi.html").read_text(encoding="utf-8")
head = """<!doctype html>
<html lang="tr">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Ders Bahçesi">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#E6F3EC">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" href="apple-touch-icon.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}</style>
"""
(root / "index.html").write_text(head + body + "\n</html>\n", encoding="utf-8")
print("index.html yazıldı")
