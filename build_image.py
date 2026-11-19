#!/usr/bin/env python3
"""Build entry.png: a 1024x1024 infographic summing up world news of Thu 19 Nov 2026.
Drawn with PIL (sharp vector text, no AI image generation, so no garbled words).
Deterministic: same input -> same bytes every run.
"""
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28

INK = (20, 33, 61)          # dark navy text
NAVY = (16, 42, 67)         # header background
RED = (192, 57, 43)         # date band / lead accent
PAPER = (251, 248, 242)     # warm paper background
CARD = (255, 255, 255)
BORDER = (214, 219, 224)
MUTED = (90, 100, 114)
LEAD_BG = (253, 236, 234)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to max width in pixels; returns list of lines."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# ---------- icons (simple geometric pictograms, drawn in accent colour) ----------
def icon_rocket(d, box, c):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    d.polygon([(cx - 9, y1 - 8), (cx + 9, y1 - 8), (cx, y1 + 2)], fill=(245, 158, 11))
    d.rounded_rectangle([cx - 13, y0 + 14, cx + 13, y1 - 12], radius=10, fill=c)
    d.polygon([(cx - 13, y0 + 16), (cx + 13, y0 + 16), (cx, y0)], fill=c)
    d.ellipse([cx - 6, y0 + 30, cx + 6, y0 + 42], fill=(255, 255, 255))
    d.polygon([(cx - 13, y1 - 26), (cx - 26, y1 - 6), (cx - 13, y1 - 12)], fill=c)
    d.polygon([(cx + 13, y1 - 26), (cx + 26, y1 - 6), (cx + 13, y1 - 12)], fill=c)


def icon_flags(d, box, c):
    x0, y0, x1, y1 = box
    for i, col in enumerate([(192, 57, 43), (37, 99, 235), (21, 128, 61)]):
        px = x0 + 8 + i * 22
        d.line([(px, y0 + 22), (px, y1 - 16)], fill=INK, width=5)
        d.polygon([(px, y0 + 22), (px + 21, y0 + 32), (px, y0 + 42)], fill=col)
    # ground line
    d.line([(x0 + 4, y1 - 14), (x1 - 4, y1 - 14)], fill=INK, width=4)


def icon_chart(d, box, c):
    x0, y0, x1, y1 = box
    # rising bars
    base = y1 - 10
    for i, h in enumerate((18, 30, 44)):
        bx = x0 + 8 + i * 18
        d.rectangle([bx, base - h, bx + 12, base], fill=c)
    # arrow up-right
    d.line([(x0 + 6, base - 6), (x1 - 8, y0 + 10)], fill=(21, 128, 61), width=5)
    d.polygon([(x1 - 8, y0 + 10), (x1 - 20, y0 + 12), (x1 - 10, y0 + 22)], fill=(21, 128, 61))


def icon_tank(d, box, c):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    # barrel
    d.line([(cx + 4, y0 + 22), (x1 - 2, y0 + 18)], fill=c, width=5)
    # turret
    d.rounded_rectangle([cx - 12, y0 + 12, cx + 12, y0 + 30], radius=5, fill=c)
    # body
    d.rounded_rectangle([x0 + 4, y0 + 30, x1 - 4, y1 - 14], radius=6, fill=c)
    # wheels
    for i in range(3):
        wx = x0 + 16 + i * 18
        d.ellipse([wx - 6, y1 - 14, wx + 6, y1 - 2], fill=INK)


def icon_scales(d, box, c):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    # pole + base
    d.line([(cx, y0 + 8), (cx, y1 - 10)], fill=c, width=5)
    d.line([(x0 + 8, y1 - 6), (x1 - 8, y1 - 6)], fill=c, width=5)
    # beam
    d.line([(x0 + 6, y0 + 14), (x1 - 6, y0 + 14)], fill=c, width=5)
    # pans
    for px in (x0 + 12, x1 - 12):
        d.line([(px, y0 + 14), (px, y0 + 30)], fill=c, width=3)
        d.pieslice([px - 13, y0 + 28, px + 13, y0 + 48], start=0, end=180, fill=c)


def icon_controller(d, box, c):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rounded_rectangle([x0 + 2, y0 + 12, x1 - 2, y1 - 12], radius=14, fill=c)
    # d-pad
    d.rectangle([x0 + 12, cy - 4, x0 + 30, cy + 4], fill=(255, 255, 255))
    d.rectangle([x0 + 17, cy - 9, x0 + 25, cy + 9], fill=(255, 255, 255))
    # buttons
    d.ellipse([x1 - 30, cy - 12, x1 - 20, cy - 2], fill=(255, 255, 255))
    d.ellipse([x1 - 20, cy + 2, x1 - 10, cy + 12], fill=(255, 255, 255))


def icon_euro(d, box, c):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.ellipse([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=c)
    f = font(SANS_B, 40)
    t = "\u20ac"
    tw = d.textlength(t, font=f)
    th = f.size
    d.text((cx - tw / 2, cy - th / 2 - 4), t, font=f, fill=(255, 255, 255))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # outer border
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=3)

    # ---------- masthead ----------
    d.rectangle([MARGIN, MARGIN, W - MARGIN, MARGIN + 92], fill=NAVY)
    gx, gy = MARGIN + 18, MARGIN + 16
    d.ellipse([gx, gy, gx + 60, gy + 60], outline=(255, 255, 255), width=4)
    d.ellipse([gx + 18, gy, gx + 42, gy + 60], outline=(255, 255, 255), width=3)
    d.line([(gx, gy + 30), (gx + 60, gy + 30)], fill=(255, 255, 255), width=3)
    d.arc([gx - 6, gy + 8, gx + 66, gy + 52], start=200, end=340, fill=(255, 255, 255), width=3)
    f_mast = font(SERIF_B, 58)
    d.text((MARGIN + 96, MARGIN + 16), "WORLD NEWS", font=f_mast, fill=(255, 255, 255))
    f_sub = font(SANS_B, 21)
    d.text((MARGIN + 98, MARGIN + 66), "THE DAY IN ONE IMAGE", font=f_sub, fill=(180, 200, 220))

    # ---------- date band ----------
    y = MARGIN + 92 + 10
    d.rectangle([MARGIN, y, W - MARGIN, y + 52], fill=RED)
    f_date = font(SANS_B, 30)
    date_txt = "THURSDAY, 19 NOVEMBER 2026"
    tw = d.textlength(date_txt, font=f_date)
    d.text(((W - tw) / 2, y + 10), date_txt, font=f_date, fill=(255, 255, 255))

    # ---------- lead story ----------
    y = y + 52 + 12
    lead_h = 210
    d.rounded_rectangle([MARGIN, y, W - MARGIN, y + lead_h], radius=10, fill=LEAD_BG,
                        outline=RED, width=2)
    ix0, iy0, ix1, iy1 = MARGIN + 16, y + 16, MARGIN + 132, y + lead_h - 16
    d.rounded_rectangle([ix0, iy0, ix1, iy1], radius=8, fill=(255, 255, 255))
    icon_flags(d, (ix0 + 18, iy0 + 14, ix1 - 18, iy1 - 14), RED)
    tx = MARGIN + 152
    f_kick = font(SANS_B, 20)
    d.text((tx, y + 18), "DIPLOMACY  ·  SHENZHEN", font=f_kick, fill=RED)
    f_lead = font(SANS_B, 34)
    lead_head = "Trump, Xi and Putin meet in Shenzhen"
    lines = wrap(d, lead_head, f_lead, W - MARGIN - tx - 18)
    ly = draw_lines(d, lines, tx, y + 48, f_lead, INK, 42)
    f_body = font(SANS, 24)
    lead_sum = ("First three-way summit of the U.S., Chinese and Russian leaders, "
                "at the APEC meeting. Nuclear arms control tops the agenda.")
    lines = wrap(d, lead_sum, f_body, W - MARGIN - tx - 18)
    draw_lines(d, lines, tx, ly + 6, f_body, (60, 68, 80), 31)

    # ---------- grid of six stories ----------
    stories = [
        ("TECH", "Anthropic's $81.3B IPO, the biggest ever",
         "Priced at $83 a share, valuing it near $1.5 trillion. Trading starts today.",
         (37, 99, 235), icon_chart),
        ("MIDDLE EAST", "Israeli tanks cross Gaza ceasefire line",
         "A rare ground raid beyond the Yellow Line sent displaced families fleeing.",
         (153, 27, 27), icon_tank),
        ("LAW", "UN court rules on Myanmar genocide case",
         "The court delivers its verdict in The Gambia's case over the 2017 crackdown.",
         (124, 58, 237), icon_scales),
        ("GAMES", "GTA VI rolls out worldwide",
         "Gamers enter Vice City as Grand Theft Auto VI begins its global launch.",
         (21, 128, 61), icon_controller),
        ("SPACE", "Voyager 1 reaches one light-day",
         "After 49 years in space, the probe is the first object one light-day from Earth.",
         (14, 116, 144), icon_rocket),
        ("EUROPE", "EU plans \u20ac45B loan for Ukraine",
         "A loan to cover Kyiv's budget, to be repaid once Russia pays reparations.",
         (194, 65, 12), icon_euro),
    ]
    gx0 = MARGIN
    gy0 = y + lead_h + 12
    cw = (W - 2 * MARGIN - 14) // 2
    ch = 148
    f_kick2 = font(SANS_B, 17)
    f_head2 = font(SANS_B, 25)
    f_body2 = font(SANS, 20)
    for i, (kick, head, summ, accent, icon_fn) in enumerate(stories):
        col, row = i % 2, i // 2
        cx0 = gx0 + col * (cw + 14)
        cy0 = gy0 + row * (ch + 12)
        d.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + ch], radius=8, fill=CARD,
                            outline=BORDER, width=2)
        t = 12
        d.rounded_rectangle([cx0 + t, cy0 + t, cx0 + t + 74, cy0 + ch - t], radius=6,
                            fill=(239, 243, 247))
        icon_fn(d, (cx0 + t + 8, cy0 + t + 8, cx0 + t + 66, cy0 + ch - t - 8), accent)
        tx2 = cx0 + t + 86
        d.text((tx2, cy0 + 12), kick, font=f_kick2, fill=accent)
        lines = wrap(d, head, f_head2, cw - t - 86 - 12)
        ly2 = draw_lines(d, lines, tx2, cy0 + 36, f_head2, INK, 30)
        lines = wrap(d, summ, f_body2, cw - t - 86 - 12)
        draw_lines(d, lines, tx2, ly2 + 3, f_body2, MUTED, 25)

    # ---------- "also" strip + sources ----------
    y = gy0 + 3 * ch + 2 * 12 + 12
    d.rounded_rectangle([MARGIN, y, W - MARGIN, y + 64], radius=8, fill=(239, 243, 247))
    f_also = font(SANS_B, 19)
    f_also2 = font(SANS, 19)
    d.text((MARGIN + 16, y + 9), "Also: ", font=f_also, fill=INK)
    aw = d.textlength("Also: ", font=f_also)
    also = ("Van Gogh sells for a record $190.4m  ·  Canada rethinks its China ties  ·  "
            "Cyclone Akvan nears India's east coast")
    lines = wrap(d, also, f_also2, W - 2 * MARGIN - 32 - aw)
    draw_lines(d, lines, MARGIN + 16 + aw, y + 9, f_also2, INK, 25)

    y = y + 64 + 10
    f_src = font(SANS, 18)
    src = "Sources: Reuters · Associated Press · BBC · The New York Times — 19 November 2026"
    sw = d.textlength(src, font=f_src)
    d.text(((W - sw) / 2, y), src, font=f_src, fill=MUTED)

    return img


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    im = build()
    im.save(out, "PNG", optimize=True)
    print("saved", out, im.size)
