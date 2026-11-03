"""Haber videosu için telifsiz arka plan müziği üretir.

Tamamen kodla sentezlenir (hazır örnek/sample kullanılmaz), bu yüzden telif sorunu yoktur.
Hava uyarısı haberine uygun: gergin ama sakin bir pad, yumuşak bas vuruşu,
sahne geçişlerinde "whoosh" efektleri ve başta gök gürültüsü.

Kullanım: python3 muzik.py <cikti.wav> <sure_sn> <gecis1,gecis2,...> <simsek1,simsek2,...>
"""
import sys
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def one_pole_lowpass(x, cutoff):
    """Basit tek kutuplu alçak geçiren filtre (vektörel değil ama yeterince hızlı)."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def note_freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def pad(duration, t, chords, bar):
    out = np.zeros_like(t)
    for i, chord in enumerate(chords):
        start = i * bar
        if start >= duration:
            break
        seg = (t >= start) & (t < start + bar + 1.5)
        tt = t[seg] - start
        env = np.minimum(tt / 1.2, 1.0) * np.clip((bar + 1.5 - tt) / 1.5, 0, 1)
        sig = np.zeros_like(tt)
        for m in chord:
            f = note_freq(m)
            for det in (-0.12, 0.0, 0.12):  # hafif detune ile genişlik
                ff = f * 2 ** (det / 12)
                # birkaç harmonik, azalan genlikle -> yumuşak, "string pad" hissi
                for h, amp in ((1, 1.0), (2, 0.35), (3, 0.15), (4, 0.06)):
                    sig += amp * np.sin(2 * np.pi * ff * h * tt + rng.uniform(0, 6.28))
        out[seg] += sig * env
    return out / np.max(np.abs(out) + 1e-9)


def bass(duration, t, roots, bar, beat, start_at):
    out = np.zeros_like(t)
    n_beats = int(duration / beat) + 1
    for b in range(n_beats):
        st = b * beat
        if st < start_at or st >= duration - 1.0:
            continue
        root = roots[int(st // bar) % len(roots)]
        f = note_freq(root - 12)
        seg = (t >= st) & (t < st + beat)
        tt = t[seg] - st
        env = np.exp(-tt * 3.5) * np.minimum(tt / 0.01, 1)
        out[seg] += np.sin(2 * np.pi * f * tt) * env * (1.0 if b % 2 == 0 else 0.6)
    return out


def kick(duration, t, beat, start_at):
    out = np.zeros_like(t)
    n_beats = int(duration / beat) + 1
    for b in range(n_beats):
        st = b * beat
        if st < start_at or st >= duration - 1.0 or b % 2:
            continue
        seg = (t >= st) & (t < st + 0.5)
        tt = t[seg] - st
        freq = 45 + 75 * np.exp(-tt * 30)
        phase = 2 * np.pi * np.cumsum(freq) / SR
        out[seg] += np.sin(phase) * np.exp(-tt * 9)
    return out


def ticks(duration, t, beat, start_at):
    """Haber bülteni hissi veren hafif saat/tik sesi."""
    out = np.zeros_like(t)
    step = beat / 2
    n = int(duration / step) + 1
    for k in range(n):
        st = k * step
        if st < start_at or st >= duration - 1.0:
            continue
        seg = (t >= st) & (t < st + 0.05)
        tt = t[seg] - st
        out[seg] += np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 140) * (1.0 if k % 2 == 0 else 0.5)
    return out


def brown_noise(n):
    w = rng.standard_normal(n)
    b = np.cumsum(w)
    b -= one_pole_lowpass(b, 2.0)  # DC kaymasını temizle
    return b / (np.max(np.abs(b)) + 1e-9)


def whoosh(t, at, length=0.9):
    out = np.zeros_like(t)
    st = at - length * 0.6
    seg = (t >= st) & (t < st + length)
    tt = t[seg] - st
    n = brown_noise(len(tt))
    env = np.sin(np.pi * np.clip(tt / length, 0, 1)) ** 2
    out[seg] = n * env
    return out


def thunder(t, at):
    out = np.zeros_like(t)
    length = 3.5
    seg = (t >= at) & (t < at + length)
    tt = t[seg] - at
    n = brown_noise(len(tt))
    n = one_pole_lowpass(n, 180.0)
    n /= np.max(np.abs(n)) + 1e-9
    env = np.minimum(tt / 0.04, 1) * np.exp(-tt * 1.3) * (1 + 0.5 * np.sin(tt * 17))
    out[seg] = n * env
    return out


def main():
    path = sys.argv[1]
    duration = float(sys.argv[2])
    transitions = [float(x) for x in sys.argv[3].split(",") if x]
    flashes = [float(x) for x in sys.argv[4].split(",") if x]

    t = np.arange(int(duration * SR)) / SR
    bpm = 84
    beat = 60 / bpm
    bar = beat * 4

    # La minör: Am - F - C - G  (dramatik ama sakin)
    chords = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]
    roots = [45, 41, 48, 43]
    chords = chords * 8
    rhythm_start = 2.0

    mix = (
        0.32 * pad(duration, t, chords, bar)
        + 0.30 * bass(duration, t, roots, bar, beat, rhythm_start)
        + 0.42 * kick(duration, t, beat, rhythm_start)
        + 0.05 * ticks(duration, t, beat, rhythm_start)
    )
    for at in transitions:
        mix += 0.20 * whoosh(t, at)
    for at in flashes:
        mix += 0.55 * thunder(t, at)

    # genel giriş/çıkış fade
    fade_in = np.minimum(t / 0.8, 1)
    fade_out = np.clip((duration - t) / 2.5, 0, 1)
    mix *= fade_in * fade_out
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.9

    # hafif stereo genişlik: sağ kanala çok küçük gecikme
    d = int(0.012 * SR)
    left = mix
    right = np.concatenate([np.zeros(d), mix[:-d]])
    stereo = np.stack([left, right], axis=1)
    data = (stereo * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    main()
