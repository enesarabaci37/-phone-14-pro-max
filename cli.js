#!/usr/bin/env node
/*
 * VektörSihirbazı komut satırı aracı (bağımlılık yok)
 *
 *   node cli.js logo.png                 -> logo.svg
 *   node cli.js logo.png -o cikti.pdf    -> PDF (uzantıya göre: .svg .pdf .eps)
 *   node cli.js logo.png --mode bw --colors 2 --tolerance 0.4
 *
 * Not: Komut satırında yalnızca PNG okunur. JPG vb. için tarayıcı arayüzünü
 * (index.html) kullanın veya görseli önce PNG'ye çevirin.
 */
'use strict';
var fs = require('fs'), path = require('path'), zlib = require('zlib');
var V = require('./vectorizer.js');

function decodePNG(buf) {
  var sig = [137, 80, 78, 71, 13, 10, 26, 10];
  for (var i = 0; i < 8; i++) if (buf[i] !== sig[i]) throw new Error('PNG dosyası değil');
  var pos = 8, w, h, depth, ctype, interlace, plte = null, trns = null, idat = [];
  while (pos < buf.length) {
    var len = buf.readUInt32BE(pos), type = buf.toString('ascii', pos + 4, pos + 8), d = buf.subarray(pos + 8, pos + 8 + len);
    if (type === 'IHDR') { w = d.readUInt32BE(0); h = d.readUInt32BE(4); depth = d[8]; ctype = d[9]; interlace = d[12]; }
    else if (type === 'PLTE') plte = d;
    else if (type === 'tRNS') trns = d;
    else if (type === 'IDAT') idat.push(d);
    else if (type === 'IEND') break;
    pos += 12 + len;
  }
  if (interlace) throw new Error('Geçmeli (interlaced) PNG desteklenmiyor');
  if (depth !== 8 && depth !== 16 && !(ctype === 3 && depth <= 8) && !(ctype === 0 && depth < 8)) throw new Error('Desteklenmeyen bit derinliği: ' + depth);
  var ch = { 0: 1, 2: 3, 3: 1, 4: 2, 6: 4 }[ctype];
  var raw = zlib.inflateSync(Buffer.concat(idat));
  var bpp = Math.max(1, (ch * depth) >> 3), stride = (w * ch * depth + 7) >> 3;
  var out = new Uint8ClampedArray(w * h * 4), prev = Buffer.alloc(stride), cur = Buffer.alloc(stride), p = 0;
  for (var y = 0; y < h; y++) {
    var ft = raw[p++];
    raw.copy(cur, 0, p, p + stride); p += stride;
    for (var x = 0; x < stride; x++) {
      var a = x >= bpp ? cur[x - bpp] : 0, b = prev[x], c = x >= bpp ? prev[x - bpp] : 0, v = cur[x];
      if (ft === 1) v += a; else if (ft === 2) v += b; else if (ft === 3) v += (a + b) >> 1;
      else if (ft === 4) { var pa = Math.abs(b - c), pb = Math.abs(a - c), pc = Math.abs(a + b - 2 * c); v += (pa <= pb && pa <= pc) ? a : (pb <= pc ? b : c); }
      cur[x] = v & 255;
    }
    for (x = 0; x < w; x++) {
      var o = (y * w + x) * 4, s;
      function sample(k) { // k. kanal, 8 bite indirilmiş
        if (depth === 16) return cur[(x * ch + k) * 2];
        if (depth === 8) return cur[x * ch + k];
        var bit = x * depth, byte = cur[bit >> 3], sh = 8 - depth - (bit & 7);
        return (byte >> sh) & ((1 << depth) - 1);
      }
      if (ctype === 3) {
        s = sample(0); out[o] = plte[s * 3]; out[o + 1] = plte[s * 3 + 1]; out[o + 2] = plte[s * 3 + 2];
        out[o + 3] = trns && s < trns.length ? trns[s] : 255;
      } else if (ctype === 0 || ctype === 4) {
        s = sample(0); if (depth < 8) s = Math.round(s * 255 / ((1 << depth) - 1));
        out[o] = out[o + 1] = out[o + 2] = s; out[o + 3] = ctype === 4 ? sample(1) : 255;
      } else {
        out[o] = sample(0); out[o + 1] = sample(1); out[o + 2] = sample(2); out[o + 3] = ctype === 6 ? sample(3) : 255;
      }
    }
    var t = prev; prev = cur; cur = t;
  }
  return { width: w, height: h, data: out };
}

function main(argv) {
  var args = { _: [] };
  for (var i = 0; i < argv.length; i++) {
    var a = argv[i];
    if (a === '-o' || a === '--out') args.out = argv[++i];
    else if (a.indexOf('--') === 0) {
      var k = a.slice(2), v = argv[i + 1];
      if (v === undefined || v.indexOf('--') === 0) args[k] = true; else { args[k] = isNaN(+v) ? v : +v; i++; }
    } else args._.push(a);
  }
  if (!args._.length || args.help) {
    console.log('Kullanım: node cli.js <girdi.png> [-o çıktı.svg|.pdf|.eps] [seçenekler]\n\n' +
      'Seçenekler:\n' +
      '  --mode auto|photo|bw    görsel türü (varsayılan auto = logo/çizim)\n' +
      '  --colors N              renk sayısı (0 = otomatik)\n' +
      '  --colorSensitivity N    otomatik palette renk ayırma (ΔE, varsayılan 14)\n' +
      '  --minArea N             leke temizleme alanı (px², varsayılan 4)\n' +
      '  --tolerance N           eğri toleransı (px, varsayılan 0.5)\n' +
      '  --cornerAngle N         köşe açısı eşiği (derece, varsayılan 130)\n' +
      '  --smoothing N           yumuşatma (varsayılan 3)\n' +
      '  --no-upscale --no-thinLines --no-blendFix --denoise --no-gapFill');
    return;
  }
  var input = args._[0], out = args.out || input.replace(/\.[^.]+$/, '') + '.svg';
  var opts = {};
  ['mode', 'colors', 'colorSensitivity', 'minArea', 'tolerance', 'cornerAngle', 'smoothing', 'denoise'].forEach(function (k) { if (args[k] !== undefined) opts[k] = args[k]; });
  ['upscale', 'thinLines', 'blendFix'].forEach(function (k) { if (args['no-' + k]) opts[k] = false; });
  var img = decodePNG(fs.readFileSync(input));
  var res = V.vectorize(img, opts, function (msg, pct) { process.stderr.write('\r' + ('   ' + pct).slice(-3) + '% ' + msg + '                '); });
  process.stderr.write('\n');
  var ext = path.extname(out).toLowerCase(), text;
  if (ext === '.pdf') text = V.toPDF(res);
  else if (ext === '.eps') text = V.toEPS(res);
  else text = V.toSVG(res, { gapFill: !args['no-gapFill'] });
  fs.writeFileSync(out, text, 'utf8');
  var s = res.stats;
  console.log(out + ' yazıldı · ' + s.colors + ' renk · ' + s.shapes + ' şekil · ' + s.nodes + ' düğüm · ' + (s.time / 1000).toFixed(2) + ' sn');
}

main(process.argv.slice(2));
