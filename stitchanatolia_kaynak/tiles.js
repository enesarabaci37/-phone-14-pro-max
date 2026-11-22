// Büyük boy şema parçaları: desen, karesi ~4.5 mm olacak şekilde sayfalara bölünür.
// pattern2.html, listing2.html ve bundle.html aynı hesabı kullanır.
const MAXC = 38, MAXR = 54;
function splitEven(n, max) {
  const k = Math.ceil(n / max), out = []; let a = 0;
  for (let i = 0; i < k; i++) { const len = Math.round((n - a) / (k - i)); out.push([a, a + len]); a += len; }
  return out;
}
function tiles(W, H) {
  const xs = splitEven(W, MAXC), ys = splitEven(H, MAXR), t = [];
  ys.forEach(([y0, y1], j) => xs.forEach(([x0, x1], i) => t.push({ x0, x1, y0, y1, i, j, nx: xs.length, ny: ys.length })));
  return t;
}
function pageCount(W, H) { return 5 + tiles(W, H).length; }
