#!/usr/bin/env python3
"""
Legendary neon dragon takeoff GIF for GitHub profile.
Side-view cyber dragon: summon circle → takeoff → flap → plasma roar.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "dragon.gif"
PREVIEW = ROOT / "assets" / "preview"

BG = (13, 17, 23)
CYAN = (0, 212, 255)
CYAN2 = (0, 150, 200)
CYAN3 = (120, 235, 255)
ORANGE = (255, 107, 53)
GOLD = (255, 205, 70)
WHITE = (245, 252, 255)
GREEN = (80, 250, 123)
MUTED = (115, 125, 145)

FONT = "/usr/share/fonts/truetype/jetbrains-mono-zorin-os/JetBrainsMono-Regular.ttf"
FONT_B = "/usr/share/fonts/truetype/jetbrains-mono-zorin-os/JetBrainsMono-Bold.ttf"

W, H = 640, 360


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def catmull(points, n_per=10):
    if len(points) < 2:
        return list(points)
    pts = [points[0]] + list(points) + [points[-1], points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(n_per):
            t = j / n_per
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def rot(p, origin, ang):
    ox, oy = origin
    x, y = p[0] - ox, p[1] - oy
    c, s = math.cos(ang), math.sin(ang)
    return (ox + x * c - y * s, oy + x * s + y * c)


# ---------------------------------------------------------------------------
# Side-view dragon (facing right) — much more readable & dramatic
# ---------------------------------------------------------------------------

def build_dragon(wing: float, breath: float, lift: float, charge: float = 1.0):
    """
    wing: -1 (down) .. +1 (up)
    breath: 0..1 plasma
    lift: vertical offset
    charge: 0..1 body opacity / materialize
    """
    # Anchor: chest center
    cx = W * 0.42
    cy = H * 0.52 + lift

    # Body silhouette (side profile, facing +x)
    body = catmull(
        [
            (cx - 55, cy - 10),   # neck base
            (cx - 40, cy - 35),
            (cx - 10, cy - 42),   # withers
            (cx + 35, cy - 28),   # back
            (cx + 70, cy - 5),    # hip
            (cx + 85, cy + 25),   # rump
            (cx + 55, cy + 40),
            (cx + 10, cy + 45),   # belly
            (cx - 30, cy + 35),
            (cx - 55, cy + 10),
        ],
        8,
    )

    # Neck + head
    neck = catmull(
        [
            (cx - 50, cy - 15),
            (cx - 75, cy - 45),
            (cx - 95, cy - 70),
        ],
        8,
    )
    head = [
        (cx - 100, cy - 78),
        (cx - 125, cy - 85),  # snout top
        (cx - 138, cy - 72),  # nose
        (cx - 132, cy - 60),  # jaw tip
        (cx - 110, cy - 55),
        (cx - 95, cy - 62),
        (cx - 92, cy - 78),
    ]
    jaw = [
        (cx - 108, cy - 58),
        (cx - 130, cy - 58),
        (cx - 125, cy - 48),
        (cx - 105, cy - 52),
    ]
    horn = [
        (cx - 98, cy - 82),
        (cx - 108, cy - 118),
        (cx - 100, cy - 112),
        (cx - 92, cy - 85),
    ]
    horn2 = [
        (cx - 90, cy - 80),
        (cx - 96, cy - 102),
        (cx - 88, cy - 98),
        (cx - 86, cy - 82),
    ]
    eye = (cx - 112, cy - 74)
    nostril = (cx - 134, cy - 68)

    # Spine plates along back
    plates = []
    back_pts = [
        (cx - 35, cy - 38),
        (cx - 5, cy - 44),
        (cx + 25, cy - 32),
        (cx + 55, cy - 12),
        (cx + 75, cy + 5),
    ]
    for i, (bx, by) in enumerate(back_pts):
        hgt = 16 if i % 2 == 0 else 11
        plates.append([(bx - 4, by), (bx, by - hgt), (bx + 5, by + 2)])

    # Wing — shoulder pivot, flaps around Z
    shoulder = (cx - 5, cy - 25)
    # Base wing shape (up position), then rotate by flap angle
    flap_ang = -wing * 0.85  # radians-ish scale
    wing_outer = [
        shoulder,
        (shoulder[0] + 20, shoulder[1] - 70),
        (shoulder[0] + 55, shoulder[1] - 110),
        (shoulder[0] + 100, shoulder[1] - 95),  # tip
        (shoulder[0] + 90, shoulder[1] - 50),
        (shoulder[0] + 70, shoulder[1] - 10),
        (shoulder[0] + 35, shoulder[1] + 15),
        shoulder,
    ]
    wing_poly = [rot(p, shoulder, flap_ang) for p in wing_outer]
    # When wings down, stretch tip lower
    if wing < 0:
        tip_i = 3
        tx, ty = wing_poly[tip_i]
        wing_poly[tip_i] = (tx + abs(wing) * 15, ty + abs(wing) * 40)

    # Wing bones
    tip = wing_poly[3]
    mid1 = wing_poly[1]
    mid2 = wing_poly[2]
    bones = [
        catmull([shoulder, mid1, tip], 6),
        catmull([shoulder, mid2, (tip[0] - 15, tip[1] + 25)], 6),
        catmull([shoulder, (lerp(shoulder[0], tip[0], 0.4), lerp(shoulder[1], tip[1], 0.35) + 20), (tip[0] - 30, tip[1] + 45)], 6),
    ]
    # membrane ribs
    ribs = []
    for bi in range(len(bones) - 1):
        for t in (0.3, 0.55, 0.8):
            a = bones[bi][int(t * (len(bones[bi]) - 1))]
            b = bones[bi + 1][int(t * (len(bones[bi + 1]) - 1))]
            ribs.append([a, b])

    # Near wing (smaller, behind-ish) — other wing peeking
    near_shoulder = (cx + 8, cy - 18)
    near_wing = [
        near_shoulder,
        (near_shoulder[0] - 15, near_shoulder[1] - 40 - wing * 20),
        (near_shoulder[0] - 40, near_shoulder[1] - 55 - wing * 30),
        (near_shoulder[0] - 25, near_shoulder[1] - 10),
        near_shoulder,
    ]

    # Foreleg
    fore = catmull([(cx - 25, cy + 20), (cx - 35, cy + 55), (cx - 30, cy + 78)], 5)
    fore_claws = [
        [(cx - 30, cy + 78), (cx - 42, cy + 88)],
        [(cx - 28, cy + 76), (cx - 34, cy + 90)],
        [(cx - 24, cy + 75), (cx - 26, cy + 88)],
    ]
    # Hind leg
    hind = catmull([(cx + 45, cy + 25), (cx + 60, cy + 60), (cx + 48, cy + 90), (cx + 55, cy + 95)], 6)
    hind_claws = [
        [(cx + 55, cy + 95), (cx + 68, cy + 102)],
        [(cx + 52, cy + 93), (cx + 60, cy + 105)],
        [(cx + 48, cy + 92), (cx + 50, cy + 103)],
    ]

    # Tail
    sway = wing * 10
    tail = catmull(
        [
            (cx + 80, cy + 15),
            (cx + 115, cy + 35 + sway * 0.3),
            (cx + 140, cy + 20 + sway * 0.6),
            (cx + 165, cy + 45 + sway),
            (cx + 185, cy + 30 + sway * 1.2),
        ],
        10,
    )
    tip_t = tail[-1]
    fin = [
        tip_t,
        (tip_t[0] + 18, tip_t[1] - 16),
        (tip_t[0] + 28, tip_t[1]),
        (tip_t[0] + 14, tip_t[1] + 12),
    ]

    # Belly scales (side chevrons)
    scales = []
    for i in range(6):
        sx = cx - 20 + i * 18
        sy = cy + 15 + (i % 2) * 3
        scales.append([(sx, sy), (sx + 8, sy + 6), (sx + 16, sy)])

    mouth = (cx - 136, cy - 64)

    return {
        "charge": charge,
        "body": body,
        "neck": neck,
        "head": head,
        "jaw": jaw,
        "horn": horn,
        "horn2": horn2,
        "eye": eye,
        "nostril": nostril,
        "plates": plates,
        "wing": wing_poly,
        "near_wing": near_wing,
        "bones": bones,
        "ribs": ribs,
        "fore": fore,
        "fore_claws": fore_claws,
        "hind": hind,
        "hind_claws": hind_claws,
        "tail": tail,
        "fin": fin,
        "scales": scales,
        "mouth": mouth,
        "breath": breath,
        "shoulder": shoulder,
        "cx": cx,
        "cy": cy,
    }


def render_dragon(parts: dict) -> Image.Image:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ink = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd, bd, id_ = ImageDraw.Draw(glow), ImageDraw.Draw(body), ImageDraw.Draw(ink)

    a = int(255 * clamp(parts["charge"], 0, 1))
    fill = (0, 55, 95, int(230 * a / 255))
    fill2 = (0, 75, 120, int(210 * a / 255))
    wing_f = (0, 65, 115, int(175 * a / 255))
    wing_f2 = (0, 40, 80, int(130 * a / 255))
    line = CYAN + (a,)
    bright = CYAN3 + (a,)
    dim = CYAN2 + (int(a * 0.85),)

    def poly(pts, f, outline=True):
        p = [(int(x), int(y)) for x, y in pts]
        if len(p) < 3:
            return
        gd.polygon(p, fill=CYAN[:3] + (int(35 * a / 255),))
        bd.polygon(p, fill=f)
        if outline:
            id_.line(p + [p[0]], fill=line, width=2)

    def stroke(pts, width=3, color=None):
        p = [(int(x), int(y)) for x, y in pts]
        if len(p) < 2:
            return
        col = color or line
        gd.line(p, fill=CYAN[:3] + (int(70 * a / 255),), width=width + 6)
        id_.line(p, fill=col, width=width)

    # Far / near wing first
    poly(parts["near_wing"], wing_f2)
    poly(parts["wing"], wing_f)
    # darker inner membrane
    if len(parts["wing"]) > 5:
        inner = parts["wing"][1:-1]
        if len(inner) >= 3:
            p = [(int(x), int(y)) for x, y in inner]
            bd.polygon(p, fill=wing_f2)

    for bone in parts["bones"]:
        stroke(bone, 2, bright)
    for rib in parts["ribs"]:
        stroke(rib, 1, dim)

    # Body
    poly(parts["body"], fill)
    # belly highlight band
    belly = [
        (parts["cx"] - 35, parts["cy"] + 20),
        (parts["cx"] + 50, parts["cy"] + 28),
        (parts["cx"] + 40, parts["cy"] + 42),
        (parts["cx"] - 30, parts["cy"] + 35),
    ]
    poly(belly, fill2, outline=False)
    for sc in parts["scales"]:
        stroke(sc, 1, dim)

    for pl in parts["plates"]:
        poly(pl, (0, 90, 140, int(230 * a / 255)))

    # Neck tube
    stroke(parts["neck"], 5, line)
    for i, (x, y) in enumerate(parts["neck"][::2]):
        r = 6 - i // 2
        if r > 0:
            bd.ellipse((x - r, y - r, x + r, y + r), fill=fill)

    poly(parts["head"], (0, 60, 100, int(240 * a / 255)))
    poly(parts["jaw"], (0, 40, 70, int(220 * a / 255)))
    poly(parts["horn"], (0, 85, 130, int(240 * a / 255)))
    poly(parts["horn2"], (0, 75, 115, int(230 * a / 255)))

    # Eye
    ex, ey = parts["eye"]
    gd.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=CYAN[:3] + (int(110 * a / 255),))
    id_.ellipse((ex - 4, ey - 4, ex + 4, ey + 4), fill=WHITE + (a,))
    id_.ellipse((ex - 1, ey - 1, ex + 2, ey + 2), fill=CYAN + (a,))
    # brow ridge
    id_.arc((ex - 10, ey - 12, ex + 8, ey + 2), 200, 340, fill=bright, width=2)

    nx, ny = parts["nostril"]
    id_.ellipse((nx - 2, ny - 2, nx + 2, ny + 2), fill=ORANGE + (a,))

    # Limbs
    stroke(parts["fore"], 4)
    stroke(parts["hind"], 4)
    for c in parts["fore_claws"] + parts["hind_claws"]:
        stroke(c, 2, bright)

    # Tail
    stroke(parts["tail"], 4)
    for i, (x, y) in enumerate(parts["tail"][::3]):
        r = max(2, 6 - i // 2)
        bd.ellipse((x - r, y - r, x + r, y + r), fill=fill)
    poly(parts["fin"], (0, 95, 145, int(230 * a / 255)))

    # Energy core in chest
    cx, cy = parts["cx"], parts["cy"]
    gd.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(0, 180, 255, int(45 * a / 255)))
    id_.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=CYAN3 + (int(180 * a / 255),))

    # Plasma breath (to the left / forward from snout)
    breath = parts["breath"]
    if breath > 0.05:
        mx, my = parts["mouth"]
        rng = random.Random(int(mx + breath * 100))
        for i in range(int(30 * breath)):
            dist = 10 + i * 9
            spread = (rng.random() - 0.5) * (8 + i * 3.5) * breath
            # facing left (negative x)
            px = mx - dist
            py = my + spread + i * 0.4
            r = max(1.5, (11 - i * 0.28) * breath)
            col = GOLD if i < 6 else ORANGE if i < 14 else (255, 130, 50)
            aa = int(220 * breath * (1 - i / 32))
            gd.ellipse((px - r * 2, py - r * 2, px + r * 2, py + r * 2), fill=col + (aa // 3,))
            id_.ellipse((px - r, py - r, px + r, py + r), fill=col + (aa,))
        id_.polygon(
            [
                (mx, my - 4),
                (mx, my + 4),
                (mx - 95 * breath, my + 12 * breath),
                (mx - 95 * breath, my - 8 * breath),
            ],
            fill=GOLD + (int(130 * breath),),
        )
        for _ in range(int(14 * breath)):
            id_.point(
                (mx - rng.random() * 100 * breath, my + (rng.random() - 0.5) * 40 * breath),
                fill=WHITE + (255,),
            )

    out = Image.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)), glow.filter(ImageFilter.GaussianBlur(5)))
    out = Image.alpha_composite(out, body)
    out = Image.alpha_composite(out, ink)
    bloom = ink.filter(ImageFilter.GaussianBlur(3))
    out = Image.alpha_composite(out, Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 0)), bloom, 0.5))
    return out


# ---------------------------------------------------------------------------
# Scene FX
# ---------------------------------------------------------------------------

def summon_circle(draw, cx, cy, radius, t, alpha=180):
    """Rotating runic summon ring."""
    for ring, w in ((1.0, 2), (0.78, 1), (0.55, 1)):
        r = radius * ring
        bbox = (cx - r, cy - r, cx + r, cy + r)
        draw.arc(bbox, 0, 360, fill=CYAN[:3] + (int(alpha * 0.5),), width=w)
    # ticks
    for i in range(12):
        ang = t * 2 + i * (math.tau / 12)
        x0 = cx + math.cos(ang) * radius * 0.9
        y0 = cy + math.sin(ang) * radius * 0.9
        x1 = cx + math.cos(ang) * radius * 1.05
        y1 = cy + math.sin(ang) * radius * 1.05
        draw.line([(x0, y0), (x1, y1)], fill=CYAN3[:3] + (alpha,), width=2)
    # inner hex
    hex_pts = []
    for i in range(6):
        ang = t * -1.5 + i * (math.tau / 6)
        hex_pts.append((cx + math.cos(ang) * radius * 0.45, cy + math.sin(ang) * radius * 0.45))
    draw.polygon(hex_pts, outline=CYAN[:3] + (alpha,))


def radial(strength: float) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    cx, cy = int(W * 0.42), int(H * 0.52)
    for r, amp in ((260, 18), (180, 28), (110, 42), (50, 55)):
        shade = (BG[0], clamp(BG[1] + int(amp * strength * 0.5), 0, 255), clamp(BG[2] + int(amp * strength), 0, 255))
        d.ellipse((cx - r, cy - int(r * 0.7), cx + r, cy + int(r * 0.7)), fill=shade)
    return img


def font(size=12, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def chrome(img: Image.Image, status: str, boot: list[str] | None = None):
    d = ImageDraw.Draw(img)
    f, fs = font(12), font(11)
    d.rectangle((1, 1, W - 2, H - 2), outline=(0, 95, 125))
    d.rectangle((3, 3, W - 4, H - 4), outline=(0, 50, 70))

    d.text((12, 8), "moon@kirirom", font=f, fill=GREEN)
    x = 12 + f.getlength("moon@kirirom")
    d.text((x, 8), ":~$ ", font=f, fill=MUTED)
    x += f.getlength(":~$ ")
    d.text((x, 8), "./dragon.sh --takeoff --legendary", font=f, fill=CYAN)

    if boot:
        y = 32
        for line in boot:
            col = GREEN if line.endswith("OK") else ORANGE if line.startswith(">>>") else CYAN2
            if line.startswith("[summon]"):
                col = CYAN
            d.text((14, y), line, font=fs, fill=col)
            y += 14

    if status:
        sw = fs.getlength(status)
        hot = any(k in status for k in ("PLASMA", "LEGENDARY", "dragon", "ONLINE"))
        d.text(((W - sw) / 2, H - 22), status, font=fs, fill=ORANGE if hot else MUTED)


def particles(img, idx, fire):
    d = ImageDraw.Draw(img)
    rng = random.Random(idx * 104729 + 9)
    for i in range(40 if fire else 22):
        x = int(rng.random() * W)
        y = (int(rng.random() * H) + idx * (2 + i % 3)) % H
        s = 1 + i % 3
        col = (ORANGE if rng.random() < 0.5 else GOLD) if fire and rng.random() < 0.45 else (CYAN if rng.random() < 0.7 else CYAN3)
        d.ellipse((x, y, x + s, y + s), fill=col)


def scanlines(img: Image.Image) -> Image.Image:
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, 35))
    return Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")


def ground_glow(draw, cy_ground, strength):
    # runway / lift glow under dragon
    for i, a in enumerate((40, 25, 12)):
        r = 90 + i * 40
        draw.ellipse(
            (W * 0.42 - r, cy_ground - 8 - i * 3, W * 0.42 + r * 0.6, cy_ground + 8 + i * 3),
            fill=(0, int(80 * strength), int(120 * strength), a),
        )


def frame(
    *,
    wing: float,
    breath: float,
    lift: float,
    glow: float,
    status: str,
    idx: int,
    fire: bool,
    boot: list[str] | None = None,
    show: bool = True,
    charge: float = 1.0,
    circle_t: float = 0.0,
    circle_r: float = 0.0,
) -> Image.Image:
    base = Image.blend(Image.new("RGB", (W, H), BG), radial(glow), 0.48)
    rgba = base.convert("RGBA")

    # summon circle layer
    if circle_r > 5:
        circ = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(circ)
        summon_circle(cd, int(W * 0.42), int(H * 0.62), circle_r, circle_t, alpha=int(160 * min(1, circle_r / 80)))
        ground_glow(cd, H * 0.72, glow)
        rgba = Image.alpha_composite(rgba, circ)

    if show:
        dragon = render_dragon(build_dragon(wing, breath, lift, charge))
        # motion afterimage on strong flaps
        if abs(wing) > 0.5:
            ghost = render_dragon(build_dragon(wing * 0.7, 0, lift + 3, charge * 0.35))
            rgba = Image.alpha_composite(rgba, ghost)
        bloom = dragon.filter(ImageFilter.GaussianBlur(4))
        rgba = Image.alpha_composite(rgba, Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 0)), bloom, 0.55))
        rgba = Image.alpha_composite(rgba, dragon)

    base = rgba.convert("RGB")
    if show or fire:
        particles(base, idx, fire)
    chrome(base, status, boot)
    base = scanlines(base)
    return ImageEnhance.Contrast(base).enhance(1.1)


def boot_at(t: float) -> list[str]:
    pct = int(min(1.0, t) * 100)
    filled = pct * 28 // 100
    bar = "#" * filled + "-" * (28 - filled)
    lines = [
        "[boot] loading scale shaders ................ OK",
        "[boot] calibrating wing actuators ........... OK",
        "[boot] igniting core plasma ................. OK",
        "[boot] linking neon optic nerves ............ OK",
        "",
        f"[summon] [{bar}] {pct:3d}%",
    ]
    if pct >= 80:
        lines += ["", ">>> ENTITY SIGNATURE DETECTED", ">>> STAND CLEAR OF BLAST RADIUS"]
    return lines


def build():
    frames, durs = [], []
    i = 0

    # Boot + growing summon circle
    for s in range(12):
        t = s / 11
        frames.append(
            frame(
                wing=-0.9,
                breath=0,
                lift=22,
                glow=0.4 + t * 0.4,
                status="",
                idx=i,
                fire=False,
                boot=boot_at(t),
                show=False,
                circle_t=t * 4,
                circle_r=20 + t * 90,
            )
        )
        durs.append(70)
        i += 1

    # Materialize inside circle
    for s, (charge, wing, lift, status) in enumerate(
        [
            (0.25, -0.9, 18, "[ materializing -- hold ]"),
            (0.55, -0.7, 12, "[ wings folded -- charging ]"),
            (0.85, -0.2, 4, "[ wing membranes deploying ]"),
            (1.0, 0.5, -2, "[ wings half-spread -- lift rising ]"),
            (1.0, 0.95, -8, "[ wings fully deployed -- ascending ]"),
        ]
    ):
        frames.append(
            frame(
                wing=wing,
                breath=0,
                lift=lift,
                glow=0.9 + s * 0.08,
                status=status,
                idx=i,
                fire=False,
                charge=charge,
                circle_t=s * 0.8,
                circle_r=max(0, 100 - s * 22),
            )
        )
        durs.append(140)
        i += 1

    # Flap loops
    for _ in range(3):
        for step in range(8):
            t = step / 8
            w = math.sin(t * math.tau)
            if w > 0.4:
                st = "[ wings fully deployed -- ascending ]"
            elif w < -0.4:
                st = "[ recovery -- glide ]"
            else:
                st = "[ downstroke -- thrust ]"
            lift = -10 - abs(w) * 6 - math.sin(t * math.tau) * 3
            frames.append(
                frame(wing=w, breath=0, lift=lift, glow=1.05 + abs(w) * 0.15, status=st, idx=i, fire=False, circle_r=0)
            )
            durs.append(85)
            i += 1

    # Plasma roar
    for s in range(8):
        t = s / 7
        breath = min(1.0, t * 1.25)
        w = 0.7 + 0.25 * math.sin(t * math.pi)
        frames.append(
            frame(
                wing=w,
                breath=breath,
                lift=-12,
                glow=1.2 + breath * 0.35,
                status="[ PLASMA BREATH -- TARGET LOCKED ]" if breath > 0.3 else "[ LEGENDARY MODE -- ONLINE ]",
                idx=i,
                fire=True,
            )
        )
        durs.append(100)
        i += 1

    # Final flaps + hold
    for step in range(6):
        t = step / 6
        w = math.sin(t * math.tau)
        frames.append(
            frame(
                wing=w,
                breath=0,
                lift=-10 - abs(w) * 3,
                glow=1.1,
                status="[ wings fully deployed -- ascending ]",
                idx=i,
                fire=False,
            )
        )
        durs.append(90)
        i += 1

    frames.append(
        frame(
            wing=0.9,
            breath=0,
            lift=-12,
            glow=1.15,
            status="+  every good compiler deserves a dragon  +",
            idx=i,
            fire=False,
        )
    )
    durs.append(400)
    return frames, durs


def quantize(img: Image.Image) -> Image.Image:
    return img.resize((560, 315), Image.Resampling.LANCZOS).quantize(
        colors=40, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE
    )


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    frames, durs = build()
    for n in (0, 11, 15, 25, 45, len(frames) - 1):
        if 0 <= n < len(frames):
            frames[n].save(PREVIEW / f"frame_{n:02d}.png")
    q = [quantize(f) for f in frames]
    q[0].save(OUT, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=2)
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.1f} KB, {len(frames)} frames)")


if __name__ == "__main__":
    main()
