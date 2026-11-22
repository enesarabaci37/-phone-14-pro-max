"""Normal (Rec.709) profille cekilmis videolar icin Lightroom presetleri.
Her kamera icin: kamera duzeltmesi (BASE) + gorunum (LOOK) birlestirilir."""
import uuid, os, zipfile, sys
from xml.sax.saxutils import escape

GROUP_ROOT = "Pro Video"

# ---- Ton egrileri (temiz, siyahlar soluk degil) ----
CLEAN_S  = [(0,0),(60,55),(128,128),(196,201),(255,255)]
SOFT_S   = [(0,0),(64,61),(128,128),(192,195),(255,255)]
CRISP_S  = [(0,0),(56,49),(128,128),(200,207),(255,255)]
CINE     = [(0,10),(58,52),(128,126),(196,200),(255,250)]

# ---- Kamera bazli duzeltmeler (Normal / Standart renk profili) ----
CAMERAS = {
  "DJI Mini 5 Pro": ("M5P", dict(   # drone: hava pusu, DJI normal profil zaten doygun
      Highlights2012=-15, Shadows2012=8, Contrast2012=4, Dehaze=8, Clarity2012=4, Texture=4,
      Vibrance=6, Saturation=-4, LuminanceAdjustmentBlue=-6)),
  "DJI Osmo Pocket 3": ("OP3", dict(  # 1" sensor, kontrastli ve keskinlestirilmis cikis
      Highlights2012=-12, Shadows2012=10, Contrast2012=-4, Saturation=-6, Texture=-4,
      SaturationAdjustmentOrange=-6, LuminanceAdjustmentOrange=6)),
  "Insta360 X5": ("X5", dict(        # Standart profil daha duz ve yumusak
      Highlights2012=-18, Shadows2012=6, Contrast2012=8, Vibrance=10, Saturation=2,
      Dehaze=6, Clarity2012=6, Texture=8, SaturationAdjustmentGreen=-6)),
}

# ---- Gorunumler ----
LOOKS = [
  ("01 Clean Natural", "Temiz, dogal ve net. Her cekime guvenle uygulanabilir temel.", CLEAN_S, dict(
      Exposure2012=0.05, Contrast2012=6, Highlights2012=-10, Shadows2012=6, Whites2012=6, Blacks2012=-6,
      Vibrance=10, Clarity2012=2)),
  ("02 İlkbahar", "Taze yesiller, cicek tonlari, parlak ve hafif pastel bahar havasi.", SOFT_S, dict(
      Exposure2012=0.10, Contrast2012=4, Highlights2012=-20, Shadows2012=12, Whites2012=4, Blacks2012=-4,
      Vibrance=16, Clarity2012=2, Dehaze=2,
      HueAdjustmentGreen=-8, SaturationAdjustmentGreen=10, LuminanceAdjustmentGreen=8,
      LuminanceAdjustmentYellow=6, SaturationAdjustmentMagenta=10, SaturationAdjustmentPurple=6,
      SaturationAdjustmentBlue=6, LuminanceAdjustmentOrange=4,
      SplitToningHighlightHue=60, SplitToningHighlightSaturation=6, SplitToningShadowHue=190, SplitToningShadowSaturation=4)),
  ("03 Yaz", "Parlak gunes, turkuaz deniz, derin mavi gokyuzu, sicak ten.", CRISP_S, dict(
      Exposure2012=0.05, Contrast2012=10, Highlights2012=-30, Shadows2012=10, Whites2012=6, Blacks2012=-8,
      Vibrance=22, Saturation=4, Clarity2012=4, Dehaze=4,
      HueAdjustmentAqua=-10, SaturationAdjustmentAqua=18, SaturationAdjustmentBlue=12, LuminanceAdjustmentBlue=-10,
      SaturationAdjustmentOrange=6, LuminanceAdjustmentOrange=6, SaturationAdjustmentYellow=8,
      ColorGradeGlobalHue=45, ColorGradeGlobalSat=5,
      SplitToningHighlightHue=45, SplitToningHighlightSaturation=10, SplitToningShadowHue=200, SplitToningShadowSaturation=6)),
  ("04 Sonbahar", "Altin yapraklar, zengin turuncu-kahve tonlar, sicak ve derin.", CLEAN_S, dict(
      Contrast2012=12, Highlights2012=-24, Shadows2012=6, Blacks2012=-10,
      Vibrance=12, Saturation=-2, Clarity2012=6,
      HueAdjustmentGreen=-30, SaturationAdjustmentGreen=-25, HueAdjustmentYellow=-12, SaturationAdjustmentYellow=15,
      SaturationAdjustmentOrange=18, LuminanceAdjustmentOrange=-4, SaturationAdjustmentRed=8, SaturationAdjustmentBlue=-10,
      ColorGradeGlobalHue=35, ColorGradeGlobalSat=9,
      SplitToningHighlightHue=45, SplitToningHighlightSaturation=12, SplitToningShadowHue=25, SplitToningShadowSaturation=8,
      PostCropVignetteAmount=-8)),
  ("05 Kış", "Bembeyaz kar, soguk ve kristal netlikte gorunum; gri kari temizler.", CRISP_S, dict(
      Exposure2012=0.15, Contrast2012=10, Highlights2012=-28, Shadows2012=10, Whites2012=14, Blacks2012=-8,
      Vibrance=6, Saturation=-10, Clarity2012=8, Dehaze=8, Texture=6,
      HueAdjustmentBlue=-6, LuminanceAdjustmentBlue=6, SaturationAdjustmentAqua=-6,
      SaturationAdjustmentGreen=-20, SaturationAdjustmentOrange=-6,
      ColorGradeGlobalHue=215, ColorGradeGlobalSat=7,
      SplitToningHighlightHue=200, SplitToningHighlightSaturation=4, SplitToningShadowHue=210, SplitToningShadowSaturation=12)),
  ("06 Golden Hour", "Gun batimi / gun dogumu icin sicak, isiltili ve sinematik.", SOFT_S, dict(
      Exposure2012=0.05, Contrast2012=6, Highlights2012=-38, Shadows2012=14, Blacks2012=-6,
      Vibrance=18, Clarity2012=2,
      HueAdjustmentYellow=-6, SaturationAdjustmentYellow=10, SaturationAdjustmentOrange=12, SaturationAdjustmentRed=4,
      SaturationAdjustmentBlue=-12,
      ColorGradeGlobalHue=40, ColorGradeGlobalSat=12,
      SplitToningHighlightHue=42, SplitToningHighlightSaturation=18, SplitToningShadowHue=220, SplitToningShadowSaturation=6)),
]

UNIVERSAL = [
  ("Cinematic Teal Orange", "Film gorunumu: teal golgeler, sicak tenler. Her kamerada calisir.", CINE, dict(
      Contrast2012=10, Highlights2012=-30, Shadows2012=6, Blacks2012=-6, Vibrance=12, Saturation=-4, Clarity2012=4,
      HueAdjustmentBlue=-10, SaturationAdjustmentBlue=10, HueAdjustmentAqua=-12, HueAdjustmentGreen=18,
      SaturationAdjustmentGreen=-20, SaturationAdjustmentOrange=8,
      SplitToningShadowHue=195, SplitToningShadowSaturation=20, SplitToningHighlightHue=38, SplitToningHighlightSaturation=16,
      ColorGradeBlending=60, PostCropVignetteAmount=-10)),
  ("Gece Şehir", "Gece cekimi: temiz siyahlar, canli neonlar, kontrollu isiklar.", CLEAN_S, dict(
      Contrast2012=8, Highlights2012=-35, Shadows2012=4, Blacks2012=-12, Vibrance=16, Dehaze=4,
      SaturationAdjustmentPurple=14, SaturationAdjustmentMagenta=12, SaturationAdjustmentBlue=10, SaturationAdjustmentOrange=6,
      SplitToningShadowHue=225, SplitToningShadowSaturation=12, SplitToningHighlightHue=35, SplitToningHighlightSaturation=8,
      PostCropVignetteAmount=-8)),
  ("Moody Dark", "Karamsar, mat ve sinematik; sehir, sokak, bulutlu hava.", CINE, dict(
      Exposure2012=-0.10, Contrast2012=12, Highlights2012=-30, Shadows2012=-6, Blacks2012=-6,
      Vibrance=-4, Saturation=-14, Clarity2012=6,
      HueAdjustmentGreen=20, SaturationAdjustmentGreen=-30, SaturationAdjustmentBlue=-12, SaturationAdjustmentOrange=4,
      SplitToningShadowHue=200, SplitToningShadowSaturation=14, SplitToningHighlightHue=40, SplitToningHighlightSaturation=8,
      PostCropVignetteAmount=-15)),
  ("Siyah Beyaz Sinema", "Net, yuksek kontrastli sinematik siyah-beyaz.", CRISP_S, dict(
      ConvertToGrayscale=True, Contrast2012=20, Highlights2012=-20, Shadows2012=6, Whites2012=10, Blacks2012=-14,
      Clarity2012=8, GrayMixerBlue=-20, GrayMixerOrange=12, GrayMixerRed=6, PostCropVignetteAmount=-12)),
]

LIMITS = dict(Exposure2012=(-5, 5))
def merge(base, look):
    out = dict(look)
    for k, v in base.items():
        if k in out and isinstance(v, (int, float)) and not isinstance(v, bool):
            out[k] = max(-100, min(100, out[k] + v)) if not k.startswith("Exposure") else round(out[k] + v, 2)
        else:
            out.setdefault(k, v)
    return out

P = []
for cam, (short, base) in CAMERAS.items():
    for name, desc, crv, look in LOOKS:
        P.append((cam, f"{short} {name}", desc, crv, merge(base, look)))
for name, desc, crv, look in UNIVERSAL:
    P.append(("Universal", f"UNI {name}", desc, crv, look))


# ======================= GECE SETI =======================
NIGHT_S  = [(0,0),(40,31),(128,126),(200,205),(255,255)]   # derin ama temiz siyahlar
NIGHT_CINE = [(0,8),(44,36),(128,125),(200,203),(255,250)]

NIGHT_CAMERAS = {   # gece icin kamera duzeltmeleri (videoda gurultu azaltma yok -> golgeleri fazla acmiyoruz)
  "DJI Mini 5 Pro": ("M5P", dict(Highlights2012=-15, Shadows2012=4, Dehaze=4, Texture=-6, Saturation=-4,
                                 LuminanceAdjustmentBlue=-4)),
  "DJI Osmo Pocket 3": ("OP3", dict(Highlights2012=-10, Shadows2012=6, Contrast2012=-2, Texture=-2,
                                    SaturationAdjustmentOrange=-4)),
  "Insta360 X5": ("X5", dict(Highlights2012=-15, Blacks2012=-6, Texture=-10, Clarity2012=-4, Vibrance=6, Dehaze=2)),
}

NIGHT_LOOKS = [
  ("Gece 01 Doğal", "Dogal gece: temiz siyahlar, kontrollu sokak lambalari, gercekci renkler.", NIGHT_S, dict(
      Exposure2012=0.05, Contrast2012=8, Highlights2012=-35, Shadows2012=6, Whites2012=-4, Blacks2012=-10,
      Vibrance=10, Saturation=-2, SaturationAdjustmentOrange=-6, SaturationAdjustmentYellow=-8,
      SplitToningShadowHue=225, SplitToningShadowSaturation=6)),
  ("Gece 02 Altın Şehir", "Drone sehir klasigi: altin sokaklar, derin mavi gokyuzu ve golgeler.", NIGHT_S, dict(
      Contrast2012=12, Highlights2012=-30, Shadows2012=4, Whites2012=4, Blacks2012=-12, Vibrance=14, Saturation=2, Dehaze=4,
      HueAdjustmentOrange=-4, SaturationAdjustmentOrange=14, LuminanceAdjustmentOrange=6,
      HueAdjustmentYellow=-10, SaturationAdjustmentYellow=8, LuminanceAdjustmentYellow=4,
      HueAdjustmentBlue=-8, SaturationAdjustmentBlue=14, LuminanceAdjustmentBlue=-10,
      HueAdjustmentAqua=-10, SaturationAdjustmentAqua=8,
      SplitToningShadowHue=215, SplitToningShadowSaturation=14, SplitToningHighlightHue=40, SplitToningHighlightSaturation=14,
      ColorGradeBlending=60, PostCropVignetteAmount=-8)),
  ("Gece 03 Mavi Saat", "Gun batimindan hemen sonra: koyu mavi gok, sicak sehir isiklari.", NIGHT_S, dict(
      Exposure2012=0.05, Contrast2012=10, Highlights2012=-32, Shadows2012=8, Blacks2012=-8, Vibrance=16,
      HueAdjustmentBlue=-10, SaturationAdjustmentBlue=20, LuminanceAdjustmentBlue=-6,
      HueAdjustmentAqua=-14, SaturationAdjustmentAqua=12, SaturationAdjustmentPurple=6,
      SaturationAdjustmentOrange=10, LuminanceAdjustmentOrange=6, SaturationAdjustmentYellow=6,
      ColorGradeGlobalHue=220, ColorGradeGlobalSat=4,
      SplitToningShadowHue=225, SplitToningShadowSaturation=16, SplitToningHighlightHue=45, SplitToningHighlightSaturation=10)),
  ("Gece 04 Neon Şehir", "Neon tabelalar, mor-pembe-camgobegi isiklar; modern sehir gecesi.", NIGHT_S, dict(
      Contrast2012=14, Highlights2012=-30, Shadows2012=2, Whites2012=6, Blacks2012=-14, Vibrance=20, Saturation=4, Clarity2012=4,
      HueAdjustmentPurple=6, SaturationAdjustmentPurple=22, SaturationAdjustmentMagenta=20, LuminanceAdjustmentMagenta=6,
      HueAdjustmentBlue=-6, SaturationAdjustmentBlue=16, HueAdjustmentAqua=8, SaturationAdjustmentAqua=16,
      HueAdjustmentOrange=-6, SaturationAdjustmentOrange=-10, SaturationAdjustmentYellow=-16, SaturationAdjustmentGreen=-20,
      SplitToningShadowHue=240, SplitToningShadowSaturation=14, SplitToningHighlightHue=300, SplitToningHighlightSaturation=6,
      PostCropVignetteAmount=-10)),
  ("Gece 05 Sinematik", "Film gibi gece: teal golgeler, sicak isiklar, mat ve derin.", NIGHT_CINE, dict(
      Contrast2012=10, Highlights2012=-35, Blacks2012=-6, Vibrance=4, Saturation=-10,
      HueAdjustmentGreen=20, SaturationAdjustmentGreen=-30, HueAdjustmentBlue=-12, SaturationAdjustmentBlue=6, HueAdjustmentAqua=-15,
      SaturationAdjustmentOrange=6, HueAdjustmentYellow=-8, SaturationAdjustmentYellow=-12,
      SplitToningShadowHue=195, SplitToningShadowSaturation=22, SplitToningHighlightHue=38, SplitToningHighlightSaturation=14,
      ColorGradeBlending=65, PostCropVignetteAmount=-14)),
  ("Gece 06 Beyaz Işık", "Turuncu sokak lambasi rengini temizler; beyaz, modern ve net gece.", NIGHT_S, dict(
      Contrast2012=10, Highlights2012=-30, Shadows2012=4, Blacks2012=-10, Vibrance=6, Clarity2012=2,
      HueAdjustmentOrange=6, SaturationAdjustmentOrange=-25, LuminanceAdjustmentOrange=8,
      HueAdjustmentYellow=10, SaturationAdjustmentYellow=-30, SaturationAdjustmentRed=-6, SaturationAdjustmentBlue=10,
      ColorGradeGlobalHue=220, ColorGradeGlobalSat=8)),
]

NIGHT_GROUP = "Pro Video Gece"
for cam, (short, base) in NIGHT_CAMERAS.items():
    for name, desc, crv, look in NIGHT_LOOKS:
        P.append((cam + " Gece", f"{short} {name}", desc, crv, merge(base, look)))

def curve(points):
    return "".join(f"<rdf:li>{x}, {y}</rdf:li>" for x, y in points)

def val(k, v):
    if isinstance(v, bool): return "True" if v else "False"
    if k.startswith("Exposure"): return f"{v:+.2f}"
    return str(v)

def xmp(cam, name, desc, cpts, s):
    s = dict(s)
    if any(k.startswith(("SplitToning", "ColorGrade")) for k in s):
        s.setdefault("ColorGradeBlending", 50)
        for k in ("SplitToningShadowHue","SplitToningShadowSaturation","SplitToningHighlightHue","SplitToningHighlightSaturation"):
            s.setdefault(k, 0)
    if "PostCropVignetteAmount" in s:
        for k, d in (("PostCropVignetteMidpoint",50),("PostCropVignetteFeather",70),("PostCropVignetteRoundness",0),("PostCropVignetteStyle",1)):
            s.setdefault(k, d)
    s.setdefault("ConvertToGrayscale", False)
    attrs = "\n".join(f'   crs:{k}="{val(k, v)}"' for k, v in s.items())
    alt = lambda t: f'<rdf:Alt><rdf:li xml:lang="x-default">{escape(t)}</rdf:li></rdf:Alt>'
    return f'''<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 1.000000, 0000/00/00-00:00:00        ">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
   crs:PresetType="Normal"
   crs:Cluster=""
   crs:UUID="{uuid.uuid4().hex.upper()}"
   crs:SupportsAmount2="True"
   crs:SupportsAmount="True"
   crs:SupportsColor="True"
   crs:SupportsMonochrome="True"
   crs:SupportsHighDynamicRange="True"
   crs:SupportsNormalDynamicRange="True"
   crs:SupportsSceneReferred="True"
   crs:SupportsOutputReferred="True"
   crs:RequiresRGBTables="False"
   crs:CameraModelRestriction=""
   crs:Copyright=""
   crs:ContactInfo=""
   crs:Version="15.0"
   crs:ProcessVersion="11.0"
{attrs}
   crs:ToneCurveName2012="Custom"
   crs:HasSettings="True">
   <crs:Name>{alt(name)}</crs:Name>
   <crs:ShortName>{alt("")}</crs:ShortName>
   <crs:SortName>{alt("")}</crs:SortName>
   <crs:Group>{alt(GROUP_ROOT + " - " + cam)}</crs:Group>
   <crs:Description>{alt(desc)}</crs:Description>
   <crs:ToneCurvePV2012><rdf:Seq>{curve(cpts)}</rdf:Seq></crs:ToneCurvePV2012>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
'''

TR = str.maketrans("İıŞşĞğÜüÖöÇç", "IiSsGgUuOoCc")
def fname(name): return name.translate(TR).replace(" ", "_")

def main(OUT):
    os.makedirs(OUT, exist_ok=True)
    with zipfile.ZipFile(os.path.join(OUT, "Pro-Video-Presets-XMP.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for cam, name, desc, c, s in P:
            d = os.path.join(OUT, "xmp", cam.replace(" ", "-")); os.makedirs(d, exist_ok=True)
            data = xmp(cam, name, desc, c, s)
            open(os.path.join(d, fname(name) + ".xmp"), "w", encoding="utf-8").write(data)
            z.writestr(fname(name) + ".xmp", data)
    print(len(P), "XMP presets")

if __name__ == "__main__":
    main(sys.argv[1])
