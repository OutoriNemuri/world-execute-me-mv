# -*- coding: utf-8 -*-
"""shots_boot — movement A: the machine boots and builds a world."""
import math
from render_lib import (W, H, TAU, px, mix, shade, rgba, clamp01, smoothstep,
                        ease_out, ease_in, ease_io, pulse, flicker, text_at,
                        text_glow, grad_rect, dashed_line, arrow, dot, ring,
                        poly, glow, blit, vignette, FONT_EN, FONT_ZH)
from scene_paint import (rnd, hex_grid, dot_field, grid_lines, crosshair, wave_path,
                         waveform, audio_bars, oscilloscope, pcb_trace, pcb_network,
                         concentric, orbit_ring, target_rings, wire_box, project)
from render_lib import cached, text_w
import cairo


def _shatter(cr, cx, cy, t, c1, c2, alpha=0.9):
    """A dust burst used by several boot shots."""
    for i in range(40):
        a = rnd(7, i) * TAU
        sp = px(120 + rnd(7, i + 9) * 520)
        r = 0.4 + rnd(3, i) * 0.7
        x = cx + math.cos(a) * sp * t
        y = cy + math.sin(a) * sp * t * 0.82 + px(60) * t * t
        al = alpha * (1 - t) ** 1.6
        if al > 0.01:
            dot(cr, x, y, px(r * 2.4), c1 if i % 3 else c2, al)


def cold_open(cr, s):
    """00:00 Switch on the power line — a dead dark panel, one line lights up."""
    st, t = s.ctx.song, s.t
    c1 = st['key']
    hex_grid(cr, c1, alpha=0.05)
    # a horizontal power bus across the frame
    y = H * 0.52
    lit = smoothstep(0.05, 0.55, s.p)
    cr.save()
    cr.set_line_width(px(3))
    cr.set_source_rgba(c1[0], c1[1], c1[2], 0.25)
    cr.move_to(px(120), y)
    cr.line_to(W - px(120), y)
    cr.stroke()
    cr.restore()
    # the signal travels left → right
    xe = px(120) + (W - px(240)) * lit
    cr.save()
    cr.set_line_width(px(4))
    cr.set_source_rgba(*c1, 1.0)
    cr.move_to(px(120), y)
    cr.line_to(xe, y)
    cr.stroke()
    cr.restore()
    glow(cr, xe, y, px(160), c1, 0.85 * s.p, key='g_key')
    # breaker ticks
    for i in range(26):
        x = px(120) + (W - px(240)) * i / 25
        on = x <= xe
        dot(cr, x, y, px(4 if on else 2.6), c1 if on else st['sec'],
            0.95 if on else 0.28)
    # the whole grid wakes up
    lim = H * 0.06 + H * 0.42 * lit
    cr.save()
    cr.rectangle(0, 0, W, lim * 2)
    cr.clip()
    grid_lines(cr, c1, 0.10 * lit, 72, 1.0)
    cr.restore()
    text_at(cr, px(120), H - px(120), 'POWER LINE  ·  230V  ·  STANDBY → LIVE', px(22),
            st['sec'], 'lb', FONT_EN, spacing=2.0, alpha=0.6)


def breaker(cr, s):
    """Remember to put on protection — a safety interlock closes over the frame."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    p = ease_out(s.p, 2.4)
    dot_field(cr, c1, s.t, 11, 130, 0.35)
    # concentric shield rings closing in
    for i in range(5):
        rr = px(700 - i * 90) * (1.0 - p * 0.12) - px(30) * pulse(s.t, 0.5 + i * 0.1)
        ring(cr, W / 2, H / 2, rr, c2 if i % 2 else c1, 2.0,
             0.55 - i * 0.07, dash=(26, 16) if i % 2 else None)
    # a hatch barrier of chevrons wiping down
    for row in range(9):
        yy = H * (row / 9) * p + H * 0.02
        for col in range(22):
            x = px(40) + col * px(96)
            a = 0.22 * (1 - abs(row / 9 - 0.5) * 1.1) * p
            cr.save()
            cr.set_line_width(px(3))
            cr.set_source_rgba(c2[0], c2[1], c2[2], max(0, a))
            cr.move_to(x, yy + px(18))
            cr.line_to(x + px(18), yy)
            cr.line_to(x + px(36), yy + px(18))
            cr.stroke()
            cr.restore()
    ring(cr, W / 2, H / 2, px(250), c1, 3.0, 0.7 * p)
    ring(cr, W / 2, H / 2, px(250), c2, 3.0, 0.35 * p, dash=(12, 26), a0=s.t * 1.2,
         a1=s.t * 1.2 + TAU)
    text_glow(cr, W / 2, H * 0.5, 'PROTECTION', px(30), c2, 'cc', FONT_EN,
              alpha=0.55 * p, spacing=16)


def cad_parts(cr, s):
    """Lay down your pieces — parts fall onto a drafting table and settle."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.1, 96, 1.0)
    for i in range(14):
        fx = px(180) + rnd(3, i) * (W - px(360))
        fy = px(160) + rnd(5, i) * (H - px(320))
        drop = 1.0 - (1.0 - clamp01(s.p * 1.5 - i * 0.045)) ** 3
        y = fy - px(700) * (1 - drop)
        size = px(26 + rnd(9, i) * 44)
        kind = i % 4
        a = 0.2 + 0.8 * drop
        if kind == 0:
            poly(cr, [(fx, y), (fx + size, y), (fx + size, y + size),
                      (fx, y + size)], c2 if i % 3 else c1, a, 2.0, close=True)
        elif kind == 1:
            cr.save()
            cr.set_source_rgba(c1[0], c1[1], c1[2], a)
            cr.set_line_width(px(2))
            cr.arc(fx, y, size * 0.5, 0, TAU)
            cr.stroke()
            cr.restore()
        elif kind == 2:
            poly(cr, [(fx, y + size), (fx + size * 0.5, y),
                      (fx + size, y + size)], c1 if i % 3 else c2, a, 2.0, close=True)
        else:
            dot(cr, fx + size * 0.5, y + size * 0.5, size * 0.32, c2, a)
    # settle flash
    if s.p > 0.55:
        k = smoothstep(0.55, 0.75, s.p)
        glow(cr, W / 2, H / 2, px(1000), c1, 0.10 * k, key='g_key')
    text_at(cr, px(60), px(56), 'PARTS  14', px(20), c2, 'lt', FONT_EN,
            spacing=2.0, alpha=0.5)


def assemble(cr, s):
    """And let's begin object creation (first half) — a wireframe assembles."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cam = s.ctx.g('cam', s.idx, 0.6 + s.p * 0.9, 0.4 + s.p * 1.4)
    wire_box(cr, W / 2, H * 0.5, 1.5 + s.p * 0.7, cam[0], cam[1], c1, 0.32, 1.4)
    # vertices accumulate
    v, faces = None, None
    from scene_paint import cube_faces
    v, faces = cube_faces(1.0)
    n = int(2 + 6 * ease_out(s.p, 2.0))
    ssz = (1.5 + s.p * 0.7) * px(150) / 3.2
    for i, pt in enumerate(v[:n]):
        x, y, z = project(pt, cam[0], cam[1])
        dot(cr, W / 2 + x * ssz, H * 0.5 + y * ssz, px(7), c2, 0.95)
        ring(cr, W / 2 + x * ssz, H * 0.5 + y * ssz, px(15), c2, 1.4, 0.4)
    text_at(cr, W / 2, H - px(90), 'OBJECT  0x00  ·  UNDER CONSTRUCTION', px(22),
            c2, 'cb', FONT_EN, spacing=3.0, alpha=0.5)


def assemble2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.6), 2.4)
    glow(cr, W / 2, H / 2, px(700) * k, c1, 0.5, key='g_key')
    for i in range(3):
        r = px(150 + i * 130) * (0.5 + k * 1.1)
        ring(cr, W / 2, H / 2, r, c2 if i % 2 else c1, 3 - i * 0.6, 0.8 * (1 - i * 0.22) * k)
    _shatter(cr, W / 2, H / 2, clamp01((s.p - 0.15) * 1.2), c2, c1, 0.75)


def patchbay(cr, s):
    """Fill in my data parameters — a patch bay, cables plugging in."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    pcb_network(cr, 21, s.t * 0.4, c1, 0.16, 16, 1.4)
    n = 10
    for i in range(n):
        x = px(200) + (W - px(400)) * i / (n - 1)
        on = clamp01(s.p * 1.5 - i * 0.08)
        y0 = px(250)
        y1 = H - px(250)
        # socket
        ring(cr, x, y1, px(16), c1 if on < 0.5 else c2, 2.0, 0.5 + 0.5 * on)
        # cable snakes down and plugs in
        if on > 0:
            cr.save()
            cr.set_line_width(px(2.6))
            cr.set_source_rgba(c2[0], c2[1], c2[2], 0.35 + 0.6 * on)
            cr.new_path()
            cr.move_to(x, y0)
            yy = y0
            while yy < y1:
                u = (yy - y0) / (y1 - y0)
                cr.line_to(x + px(30) * math.sin(u * 5.0 + i) * (1 - on), yy)
                yy += px(14)
            cr.stroke()
            cr.restore()
            ring(cr, x, y1, px(8) * on, c2, 2.0, on)
        else:
            dashed_line(cr, x, y0, x, y1, 8, 10, 1.6, c1, 0.25)
    # parameter read-out
    vals = ['dim=3', 'mass=1.0', 'phase=0.0', 'idx=%d' % int(s.t * 7 % 999),
            'temp=36.6', 'seed=%d' % int(s.t * 13 % 997)]
    for i, v in enumerate(vals):
        a = 0.28 + 0.5 * abs(math.sin(s.t * 1.3 + i))
        text_at(cr, px(200) + (W - px(400)) * i / (len(vals) - 1), H - px(120),
                v, px(20), c2, 'cb', FONT_EN, alpha=a, spacing=1.0)


def init(cr, s):
    """Initialization — a boot ROM dump scrolls and then snaps to one word."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    hex_grid(cr, c1, alpha=0.07)
    rows = 16
    for i in range(rows):
        y = px(120) + i * px(52)
        seedline = ''.join('%X' % (int(rnd(i * 3, j) * 16)) for j in range(28))
        a = 0.10 + 0.22 * rnd(i, 3)
        text_at(cr, px(200), y, seedline, px(24), c1, 'lt', FONT_EN, alpha=a,
                spacing=3.0)
    # the scan bar
    yb = px(120) + (H - px(300)) * ((s.t * 1.6) % 1.0)
    grad_rect(cr, px(140), yb - px(30), W - px(280), px(60), c2, c1, True, 0.10)
    k = ease_out(smoothstep(0.45, 0.9, s.p), 2.0)
    if k > 0:
        glow(cr, W / 2, H / 2, px(900 + 200 * k), c1, 0.16 * k, key='g_key')
    text_glow(cr, W / 2, H / 2, 'INITIALIZATION', px(84), c2, 'cc', FONT_EN,
              weight=700, alpha=k, spacing=10)


def blueprint(cr, s):
    """Set up our new world — a world grid unfolds in perspective."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    horizon = H * 0.42
    p = ease_out(s.p, 2.0)
    # perspective floor
    cr.save()
    cr.set_line_width(px(1.4))
    for i in range(-14, 15):
        x0 = W / 2 + i * px(60)
        cr.set_source_rgba(c1[0], c1[1], c1[2], 0.22)
        cr.move_to(x0, horizon)
        cr.line_to(W / 2 + i * px(420), H)
        cr.stroke()
    nrows = 18
    for i in range(1, nrows + 1):
        u = (i / nrows) ** 2.0 * p
        y = horizon + (H - horizon) * u
        a = 0.10 + 0.30 * (1 - i / nrows)
        cr.set_source_rgba(c1[0], c1[1], c1[2], a)
        cr.move_to(0, y)
        cr.line_to(W, y)
        cr.stroke()
    cr.restore()
    # the horizon line + a rising sun of wireframe
    cr.save()
    cr.set_line_width(px(2.4))
    cr.set_source_rgba(c2[0], c2[1], c2[2], 0.55 * p)
    cr.move_to(0, horizon)
    cr.line_to(W, horizon)
    cr.stroke()
    cr.restore()
    if s.p > 0.35:
        k = smoothstep(0.35, 0.9, s.p)
        cr.save()
        cr.arc(W / 2, horizon, px(210) * k, math.pi, TAU)
        cr.clip()
        for i in range(9):
            yy = horizon - px(210) + i * px(26)
            a = 0.5 - i * 0.04
            cr.set_line_width(px(1.6))
            cr.set_source_rgba(c2[0], c2[1], c2[2], max(0, a))
            cr.move_to(W / 2 - px(240), yy)
            cr.line_to(W / 2 + px(240), yy)
            cr.stroke()
        cr.restore()
        glow(cr, W / 2, horizon, px(460) * k, c2, 0.28 * k, key='g_sec')


def blueprint2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.4), 2.2)
    horizon = H * 0.42
    for i in range(6):
        u = (i + 1) / 6
        cr.save()
        cr.set_line_width(px(2))
        cr.set_source_rgba(*c2, 0.5 * (1 - u) * k)
        yy = horizon - px(40) * u
        cr.move_to(px(200) - px(120) * u, yy)
        cr.line_to(W - px(200) + px(120) * u, yy)
        cr.stroke()
        cr.restore()
    glow(cr, W / 2, horizon, px(900) * k, c2, 0.22 * k, key='g_sec')
    # the world "locks in": a title plate
    if k > 0.5:
        text_at(cr, W / 2, H * 0.72, 'OUR NEW WORLD', px(30), c2, 'cc', FONT_EN,
                alpha=(k - 0.5) * 1.6 * 0.8, spacing=16)


def ignition(cr, s):
    """And let's begin the simulation (first half) — a spark fires."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.09, 84, 1.0)
    cx, cy = W / 2, H / 2
    k = ease_out(clamp01(s.p * 1.3), 2.6)
    # capacitor plates charging
    for i, sgn in ((0, -1), (1, 1)):
        x = cx + sgn * px(210)
        grad_rect(cr, x - px(10), cy - px(180), px(20), px(360), c1, shade(c1, 0.3), False, 0.85)
        for j in range(9):
            x2 = x + sgn * px(40 + j * 26) * k
            dot(cr, x2, cy, px(3.5), c2, 0.7 * k)
    glow(cr, cx, cy, px(340) * k, c2, 0.5 * k, key='g_sec')
    if s.p > 0.72:
        _shatter(cr, cx, cy, smoothstep(0.72, 1.0, s.p), c2, (1, 1, 1), 0.9)
    ring(cr, cx, cy, px(230), c2, 2.4, 0.6 * k, dash=(18, 22), a0=s.t * 2.0,
         a1=s.t * 2.0 + TAU)


def ignition2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.5), 2.6)
    glow(cr, W / 2, H / 2, px(1200) * k, c2, 0.34 * k, key='g_sec')
    for i in range(4):
        r = px(120 + i * 180) * (0.2 + k * 1.15)
        ring(cr, W / 2, H / 2, r, c2, 3.0 - i * 0.4, (0.9 - i * 0.16) * k)
    _shatter(cr, W / 2, H / 2, clamp01((s.p - 0.2) * 1.1), c2, c1, 0.85)
    if s.p > 0.55:
        a = smoothstep(0.55, 1.0, s.p)
        text_at(cr, W / 2, H / 2, 'SIMULATION', px(96), (1, 1, 1), 'cc', FONT_EN,
                weight=900, alpha=a * 0.9, spacing=24)


def execution_run(cr, s):
    """I will run the execution — a program counter starts stepping."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    pcb_network(cr, 33, s.t * 0.5, c1, 0.2, 14, 1.4)
    # a bar that fills with executed instructions
    x0, x1 = px(220), W - px(220)
    y = H * 0.58
    cr.save()
    cr.set_line_width(px(3))
    cr.set_source_rgba(c1[0], c1[1], c1[2], 0.3)
    cr.move_to(x0, y); cr.line_to(x1, y); cr.stroke()
    cr.restore()
    xe = x0 + (x1 - x0) * smoothstep(0, 1, s.p)
    cr.save()
    cr.set_line_width(px(6))
    cr.set_source_rgba(*c2, 0.95)
    cr.move_to(x0, y); cr.line_to(xe, y); cr.stroke()
    cr.restore()
    for i in range(34):
        x = x0 + (x1 - x0) * i / 33
        on = x <= xe
        dot(cr, x, y, px(4.5 if on else 2.4), c2 if on else c1, 0.95 if on else 0.25)
    glow(cr, xe, y, px(180), c2, 0.7 * s.p, key='g_sec')
    for i in range(5):
        a = 0.35 + 0.4 * abs(math.sin(s.t * 2 + i))
        text_at(cr, x0, y - px(60) - i * px(0), 'EXEC 0x%04X' % (0x1A00 + i * 0x40),
                px(20), c1, 'lb', FONT_EN, alpha=a * s.p, spacing=1.5) if i == 0 else None
    text_at(cr, x1, y - px(60), 'PC →', px(20), c2, 'rb', FONT_EN, alpha=0.6 * s.p)
