# -*- coding: utf-8 -*-
"""shots_elec — movement C/E: current, gender, the swap.  Heat and copper."""
import math
from render_lib import (W, H, TAU, px, mix, shade, clamp01, smoothstep, ease_out,
                        ease_in, pulse, text_at, text_glow, grad_rect, dashed_line,
                        arrow, dot, ring, poly, glow, blit, FONT_EN, FONT_ZH)
from scene_paint import (rnd, hex_grid, dot_field, grid_lines, crosshair, waveform,
                         wave_path, oscilloscope, pcb_network, pcb_trace, concentric,
                         orbit_ring, target_rings)
import cairo


def _coil(cr, cx, cy, r, turns, t, col, alpha, w=3.0):
    cr.save()
    cr.set_line_width(px(w))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(*col, alpha)
    cr.new_path()
    n = 420
    for i in range(n + 1):
        u = i / n
        a = turns * TAU * u + t * 1.4
        rr = r * (0.55 + 0.45 * u)
        x = cx + rr * math.cos(a)
        y = cy + rr * math.sin(a) * 0.42
        if i == 0:
            cr.move_to(x, y)
        else:
            cr.line_to(x, y)
    cr.stroke()
    cr.restore()


def current(cr, s):
    """Switch my current — a copper trace with electrons streaming through it."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    pcb_network(cr, 7, s.t * 0.3, c1, 0.18, 12, 1.4)
    ry = H * 0.54
    pts = [(px(120), ry), (px(560), ry), (px(560), H * 0.34), (W - px(560), H * 0.34),
           (W - px(560), ry), (W - px(120), ry)]
    pcb_trace(cr, pts, c1, 0.5, 3.4, pads=True, r=7)
    # electron flow along the path
    segs = list(zip(pts[:-1], pts[1:]))
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs)
    for k in range(70):
        u = ((s.t * 0.34 + k / 70.0) % 1.0)
        d = u * total
        for a, b in segs:
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if d <= L:
                f = d / max(L, 1e-6)
                x = a[0] + (b[0] - a[0]) * f
                y = a[1] + (b[1] - a[1]) * f
                dot(cr, x, y, px(5.0), c2, 0.35 + 0.6 * abs(math.sin(s.t * 3 + k)))
                break
            d -= L
    glow(cr, W / 2, ry, px(520), c1, 0.14, key='g_key')


def switch_ac(cr, s):
    """To AC — the current turns into an alternating wave."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.06, 60, 1.0)
    y = H * 0.5
    k = ease_out(s.p, 2.0)
    for i in range(3):
        amp = px(60 + i * 60) * k
        waveform(cr, px(120), W - px(120), y, amp, TAU * 1.1, s.t * (1.4 + i * 0.2),
                 c2 if i == 1 else c1, 0.85 - i * 0.24, 3.0 - i * 0.7)
    text_at(cr, W / 2, y - px(300), 'AC', px(150), c2, 'cc', FONT_EN, weight=900,
            alpha=0.16 * k, spacing=20)
    text_at(cr, px(120), px(120), '~  alternating', px(26), c2, 'lt', FONT_EN,
            alpha=0.7 * k, spacing=2)


def switch_dc(cr, s):
    """To DC — flattened into a single unidirectional line."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.06, 60, 1.0)
    y = H * 0.5
    k = ease_out(s.p, 2.0)
    # the wave morphs: sine → rectified → straight
    cr.save()
    cr.set_line_width(px(3.2))
    cr.set_source_rgba(*c2, 0.95)
    cr.new_path()
    n = 300
    for i in range(n + 1):
        u = i / n
        x = px(120) + (W - px(240)) * u
        sine = math.sin(u * TAU * 1.1 + s.t * 1.4)
        flat = 1.0 - math.exp(-u * 4.0)
        v = sine * (1 - k) + flat * k
        yy = y + px(200) * v
        if i == 0:
            cr.move_to(x, yy)
        else:
            cr.line_to(x, yy)
    cr.stroke()
    cr.restore()
    for i in range(3):
        dashed_line(cr, px(120), y + px(60 + i * 40), W - px(120), y + px(60 + i * 40),
                    6, 12, 1.2, c1, 0.12)
    text_at(cr, W / 2, y - px(300), 'DC', px(150), c1, 'cc', FONT_EN, weight=900,
            alpha=0.16, spacing=20)
    text_at(cr, px(120), px(120), '⎓  direct', px(26), c1, 'lt', FONT_EN,
            alpha=0.7, spacing=2)


def blind(cr, s):
    """And then blind my vision — the picture is torn away."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    p = ease_out(s.p, 1.6)
    # a bright arc flash that swells and collapses
    glow(cr, W / 2, H / 2, px(1200), (1, 0.95, 0.8), 0.9 * math.sin(min(p, 0.55) * math.pi / 0.55), key='g_warm')
    # horizontal shutters close over the frame
    bars = 22
    for i in range(bars):
        u = i / (bars - 1.0)
        d = clamp01((p - u * 0.35) / 0.65)
        e = ease_out(d, 2.6)
        h = px(200) * e
        y = H * u
        cr.save()
        cr.set_source_rgba(shade(c1, 0.12)[0], shade(c1, 0.12)[1], shade(c1, 0.12)[2], e)
        cr.rectangle(0, y - h / 2, W, h)
        cr.fill()
        cr.restore()
    # the last sliver of light
    if p < 0.9:
        cr.save()
        cr.rectangle(0, H * 0.5 - px(4), W, px(8))
        cr.set_source_rgba(*c2, (1 - p / 0.9) * 0.7)
        cr.fill()
        cr.restore()
    for i in range(9):
        a = (1 - p) * 0.4 * rnd(3, i)
        dot(cr, rnd(5, i) * W, rnd(9, i) * H, px(3), c2, a)


def spin(cr, s):
    """So dizzy, so dizzy — the frame itself loses its footing."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H / 2
    k = ease_out(s.p, 1.6)
    # spiral
    cr.save()
    cr.set_line_width(px(2.4))
    cr.set_source_rgba(*c2, 0.7)
    cr.new_path()
    n = 620
    for i in range(n + 1):
        u = i / n
        a = u * TAU * 7 + s.t * 4.0
        r = px(60) + px(560) * u
        x = cx + r * math.cos(a) * (0.45 + 0.55 * u)
        y = cy + r * math.sin(a) * 0.55
        if i == 0:
            cr.move_to(x, y)
        else:
            cr.line_to(x, y)
    cr.stroke()
    cr.restore()
    # orbit rings tilt and slip
    for i in range(7):
        rr = px(140 + i * 90)
        wob = math.sin(s.t * 3.1 + i * 0.7) * px(40) * k
        cr.save()
        cr.translate(cx, cy + wob)
        cr.scale(1.0, 0.35 + 0.25 * math.sin(s.t * 2.2 + i))
        cr.rotate(s.t * (0.9 + i * 0.14))
        ring(cr, 0, 0, rr, c2 if i % 2 else c1, 2.2, 0.55 - i * 0.05)
        cr.restore()
    glow(cr, cx, cy, px(620), c2, 0.20 * k, key='g_sec')
    # nystagmus: a couple of ghosted duplicates of the whole idea
    for i, off in enumerate((px(26), -px(26))):
        ring(cr, cx + off, cy + off * 0.4, px(300), c1, 1.6, 0.14)


def travel(cr, s):
    """Oh, we can travel — a starfield rush."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H / 2
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    n = 260
    for i in range(n):
        a = rnd(23, i) * TAU
        sp = 0.25 + rnd(29, i) * 1.1
        u = ((s.t * 0.55 * sp + rnd(31, i)) % 1.0)
        r0 = px(40)
        r1 = px(1500)
        rr = r0 + (r1 - r0) * u ** 2.0
        x = cx + math.cos(a) * rr
        y = cy + math.sin(a) * rr * 0.62
        L = px(24 + 90 * u) * k
        dx = math.cos(a) * L * u
        dy = math.sin(a) * L * u * 0.62
        cr.save()
        cr.set_line_width(px(1.0 + 2.6 * u))
        cr.set_source_rgba(*(c2 if i % 5 == 0 else c1), 0.12 + 0.65 * u)
        cr.move_to(x - dx, y - dy)
        cr.line_to(x, y)
        cr.stroke()
        cr.restore()
    glow(cr, cx, cy, px(420), c1, 0.16, key='g_key')
    # travel markers
    for i, lab in enumerate(('AD', 'BC', 'α', 'Ω', '∞')):
        x = px(200) + i * px(320)
        text_at(cr, x, H - px(110), lab, px(26), c1, 'cb', FONT_EN,
                alpha=0.32 + 0.25 * abs(math.sin(s.t * 2 + i)), spacing=3)


def ad(cr, s):
    """To AD — the years run forward."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.05, 44, 1.0)
    k = ease_out(s.p * 1.6, 2.0)
    # a timeline running off to the right
    y = H * 0.5
    cr.save()
    cr.set_line_width(px(2.6))
    cr.set_source_rgba(*c1, 0.4)
    cr.move_to(px(120), y); cr.line_to(W - px(120), y)
    cr.stroke()
    cr.restore()
    for i in range(26):
        u = i / 25.0
        x = px(120) + (W - px(240)) * u
        on = u <= k
        h = px(30 if i % 5 else 54)
        cr.save()
        cr.set_line_width(px(2))
        cr.set_source_rgba(*(c2 if on else c1), 0.8 if on else 0.2)
        cr.move_to(x, y - h / 2); cr.line_to(x, y + h / 2)
        cr.stroke()
        cr.restore()
    text_at(cr, W / 2, y - px(140), 'AD', px(190), c2, 'cc', FONT_EN, weight=900,
            alpha=0.9 * k, spacing=14)
    text_at(cr, W / 2, y + px(96), '公元后', px(34), c2, 'cc', FONT_ZH,
            alpha=0.7 * k, spacing=12)


def bc(cr, s):
    """To BC — and the years run backward."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.05, 44, 1.0)
    k = ease_out(s.p * 1.6, 2.0)
    y = H * 0.5
    cr.save()
    cr.set_line_width(px(2.6))
    cr.set_source_rgba(*c1, 0.4)
    cr.move_to(px(120), y); cr.line_to(W - px(120), y)
    cr.stroke()
    cr.restore()
    # ticks march leftward
    for i in range(26):
        u = i / 25.0
        x = W - px(120) - (W - px(240)) * (u * k)
        cr.save()
        cr.set_line_width(px(2))
        cr.set_source_rgba(*(c2 if u <= k else c1), 0.85 if u <= k else 0.2)
        cr.move_to(x, y - px(28)); cr.line_to(x, y + px(28))
        cr.stroke()
        cr.restore()
    text_at(cr, W / 2, y - px(140), 'BC', px(190), c2, 'cc', FONT_EN, weight=900,
            alpha=0.9 * k, spacing=14)
    text_at(cr, W / 2, y + px(96), '公元前', px(34), c2, 'cc', FONT_ZH,
            alpha=0.7 * k, spacing=12)


def unite(cr, s):
    """And we can unite — two lines converge."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(s.p * 1.4, 2.2)
    cy = H / 2
    top = cy - px(300) * (1 - k)
    bot = cy + px(300) * (1 - k)
    waveform(cr, px(100), W - px(100), top, px(80) * (1 - k * 0.6), TAU * 1.4,
             s.t * 1.2, c1, 0.8, 2.6)
    waveform(cr, px(100), W - px(100), bot, px(80) * (1 - k * 0.6), TAU * 1.4,
             s.t * 1.2 + math.pi, c2, 0.8, 2.6)
    # the seam
    if k > 0.55:
        a = smoothstep(0.55, 1.0, k)
        cr.save()
        cr.set_line_width(px(5))
        cr.set_source_rgba(*(1, 1, 1), a * 0.85)
        cr.move_to(px(100), cy); cr.line_to(W - px(100), cy)
        cr.stroke()
        cr.restore()
        glow(cr, W / 2, cy, px(900), c2, 0.30 * a, key='g_sec')


def deep1(cr, s):
    """So deeply, so deeply — plunge."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.42
    k = ease_out(s.p, 1.8)
    # concentric depth rings falling inward
    for i in range(18):
        u = ((k * 1.4 + i / 18.0) % 1.0)
        r = px(1000) * (1 - u)
        ring(cr, cx, cy, max(r, 1), c2 if i % 3 == 0 else c1, 3.0, u ** 1.6 * 0.8)
    # a vertical shaft of light
    grad_rect(cr, cx - px(120), 0, px(240), H, c2, (0.02, 0.03, 0.06), True, 0.20 * k)
    text_at(cr, cx, H - px(110), 'depth = %.1f m' % (s.t * 12), px(24), c1, 'cb',
            FONT_EN, alpha=0.5, spacing=2)


def deep2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(s.p, 1.8)
    for i in range(22):
        u = ((k * 1.6 + i / 22.0) % 1.0)
        r = px(1100) * (1 - u)
        ring(cr, cx, cy, max(r, 1), c1 if i % 2 else c2, 3.2, u ** 1.5 * 0.7)
    glow(cr, cx, cy, px(300) * k, c2, 0.4 * k, key='g_sec')


def gender(cr, s):
    """Switch my gender — the two symbols overlap and swap."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.05, 70, 1.0)
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.4), 2.0)
    off = px(300) * (1 - k)
    # ♀ — circle with a cross below
    def female(x, y, a, col):
        ring(cr, x, y, px(130), col, 4.0, a)
        cr.save()
        cr.set_line_width(px(4))
        cr.set_source_rgba(*col, a)
        cr.move_to(x, y + px(130)); cr.line_to(x, y + px(220))
        cr.move_to(x - px(46), y + px(178)); cr.line_to(x + px(46), y + px(178))
        cr.stroke()
        cr.restore()

    def male(x, y, a, col):
        ring(cr, x, y, px(130), col, 4.0, a)
        cr.save()
        cr.set_line_width(px(4))
        cr.set_source_rgba(*col, a)
        cr.move_to(x + px(92), y - px(92)); cr.line_to(x + px(196), y - px(196))
        cr.move_to(x + px(196), y - px(196)); cr.line_to(x + px(126), y - px(196))
        cr.move_to(x + px(196), y - px(196)); cr.line_to(x + px(196), y - px(126))
        cr.stroke()
        cr.restore()

    female(cx - off, cy, 0.85, c2)
    male(cx + off, cy, 0.85, c1)
    # a compass rose behind
    for i in range(12):
        a = TAU * i / 12
        ring(cr, cx, cy, px(360), c1, 1.2, 0.08)
        cr.save()
        cr.set_line_width(px(1.4))
        cr.set_source_rgba(*c1, 0.2)
        cr.move_to(cx + px(340) * math.cos(a), cy + px(340) * math.sin(a))
        cr.line_to(cx + px(372) * math.cos(a), cy + px(372) * math.sin(a))
        cr.stroke()
        cr.restore()
    text_at(cr, cx - off, cy + px(280), 'F', px(40), c2, 'ct', FONT_EN, weight=800,
            alpha=0.8)
    text_at(cr, cx + off, cy + px(280), 'M', px(40), c1, 'ct', FONT_EN, weight=800,
            alpha=0.8)


def to_f(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.8), 2.0)
    glow(cr, W / 2, H / 2, px(760), c2, 0.24 * k, key='g_sec')
    text_at(cr, W / 2, H / 2, 'F', px(340), c2, 'cc', FONT_EN, weight=900,
            alpha=0.85 * k, spacing=20)
    for i in range(5):
        ring(cr, W / 2, H / 2, px(260 + i * 90) * (0.6 + 0.6 * k), c2, 2.0,
             0.3 * k - i * 0.04, dash=(16, 20), a0=s.t * 1.4, a1=s.t * 1.4 + TAU)


def to_m(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.8), 2.0)
    glow(cr, W / 2, H / 2, px(760), c1, 0.24 * k, key='g_key')
    text_at(cr, W / 2, H / 2, 'M', px(340), c1, 'cc', FONT_EN, weight=900,
            alpha=0.85 * k, spacing=20)
    for i in range(5):
        ring(cr, W / 2, H / 2, px(260 + i * 90) * (0.6 + 0.6 * k), c1, 2.0,
             0.3 * k - i * 0.04, dash=(16, 20), a0=-s.t * 1.4, a1=-s.t * 1.4 + TAU)


def whatever(cr, s):
    """And then do whatever — controlled chaos."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    for i in range(26):
        x = rnd(31, i) * W
        y = rnd(37, i) * H
        a = rnd(41, i) * TAU + s.t * (0.6 + rnd(43, i))
        L = px(120 + rnd(47, i) * 260)
        cr.save()
        cr.set_line_width(px(1.6 + rnd(53, i) * 2.4))
        cr.set_source_rgba(*(c2 if i % 3 == 0 else c1), 0.20 + rnd(59, i) * 0.45)
        cr.move_to(x, y)
        cr.line_to(x + L * math.cos(a), y + L * math.sin(a))
        cr.stroke()
        cr.restore()
    for i in range(14):
        x = (rnd(61, i) * W + s.t * px(40) * (1 if i % 2 else -1)) % W
        y = rnd(67, i) * H
        s_ = px(40 + rnd(71, i) * 90)
        poly(cr, [(x, y), (x + s_, y + s_ * 0.3), (x + s_ * 0.6, y + s_)],
             c2 if i % 2 else c1, 0.35, 2.0, close=True)
    glow(cr, W / 2, H / 2, px(700), c1, 0.10, key='g_key')


def am_pm(cr, s):
    """From AM to PM — a clock hand sweeps a day."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.52
    R = px(300)
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    ring(cr, cx, cy, R, c1, 3.0, 0.55)
    ring(cr, cx, cy, R * 0.82, c1, 1.4, 0.25, dash=(8, 12))
    for i in range(12):
        a = TAU * i / 12 - math.pi / 2
        L = px(28 if i % 3 else 48)
        cr.save()
        cr.set_line_width(px(3 if i % 3 == 0 else 1.8))
        cr.set_source_rgba(*c1, 0.5)
        cr.move_to(cx + (R - L) * math.cos(a), cy + (R - L) * math.sin(a))
        cr.line_to(cx + R * math.cos(a), cy + R * math.sin(a))
        cr.stroke()
        cr.restore()
    a = -math.pi / 2 + TAU * k
    arrow(cr, cx, cy, cx + R * 0.86 * math.cos(a), cy + R * 0.86 * math.sin(a),
          c2, 4.0, 0.95, 22)
    dot(cr, cx, cy, px(10), c2, 0.95)
    # shaded half for PM
    cr.save()
    cr.arc(cx, cy, R, -math.pi / 2, a, False)
    cr.line_to(cx, cy)
    cr.close_path()
    cr.set_source_rgba(*c2, 0.10 * k)
    cr.fill()
    cr.restore()
    text_at(cr, cx - px(220), cy - px(120), 'AM', px(44), c1, 'cc', FONT_EN,
            weight=800, alpha=0.75)
    text_at(cr, cx + px(220), cy + px(120), 'PM', px(44), c2, 'cc', FONT_EN,
            weight=800, alpha=0.85)


def switch_role(cr, s):
    """Oh, my switch role — a toggle flips."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H / 2
    k = ease_out(clamp01(s.p * 1.5), 2.4)
    Wd, Ht = px(520), px(200)
    cr.save()
    cr.set_line_width(px(5))
    cr.set_source_rgba(*c1, 0.7)
    cr.rectangle(cx - Wd / 2, cy - Ht / 2, Wd, Ht)
    cr.stroke()
    cr.restore()
    # knob travels
    kx = cx - Wd / 2 + px(120) + (Wd - px(240)) * k
    glow(cr, kx, cy, px(260), c2, 0.55, key='g_sec')
    cr.save()
    cr.arc(kx, cy, px(72), 0, TAU)
    cr.set_source_rgba(*c2, 0.95)
    cr.fill()
    cr.restore()
    ring(cr, kx, cy, px(72), (1, 1, 1), 2.4, 0.8)
    text_at(cr, cx - Wd / 2 + px(120), cy + Ht, 'S', px(40), c1, 'ct', FONT_EN,
            weight=800, alpha=0.6 + 0.3 * (1 - k))
    text_at(cr, cx + Wd / 2 - px(120), cy + Ht, 'M', px(40), c1, 'ct', FONT_EN,
            weight=800, alpha=0.6 + 0.3 * k)
    # sparks at the flip
    d = abs(k - 0.5)
    if d < 0.1:
        for i in range(24):
            a = rnd(83, i) * TAU
            r = px(90 + rnd(89, i) * 180) * (1 - d * 10)
            dot(cr, kx + r * math.cos(a), cy + r * math.sin(a), px(3.5), (1, 1, 1),
                (1 - d * 10) * 0.7)


def to_s(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.8), 2.0)
    glow(cr, W / 2, H / 2, px(700), c2, 0.22 * k, key='g_sec')
    text_at(cr, W / 2, H / 2, 'S', px(320), c2, 'cc', FONT_EN, weight=900,
            alpha=0.85 * k, spacing=18)
    for i in range(4):
        ring(cr, W / 2, H / 2, px(280 + i * 110) * (0.6 + 0.6 * k), c2, 2.0,
             0.3 * k - i * 0.05, dash=(14, 18), a0=s.t * 1.2, a1=s.t * 1.2 + TAU)


def to_m2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.8), 2.0)
    glow(cr, W / 2, H / 2, px(700), c1, 0.22 * k, key='g_key')
    text_at(cr, W / 2, H / 2, 'M', px(320), c1, 'cc', FONT_EN, weight=900,
            alpha=0.85 * k, spacing=18)
    for i in range(4):
        ring(cr, W / 2, H / 2, px(280 + i * 110) * (0.6 + 0.6 * k), c1, 2.0,
             0.3 * k - i * 0.05, dash=(14, 18), a0=-s.t * 1.2, a1=-s.t * 1.2 + TAU)
