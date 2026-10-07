# -*- coding: utf-8 -*-
"""shots_trance — movements D/F: the trance, the confession, the collapse."""
import math
from render_lib import (W, H, TAU, px, mix, shade, clamp01, smoothstep, ease_out,
                        ease_in, pulse, text_at, text_glow, grad_rect, dashed_line,
                        arrow, dot, ring, poly, glow, blit, FONT_EN, FONT_ZH)
from scene_paint import (rnd, hex_grid, dot_field, grid_lines, crosshair, waveform,
                         oscilloscope, pcb_network, concentric, orbit_ring,
                         target_rings, project)
import cairo


def then_i_can(cr, s):
    """Then I can, then I can — a door unlocks."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H / 2
    k = ease_out(clamp01(s.p * 1.6), 2.2)
    glow(cr, cx, cy, px(340 + 500 * k), c2, 0.5 * k, key='g_sec')
    for i in range(3):
        r = px(150 + i * 120) * (0.4 + k * 1.1)
        ring(cr, cx, cy, r, c2 if i == 0 else c1, 3.4 - i * 0.8, (0.9 - i * 0.24) * k)
    # keyhole
    if k > 0.4:
        cr.save()
        cr.set_source_rgba(0, 0, 0, 0.55 * smoothstep(0.4, 1.0, k))
        cr.arc(cx, cy - px(30), px(40), 0, TAU)
        cr.fill()
        cr.rectangle(cx - px(22), cy - px(10), px(44), px(90))
        cr.fill()
        cr.restore()


def then_i_can2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.6), 2.4)
    cx, cy = W / 2, H / 2
    # the door swings open: a bright wedge grows
    cr.save()
    cr.move_to(cx, cy)
    a0 = -math.pi / 2
    cr.arc(cx, cy, px(1400) * k, a0, a0 + px(0.001) + 0.9 * k)
    cr.close_path()
    cr.set_source_rgba(*c2, 0.12 * k)
    cr.fill()
    cr.restore()
    glow(cr, cx, cy, px(900) * k, c2, 0.4 * k, key='g_sec')
    for i in range(4):
        ring(cr, cx, cy, px(120 + i * 150) * (0.3 + k), c2, 2.6, 0.4 * k - i * 0.06)


def satisfaction(cr, s):
    """Be your only satisfaction — a full-bar graph that never empties."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    # bar chart / equalizer
    n = 34
    for i in range(n):
        u = i / (n - 1.0)
        x = px(300) + u * (W - px(600))
        h = px(420) * (0.25 + 0.75 * abs(math.sin(u * 3.2 + s.t * 1.1))) * k
        a = 0.35 + 0.5 * (1 - abs(u - 0.5) * 2)
        cr.save()
        cr.rectangle(x - px(9), cy + px(230) - h, px(18), h)
        cr.set_source_rgba(*(c2 if i % 2 else c1), a)
        cr.fill()
        cr.restore()
    dashed_line(cr, px(260), cy + px(230), W - px(260), cy + px(230), 8, 10, 1.4, c1, 0.4)
    # "100%" readout that pulses at full
    pct = min(100.0, 100.0 * k * (1.0 + 0.02 * math.sin(s.t * 6)))
    text_glow(cr, cx, cy - px(330), '%.0f%%' % pct, px(120), c2, 'cc', FONT_EN,
              weight=800, alpha=0.9 * k)
    text_at(cr, cx, cy + px(300), 'satisfaction', px(30), c1, 'ct', FONT_EN,
            alpha=0.6 * k, spacing=10)


def make_happy(cr, s):
    """If I can make you happy — a smile drawn as a curve, then filled with colour."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.48
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    # an arc drawn as the smile
    cr.save()
    cr.set_line_width(px(14))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(*c2, 0.9)
    cr.arc(cx, cy - px(60), px(230), math.pi * 0.20, math.pi * 0.20 + math.pi * 0.60 * k)
    cr.stroke()
    cr.restore()
    # eyes
    ea = smoothstep(0.3, 0.7, k)
    for sgn in (-1, 1):
        cr.save()
        cr.set_line_width(px(10))
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgba(*c1, 0.9 * ea)
        cr.arc(cx + sgn * px(120), cy - px(190), px(34), math.pi * 1.15, math.pi * 1.85)
        cr.stroke()
        cr.restore()
    glow(cr, cx, cy, px(700), c2, 0.18 * k, key='g_sec')
    # warmth particles rising
    for i in range(48):
        u = ((s.t * 0.30 + rnd(131, i)) % 1.0)
        x = cx + (rnd(137, i) - 0.5) * px(900)
        y = cy + px(240) - u * px(620)
        a = (1 - u) * 0.55 * k
        dot(cr, x, y, px(2.6 + rnd(139, i) * 3.5), c2, a)


def vibrations(cr, s):
    """Feel your vibrations — a string vibrates and its harmonics appear."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.3), 2.0)
    # the string
    y = H * 0.52
    x0, x1 = px(160), W - px(160)
    for h in range(1, 6):
        amp = px(190) * k / h
        cr.save()
        cr.set_line_width(px(3.4 - h * 0.4))
        cr.set_source_rgba(*(c2 if h == 1 else c1), 0.9 / h)
        cr.new_path()
        n = 300
        for i in range(n + 1):
            u = i / n
            x = x0 + (x1 - x0) * u
            yy = y + amp * math.sin(u * math.pi * h) * math.cos(s.t * (6.0 - h))
            if i == 0:
                cr.move_to(x, yy)
            else:
                cr.line_to(x, yy)
        cr.stroke()
        cr.restore()
    # fixed ends
    for x in (x0, x1):
        dot(cr, x, y, px(11), c1, 0.9)
        ring(cr, x, y, px(24), c1, 2.0, 0.4)
    glow(cr, W / 2, y, px(700), c2, 0.14 * k, key='g_sec')
    # frequency labels
    for h in range(1, 6):
        text_at(cr, x0 - px(30), y - px(10) + (h - 3) * px(34), '%d×' % h, px(20),
                c1, 'rc', FONT_EN, alpha=(0.7 / h) * k)


def completion(cr, s):
    """Finally be completion — a shape closes into a complete thing."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    # incomplete ring slowly closes
    a_end = -math.pi / 2 + TAU * k
    ring(cr, cx, cy, px(320), c1, 2.0, 0.25)
    cr.save()
    cr.set_line_width(px(7))
    cr.set_source_rgba(*c2, 0.95)
    cr.arc(cx, cy, px(320), -math.pi / 2, a_end)
    cr.stroke()
    cr.restore()
    # inner geometry assembles
    for i in range(6):
        a0 = TAU * i / 6 - math.pi / 2
        a1 = TAU * ((i + 2) % 6) / 6 - math.pi / 2
        if k > i / 8.0:
            aa = smoothstep(i / 8.0, min(1.0, i / 8.0 + 0.3), k)
            x1 = cx + px(320) * math.cos(a0); y1 = cy + px(320) * math.sin(a0)
            x2 = cx + px(320) * math.cos(a1); y2 = cy + px(320) * math.sin(a1)
            cr.save()
            cr.set_line_width(px(2.4))
            cr.set_source_rgba(*c1, 0.75 * aa)
            cr.move_to(x1, y1)
            cr.line_to(x1 + (x2 - x1) * aa, y1 + (y2 - y1) * aa)
            cr.stroke()
            cr.restore()
    glow(cr, cx, cy, px(420 + 500 * k), c2, 0.30 * k, key='g_sec')
    if k > 0.92:
        text_glow(cr, cx, cy, 'COMPLETE', px(56), (1, 1, 1), 'cc', FONT_EN,
                  weight=800, alpha=smoothstep(0.92, 1.0, k), spacing=14)
