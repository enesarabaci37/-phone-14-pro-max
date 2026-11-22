"""Lightroom Mobile icin DNG preset dosyalari uretir.
Her DNG'nin uzerinde preset adi yazar; gece presetleri gece sehir sahnesi kullanir."""
import os, sys, re, zipfile
import numpy as np, tifffile
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_presets as G

W, H = 600, 400
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CAM_FULL = {"M5P": "DJI Mini 5 Pro", "OP3": "DJI Osmo Pocket 3", "X5": "Insta360 X5", "UNI": "Tüm kameralar"}

def dng_xmp(cam, name, desc, cpts, s):
    x = G.xmp(cam, name, desc, cpts, s)
    x = re.sub(r'\s+crs:(PresetType|Cluster|UUID|SupportsAmount2?|Supports\w+|RequiresRGBTables|CameraModelRestriction|Copyright|ContactInfo)="[^"]*"', '', x)
    x = re.sub(r'<crs:(Name|ShortName|SortName|Group|Description)>.*?</crs:\1>\s*', '', x, flags=re.S)
    x = x.replace('crs:HasSettings="True"', 'crs:WhiteBalance="As Shot" crs:HasSettings="True" crs:HasCrop="False" crs:AlreadyApplied="False"')
    return '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>\n' + x + '<?xpacket end="w"?>'

def day_scene():
    Y, X = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]
    img = np.stack([0.25+0.5*Y, 0.45+0.35*Y, 0.85+0.1*Y], -1)
    img += np.exp(-((X-0.7)**2/0.02 + (Y-0.55)**2/0.01))[..., None]*np.array([1.0, 0.6, 0.25])
    g = Y > 0.62
    img[g] = np.stack([0.25*(1.3-Y), 0.45*(1.3-Y), 0.2*(1.3-Y)], -1)[g]
    img[300:370, 30:110] = [0.80, 0.55, 0.42]                       # ten rengi
    for i in range(8):
        img[300:370, 140+i*55:185+i*55] = i/7                         # gri skala
    return np.clip(img, 0, 1)

def night_scene():
    rng = np.random.default_rng(7)
    Y, X = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]
    img = np.stack([0.02+0.10*Y, 0.03+0.12*Y, 0.10+0.25*Y], -1)     # lacivert gece gogu
    x = 0
    while x < W:                                                     # binalar + pencereler
        bw = rng.integers(30, 70); bh = rng.integers(120, 270); top = H - 60 - bh
        img[top:H-60, x:x+bw] = [0.03, 0.035, 0.05]
        for wy in range(top+8, H-70, 12):
            for wx in range(x+5, x+bw-6, 10):
                if rng.random() < 0.45:
                    c = [[1.0, 0.72, 0.35], [1.0, 0.85, 0.6], [0.85, 0.9, 1.0]][rng.integers(0, 3)]
                    img[wy:wy+6, wx:wx+5] = np.array(c) * rng.uniform(0.5, 1.0)
        x += bw + rng.integers(2, 8)
    img[H-60:] = [0.04, 0.035, 0.03]                                  # cadde
    glow = np.zeros((H, W))
    for lx in np.linspace(20, W-20, 9):                               # turuncu sokak lambalari
        glow += np.exp(-((X*W-lx)**2 + (Y*H-(H-52))**2) / 300)
    img += glow[..., None] * np.array([1.0, 0.55, 0.15]) * 1.4
    img[H-30:H-26] += np.array([1.0, 0.25, 0.15]) * 0.8               # stop lambasi izi
    img[H-22:H-19] += np.array([1.0, 0.95, 0.85]) * 0.9               # far izi
    for (nx, ny, c) in [(90, 210, [1.0, 0.1, 0.8]), (330, 180, [0.1, 0.9, 1.0]), (470, 230, [0.6, 0.2, 1.0])]:
        img[ny:ny+14, nx:nx+60] = c                                   # neon tabelalar
        img += np.exp(-((X*W-nx-30)**2/900 + (Y*H-ny-7)**2/200))[..., None] * np.array(c) * 0.35
    img += np.exp(-((X-0.85)**2/0.0006 + (Y-0.36)**2/0.0006))[..., None] * 1.2   # ay / patlak isik
    return np.clip(img, 0, 1)

def label(rgb, name, desc):
    im = Image.fromarray((rgb*255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    short, rest = name.split(" ", 1)
    d.rectangle([0, 0, W, 108], fill=(0, 0, 0, 200))
    d.text((18, 12), rest, font=ImageFont.truetype(FONT_B, 40), fill=(255, 255, 255))
    d.text((20, 64), f"{CAM_FULL[short]}  ·  {name}", font=ImageFont.truetype(FONT_R, 20), fill=(230, 230, 230))
    return np.asarray(im).astype(float) / 255

def to_linear16(srgb):
    lin = np.where(srgb <= 0.04045, srgb/12.92, ((srgb+0.055)/1.055)**2.4)
    return (lin*65535).astype(np.uint16)

def sr(v): return [int(round(v*10000)), 10000]
CM = [3.2406, -1.5372, -0.4986, -0.9689, 1.8758, 0.0415, 0.0557, -0.2040, 1.0570]

def write_dng(path, img, xmp):
    tags = [
        (50706, 'B', 4, (1, 4, 0, 0), True), (50707, 'B', 4, (1, 1, 0, 0), True),
        (50708, 's', 0, 'Pro Video Preset', True),
        (50721, '2i', 9, sum((sr(v) for v in CM), []), True),
        (50778, 'H', 1, 21, True), (50728, '2I', 3, [1, 1, 1, 1, 1, 1], True),
        (50717, 'I', 1, 65535, True), (271, 's', 0, 'Pro Video', True), (272, 's', 0, 'Preset', True),
        (700, 'B', len(xmp.encode()), xmp.encode(), True),
    ]
    tifffile.imwrite(path, img, photometric='rgb', planarconfig='contig', subfiletype=0,
                     extratags=tags, metadata=None, software='Pro Video')
    with tifffile.TiffFile(path, mode='r+') as t:      # RGB -> LinearRaw (DNG)
        t.pages[0].tags[262].overwrite(34892)

def main(OUT):
    DAY, NIGHT = day_scene(), night_scene()
    packs = {"Pro-Video-Presets-DNG.zip": lambda c: "Gece" not in c, "Pro-Video-Gece-DNG.zip": lambda c: "Gece" in c}
    for zname, keep in packs.items():
        with zipfile.ZipFile(os.path.join(OUT, zname), 'w', zipfile.ZIP_DEFLATED) as z:
            for cam, name, desc, c, s in G.P:
                if not keep(cam): continue
                sub = os.path.join(OUT, 'dng', 'gece' if 'Gece' in cam else 'gunduz'); os.makedirs(sub, exist_ok=True)
                img = to_linear16(label(NIGHT if 'Gece' in cam else DAY, name, desc))
                p = os.path.join(sub, G.fname(name) + '.dng'); write_dng(p, img, dng_xmp(cam, name, desc, c, s)); z.write(p, G.fname(name) + '.dng')
    print('dng ok')

if __name__ == "__main__":
    main(sys.argv[1])
