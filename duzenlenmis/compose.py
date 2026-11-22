import sys, numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage
src, pm, tm, out = sys.argv[1:5]; extra = sys.argv[5:]
img = Image.open(src).convert('RGB')
W,H = img.size
p = np.asarray(Image.open(pm).convert('L')).astype(np.float32)/255
t = np.asarray(Image.open(tm).convert('L')) > 127
t = ndimage.binary_fill_holes(ndimage.binary_closing(t, iterations=6))
# table top edge: per-column first table row, smoothed so hands/papers can't punch gaps
cols = np.where(t.any(0), t.argmax(0), H)
top = np.minimum(cols, ndimage.median_filter(cols, size=301, mode='nearest'))
t = (np.arange(H)[:,None] >= top[None,:])
t = t.astype(np.float32)
m = np.maximum(p, t)
for e in extra:
    em = np.asarray(Image.open(e).convert('L')).astype(np.float32)/255
    m = np.maximum(m, ndimage.grey_dilation(em, size=5))
# fill any holes inside the union
# fill small enclosed gaps (pens, between fingers) but not larger wall patches
mb = m > 0.5
holes = ndimage.binary_fill_holes(mb) & ~mb
lab, n = ndimage.label(holes)
sizes = ndimage.sum(holes, lab, range(1, n+1))
small = np.isin(lab, np.nonzero(sizes < 3000)[0] + 1)
m = np.where(small, 1.0, m)
print('holes', n, sorted(sizes.astype(int))[-8:])
mask = Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))

# background: deep red-to-dark gradient with soft spotlight + club-colour stripes
y, x = np.mgrid[0:H, 0:W].astype(np.float32)
top = np.array([120, 12, 18]); bot = np.array([25, 5, 8])
g = (y/H)[...,None]
bg = top*(1-g) + bot*g
cx, cy = W*0.5, H*0.42
r = np.sqrt(((x-cx)/(W*0.75))**2 + ((y-cy)/(H*0.55))**2)
glow = np.clip(1-r, 0, 1)[...,None]**1.6
bg = bg + glow*np.array([150, 70, 20])
# diagonal subtle stripes in gold
stripe = ((x + y*0.6) // (W*0.09)) % 2
bg = bg + (stripe[...,None]*np.array([7, 5, 0]))
bg = np.clip(bg, 0, 255).astype(np.uint8)
bgi = Image.fromarray(bg)
# gold accent band near bottom-left/right corners
d = ImageDraw.Draw(bgi, 'RGBA')

# soft shadow of subjects on backdrop
sh = mask.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v*0.55))
dark = Image.new('RGB', (W,H), (0,0,0))
bgi = Image.composite(dark, bgi, sh.transform((W,H), Image.AFFINE, (1,0,-20,0,1,-25)))
res = Image.composite(img, bgi, mask)
res.save(out, quality=95)
