/* VektörSihirbazı – arayüz */
(function () {
  'use strict';
  var V = window.Vectorizer;
  var $ = function (id) { return document.getElementById(id); };

  var state = {
    img: null,          // {width, height, data}
    url: null,          // orijinal görsel URL'si
    name: 'vektor',
    result: null,       // son vektör sonucu
    mode: 'auto',
    view: 'split',
    split: 0.5,
    fixedPalette: null, // renk kaldırılınca sabit palet
    recolor: {},        // orijinal hex -> yeni hex
    z: { s: 1, x: 0, y: 0 },
    jobId: 0,
  };

  // ------------------------------------------------------------ worker
  var worker = null, workerOK = true;
  try {
    // Tek dosya sürümünde motor kaynağı sayfanın içinde: Blob işçisi (çift tıklayınca da çalışır)
    var inl = document.getElementById('vec-src');
    worker = inl ? new Worker(URL.createObjectURL(new Blob([inl.textContent], { type: 'text/javascript' })))
                 : new Worker('vectorizer.js');
    worker.onmessage = onWorkerMsg;
    worker.onerror = function (e) { e.preventDefault && e.preventDefault(); workerOK = false; worker = null; if (state.img) run(); };
  } catch (e) { workerOK = false; }

  function onWorkerMsg(ev) {
    var m = ev.data;
    if (m.id !== state.jobId) return;
    if (m.type === 'progress') progress(m.msg, m.pct);
    else if (m.type === 'done') done(m.result);
    else if (m.type === 'error') { busy(false); alert('Hata: ' + m.error); }
  }

  function options() {
    var auto = $('autoColors').checked;
    return {
      mode: state.mode,
      colors: state.mode === 'bw' ? 2 : (auto ? 0 : +$('colors').value),
      colorSensitivity: +$('sens').value,
      bwThreshold: +$('thr').value,
      minArea: +$('area').value,
      tolerance: +$('tol').value / 100,
      cornerAngle: +$('corn').value,
      smoothing: +$('sm').value,
      upscale: $('upscale').checked,
      thinLines: $('thin').checked,
      blendFix: $('blend').checked,
      denoise: $('denoise').checked,
      palette: state.fixedPalette,
    };
  }

  var debounceT = null;
  function schedule() { clearTimeout(debounceT); debounceT = setTimeout(run, 250); }

  function run() {
    if (!state.img) return;
    var id = ++state.jobId, opts = options();
    busy(true); progress('Başlıyor', 0);
    if (worker && workerOK) {
      worker.postMessage({ type: 'run', id: id, image: state.img, options: opts });
    } else {
      setTimeout(function () {
        if (id !== state.jobId) return;
        try {
          done(V.vectorize(state.img, opts, function () {}));
        } catch (e) { busy(false); alert('Hata: ' + e); }
      }, 30);
    }
  }

  function done(res) {
    state.result = res;
    busy(false);
    applyRecolor();
    render();
    renderPalette();
    var s = res.stats;
    $('stats').textContent = res.width + '×' + res.height + ' px · ' + s.colors + ' renk · ' + s.shapes + ' şekil · ' + s.nodes +
      ' düğüm · ' + (s.scale > 1 ? s.scale.toFixed(0) + '× alt-piksel · ' : '') + (s.time / 1000).toFixed(2) + ' sn';
    $('photoHint').hidden = !(state.mode === 'auto' && s.colors >= 40);
    ['dlSvg', 'dlPdf', 'dlEps', 'dlPng'].forEach(function (b) { $(b).disabled = false; });
  }

  function busy(on) { $('busy').classList.toggle('on', on); }
  function progress(msg, pct) { $('busyMsg').textContent = msg + '…'; $('busyBar').style.width = (pct || 0) + '%'; }

  // ------------------------------------------------------------ çizim
  function applyRecolor() {
    if (!state.result) return;
    state.result.layers.forEach(function (l) {
      if (!l.orig) l.orig = l.color.slice();
      var h = V.hex(l.orig), n = state.recolor[h];
      l.color = n ? hexToRgb(n) : l.orig.slice();
    });
  }
  function hexToRgb(h) { return [parseInt(h.substr(1, 2), 16), parseInt(h.substr(3, 2), 16), parseInt(h.substr(5, 2), 16)]; }

  function render() {
    var res = state.result, layer = $('vecLayer');
    if (!res) { layer.innerHTML = ''; return; }
    var outline = state.view === 'line';
    layer.innerHTML = V.toSVG(res, { gapFill: $('gap').checked, outline: outline });
    var svg = layer.firstElementChild;
    svg.setAttribute('width', state.img.width); svg.setAttribute('height', state.img.height);
    updateView();
  }

  function updateView() {
    var v = state.view, img = $('origImg'), layer = $('vecLayer');
    img.style.visibility = (v === 'vec') ? 'hidden' : 'visible';
    layer.style.visibility = (v === 'orig') ? 'hidden' : 'visible';
    var split = v === 'split' && state.result;
    $('divider').hidden = !split; $('lblL').hidden = !split; $('lblR').hidden = !split;
    applyTransform();
  }

  function applyTransform() {
    var z = state.z;
    $('stage').style.transform = 'translate(' + z.x + 'px,' + z.y + 'px) scale(' + z.s + ')';
    if (state.view === 'split' && state.result) {
      var vw = $('viewer').clientWidth, sx = state.split * vw;
      $('divider').style.left = (sx - 1) + 'px';
      var ix = (sx - z.x) / z.s;
      $('vecLayer').style.clipPath = 'inset(0 0 0 ' + Math.max(0, ix) + 'px)';
    } else {
      $('vecLayer').style.clipPath = 'none';
    }
  }

  function fit() {
    if (!state.img) return;
    var vw = $('viewer').clientWidth, vh = $('viewer').clientHeight - 56;
    var s = Math.min((vw - 32) / state.img.width, (vh - 32) / state.img.height);
    state.z.s = s;
    state.z.x = (vw - state.img.width * s) / 2;
    state.z.y = (vh - state.img.height * s) / 2 + 8;
    applyTransform();
  }
  function zoomAt(f, cx, cy) {
    var z = state.z, ns = Math.max(0.05, Math.min(64, z.s * f));
    z.x = cx - (cx - z.x) * ns / z.s; z.y = cy - (cy - z.y) * ns / z.s; z.s = ns;
    applyTransform();
  }

  // ------------------------------------------------------------ palet
  function renderPalette() {
    var pal = $('pal'); pal.innerHTML = '';
    if (!state.result) return;
    state.result.layers.forEach(function (l) {
      var hx = V.hex(l.color), sw = document.createElement('div');
      sw.className = 'sw'; sw.style.background = hx; sw.title = hx;
      var inp = document.createElement('input'); inp.type = 'color'; inp.value = hx;
      inp.addEventListener('input', function () {
        state.recolor[V.hex(l.orig)] = inp.value; sw.style.background = inp.value;
        applyRecolor(); render();
      });
      var x = document.createElement('span'); x.className = 'x'; x.textContent = '×'; x.title = 'Rengi kaldır';
      x.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        if (state.result.layers.length <= 1) return;
        var keep = state.result.layers.filter(function (o) { return o !== l; }).map(function (o) { return o.orig.slice(); });
        state.fixedPalette = keep;
        $('palReset').hidden = false;
        run();
      });
      sw.appendChild(inp); sw.appendChild(x); pal.appendChild(sw);
    });
  }
  $('palReset').addEventListener('click', function () {
    state.fixedPalette = null; state.recolor = {}; $('palReset').hidden = true; run();
  });

  // ------------------------------------------------------------ kontroller
  function setPreset(p) {
    state.mode = p;
    var P = V.PRESETS[p];
    document.querySelectorAll('#presets button').forEach(function (b) { b.classList.toggle('on', b.dataset.p === p); });
    $('autoColors').checked = P.colors === 0;
    if (P.colors) $('colors').value = P.colors;
    $('area').value = P.minArea; $('tol').value = Math.round(P.tolerance * 100);
    $('corn').value = P.cornerAngle; $('sm').value = P.smoothing;
    $('upscale').checked = P.upscale; $('denoise').checked = P.denoise;
    $('blend').checked = P.blendFix; $('thin').checked = p !== 'photo';
    state.fixedPalette = null; state.recolor = {}; $('palReset').hidden = true;
    syncLabels();
  }
  function syncLabels() {
    var bw = state.mode === 'bw', auto = $('autoColors').checked;
    $('autoColors').parentElement.hidden = bw;
    $('colorsRow').hidden = bw || auto;
    $('sensRow').hidden = bw || !auto;
    $('thrRow').hidden = !bw;
    $('colorsV').textContent = $('colors').value;
    $('sensV').textContent = $('sens').value + ' ΔE';
    $('thrV').textContent = +$('thr').value < 0 ? 'Otomatik' : $('thr').value;
    $('areaV').textContent = $('area').value + ' px²';
    $('tolV').textContent = (+$('tol').value / 100).toFixed(2) + ' px';
    $('cornV').textContent = $('corn').value + '°';
    $('smV').textContent = $('sm').value;
  }
  document.querySelectorAll('#presets button').forEach(function (b) {
    b.addEventListener('click', function () { setPreset(b.dataset.p); run(); });
  });
  ['colors', 'sens', 'thr', 'area', 'tol', 'corn', 'sm'].forEach(function (id) {
    $(id).addEventListener('input', function () { syncLabels(); schedule(); });
  });
  ['autoColors', 'upscale', 'thin', 'blend', 'denoise'].forEach(function (id) {
    $(id).addEventListener('change', function () { syncLabels(); if (id === 'autoColors') state.fixedPalette = null; schedule(); });
  });
  $('gap').addEventListener('change', render);
  document.querySelectorAll('#viewSeg button').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('#viewSeg button').forEach(function (o) { o.classList.toggle('on', o === b); });
      var prev = state.view; state.view = b.dataset.v;
      if (prev === 'line' || state.view === 'line') render(); else updateView();
    });
  });
  $('zIn').addEventListener('click', function () { var v = $('viewer'); zoomAt(1.5, v.clientWidth / 2, v.clientHeight / 2); });
  $('zOut').addEventListener('click', function () { var v = $('viewer'); zoomAt(1 / 1.5, v.clientWidth / 2, v.clientHeight / 2); });
  $('zFit').addEventListener('click', fit);
  window.addEventListener('resize', fit);

  // ------------------------------------------------------- kaydır / yakınlaştır
  var viewer = $('viewer'), pointers = new Map(), drag = null;
  viewer.addEventListener('wheel', function (e) {
    if (!state.img) return;
    e.preventDefault();
    var r = viewer.getBoundingClientRect();
    zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX - r.left, e.clientY - r.top);
  }, { passive: false });
  viewer.addEventListener('pointerdown', function (e) {
    if (!state.img || e.target.closest('.toolbar')) return;
    viewer.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    var r = viewer.getBoundingClientRect();
    if (e.target === $('divider')) drag = { type: 'split' };
    else if (pointers.size === 1) drag = { type: 'pan', x: e.clientX, y: e.clientY, zx: state.z.x, zy: state.z.y };
    if (pointers.size === 2) {
      var p = Array.from(pointers.values());
      drag = { type: 'pinch', d: Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y), cx: (p[0].x + p[1].x) / 2 - r.left, cy: (p[0].y + p[1].y) / 2 - r.top };
    }
  });
  viewer.addEventListener('pointermove', function (e) {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    var r = viewer.getBoundingClientRect();
    if (!drag) return;
    if (drag.type === 'split') {
      state.split = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)); applyTransform();
    } else if (drag.type === 'pan') {
      state.z.x = drag.zx + e.clientX - drag.x; state.z.y = drag.zy + e.clientY - drag.y; applyTransform();
    } else if (drag.type === 'pinch' && pointers.size === 2) {
      var p = Array.from(pointers.values()), d = Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y);
      zoomAt(d / drag.d, drag.cx, drag.cy); drag.d = d;
    }
  });
  function endPtr(e) { pointers.delete(e.pointerId); if (pointers.size === 0) drag = null; }
  viewer.addEventListener('pointerup', endPtr);
  viewer.addEventListener('pointercancel', endPtr);

  // ------------------------------------------------------------ yükleme
  var MAX_DIM = 4096;
  function loadFile(file) {
    if (!file || !/^image\//.test(file.type)) return;
    state.name = (file.name || 'vektor').replace(/\.[^.]+$/, '') || 'vektor';
    var url = URL.createObjectURL(file), im = new Image();
    im.onload = function () {
      var w = im.naturalWidth, h = im.naturalHeight, k = Math.min(1, MAX_DIM / Math.max(w, h));
      w = Math.max(1, Math.round(w * k)); h = Math.max(1, Math.round(h * k));
      var c = document.createElement('canvas'); c.width = w; c.height = h;
      var g = c.getContext('2d'); g.drawImage(im, 0, 0, w, h);
      var d = g.getImageData(0, 0, w, h);
      state.img = { width: w, height: h, data: d.data };
      if (state.url) URL.revokeObjectURL(state.url);
      state.url = url;
      var oi = $('origImg'); oi.src = url; oi.width = w; oi.height = h;
      $('drop').hidden = true; $('toolbar').hidden = false;
      state.result = null; state.fixedPalette = null; state.recolor = {}; $('palReset').hidden = true;
      $('vecLayer').innerHTML = ''; $('pal').innerHTML = '';
      fit(); updateView(); run();
    };
    im.onerror = function () { alert('Görsel açılamadı.'); };
    im.src = url;
  }
  $('openBtn').addEventListener('click', function () { $('file').click(); });
  $('drop').addEventListener('click', function () { $('file').click(); });
  $('file').addEventListener('change', function () { loadFile(this.files[0]); this.value = ''; });
  ['dragenter', 'dragover'].forEach(function (t) {
    document.addEventListener(t, function (e) { e.preventDefault(); $('drop').classList.add('hover'); });
  });
  document.addEventListener('dragleave', function () { $('drop').classList.remove('hover'); });
  document.addEventListener('drop', function (e) {
    e.preventDefault(); $('drop').classList.remove('hover');
    if (e.dataTransfer.files[0]) loadFile(e.dataTransfer.files[0]);
  });
  document.addEventListener('paste', function (e) {
    var items = (e.clipboardData || {}).items || [];
    for (var i = 0; i < items.length; i++) if (items[i].type.indexOf('image') === 0) { loadFile(items[i].getAsFile()); break; }
  });

  // ------------------------------------------------------------ indirme
  function save(blob, ext) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = state.name + '.' + ext;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
  }
  function svgText() { return V.toSVG(state.result, { gapFill: $('gap').checked }); }
  $('dlSvg').addEventListener('click', function () { save(new Blob([svgText()], { type: 'image/svg+xml' }), 'svg'); });
  $('dlPdf').addEventListener('click', function () { save(new Blob([V.toPDF(state.result)], { type: 'application/pdf' }), 'pdf'); });
  $('dlEps').addEventListener('click', function () { save(new Blob([V.toEPS(state.result)], { type: 'application/postscript' }), 'eps'); });
  $('dlPng').addEventListener('click', function () {
    var res = state.result, k = Math.min(4, 8000 / Math.max(res.width, res.height));
    var im = new Image();
    im.onload = function () {
      var c = document.createElement('canvas'); c.width = Math.round(res.width * k); c.height = Math.round(res.height * k);
      c.getContext('2d').drawImage(im, 0, 0, c.width, c.height);
      c.toBlob(function (b) { save(b, 'png'); }, 'image/png');
    };
    im.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgText());
  });

  syncLabels();
})();
