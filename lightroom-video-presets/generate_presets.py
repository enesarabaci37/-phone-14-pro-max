import uuid, os, zipfile, sys
from xml.sax.saxutils import escape
OUT = sys.argv[1]
GROUP_ROOT = "Video Pro"

def curve(points):
    return "".join(f"<rdf:li>{x}, {y}</rdf:li>" for x, y in points)

LOG = [(0,0),(22,0),(60,34),(128,128),(196,222),(236,255),(255,255)]      # D-Log M -> Rec709 approx
ILOG = [(0,0),(18,0),(58,36),(128,130),(200,224),(240,255),(255,255)]     # I-Log -> Rec709 approx
SOFT_S = [(0,0),(64,58),(128,128),(192,200),(255,255)]
FADE = [(0,22),(60,62),(128,130),(196,204),(255,245)]
MOODY = [(0,14),(64,54),(128,124),(192,198),(255,248)]

P = []
def add(cam, name, desc, curve_pts=None, **s):
    P.append((cam, name, desc, curve_pts, s))

# ---------- DJI Mini 5 Pro (D-Log M) ----------
add("DJI Mini 5 Pro", "M5P 01 - D-Log M Natural",
    "D-Log M -> dogal Rec.709 donusumu. Tum duzenlemelerin temeli.", LOG,
    Exposure2012=0.10, Contrast2012=12, Highlights2012=-20, Shadows2012=10, Whites2012=8, Blacks2012=-8,
    Vibrance=22, Saturation=14, Clarity2012=4, Dehaze=4,
    SaturationAdjustmentBlue=8, LuminanceAdjustmentBlue=-6, SaturationAdjustmentGreen=-4)
add("DJI Mini 5 Pro", "M5P 02 - Cinematic Teal Orange",
    "Hava cekimleri icin sinematik teal-orange; gokyuzu derin, ten/kum sicak.", LOG,
    Contrast2012=18, Highlights2012=-30, Shadows2012=6, Whites2012=4, Blacks2012=-12,
    IncrementalTemperature=4, Vibrance=18, Saturation=8, Dehaze=8,
    HueAdjustmentBlue=-10, SaturationAdjustmentBlue=14, LuminanceAdjustmentBlue=-14,
    HueAdjustmentAqua=-12, SaturationAdjustmentAqua=10, HueAdjustmentGreen=18, SaturationAdjustmentGreen=-22,
    SaturationAdjustmentOrange=10, HueAdjustmentOrange=-4,
    SplitToningShadowHue=200, SplitToningShadowSaturation=22, SplitToningHighlightHue=38, SplitToningHighlightSaturation=18,
    SplitToningBalance=10, ColorGradeBlending=60, PostCropVignetteAmount=-12)
add("DJI Mini 5 Pro", "M5P 03 - Golden Hour",
    "Gun batimi / gun dogumu hava cekimleri icin sicak, parlak tonlar.", LOG,
    Exposure2012=0.15, Contrast2012=10, Highlights2012=-35, Shadows2012=14, Blacks2012=-6,
    IncrementalTemperature=14, IncrementalTint=4, Vibrance=20, Saturation=6, Dehaze=6,
    SaturationAdjustmentOrange=14, SaturationAdjustmentYellow=10, HueAdjustmentYellow=-6, LuminanceAdjustmentOrange=6,
    SaturationAdjustmentBlue=-6, SplitToningHighlightHue=42, SplitToningHighlightSaturation=22,
    SplitToningShadowHue=25, SplitToningShadowSaturation=8)
add("DJI Mini 5 Pro", "M5P 04 - Epic Landscape",
    "Daglar, deniz, sehir panoramalari icin net ve derin, punch'li gorunum.", LOG,
    Contrast2012=20, Highlights2012=-40, Shadows2012=18, Whites2012=12, Blacks2012=-14,
    Vibrance=28, Saturation=6, Clarity2012=10, Dehaze=14, Texture=8,
    SaturationAdjustmentBlue=16, LuminanceAdjustmentBlue=-18, SaturationAdjustmentGreen=8, HueAdjustmentGreen=-6,
    LuminanceAdjustmentGreen=-6, SaturationAdjustmentAqua=12)
add("DJI Mini 5 Pro", "M5P 05 - Normal Profile Punch",
    "Normal (Rec.709) renk profiliyle cekilmis drone videolari icin hafif iyilestirme.", SOFT_S,
    Contrast2012=8, Highlights2012=-18, Shadows2012=10, Vibrance=14, Saturation=2, Dehaze=6, Clarity2012=4,
    LuminanceAdjustmentBlue=-8, SaturationAdjustmentBlue=6)

# ---------- DJI Osmo Pocket 3 (D-Log M) ----------
add("DJI Osmo Pocket 3", "OP3 01 - D-Log M Natural",
    "Pocket 3 D-Log M -> dogal Rec.709. Ten renklerini korur.", LOG,
    Exposure2012=0.08, Contrast2012=10, Highlights2012=-18, Shadows2012=8, Whites2012=6, Blacks2012=-6,
    Vibrance=20, Saturation=10, Clarity2012=2,
    SaturationAdjustmentOrange=-4, LuminanceAdjustmentOrange=6, HueAdjustmentRed=4)
add("DJI Osmo Pocket 3", "OP3 02 - Vlog Warm Skin",
    "Vlog / yuz cekimleri icin sicak, temiz ve parlak ten tonu.", LOG,
    Exposure2012=0.15, Contrast2012=6, Highlights2012=-24, Shadows2012=16, Blacks2012=-4,
    IncrementalTemperature=6, IncrementalTint=3, Vibrance=16, Saturation=4, Clarity2012=-6, Texture=-8,
    HueAdjustmentOrange=-3, SaturationAdjustmentOrange=-6, LuminanceAdjustmentOrange=10,
    LuminanceAdjustmentRed=4, SaturationAdjustmentRed=-4,
    SplitToningHighlightHue=40, SplitToningHighlightSaturation=10)
add("DJI Osmo Pocket 3", "OP3 03 - Moody Film",
    "Sokak / gece / sehir cekimleri icin karamsar, filmik gorunum.", MOODY,
    Contrast2012=14, Highlights2012=-28, Shadows2012=-4, Blacks2012=-10,
    IncrementalTemperature=-4, Vibrance=-6, Saturation=-10, Clarity2012=6,
    HueAdjustmentGreen=24, SaturationAdjustmentGreen=-30, SaturationAdjustmentBlue=-10, HueAdjustmentBlue=-8,
    SaturationAdjustmentOrange=4,
    SplitToningShadowHue=195, SplitToningShadowSaturation=18, SplitToningHighlightHue=35, SplitToningHighlightSaturation=12,
    ColorGradeBlending=70, PostCropVignetteAmount=-18, GrainAmount=10)
add("DJI Osmo Pocket 3", "OP3 04 - Clean Travel",
    "Seyahat vlog'lari icin canli ama dogal renkler.", LOG,
    Exposure2012=0.10, Contrast2012=14, Highlights2012=-26, Shadows2012=12, Whites2012=8, Blacks2012=-10,
    Vibrance=26, Saturation=8, Dehaze=4, Clarity2012=4,
    SaturationAdjustmentBlue=10, SaturationAdjustmentAqua=10, LuminanceAdjustmentOrange=4)

# ---------- Insta360 X5 (I-Log / Standard) ----------
add("Insta360 X5", "X5 01 - I-Log Natural",
    "I-Log -> dogal Rec.709 donusumu. 360 ve reframe videolar icin temel.", ILOG,
    Exposure2012=0.10, Contrast2012=14, Highlights2012=-22, Shadows2012=10, Whites2012=8, Blacks2012=-8,
    Vibrance=24, Saturation=12, Clarity2012=4, Dehaze=4)
add("Insta360 X5", "X5 02 - Action Vivid",
    "Motor, kayak, bisiklet, su sporlari icin enerjik ve canli renkler.", ILOG,
    Contrast2012=22, Highlights2012=-30, Shadows2012=14, Whites2012=12, Blacks2012=-14,
    Vibrance=32, Saturation=12, Clarity2012=10, Dehaze=10, Texture=6,
    SaturationAdjustmentBlue=16, SaturationAdjustmentAqua=14, SaturationAdjustmentOrange=10, SaturationAdjustmentRed=6,
    LuminanceAdjustmentBlue=-10)
add("Insta360 X5", "X5 03 - Standard Clean Bright",
    "Standart/Vivid profil ile cekilmis X5 videolari icin parlak, temiz duzeltme.", SOFT_S,
    Exposure2012=0.12, Contrast2012=4, Highlights2012=-22, Shadows2012=14, Blacks2012=-4,
    Vibrance=10, Saturation=-2, Dehaze=4, Clarity2012=2,
    SaturationAdjustmentGreen=-6, LuminanceAdjustmentOrange=6)
add("Insta360 X5", "X5 04 - Snow & Sky",
    "Kar, gokyuzu ve deniz sahneleri icin; mavi kaymayi ve gri kari duzeltir.", ILOG,
    Exposure2012=0.20, Contrast2012=16, Highlights2012=-34, Shadows2012=10, Whites2012=14, Blacks2012=-10,
    IncrementalTemperature=3, Vibrance=18, Saturation=4, Dehaze=10,
    SaturationAdjustmentBlue=14, LuminanceAdjustmentBlue=-12, SaturationAdjustmentAqua=8)

# ---------- Universal ----------
add("Universal", "UNI 01 - Night City",
    "Gece sehir cekimleri: neon renkleri vurgular, golgeleri temiz tutar.", SOFT_S,
    Contrast2012=12, Highlights2012=-30, Shadows2012=6, Blacks2012=-14,
    IncrementalTemperature=-8, IncrementalTint=6, Vibrance=18, Saturation=4, Dehaze=6,
    SaturationAdjustmentPurple=16, SaturationAdjustmentMagenta=12, SaturationAdjustmentBlue=10, SaturationAdjustmentOrange=8,
    SplitToningShadowHue=230, SplitToningShadowSaturation=16, SplitToningHighlightHue=30, SplitToningHighlightSaturation=10,
    PostCropVignetteAmount=-10)
add("Universal", "UNI 02 - Faded Film",
    "Retro / analog film hissi: soluk siyahlar, yumusak renkler, hafif grain.", FADE,
    Contrast2012=-6, Highlights2012=-16, Shadows2012=8,
    IncrementalTemperature=5, Vibrance=-8, Saturation=-12,
    HueAdjustmentGreen=16, SaturationAdjustmentGreen=-18, SaturationAdjustmentBlue=-12,
    SplitToningShadowHue=180, SplitToningShadowSaturation=10, SplitToningHighlightHue=45, SplitToningHighlightSaturation=14,
    GrainAmount=18, PostCropVignetteAmount=-8)
add("Universal", "UNI 03 - B&W Cinema",
    "Yuksek kontrastli sinematik siyah-beyaz.", SOFT_S,
    ConvertToGrayscale=True, Contrast2012=24, Highlights2012=-20, Shadows2012=6, Whites2012=10, Blacks2012=-16,
    Clarity2012=10, GrayMixerBlue=-20, GrayMixerOrange=12, GrayMixerRed=6, GrainAmount=12, PostCropVignetteAmount=-15)

def fmt(k, v):
    if isinstance(v, bool): return f'crs:{k}="{"True" if v else "False"}"'
    if k.startswith("Exposure"): return f'crs:{k}="{v:+.2f}"'
    return f'crs:{k}="{v:+d}"' if v != 0 and not k.endswith("Hue") else f'crs:{k}="{v}"'

def xmp(cam, name, desc, cpts, s):
    s = dict(s)
    attrs = []
    if any(k.startswith("Incremental") for k in s):
        attrs.append('crs:WhiteBalance="Custom"')
    if any(k.startswith(("SplitToning","ColorGrade")) for k in s):
        s.setdefault("ColorGradeBlending", 50)
        for k in ("SplitToningShadowHue","SplitToningShadowSaturation","SplitToningHighlightHue","SplitToningHighlightSaturation"):
            s.setdefault(k, 0)
    if "GrainAmount" in s:
        s.setdefault("GrainSize", 25); s.setdefault("GrainFrequency", 50)
    if "PostCropVignetteAmount" in s:
        s.setdefault("PostCropVignetteMidpoint", 50); s.setdefault("PostCropVignetteFeather", 70)
        s.setdefault("PostCropVignetteRoundness", 0); s.setdefault("PostCropVignetteStyle", 1)
    bw = s.pop("ConvertToGrayscale", False)
    attrs.append(f'crs:ConvertToGrayscale="{"True" if bw else "False"}"')
    for k, v in s.items():
        if k in ("ColorGradeBlending","GrainSize","GrainFrequency","PostCropVignetteMidpoint",
                 "PostCropVignetteFeather","PostCropVignetteRoundness","PostCropVignetteStyle") or k.endswith(("Hue","Saturation")) and k.startswith("SplitToning"):
            attrs.append(f'crs:{k}="{v}"')
        else:
            attrs.append(fmt(k, v))
    curve_xml = ""
    if cpts:
        attrs.append('crs:ToneCurveName2012="Custom"')
        curve_xml = f"<crs:ToneCurvePV2012><rdf:Seq>{curve(cpts)}</rdf:Seq></crs:ToneCurvePV2012>"
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
   {chr(10).join("   "+a for a in attrs).lstrip()}
   crs:HasSettings="True">
   <crs:Name>{alt(name)}</crs:Name>
   <crs:ShortName>{alt("")}</crs:ShortName>
   <crs:SortName>{alt("")}</crs:SortName>
   <crs:Group>{alt(GROUP_ROOT + " - " + cam)}</crs:Group>
   <crs:Description>{alt(desc)}</crs:Description>
   {curve_xml}
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
'''

os.makedirs(OUT, exist_ok=True)
zpath = os.path.join(OUT, "Video-Pro-Presets.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for cam, name, desc, c, s in P:
        d = os.path.join(OUT, "xmp", cam.replace(" ", "-"))
        os.makedirs(d, exist_ok=True)
        fn = name.replace(" ", "_").replace("&", "and") + ".xmp"
        data = xmp(cam, name, desc, c, s)
        open(os.path.join(d, fn), "w").write(data)
        z.writestr(fn, data)
print(len(P), "presets ->", zpath)
