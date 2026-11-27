import math,sys,os
out=sys.argv[1]
SKY="#4FB3E8"; SKYL="#A9DBF5"; NAVY="#0B2545"; RED="#E30A17"; GOLD="#E8B931"; W="#FFFFFF"
SANS="DejaVu Sans, Arial, sans-serif"; SERIF="DejaVu Serif, Georgia, serif"

def brick(pid,fill,line,w=12,h=6):
    return f'<pattern id="{pid}" width="{w}" height="{h*2}" patternUnits="userSpaceOnUse"><rect width="{w}" height="{h*2}" fill="{fill}"/><path d="M0 0H{w} M0 {h}H{w} M{w/2} 0V{h} M0 {h}V{h*2} M{w} {h}V{h*2}" stroke="{line}" stroke-width="0.9"/></pattern>'

def bridge(x0,x1,yb,yt,peak,arches,fill,stroke,sw=3):
    cx=(x0+x1)/2; cy=2*peak-yt
    d=f"M{x0} {yb} L{x0} {yt} Q{cx} {cy} {x1} {yt} L{x1} {yb} Z"
    for c,r,ty in arches:
        d+=f" M{c-r} {yb} L{c-r} {ty+r} A{r} {r} 0 0 1 {c+r} {ty+r} L{c+r} {yb} Z"
    par=f'<path d="M{x0-4} {yt-1} Q{cx} {cy-2} {x1+4} {yt-1}" fill="none" stroke="{stroke}" stroke-width="{sw+2}" stroke-linecap="round"/>'
    return f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'+par

def garlic(cx,cy,s,fill,line,sw=2.5):
    return f'''<g transform="translate({cx} {cy}) scale({s})" stroke="{line}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round">
<path d="M-3 -29 C-3 -35 -2 -40 -1 -45 L2 -45 C2 -40 3 -35 3 -29" fill="{fill}"/>
<path d="M0 -28 C4 -19 10 -15 19 -10 C35 -2 37 16 27 26 C21 32 12 30 7 33 C3 35 -3 35 -7 33 C-12 30 -21 32 -27 26 C-37 16 -35 -2 -19 -10 C-10 -15 -4 -19 0 -28 Z" fill="{fill}"/>
<path d="M0 -22 C-6 -4 -8 16 -6 32 M0 -22 C6 -4 8 16 6 32 M-13 -8 C-24 6 -22 20 -16 29 M13 -8 C24 6 22 20 16 29" fill="none" stroke-width="{sw*0.8}"/>
<path d="M-6 34 l-4 6 M-2 35 l-1 7 M2 35 l1 7 M6 34 l4 6" fill="none"/></g>'''

def star(cx,cy,R,rot,fill):
    pts=[]
    for i in range(10):
        r=R if i%2==0 else R*0.382
        a=math.radians(rot+i*36)
        pts.append(f"{cx+r*math.cos(a):.2f},{cy+r*math.sin(a):.2f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'

def waves(x0,x1,y,step,amp,color,sw,op=1):
    d=f"M{x0} {y}"; n=int((x1-x0)/step)
    d+=f" q{step/2} {-amp} {step} 0"+f" t{step} 0"*(n-1)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" opacity="{op}"/>'

def svg(w,h,body,name):
    open(os.path.join(out,name),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n{body}\n</svg>\n')

# 1 — Yenilenmiş klasik kalkan (eski logonun formu, açık mavi)
outer="M110 28 L290 28 L372 98 C382 230 330 362 200 442 C70 362 18 230 28 98 Z"
inner="M115 40 L285 40 L359 104 C368 228 320 350 200 427 C80 350 32 228 41 104 Z"
b=f'''<defs><clipPath id="c1"><path d="{inner}"/></clipPath>{brick("b1",W,NAVY)}</defs>
<path d="{outer}" fill="{NAVY}"/><path d="{inner}" fill="{W}"/>
<g clip-path="url(#c1)"><path d="M0 0 L132 0 L194 440 L0 440 Z" fill="{SKY}"/><path d="M268 0 L400 0 L400 440 L206 440 Z" fill="{SKY}"/></g>
<path d="{inner}" fill="none" stroke="{NAVY}" stroke-width="3"/>
<circle cx="194" cy="80" r="19" fill="{RED}"/><circle cx="199.5" cy="80" r="15" fill="{W}"/>{star(214,80,8,180,RED)}
<path id="t1" d="M60 206 Q200 140 340 206" fill="none"/>
<text font-family="{SANS}" font-weight="bold" font-size="31" fill="{NAVY}" stroke="{W}" stroke-width="5" paint-order="stroke" letter-spacing="0.5"><textPath href="#t1" startOffset="50%" text-anchor="middle">TAŞKÖPRÜSPOR</textPath></text>
{garlic(200,232,0.82,W,NAVY,3)}
{bridge(94,306,322,292,272,[(118,13,300),(158,17,290),(200,22,282),(242,17,290),(282,13,300)],"url(#b1)",NAVY)}
{waves(108,292,334,23,7,NAVY,3.5)}{waves(130,270,345,23,6,NAVY,3,.5)}
<text x="200" y="384" text-anchor="middle" font-family="{SANS}" font-weight="bold" font-size="40" fill="{NAVY}">1937</text>'''
svg(400,470,b,"1-klasik-kalkan-mavi.svg")

# 2 — Yuvarlak mühür arma
b=f'''<defs>{brick("b2",W,NAVY,10,5)}<clipPath id="c2"><circle cx="200" cy="200" r="106"/></clipPath>
<path id="tt" d="M70 200 A130 130 0 0 1 330 200"/><path id="tb" d="M56 200 A144 144 0 0 0 344 200"/></defs>
<circle cx="200" cy="200" r="192" fill="{NAVY}"/><circle cx="200" cy="200" r="182" fill="{SKY}"/>
<circle cx="200" cy="200" r="174" fill="none" stroke="{W}" stroke-width="2"/>
<circle cx="200" cy="200" r="112" fill="{NAVY}"/><circle cx="200" cy="200" r="106" fill="{W}"/>
<text font-family="{SANS}" font-weight="bold" font-size="38" fill="{NAVY}" letter-spacing="3"><textPath href="#tt" startOffset="50%" text-anchor="middle">TAŞKÖPRÜSPOR</textPath></text>
<text font-family="{SANS}" font-weight="bold" font-size="21" fill="{W}" letter-spacing="4"><textPath href="#tb" startOffset="50%" text-anchor="middle">TAŞKÖPRÜ · KASTAMONU</textPath></text>
{star(46,204,9,-90,W)}{star(354,204,9,-90,W)}
<g clip-path="url(#c2)"><rect x="90" y="232" width="220" height="90" fill="{SKY}"/>
{waves(90,310,246,20,6,W,3,.9)}{waves(80,320,258,20,6,W,2.5,.5)}</g>
{garlic(200,150,0.78,W,NAVY,3)}
{bridge(112,288,232,206,190,[(130,10,214),(165,14,206),(200,17,200),(235,14,206),(270,10,214)],"url(#b2)",NAVY,2.5)}
<text x="200" y="295" text-anchor="middle" font-family="{SERIF}" font-weight="bold" font-size="32" fill="{NAVY}">1937</text>'''
svg(400,400,b,"2-yuvarlak-muhur.svg")

# 3 — Modern sade
sh="M60 34 H340 A20 20 0 0 1 360 54 V220 C360 330 282 398 200 430 C118 398 40 330 40 220 V54 A20 20 0 0 1 60 34 Z"
b=f'''<path d="{sh}" fill="{SKY}"/>
<path d="{sh}" fill="none" stroke="{W}" stroke-width="4" transform="translate(200 232) scale(0.95) translate(-200 -232)"/>
{garlic(200,128,1.3,W,NAVY,2.6)}
{bridge(66,334,272,232,212,[(106,16,246),(153,19,238),(200,22,232),(247,19,238),(294,16,246)],NAVY,NAVY,2)}
{waves(80,320,286,24,6,W,4)}{waves(104,296,299,24,5,W,3,.6)}
<text x="200" y="338" text-anchor="middle" font-family="{SANS}" font-weight="bold" font-size="25" fill="{NAVY}" letter-spacing="2">TAŞKÖPRÜSPOR</text>
<path d="M136 364 H166 M234 364 H264" stroke="{NAVY}" stroke-width="3"/>
<text x="200" y="372" text-anchor="middle" font-family="{SANS}" font-weight="bold" font-size="22" fill="{W}">1937</text>'''
svg(400,450,b,"3-modern-sade.svg")

# 4 — Tarih: Pompeiopolis sütunları + köprü + sarımsak + defne
C=(220,205); R=165
leaves=""
for side in (-1,1):
    for i,deg in enumerate(range(100,232,11)):
        th=deg if side<0 else 180-deg
        a=math.radians(th); rr=186+(6 if i%2 else -6)
        x=C[0]+rr*math.cos(a); y=C[1]+rr*math.sin(a)
        rot=th+(25 if i%2 else -25)*(-side)
        leaves+=f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="6" ry="15" transform="rotate({rot:.1f} {x:.1f} {y:.1f})"/>'
cols="".join(f'<rect x="{x}" y="130" width="11" height="44"/><path d="M{x+3.7} 133 V171 M{x+7.3} 133 V171" stroke="{NAVY}" stroke-width="1.2"/>' for x in (176,201,228,253))
b=f'''<defs>{brick("b4",SKYL,NAVY,12,6)}</defs>
<path d="M{C[0]} 396 A186 186 0 0 1 {C[0]-186*math.cos(math.radians(40)):.1f} {C[1]-186*math.sin(math.radians(40)):.1f} M{C[0]} 396 A186 186 0 0 0 {C[0]+186*math.cos(math.radians(40)):.1f} {C[1]-186*math.sin(math.radians(40)):.1f}" fill="none" stroke="{SKY}" stroke-width="4"/>
<g fill="{SKY}">{leaves}</g>
<circle cx="{C[0]}" cy="{C[1]}" r="{R}" fill="{NAVY}"/><circle cx="{C[0]}" cy="{C[1]}" r="{R-10}" fill="none" stroke="{SKY}" stroke-width="2.5"/>
<g fill="{SKY}"><path d="M164 120 L220 90 L276 120 Z"/><rect x="162" y="120" width="116" height="9"/>{cols}<rect x="166" y="174" width="108" height="6"/><rect x="160" y="180" width="120" height="6"/></g>
<path d="M190 114 L220 99 L250 114" fill="none" stroke="{NAVY}" stroke-width="2"/>
{garlic(118,152,0.72,W,NAVY,3)}{garlic(322,152,0.72,W,NAVY,3)}
{bridge(98,342,256,226,206,[(126,12,234),(173,15,226),(220,18,218),(267,15,226),(314,12,234)],"url(#b4)",SKY,2.5)}
{waves(112,328,267,24,6,SKY,3)}
<path d="M50 290 L92 282 L92 330 L50 338 L64 314 Z" fill="#2B7FB0"/><path d="M390 290 L348 282 L348 330 L390 338 L376 314 Z" fill="#2B7FB0"/>
<rect x="78" y="280" width="284" height="48" rx="3" fill="{SKY}"/><rect x="84" y="285" width="272" height="38" fill="none" stroke="{W}" stroke-width="1.5"/>
<text x="220" y="314" text-anchor="middle" font-family="{SERIF}" font-weight="bold" font-size="27" fill="{NAVY}" letter-spacing="1">TAŞKÖPRÜSPOR</text>
<text x="220" y="356" text-anchor="middle" font-family="{SERIF}" font-weight="bold" font-size="22" fill="{W}" letter-spacing="3">★ 1937 ★</text>
<text x="220" y="436" text-anchor="middle" font-family="{SERIF}" font-weight="bold" font-size="15" fill="{NAVY}" letter-spacing="5">TAŞKÖPRÜ · KASTAMONU</text>'''
svg(440,450,b,"4-tarih-pompeiopolis.svg")
