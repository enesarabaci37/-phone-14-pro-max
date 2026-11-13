import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
def mask(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
    bg = np.median(np.concatenate([a[:40,:40].reshape(-1,3), a[:40,-40:].reshape(-1,3)]),0)
    d = np.abs(a-bg).max(2)
    m = d > 28
    m = ndi.binary_opening(m, iterations=2)
    lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1,n+1))
    m = lab == (np.argmax(sizes)+1)
    m = ndi.binary_closing(m, iterations=3)
    return ndi.binary_fill_holes(m), a.astype(np.uint8)
if __name__ == '__main__':
    d = sys.argv[1]
    for i in (1,2,3):
        m,_ = mask(f'{d}/{i}.webp'); ys,xs=np.nonzero(m); print(i, ys.min(),ys.max(),xs.min(),xs.max())
        Image.fromarray((m*255).astype(np.uint8)).resize((256,384)).save(f'{sys.argv[2]}/mask{i}.png')
