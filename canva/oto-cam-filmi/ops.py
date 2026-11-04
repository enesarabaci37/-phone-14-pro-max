import json, sys

RED, GREEN, TEAL, GRAY, DARK, LIGHT, WHITE = "#CA4C4B", "#A4B542", "#65ADA4", "#454B52", "#262A2F", "#F6F7F4", "#FFFFFF"
LOGO, LOGO_W = "MAHZ9jrn9As", "MAHZ9l7Bu2Q"  # LOGO_W = beyaz yazılı? (aşağıda düzeltilir)
LOGO_COLOR, LOGO_WHITE = "MAHZ9l7Bu2Q", "MAHZ9jrn9As"
R = "M0 0H64V64H0z"
M = 80
N = 10
PHONE = "0534 080 26 79"


def rect(pid, top, left, w, h, color, rnd=0, op=None):
    d = {"type": "insert_shape", "page_id": pid, "top": top, "left": left, "width": w, "height": h,
         "path": R, "view_box_width": 64, "view_box_height": 64, "color": color}
    if rnd:
        d["corner_rounding"] = rnd
    if op is not None:
        d["opacity"] = op
    return d


def text(pid, t, top, left, width=None):
    d = {"type": "add_text", "page_id": pid, "text": t, "top": top, "left": left}
    if width:
        d["width"] = width
    return d


def stripe(pid):
    w = 1080 / 3
    return [rect(pid, 0, i * w, w + 1, 12, c) for i, c in enumerate([RED, GREEN, TEAL])]


def logo(pid, dark, top=48, width=200):
    return {"type": "insert_fill", "page_id": pid, "asset_type": "image",
            "asset_id": LOGO_WHITE if dark else LOGO_COLOR, "alt_text": "Arabacı Reklam logosu",
            "top": top, "left": M, "width": width, "height": round(width * 749 / 1004)}


def footer(pid, idx, dark, accent):
    ops = []
    y = 1218
    pill_bg = WHITE if dark else GRAY
    ops.append(rect(pid, y, M, 410, 76, pill_bg, rnd=38))
    ops.append(rect(pid, y + 16, M + 22, 44, 44, accent, rnd=22))
    ops.append(text(pid, "TEL", y + 28, M + 26, 40))
    ops.append(text(pid, PHONE, y + 15, M + 84, 320))
    seg, gap = 24, 8
    tw = N * seg + (N - 1) * gap
    x0 = 1080 - M - tw
    off = "#FFFFFF" if dark else "#C9CCCF"
    for i in range(N):
        ops.append(rect(pid, y + 18, x0 + i * (seg + gap), seg, 7, accent if i <= idx else off, rnd=3,
                        op=None if i <= idx else (0.35 if dark else 1)))
    left = N - idx - 1
    ops.append(text(pid, f"{idx + 1}/{N}  ·  " + ("Son" if left == 0 else f"{left} kaldı"), y + 36, x0 - 20, tw + 20))
    return ops


if __name__ == "__main__":
    print(json.dumps(footer("X", 0, True, TEAL))[:200])
