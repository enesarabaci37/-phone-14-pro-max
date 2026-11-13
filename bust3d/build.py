"""Build a textured 3D bust (GLB) from front + two side photos via a rounded visual hull.
usage: python3 build.py <images_dir> <out_dir>   (images: 1=right side, 2=left side, 3=front)"""
import sys, numpy as np, trimesh
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from masks import mask

src, out = sys.argv[1], sys.argv[2]
views = {}
for i in (1, 2, 3):
    m, img = mask(f'{src}/{i}.webp')
    ys, xs = np.nonzero(m)
    views[i] = dict(m=m, img=img, top=ys.min(), H=ys.max() - ys.min(), c=(xs.min() + xs.max()) / 2)

def col_row(i, h, y):  # world horizontal coord h, height y -> pixel col,row
    v = views[i]; sign = {3: 1, 1: 1, 2: -1}[i]
    return v['c'] + sign * h * v['H'], v['top'] + (1 - y) * v['H']

def sample(i, h, y):
    c, r = col_row(i, h, y); m = views[i]['m']
    c = np.clip(np.round(c).astype(int), 0, m.shape[1] - 1); r = np.clip(np.round(r).astype(int), 0, m.shape[0] - 1)
    return m[r, c]

NY = 340; d = 1 / NY
ys = np.linspace(-0.01, 1.01, int(1.02 * NY))
xs = np.arange(-0.36, 0.36, d); zs = np.arange(-0.30, 0.30, d)
Y, X = np.meshgrid(ys, xs, indexing='ij'); F = sample(3, X, Y)                     # front mask [y,x]
Y2, Z = np.meshgrid(ys, zs, indexing='ij'); S = sample(1, Z, Y2) | sample(2, Z, Y2)  # side mask [y,z]

def runs(row, coords):  # per-cell (center, halfwidth) of the run it belongs to
    lab, n = ndi.label(row); cen = np.zeros(len(row)); hw = np.ones(len(row))
    for k in range(1, n + 1):
        idx = np.nonzero(lab == k)[0]; a, b = coords[idx[0]], coords[idx[-1]]
        cen[idx] = (a + b) / 2; hw[idx] = (b - a) / 2 + d / 2
    return cen, hw

vol = np.zeros((len(ys), len(xs), len(zs)), np.float32)
for j, y in enumerate(ys):
    if not F[j].any() or not S[j].any(): continue
    cx, hx = runs(F[j], xs); cz, hz = runs(S[j], zs)
    p = 8.0 if y < 0.30 else (2.6 if y < 0.62 else 2.2)   # boxy pedestal, rounded body/head
    u = np.abs((xs - cx) / hx)[:, None]; w = np.abs((zs - cz) / hz)[None, :]
    val = 1 - (u ** p + w ** p)
    val[~F[j], :] = -1; val[:, ~S[j]] = -1
    vol[j] = val
vol = ndi.gaussian_filter(vol, (3.0, 1.3, 1.3))  # extra vertical smoothing removes slice banding
vol = np.pad(vol, 2, constant_values=-1)
verts, faces, _, _ = measure.marching_cubes(vol, 0.0)
verts = (verts - 2)
P = np.c_[xs[0] + verts[:, 1] * d, ys[0] + verts[:, 0] * (ys[1] - ys[0]), zs[0] + verts[:, 2] * d]
mesh = trimesh.Trimesh(P, faces[:, ::-1], process=True)
if mesh.volume < 0: mesh.invert()
trimesh.smoothing.filter_taubin(mesh, iterations=40)
mesh = mesh.simplify_quadric_decimation(face_count=140000)
print('faces', len(mesh.faces))

# texture atlas: [right side | left side | front]
W, Hh = 1024, 1536
atlas = Image.new('RGB', (3 * W, Hh))
for slot, i in enumerate((1, 2, 3)): atlas.paste(Image.fromarray(views[i]['img']), (slot * W, 0))
n = mesh.face_normals
score = np.stack([-n[:, 0], n[:, 0], np.where(n[:, 2] > -0.05, n[:, 2] * 1.15, -9)], 1)
choice = score.argmax(1)
parts = []
for slot, i in enumerate((1, 2, 3)):
    sub = mesh.submesh([np.nonzero(choice == slot)[0]], append=True)
    v = sub.vertices; h = v[:, 0] if i == 3 else v[:, 2]
    c, r = col_row(i, h, v[:, 1])
    uv = np.c_[(slot * W + c) / (3 * W), 1 - r / Hh]
    sub.visual = trimesh.visual.TextureVisuals(uv=uv)
    parts.append(sub)
full = trimesh.util.concatenate(parts)
import io
buf = io.BytesIO(); atlas.save(buf, 'JPEG', quality=88); buf.seek(0); atlas = Image.open(buf)
mat = trimesh.visual.material.PBRMaterial(baseColorTexture=atlas, metallicFactor=0.0, roughnessFactor=0.75)
full.visual = trimesh.visual.TextureVisuals(uv=full.visual.uv, material=mat)
full.apply_translation([0, 0, 0]); full.apply_scale(2.0)
full.export(f'{out}/bust.glb')
mesh.export(f'{out}/bust.stl')
print('done', full.bounds)
