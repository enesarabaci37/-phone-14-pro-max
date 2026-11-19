/* Birsıfır illüstrasyon kütüphanesi — düz, sade, marka renkleri */
const C_={blue:'#0A5CFF',soft:'#E8EFFF',ink:'#0B0F1A',white:'#FFFFFF',yellow:'#FFC300',gray:'#C9CED8',red:'#E5192E',paper:'#F6F7F9'};
function sparkle(cx,cy,r,fill){const k=0.2;return `<path d="M ${cx} ${cy-r} C ${cx+r*k} ${cy-r*k} ${cx+r*k} ${cy-r*k} ${cx+r} ${cy} C ${cx+r*k} ${cy+r*k} ${cx+r*k} ${cy+r*k} ${cx} ${cy+r} C ${cx-r*k} ${cy+r*k} ${cx-r*k} ${cy+r*k} ${cx-r} ${cy} C ${cx-r*k} ${cy-r*k} ${cx-r*k} ${cy-r*k} ${cx} ${cy-r} Z" fill="${fill}"/>`;}
const ART={
 /* ---- kapak çizimleri (420x420) ---- */
 chat:()=>`<svg viewBox="0 0 420 420"><circle cx="210" cy="210" r="200" fill="${C_.soft}"/>
   <rect x="120" y="40" width="180" height="340" rx="34" fill="${C_.white}" stroke="${C_.ink}" stroke-width="12"/>
   <rect x="180" y="58" width="60" height="10" rx="5" fill="${C_.ink}"/>
   <rect x="142" y="100" width="110" height="44" rx="18" fill="${C_.paper}" stroke="${C_.gray}" stroke-width="3"/>
   <rect x="170" y="160" width="110" height="44" rx="18" fill="${C_.blue}"/>
   <path d="M 236 190 l 8 8 l 14 -16 M 248 190 l 8 8 l 14 -16" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
   <rect x="142" y="220" width="90" height="44" rx="18" fill="${C_.paper}" stroke="${C_.gray}" stroke-width="3"/>
   <rect x="190" y="280" width="90" height="44" rx="18" fill="${C_.blue}"/>
   <circle cx="330" cy="110" r="44" fill="${C_.yellow}"/><text x="330" y="128" text-anchor="middle" font-family="Inter Display" font-weight="800" font-size="52" fill="${C_.ink}">5</text></svg>`,
 battery:()=>`<svg viewBox="0 0 420 420"><circle cx="210" cy="210" r="200" fill="${C_.soft}"/>
   <rect x="70" y="130" width="250" height="160" rx="30" fill="${C_.white}" stroke="${C_.ink}" stroke-width="14"/>
   <rect x="330" y="180" width="26" height="60" rx="10" fill="${C_.ink}"/>
   <rect x="92" y="152" width="170" height="116" rx="16" fill="${C_.blue}"/>
   <path d="M 205 160 L 168 218 L 198 218 L 186 262 L 232 196 L 200 196 L 214 160 Z" fill="${C_.yellow}" stroke="${C_.ink}" stroke-width="6" stroke-linejoin="round"/></svg>`,
 binary:()=>`<svg viewBox="0 0 420 420"><circle cx="210" cy="210" r="200" fill="rgba(255,255,255,.12)"/>
   <line x1="130" y1="110" x2="130" y2="310" stroke="#fff" stroke-width="40" stroke-linecap="round"/>
   <circle cx="285" cy="210" r="82" fill="none" stroke="#fff" stroke-width="40"/></svg>`,
 ai:()=>`<svg viewBox="0 0 420 420"><circle cx="210" cy="210" r="200" fill="rgba(91,140,255,.14)"/>
   <rect x="70" y="100" width="280" height="190" rx="44" fill="none" stroke="#fff" stroke-width="12"/>
   <path d="M 130 290 L 112 345 L 180 290" fill="#0B0F1A" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>
   ${sparkle(210,195,62,C_.blue)}${sparkle(292,138,22,'#fff')}${sparkle(138,250,16,C_.yellow)}</svg>`,
 slow:()=>`<svg viewBox="0 0 420 420"><circle cx="210" cy="210" r="200" fill="${C_.soft}"/>
   <rect x="120" y="40" width="180" height="340" rx="34" fill="${C_.white}" stroke="${C_.ink}" stroke-width="12"/>
   <rect x="180" y="58" width="60" height="10" rx="5" fill="${C_.ink}"/>
   <circle cx="210" cy="190" r="52" fill="none" stroke="${C_.soft}" stroke-width="16"/>
   <path d="M 210 138 A 52 52 0 0 1 259 207" fill="none" stroke="${C_.blue}" stroke-width="16" stroke-linecap="round"/>
   <rect x="150" y="280" width="120" height="16" rx="8" fill="${C_.soft}"/><rect x="150" y="280" width="36" height="16" rx="8" fill="${C_.blue}"/>
   <circle cx="330" cy="110" r="44" fill="${C_.yellow}"/><path d="M 310 92 h 40 M 310 128 h 40 M 314 92 q 0 18 16 18 q -16 0 -16 18 M 346 92 q 0 18 -16 18 q 16 0 16 18" stroke="${C_.ink}" stroke-width="6" fill="none" stroke-linecap="round"/></svg>`,
 cv:()=>`<svg viewBox="0 0 420 420"><circle cx="210" cy="210" r="200" fill="rgba(91,140,255,.14)"/>
   <rect x="110" y="50" width="200" height="290" rx="20" fill="#fff"/>
   <circle cx="160" cy="105" r="28" fill="${C_.soft}"/><circle cx="160" cy="98" r="10" fill="${C_.blue}"/><path d="M 142 124 q 18 -22 36 0" fill="${C_.blue}"/>
   <rect x="200" y="88" width="88" height="12" rx="6" fill="${C_.ink}"/><rect x="200" y="110" width="60" height="10" rx="5" fill="${C_.gray}"/>
   ${[160,190,220,250,280].map((y,i)=>`<rect x="135" y="${y}" width="${[150,120,150,100,130][i]}" height="10" rx="5" fill="${i%2?C_.gray:'#DDE3EE'}"/>`).join('')}
   ${sparkle(318,300,46,C_.blue)}${sparkle(352,240,16,C_.yellow)}</svg>`,
 lock:()=>`<svg viewBox="0 0 420 420"><circle cx="210" cy="210" r="200" fill="${C_.soft}"/>
   <path d="M 150 200 V 150 a 60 60 0 0 1 120 0 V 200" fill="none" stroke="${C_.ink}" stroke-width="22" stroke-linecap="round"/>
   <rect x="110" y="190" width="200" height="170" rx="30" fill="${C_.blue}"/>
   <circle cx="210" cy="260" r="20" fill="#fff"/><rect x="202" y="268" width="16" height="44" rx="8" fill="#fff"/>
   <g transform="rotate(-8 300 90)"><rect x="210" y="62" width="180" height="58" rx="16" fill="#fff" stroke="${C_.red}" stroke-width="5"/>
   <text x="300" y="104" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="34" fill="${C_.ink}">123456</text>
   <line x1="222" y1="91" x2="378" y2="91" stroke="${C_.red}" stroke-width="7" stroke-linecap="round"/></g></svg>`,

 /* ---- haber çizimleri (geniş, 920x560) ---- */
 n_gamepad:()=>`<svg viewBox="0 0 920 560"><rect width="920" height="560" fill="${C_.ink}"/>
   ${Array.from({length:40},(_,i)=>`<circle cx="${(i*137)%920}" cy="${(i*89)%560}" r="${1+(i%3)}" fill="rgba(255,255,255,.18)"/>`).join('')}
   <text x="700" y="430" text-anchor="middle" font-family="Inter Display" font-weight="800" font-size="420" fill="rgba(10,92,255,.35)">6</text>
   <path d="M 250 230 C 170 230 140 300 130 370 C 120 440 170 470 210 440 L 270 390 H 470 L 530 440 C 570 470 620 440 610 370 C 600 300 570 230 490 230 Z" fill="#fff"/>
   <rect x="215" y="285" width="16" height="64" rx="6" fill="${C_.ink}"/><rect x="191" y="309" width="64" height="16" rx="6" fill="${C_.ink}"/>
   <circle cx="500" cy="290" r="13" fill="${C_.blue}"/><circle cx="530" cy="318" r="13" fill="${C_.yellow}"/><circle cx="470" cy="318" r="13" fill="${C_.red}"/><circle cx="500" cy="346" r="13" fill="#1F9D55"/>
   <circle cx="320" cy="360" r="26" fill="${C_.soft}"/><circle cx="420" cy="360" r="26" fill="${C_.soft}"/></svg>`,
 n_chip:()=>`<svg viewBox="0 0 920 560"><rect width="920" height="560" fill="${C_.soft}"/>
   <g transform="translate(-70 0)">
   ${[0,1,2,3,4,5].map(i=>`<rect x="${300+i*52}" y="90" width="18" height="56" rx="6" fill="${C_.ink}"/><rect x="${300+i*52}" y="414" width="18" height="56" rx="6" fill="${C_.ink}"/>`).join('')}
   ${[0,1,2,3,4].map(i=>`<rect x="226" y="${178+i*48}" width="56" height="18" rx="6" fill="${C_.ink}"/><rect x="584" y="${178+i*48}" width="56" height="18" rx="6" fill="${C_.ink}"/>`).join('')}
   <rect x="272" y="136" width="322" height="288" rx="34" fill="${C_.ink}"/>
   <rect x="316" y="180" width="234" height="200" rx="18" fill="${C_.blue}"/>
   <path d="M 393 280 h 80 M 433 240 v 80" stroke="rgba(255,255,255,.35)" stroke-width="10" stroke-linecap="round"/></g>
   <g transform="translate(700 150)">
     <rect x="-62" y="0" width="124" height="150" rx="26" fill="#fff" stroke="${C_.ink}" stroke-width="10"/>
     <rect x="-82" y="150" width="164" height="40" rx="14" fill="#fff" stroke="${C_.ink}" stroke-width="10"/>
     <path d="M 0 190 V 260 M -60 290 L 0 260 L 60 290" stroke="${C_.ink}" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
     <circle cx="-60" cy="296" r="10" fill="${C_.ink}"/><circle cx="60" cy="296" r="10" fill="${C_.ink}"/>
     <rect x="-56" y="44" width="112" height="44" rx="10" fill="${C_.yellow}"/>
     <text y="76" text-anchor="middle" font-family="Inter Display" font-weight="800" font-size="30" fill="${C_.ink}">CEO</text></g>
   <path d="M 600 300 C 625 300 630 280 640 270" stroke="${C_.gray}" stroke-width="6" stroke-dasharray="2 12" stroke-linecap="round" fill="none"/></svg>`,
 n_voyager:()=>`<svg viewBox="0 0 920 560"><rect width="920" height="560" fill="#060A18"/>
   ${Array.from({length:70},(_,i)=>`<circle cx="${(i*131+40)%920}" cy="${(i*73+20)%560}" r="${(i%4)?1.5:2.6}" fill="rgba(255,255,255,${(i%3)?.35:.7})"/>`).join('')}
   <circle cx="110" cy="440" r="44" fill="${C_.blue}"/><path d="M 80 420 q 20 -10 30 6 q 12 14 34 4" stroke="#1F9D55" stroke-width="12" fill="none" stroke-linecap="round"/>
   <path d="M 170 420 C 380 360 520 260 640 200" stroke="rgba(255,255,255,.55)" stroke-width="5" stroke-dasharray="4 16" stroke-linecap="round" fill="none"/>
   <g transform="translate(720 170) rotate(-18)">
     <rect x="-120" y="-6" width="240" height="12" rx="6" fill="#C9CED8"/>
     <path d="M -70 -10 A 70 70 0 0 0 70 -10 Z" fill="#fff"/><rect x="-6" y="-60" width="12" height="54" fill="#fff"/>
     <rect x="-34" y="0" width="68" height="44" rx="8" fill="${C_.yellow}"/><line x1="0" y1="44" x2="0" y2="120" stroke="#C9CED8" stroke-width="6"/></g>
   <g transform="translate(400 470)"><rect x="-150" y="-34" width="300" height="68" rx="34" fill="rgba(255,255,255,.1)" stroke="rgba(255,255,255,.3)" stroke-width="2"/>
   <text y="12" text-anchor="middle" font-family="Inter Display" font-weight="800" font-size="34" fill="#fff">1 ışık günü</text></g></svg>`,
};
