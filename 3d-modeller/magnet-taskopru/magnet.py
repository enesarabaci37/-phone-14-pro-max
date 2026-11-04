"""Taşköprü sarımsağı buzdolabı magneti (Bambu Studio + AMS, 3 renk).

Gövde sarımsak başı şeklinde. Ortasından "TAŞKÖPRÜ" yazılı kırmızı bir kurdele geçiyor.
- beyaz  : sarımsak gövdesi + kurdele üstündeki kabartma yazı
- mor    : diş (karanfil) çizgileri, gövdeye gömülü (üst 0.6 mm)
- kirmizi: kabartma kurdele

Arkada 2 adet 10x3 mm neodimyum mıknatıs yuvası var (yapıştırarak takılır).

Kullanım: python3 magnet.py [cikti_klasoru]
Çıktı: tek 3MF (parçalar ayrı), parça parça STL, önizleme PNG.
"""
import math
import os
import sys

import numpy as np
import trimesh
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

T = 4.4          # gövde kalınlığı (mm)
EDGE = 0.6       # ön kenar pahı (üst 0.6 mm içeri çekilir)
INLAY = 0.6      # gömülü renk katmanı
BANNER_H = 1.2   # kurdele kabartma yüksekliği
TEXT_H = 0.6     # yazı kabartma yüksekliği
MAG_D, MAG_DEPTH = 10.3, 3.2   # 10x3 mm mıknatıs yuvası (0.3 mm tolerans)

COLORS = {
    "beyaz": (0.96, 0.95, 0.92),
    "mor": (0.62, 0.45, 0.72),
    "yesil": (0.36, 0.64, 0.30),
    "kirmizi": (0.83, 0.13, 0.12),
}


# ------------------------------------------------------------------ 2B şekiller

def smooth(g, r):
    return g.buffer(r, join_style="round").buffer(-2 * r, join_style="round").buffer(r, join_style="round")


CLOVES = [  # (x, y, rx, ry, açı) önden görünen dişler
    (0, -1.5, 8.6, 19.0, 0),
    (-10.5, -2.0, 9.4, 18.2, 9), (10.5, -2.0, 9.4, 18.2, -9),
    (-20.5, -3.5, 9.0, 14.8, 24), (20.5, -3.5, 9.0, 14.8, -24),
]


def ellipse(x, y, rx, ry, ang):
    e = affinity.scale(Point(0, 0).buffer(1, resolution=64), rx, ry)
    return affinity.translate(affinity.rotate(e, ang, origin=(0, 0)), x, y)


def bulb_shape():
    """Sarımsak başı: alt kenarı diş diş, tepesi boyuna doğru sivrilir."""
    cl = unary_union([ellipse(*c) for c in CLOVES])
    upper = cl.intersection(box(-40, 2, 40, 40))
    top = unary_union([upper, Point(0, 27).buffer(3.2)]).convex_hull
    shape = unary_union([cl, top])
    for sx in (-1, 1):  # içbükey boyun
        shape = shape.difference(Point(sx * 16.5, 31.5).buffer(12.4))
    return smooth(shape, 1.2)


def roots():
    lines = []
    for i, x in enumerate(np.linspace(-6, 6, 6)):
        ang = math.radians(-12 + 24 * i / 5)
        L = 4.2 + (0.8 if i in (2, 3) else 0)
        x0, y0 = x * 0.9, -19.6
        lines.append(LineString([(x0, y0), (x0 + L * math.sin(ang), y0 - L * math.cos(ang))]).buffer(0.75, cap_style="round"))
    return unary_union(lines)


def stem_and_leaves():
    """Kurutulmuş sap (gövdeyle aynı renk)."""
    stem = Polygon([(-3.0, 26.0), (3.0, 26.0), (2.3, 37.5), (-2.1, 38.2)])
    return smooth(stem, 0.5)


def clove_lines(bulb):
    """Dişleri ayıran mor çizgiler: tepeden dişlerin birleştiği alt noktalara."""
    lines = []
    for k in (-1, 1):
        for xb, yb, bulge in ((5.0, -17.5, 0.35), (15.5, -14.0, 0.28)):
            pts = []
            for i in range(61):
                u = i / 60
                x = k * xb * math.sin(math.pi / 2 * u) ** 0.7 * (1 + bulge * math.sin(math.pi * u))
                y = 25 + (yb - 25) * u
                pts.append((x, y))
            lines.append(LineString(pts).buffer(0.55, cap_style="round"))
    return unary_union(lines).intersection(bulb.buffer(-1.4)).buffer(0)


def text_geom(s, height):
    tp = TextPath((0, 0), s, size=10, prop=FontProperties(fname=FONT))
    polys = [Polygon(p) for p in tp.to_polygons() if len(p) > 2]
    geom = Polygon()
    for p in polys:
        geom = geom.symmetric_difference(p.buffer(0))
    # büyük harf yüksekliğine göre ölçekle ("T" yüksekliği)
    cap = TextPath((0, 0), "T", size=10, prop=FontProperties(fname=FONT)).get_extents().height
    sc = height / cap
    geom = affinity.scale(geom, sc, sc, origin=(0, 0))
    minx, miny, maxx, maxy = geom.bounds
    return affinity.translate(geom, -(minx + maxx) / 2, 0), (maxx - minx)


def banner(text_w, cy):
    """Ortası düz, uçları çatallı kurdele."""
    h = 15.0
    half = text_w / 2 + 5.5
    main = box(-half, cy - h / 2, half, cy + h / 2)
    tails = []
    for sx in (-1, 1):
        x0 = sx * (half - 2)
        x1 = sx * (half + 8)
        t = Polygon([(x0, cy - h / 2 - 3), (x1, cy - h / 2 - 3), (sx * (half + 5), cy - 3 + 1.5), (x1, cy + h / 2 - 3), (x0, cy + h / 2 - 3)])
        tails.append(t)
    return smooth(main, 1.0), unary_union(tails).buffer(0.8).buffer(-0.8)


# ------------------------------------------------------------------ 3B

def extrude(geom, z0, z1):
    parts = []
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for p in polys:
        p = p.simplify(0.02, preserve_topology=True).buffer(0)
        if p.is_empty or p.area < 0.05:
            continue
        if p.geom_type != "Polygon":
            parts.append(extrude(p, z0, z1))
            continue
        m = trimesh.creation.extrude_polygon(p, z1 - z0)
        m.apply_translation((0, 0, z0))
        parts.append(m)
    return trimesh.util.concatenate(parts)


def boolean(op, a, b):
    return getattr(trimesh.boolean, op)([a, b], engine="manifold")


def build():
    bulb = bulb_shape()
    outline = unary_union([bulb, roots(), stem_and_leaves()]).buffer(0.3).buffer(-0.3)
    green = Polygon()
    purple = clove_lines(bulb)

    word, tw = text_geom("TAŞKÖPRÜ", 7.0)
    cy = -6.0
    band, tails = banner(tw, cy)
    # yazıyı kurdele ortasına yerleştir (aksanlar dahil dikey ortala)
    minx, miny, maxx, maxy = word.bounds
    word = affinity.translate(word, 0, cy - (miny + maxy) / 2)
    assert band.buffer(-1.2).contains(word), "Yazı kurdeleye sığmadı"

    # gövde: arka düz, ön kenarı pahlı
    inner = outline.buffer(-EDGE, join_style="round")
    body = boolean("union", extrude(outline, 0, T - EDGE), extrude(inner, T - EDGE - 0.01, T))
    inlays = purple
    body = boolean("difference", body, extrude(inlays, T - INLAY, T + 1))
    # mıknatıs yuvaları (arkadan)
    mags = [(-10.5, 10.0), (10.5, 10.0)]
    for c in mags:
        assert inner.buffer(-1.5).contains(Point(c).buffer(MAG_D / 2))
        body = boolean("difference", body, extrude(Point(c).buffer(MAG_D / 2, resolution=48), -1, MAG_DEPTH))

    # kurdele: kuyruklar biraz daha alçak, ana bant üstte
    z0 = T
    red = boolean("union", extrude(tails, z0, z0 + BANNER_H * 0.6), extrude(band, z0, z0 + BANNER_H))
    # gövdenin dışına taşan kurdele kısımları havada kalmasın: tablaya kadar indir
    out_t = tails.difference(outline.buffer(-0.01))
    out_b = band.difference(outline.buffer(-0.01))
    for g, top in ((out_t, z0 + BANNER_H * 0.6), (out_b, z0 + BANNER_H)):
        if not g.is_empty and g.area > 0.05:
            red = boolean("union", red, extrude(g.buffer(0.01), 0, top))
    # pahlı kenar şeridinin üstünde kalan kısım da gövdeye otursun
    ring = outline.difference(inner)
    for g, top in ((tails.intersection(ring), z0 + BANNER_H * 0.6), (band.intersection(ring), z0 + BANNER_H)):
        if not g.is_empty and g.area > 0.05:
            red = boolean("union", red, extrude(g, T - EDGE, top))
    meshes = {
        "beyaz_govde": body,
        "mor_dis_cizgileri": extrude(purple.difference(band.buffer(0.2)), T - INLAY, T),
        "kirmizi_kurdele": red,
        "beyaz_yazi": extrude(word, z0 + BANNER_H, z0 + BANNER_H + TEXT_H),
    }
    # kurdelenin altında kalan mor çizgi parçalarını gövde doldursun
    hidden = purple.intersection(band.buffer(0.2))
    if not hidden.is_empty:
        meshes["beyaz_govde"] = boolean("union", meshes["beyaz_govde"], extrude(hidden.buffer(0.01), T - INLAY - 0.01, T))
    return meshes, outline, (band, tails, word, purple, green, mags)


# ------------------------------------------------------------------ çıktı

def color_of(name):
    return COLORS[name.split("_")[0]]


def preview(meshes, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    views = [(62, -90, "Ön"), (28, -60, "Yandan"), (-62, -90, "Arka (mıknatıs yuvaları)")]
    fig = plt.figure(figsize=(18, 6.4), dpi=120)
    fig.patch.set_facecolor("#23272c")
    light = np.array([0.35, -0.55, 1.0])
    light /= np.linalg.norm(light)
    allv = np.vstack([m.vertices for m in meshes.values()])
    mn, mx = allv.min(0), allv.max(0)
    c, r = (mn + mx) / 2, (mx - mn).max() / 2
    for i, (elev, azim, name) in enumerate(views):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        ax.set_facecolor("#23272c")
        tris, cols = [], []
        for k, m in meshes.items():
            if name.startswith("Arka") and k != "beyaz_govde":
                continue
            base = np.array(color_of(k))
            shade = np.clip(m.face_normals @ light, 0.0, 1.0)[:, None]
            tris.append(m.triangles)
            cols.append(np.clip(base * (0.42 + 0.58 * shade), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.vstack(tris), facecolors=np.vstack(cols), edgecolors="none"))
        ax.set_xlim(c[0] - r, c[0] + r)
        ax.set_ylim(c[1] - r, c[1] + r)
        ax.set_zlim(c[2] - r, c[2] + r)
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(name, color="white", fontsize=13)
    plt.tight_layout()
    plt.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def flat_preview(parts2d, outline, path):
    """Üstten bakış: renklerin net göründüğü 2B önizleme."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    band, tails, word, purple, green, mags = parts2d

    def draw(ax, g, col, z=1):
        polys = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
        for p in polys:
            if p.is_empty or p.geom_type != "Polygon":
                continue
            ax.fill(*p.exterior.xy, color=col, zorder=z, lw=0)
            for h in p.interiors:
                ax.fill(*h.xy, color=under.get(z, "#23272c"), zorder=z + 0.1, lw=0)

    fig, ax = plt.subplots(figsize=(7, 7.6), dpi=140)
    fig.patch.set_facecolor("#23272c")
    ax.set_facecolor("#23272c")
    under = {1: "#d9d3c5", 1.5: "#f5f2ea", 2: "#f5f2ea", 3: "#f5f2ea", 4: "#d42320", 5: "#d42320"}
    shadow = affinity.translate(outline, 0.8, -0.8)
    draw(ax, shadow, "#15181b", 0.5)
    draw(ax, outline, "#d9d3c5", 1)
    draw(ax, outline.buffer(-EDGE), "#f5f2ea", 1.5)
    draw(ax, purple, "#9e73b8", 2)
    draw(ax, tails, "#a8150f", 3)
    draw(ax, band, "#d42320", 4)
    draw(ax, word, "#ffffff", 5)
    ax.set_aspect("equal")
    ax.axis("off")
    minx, miny, maxx, maxy = unary_union([outline, tails]).bounds
    ax.set_title(f"Taşköprü sarımsağı magnet  ·  {maxx - minx:.0f} x {maxy - miny:.0f} mm", color="white", fontsize=12)
    plt.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(out, exist_ok=True)
    meshes, outline, parts2d = build()
    name = "taskopru-sarimsak-magnet"
    for k, m in meshes.items():
        assert m.is_watertight, f"{k} su geçirmez değil"
        m.export(os.path.join(out, f"{name}_{k}.stl"))
    scene = trimesh.Scene()
    for k, m in meshes.items():
        scene.add_geometry(m, node_name=k, geom_name=k)
    scene.export(os.path.join(out, f"{name}.3mf"))
    preview(meshes, os.path.join(out, f"{name}_onizleme_3d.png"))
    flat_preview(parts2d, outline, os.path.join(out, f"{name}_onizleme.png"))
    allv = np.vstack([m.vertices for m in meshes.values()])
    size = allv.max(0) - allv.min(0)
    print(f"{name}: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm; parçalar: {', '.join(meshes)}")


if __name__ == "__main__":
    main()
