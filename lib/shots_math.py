# -*- coding: utf-8 -*-
"""shots_math — movement B: the program offers itself as geometry."""
import math
from render_lib import (W, H, TAU, px, mix, shade, clamp01, smoothstep, ease_out,
                        ease_in, pulse, text_at, text_glow, grad_rect, dashed_line,
                        arrow, dot, ring, poly, glow, blit, FONT_EN, FONT_ZH)
from scene_paint import (rnd, hex_grid, dot_field, grid_lines, crosshair, waveform,
                         wave_path, oscilloscope, pcb_network, concentric, orbit_ring,
                         target_rings, project, cube_faces)
import cairo


def points(cr, s):
    """If I'm a set of point — a cloud of points crystallises into a grid."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.06, 120, 1.0)
    n = 220
    k = ease_out(clamp01(s.p * 1.4), 2.0)
    for i in range(n):
        col = i % 20
        row = i // 20
        tx = px(150) + col * ((W - px(300)) / 19)
        ty = px(200) + row * ((H - px(400)) / 10)
        sx = rnd(11, i) * W
        sy = rnd(13, i) * H
        # stagger the arrival
        d = clamp01((k - rnd(17, i) * 0.35) / 0.65)
        d = ease_out(d, 2.2)
        x = sx + (tx - sx) * d
        y = sy + (ty - sy) * d
        a = 0.25 + 0.75 * d
        dot(cr, x, y, px(3.4), c2 if i % 7 == 0 else c1, a)
    # a slow scanning column reads the points
    sx = px(150) + (W - px(300)) * ((s.t * 0.55) % 1.0)
    cr.save()
    cr.set_line_width(px(1.6))
    cr.set_source_rgba(*c2, 0.30)
    cr.move_to(sx, px(150)); cr.line_to(sx, H - px(150))
    cr.stroke()
    cr.restore()
    text_at(cr, px(150), px(120), 'n = %d  ·  { p ∈ ℝ³ }' % n, px(24), c1, 'lt',
            FONT_EN, alpha=0.55, spacing=1.5)


def cube(cr, s):
    """Then I will give you my dimension — the cloud extrudes into 3D."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.4), 2.2)
    rx = math.radians(-22 + 6 * math.sin(s.t * 0.7))
    ry = math.radians(30) + s.t * 0.32
    cx, cy = W / 2, H * 0.52
    sz = px(200) * (0.35 + k * 0.9)
    # the wireframe grows out of the point field
    cr.save()
    v, faces = cube_faces(1.0)
    proj = [project(p, rx, ry) for p in v]
    for fi, f in enumerate(faces):
        pts = [(cx + proj[i][0] * sz, cy + proj[i][1] * sz) for i in f]
        depth = sum(proj[i][2] for i in f) / 4.0
        a = (0.30 + 0.35 * (1.0 - min(1.0, depth / 5.0))) * k
        poly(cr, pts, c2 if fi % 2 else c1, a, 1.8, close=True)
    # grid on three visible faces
    for fi in (0, 2, 3):
        f = faces[fi]
        for u in (0.25, 0.5, 0.75):
            for a_, b_ in ((0, 1), (1, 2)):
                p0 = [v[f[a_]][i] + (v[f[b_]][i] - v[f[a_]][i]) * u for i in range(3)]
                p1 = [v[f[(a_ + 1) % 4]][i] + (v[f[(b_ + 1) % 4]][i] -
                                               v[f[(a_ + 1) % 4]][i]) * u for i in range(3)]
                pr0 = project(p0, rx, ry); pr1 = project(p1, rx, ry)
                cr.save()
                cr.set_line_width(px(1.0))
                cr.set_source_rgba(*c1, 0.16 * k)
                cr.move_to(cx + pr0[0] * sz, cy + pr0[1] * sz)
                cr.line_to(cx + pr1[0] * sz, cy + pr1[1] * sz)
                cr.stroke()
                cr.restore()
    for pi, pr in enumerate(proj):
        dot(cr, cx + pr[0] * sz, cy + pr[1] * sz, px(5.5), c2, 0.95 * k)
    cr.restore()
    glow(cr, cx, cy, px(700), c1, 0.14 * k, key='g_key')
    # axis read-out
    for i, lab in enumerate(('x', 'y', 'z')):
        pr = project((1.6 if i == 0 else 0, 1.6 if i == 1 else 0, 1.6 if i == 2 else 0),
                     rx, ry)
        arrow(cr, cx, cy, cx + pr[0] * sz, cy + pr[1] * sz, c1, 1.6, 0.5 * k, 10)
        text_at(cr, cx + pr[0] * sz * 1.09, cy + pr[1] * sz * 1.09, lab, px(22),
                c1, 'cc', FONT_EN, alpha=0.6 * k)
    text_at(cr, cx, H - px(110), 'dimension = 3', px(26), c2, 'cb', FONT_EN,
            alpha=0.55 * k, spacing=3)


def circle(cr, s):
    """If I'm a circle — one circle drawn clean, on a measuring field."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.07, 60, 1.0)
    cx, cy = W / 2, H * 0.52
    R = px(330)
    k = ease_out(clamp01(s.p * 1.5), 2.0)
    # the circle is drawn by a rotating radius arm
    a = -math.pi / 2 + TAU * k
    cr.save()
    cr.set_line_width(px(4))
    cr.set_source_rgba(*c2, 0.95)
    cr.arc(cx, cy, R, -math.pi / 2, a)
    cr.stroke()
    cr.restore()
    cr.save()
    cr.set_line_width(px(2))
    cr.set_source_rgba(*c1, 0.75)
    cr.move_to(cx, cy)
    cr.line_to(cx + R * math.cos(a), cy + R * math.sin(a))
    cr.stroke()
    cr.restore()
    dot(cr, cx + R * math.cos(a), cy + R * math.sin(a), px(8), c2, 1.0)
    dot(cr, cx, cy, px(5), c2, 0.9)
    glow(cr, cx, cy, px(560), c1, 0.16 * k, key='g_key')
    # centre cross
    crosshair(cr, cx, cy, px(70), c1, 0.35)
    # radius label follows the arm
    mx = cx + R * 0.55 * math.cos(a)
    my = cy + R * 0.55 * math.sin(a)
    text_at(cr, mx, my - px(22), 'r', px(26), c2, 'cb', FONT_EN, alpha=0.85,
            italic=True)
    text_at(cr, px(150), px(120), 'x² + y² = r²', px(30), c1, 'lt', FONT_EN,
            alpha=0.6, spacing=2)


def circumf(cr, s):
    """Then I will give you my circumference — the outline becomes a ribbon."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    R = px(320)
    k = ease_out(clamp01(s.p * 1.5), 2.2)
    ring(cr, cx, cy, R, c1, 2.0, 0.35)
    # the circumference unwinds into a straight line of length 2πr
    L = TAU * R
    lx0 = px(140)
    y = H * 0.80
    d = k * min(1.0, (W - px(280)) / L)
    n = int(72 + 200 * k)
    for i in range(n):
        u = i / n
        a = -math.pi / 2 + TAU * u
        px_ = cx + R * math.cos(a)
        py_ = cy + R * math.sin(a)
        tx = lx0 + L * u * d
        ty = y
        if tx > W - px(80):
            break
        e = ease_out(clamp01((k - u * 0.45) / 0.55), 2.0)
        x = px_ + (tx - px_) * e
        yy = py_ + (ty - py_) * e
        dot(cr, x, yy, px(3.0), c2 if i % 4 == 0 else c1, 0.30 + 0.6 * e)
    # ruler under the unwound line
    cr.save()
    cr.set_line_width(px(1.6))
    cr.set_source_rgba(*c1, 0.45 * k)
    cr.move_to(lx0, y + px(26))
    cr.line_to(min(lx0 + L * d, W - px(80)), y + px(26))
    cr.stroke()
    cr.restore()
    for i in range(0, 21):
        x = lx0 + (W - px(280)) * i / 20 * min(1.0, d)
        if x > W - px(80):
            break
        h = px(16) if i % 5 == 0 else px(8)
        cr.save()
        cr.set_line_width(px(1.4))
        cr.set_source_rgba(*c1, 0.4 * k)
        cr.move_to(x, y + px(26))
        cr.line_to(x, y + px(26) + h)
        cr.stroke()
        cr.restore()
    text_at(cr, cx, cy - R - px(50), 'circumference = 2πr = %.2f r' % TAU, px(26),
            c2, 'cb', FONT_EN, alpha=0.7 * k, spacing=2)


def sine(cr, s):
    """If I'm a sine wave — a wave sweeps across a scope."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.06, 60, 1.0)
    y = H * 0.5
    for gi, (amp, ph, al, wd) in enumerate(((px(190), 0.0, 0.95, 3.0),
                                            (px(140), 1.0, 0.35, 1.6),
                                            (px(90), 2.1, 0.25, 1.4))):
        waveform(cr, px(110), W - px(110), y, amp * (0.3 + 0.7 * ease_out(s.p, 2.0)),
                 TAU * 1.6, ph + s.t * 1.6, c2 if gi == 0 else c1, al, wd)
    # the tracing point rides the wave
    phase = s.t * 1.6
    x = px(110) + (W - px(220)) * clamp01((s.t - s.t0) / 2.4)
    yy = y + px(190) * math.sin((x - px(110)) / (W - px(220)) * TAU * 1.6 + phase)
    dot(cr, x, yy, px(9), (1, 1, 1), 0.95)
    glow(cr, x, yy, px(120), c2, 0.7, key='g_sec')
    # axis labels
    text_at(cr, px(110), y - px(240), 'A = 1', px(22), c1, 'lt', FONT_EN, alpha=0.5)
    text_at(cr, W - px(110), y - px(240), 'y = sin(ωt + φ)', px(22), c1, 'rt',
            FONT_EN, alpha=0.5, spacing=1.5)


def tangent(cr, s):
    """Then you can sit on all my tangents — tangents slide along the curve."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.05, 48, 1.0)
    y0 = H * 0.54
    amp = px(180)
    k = ease_out(clamp01(s.p * 1.5), 2.2)
    waveform(cr, px(90), W - px(90), y0, amp, TAU * 2.2, s.t * 0.8, c1, 0.5, 2.0)
    # several tangents, each with a rider dot
    for i in range(5):
        u = ((s.t * 0.22 + i * 0.17) % 1.0)
        x = px(90) + (W - px(180)) * u
        ph = u * TAU * 2.2 + s.t * 0.8
        y = y0 + amp * math.sin(ph)
        slope = amp * math.cos(ph) * TAU * 2.2 / (W - px(180))
        L = px(230) * k
        dx = L / math.sqrt(1 + slope * slope)
        dy = slope * dx
        a = 0.22 + 0.5 * (1 - abs(u - 0.5) * 1.9)
        cr.save()
        cr.set_line_width(px(2.2))
        cr.set_source_rgba(*c2, max(0.0, a))
        cr.move_to(x - dx, y - dy)
        cr.line_to(x + dx, y + dy)
        cr.stroke()
        cr.restore()
        dot(cr, x, y, px(6.5), (1, 1, 1), 0.9)
        if i == 0:
            text_at(cr, x, y - px(44), 'tangent', px(22), c2, 'cb', FONT_EN,
                    alpha=0.8)
    text_at(cr, px(90), px(110), "dy/dx = cos(x)", px(26), c1, 'lt', FONT_EN,
            alpha=0.55, spacing=1.5)


def infinity(cr, s):
    """If I approach infinity — an endless zoom."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H / 2
    k = ease_out(clamp01(s.p * 1.2), 2.2)
    for i in range(16):
        u = ((s.t * 0.30 + i / 16.0) % 1.0)
        r = px(60) + px(900) * u
        a = (1 - u) ** 1.4 * 0.75 * k
        ring(cr, cx, cy, r, c2 if i % 3 == 0 else c1, 2.4 - u * 1.4, a)
    # the symbol itself, breathing in the centre
    glow(cr, cx, cy, px(520), c1, 0.24, key='g_key')
    w, h = px(360), px(170)
    cr.save()
    cr.set_line_width(px(7))
    cr.set_source_rgba(*c2, 0.95 * k)
    cr.new_path()
    for i in range(121):
        u = i / 120.0
        a = u * TAU
        # lemniscate of Bernoulli
        d = 1 + math.sin(a) ** 2
        x = cx + w * 0.55 * math.cos(a) / d
        yy = cy + h * 0.55 * math.cos(a) * math.sin(a) / d
        if i == 0:
            cr.move_to(x, yy)
        else:
            cr.line_to(x, yy)
    cr.stroke()
    cr.restore()
    # a number running away
    n = int(1 + 30 * ease_out(clamp01(s.p * 1.3), 2.0))
    text_at(cr, cx, H - px(150), 'n = ' + '9' * n, px(30), c1, 'cb', FONT_EN,
            alpha=0.6 * k, spacing=2)


def limits(cr, s):
    """Then you can be my limitations — an asymptote the curve never touches."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.06, 54, 1.0)
    xa = W * 0.66      # the asymptote
    y0 = H * 0.72
    cr.save()
    cr.set_line_width(px(2.4))
    cr.set_dash([px(16), px(12)])
    cr.set_source_rgba(*c2, 0.75)
    cr.move_to(xa, px(90)); cr.line_to(xa, H - px(90))
    cr.stroke()
    cr.restore()
    text_at(cr, xa + px(14), px(110), 'x → ∞   asymptote', px(22), c2, 'lt',
            FONT_EN, alpha=0.7, spacing=1.5)
    # curve hugging the asymptote
    cr.save()
    cr.set_line_width(px(3.4))
    cr.set_source_rgba(*c1, 0.95)
    cr.new_path()
    for i in range(400):
        u = i / 399.0
        x = px(120) + (float(xa) - px(120) + px(160)) * u
        yy = y0 - px(340) * (1.0 - math.exp(-u * 3.4))
        if i == 0:
            cr.move_to(x, yy)
        else:
            cr.line_to(x, yy)
    cr.stroke()
    cr.restore()
    # the gap that never closes, annotated
    gx = xa - px(6)
    gy = y0 - px(340) * (1.0 - math.exp(-3.4 * (1 - px(6) / (xa - px(120) + px(160)) + 1)))
    arrow(cr, gx - px(120), y0 - px(330), gx, y0 - px(340), c2, 1.6, 0.6, 12)
    text_at(cr, gx - px(140), y0 - px(350), 'never reached', px(22), c2, 'rb',
            FONT_EN, alpha=0.7)
    # a tiny creature sitting on the curve
    dot(cr, px(400), y0 - px(340) * (1 - math.exp(-3.4 * ((px(400) - px(120)) / (xa - px(120) + px(160))))),
        px(9), (1, 1, 1), 0.85 * ease_out(s.p, 2))
