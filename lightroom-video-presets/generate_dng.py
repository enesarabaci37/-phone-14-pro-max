"""Lightroom Mobile icin DNG preset dosyalari uretir (eski 'DNG ile preset' yontemi)."""
import os, sys, re, zipfile
import numpy as np, tifffile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_presets as G

def dng_xmp(cam, name, desc, cpts, s):
    s = {k: v for k, v in s.items() if not k.startswith("Incremental")}  # RAW'da beyaz dengesi mutlak; atla
    x = G.xmp(cam, name, desc, cpts, s)
    # preset-only alanlari kaldir, fotograf ayari haline getir
    x = re.sub(r'\s+crs:(PresetType|Cluster|UUID|SupportsAmount2?|Supports\w+|RequiresRGBTables|CameraModelRestriction|Copyright|ContactInfo)="[^"]*"', '', x)
    x = re.sub(r'<crs:(Name|ShortName|SortName|Group|Description)>.*?</crs:\1>\s*', '', x)
    x = x.replace('crs:WhiteBalance="Custom"', '')
    x = x.replace('crs:HasSettings="True"', 'crs:WhiteBalance="As Shot" crs:HasSettings="True" crs:HasCrop="False" crs:AlreadyApplied="False"')
    return '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>\n' + x + '<?xpacket end="w"?>'

def scene(w=300, h=200):
    Y, X = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    img = np.stack([0.25+0.5*Y, 0.45+0.35*Y, 0.85+0.1*Y], -1)                   # mavi gokyuzu
    img += np.exp(-((X-0.7)**2/0.02 + (Y-0.55)**2/0.01))[..., None]*np.array([1.0, 0.6, 0.25])  # gunes
    g = Y > 0.62                                                                 # yesil zemin
    img[g] = np.stack([0.25*(1.3-Y), 0.45*(1.3-Y), 0.2*(1.3-Y)], -1)[g]
    img[150:190, 20:60] = [0.80, 0.55, 0.42]                                    # ten rengi
    for i in range(8):                                                           # gri skala
        img[150:190, 80+i*25:100+i*25] = i/7
    srgb = np.clip(img, 0, 1)
    lin = np.where(srgb <= 0.04045, srgb/12.92, ((srgb+0.055)/1.055)**2.4)
    return (lin*65535).astype(np.uint16)

def sr(v): return [int(round(v*10000)), 10000]
CM = [3.2406, -1.5372, -0.4986, -0.9689, 1.8758, 0.0415, 0.0557, -0.2040, 1.0570]

def write_dng(path, xmp):
    tags = [
        (50706, 'B', 4, (1, 4, 0, 0), True), (50707, 'B', 4, (1, 1, 0, 0), True),
        (50708, 's', 0, 'Video Pro Preset', True),
        (50721, '2i', 9, sum((sr(v) for v in CM), []), True),
        (50778, 'H', 1, 21, True), (50728, '2I', 3, [1, 1, 1, 1, 1, 1], True),
        (50717, 'I', 1, 65535, True), (271, 's', 0, 'Video Pro', True), (272, 's', 0, 'Preset', True),
        (700, 'B', len(xmp.encode()), xmp.encode(), True),
    ]
    tifffile.imwrite(path, IMG, photometric='rgb', planarconfig='contig', subfiletype=0,
                     extratags=tags, metadata=None, software='Video Pro')
    with tifffile.TiffFile(path, mode='r+') as t:   # RGB -> LinearRaw (DNG)
        t.pages[0].tags[262].overwrite(34892)

IMG = scene()
OUT = sys.argv[1]; os.makedirs(os.path.join(OUT, 'dng'), exist_ok=True)
with zipfile.ZipFile(os.path.join(OUT, 'Pro-Video-Presets-DNG.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for cam, name, desc, c, s in G.P:
        fn = G.fname(name) + '.dng'
        p = os.path.join(OUT, 'dng', fn); write_dng(p, dng_xmp(cam, name, desc, c, s)); z.write(p, fn)
print('ok', len(G.P))
