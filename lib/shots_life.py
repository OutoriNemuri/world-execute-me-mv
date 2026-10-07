# -*- coding: utf-8 -*-
"""shots_life — movement D: vegetables, a cat, and godhood."""
import math
from render_lib import (W, H, TAU, px, mix, shade, clamp01, smoothstep, ease_out,
                        ease_in, pulse, text_at, text_glow, grad_rect, dashed_line,
                        arrow, dot, ring, poly, glow, blit, FONT_EN, FONT_ZH)
from scene_paint import (rnd, hex_grid, dot_field, grid_lines, crosshair, waveform,
                         oscilloscope, pcb_network, concentric, orbit_ring,
                         target_rings, project)
import cairo


def _leaf(cr, x, y, size, angle, col, a, vein=True):
    cr.save()
    cr.translate(x, y)
    cr.rotate(angle)
    cr.scale(size, size * 0.42)
    cr.arc(0, 0, 1.0, 0, TAU)
    cr.restore()
    cr.save()
    cr.translate(x, y)
    cr.rotate(angle)
    cr.set_source_rgba(*col, a)
    cr.save()
    cr.scale(size, size * 0.42)
    cr.arc(0, 0, 1.0, 0, TAU)
    cr.restore()
    cr.fill()
    if vein:
        cr.set_line_width(px(1.4))
        cr.set_source_rgba(0, 0, 0, a * 0.30)
        cr.move_to(-size, 0)
        cr.line_to(size, 0)
        cr.stroke()
    cr.restore()


def eggplant(cr, s):
    """If I'm an eggplant — a botanical specimen plate."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # specimen paper
    hex_grid(cr, c1, alpha=0.04)
    cx, cy = W / 2, H * 0.54
    k = ease_out(clamp01(s.p * 1.3), 2.0)
    # stem
    cr.save()
    cr.set_line_width(px(16))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(*shade(c2, 0.7), 0.9 * k)
    cr.move_to(cx + px(10), cy - px(250))
    cr.line_to(cx + px(6), cy - px(360))
    cr.stroke()
    cr.restore()
    _leaf(cr, cx - px(60), cy - px(330), px(90), -0.5, c2, 0.8 * k)
    _leaf(cr, cx + px(80), cy - px(300), px(70), 0.7, c2, 0.7 * k)
    # body: an ellipse with a highlight
    cr.save()
    cr.translate(cx, cy)
    cr.scale(px(190), px(330))
    cr.arc(0, 0, 1.0, 0, TAU)
    cr.set_source_rgba(*mix(c2, (0, 0, 0), 0.45), 0.92 * k)
    cr.fill()
    cr.restore()
    # sheen
    cr.save()
    cr.translate(cx - px(60), cy - px(90))
    cr.rotate(-0.22)
    cr.scale(px(60), px(150))
    cr.arc(0, 0, 1.0, 0, TAU)
    cr.set_source_rgba(1, 1, 1, 0.16 * k)
    cr.fill()
    cr.restore()
    ring(cr, cx, cy, 0, c2, 0)  # keep import used
    # measurement callouts
    def measure(x1, y1, x2, y2, label):
        dashed_line(cr, x1, y1, x2, y2, 6, 8, 1.4, c1, 0.5 * k)
        arrow(cr, x1, y1, x2, y2, c1, 1.4, 0.5 * k, 10)
        arrow(cr, x2, y2, x1, y1, c1, 1.4, 0.5 * k, 10)
        text_at(cr, (x1 + x2) / 2, (y1 + y2) / 2 - px(16), label, px(20), c1,
                'cb', FONT_EN, alpha=0.6 * k, spacing=1.5)

    measure(cx - px(330), cy - px(330), cx - px(330), cy + px(330), 'long axis')
    # a data block, like a herbarium label
    bx, by = px(130), H - px(330)
    cr.save()
    cr.set_line_width(px(1.4))
    cr.set_source_rgba(*c1, 0.35 * k)
    cr.rectangle(bx, by, px(430), px(230))
    cr.stroke()
    cr.restore()
    for i, line in enumerate(('SOLANUM MELONGENA', 'family  Solanaceae',
                              'nutrients  17 kcal/100g',
                              'sample  %d' % (s.idx * 7 % 900 + 100))):
        text_at(cr, bx + px(24), by + px(30) + i * px(46), line, px(i and 22 or 26),
                c2 if i == 0 else c1, 'lt', FONT_EN, alpha=(0.85 if i == 0 else 0.55) * k,
                spacing=1.5)


def nutrients(cr, s):
    """Then I will give you my nutrients — nutrients stream out as points."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = px(430), H * 0.52
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    # the eggplant, simplified, on the left
    cr.save()
    cr.translate(cx, cy)
    cr.scale(px(130), px(220))
    cr.arc(0, 0, 1.0, 0, TAU)
    cr.set_source_rgba(*mix(c2, (0, 0, 0), 0.4), 0.85)
    cr.fill()
    cr.restore()
    # streams of values flying right into a collection bin
    for i in range(90):
        u = ((s.t * 0.42 + rnd(97, i)) % 1.0)
        e = ease_out(u, 1.6)
        x = cx + px(160) + (W - px(300) - cx - px(160)) * e
        base = cy - px(260) + rnd(101, i) * px(520)
        y = base + math.sin(e * 6 + i) * px(70) * (1 - e)
        a = (1 - e) * 0.9 * k
        col = c2 if i % 4 == 0 else c1
        dot(cr, x, y, px(3.4), col, a)
        if i % 24 == 0 and e > 0.1:
            text_at(cr, x, y - px(18), ('+%d mg' % (3 + i % 17)), px(18), c2, 'cb',
                    FONT_EN, alpha=(1 - e) * 0.7 * k)
    # collection bar on the right
    bx = W - px(260)
    cr.save()
    cr.set_line_width(px(2))
    cr.set_source_rgba(*c1, 0.5)
    cr.rectangle(bx, cy - px(300), px(90), px(600))
    cr.stroke()
    cr.restore()
    fill = clamp01(s.p * 1.1)
    cr.save()
    cr.rectangle(bx + px(8), cy + px(300) - px(584) * fill, px(74), px(584) * fill)
    cr.set_source_rgba(*c2, 0.55)
    cr.fill()
    cr.restore()
    for i in range(9):
        cr.save()
        cr.set_line_width(px(1.2))
        cr.set_source_rgba(*c1, 0.35)
        yy = cy + px(300) - px(584) * i / 8
        cr.move_to(bx, yy); cr.line_to(bx + px(90), yy)
        cr.stroke()
        cr.restore()
    text_at(cr, bx + px(45), cy - px(330), 'INTAKE', px(22), c1, 'cb', FONT_EN,
            alpha=0.6 * k, spacing=4)


def tomato(cr, s):
    """If I'm a tomato — same plate, different specimen, tighter."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    hex_grid(cr, c1, alpha=0.04)
    cx, cy = W * 0.56, H * 0.56
    k = ease_out(clamp01(s.p * 1.3), 2.0)
    R = px(300) * (0.9 + 0.1 * k)
    # body
    cr.save()
    cr.translate(cx, cy)
    cr.scale(R, R * 0.94)
    cr.arc(0, 0, 1.0, 0, TAU)
    cr.set_source_rgba(*mix(c2, (0.35, 0.02, 0.02), 0.6), 0.94 * k)
    cr.fill()
    cr.restore()
    # lobes
    for i in range(5):
        a = TAU * i / 5 - math.pi / 2
        cr.save()
        cr.set_line_width(px(2))
        cr.set_source_rgba(0, 0, 0, 0.10 * k)
        cr.move_to(cx, cy)
        cr.line_to(cx + R * 0.9 * math.cos(a), cy + R * 0.88 * math.sin(a))
        cr.stroke()
        cr.restore()
    # highlight
    cr.save()
    cr.translate(cx - R * 0.34, cy - R * 0.38)
    cr.scale(R * 0.20, R * 0.14)
    cr.arc(0, 0, 1, 0, TAU)
    cr.set_source_rgba(1, 1, 1, 0.22 * k)
    cr.fill()
    cr.restore()
    # calyx
    for i in range(6):
        a = TAU * i / 6 - math.pi / 2
        _leaf(cr, cx + px(50) * math.cos(a), cy - R * 0.86 + px(20) * math.sin(a),
              px(62), a, shade(c2, 0.8), 0.85 * k)
    # label
    bx, by = px(140), H - px(300)
    cr.save()
    cr.set_line_width(px(1.4))
    cr.set_source_rgba(*c1, 0.35 * k)
    cr.rectangle(bx, by, px(430), px(180))
    cr.stroke()
    cr.restore()
    for i, line in enumerate(('SOLANUM LYCOPERSICUM', 'sample  %d' % (s.idx * 3 % 700 + 200),
                              'red  ·  ripe  ·  indexed')):
        text_at(cr, bx + px(24), by + px(34) + i * px(52), line, px(i and 22 or 24),
                c2 if i == 0 else c1, 'lt', FONT_EN,
                alpha=(0.85 if i == 0 else 0.5) * k, spacing=1.5)


def antioxidants(cr, s):
    """Then I will give you antioxidants — molecular rings dock and neutralise."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx = W / 2
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    # a big target molecule
    ring(cr, cx, H * 0.52, px(250), c1, 3.0, 0.6)
    for i in range(6):
        a = TAU * i / 6 + s.t * 0.3
        x = cx + px(250) * math.cos(a)
        y = H * 0.52 + px(250) * math.sin(a)
        dot(cr, x, y, px(13), c1, 0.8)
        cr.save()
        cr.set_line_width(px(2.4))
        cr.set_source_rgba(*c1, 0.6)
        cr.move_to(cx + px(150) * math.cos(a), H * 0.52 + px(150) * math.sin(a))
        cr.line_to(x, y)
        cr.stroke()
        cr.restore()
    ring(cr, cx, H * 0.52, px(150), c1, 2.0, 0.4, dash=(10, 12))
    # incoming radical attackers, absorbed on impact
    for i in range(58):
        u = ((s.t * 0.36 + rnd(103, i)) % 1.0)
        a = rnd(107, i) * TAU
        r0 = px(1100)
        r1 = px(240)
        rr = r0 + (r1 - r0) * ease_in(u, 2.0)
        x = cx + rr * math.cos(a)
        y = H * 0.52 + rr * math.sin(a)
        near = 1 - clamp01((u - 0.86) / 0.14)
        col = (1, 0.45, 0.35) if near < 0.5 else c2
        dot(cr, x, y, px(6.5), col, 0.25 + 0.7 * near)
        if near < 0.35:
            for j in range(5):
                b = rnd(109, i * 7 + j) * TAU
                dot(cr, x + px(30) * (1 - near / 0.35) * math.cos(b),
                    y + px(30) * (1 - near / 0.35) * math.sin(b), px(3),
                    c2, (1 - near / 0.35) * 0.8)
    glow(cr, cx, H * 0.52, px(520), c2, 0.14 * k, key='g_sec')
    text_at(cr, cx, H - px(110), 'free radicals  ·  neutralised  ·  %d' %
            int(58 * clamp01(s.t / 2.0)), px(24), c1, 'cb', FONT_EN, alpha=0.55,
            spacing=2)


def tabby(cr, s):
    """If I'm a tabby cat — the cat is drawn in one continuous line."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    hex_grid(cr, c1, alpha=0.04)
    cx, cy = W / 2, H * 0.58
    k = ease_out(clamp01(s.p * 1.15), 2.0)
    # ---- single-stroke cat -------------------------------------------------
    pts = []
    # body arc
    for i in range(60):
        u = i / 59.0
        a = math.pi * 0.15 + u * math.pi * 1.05
        pts.append((cx - px(230) + px(230) * math.cos(a) * 1.9,
                    cy + px(150) - px(150) * math.sin(a)))
    # back leg
    pts += [(cx + px(120), cy + px(150)), (cx + px(140), cy + px(240)),
            (cx + px(96), cy + px(240))]
    # front leg
    pts += [(cx - px(60), cy + px(240)), (cx - px(90), cy + px(150))]
    # head circle
    hx, hy, hr = cx - px(250), cy - px(60), px(120)
    for i in range(48):
        u = i / 47.0
        a = -math.pi * 0.9 + u * math.pi * 2.1
        pts.append((hx + hr * math.cos(a), hy + hr * math.sin(a)))
    # ears
    pts += [(hx - px(70), hy - px(96)), (hx - px(96), hy - px(196)),
            (hx - px(6), hy - px(120))]
    pts += [(hx + px(20), hy - px(120)), (hx + px(104), hy - px(190)),
            (hx + px(84), hy - px(84))]
    # tail
    for i in range(50):
        u = i / 49.0
        pts.append((cx + px(300) + px(150) * u,
                    cy - px(40) - px(190) * math.sin(u * 2.2) - px(60) * u))
    n = int(len(pts) * k)
    cr.save()
    cr.set_line_width(px(5))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_source_rgba(*c1, 0.92)
    cr.new_path()
    for i, p in enumerate(pts[:max(n, 2)]):
        if i == 0:
            cr.move_to(*p)
        else:
            cr.line_to(*p)
    cr.stroke()
    cr.restore()
    # the pen tip
    if 0 < n < len(pts):
        dot(cr, pts[n - 1][0], pts[n - 1][1], px(10), c2, 1.0)
        glow(cr, pts[n - 1][0], pts[n - 1][1], px(90), c2, 0.7, key='g_sec')
    # face details appear once the head is drawn
    if k > 0.75:
        a = smoothstep(0.75, 0.95, k)
        dot(cr, hx - px(44), hy - px(14), px(12), c2, a)
        dot(cr, hx + px(44), hy - px(14), px(12), c2, a)
        for i in range(4):
            dot(cr, hx - px(32) + i * px(22), hy + px(52), px(2.6), c1, a * 0.7)
        # whiskers
        for i, aa in enumerate((-0.35, 0.0, 0.35)):
            cr.save()
            cr.set_line_width(px(2))
            cr.set_source_rgba(*c2, a * 0.5)
            cr.move_to(hx + px(20), hy + px(30))
            cr.line_to(hx + px(300), hy + px(30) + px(140) * math.sin(aa))
            cr.stroke()
            cr.restore()
    # tabby stripes
    if k > 0.5:
        a = smoothstep(0.5, 0.8, k)
        for i in range(7):
            u = i / 6.0
            x = cx - px(140) + u * px(420)
            cr.save()
            cr.set_line_width(px(9))
            cr.set_source_rgba(*shade(c1, 1.5), a * 0.45)
            cr.move_to(x, cy - px(6) - px(60) * math.sin(u * math.pi))
            cr.line_to(x + px(18), cy + px(96) - px(60) * math.sin(u * math.pi))
            cr.stroke()
            cr.restore()
    text_at(cr, px(120), px(120), 'FELIS CATUS  ·  TABBY', px(24), c1, 'lt',
            FONT_EN, alpha=0.5, spacing=2)


def purr(cr, s):
    """Then I will purr for your enjoyment — the sound made visible."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # ribcage glow
    glow(cr, W / 2, H * 0.56, px(700), c2, 0.16, key='g_sec')
    # a low-frequency wave, amplitude-modulated like a purr (25 Hz carrier)
    y = H * 0.56
    for layer in range(3):
        cr.save()
        cr.set_line_width(px(3.4 - layer))
        cr.set_source_rgba(*(c2 if layer == 0 else c1), 0.85 - layer * 0.28)
        cr.new_path()
        n = 900
        for i in range(n + 1):
            u = i / n
            x = px(100) + (W - px(200)) * u
            env = 0.55 + 0.45 * math.sin(u * TAU * 2.6 - s.t * 3.4)
            v = math.sin(u * TAU * 26.0 + s.t * 30) * env
            yy = y + px(150 + layer * 40) * v
            if i == 0:
                cr.move_to(x, yy)
            else:
                cr.line_to(x, yy)
        cr.stroke()
        cr.restore()
    # radiating ripple rings
    for i in range(8):
        u = ((s.t * 0.8 + i / 8.0) % 1.0)
        ring(cr, W / 2, y, px(120) + px(760) * u, c2, 2.0, (1 - u) ** 1.4 * 0.5)
    text_at(cr, px(120), px(130), '25 Hz  ·  sustained', px(24), c1, 'lt', FONT_EN,
            alpha=0.5, spacing=2)
    # a small heart-rate trace
    waveform(cr, px(120), W - px(120), H - px(180), px(40), TAU * 3.2, s.t * 2.4,
             c2, 0.55, 2.0)


def only_god(cr, s):
    """If I'm the only God — a cathedral of light."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx = W / 2
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    # rays from a point above
    apex = (cx, -px(120))
    for i in range(26):
        a = math.pi * 0.22 + (math.pi * 0.56) * (i / 25.0)
        L = px(1700)
        cr.save()
        cr.set_line_width(px(30 + 60 * rnd(113, i)))
        cr.set_source_rgba(*(c2 if i % 3 == 0 else c1),
                           (0.05 + 0.09 * rnd(127, i)) * k * (0.6 + 0.4 * math.sin(s.t * 0.9 + i)))
        cr.move_to(*apex)
        cr.line_to(apex[0] + L * math.cos(a), apex[1] + L * math.sin(a))
        cr.stroke()
        cr.restore()
    # arches
    for i in range(5):
        rr = px(300 + i * 190)
        ring(cr, cx, H + px(60), rr, c1, 2.0 - i * 0.2, (0.36 - i * 0.05) * k)
    # halo
    glow(cr, cx, H * 0.30, px(500) * k, c2, 0.34 * k, key='g_sec')
    ring(cr, cx, H * 0.30, px(200) * (0.8 + 0.2 * k), c2, 3.0, 0.7 * k)
    ring(cr, cx, H * 0.30, px(240) * (0.8 + 0.2 * k), c2, 1.4, 0.4 * k, dash=(12, 16))
    # a tiny figure at the bottom
    fy = H - px(150)
    dot(cr, cx, fy - px(60), px(22), shade(c1, 0.5), 0.8 * k)
    poly(cr, [(cx - px(34), fy), (cx - px(18), fy - px(52)), (cx + px(18), fy - px(52)),
              (cx + px(34), fy)], shade(c1, 0.5), 0.8 * k, 3.0)


def proof(cr, s):
    """Then you're the proof of my existence — two nodes confirm each other."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.05, 60, 1.0)
    A = (W * 0.32, H * 0.50)
    B = (W * 0.68, H * 0.50)
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    # the link draws itself
    cr.save()
    cr.set_line_width(px(3.2))
    cr.set_source_rgba(*c2, 0.8)
    cr.move_to(*A)
    cr.line_to(A[0] + (B[0] - A[0]) * k, A[1] + (B[1] - A[1]) * k)
    cr.stroke()
    cr.restore()
    # packets crossing the link
    for i in range(16):
        u = ((s.t * 0.5 + i / 16.0) % 1.0) * k
        x = A[0] + (B[0] - A[0]) * u
        y = A[1] + (B[1] - A[1]) * u
        dot(cr, x, y, px(5.5), (1, 1, 1), 0.85)
    for P, col, lab in ((A, c1, 'YOU'), (B, c2, 'ME')):
        glow(cr, P[0], P[1], px(260) * k, col, 0.34 * k, key='g_%s' % lab)
        ring(cr, P[0], P[1], px(96) * (0.6 + 0.4 * k), col, 3.4, 0.9)
        ring(cr, P[0], P[1], px(128) * (0.6 + 0.4 * k), col, 1.6, 0.45, dash=(10, 12))
        dot(cr, P[0], P[1], px(20), col, 0.95)
        text_at(cr, P[0], P[1] + px(200), lab, px(34), col, 'ct', FONT_EN,
                weight=800, alpha=0.85 * k, spacing=10)
    if k > 0.9:
        a = smoothstep(0.9, 1.0, k)
        text_glow(cr, W / 2, H * 0.80, 'EXISTENCE VERIFIED', px(32), (1, 1, 1),
                  'cc', FONT_EN, alpha=a * 0.9, spacing=10)
