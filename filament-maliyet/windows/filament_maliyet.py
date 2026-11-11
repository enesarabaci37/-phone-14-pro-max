"""Filament Maliyet - Windows programi.

index.html uygulamasini kendi penceresinde (Edge WebView2) acar.
Veriler %LOCALAPPDATA%\\FilamentMaliyet altinda kalici tutulur.
"""
import os
import sys

import webview

# Sabit port: tarayici verisi (localStorage) adrese bagli oldugu icin her acilista ayni olmali.
PORT = 47613


def base_dir():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def main():
    data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "FilamentMaliyet")
    os.makedirs(data_dir, exist_ok=True)
    webview.settings["ALLOW_DOWNLOADS"] = True  # yedek (.json) ve CSV indirme icin
    webview.create_window(
        "Filament Maliyet",
        url=os.path.join(base_dir(), "app", "index.html"),
        width=1280,
        height=860,
        min_size=(760, 560),
    )
    webview.start(
        http_server=True,
        http_port=PORT,
        private_mode=False,
        storage_path=data_dir,
        icon=os.path.join(base_dir(), "app", "icon-512.png"),
    )


if __name__ == "__main__":
    main()
