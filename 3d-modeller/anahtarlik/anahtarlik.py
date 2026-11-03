"""Arabacı Reklam logolu, çok renkli anahtarlık modelleri (Bambu Studio + AMS için).

Logo PNG'sinden renk renk vektör çıkarılır, her renk ayrı parça olarak modellenir.
Renkli bölgeler gövdeye gömülüdür (inlay): üst yüzey düz, sadece son 0.6 mm renklidir.

Model A: Sadece üçgen sembol şeklinde anahtarlık (4 renk). Arkada "ARABACI" yazısı oyuk.
Model B: Tam logo (sembol + ARABACI + REKLAM) dikdörtgen plaka (5 renk).

Kullanım: python3 anahtarlik.py <cikti_klasoru>
Çıktı: her model için tek 3MF (parçalar ayrı) + parça parça STL + önizleme PNG.
"""
import os
import sys

import numpy as np
import trimesh
from PIL import Image
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from skimage import measure

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "..", "..", "instagram", "logo-arabaci-reklam.png")

COLORS = {
    "kirmizi": (202, 76, 75),
    "yesil": (164, 181, 66),
    "turkuaz": (101, 173, 164),
    "gri": (69, 75, 82),
}

T = 3.4        # toplam kalınlık (mm)
INLAY = 0.6    # renkli üst katman kalınlığı (3 katman x 0.2 mm)
BACK = 0.6     # arka yazı derinliği


# ---------------------------------------------------------------- logodan vektör

def load_masks():
    im = np.array(Image.open(LOGO).convert("RGBA")).astype(int)
    alpha = im[..., 3] > 128
    rgb = im[..., :3]
    names = list(COLORS)
    dists = np.stack([np.abs(rgb - np.array(COLORS[n])).sum(axis=2) for n in names])
    nearest = np.argmin(dists, axis=0)
    return {n: (alpha & (nearest == i)) for i, n in enumerate(names)}


def mask_to_geom(mask, crop, scale, origin):
    """Binary maskeyi shapely geometriye çevirir (mm, y yukarı)."""
    x0, y0, x1, y1 = crop
    m = np.pad(mask[y0:y1, x0:x1], 1)
    geom = Polygon()
    for c in measure.find_contours(m.astype(float), 0.5):
        if len(c) < 4:
            continue
        pts = [((col - 1 + x0 - origin[0]) * scale, -(row - 1 + y0 - origin[1]) * scale) for row, col in c]
        p = Polygon(pts).buffer(0)
        geom = geom.symmetric_difference(p)  # çift-tek kuralı: delikleri doğru çıkarır
    return geom.simplify(0.03).buffer(0)


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


def diff(a, b):
    return trimesh.boolean.difference([a, b], engine="manifold")


# ---------------------------------------------------------------- modeller

def model_a(masks):
    # Sembol: piksel 300..700 x 0..392 -> 48 mm genişlik
    crop = (290, 0, 710, 395)
    scale = 48 / 400
    origin = (500, 200)
    parts = {n: mask_to_geom(masks[n], crop, scale, origin) for n in ("kirmizi", "yesil", "turkuaz")}
    mark = unary_union(list(parts.values()))

    # Gövde: sembolün dışına 3 mm pay, yuvarlatılmış
    outline = mark.buffer(3.2, join_style="round")
    outline = outline.buffer(4).buffer(-4)  # iç boşlukları doldur
    outline = Polygon(outline.exterior)
    # Halka tutamağı: tepe noktasının üstünde
    top_y = outline.bounds[3]
    apex_x = max(outline.exterior.coords, key=lambda p: p[1])[0]
    ring = Point(apex_x, top_y + 1.5).buffer(5.5)
    outline = unary_union([outline, ring]).buffer(1).buffer(-1)
    hole = Point(apex_x, top_y + 1.5).buffer(2.6)
    outline = outline.difference(hole)

    # Arka yazı: logodaki ARABACI kelimesi, aynalanmış
    word_mask = masks["gri"]
    wcrop = (0, 445, 1004, 632)
    wscale = 28 / 1004
    word = mask_to_geom(word_mask, wcrop, wscale, (502, 540))
    word = affinity.scale(word, xfact=-1, origin=(0, 0))  # arkadan bakınca düz okunsun
    cy = outline.bounds[1] + 13
    word = affinity.translate(word, 0, cy)
    assert outline.buffer(-1.0).contains(word), "Arka yazı gövdeye sığmadı"

    body = extrude(outline, 0, T)
    body = diff(body, extrude(mark, T - INLAY, T + 1))
    body = diff(body, extrude(word, -1, BACK))
    meshes = {"govde_beyaz": body}
    for n, g in parts.items():
        meshes[n] = extrude(g, T - INLAY, T)
    return meshes, outline


def model_b(masks):
    crop = (0, 0, 1004, 749)
    scale = 44 / 1004
    origin = (502, 374)
    parts = {n: mask_to_geom(masks[n], crop, scale, origin) for n in COLORS}
    # REKLAM yanındaki ince çizgileri yazdırılabilir kalınlığa (1 mm) getir
    tq = parts["turkuaz"]
    polys = [tq] if tq.geom_type == "Polygon" else list(tq.geoms)
    fixed = []
    for p in polys:
        minx, miny, maxx, maxy = p.bounds
        if maxy - miny < 1.0 and maxx - minx > 5:
            c = (miny + maxy) / 2
            fixed.append(box(minx, c - 0.5, maxx, c + 0.5))
        else:
            fixed.append(p)
    parts["turkuaz"] = unary_union(fixed)
    allc = unary_union(list(parts.values()))
    minx, miny, maxx, maxy = allc.bounds
    m = 4
    plate = box(minx - m, miny - m, maxx + m, maxy + m + 8).buffer(-4).buffer(4)
    hole_c = ((minx + maxx) / 2 - 17, maxy + m + 2.5)
    plate = plate.difference(Point(hole_c).buffer(2.6))

    body = extrude(plate, 0, T)
    body = diff(body, extrude(allc, T - INLAY, T + 1))
    meshes = {"govde_beyaz": body}
    for n, g in parts.items():
        meshes[n] = extrude(g, T - INLAY, T)
    return meshes, plate


# ---------------------------------------------------------------- çıktı

PREVIEW_COLORS = {"govde_beyaz": (0.96, 0.96, 0.95), **{k: tuple(c / 255 for c in v) for k, v in COLORS.items()}}


def preview(meshes, path, title, back=True):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    views = [(55, -70, "Ön"), (-55, -110, "Arka")] if back else [(55, -70, "Ön")]
    fig = plt.figure(figsize=(6 * len(views), 6), dpi=110)
    fig.patch.set_facecolor("#2b2f34")
    light = np.array([0.3, -0.5, 1.0])
    light /= np.linalg.norm(light)
    for i, (elev, azim, name) in enumerate(views):
        ax = fig.add_subplot(1, len(views), i + 1, projection="3d")
        ax.set_facecolor("#2b2f34")
        allv = np.vstack([m.vertices for m in meshes.values()])
        tris, cols = [], []
        for k, m in meshes.items():
            if name == "Arka" and k != "govde_beyaz":
                continue  # arkadan renkli parçalar görünmez; çizim hatasını önler
            base = np.array(PREVIEW_COLORS[k])
            shade = np.clip(np.abs(m.face_normals @ light), 0.35, 1.0)[:, None]
            tris.append(m.triangles)
            cols.append(np.clip(base * (0.45 + 0.55 * shade), 0, 1))
        # tek koleksiyon: matplotlib yüzleri derinliğe göre birlikte sıralasın
        pc = Poly3DCollection(np.vstack(tris), facecolors=np.vstack(cols), edgecolors="none")
        ax.add_collection3d(pc)
        mn, mx = allv.min(0), allv.max(0)
        c = (mn + mx) / 2
        r = (mx - mn).max() / 2
        ax.set_xlim(c[0] - r, c[0] + r)
        ax.set_ylim(c[1] - r, c[1] + r)
        ax.set_zlim(c[2] - r, c[2] + r)
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(name, color="white")
    fig.suptitle(title, color="white", fontsize=14)
    plt.tight_layout()
    plt.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def export(meshes, outline, out_dir, name, title, back=True):
    d = os.path.join(out_dir, name)
    os.makedirs(d, exist_ok=True)
    for k, m in meshes.items():
        assert m.is_watertight, f"{name}/{k} su geçirmez değil"
        m.export(os.path.join(d, f"{name}_{k}.stl"))
    scene = trimesh.Scene()
    for k, m in meshes.items():
        scene.add_geometry(m, node_name=k, geom_name=k)
    scene.export(os.path.join(d, f"{name}.3mf"))
    preview(meshes, os.path.join(d, f"{name}_onizleme.png"), title, back)
    minx, miny, maxx, maxy = outline.bounds
    print(f"{name}: {maxx - minx:.1f} x {maxy - miny:.1f} x {T} mm, parçalar: {', '.join(meshes)}")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    masks = load_masks()
    ma, oa = model_a(masks)
    export(ma, oa, out, "model-a-sembol", "Model A - Sembol anahtarlık (4 renk)")
    mb, ob = model_b(masks)
    export(mb, ob, out, "model-b-tam-logo", "Model B - Tam logo anahtarlık (5 renk)", back=False)


if __name__ == "__main__":
    main()
