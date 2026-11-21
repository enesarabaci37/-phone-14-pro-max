#!/usr/bin/env python3
"""WhatsApp güvenlik Reels'i: sesten zaman çizelgesi + yazı katmanı. Kullanım: python3 build.py <ses_klasörü> [tempo=1.2]"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
VO, TEMPO = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 1.2
GAP, LEAD, TAIL, N = 0.3, 0.25, 2.3, 7
dur = lambda p: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
D = [dur(os.path.join(VO, f't{i}.wav')) / TEMPO for i in range(1, N + 1)]
V = [0.4]
for d in D[:-1]: V.append(round(V[-1] + d + GAP, 3))
S = [0.0] + [round(v - LEAD, 3) for v in V[1:]]
END = round(V[-1] + D[-1] + TAIL, 2); E = S[1:] + [99]
r = lambda i, x: round(x * D[i] + LEAD, 2)
LOGO = ('<svg width="{s}" height="{s}" viewBox="0 0 120 120" aria-hidden="true"><rect x="18" y="8" width="24" height="104" rx="5" fill="#F3F5F8"/>'
        '<circle cx="68" cy="72" r="28" fill="none" stroke="#F3F5F8" stroke-width="24"/><circle {id} cx="68" cy="72" r="8" fill="#C6FF3D"/></svg>')
SEND = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7z"/></svg>'
WARN = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#0B0E14" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>'
num = lambda n: f'<div class="badge">{n}</div>'
scenes = [
f'''<div class="pad" style="top:420px">
  <div class="el" data-in="0.1"><span class="chip red">{WARN} DİKKAT!</span></div>
  <div class="el bub" data-in="{r(0,.05)}" data-fx="left" style="margin-top:50px"><div class="who">ANNEM ❤️ · şimdi</div>Kızım acil 5.000 TL lazım, şu IBAN'a atar mısın? Sonra anlatırım 🙏</div>
  <div class="el h1" data-in="{r(0,.35)}" style="font-size:80px;margin-top:60px">Böyle bir mesaj gelirse…</div>
  <div class="el big" data-in="{r(0,.7)}" data-fx="punch" style="font-size:108px;margin-top:30px"><span class="hl dark" data-hl="{r(0,.76)}">sakın gönderme.<i></i></span></div>
</div>''',
f'''<div class="pad" style="top:440px">
  <div class="el label" data-in="0.1">Hesaplar ele geçiriliyor</div>
  <div class="el h1" data-in="{r(1,.0)}" style="font-size:86px;margin-top:40px">WhatsApp'ın çalınıyor, <span class="v">rehberindeki herkesten</span> para isteniyor.</div>
  <div class="el glass" data-in="{r(1,.65)}" style="display:inline-flex;align-items:center;gap:18px;padding:24px 34px;margin-top:60px;font-size:34px;font-weight:600">🛡️ Siber Güvenlik Başkanlığı uyardı</div>
</div>''',
f'''<div class="pad" style="top:380px">
  <div class="el" data-in="0.1" style="display:flex;align-items:center;gap:26px">{num(1)}<div class="h1" style="font-size:64px">İki adımlı doğrulamayı aç</div></div>
  <div class="el phone" data-in="{r(2,.15)}" data-fx="punch" style="margin:46px auto 0"><div class="scr">
    <div class="crumb">Ayarlar › Hesap</div><div class="ttl">İki adımlı doğrulama</div>
    <div class="grp"><div class="row hit"><span>İki adımlı doğrulama<small>6 haneli PIN ile koru</small></span><div class="tog" data-on="{r(2,.62)}"></div></div></div>
    <div class="grp"><div class="row"><span>PIN'i değiştir</span><span style="color:#9CA3AF">›</span></div><div class="row"><span>E-posta adresi ekle</span><span style="color:#9CA3AF">›</span></div></div>
  </div></div>
</div>''',
f'''<div class="pad" style="top:380px">
  <div class="el" data-in="0.1" style="display:flex;align-items:center;gap:26px">{num(2)}<div class="h1" style="font-size:64px">Bağlı cihazlara bak</div></div>
  <div class="el phone" data-in="{r(3,.1)}" data-fx="punch" style="margin:46px auto 0"><div class="scr">
    <div class="crumb">Ayarlar</div><div class="ttl">Bağlı cihazlar</div>
    <div class="grp"><div class="row"><span>💻 Mac · Safari<small>Son etkin: dün</small></span><span style="color:#16A34A;font-size:24px">SENİN</span></div>
    <div class="row hit"><span>🖥️ Windows · Chrome<small>Son etkin: şimdi · İstanbul?</small></span><span class="danger" style="font-size:24px">?</span></div></div>
    <div class="grp"><div class="row danger" style="justify-content:center">Çıkış yap</div></div>
  </div></div>
  <div class="el h1" data-in="{r(3,.6)}" style="font-size:56px;margin-top:40px;text-align:center">Tanımıyorsan <span class="v">hemen çıkış yap.</span></div>
</div>''',
f'''<div class="pad" style="top:470px">
  <div class="el label" data-in="0.1">Bir de</div>
  <div style="display:flex;flex-direction:column;gap:30px;margin-top:44px">
    <div class="el glass sign" data-in="{r(4,.0)}" data-fx="left">{num("🔒")}<div><div class="st">Kodu kimseyle paylaşma</div><div class="ss">WhatsApp'tan gelen 6 haneli doğrulama kodu sadece senin</div></div></div>
    <div class="el glass sign" data-in="{r(4,.5)}" data-fx="left">{num("📞")}<div><div class="st">Para isteyeni ara</div><div class="ss">Mesajla değil, telefonla sesini duyarak doğrula</div></div></div>
  </div>
</div>''',
f'''<div class="pad" style="top:470px">
  <div class="el" data-in="0.1" data-fx="plane">{SEND.format(s=180,c="#C6FF3D")}</div>
  <div class="el h1" data-in="{r(5,.0)}" style="font-size:108px;margin-top:50px">Bunu <span class="v">aile grubuna</span> gönder.</div>
  <div class="el h1 c" data-in="{r(5,.45)}" style="font-size:62px;margin-top:30px">Bir dakikada herkes korunsun.</div>
  <div class="el" data-in="{r(5,.7)}" style="display:flex;gap:22px;margin-top:70px"><span class="chip" style="font-size:30px;padding:20px 34px">{SEND.format(s=30,c="#0B0E14")}GÖNDER</span><span class="chip ghost" style="font-size:30px;padding:20px 34px">KAYDET</span></div>
</div>''',
f'''<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding-bottom:160px">
  <div class="el" data-in="0.1" data-fx="punch" style="display:flex;align-items:center;gap:32px">{LOGO.format(s=170,id='id="dot"')}<span class="sora" style="font-weight:700;font-size:170px;letter-spacing:-.045em;padding-bottom:14px">bentaka</span></div>
  <div class="el sora c" data-in="0.7" style="font-weight:600;font-size:60px;margin-top:40px">Future, first<span class="v">.</span></div>
  <div class="el" data-in="1.3" style="margin-top:60px"><span class="chip" style="font-size:28px;padding:16px 30px">TAKİP ET · @BENTAKATR</span></div>
</div>''',
]
secs = ''.join(f'<section class="scene" data-s="{S[i]}" data-e="{E[i]}">{scenes[i]}</section>\n' for i in range(N))
h = open(os.path.join(HERE, 'template.html')).read()
h = (h.replace('/*SCENES*/', secs).replace('/*WIPES*/', ','.join(str(x) for x in [S[1], S[2], S[4], S[5], S[6]]))
     .replace('/*FLASH*/', ','.join(str(x) for x in [r(0, .7), S[2] + r(2, .62), S[6] + .1]))
     .replace('/*END*/', str(END)).replace('/*LAST*/', str(S[6])).replace('/*CD*/', '0,0'))
open(os.path.join(HERE, 'reels.html'), 'w').write(h)
tl = {'END': END, 'S': S, 'V': V, 'D': D, 'SPEED': TEMPO, 'cuts': S[1:],
      'impacts': [r(0, .7), S[2] + r(2, .62), S[6] + .1], 'risers': [[round(S[5] - 1.0, 3), 1.0], [round(S[6] - 1.2, 3), 1.2]],
      'tr_ticks': [S[2] + r(2, .3), 0.8], 'day_ticks': [S[3] + r(3, .3), 0.6],
      'sections': [[S[1], 'full'], [S[2], 'tension'], [S[5], 'full'], [S[6] - 1.5, 'build'], [S[6], 'full'], [999, 'outro']]}
json.dump(tl, open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
print(json.dumps({'S': S, 'END': END}))
