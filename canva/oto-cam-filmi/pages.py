import json, sys
from ops import *

PID = {2:"PBB9zdNmZHH4q0m2",3:"PBjmT3Tjsq1Gyw5M",4:"PBGhYvtC7snsBWs3",5:"PBXBxB19pRTvgcYr",6:"PBNL9VrbYR399GP5",
       7:"PBjzGHp6bN237YyH",8:"PBfX7k2rvjT6f45t",9:"PBm9BqRJZsp3ZfQd",10:"PBT8hysYdx3JQ1QC"}
FMT = {}  # (page, text) -> formatting

def T(pg, p, t, top, left, width, size, color, bold=True, align=None, lh=None):
    FMT[(pg, t)] = dict(font_size=size, color=color, font_weight="bold" if bold else "normal",
                        **({"text_align": align} if align else {}), **({"line_height": lh} if lh else {}))
    return text(p, t, top, left, width)

def shape(p, top, left, w, h, path, vb=64, color=None, stroke=None, sw=None, op=None):
    d = {"type":"insert_shape","page_id":p,"top":top,"left":left,"width":w,"height":h,"path":path,
         "view_box_width":vb,"view_box_height":vb}
    if color: d["color"]=color
    if stroke: d["stroke_color"]=stroke; d["stroke_weight"]=sw
    if op is not None: d["opacity"]=op
    return d

def badge(p):
    return [rect(p,34,62,236,178,WHITE,rnd=24), logo(p,False)]

def kick(pg, p, t, color):
    return [T(pg,p,t,270,M,900,30,color), rect(p,316,M,70,6,color)]

def foot(pg, p, dark, accent):
    ops = footer(p, pg-1, dark, accent)
    left = N-pg
    FMT[(pg,"TEL")] = dict(font_size=14,color=WHITE,font_weight="bold",text_align="center",line_height=1)
    FMT[(pg,PHONE)] = dict(font_size=38,color=GRAY if dark else WHITE,font_weight="bold",line_height=1)
    FMT[(pg,f"{pg}/{N}  ·  "+("Son" if left==0 else f"{left} kaldı"))] = dict(font_size=26,color=WHITE if dark else GRAY,font_weight="bold",text_align="end",line_height=1)
    return ops

def card(pg,p,top,h,bar,title,sub,tsize=40,ssize=30):
    return [rect(p,top,M,920,h,WHITE,rnd=26), rect(p,top,M,14,h,bar,rnd=7),
            T(pg,p,title,top+26,M+46,850,tsize,GRAY,lh=1.1), T(pg,p,sub,top+26+tsize+20,M+46,850,ssize,"#6B7178",bold=False,lh=1.2)]

def page(pg):
    p = PID[pg]; o = stripe(p)
    if pg==2:
        o += [logo(p,False)] + kick(pg,p,"TEMEL BİLGİ",TEAL)
        o += [T(pg,p,"Cam filmi nedir?",340,M,920,92,GRAY,lh=1.05),
              T(pg,p,"Araç camlarının iç yüzeyine uygulanan, çok katmanlı ince bir polyester filmdir. Güneş ışınlarını süzer, camı güçlendirir ve aracınıza şık bir görünüm kazandırır.",470,M,920,36,"#50565E",bold=False,lh=1.35)]
        for i,(a,b) in enumerate([("Çok katmanlı yapı","İnce ama dayanıklı polyester katmanlar"),("İçten uygulama","Film, camın iç yüzeyine yapıştırılır"),("Işığı süzer","Görüşü kapatmadan ısıyı ve UV'yi azaltır")]):
            o += card(pg,p,720+i*150,130,TEAL,a,b,36,28)
        o += foot(pg,p,False,TEAL)
    if pg==3:
        o += [logo(p,True)] + kick(pg,p,"SAĞLIĞINIZ İÇİN",WHITE)
        o += [rect(p,330,800,200,200,WHITE,rnd=100,op=0.22), rect(p,380,850,100,100,WHITE,rnd=50,op=0.9)]
        o += [T(pg,p,"%99",330,M-6,700,280,WHITE,lh=1),
              T(pg,p,"UV koruması",650,M,920,84,DARK,lh=1.05),
              T(pg,p,"Kaliteli cam filmleri, güneşin zararlı UV ışınlarının %99'a varan kısmını engeller. Uzun yolculuklarda cildinizi ve gözlerinizi korur.",780,M,920,38,WHITE,bold=False,lh=1.35)]
        o += foot(pg,p,True,DARK)
    if pg==4:
        o += [logo(p,False)] + kick(pg,p,"KONFOR",RED)
        o += [T(pg,p,"Daha serin",340,M,920,100,GRAY,lh=1), T(pg,p,"bir araç",450,M,920,100,RED,lh=1)]
        for i,(a,b) in enumerate([("Güneş ısısını azaltır","Araç içi yaz aylarında çok daha serin kalır."),("Klima daha az yorulur","Daha hızlı soğuma, yakıt tasarrufuna katkı."),("Direksiyon ve koltuklar","Güneşte bekleyen araçta daha az ısınır.")]):
            o += card(pg,p,630+i*160,140,RED,a,b,40,30)
        o += foot(pg,p,False,RED)
    if pg==5:
        o += [logo(p,True)] + kick(pg,p,"GÜVENLİ SÜRÜŞ",GREEN)
        o += [shape(p,370,300,480,290,"M0 32 C16 2 48 2 64 32 C48 62 16 62 0 32 Z",color=GREEN),
              rect(p,430,455,170,170,DARK,rnd=85), rect(p,475,500,80,80,GREEN,rnd=40), rect(p,480,545,26,26,WHITE,rnd=13)]
        o += [T(pg,p,"Daha az parlama",720,M,920,92,WHITE,lh=1.05),
              T(pg,p,"Güneşin ve karşıdan gelen farların yarattığı göz kamaşmasını azaltır. Gözleriniz daha az yorulur, yola daha rahat odaklanırsınız.",850,M,920,36,"#CDD3D9",bold=False,lh=1.35)]
        o += foot(pg,p,True,GREEN)
    if pg==6:
        o += badge(p) + kick(pg,p,"MAHREMİYET",WHITE)
        o += [T(pg,p,"Daha fazla",340,M,920,104,WHITE,lh=1), T(pg,p,"mahremiyet",455,M,920,104,DARK,lh=1)]
        for top,t in [(650,"Araç içi dışarıdan zor görünür, eşyalarınız meraklı gözlerden uzak kalır"),(810,"Hırsızlık riskine karşı caydırıcı olur"),(910,"Kendinizi daha özel ve rahat hissedersiniz")]:
            o += [rect(p,top+12,M,28,28,WHITE,rnd=14), T(pg,p,t,top,M+56,860,40,WHITE,lh=1.3)]
        o += foot(pg,p,True,DARK)
    if pg==7:
        o += [logo(p,False)] + kick(pg,p,"EKSTRA GÜVENLİK",TEAL)
        o += [T(pg,p,"Cam kırılsa bile",340,M,920,88,GRAY,lh=1), T(pg,p,"dağılmaz",440,M,920,88,TEAL,lh=1)]
        o += [rect(p,590,M,920,300,"#D6E8EC",rnd=30),
              shape(p,610,200,380,260,"M32 32 L4 6 M32 32 L60 4 M32 32 L62 40 M32 32 L42 62 M32 32 L10 60 M32 32 L2 34 M32 32 L26 2 M32 32 L50 58",stroke=WHITE,sw=3),
              shape(p,655,770,170,180,"M32 2 L60 12 V30 C60 46 48 58 32 62 C16 58 4 46 4 30 V12 Z",color=TEAL),
              shape(p,655,770,170,180,"M18 32 L28 42 L46 22",stroke=WHITE,sw=7)]
        o += [T(pg,p,"Kaza veya darbe anında film, cam parçalarını bir arada tutar. Sıçrayan cam parçalarının yaralanmalara yol açma riskini azaltır.",930,M,920,36,"#50565E",bold=False,lh=1.35)]
        o += foot(pg,p,False,TEAL)
    if pg==8:
        o += badge(p) + kick(pg,p,"İÇ MEKAN KORUMASI",DARK)
        o += [T(pg,p,"Aracınız",340,M,920,100,WHITE,lh=1), T(pg,p,"daha uzun",450,M,920,100,WHITE,lh=1), T(pg,p,"yeni kalır",560,M,920,100,DARK,lh=1)]
        w = (920-48)/3
        for i,(a,b) in enumerate([("Döşeme","Solmayı geciktirir"),("Torpido","Çatlama riski azalır"),("Değer","İkinci elde avantaj")]):
            x = M+i*(w+24)
            o += [rect(p,750,x,w,250,WHITE,rnd=26), T(pg,p,a,786,x+28,w-56,44,GRAY,lh=1.1), T(pg,p,b,860,x+28,w-56,30,"#6B7178",bold=False,lh=1.25)]
        o += foot(pg,p,True,DARK)
    if pg==9:
        o += [logo(p,False)] + kick(pg,p,"DOĞRU SEÇİM",RED)
        o += [T(pg,p,"Film çeşitleri",340,M,920,92,GRAY,lh=1.05)]
        w = 445
        for i,(title,col,feats) in enumerate([("Karbon Film",GRAY,["Mat ve şık görünüm","Solmaya dayanıklı","Uygun fiyatlı","İyi ısı yalıtımı"]),
                                               ("Nano Seramik",TEAL,["En yüksek ısı yalıtımı","Net ve berrak görüş","GPS ve telefon sinyalini kesmez","Uzun ömürlü"])]):
            x = M+i*(w+30)
            o += [rect(p,490,x,w,560,WHITE,rnd=30), rect(p,490,x,w,110,col,rnd=30), rect(p,560,x,w,40,col),
                  T(pg,p,title,520,x+30,w-60,44,WHITE,lh=1)]
            for j,f in enumerate(feats):
                o += [T(pg,p,"✓  "+f,640+j*100,x+30,w-60,30,GRAY,lh=1.2)]
        o += [T(pg,p,"Hangisinin size uygun olduğuna birlikte karar verelim.",1090,M,920,34,RED,lh=1.2)]
        o += foot(pg,p,False,RED)
    if pg==10:
        o = [{"type":"insert_fill","page_id":p,"asset_type":"image","asset_id":"MAHZ9nFSnNQ","alt_text":"Siyah sedan araç","top":0,"left":-200,"width":1480,"height":1350,"opacity":0.22}] + o
        o += [{"type":"insert_fill","page_id":p,"asset_type":"image","asset_id":LOGO_WHITE,"alt_text":"Arabacı Reklam logosu","top":150,"left":300,"width":480,"height":358}]
        o += [T(pg,p,"Randevu için hemen arayın",570,M,920,62,WHITE,align="center",lh=1.1),
              rect(p,690,140,800,150,GREEN,rnd=75), T(pg,p,PHONE+" ",722,140,800,86,WHITE,align="center",lh=1),
              T(pg,p,"Profesyonel uygulama · Kaliteli malzeme",890,M,920,36,"#D0D5DA",bold=False,align="center"),
              T(pg,p,"Uygulamalar yasal mevzuata uygun şekilde yapılır.",950,M,920,26,"#9AA2AA",bold=False,align="center")]
        o += foot(pg,p,True,GREEN)
    return o

if __name__=="__main__":
    pg=int(sys.argv[1]); ops=page(pg)
    json.dump({"ops":ops,"fmt":{t:f for (g,t),f in FMT.items() if g==pg}}, open(f"p{pg}.json","w"), ensure_ascii=False)
    print(len(ops))
