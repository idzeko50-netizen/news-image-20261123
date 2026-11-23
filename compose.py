#!/usr/bin/env python3
"""Compose the news-image-20261123 entry: a newspaper front page for
Monday 23 November 2026. Forty verified stories: 4 large + 12 small
illustrated panels, a 24-item index, a world map with numbered pins, a
number strip, a region bar and a DATE CHECK box. Every illustration is
drawn in code with PIL; no photographs, no downloaded images.
Run: python3 compose.py  ->  writes entry/entry.png"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 16  # side margin
PAPER = (247, 241, 227)
INK = (23, 19, 14)
RED = (179, 39, 30)
RED_DK = (140, 28, 22)
PANEL = (255, 253, 246)
GREY = (90, 84, 74)
RULE = (60, 54, 46)
WHITE = (255, 255, 255)
BLUE = (38, 84, 150)
GREEN = (46, 125, 70)
GOLD = (214, 164, 48)
SKY = (168, 205, 225)
SEA = (72, 130, 170)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SERIF = FD + "DejaVuSerif.ttf"
SERIF_I = FD + "DejaVuSerif.ttf"  # no italic face installed on this VM; use regular serif
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    """Wrap text to fit width; return list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, x, y, fnt, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit(d, text, fnt, width, max_lines, what):
    lines = wrap(d, text, fnt, width)
    assert len(lines) <= max_lines, "%s wraps to %d lines: %r" % (what, len(lines), text)
    return lines


def panel_box(d, box, fill=PANEL):
    d.rectangle(box, fill=fill, outline=RULE, width=1)


def paint_scene(box, painter):
    """Paint a scene into a temp image clipped to the box, return the image."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    img = Image.new("RGB", (w, h), PAPER)
    td = ImageDraw.Draw(img)
    painter(td, w, h)
    return img


def ground(td, w, h, y, col):
    td.rectangle((0, y, w, h), fill=col)


# ------------------------------------------------------------------ scenes
# Each painter draws a flat vector-style scene into a (w, h) box.

def sc_cop31(td, w, h):
    td.rectangle((0, 0, w, h), fill=SKY)
    td.ellipse((w // 2 - 34, 12, w // 2 + 34, 80), fill=(96, 160, 96))
    td.ellipse((w // 2 - 22, 26, w // 2 + 6, 44), fill=(140, 190, 140))
    td.ellipse((w // 2 + 2, 52, w // 2 + 26, 70), fill=(140, 190, 140))
    td.rectangle((w // 2 - 34, 44, w // 2 + 34, 48), fill=RED_DK)
    td.line((w // 2 - 30, 20, w // 2 + 30, 74), fill=RED, width=4)
    ground(td, w, h, h - 16, (190, 170, 120))
    td.text((8, h - 14), "ANTALYA", font=font(SANS_B, 11), fill=INK)


def sc_dems(td, w, h):
    td.rectangle((0, 0, w, h), fill=(235, 238, 245))
    bx, bw = 18, 16
    heights = [18, 30, 44, 62]
    for i, hh in enumerate(heights):
        td.rectangle((bx + i * (bw + 8), h - 18 - hh, bx + i * (bw + 8) + bw, h - 18), fill=BLUE)
    td.rectangle((bx + 3 * (bw + 8), h - 18 - 62, bx + 3 * (bw + 8) + bw, h - 18), fill=RED)
    td.text((bx, 8), "258", font=font(SANS_B, 20), fill=BLUE)
    ground(td, w, h, h - 18, (200, 200, 200))


def sc_trump(td, w, h):
    td.rectangle((0, 0, w, h), fill=(240, 235, 220))
    td.rectangle((w // 2 - 30, h - 34, w // 2 + 30, h - 8), fill=(90, 60, 50))
    td.rectangle((w // 2 - 44, h - 44, w // 2 + 44, h - 34), fill=(70, 45, 38))
    td.line((w // 2, h - 44, w // 2 + 26, h - 62), fill=INK, width=3)
    td.ellipse((w // 2 + 22, h - 66, w // 2 + 30, h - 58), fill=INK)
    td.rectangle((w - 52, 8, w - 8, 34), fill=WHITE, outline=RED, width=2)
    td.text((w - 46, 12), "JAN 1", font=font(SANS_B, 12), fill=RED)


def sc_poland(td, w, h):
    td.rectangle((0, 0, w, h), fill=(225, 232, 240))
    for i, x in enumerate((w // 4, w // 2, 3 * w // 4)):
        td.line((x, h - 14, x + 14, 18 + i * 6), fill=GREY, width=2)
        td.polygon([(x + 14, 18 + i * 6), (x + 6, 30 + i * 6), (x + 22, 30 + i * 6)], fill=RED)
    td.ellipse((8, h - 30, 44, h - 8), fill=(255, 255, 255), outline=RED, width=2)
    td.text((16, h - 26), "PL", font=font(SANS_B, 12), fill=RED)
    td.text((w - 58, h - 16), "NATO", font=font(SANS_B, 11), fill=BLUE)


def sc_ship(td, w, h):
    td.rectangle((0, 0, w, h), fill=(200, 215, 225))
    td.rectangle((0, h - 26, w, h), fill=SEA)
    td.rectangle((w // 2 - 46, h - 52, w // 2 + 46, h - 26), fill=(70, 70, 78))
    td.rectangle((w // 2 - 20, h - 66, w // 2 + 8, h - 52), fill=(90, 90, 98))
    td.polygon([(w // 2 - 8, h - 66), (w // 2 + 2, h - 88), (w // 2 + 12, h - 66)], fill=(240, 120, 30))
    td.polygon([(w // 2 + 2, h - 88), (w // 2 + 16, h - 70), (w // 2 + 22, h - 84)], fill=(250, 180, 40))
    td.text((8, 8), "BENGHAZI", font=font(SANS_B, 11), fill=INK)


def sc_block(td, w, h):
    td.rectangle((0, 0, w, h), fill=(228, 222, 210))
    td.rectangle((w // 2 - 40, 18, w // 2 + 40, h - 14), fill=(150, 140, 125))
    td.polygon([(w // 2 + 40, 18), (w // 2 + 40, h - 14), (w // 2 + 4, h - 14), (w // 2 + 22, 46)], fill=(110, 100, 88))
    for ry in (30, 52, 74):
        for rx in (w // 2 - 30, w // 2 - 8):
            td.rectangle((rx, ry, rx + 12, ry + 10), fill=(60, 55, 48))
    td.polygon([(w // 2 - 40, h - 14), (w // 2 - 8, h - 14), (w // 2 - 24, h - 34)], fill=(90, 82, 70))
    td.text((8, h - 14), "DYMER", font=font(SANS_B, 11), fill=INK)


def sc_market(td, w, h):
    td.rectangle((0, 0, w, h), fill=(245, 240, 232))
    pts = [(10, 14), (30, 20), (50, 18), (70, 32), (90, 38), (110, 52), (130, 58)]
    td.line(pts, fill=RED, width=4)
    td.ellipse((126, 54, 134, 62), fill=RED)
    td.text((10, 4), "-8.6%", font=font(SANS_B, 18), fill=RED)
    td.ellipse((w - 34, h - 34, w - 8, h - 8), fill=GOLD, outline=(150, 110, 20), width=2)
    td.text((w - 29, h - 30), "B", font=font(SANS_B, 14), fill=(120, 85, 10))


def sc_india(td, w, h):
    td.rectangle((0, 0, w, h), fill=(235, 245, 235))
    pts = [(10, 56), (34, 50), (58, 54), (82, 38), (106, 28), (130, 14)]
    td.line(pts, fill=GREEN, width=4)
    td.polygon([(130, 14), (122, 16), (130, 24)], fill=GREEN)
    td.text((10, 4), "+12%", font=font(SANS_B, 18), fill=GREEN)


def sc_gaza(td, w, h):
    td.rectangle((0, 0, w, h), fill=(225, 220, 205))
    td.rectangle((0, h - 24, w, h), fill=SEA)
    td.rectangle((w // 2 - 52, h - 48, w // 2 + 52, h - 24), fill=(180, 60, 50))
    td.rectangle((w // 2 - 30, h - 64, w // 2 - 6, h - 48), fill=(200, 200, 200))
    td.polygon([(w // 2 + 20, h - 64), (w // 2 + 30, h - 92), (w // 2 + 40, h - 64)], fill=(120, 120, 120))
    td.polygon([(w // 2 + 30, h - 92), (w // 2 + 44, h - 78), (w // 2 + 48, h - 92)], fill=(90, 90, 90))
    td.text((8, 8), "GULF", font=font(SANS_B, 11), fill=INK)


def sc_iranuk(td, w, h):
    td.rectangle((0, 0, w, h), fill=(232, 236, 242))
    td.rectangle((w // 2 - 48, h - 46, w // 2 + 48, h - 22), fill=(80, 95, 120))
    td.rectangle((w // 2 - 24, h - 62, w // 2 + 4, h - 46), fill=(100, 115, 140))
    td.line((w // 2 - 56, h - 66, w // 2 + 56, h - 16), fill=RED, width=5)
    td.line((w // 2 - 56, h - 16, w // 2 + 56, h - 66), fill=RED, width=5)
    td.text((8, 8), "LONDON", font=font(SANS_B, 11), fill=INK)


def sc_arrest(td, w, h):
    td.rectangle((0, 0, w, h), fill=(238, 228, 205))
    for i in range(5):
        x = 14 + i * 26
        td.rectangle((x, 10, x + 8, h - 10), fill=(70, 70, 78))
    td.ellipse((w // 2 - 26, h // 2 - 12, w // 2 - 6, h // 2 + 8), fill=GOLD, outline=(120, 90, 10), width=2)
    td.ellipse((w // 2 + 6, h // 2 - 12, w // 2 + 26, h // 2 + 8), fill=GOLD, outline=(120, 90, 10), width=2)
    td.line((w // 2 - 6, h // 2 - 2, w // 2 + 6, h // 2 - 2), fill=(120, 90, 10), width=3)
    td.text((8, h - 14), "SINALOA", font=font(SANS_B, 11), fill=INK)


def sc_cricket(td, w, h):
    td.rectangle((0, 0, w, h), fill=(120, 170, 90))
    td.ellipse((w - 44, 10, w - 14, 40), fill=(200, 40, 30))
    td.rectangle((w // 2 - 4, 20, w // 2 + 4, h - 20), fill=(230, 220, 190))
    td.rectangle((w // 2 - 22, 12, w // 2 + 22, 22), fill=(230, 220, 190))
    td.rectangle((10, h - 34, 108, h - 8), fill=(30, 30, 30))
    td.text((16, h - 31), "720/9", font=font(SANS_B, 16), fill=(255, 255, 255))


def sc_tennis(td, w, h):
    td.rectangle((0, 0, w, h), fill=(90, 140, 200))
    td.rectangle((10, h - 30, w - 10, h - 10), fill=(200, 120, 60))
    td.line((w // 2, 10, w // 2, h - 30), fill=WHITE, width=2)
    td.ellipse((w // 2 - 30, 16, w // 2 - 6, 40), fill=(220, 230, 60))
    td.polygon([(w // 2 + 14, 12), (w // 2 + 34, 12), (w // 2 + 30, 40), (w // 2 + 18, 40)], fill=GOLD)
    td.text((8, h - 14), "TURIN", font=font(SANS_B, 11), fill=INK)


def sc_race(td, w, h):
    td.rectangle((0, 0, w, h), fill=(30, 30, 40))
    for i in range(6):
        for j in range(2):
            if (i + j) % 2 == 0:
                td.rectangle((w - 34 + i * 6, 8 + j * 6, w - 28 + i * 6, 14 + j * 6), fill=WHITE)
    td.polygon([(20, h - 34), (110, h - 34), (120, h - 18), (30, h - 18)], fill=(200, 30, 30))
    td.ellipse((40, h - 20, 56, h - 4), fill=INK)
    td.ellipse((96, h - 20, 112, h - 4), fill=INK)
    td.text((10, 10), "LAS VEGAS", font=font(SANS_B, 11), fill=WHITE)


def sc_fire(td, w, h):
    td.rectangle((0, 0, w, h), fill=(240, 225, 200))
    td.rectangle((w // 2 - 48, h - 44, w // 2 + 48, h - 14), fill=(120, 115, 105))
    td.rectangle((w // 2 - 48, h - 58, w // 2 + 48, h - 44), fill=(90, 85, 78))
    td.polygon([(w // 2 - 20, h - 58), (w // 2 - 6, h - 88), (w // 2 + 8, h - 58)], fill=(240, 120, 30))
    td.polygon([(w // 2 + 4, h - 58), (w // 2 + 18, h - 80), (w // 2 + 30, h - 58)], fill=(250, 180, 40))
    td.ellipse((w - 40, 10, w - 16, 34), fill=(150, 150, 150))
    td.text((8, h - 14), "SERANG", font=font(SANS_B, 11), fill=INK)


def sc_delta(td, w, h):
    td.rectangle((0, 0, w, h), fill=(215, 228, 240))
    td.polygon([(20, h // 2), (90, h // 2 - 22), (110, h // 2 - 22), (116, h // 2 - 10), (96, h // 2 + 2), (60, h // 2 + 6)], fill=(200, 40, 40))
    td.rectangle((96, h // 2 - 30, 102, h // 2 - 22), fill=(200, 40, 40))
    td.text((10, 10), "DELAYED", font=font(SANS_B, 13), fill=RED)
    td.text((w - 66, h - 20), "1,000+", font=font(SANS_B, 13), fill=INK)

# ------------------------------------------------------------------ content
# 40 verified stories: 4 large + 12 small featured, 24 in the index.
# Regions: Europe 10, Americas 10, Asia 9, Middle East 8, Global 2, Oceania 1.

LARGE = [
    (sc_cop31, "COP31 ends with no deal",
     "Antalya talks collapse after 50 hours overtime; no fossil-fuel language."),
    (sc_dems, "Democrats take 258 House seats",
     "Biggest majority since 1992 after a North Carolina recount flip."),
    (sc_trump, "Trump warns of new Iran strikes",
     "\u2018Professional tap dancers,\u2019 he says; deadline 1 January."),
    (sc_poland, "All three objects were Russian missiles",
     "Polish prosecutors confirm Kh-101s; NATO council meets in Brussels today."),
]

SMALL = [
    (sc_ship, "Russian warship ablaze in Benghazi"),
    (sc_block, "Kyiv-region block hit; 3 killed"),
    (sc_market, "Markets reel; S&P \u22128.6% in a week"),
    (sc_india, "India bucks rout; $13bn inflows"),
    (sc_gaza, "8 killed in Gaza; Qatari ship hit"),
    (sc_iranuk, "Iran brands Royal Navy terrorists"),
    (sc_arrest, "\u2018El Chapo Isidro\u2019 captured in Sinaloa"),
    (sc_cricket, "India pile up record 720/9"),
    (sc_tennis, "Alcaraz wins first ATP Finals"),
    (sc_race, "Verstappen wins Las Vegas GP"),
    (sc_fire, "Factory fire: 3 dead, 36 missing"),
    (sc_delta, "Delta glitch delays 1,000+ flights"),
]

LISTED = [
    "Sparta II towed away after Baltic attack",
    "Iran claims two US drones downed",
    "Netanyahu\u2013Eisenkot unity talks collapse",
    "Settler arson hits five West Bank villages",
    "Yemen strikes kill 5, injure 18",
    "Burnham: UK \u2018lost more than it gained\u2019",
    "FIFA to confirm UK as 2035 host today",
    "Manchester arena evacuated in tear-gas scare",
    "Liverpool beat 10-man Man Utd",
    "Europe's worst wildfire season on record",
    "UK sanctions eight firms over settlements",
    "Skubal signs record $450m Mets deal",
    "Nine shot at California concert",
    "US Army to detonate explosives in Iowa",
    "Father, daughter detained by ICE in Seattle",
    "Pregnant-workers law ruled unconstitutional",
    "California voters reject billionaire tax",
    "Lahore tops pollution ranking; AQI over 500",
    "Kim: N. Korea seeks security, not supremacy",
    "S. Korea minister quits over exam scandal",
    "S. Korea sees growth in upper-3% range",
    "India, China conclude 10-day LAC talks",
    "Nepal PM in Delhi; Modi talks today",
    "Myanmar calls ASEAN review \u2018unfair\u2019",
]

NUMBERS = [
    ("258", "Dem House seats"),
    ("3", "Kh-101 missiles in Poland"),
    ("\u22128.6%", "S&P 500 in a week"),
    ("$13bn", "India inflows in Nov"),
    ("720/9", "India record total"),
    ("36", "missing in factory fire"),
]

REGIONS = [
    ("Europe", 10, (38, 84, 150)),
    ("Americas", 10, (46, 125, 70)),
    ("Asia", 9, (214, 164, 48)),
    ("Middle East", 8, (179, 39, 30)),
    ("Global", 2, (90, 84, 74)),
    ("Oceania", 1, (72, 130, 170)),
]

DATE_CHECK = [
    "Pete Rose pardon \u2014 19 Nov",
    "Anthropic IPO \u2014 19 Nov",
    "Huang resigns \u2014 12 Nov",
    "Poland missiles fell \u2014 20 Nov",
    "Cyclone Akvan \u2014 20 Nov",
    "Miley Cyrus wedding \u2014 21 Nov",
]

# Map pins for the 16 featured stories: (number, x, y) in map coords.
PINS = [
    (1, 192, 58), (2, 60, 50), (3, 198, 64), (4, 160, 36),
    (5, 170, 86), (6, 180, 44), (7, 118, 92), (8, 205, 88),
    (9, 182, 72), (10, 140, 40), (11, 46, 90), (12, 292, 118),
    (13, 166, 58), (14, 74, 64), (15, 246, 96), (16, 52, 74),
]


def draw_map(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(214, 228, 235), outline=RULE, width=1)
    # Rough continents, drawn as simple blobs (offset by the box origin).
    d.ellipse((x0 + 18, y0 + 18, x0 + 108, y0 + 66), fill=(200, 205, 170))   # N America
    d.ellipse((x0 + 78, y0 + 72, x0 + 128, y0 + 122), fill=(200, 205, 170))  # S America
    d.ellipse((x0 + 148, y0 + 22, x0 + 196, y0 + 62), fill=(200, 205, 170))  # Europe
    d.ellipse((x0 + 150, y0 + 64, x0 + 200, y0 + 118), fill=(200, 205, 170)) # Africa
    d.ellipse((x0 + 204, y0 + 16, x0 + 296, y0 + 72), fill=(200, 205, 170))  # Asia
    d.ellipse((x0 + 258, y0 + 100, x0 + 296, y0 + 126), fill=(200, 205, 170))  # Oceania
    d.text((x0 + 8, y0 + 6), "WHERE IT HAPPENED", font=font(SANS_B, 12), fill=INK)
    for num, px, py in PINS:
        cx, cy = x0 + px, y0 + py
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=RED, outline=WHITE, width=1)
        t = str(num)
        tw = d.textlength(t, font=font(SANS_B, 9))
        d.text((cx - tw / 2, cy - 6), t, font=font(SANS_B, 9), fill=WHITE)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead.
    d.line((M, 12, W - M, 12), fill=RULE, width=2)
    title = "Monday 23 November 2026"
    tf = font(SERIF_B, 42)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 26), title, font=tf, fill=INK)
    strap = "The world in one page \u2014 40 stories from Monday, verified against the day's reporting"
    sf = font(SERIF_I, 15)
    sw = d.textlength(strap, font=sf)
    d.text(((W - sw) / 2, 78), strap, font=sf, fill=GREY)

    # Number strip: 6 boxes.
    ny0, ny1 = 102, 142
    nwid = (W - 2 * M - 5 * 8) // 6
    for i, (num, label) in enumerate(NUMBERS):
        x0 = M + i * (nwid + 8)
        x1 = x0 + nwid
        d.rectangle((x0, ny0, x1, ny1), fill=PANEL, outline=RULE, width=1)
        nf = font(SERIF_B, 20)
        nw = d.textlength(num, font=nf)
        d.text(((x0 + x1 - nw) / 2, ny0 + 3), num, font=nf, fill=RED)
        lf = font(SANS, 11)
        lw = d.textlength(label, font=lf)
        d.text(((x0 + x1 - lw) / 2, ny0 + 25), label, font=lf, fill=INK)

    # Region bar: segments proportional to counts (total 40).
    ry0, ry1 = 152, 170
    total = sum(c for _, c, _ in REGIONS)
    assert total == 40, "region counts must sum to 40, got %d" % total
    x = M
    bar_w = W - 2 * M
    for name, count, col in REGIONS:
        seg = bar_w * count // total
        d.rectangle((x, ry0, x + seg - 1, ry1), fill=col)
        x += seg
    lx, ly = M, 176
    for name, count, col in REGIONS:
        d.rectangle((lx, ly + 2, lx + 10, ly + 12), fill=col)
        lx += 14
        lab = "%s %d" % (name, count)
        lf = font(SANS, 12)
        d.text((lx, ly), lab, font=lf, fill=INK)
        lx += d.textlength(lab, font=lf) + 16

    # Large panels: 4 across.
    ly0, ly1 = 198, 362
    lw_ = (W - 2 * M - 3 * 8) // 4
    for i, (scene, head, deck) in enumerate(LARGE):
        x0 = M + i * (lw_ + 8)
        x1 = x0 + lw_
        panel_box(d, (x0, ly0, x1, ly1))
        scene_img = paint_scene((x0 + 1, ly0 + 1, x1 - 1, ly0 + 93), scene)
        img.paste(scene_img, (x0 + 1, ly0 + 1))
        hf = font(SANS_B, 15)
        lines = fit(d, head, hf, lw_ - 12, 2, "large headline %d" % i)
        draw_lines(d, lines, x0 + 6, ly0 + 98, hf, INK, 18)
        df = font(SANS, 12)
        dlines = fit(d, deck, df, lw_ - 12, 2, "large deck %d" % i)
        draw_lines(d, dlines, x0 + 6, ly0 + 98 + 18 * len(lines) + 2, df, GREY, 15)

    # Small panels: 2 rows of 6.
    sw_ = (W - 2 * M - 5 * 8) // 6
    for row in range(2):
        sy0 = 370 + row * 140
        sy1 = sy0 + 132
        for col in range(6):
            i = row * 6 + col
            scene, head = SMALL[i]
            x0 = M + col * (sw_ + 8)
            x1 = x0 + sw_
            panel_box(d, (x0, sy0, x1, sy1))
            scene_img = paint_scene((x0 + 1, sy0 + 1, x1 - 1, sy0 + 65), scene)
            img.paste(scene_img, (x0 + 1, sy0 + 1))
            hf = font(SANS_B, 12)
            lines = fit(d, head, hf, sw_ - 10, 3, "small headline %d" % i)
            draw_lines(d, lines, x0 + 5, sy0 + 70, hf, INK, 15)

    # Bottom section: map + date check on the left, index on the right.
    by = 658
    map_box = (M, by, M + 330, by + 150)
    draw_map(d, map_box)
    dcb = (M, by + 158, M + 330, by + 326)
    d.rectangle(dcb, fill=PANEL, outline=RULE, width=1)
    d.text((dcb[0] + 8, dcb[1] + 6), "DATE CHECK \u2014 NOT 23 NOVEMBER",
           font=font(SANS_B, 12), fill=RED)
    y = dcb[1] + 24
    for item in DATE_CHECK:
        d.text((dcb[0] + 8, y), "\u2022  " + item, font=font(SANS, 12), fill=INK)
        y += 16
    d.text((dcb[0] + 8, y + 4), "These made the rounds today, but",
           font=font(SERIF_I, 12), fill=GREY)
    d.text((dcb[0] + 8, y + 20), "happened on an earlier date.",
           font=font(SERIF_I, 12), fill=GREY)

    lx0 = M + 346
    d.text((lx0, by), "ALSO ON MONDAY", font=font(SANS_B, 13), fill=INK)
    d.line((lx0, by + 18, W - M, by + 18), fill=RULE, width=1)
    col_w = (W - M - lx0 - 12) // 2
    for idx, item in enumerate(LISTED):
        col = idx // 12
        row = idx % 12
        x = lx0 + col * (col_w + 12)
        y = by + 26 + row * 25
        num = "%d." % (idx + 17)
        d.text((x, y), num, font=font(SANS_B, 12), fill=RED)
        txt = item
        tf_ = font(SANS, 12)
        assert d.textlength(txt, font=tf_) <= col_w - 28, "list item too long: %r" % txt
        d.text((x + 26, y), txt, font=tf_, fill=INK)

    # Footer.
    d.line((M, 992, W - M, 992), fill=RULE, width=1)
    foot = "40 stories \u00b7 Sources: BBC, AP, Reuters, The Hindu, Dawn, Xinhua, Times of India \u00b7 Drawn in code, no photographs"
    ff = font(SANS, 11)
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, 998), foot, font=ff, fill=GREY)

    os.makedirs("entry", exist_ok=True)
    img.save("entry/entry.png", optimize=True)
    data = open("entry/entry.png", "rb").read()
    print("entry.png: %d bytes, sha256 %s" % (len(data), hashlib.sha256(data).hexdigest()))
    assert len(data) <= 1048576, "entry.png over 1 MiB"
    assert img.size == (1024, 1024)


if __name__ == "__main__":
    main()
