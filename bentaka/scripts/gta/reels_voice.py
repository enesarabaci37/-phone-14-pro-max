#!/usr/bin/env python3
"""Seslendirmeye göre zamanlanmış GTA 6 Reels'i: HTML + ses (voice.wav) + seslendirme metni."""
import json, os, wave
import numpy as np
from gta import HEAD, WATERMARK, scene_svg, mono, H, MAXH, tr_num, tr_hourly, TR_DAYS

HERE = os.path.dirname(os.path.abspath(__file__))
TTS = os.path.abspath(os.path.join(HERE, '..', '..', 'tts', 'seg'))
d = json.load(open(os.path.join(TTS, 'durations.json')))
DUR, TXT = d['dur'], d['text']

# --- Zaman çizelgesi (saniye) ---------------------------------------------
order = [('A', 0.30), ('B', 0.35), ('C', 0.25), ('D', 0.25), ('E1', 0.30), ('E2', 0.20), ('F1', 0.60), ('F2', 0.15), ('G', 0.35)]
T, t = {}, 0.0
for k, gap in order:
    t += gap
    T[k] = (round(t, 3), round(t + DUR[k], 3))
    t += DUR[k]
TOTAL = round(T['G'][1] + 1.2, 2)
s = lambda k: T[k][0]
e = lambda k: T[k][1]

def bar_row(label, hours, detail, accent, t0, out, dur):
    w = hours / MAXH * 936
    color = '#C6FF3D' if accent else '#8A93A6'
    return (f'<div data-in="{t0}" data-out="{out}" style="display:flex;flex-direction:column;gap:14px;opacity:0">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline"><span class="sora" style="font-weight:600;font-size:52px">{label}</span>'
            f'<span class="sora" style="font-weight:700;font-size:68px;color:{"#C6FF3D" if accent else "#F3F5F8"}"><span data-count="{hours:.4f}" data-cs="{t0 + 0.1}" data-cd="{dur}">0,0</span> saat</span></div>'
            f'<div style="height:34px;border-radius:17px;background:#1A1F2B;overflow:hidden"><div data-bar="{w:.1f}" data-bs="{t0 + 0.1}" data-bd="{dur}" style="width:0;height:100%;border-radius:17px;background:{color}"></div></div>'
            f'<span class="mono c" style="font-size:24px;letter-spacing:.06em">{detail}</span></div>')

S1_OUT = round(s('B') - 0.15, 2)
S2_OUT = round(e('E2') + 0.4, 2)
S5_IN = round(s('F1') - 0.05, 2)
S5_OUT = round(s('G') - 0.1, 2)

HTML = HEAD + f'''<div class="root" style="width:1080px;height:1920px">
{WATERMARK.format(b=420)}
<div data-in="0" data-out="{S5_OUT}" style="position:absolute;left:72px;top:250px;display:flex;align-items:center;gap:18px;opacity:0"><span class="chip">OYUN</span><span class="mono c" style="font-size:24px">GTA 6 · 19 KASIM 2026</span></div>

<div data-in="0.05" data-out="{S1_OUT}" style="position:absolute;left:72px;top:340px;border-radius:40px;overflow:hidden;opacity:0">{scene_svg(936, 618)}</div>
<div style="position:absolute;left:72px;right:72px;top:1010px;display:flex;flex-direction:column;gap:22px">
<span data-in="0.25" data-out="{S1_OUT}" class="sora c" style="font-weight:700;font-size:72px;letter-spacing:-.03em;opacity:0">GTA 6 nihayet çıktı.</span>
<span data-in="{round(s('A') + 1.9, 2)}" data-out="{S1_OUT}" class="sora" style="font-weight:700;font-size:84px;line-height:1.04;letter-spacing:-.035em;opacity:0">Peki onu almak için <span class="v">kaç saat</span> çalışman gerekiyor?</span></div>

<div style="position:absolute;left:72px;right:72px;top:360px;display:flex;flex-direction:column;gap:40px">
<div data-in="{s('B')}" data-out="{S2_OUT}" style="display:flex;flex-direction:column;gap:18px;opacity:0"><span class="mono v" style="font-size:26px">ASGARİ ÜCRETLE HESAPLADIK</span>
<span class="sora" style="font-weight:700;font-size:76px;line-height:1.05;letter-spacing:-.03em">Bir oyun kaç saatlik emek?</span></div>
{bar_row('Almanya', H['de'], '13,90 € / SAAT · OYUN 79,99 €', False, s('C'), S2_OUT, 1.2)}
{bar_row('ABD', H['us'], '7,25 $ / SAAT · OYUN 79,99 $', False, s('D'), S2_OUT, 1.2)}
{bar_row('Türkiye', H['tr'], f'{tr_num(tr_hourly, 2)} TL / SAAT · OYUN 3.999 TL', True, s('E1'), S2_OUT, 1.8)}
<div data-in="{s('E2')}" data-out="{S2_OUT}" class="sora" style="font-weight:700;font-size:58px;line-height:1.1;letter-spacing:-.03em;opacity:0">Yani <span class="v">3,5 iş gününden fazla.</span></div>
</div>

<div data-in="{S5_IN}" data-out="{S5_OUT}" style="position:absolute;left:72px;top:340px;border-radius:40px;overflow:hidden;opacity:0">{scene_svg(936, 618)}</div>
<div style="position:absolute;left:72px;right:72px;top:1010px;display:flex;flex-direction:column;gap:26px">
<span data-in="{S5_IN}" data-out="{S5_OUT}" class="sora" style="font-weight:700;font-size:100px;line-height:1.02;letter-spacing:-.035em;opacity:0">Sence bu fiyata <span class="v">değer mi?</span></span>
<span data-in="{s('F2')}" data-out="{S5_OUT}" class="c" style="font-size:40px;line-height:1.4;opacity:0">Cevabını yorumlara yaz, oyun seven arkadaşına gönder.</span></div>

<div data-in="0" data-out="{S5_OUT}" style="position:absolute;left:72px;top:1460px;display:flex;align-items:center;gap:14px;opacity:0">{mono(44)}<span style="font-size:30px;font-weight:600">@bentaka</span></div>

<div data-in="{s('G')}" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px;opacity:0;padding-bottom:180px">
<div style="display:flex;align-items:center;gap:30px">{mono(150)}<span class="sora" style="font-weight:700;font-size:150px;letter-spacing:-.045em;padding-bottom:12px">bentaka</span></div>
<span class="sora c" style="font-weight:600;font-size:52px">Future, first<span class="v">.</span></span>
<span class="chip" style="font-size:26px;padding:14px 28px">TAKİP ET · @BENTAKA</span>
<span class="mono c" style="font-size:20px;letter-spacing:.06em;text-align:center;line-height:1.7;margin-top:24px">KAYNAK: PLAYSTATION STORE TR / DE · 2026 BRÜT ASGARİ ÜCRETLER<br>TR 33.030 TL / 225 SAAT · DE 13,90 € · ABD FEDERAL 7,25 $</span></div>
</div>
<script>
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const prog=(t,s,d)=>clamp((t-s)/d,0,1);
const ease=p=>1-Math.pow(1-p,3);
const fmt=x=>x.toFixed(1).replace('.',',');
window.render=function(t){{
  document.querySelectorAll('[data-in]').forEach(el=>{{
    const a=ease(prog(t,+el.dataset.in,0.45));
    const o=el.dataset.out?1-ease(prog(t,+el.dataset.out,0.35)):1;
    el.style.opacity=Math.min(a,o);
    el.style.transform='translateY('+((1-a)*40).toFixed(1)+'px)';
  }});
  document.querySelectorAll('[data-bar]').forEach(el=>{{
    el.style.width=(ease(prog(t,+el.dataset.bs,+el.dataset.bd))*+el.dataset.bar).toFixed(1)+'px';
  }});
  document.querySelectorAll('[data-count]').forEach(el=>{{
    el.textContent=fmt(ease(prog(t,+el.dataset.cs,+el.dataset.cd))*+el.dataset.count);
  }});
}};
window.render(0);
</script></body></html>'''

def build_voice(path):
    sr = None
    track = None
    for k, _ in order:
        with wave.open(os.path.join(TTS, f'{k}.wav')) as w:
            sr = sr or w.getframerate()
            if track is None:
                track = np.zeros(int(TOTAL * sr), np.int16)
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        i = int(s(k) * sr)
        track[i:i + len(a)] = a[: len(track) - i]
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(track.tobytes())

def script_txt(path):
    labels = {'A': 'Giriş', 'B': 'Geçiş', 'C': 'Almanya', 'D': 'ABD', 'E1': 'Türkiye', 'E2': 'Vurgu',
              'F1': 'Soru', 'F2': 'Çağrı', 'G': 'Kapanış'}
    lines = ['BENTAKA · GTA 6 REELS SESLENDİRME METNİ', f'Toplam süre: {TOTAL:.0f} sn', '',
             'Her satırı solundaki saniyede söylemeye başla. Sakin ama enerjik, gülümseyerek konuş.', '']
    for k, _ in order:
        txt = TXT[k].replace('Ci ti ey altı', 'GTA 6')
        lines.append(f'{s(k):5.1f} sn  [{labels[k]}]  {txt}')
    lines += ['', 'Kayıt ipuçları: sessiz bir odada, telefonu ağzından bir karış uzakta tut;',
              'battaniye veya dolap içi gibi yumuşak bir ortam yankıyı azaltır.']
    open(path, 'w').write('\n'.join(lines) + '\n')

if __name__ == '__main__':
    open(os.path.join(HERE, 'reels_voice.html'), 'w').write(HTML)
    build_voice(os.path.join(HERE, 'voice.wav'))
    print(json.dumps({'total': TOTAL, 'T': T}))
