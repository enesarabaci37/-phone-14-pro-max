/*
 * VektörSihirbazı – bitmap → vektör motoru
 *
 * Aşamalar (Vector Magic'in yaklaşımına benzer):
 *  1. (İsteğe bağlı) kenar koruyan gürültü azaltma (bilateral filtre)
 *  2. Küçük görüntüleri büyütme: anti-aliasing'deki ara tonlar sayesinde
 *     sınırlar alt-piksel hassasiyetle bulunur
 *  3. Lab renk uzayında palet çıkarma (yalnızca "düz" alanlardan örnekleme,
 *     böylece kenar karışımları sahte renk oluşturmaz)
 *  4. Piksel sınıflandırma + kenar karışımı (anti-aliasing) düzeltmesi
 *  5. Bağlı bölgeler, küçük lekelerin komşuya katılması
 *  6. Paylaşılan kenar grafiği: iki bölgeyi ayıran her sınır yalnızca bir kez
 *     eğriye çevrilir → şekiller arasında boşluk/üst üste binme olmaz
 *  7. Köşe tespiti, yumuşatma, Schneider Bezier eğri uydurma, düz çizgi tespiti
 *  8. SVG / EPS / PDF çıktıları
 *
 * Tarayıcıda <script>, Web Worker ve Node.js (require) ile çalışır.
 */
(function (root) {
  'use strict';

  var DEFAULTS = {
    mode: 'auto',          // 'auto' (logo/çizim) | 'photo' | 'bw'
    colors: 0,             // 0 = otomatik
    colorSensitivity: 14,  // otomatik paletteki minimum renk farkı (ΔE)
    minArea: 4,            // bu alandan (orijinal px²) küçük lekeler silinir
    tolerance: 0.5,        // eğri uydurma hatası (orijinal px)
    cornerAngle: 130,      // bu açıdan keskin dönüşler köşe sayılır (derece)
    smoothing: 3,          // yumuşatma geçişi
    denoise: false,
    upscale: true,
    blendFix: true,
    thinLines: true,       // ince çizgi / küçük yazı koruması
    bwThreshold: -1,       // siyah-beyaz eşiği (L*, -1 = otomatik / Otsu)
    palette: null,         // sabit palet [[r,g,b],...]
    maxPixels: 3000000,
    alphaThreshold: 128,
  };

  var PRESETS = {
    auto:  { colors: 0, minArea: 4, tolerance: 0.5, cornerAngle: 130, smoothing: 3, denoise: false, upscale: true, blendFix: true },
    photo: { colors: 24, minArea: 20, tolerance: 0.9, cornerAngle: 110, smoothing: 3, denoise: true, upscale: false, blendFix: false },
    bw:    { colors: 2, minArea: 4, tolerance: 0.5, cornerAngle: 130, smoothing: 3, denoise: false, upscale: true, blendFix: false },
  };

  // ---------------------------------------------------------------- yardımcılar
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function srgbToLin(c) { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
  function linToSrgb(c) {
    c = c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
    return Math.max(0, Math.min(255, c * 255));
  }
  var LIN = new Float64Array(256);
  for (var li = 0; li < 256; li++) LIN[li] = srgbToLin(li);
  function labF(t) { return t > 0.008856451679 ? Math.cbrt(t) : 7.787037037 * t + 0.137931034; }

  function linRgbToLab(R, G, B, out, o) {
    var fx = labF((R * 0.4124564 + G * 0.3575761 + B * 0.1804375) / 0.95047);
    var fy = labF(R * 0.2126729 + G * 0.7151522 + B * 0.0721750);
    var fz = labF((R * 0.0193339 + G * 0.1191920 + B * 0.9503041) / 1.08883);
    out[o] = 116 * fy - 16; out[o + 1] = 500 * (fx - fy); out[o + 2] = 200 * (fy - fz);
  }
  function rgbToLab(r, g, b, out, o) { linRgbToLab(LIN[r], LIN[g], LIN[b], out, o || 0); }
  function rgbToLabF(r, g, b, out, o) { linRgbToLab(srgbToLin(r), srgbToLin(g), srgbToLin(b), out, o || 0); }
  function labToRgb(L, a, b) {
    var fy = (L + 16) / 116, fx = fy + a / 500, fz = fy - b / 200;
    function inv(t) { var t3 = t * t * t; return t3 > 0.008856451679 ? t3 : (t - 0.137931034) / 7.787037037; }
    var X = inv(fx) * 0.95047, Y = inv(fy), Z = inv(fz) * 1.08883;
    return [
      Math.round(linToSrgb(X * 3.2404542 - Y * 1.5371385 - Z * 0.4985314)),
      Math.round(linToSrgb(-X * 0.9692660 + Y * 1.8760108 + Z * 0.0415560)),
      Math.round(linToSrgb(X * 0.0556434 - Y * 0.2040259 + Z * 1.0572252)),
    ];
  }

  // -------------------------------------------------------- 1. gürültü azaltma
  function bilateral(src, w, h, radius, sigmaR) {
    var out = new Uint8ClampedArray(src.length);
    var size = 2 * radius + 1, ws = new Float64Array(size * size), sigS = radius / 1.5 + 0.5;
    for (var dy = -radius; dy <= radius; dy++)
      for (var dx = -radius; dx <= radius; dx++)
        ws[(dy + radius) * size + dx + radius] = Math.exp(-(dx * dx + dy * dy) / (2 * sigS * sigS));
    var LUT_N = (3 * 255 * 255 >> 4) + 1, lut = new Float64Array(LUT_N);
    for (var i = 0; i < LUT_N; i++) lut[i] = Math.exp(-(i << 4) / (2 * sigmaR * sigmaR));
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) {
        var p = (y * w + x) * 4, r0 = src[p], g0 = src[p + 1], b0 = src[p + 2];
        var sr = 0, sg = 0, sb = 0, sw = 0;
        for (dy = -radius; dy <= radius; dy++) {
          var yy = y + dy; if (yy < 0 || yy >= h) continue;
          for (dx = -radius; dx <= radius; dx++) {
            var xx = x + dx; if (xx < 0 || xx >= w) continue;
            var q = (yy * w + xx) * 4;
            var dr = src[q] - r0, dg = src[q + 1] - g0, db = src[q + 2] - b0;
            var wt = ws[(dy + radius) * size + dx + radius] * lut[(dr * dr + dg * dg + db * db) >> 4];
            sr += src[q] * wt; sg += src[q + 1] * wt; sb += src[q + 2] * wt; sw += wt;
          }
        }
        out[p] = sr / sw; out[p + 1] = sg / sw; out[p + 2] = sb / sw; out[p + 3] = src[p + 3];
      }
    }
    return out;
  }

  // ------------------------------------------------------- 2. yeniden örnekleme
  function resample(src, w, h, nw, nh) {
    var out = new Uint8ClampedArray(nw * nh * 4);
    var x, y, c, p;
    // önceden çarpılmış alfa (premultiplied) – şeffaf piksel rengi kenara sızmasın
    var pm = new Float32Array(w * h * 4);
    for (p = 0; p < w * h; p++) {
      var a = src[p * 4 + 3] / 255;
      pm[p * 4] = src[p * 4] * a; pm[p * 4 + 1] = src[p * 4 + 1] * a; pm[p * 4 + 2] = src[p * 4 + 2] * a; pm[p * 4 + 3] = src[p * 4 + 3];
    }
    var acc = [0, 0, 0, 0];
    if (nw >= w) {
      var sx = w / nw, sy = h / nh;
      for (y = 0; y < nh; y++) {
        var fy = (y + 0.5) * sy - 0.5; if (fy < 0) fy = 0; if (fy > h - 1) fy = h - 1;
        var y0 = Math.floor(fy), y1 = Math.min(h - 1, y0 + 1), ty = fy - y0;
        for (x = 0; x < nw; x++) {
          var fx = (x + 0.5) * sx - 0.5; if (fx < 0) fx = 0; if (fx > w - 1) fx = w - 1;
          var x0 = Math.floor(fx), x1 = Math.min(w - 1, x0 + 1), tx = fx - x0;
          var i00 = (y0 * w + x0) * 4, i01 = (y0 * w + x1) * 4, i10 = (y1 * w + x0) * 4, i11 = (y1 * w + x1) * 4;
          for (c = 0; c < 4; c++)
            acc[c] = (pm[i00 + c] * (1 - tx) + pm[i01 + c] * tx) * (1 - ty) + (pm[i10 + c] * (1 - tx) + pm[i11 + c] * tx) * ty;
          writePx(out, (y * nw + x) * 4, acc);
        }
      }
    } else {
      for (y = 0; y < nh; y++) {
        var ya = Math.floor(y * h / nh), yb = Math.max(ya + 1, Math.floor((y + 1) * h / nh));
        for (x = 0; x < nw; x++) {
          var xa = Math.floor(x * w / nw), xb = Math.max(xa + 1, Math.floor((x + 1) * w / nw));
          acc[0] = acc[1] = acc[2] = acc[3] = 0;
          for (var yy = ya; yy < yb; yy++) for (var xx = xa; xx < xb; xx++) {
            var q = (yy * w + xx) * 4;
            acc[0] += pm[q]; acc[1] += pm[q + 1]; acc[2] += pm[q + 2]; acc[3] += pm[q + 3];
          }
          var n = (yb - ya) * (xb - xa);
          acc[0] /= n; acc[1] /= n; acc[2] /= n; acc[3] /= n;
          writePx(out, (y * nw + x) * 4, acc);
        }
      }
    }
    return out;
  }
  function writePx(out, o, acc) {
    var a = acc[3] / 255;
    if (a > 1e-4) { out[o] = acc[0] / a; out[o + 1] = acc[1] / a; out[o + 2] = acc[2] / a; }
    out[o + 3] = acc[3];
  }

  // ---------------------------------------------------------------- 3. palet
  function dist2(A, i, B, j) {
    var d0 = A[i] - B[j], d1 = A[i + 1] - B[j + 1], d2 = A[i + 2] - B[j + 2];
    return d0 * d0 + d1 * d1 + d2 * d2;
  }

  function lloyd(S, N, C, k, iters) {
    var assign = new Int32Array(N), sums = new Float64Array(k * 3), cnt = new Int32Array(k);
    for (var it = 0; it < iters; it++) {
      sums.fill(0); cnt.fill(0);
      var moved = 0, farIdx = -1, farD = -1;
      for (var i = 0; i < N; i++) {
        var best = 0, bd = Infinity;
        for (var c = 0; c < k; c++) { var d = dist2(S, i * 3, C, c * 3); if (d < bd) { bd = d; best = c; } }
        if (assign[i] !== best) moved++;
        assign[i] = best; cnt[best]++;
        sums[best * 3] += S[i * 3]; sums[best * 3 + 1] += S[i * 3 + 1]; sums[best * 3 + 2] += S[i * 3 + 2];
        if (bd > farD) { farD = bd; farIdx = i; }
      }
      for (c = 0; c < k; c++) {
        if (cnt[c] > 0) { C[c * 3] = sums[c * 3] / cnt[c]; C[c * 3 + 1] = sums[c * 3 + 1] / cnt[c]; C[c * 3 + 2] = sums[c * 3 + 2] / cnt[c]; }
        else if (farIdx >= 0) { C[c * 3] = S[farIdx * 3]; C[c * 3 + 1] = S[farIdx * 3 + 1]; C[c * 3 + 2] = S[farIdx * 3 + 2]; }
      }
      if (it > 0 && moved === 0) break;
    }
    return { assign: assign, count: cnt };
  }

  function kmeansPP(S, N, k, rng) {
    var C = new Float64Array(k * 3), D = new Float64Array(N);
    var f = Math.floor(rng() * N);
    C[0] = S[f * 3]; C[1] = S[f * 3 + 1]; C[2] = S[f * 3 + 2];
    for (var i = 0; i < N; i++) D[i] = dist2(S, i * 3, C, 0);
    for (var c = 1; c < k; c++) {
      var sum = 0; for (i = 0; i < N; i++) sum += D[i];
      var r = rng() * sum, pick = N - 1;
      for (i = 0; i < N; i++) { r -= D[i]; if (r <= 0) { pick = i; break; } }
      C[c * 3] = S[pick * 3]; C[c * 3 + 1] = S[pick * 3 + 1]; C[c * 3 + 2] = S[pick * 3 + 2];
      for (i = 0; i < N; i++) { var d = dist2(S, i * 3, C, c * 3); if (d < D[i]) D[i] = d; }
    }
    return C;
  }

  // Otomatik palet: baskın renkten başla, mevcut renklerle açıklanamayan
  // anlamlı bir piksel topluluğu kaldıkça yeni renk ekle.
  function autoPalette(S, N, T, maxK) {
    var bin = T / 2, minCount = Math.max(6, Math.round(N * 0.0006));
    function densest(filter) {
      var map = new Map(), bestKey = null, bestN = 0;
      for (var i = 0; i < N; i++) {
        if (filter && !filter[i]) continue;
        var key = Math.floor(S[i * 3] / bin) + ',' + Math.floor((S[i * 3 + 1] + 200) / bin) + ',' + Math.floor((S[i * 3 + 2] + 200) / bin);
        var e = map.get(key);
        if (!e) { e = [0, 0, 0, 0]; map.set(key, e); }
        e[0]++; e[1] += S[i * 3]; e[2] += S[i * 3 + 1]; e[3] += S[i * 3 + 2];
        if (e[0] > bestN) { bestN = e[0]; bestKey = key; }
      }
      var b = map.get(bestKey);
      return [b[1] / b[0], b[2] / b[0], b[3] / b[0]];
    }
    var centers = densest(null), k = 1, T2 = T * T;
    var far = new Uint8Array(N);
    while (k < maxK) {
      var C = Float64Array.from(centers), nFar = 0;
      for (var i = 0; i < N; i++) {
        var bd = Infinity;
        for (var c = 0; c < k; c++) { var d = dist2(S, i * 3, C, c * 3); if (d < bd) bd = d; }
        far[i] = bd > T2 ? 1 : 0; nFar += far[i];
      }
      if (nFar < minCount) break;
      centers = centers.concat(densest(far));
      k++;
      C = Float64Array.from(centers);
      lloyd(S, N, C, k, 4);
      centers = Array.prototype.slice.call(C);
    }
    var Cf = Float64Array.from(centers);
    lloyd(S, N, Cf, k, 15);
    // birbirine çok yakın merkezleri birleştir
    var keep = [];
    for (c = 0; c < k; c++) {
      var dup = false;
      for (var j = 0; j < keep.length; j++) if (dist2(Cf, c * 3, Cf, keep[j] * 3) < T2 * 0.6) { dup = true; break; }
      if (!dup) keep.push(c);
    }
    var out = new Float64Array(keep.length * 3);
    keep.forEach(function (c, n) { out[n * 3] = Cf[c * 3]; out[n * 3 + 1] = Cf[c * 3 + 1]; out[n * 3 + 2] = Cf[c * 3 + 2]; });
    return out;
  }

  function otsu(values, n) {
    var hist = new Float64Array(101);
    for (var i = 0; i < n; i++) hist[Math.max(0, Math.min(100, Math.round(values[i])))]++;
    var total = n, sum = 0; for (i = 0; i <= 100; i++) sum += i * hist[i];
    var sumB = 0, wB = 0, best = 50, bestV = -1;
    for (i = 0; i <= 100; i++) {
      wB += hist[i]; if (!wB) continue;
      var wF = total - wB; if (!wF) break;
      sumB += i * hist[i];
      var mB = sumB / wB, mF = (sum - sumB) / wF, v = wB * wF * (mB - mF) * (mB - mF);
      if (v > bestV) { bestV = v; best = i + 0.5; }
    }
    return best;
  }

  // ----------------------------------------------------- 5. bağlı bölgeler
  function components(cls, w, h) {
    var n = w * h, comp = new Int32Array(n).fill(-1), stack = new Int32Array(n);
    var area = [], ccls = [], count = 0;
    for (var s = 0; s < n; s++) {
      if (comp[s] !== -1) continue;
      var c = cls[s], top = 0, a = 0;
      comp[s] = count; stack[top++] = s;
      while (top) {
        var p = stack[--top]; a++;
        var x = p % w;
        if (x > 0 && comp[p - 1] === -1 && cls[p - 1] === c) { comp[p - 1] = count; stack[top++] = p - 1; }
        if (x < w - 1 && comp[p + 1] === -1 && cls[p + 1] === c) { comp[p + 1] = count; stack[top++] = p + 1; }
        if (p >= w && comp[p - w] === -1 && cls[p - w] === c) { comp[p - w] = count; stack[top++] = p - w; }
        if (p + w < n && comp[p + w] === -1 && cls[p + w] === c) { comp[p + w] = count; stack[top++] = p + w; }
      }
      area.push(a); ccls.push(c); count++;
    }
    return { comp: comp, count: count, area: area, cls: ccls };
  }

  function removeSpeckles(cls, w, h, minArea) {
    var n = w * h, R;
    for (var iter = 0; iter < 8; iter++) {
      R = components(cls, w, h);
      if (minArea <= 1) break;
      var small = [];
      for (var c = 0; c < R.count; c++) if (R.area[c] < minArea) small.push(c);
      if (!small.length) break;
      small.sort(function (a, b) { return R.area[a] - R.area[b]; });
      // bölge başına piksel listeleri
      var start = new Int32Array(R.count + 1);
      for (var p = 0; p < n; p++) start[R.comp[p] + 1]++;
      for (c = 0; c < R.count; c++) start[c + 1] += start[c];
      var fill = start.slice(0, R.count), list = new Int32Array(n);
      for (p = 0; p < n; p++) list[fill[R.comp[p]]++] = p;
      var touched = new Uint8Array(R.count), comp = R.comp, changed = false;
      for (var si = 0; si < small.length; si++) {
        c = small[si];
        if (touched[c] || R.area[c] >= minArea) continue;
        var nb = new Map();
        for (var k = start[c]; k < start[c + 1]; k++) {
          p = list[k]; var x = p % w, q;
          if (x > 0 && (q = comp[p - 1]) !== c) nb.set(q, (nb.get(q) || 0) + 1);
          if (x < w - 1 && (q = comp[p + 1]) !== c) nb.set(q, (nb.get(q) || 0) + 1);
          if (p >= w && (q = comp[p - w]) !== c) nb.set(q, (nb.get(q) || 0) + 1);
          if (p + w < n && (q = comp[p + w]) !== c) nb.set(q, (nb.get(q) || 0) + 1);
        }
        var best = -1, bc = -1;
        nb.forEach(function (v, key) { if (v > bc || (v === bc && R.area[key] > R.area[best])) { bc = v; best = key; } });
        if (best < 0) continue;
        var nc = R.cls[best];
        for (k = start[c]; k < start[c + 1]; k++) { p = list[k]; cls[p] = nc; comp[p] = best; }
        R.area[best] += R.area[c]; R.area[c] = 0;
        touched[best] = 1; changed = true;
      }
      if (!changed) break;
    }
    return components(cls, w, h);
  }

  // ------------------------------------------- 6. paylaşılan kenar grafiği
  var DX = [1, 0, -1, 0], DY = [0, 1, 0, -1]; // D, G, B, K (ekranda saat yönü)

  function buildGraph(lab, w, h) {
    var W1 = w + 1, nh = w * (h + 1), nv = W1 * h;
    function L(x, y) { return (x < 0 || y < 0 || x >= w || y >= h) ? -1 : lab[y * w + x]; }
    var isB = new Uint8Array(nh + nv), x, y;
    for (y = 0; y <= h; y++) for (x = 0; x < w; x++) isB[y * w + x] = L(x, y - 1) !== L(x, y) ? 1 : 0;
    for (y = 0; y < h; y++) for (x = 0; x <= w; x++) isB[nh + y * W1 + x] = L(x - 1, y) !== L(x, y) ? 1 : 0;
    function edge(x, y, d) {
      switch (d) {
        case 0: return x < w ? y * w + x : -1;
        case 1: return y < h ? nh + y * W1 + x : -1;
        case 2: return x > 0 ? y * w + x - 1 : -1;
        default: return y > 0 ? nh + (y - 1) * W1 + x : -1;
      }
    }
    function leftRight(x, y, d) {
      switch (d) {
        case 0: return [L(x, y - 1), L(x, y)];
        case 1: return [L(x, y), L(x - 1, y)];
        case 2: return [L(x - 1, y), L(x - 1, y - 1)];
        default: return [L(x - 1, y - 1), L(x, y - 1)];
      }
    }
    var nVert = W1 * (h + 1), isNode = new Uint8Array(nVert);
    for (y = 0; y <= h; y++) for (x = 0; x <= w; x++) {
      var deg = 0;
      for (var d = 0; d < 4; d++) { var e = edge(x, y, d); if (e >= 0 && isB[e]) deg++; }
      if (deg >= 3) isNode[y * W1 + x] = 1;
    }
    isNode[0] = isNode[w] = isNode[h * W1] = isNode[h * W1 + w] = 1;

    var visited = new Uint8Array(nh + nv), chains = [], nodeOut = new Map();
    function trace(x0, y0, d0, closedStart) {
      var lr = leftRight(x0, y0, d0), pts = [x0, y0], x = x0, y = y0, d = d0;
      visited[edge(x, y, d)] = 1;
      x += DX[d]; y += DY[d]; pts.push(x, y);
      while (!isNode[y * W1 + x] && !(x === x0 && y === y0)) {
        var nd = -1, ne = -1, cands = [(d + 3) & 3, d, (d + 1) & 3];
        for (var i = 0; i < 3; i++) {
          var e = edge(x, y, cands[i]);
          if (e >= 0 && isB[e] && !visited[e]) { nd = cands[i]; ne = e; break; }
        }
        if (nd < 0) break;
        visited[ne] = 1; d = nd; x += DX[d]; y += DY[d]; pts.push(x, y);
      }
      var ch = { pts: pts, left: lr[0], right: lr[1], firstDir: d0, lastDir: d, closed: !!closedStart,
        start: y0 * W1 + x0, end: y * W1 + x };
      chains.push(ch);
      return chains.length - 1;
    }
    for (y = 0; y <= h; y++) for (x = 0; x <= w; x++) {
      var v = y * W1 + x;
      if (!isNode[v]) continue;
      for (d = 0; d < 4; d++) {
        e = edge(x, y, d);
        if (e < 0 || !isB[e] || visited[e]) continue;
        var ci = trace(x, y, d, false), ch = chains[ci];
        nodeOut.set(v * 4 + d, ci * 2);
        nodeOut.set(ch.end * 4 + ((ch.lastDir + 2) & 3), ci * 2 + 1);
      }
    }
    // düğümsüz kapalı döngüler (ör. başka bir bölgenin içindeki daire)
    for (e = 0; e < nh; e++) {
      if (!isB[e] || visited[e]) continue;
      trace(e % w, Math.floor(e / w), 0, true);
    }
    for (e = nh; e < nh + nv; e++) {
      if (!isB[e] || visited[e]) continue;
      var k = e - nh;
      trace(k % W1, Math.floor(k / W1), 1, true);
    }
    return { chains: chains, nodeOut: nodeOut };
  }

  // her bölge için sınır döngüleri (yarım-kenar dizileri, bölge solda)
  function buildLoops(G, compCls, skipCls) {
    var chains = G.chains, nHE = chains.length * 2, used = new Uint8Array(nHE), loops = [];
    function leftOf(he) { var c = chains[he >> 1]; return (he & 1) ? c.right : c.left; }
    for (var he = 0; he < nHE; he++) {
      if (used[he]) continue;
      var region = leftOf(he);
      if (region < 0 || compCls[region] === skipCls) { used[he] = 1; continue; }
      var loop = [he]; used[he] = 1;
      var ch = chains[he >> 1];
      if (!ch.closed) {
        var cur = he;
        for (var guard = 0; guard < nHE; guard++) {
          var c = chains[cur >> 1], back = cur & 1;
          var v = back ? c.start : c.end, d = back ? ((c.firstDir + 2) & 3) : c.lastDir;
          var next = -1, cands = [(d + 3) & 3, d, (d + 1) & 3];
          for (var i = 0; i < 3; i++) {
            var hx = G.nodeOut.get(v * 4 + cands[i]);
            if (hx !== undefined && leftOf(hx) === region) { next = hx; break; }
          }
          if (next < 0 || next === loop[0] || used[next]) break;
          used[next] = 1; loop.push(next); cur = next;
        }
      }
      loops.push({ cls: compCls[region], region: region, hes: loop });
    }
    return loops;
  }

  // ------------------------------------------------------ 7. eğri uydurma
  function detectCorners(P, closed, cosT, s1) {
    var n = P.length, corners = [];
    if (n < 5) return corners;
    var s = Math.min(s1, Math.floor(n / 4)), s2 = Math.max(1, Math.round(s / 2));
    if (s < 2) return corners;
    function cosAt(i, sc) {
      var a, b;
      if (closed) { a = P[(i - sc + n) % n]; b = P[(i + sc) % n]; }
      else { a = P[Math.max(0, i - sc)]; b = P[Math.min(n - 1, i + sc)]; }
      var p = P[i], ax = a[0] - p[0], ay = a[1] - p[1], bx = b[0] - p[0], by = b[1] - p[1];
      var la = Math.hypot(ax, ay), lb = Math.hypot(bx, by);
      if (la < 1e-9 || lb < 1e-9) return -1;
      return (ax * bx + ay * by) / (la * lb);
    }
    var cs = new Float64Array(n).fill(-2);
    var from = closed ? 0 : 2, to = closed ? n : n - 2;
    for (var i = from; i < to; i++) {
      var c1 = cosAt(i, s);
      if (c1 > cosT && cosAt(i, s2) > cosT - 0.15) cs[i] = c1;
    }
    // yerel maksimum (en keskin nokta) seçimi
    for (i = from; i < to; i++) {
      if (cs[i] < -1.5) continue;
      var isMax = true;
      for (var j = -s; j <= s && isMax; j++) {
        if (!j) continue;
        var k = i + j;
        if (closed) k = (k + n) % n; else if (k < 0 || k >= n) continue;
        if (cs[k] > cs[i] || (cs[k] === cs[i] && j < 0)) isMax = false;
      }
      if (isMax) corners.push(i);
    }
    return corners;
  }

  function smoothOpen(q, passes) {
    var r = q.map(function (p) { return [p[0], p[1]]; }), k = r.length - 1;
    for (var it = 0; it < passes; it++) {
      var prev = r.map(function (p) { return [p[0], p[1]]; });
      for (var i = 1; i < k; i++) {
        r[i][0] = (prev[i - 1][0] + 2 * prev[i][0] + prev[i + 1][0]) / 4;
        r[i][1] = (prev[i - 1][1] + 2 * prev[i][1] + prev[i + 1][1]) / 4;
      }
    }
    return r;
  }
  function smoothClosed(q, passes) {
    var r = q.map(function (p) { return [p[0], p[1]]; }), n = r.length;
    for (var it = 0; it < passes; it++) {
      var prev = r.map(function (p) { return [p[0], p[1]]; });
      for (var i = 0; i < n; i++) {
        var a = prev[(i - 1 + n) % n], b = prev[(i + 1) % n];
        r[i][0] = (a[0] + 2 * prev[i][0] + b[0]) / 4;
        r[i][1] = (a[1] + 2 * prev[i][1] + b[1]) / 4;
      }
    }
    return r;
  }

  function sub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function add(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
  function mul(a, s) { return [a[0] * s, a[1] * s]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1]; }
  function norm(a) { var l = Math.hypot(a[0], a[1]); return l < 1e-12 ? [0, 0] : [a[0] / l, a[1] / l]; }
  function dist(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); }

  function bez(b, t) {
    var mt = 1 - t, a = mt * mt * mt, c = 3 * mt * mt * t, d = 3 * mt * t * t, e = t * t * t;
    return [a * b[0][0] + c * b[1][0] + d * b[2][0] + e * b[3][0], a * b[0][1] + c * b[1][1] + d * b[2][1] + e * b[3][1]];
  }

  // Philip J. Schneider, "An Algorithm for Automatically Fitting Digitized Curves" (Graphics Gems)
  function fitCubic(d, first, last, t1, t2, err2, out, depth) {
    var nPts = last - first + 1, dd;
    if (nPts === 2 || depth > 40) {
      dd = dist(d[first], d[last]) / 3;
      out.push([d[first], add(d[first], mul(t1, dd)), add(d[last], mul(t2, dd)), d[last]]);
      return;
    }
    var u = chordParam(d, first, last);
    var b = genBezier(d, first, last, u, t1, t2);
    var me = maxError(d, first, last, b, u);
    if (me[0] < err2) { out.push(b); return; }
    if (me[0] < err2 * 4) {
      for (var i = 0; i < 20; i++) {
        var up = reparam(d, first, last, u, b);
        b = genBezier(d, first, last, up, t1, t2);
        me = maxError(d, first, last, b, up);
        if (me[0] < err2) { out.push(b); return; }
        u = up;
      }
    }
    var split = me[1];
    var tc = norm(sub(d[split - 1], d[split + 1]));
    if (tc[0] === 0 && tc[1] === 0) tc = norm(sub(d[split - 1], d[split]));
    fitCubic(d, first, split, t1, tc, err2, out, depth + 1);
    fitCubic(d, split, last, mul(tc, -1), t2, err2, out, depth + 1);
  }
  function chordParam(d, first, last) {
    var u = [0];
    for (var i = first + 1; i <= last; i++) u.push(u[u.length - 1] + dist(d[i], d[i - 1]));
    var tot = u[u.length - 1] || 1;
    for (i = 0; i < u.length; i++) u[i] /= tot;
    return u;
  }
  function genBezier(d, first, last, u, t1, t2) {
    var p0 = d[first], p3 = d[last], C00 = 0, C01 = 0, C11 = 0, X0 = 0, X1 = 0;
    for (var i = 0; i < u.length; i++) {
      var t = u[i], mt = 1 - t, b0 = mt * mt * mt, b1 = 3 * mt * mt * t, b2 = 3 * mt * t * t, b3 = t * t * t;
      var A0 = mul(t1, b1), A1 = mul(t2, b2);
      C00 += dot(A0, A0); C01 += dot(A0, A1); C11 += dot(A1, A1);
      var tmp = sub(d[first + i], add(mul(p0, b0 + b1), mul(p3, b2 + b3)));
      X0 += dot(A0, tmp); X1 += dot(A1, tmp);
    }
    var det = C00 * C11 - C01 * C01, seg = dist(p0, p3), al = 0, ar = 0;
    if (Math.abs(det) > 1e-12) { al = (X0 * C11 - X1 * C01) / det; ar = (C00 * X1 - C01 * X0) / det; }
    var eps = 1e-6 * seg;
    if (al < eps || ar < eps || al > seg * 1.6 || ar > seg * 1.6) { al = ar = seg / 3; }
    return [p0, add(p0, mul(t1, al)), add(p3, mul(t2, ar)), p3];
  }
  function maxError(d, first, last, b, u) {
    var maxD = 0, split = Math.floor((last - first + 1) / 2) + first;
    for (var i = first + 1; i < last; i++) {
      var p = bez(b, u[i - first]), dx = p[0] - d[i][0], dy = p[1] - d[i][1], e = dx * dx + dy * dy;
      if (e >= maxD) { maxD = e; split = i; }
    }
    return [maxD, split];
  }
  function reparam(d, first, last, u, b) {
    var q1 = [mul(sub(b[1], b[0]), 3), mul(sub(b[2], b[1]), 3), mul(sub(b[3], b[2]), 3)];
    var q2 = [mul(sub(q1[1], q1[0]), 2), mul(sub(q1[2], q1[1]), 2)];
    var out = [];
    for (var i = 0; i < u.length; i++) {
      var t = u[i], mt = 1 - t, P = d[first + i], Q = bez(b, t);
      var Q1 = [mt * mt * q1[0][0] + 2 * mt * t * q1[1][0] + t * t * q1[2][0], mt * mt * q1[0][1] + 2 * mt * t * q1[1][1] + t * t * q1[2][1]];
      var Q2 = [mt * q2[0][0] + t * q2[1][0], mt * q2[0][1] + t * q2[1][1]];
      var num = (Q[0] - P[0]) * Q1[0] + (Q[1] - P[1]) * Q1[1];
      var den = Q1[0] * Q1[0] + Q1[1] * Q1[1] + (Q[0] - P[0]) * Q2[0] + (Q[1] - P[1]) * Q2[1];
      var nt = Math.abs(den) < 1e-12 ? t : t - num / den;
      out.push(Math.max(0, Math.min(1, nt)));
    }
    // monotonluk koru
    for (i = 1; i < out.length; i++) if (out[i] < out[i - 1]) out[i] = out[i - 1];
    out[0] = 0; out[out.length - 1] = 1;
    return out;
  }

  function maxChordDev(r) {
    var a = r[0], b = r[r.length - 1], v = sub(b, a), l = Math.hypot(v[0], v[1]), m = 0;
    for (var i = 1; i < r.length - 1; i++) {
      var dv = l < 1e-9 ? dist(r[i], a) : Math.abs((r[i][0] - a[0]) * v[1] - (r[i][1] - a[1]) * v[0]) / l;
      if (dv > m) m = dv;
    }
    return m;
  }

  function emitBeziers(list, segs, flatTol) {
    for (var i = 0; i < list.length; i++) {
      var b = list[i];
      var dev = Math.max(maxChordDev([b[0], b[1], b[3]]), maxChordDev([b[0], b[2], b[3]]));
      if (dev < flatTol) segs.push([0, b[3][0], b[3][1]]);
      else segs.push([1, b[1][0], b[1][1], b[2][0], b[2][1], b[3][0], b[3][1]]);
    }
  }

  // Merdiven (staircase) piksel sınırını, her düz koşunun orta noktasına indirger.
  // Yatık bir çizginin koşu orta noktaları ideal çizginin tam üstündedir.
  function stepKey(a, b) {
    var dx = b[0] - a[0], dy = b[1] - a[1];
    if (Math.abs(dx) + Math.abs(dy) !== 1 || (dx && dy)) return -1;
    return dx ? (dx > 0 ? 0 : 2) : (dy > 0 ? 1 : 3);
  }
  function runMidsOpen(q) {
    var k = q.length - 1, out = [q[0]], a = 0;
    while (a < k) {
      var key = stepKey(q[a], q[a + 1]), b = a + 1;
      if (key >= 0) while (b < k && stepKey(q[b], q[b + 1]) === key) b++;
      if (key >= 0) out.push([(q[a][0] + q[b][0]) / 2, (q[a][1] + q[b][1]) / 2]);
      a = b;
    }
    out.push(q[k]);
    return out;
  }
  function runMidsClosed(q) {
    var m = q.length, s0 = 0;
    for (var i = 0; i < m; i++) {
      if (stepKey(q[(i - 1 + m) % m], q[i]) !== stepKey(q[i], q[(i + 1) % m])) { s0 = i; break; }
    }
    var r = q.slice(s0).concat(q.slice(0, s0));
    r.push(r[0]);
    var mids = runMidsOpen(r);
    mids.shift(); mids.pop();
    return mids.length >= 3 ? mids : q;
  }

  function fitPiece(q, o, segs) {
    var k = q.length - 1;
    if (k <= 0) return;
    var end = q[k];
    if (k <= 2) { segs.push([0, end[0], end[1]]); return; }
    q = runMidsOpen(q); k = q.length - 1;
    var r = smoothOpen(q, o.passes);
    if (maxChordDev(r) <= o.lineTol) { segs.push([0, end[0], end[1]]); return; }
    if (k <= 2) { segs.push([1, r[1][0], r[1][1], r[1][0], r[1][1], end[0], end[1]]); return; }
    var j = Math.max(1, Math.min(Math.round(k / 4), o.tanSpan));
    var t1 = norm(sub(r[j], r[0])), t2 = norm(sub(r[k - j], r[k]));
    var list = [];
    fitCubic(r, 0, k, t1, t2, o.err2, list, 0);
    emitBeziers(list, segs, o.flatTol);
  }

  // En küçük kareler doğru uydurma (PCA)
  function fitLine(pts) {
    var n = pts.length, mx = 0, my = 0, i;
    for (i = 0; i < n; i++) { mx += pts[i][0]; my += pts[i][1]; }
    mx /= n; my /= n;
    var sxx = 0, sxy = 0, syy = 0;
    for (i = 0; i < n; i++) { var dx = pts[i][0] - mx, dy = pts[i][1] - my; sxx += dx * dx; sxy += dx * dy; syy += dy * dy; }
    var ang = 0.5 * Math.atan2(2 * sxy, sxx - syy);
    return { c: [mx, my], d: [Math.cos(ang), Math.sin(ang)] };
  }

  // Köşe keskinleştirme: anti-aliasing/büyütme yüzünden yuvarlanmış köşeyi,
  // iki yandaki kenar doğrularının kesişimine taşır.
  // Yuvarlanmış sivri köşeler iki ayrı köşe gibi algılanır: yakın çiftleri birleştir.
  function mergeCorners(corners, n, closed, s) {
    var res = corners.map(function (i) { return { i: i, w: 0 }; });
    var changed = true;
    while (changed && res.length > 1) {
      changed = false;
      for (var k = 0; k < res.length; k++) {
        var a = res[k], bIdx = k + 1;
        if (bIdx >= res.length) { if (!closed || res.length < 3) break; bIdx = 0; }
        var b = res[bIdx], bi = bIdx === 0 ? b.i + n : b.i;
        var gap = (bi + b.w) - (a.i - a.w);
        if (bi - a.i <= 2 * s && gap <= 3 * s) {
          var lo = a.i - a.w, hi = bi + b.w, mid = Math.round((lo + hi) / 2);
          var m = { i: closed ? ((mid % n) + n) % n : mid, w: Math.ceil((hi - lo) / 2) };
          if (bIdx === 0) { res.splice(k, 1); res[0] = m; res.sort(function (x, y) { return x.i - y.i; }); }
          else res.splice(k, 2, m);
          changed = true; break;
        }
      }
    }
    return res;
  }

  function refineCorners(P, cornerObjs, closed, s) {
    var corners = cornerObjs.map(function (c) { return c.i; });
    var n = P.length, nc = corners.length, out = P.slice(), trim = {};
    function at(i) { return closed ? P[((i % n) + n) % n] : P[i]; }
    for (var ci = 0; ci < nc; ci++) {
      var i = corners[ci];
      var prevB = nc > 1 || !closed ? (ci > 0 ? corners[ci - 1] : (closed ? corners[nc - 1] - n : 0)) : i - n;
      var nextB = nc > 1 || !closed ? (ci < nc - 1 ? corners[ci + 1] : (closed ? corners[0] + n : n - 1)) : i + n;
      var inner = Math.max(2, Math.round(s * 0.6)) + cornerObjs[ci].w, span = 3 * s + cornerObjs[ci].w;
      var aFrom = Math.max(i - span, Math.ceil((prevB + i) / 2)), aTo = i - inner;
      var bFrom = i + inner, bTo = Math.min(i + span, Math.floor((nextB + i) / 2));
      if (aTo - aFrom < 3 || bTo - bFrom < 3) continue;
      var A = [], B = [], k;
      for (k = aFrom; k <= aTo; k++) A.push(at(k));
      for (k = bFrom; k <= bTo; k++) B.push(at(k));
      var la = fitLine(A), lb = fitLine(B);
      var cr = la.d[0] * lb.d[1] - la.d[1] * lb.d[0];
      if (Math.abs(cr) < 0.35) continue; // neredeyse paralel (≈20°)
      var t = ((lb.c[0] - la.c[0]) * lb.d[1] - (lb.c[1] - la.c[1]) * lb.d[0]) / cr;
      var X = [la.c[0] + la.d[0] * t, la.c[1] + la.d[1] * t];
      if (dist(X, P[i]) > s * 1.6 + cornerObjs[ci].w) continue;
      out[i] = X;
      trim[i] = inner;
    }
    out.trim = trim;
    return out;
  }

  function fitChain(flat, closed, o) {
    var P = [];
    for (var i = 0; i < flat.length; i += 2) P.push([flat[i], flat[i + 1]]);
    var segs = [];
    if (closed) {
      P.pop();
      var corners = detectCorners(o.prePasses ? smoothClosed(P, o.prePasses) : P, true, o.cosT, o.cornerScale);
      if (corners.length) {
        var co = mergeCorners(corners, P.length, true, o.cornerScale);
        corners = co.map(function (c) { return c.i; });
        P = refineCorners(P, co, true, o.cornerScale);
      }
      if (!corners.length) {
        var Q = runMidsClosed(P), n = Q.length, r = smoothClosed(Q, o.passes);
        r.push(r[0]);
        var t = norm(sub(r[1], r[n - 1]));
        var list = [];
        if (n < 4) { for (i = 1; i <= n; i++) segs.push([0, r[i][0], r[i][1]]); return { sx: r[0][0], sy: r[0][1], segs: segs }; }
        fitCubic(r, 0, n, t, mul(t, -1), o.err2, list, 0);
        emitBeziers(list, segs, o.flatTol);
        return { sx: r[0][0], sy: r[0][1], segs: segs };
      }
      var c0 = corners[0], trimC = P.trim || {}, L0 = P.length;
      P = P.slice(c0).concat(P.slice(0, c0));
      P.push(P[0]);
      P.trim = {};
      for (var tk in trimC) { var ni = (+tk - c0 + L0) % L0; P.trim[ni] = trimC[tk]; if (ni === 0) P.trim[L0] = trimC[tk]; }
      corners = corners.map(function (c) { return (c - c0 + P.length - 1) % (P.length - 1); });
      corners.shift();
    } else {
      corners = detectCorners(o.prePasses ? smoothOpen(P, o.prePasses) : P, false, o.cosT, o.cornerScale);
      if (corners.length) {
        var co2 = mergeCorners(corners, P.length, false, o.cornerScale).filter(function (c) { return c.i > 0 && c.i < P.length - 1; });
        corners = co2.map(function (c) { return c.i; });
        P = refineCorners(P, co2, false, o.cornerScale);
      }
    }
    var br = [0].concat(corners, [P.length - 1]), trim = P.trim || {};
    for (i = 0; i + 1 < br.length; i++) {
      var a = br[i], b = br[i + 1], piece = P.slice(a, b + 1);
      var ta = trim[a] || 0, tb = trim[b] || 0;
      if (ta + tb > 0 && piece.length - ta - tb >= 4) {
        piece = [piece[0]].concat(piece.slice(1 + ta, piece.length - 1 - tb), [piece[piece.length - 1]]);
      }
      fitPiece(piece, o, segs);
    }
    return { sx: P[0][0], sy: P[0][1], segs: segs };
  }

  function reverseFit(f) {
    var starts = [[f.sx, f.sy]], segs = f.segs, i;
    for (i = 0; i < segs.length; i++) { var s = segs[i]; starts.push(s[0] ? [s[5], s[6]] : [s[1], s[2]]); }
    var out = [];
    for (i = segs.length - 1; i >= 0; i--) {
      s = segs[i]; var p = starts[i];
      if (s[0]) out.push([1, s[3], s[4], s[1], s[2], p[0], p[1]]); else out.push([0, p[0], p[1]]);
    }
    var last = starts[starts.length - 1];
    return { sx: last[0], sy: last[1], segs: out };
  }

  // ------------------------------------------------------------ ana işlem
  function vectorize(img, options, progress) {
    var o = {}, k;
    for (k in DEFAULTS) o[k] = DEFAULTS[k];
    if (options && options.mode && PRESETS[options.mode]) for (k in PRESETS[options.mode]) o[k] = PRESETS[options.mode][k];
    if (options) for (k in options) if (options[k] !== undefined && options[k] !== null) o[k] = options[k];
    if (options && options.palette) o.palette = options.palette;
    var report = progress || function () {};
    var t0 = Date.now();

    var w0 = img.width, h0 = img.height, data = img.data;
    if (o.denoise) { report('Gürültü azaltılıyor', 5); data = bilateral(data, w0, h0, 2, 22); }

    // ölçek
    var data0 = data, f = 1, maxDim = Math.max(w0, h0);
    if (o.upscale && maxDim < 900) f = Math.min(4, Math.max(2, Math.floor(1800 / maxDim)));
    while (f > 1 && w0 * h0 * f * f > o.maxPixels) f--;
    if (w0 * h0 > o.maxPixels) f = Math.sqrt(o.maxPixels / (w0 * h0));
    var w = Math.max(1, Math.round(w0 * f)), h = Math.max(1, Math.round(h0 * f));
    if (w !== w0 || h !== h0) { report('Görüntü yeniden örnekleniyor', 10); data = resample(data, w0, h0, w, h); }
    f = w / w0;
    var n = w * h;

    // Lab
    report('Renkler analiz ediliyor', 15);
    var lab = new Float32Array(n * 3), opaque = new Uint8Array(n), nOpaque = 0;
    var tmp = [0, 0, 0];
    for (var p = 0; p < n; p++) {
      if (data[p * 4 + 3] >= o.alphaThreshold) { opaque[p] = 1; nOpaque++; }
      rgbToLab(data[p * 4], data[p * 4 + 1], data[p * 4 + 2], tmp, 0);
      lab[p * 3] = tmp[0]; lab[p * 3 + 1] = tmp[1]; lab[p * 3 + 2] = tmp[2];
    }

    // düzlük haritası (kenar olmayan pikseller)
    var flatT = Math.max(2.5, 9 / f), flatT2 = flatT * flatT, flat = new Uint8Array(n), nFlat = 0;
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
      p = y * w + x; if (!opaque[p]) continue;
      var m = 0, q;
      if (x > 0) { q = p - 1; m = Math.max(m, opaque[q] ? dist2(lab, p * 3, lab, q * 3) : 1e9); }
      if (x < w - 1) { q = p + 1; m = Math.max(m, opaque[q] ? dist2(lab, p * 3, lab, q * 3) : 1e9); }
      if (y > 0) { q = p - w; m = Math.max(m, opaque[q] ? dist2(lab, p * 3, lab, q * 3) : 1e9); }
      if (y < h - 1) { q = p + w; m = Math.max(m, opaque[q] ? dist2(lab, p * 3, lab, q * 3) : 1e9); }
      if (m < flatT2) { flat[p] = 1; nFlat++; }
    }

    // örnekler
    var rng = mulberry32(12345), useFlat = nFlat >= Math.max(500, nOpaque * 0.15) && o.mode !== 'photo';
    var pool = useFlat ? nFlat : nOpaque, MAXS = 60000, step = Math.max(1, pool / MAXS);
    var S = [], cnt = 0, nextPick = 0;
    for (p = 0; p < n; p++) {
      if (!opaque[p] || (useFlat && !flat[p])) continue;
      if (cnt >= nextPick) { S.push(lab[p * 3], lab[p * 3 + 1], lab[p * 3 + 2]); nextPick += step * (0.5 + rng()); }
      cnt++;
    }
    S = Float64Array.from(S);
    var N = S.length / 3;

    // palet
    report('Palet oluşturuluyor', 25);
    var centers, K, fixedRGB = null, bwThr = -1;
    if (o.palette && o.palette.length) {
      fixedRGB = o.palette.map(function (c) { return [c[0], c[1], c[2]]; });
      K = fixedRGB.length; centers = new Float64Array(K * 3);
      fixedRGB.forEach(function (c, i) { rgbToLab(c[0] | 0, c[1] | 0, c[2] | 0, centers, i * 3); });
    } else if (o.mode === 'bw') {
      var Ls = new Float64Array(N); for (var i = 0; i < N; i++) Ls[i] = S[i * 3];
      bwThr = o.bwThreshold >= 0 ? o.bwThreshold : otsu(Ls, N);
      K = 2; centers = Float64Array.from([0, 0, 0, 100, 0, 0]);
      fixedRGB = [[0, 0, 0], [255, 255, 255]];
    } else if (N === 0) {
      K = 1; centers = Float64Array.from([100, 0, 0]);
    } else if (o.colors > 0) {
      K = Math.min(o.colors, N);
      centers = kmeansPP(S, N, K, rng);
      lloyd(S, N, centers, K, 25);
    } else {
      centers = autoPalette(S, N, o.colorSensitivity, 48);
      K = centers.length / 3;
    }

    // sınıflandırma
    report('Pikseller sınıflandırılıyor', 35);
    var TR = K; // şeffaf sınıf
    var cls = new Int32Array(n), cache = new Map();
    for (p = 0; p < n; p++) {
      if (!opaque[p]) { cls[p] = TR; continue; }
      if (bwThr >= 0) { cls[p] = lab[p * 3] > bwThr ? 1 : 0; continue; }
      var key = (data[p * 4] << 16) | (data[p * 4 + 1] << 8) | data[p * 4 + 2], c = cache.get(key);
      if (c === undefined) {
        var bd = Infinity; c = 0;
        for (var j = 0; j < K; j++) { var dd = dist2(lab, p * 3, centers, j * 3); if (dd < bd) { bd = dd; c = j; } }
        cache.set(key, c);
      }
      cls[p] = c;
    }

    // sınıf renkleri (atanmış piksellerin ortalaması – orijinale sadık)
    var palRGB = [];
    if (fixedRGB) palRGB = fixedRGB;
    else {
      var acc = new Float64Array(K * 4);
      for (p = 0; p < n; p++) {
        if (cls[p] === TR || !flat[p] && useFlat) continue;
        c = cls[p]; acc[c * 4] += LIN[data[p * 4]]; acc[c * 4 + 1] += LIN[data[p * 4 + 1]]; acc[c * 4 + 2] += LIN[data[p * 4 + 2]]; acc[c * 4 + 3]++;
      }
      for (c = 0; c < K; c++) {
        if (acc[c * 4 + 3] > 0) palRGB.push([Math.round(linToSrgb(acc[c * 4] / acc[c * 4 + 3])), Math.round(linToSrgb(acc[c * 4 + 1] / acc[c * 4 + 3])), Math.round(linToSrgb(acc[c * 4 + 2] / acc[c * 4 + 3]))]);
        else palRGB.push(labToRgb(centers[c * 3], centers[c * 3 + 1], centers[c * 3 + 2]));
      }
    }

    // ince çizgi / küçük yazı koruması
    if (o.thinLines && o.mode !== 'photo' && K >= 2) {
      report('İnce detaylar korunuyor', 40);
      keepRidges(cls, data, w, h, data0, w0, h0, K, palRGB);
    }

    // anti-aliasing karışım düzeltmesi
    if (o.blendFix && K >= 3 && bwThr < 0) {
      report('Kenar karışımları düzeltiliyor', 42);
      fixBlends(cls, data, flat, lab, w, h, K, palRGB, Math.max(1, Math.round(f)));
    }

    // lekeler
    report('Küçük lekeler temizleniyor', 50);
    var R = removeSpeckles(cls, w, h, Math.max(1, Math.round(o.minArea * f * f)));

    // grafik
    report('Sınırlar çıkarılıyor', 60);
    var G = buildGraph(R.comp, w, h);

    report('Eğriler uyduruluyor', 70);
    var fo = {
      passes: Math.max(0, Math.round(o.smoothing * Math.max(1, f * 0.75))),
      prePasses: Math.round(Math.max(1, f * f * 0.75)),
      err2: Math.pow(Math.max(0.2, o.tolerance * f), 2),
      lineTol: Math.max(0.3, 0.45 * f),
      cosT: Math.cos(o.cornerAngle * Math.PI / 180),
      cornerScale: Math.max(4, Math.round(2 * f)),
      tanSpan: Math.max(2, Math.round(f)),
      flatTol: 0.04 * Math.max(1, f),
    };
    var fits = G.chains.map(function (ch) { return fitChain(ch.pts, ch.closed, fo); });

    report('Şekiller birleştiriliyor', 90);
    var loops = buildLoops(G, R.cls, TR);
    var sx = w0 / w, sy = h0 / h;
    var layers = [];
    for (c = 0; c < K; c++) layers.push({ index: c, color: palRGB[c], area: 0, paths: [] });
    for (i = 0; i < R.count; i++) if (R.cls[i] !== TR) layers[R.cls[i]].area += R.area[i];
    var nodes = 0;
    loops.forEach(function (lp) {
      var arr = [];
      lp.hes.forEach(function (he, idx) {
        var fit = (he & 1) ? reverseFit(fits[he >> 1]) : fits[he >> 1];
        if (idx === 0) arr.push(0, fit.sx * sx, fit.sy * sy);
        fit.segs.forEach(function (s) {
          nodes++;
          if (s[0]) arr.push(2, s[1] * sx, s[2] * sy, s[3] * sx, s[4] * sy, s[5] * sx, s[6] * sy);
          else arr.push(1, s[1] * sx, s[2] * sy);
        });
      });
      layers[lp.cls].paths.push(arr);
    });
    layers = layers.filter(function (l) { return l.paths.length; });
    layers.sort(function (a, b) { return b.area - a.area; });

    report('Tamamlandı', 100);
    return {
      width: w0, height: h0,
      layers: layers,
      stats: { colors: layers.length, shapes: loops.length, nodes: nodes, scale: f, time: Date.now() - t0, workW: w, workH: h },
    };
  }

  // İnce çizgi / küçük yazı koruması.
  // Orijinal çözünürlükte, komşularına göre belirgin şekilde başka bir renge doğru
  // "tepe" yapan pikselleri (1 px'lik çizgiler, küçük yazı) bul. Basit %50 eşiği
  // bu detayları yok ederdi. Sonra bu işareti büyütülmüş sınıf haritasına aktar.
  function keepRidges(cls, data, w, h, data0, w0, h0, K, palRGB) {
    var plab = new Float64Array(K * 3), tmp = [0, 0, 0];
    palRGB.forEach(function (c, i) { rgbToLab(c[0], c[1], c[2], plab, i * 3); });
    var n0 = w0 * h0, near = new Int16Array(n0), x, y, p, c, k;
    for (p = 0; p < n0; p++) {
      if (data0[p * 4 + 3] < 128) { near[p] = -1; continue; }
      rgbToLab(data0[p * 4], data0[p * 4 + 1], data0[p * 4 + 2], tmp, 0);
      var bd = Infinity, bc = 0;
      for (c = 0; c < K; c++) { var d = dist2(tmp, 0, plab, c * 3); if (d < bd) { bd = d; bc = c; } }
      near[p] = bc;
    }
    function proj(D, q, A, vx, vy, vz, vv) {
      return ((D[q * 4] - A[0]) * vx + (D[q * 4 + 1] - A[1]) * vy + (D[q * 4 + 2] - A[2]) * vz) / vv;
    }
    function solidNb(q, c) {
      if (near[q] !== c) return false;
      var qx = q % w0, qy = (q - qx) / w0, m = 0;
      if (qx > 0 && near[q - 1] === c) m++;
      if (qx < w0 - 1 && near[q + 1] === c) m++;
      if (qy > 0 && near[q - w0] === c) m++;
      if (qy < h0 - 1 && near[q + w0] === c) m++;
      return m >= 3;
    }
    var offs = [[1, 0], [0, 1], [1, 1], [1, -1]], mask = new Int16Array(n0), any = false;
    for (y = 1; y < h0 - 1; y++) for (x = 1; x < w0 - 1; x++) {
      p = y * w0 + x;
      var c0 = near[p]; if (c0 < 0) continue;
      var pr = data0[p * 4], pg = data0[p * 4 + 1], pb = data0[p * 4 + 2], bestC = -1, bestT = 0;
      for (c = 0; c < K; c++) {
        if (c === c0) continue;
        var A = palRGB[c0], B = palRGB[c];
        var vx = B[0] - A[0], vy = B[1] - A[1], vz = B[2] - A[2], vv = vx * vx + vy * vy + vz * vz;
        if (vv < 1600) continue;
        var tp = proj(data0, p, A, vx, vy, vz, vv);
        if (tp < 0.22 || tp >= 0.5 || tp <= bestT) continue;
        var ex = pr - (A[0] + tp * vx), ey = pg - (A[1] + tp * vy), ez = pb - (A[2] + tp * vz);
        if (ex * ex + ey * ey + ez * ez > 0.02 * vv + 300) continue; // gerçekten c0–c karışımı olmalı
        // bir komşusu neredeyse tamamen c ise bu bir şeklin kenarıdır, ince çizgi değil
        var edgeNb = false;
        for (var ny = -1; ny <= 1 && !edgeNb; ny++) for (var nx = -1; nx <= 1; nx++) {
          if ((nx || ny) && proj(data0, p + ny * w0 + nx, A, vx, vy, vz, vv) > 0.72) { edgeNb = true; break; }
        }
        if (edgeNb) continue;
        var drop = Math.max(0.12, tp * 0.45);
        for (k = 0; k < 4; k++) {
          var q1 = p - offs[k][1] * w0 - offs[k][0], q2 = p + offs[k][1] * w0 + offs[k][0];
          if (near[q1] !== c0 || near[q2] !== c0) continue;
          if (proj(data0, q1, A, vx, vy, vz, vv) < tp - drop && proj(data0, q2, A, vx, vy, vz, vv) < tp - drop) { bestC = c; bestT = tp; break; }
        }
      }
      // bir şeklin ucuna/kenarına bitişikse ekleme (köşeleri bozmasın)
      if (bestC >= 0 && !solidNb(p - 1, bestC) && !solidNb(p + 1, bestC) && !solidNb(p - w0, bestC) && !solidNb(p + w0, bestC)) { mask[p] = bestC + 1; any = true; }
    }
    if (!any) return;
    var sx = w0 / w, sy = h0 / h, f = w / w0;
    for (y = 0; y < h; y++) {
      var oy = Math.min(h0 - 1, Math.floor((y + 0.5) * sy));
      for (x = 0; x < w; x++) {
        var ox = Math.min(w0 - 1, Math.floor((x + 0.5) * sx)), m = mask[oy * w0 + ox];
        if (!m) continue;
        p = y * w + x; var c1 = m - 1, cc = cls[p];
        if (cc === c1 || cc >= K) continue;
        if (f <= 1) { cls[p] = c1; continue; }
        A = palRGB[cc]; B = palRGB[c1];
        vx = B[0] - A[0]; vy = B[1] - A[1]; vz = B[2] - A[2]; vv = vx * vx + vy * vy + vz * vz;
        if (vv > 0 && proj(data, p, A, vx, vy, vz, vv) >= 0.16) cls[p] = c1;
      }
    }
  }

  function fixBlends(cls, data, flat, lab, w, h, K, palRGB, r) {
    var src = cls.slice(), tmp = [0, 0, 0], plab = new Float64Array(K * 3), tol2 = 12 * 12;
    palRGB.forEach(function (c, i) { rgbToLab(c[0], c[1], c[2], plab, i * 3); });
    var near = new Int32Array(16);
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
      var p = y * w + x, c = src[p];
      if (flat[p] || c >= K) continue;
      var nn = 0;
      for (var dy = -r; dy <= r; dy++) {
        var yy = y + dy; if (yy < 0 || yy >= h) continue;
        for (var dx = -r; dx <= r; dx++) {
          var xx = x + dx; if (xx < 0 || xx >= w) continue;
          var q = src[yy * w + xx];
          if (q === c || q >= K) continue;
          var seen = false;
          for (var t = 0; t < nn; t++) if (near[t] === q) { seen = true; break; }
          if (!seen && nn < 16) near[nn++] = q;
        }
      }
      if (nn < 2) continue;
      var dc = dist2(lab, p * 3, plab, c * 3), best = -1, bestD = Math.min(tol2, dc + 36);
      var pr = data[p * 4], pg = data[p * 4 + 1], pb = data[p * 4 + 2];
      for (var a = 0; a < nn; a++) for (var b = a + 1; b < nn; b++) {
        var A = palRGB[near[a]], B = palRGB[near[b]];
        var vx = B[0] - A[0], vy = B[1] - A[1], vz = B[2] - A[2], vv = vx * vx + vy * vy + vz * vz;
        if (vv < 1) continue;
        var tt = ((pr - A[0]) * vx + (pg - A[1]) * vy + (pb - A[2]) * vz) / vv;
        if (tt < 0.04 || tt > 0.96) continue;
        rgbToLabF(A[0] + tt * vx, A[1] + tt * vy, A[2] + tt * vz, tmp, 0);
        var d = dist2(lab, p * 3, tmp, 0);
        if (d < bestD) { bestD = d; best = tt < 0.5 ? near[a] : near[b]; }
      }
      if (best >= 0) cls[p] = best;
    }
  }

  // ------------------------------------------------------------ 8. çıktılar
  function hex(c) { return '#' + c.map(function (v) { return ('0' + v.toString(16)).slice(-2); }).join(''); }
  function num(v, dp) { var m = Math.pow(10, dp), s = String(Math.round(v * m) / m); return s === '-0' ? '0' : s; }

  function pathToD(arr, dp) {
    var out = [], i = 0;
    while (i < arr.length) {
      var t = arr[i];
      if (t === 0) { if (out.length) out.push('Z'); out.push('M' + num(arr[i + 1], dp) + ' ' + num(arr[i + 2], dp)); i += 3; }
      else if (t === 1) { out.push('L' + num(arr[i + 1], dp) + ' ' + num(arr[i + 2], dp)); i += 3; }
      else { out.push('C' + num(arr[i + 1], dp) + ' ' + num(arr[i + 2], dp) + ' ' + num(arr[i + 3], dp) + ' ' + num(arr[i + 4], dp) + ' ' + num(arr[i + 5], dp) + ' ' + num(arr[i + 6], dp)); i += 7; }
    }
    out.push('Z');
    return out.join('');
  }

  function toSVG(res, opts) {
    opts = opts || {};
    var dp = opts.decimals == null ? 2 : opts.decimals, gap = opts.gapFill !== false;
    var sw = num(Math.max(res.width, res.height) / 1500 + 0.25, 3);
    var s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + res.width + ' ' + res.height + '" width="' + res.width + '" height="' + res.height + '">'];
    res.layers.forEach(function (l) {
      if (l.hidden) return;
      var col = hex(l.color), d = l.paths.map(function (p) { return pathToD(p, dp); }).join('');
      if (opts.outline) s.push('<path fill="none" stroke="' + (opts.outlineColor || '#e2187a') + '" stroke-width="1.2" vector-effect="non-scaling-stroke" d="' + d + '"/>');
      else s.push('<path fill="' + col + '" fill-rule="evenodd"' + (gap ? ' stroke="' + col + '" stroke-width="' + sw + '" stroke-linejoin="round"' : '') + ' d="' + d + '"/>');
    });
    s.push('</svg>');
    return s.join('\n');
  }

  function eachCmd(arr, H, cb) {
    var i = 0;
    while (i < arr.length) {
      var t = arr[i];
      if (t === 0) { cb('M', [arr[i + 1], H - arr[i + 2]]); i += 3; }
      else if (t === 1) { cb('L', [arr[i + 1], H - arr[i + 2]]); i += 3; }
      else { cb('C', [arr[i + 1], H - arr[i + 2], arr[i + 3], H - arr[i + 4], arr[i + 5], H - arr[i + 6]]); i += 7; }
    }
  }

  function psBody(res, ops) {
    var out = [];
    res.layers.forEach(function (l) {
      if (l.hidden) return;
      out.push(l.color.map(function (v) { return num(v / 255, 4); }).join(' ') + ' ' + ops.color);
      l.paths.forEach(function (p) {
        var first = true;
        eachCmd(p, res.height, function (c, a) {
          var s = a.map(function (v) { return num(v, 2); }).join(' ');
          if (c === 'M') { if (!first) out.push(ops.close); out.push(s + ' ' + ops.move); first = false; }
          else if (c === 'L') out.push(s + ' ' + ops.line);
          else out.push(s + ' ' + ops.curve);
        });
        out.push(ops.close);
      });
      out.push(ops.fill);
    });
    return out.join('\n');
  }

  function toEPS(res) {
    return '%!PS-Adobe-3.0 EPSF-3.0\n%%BoundingBox: 0 0 ' + Math.ceil(res.width) + ' ' + Math.ceil(res.height) +
      '\n%%Creator: VektorSihirbazi\n%%EndComments\n' +
      psBody(res, { color: 'setrgbcolor newpath', move: 'moveto', line: 'lineto', curve: 'curveto', close: 'closepath', fill: 'eofill' }) +
      '\nshowpage\n%%EOF\n';
  }

  function toPDF(res) {
    var content = psBody(res, { color: 'rg', move: 'm', line: 'l', curve: 'c', close: 'h', fill: 'f*' });
    var objs = [
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ' + res.width + ' ' + res.height + '] /Contents 4 0 R /Resources << >> >>',
      '<< /Length ' + content.length + ' >>\nstream\n' + content + '\nendstream',
    ];
    var pdf = '%PDF-1.4\n', offs = [];
    objs.forEach(function (o, i) { offs.push(pdf.length); pdf += (i + 1) + ' 0 obj\n' + o + '\nendobj\n'; });
    var xref = pdf.length;
    pdf += 'xref\n0 ' + (objs.length + 1) + '\n0000000000 65535 f \n';
    offs.forEach(function (o) { pdf += ('000000000' + o).slice(-10) + ' 00000 n \n'; });
    pdf += 'trailer\n<< /Size ' + (objs.length + 1) + ' /Root 1 0 R >>\nstartxref\n' + xref + '\n%%EOF\n';
    return pdf;
  }

  var api = { vectorize: vectorize, toSVG: toSVG, toEPS: toEPS, toPDF: toPDF, DEFAULTS: DEFAULTS, PRESETS: PRESETS, hex: hex };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.Vectorizer = api;

  // Web Worker modu
  if (typeof WorkerGlobalScope !== 'undefined' && root instanceof WorkerGlobalScope) {
    root.onmessage = function (ev) {
      var m = ev.data;
      if (m.type !== 'run') return;
      try {
        var res = vectorize(m.image, m.options, function (msg, pct) { root.postMessage({ type: 'progress', id: m.id, msg: msg, pct: pct }); });
        root.postMessage({ type: 'done', id: m.id, result: res });
      } catch (e) {
        root.postMessage({ type: 'error', id: m.id, error: String(e && e.stack || e) });
      }
    };
  }
})(typeof self !== 'undefined' ? self : this);
