"""Filament Maliyet - Windows programi.

Uygulamayi (index.html) Edge'in "uygulama penceresi" modunda acar: adres
cubugu olmayan, kendi penceresi olan bir program gibi gorunur.
.NET / pythonnet kullanilmaz; program Drive gibi klasorlerden de calisir.

Uygulama dosyalari ve veriler %LOCALAPPDATA%\\FilamentMaliyet altinda tutulur,
boylece program klasoru tasinsa ya da yeni surume gecilse de veriler kaybolmaz.
"""
import ctypes
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

APP_FILES = ["index.html", "icon.svg", "icon-180.png", "icon-512.png"]


def base_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def message(text: str) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(0, text, "Filament Maliyet", 0x40)
    except Exception:
        print(text)


def find_browser():
    env = os.environ.get
    roots = [env("ProgramFiles(x86)"), env("ProgramFiles"), env("LOCALAPPDATA")]
    rels = [
        r"Microsoft\Edge\Application\msedge.exe",
        r"Google\Chrome\Application\chrome.exe",
    ]
    for rel in rels:
        for root in roots:
            if root:
                p = Path(root) / rel
                if p.is_file():
                    return str(p)
    for name in ("msedge", "chrome", "chromium", "google-chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def main():
    home = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "FilamentMaliyet"
    app_dir = home / "app"
    profile_dir = home / "tarayici"
    app_dir.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)

    # Uygulama dosyalarini her acilista yerel klasore kopyala (yeni surum gelirse guncellenir).
    src = base_dir() / "app"
    for name in APP_FILES:
        if (src / name).is_file():
            shutil.copyfile(src / name, app_dir / name)

    url = (app_dir / "index.html").as_uri()
    browser = find_browser()
    if not browser:
        webbrowser.open(url)
        return

    args = [
        browser,
        f"--app={url}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-sync",
        "--window-size=1280,860",
    ]
    flags = 0
    if os.name == "nt":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(args, creationflags=flags, close_fds=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pencereli programda hatayi kullaniciya goster
        message(f"Program açılamadı:\n{exc}")
