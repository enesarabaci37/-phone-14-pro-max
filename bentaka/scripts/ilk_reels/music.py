#!/usr/bin/env python3
"""Bentaka ilk Reels için özgün müzik ve efektler (telifsiz, tamamen sentez).
120 BPM, La minör (Am–F–C–G). Çıktı: music.wav (48 kHz, stereo).
Kullanım: python3 music.py <çıktı.wav>
"""
import sys, wave
import numpy as np

import json, os
TL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timeline.json')))
SR, BPM, DUR = 48000, 120, TL['END']
BEAT = 60 / BPM
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i:i + len(sig)] += sig * gain * (1 + min(pan, 0))

def env(n, a=0.005, d=0.2, s=0.0, r=0.0, total=None):
    t = np.arange(n) / SR
    e = np.where(t < a, t / a, np.exp(-(t - a) / max(d, 1e-4)) * (1 - s) + s)
    if r and total:
        e *= np.clip((total - t) / r, 0, 1)
    return e

def lp(x, cut):
    # tek kutuplu alçak geçiren
    a = np.exp(-2 * np.pi * cut / SR); y = np.zeros_like(x); z = 0.0
    for k in range(len(x)):
        z = (1 - a) * x[k] + a * z; y[k] = z
    return y

def lp_fast(x, cut):
    # FFT ile yumuşak alçak geçiren (uzun sinyaller için)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cut) ** 4)
    return np.fft.irfft(X, len(x))

def hp_fast(x, cut):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (f / cut) ** 2 / np.sqrt(1 + (f / cut) ** 4)
    return np.fft.irfft(X, len(x))

def saw(freq, n, detune=0.0):
    t = np.arange(n) / SR
    ph = (t * freq * (1 + detune)) % 1.0
    return 2 * ph - 1

# --- davul sesleri ----------------------------------------------------------
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(1.6 * np.sin(ph) * np.exp(-t * 7.5))

def clap():
    n = int(0.35 * SR); t = np.arange(n) / SR
    no = hp_fast(rng.standard_normal(n), 900)
    e = np.exp(-t * 14) + 0.6 * np.exp(-((t - 0.012) % 0.011) * 300) * (t < 0.035)
    return no * e * 0.5

def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = np.arange(n) / SR
    no = hp_fast(rng.standard_normal(n), 7000)
    return no * np.exp(-t * (14 if open_ else 70)) * 0.5

def impact():
    n = int(2.2 * SR); t = np.arange(n) / SR
    f = 32 + 70 * np.exp(-t * 6)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    no = lp_fast(rng.standard_normal(n), 2500) * np.exp(-t * 4) * 0.5
    return np.tanh(1.4 * (sub + no))

def whoosh(d=0.55):
    n = int(d * SR); t = np.arange(n) / SR
    no = rng.standard_normal(n)
    out = np.zeros(n); seg = 1024
    for k in range(0, n, seg):
        p = k / n; cut = 300 + 7000 * p ** 2
        out[k:k + seg] = lp_fast(no[k:k + seg] if k + seg <= n else no[k:], cut)
    e = (t / d) ** 2 * np.clip((d - t) / 0.06, 0, 1)
    return out * e * 0.9

def riser(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    f = 200 * 2 ** (t / d * 3)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    no = hp_fast(rng.standard_normal(n), 2000) * 0.35
    return (tone + no) * (t / d) ** 2

def tick():
    n = int(0.03 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 180) * 0.35

# --- armoni -----------------------------------------------------------------
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
CHORDS = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]  # Am F C G
BAR = 4 * BEAT

def bass_note(m, n):
    s = saw(NOTE(m), n) * 0.6 + np.sin(2 * np.pi * NOTE(m - 12) * np.arange(n) / SR) * 0.7
    return lp(s, 600) * env(n, 0.004, 0.18, 0.35, 0.03, n / SR)

def pad_chord(notes, n):
    l = sum(saw(NOTE(m), n, -0.004) for m in notes); r = sum(saw(NOTE(m), n, 0.004) for m in notes)
    e = np.clip(np.arange(n) / (0.25 * SR), 0, 1) * np.clip((n - np.arange(n)) / (0.25 * SR), 0, 1)
    return lp_fast(l, 1400) * e * 0.08, lp_fast(r, 1400) * e * 0.08

def arp(notes, n_bar):
    out = np.zeros(n_bar); step = int(BEAT / 4 * SR)
    seq = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 24]
    for k in range(16):
        m = seq[k % 4]; n = step
        t = np.arange(n) / SR
        s = (saw(NOTE(m), n) * 0.5 + np.sin(2 * np.pi * NOTE(m) * t)) * np.exp(-t * 18)
        out[k * step:k * step + n] += s[: len(out) - k * step]
    return lp_fast(out, 3200) * 0.12

# Bölümler: (başlangıç, bitiş, davul, arp)
def section(t):
    for end, name in TL['sections']:
        if t < end: return name
    return 'outro'

K, C, HC, HO = kick(), clap(), hat(), hat(True)
nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    t0 = b * BAR
    root, notes = CHORDS[b % 4]
    sec = section(t0 + 0.01)
    nb = int(BAR * SR)
    # pad
    pl, pr = pad_chord(notes, nb)
    g = 0.6 if sec == 'outro' else 1.0
    add(pl, t0, g, 0.6); add(pr, t0, g, -0.6)
    if sec == 'outro':
        continue
    # bas (sekizlik, pompalanan)
    for k in range(8):
        tt = t0 + k * BEAT / 2
        if sec == 'tension' and k % 2: continue
        add(bass_note(root, int(BEAT / 2 * SR)), tt, 0.55)
    if sec in ('full', 'build'):
        add(arp(notes, nb), t0, 1.0 if sec == 'full' else 0.7, 0.25)
    for k in range(4):
        tb = t0 + k * BEAT
        if sec == 'full':
            add(K, tb, 0.9)
            if k in (1, 3): add(C, tb, 0.55, 0.1)
            add(HC, tb + BEAT / 2, 0.35, -0.3); add(HC, tb, 0.18, -0.3)
            if k == 3: add(HO, tb + BEAT / 2, 0.22, -0.3)
        elif sec == 'build':
            if k in (0, 2): add(K, tb, 0.75)
            add(HC, tb + BEAT / 2, 0.3, -0.3)
        elif sec == 'tension':
            add(HC, tb + BEAT / 2, 0.25, -0.3)

# sidechain: kick'lerde pad/bas hafif çekilsin
duck = np.ones(N)
for b in range(nbars):
    if section(b * BAR + 0.01) not in ('full', 'build'): continue
    for k in range(4):
        i = int((b * BAR + k * BEAT) * SR); n = int(0.22 * SR)
        if i >= N: break
        seg = 1 - 0.35 * np.exp(-np.arange(n) / SR * 14)
        duck[i:i + n] = np.minimum(duck[i:i + n], seg[: N - i])
L *= duck; R *= duck

# --- efektler (görüntüye senkron) -------------------------------------------
for c in TL['cuts']:
    w = whoosh(); add(w, c - len(w) / SR + 0.05, 0.5, 0.3); add(w, c - len(w) / SR + 0.05, 0.5, -0.3)
for c in TL['impacts']:
    add(impact(), c, 0.75)
for t0, d in TL['risers']: add(riser(d), t0, 0.8)
for k in range(24):  # Türkiye sayacı (30,2 – 32,8 sn)
    add(tick(), TL['tr_ticks'][0] + k * TL['tr_ticks'][1] / 24, 0.6 * (1 - k / 30))
for k in range(10):  # iş günü kutuları (38,4 – 39,8 sn)
    add(tick(), TL['day_ticks'][0] + k * TL['day_ticks'][1] / 10, 0.4)

# ana çıkış: yumuşak kırpma, giriş/çıkış
mix = np.stack([L, R], 1)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
fade = np.ones(N); fo = int(2.5 * SR); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= fade[:, None] * 0.89
out = sys.argv[1] if len(sys.argv) > 1 else 'music.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('yazıldı:', out)
