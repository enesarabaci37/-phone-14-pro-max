"""Taşköprü sarımsağı buzdolabı magneti (Bambu Studio + AMS, 4 renk).

Gövde sarımsak başı şeklinde. Ortasından "TAŞKÖPRÜ" yazılı kırmızı bir kurdele geçiyor.
- beyaz  : sarımsak gövdesi + kurdele üstündeki kabartma yazı
- mor    : diş (karanfil) çizgileri, gövdeye gömülü (üst 0.6 mm)
- yesil  : sap ve yapraklar, gövdeye gömülü (üst 0.6 mm)
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


def bulb_shape():
    """Sarımsak başı: altı geniş, tepesi sivri, boyun kısmı içbükey."""
    pts = []
    for i in range(361):
        a = math.radians(i)
        # alt kısım biraz basık, üst kısım sivri (damla)
        x = 29 * math.cos(a)
        y = 21 * math.sin(a)
        if y > 0:
            y *= 1.0 + 0.55 * (y / 21) ** 2
        pts.append((x, y - 2))
    body = Polygon(pts)
    top = Point(0, 28).buffer(3.4)
    shape = unary_union([body, top]).convex_hull
    # içbükey boyun
    for sx in (-1, 1):
        shape = shape.difference(Point(sx * 17.5, 33).buffer(13.2))
    return smooth(shape, 1.5)


def roots():
    lines = []
    for i, x in enumerate(np.linspace(-6, 6, 6)):
        ang = math.radians(-12 + 24 * i / 5)
        L = 4.2 + (0.8 if i in (2, 3) else 0)
        x0, y0 = x * 0.9, -22.2
        lines.append(LineString([(x0, y0), (x0 + L * math.sin(ang), y0 - L * math.cos(ang))]).buffer(0.75, cap_style="round"))
    return unary_union(lines)


def stem_and_leaves():
    stem = Polygon([(-3.2, 26.5), (3.2, 26.5), (2.4, 40), (-2.0, 40.5)])
    stem = smooth(stem, 0.5)

    def leaf(base, tip, width, bend):
        bx, by = base
        tx, ty = tip
        n = 40
        left, right = [], []
        dx, dy = tx - bx, ty - by
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        for k in range(n + 1):
            u = k / n
            cx = bx + dx * u + nx * bend * math.sin(math.pi * u)
            cy = by + dy * u + ny * bend * math.sin(math.pi * u)
            w = width / 2 * math.sin(math.pi * min(1, u * 1.05)) ** 0.8
            left.append((cx + nx * w, cy + ny * w))
            right.append((cx - nx * w, cy - ny * w))
        return Polygon(left + right[::-1]).buffer(0)

    l1 = leaf((-0.5, 37), (-15, 47.5), 5.0, 2.5)
    l2 = leaf((0.8, 38), (12.5, 49.5), 4.6, -2.2)
    return unary_union([stem, l1, l2])


def clove_lines(bulb):
    """Dişleri ayıran kavisli çizgiler (tepe ile dip arasında)."""
    lines = []
    top, bot = (0, 26), (0, -21)
    for k in (-1.0, -0.55, 0.55, 1.0):
        pts = []
        for i in range(61):
            u = i / 60
            y = top[1] + (bot[1] - top[1]) * u
            x = k * 23 * math.sin(math.pi * u) ** 0.85
            pts.append((x, y))
        lines.append(LineString(pts).buffer(0.6, cap_style="round"))
    return unary_union(lines).intersection(bulb.buffer(-1.6))


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
        if p.is_empty or p.area < 0.05:
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
    green = stem_and_leaves().difference(bulb.buffer(-0.01)).intersection(outline.buffer(-EDGE - 0.3))
    green = green.buffer(-0.01)
    purple = clove_lines(bulb)

    word, tw = text_geom("TAŞKÖPRÜ", 8.6)
    cy = -6.0
    band, tails = banner(tw, cy)
    # yazıyı kurdele ortasına yerleştir (aksanlar dahil dikey ortala)
    minx, miny, maxx, maxy = word.bounds
    word = affinity.translate(word, 0, cy - (miny + maxy) / 2)
    assert band.buffer(-1.2).contains(word), "Yazı kurdeleye sığmadı"

    # gövde: arka düz, ön kenarı pahlı
    inner = outline.buffer(-EDGE, join_style="round")
    body = trimesh.util.concatenate([extrude(outline, 0, T - EDGE), extrude(inner, T - EDGE, T)])
    body = boolean("union", extrude(outline, 0, T - EDGE), extrude(inner, T - EDGE - 0.01, T))
    inlays = unary_union([purple, green])
    body = boolean("difference", body, extrude(inlays, T - INLAY, T + 1))
    # mıknatıs yuvaları (arkadan)
    mags = [(-10.5, 10.0), (10.5, 10.0)]
    for c in mags:
        assert inner.buffer(-1.5).contains(Point(c).buffer(MAG_D / 2))
        body = boolean("difference", body, extrude(Point(c).buffer(MAG_D / 2, resolution=48), -1, MAG_DEPTH))

    # kurdele: kuyruklar biraz daha alçak, ana bant üstte
    z0 = T
    red = boolean("union", extrude(tails, z0, z0 + BANNER_H * 0.6), extrude(band, z0, z0 + BANNER_H))
    meshes = {
        "beyaz_govde": body,
        "mor_dis_cizgileri": extrude(purple.difference(band.buffer(0.2)), T - INLAY, T),
        "yesil_sap": extrude(green, T - INLAY, T),
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
    under = {1: "#23272c", 2: "#f5f2ea", 3: "#f5f2ea", 4: "#d42320", 5: "#d42320"}
    shadow = affinity.translate(outline, 0.8, -0.8)
    draw(ax, shadow, "#15181b", 0.5)
    draw(ax, outline, "#f5f2ea", 1)
    draw(ax, outline.difference(outline.buffer(-EDGE)), "#ddd8cc", 1.5)
    draw(ax, purple, "#9e73b8", 2)
    draw(ax, green, "#5ca34d", 2)
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
