# -*- coding: utf-8 -*-
"""shots_love — movements H–K: execution, the count, and love as a formula."""
import math
from render_lib import (W, H, TAU, px, mix, shade, clamp01, smoothstep, ease_out,
                        ease_in, pulse, text_at, text_glow, grad_rect, dashed_line,
                        arrow, dot, ring, poly, glow, blit, FONT_EN, FONT_ZH)
from scene_paint import (rnd, hex_grid, dot_field, grid_lines, crosshair, waveform,
                         oscilloscope, pcb_network, concentric, orbit_ring,
                         target_rings, project)
import cairo


def _heart_pts(cx, cy, R, n=241):
    pts = []
    for i in range(n):
        u = i / (n - 1.0) * TAU
        x = 16 * math.sin(u) ** 3
        y = (13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u)
             - math.cos(4 * u))
        pts.append((cx + x * R / 17.0, cy - y * R / 17.0))
    return pts


def exec_tick(cr, s):
    """Execution ×12 — one machine advancing, twelve different pulses."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    idx = s.ctx.tick
    pcb_network(cr, 401 + idx * 13, s.t * 0.4, c1, 0.16, 10, 1.4)
    cx = W / 2
    # a counter that increments on the beat
    n = (idx + 1) * 137 + int(s.t * 12) % 137
    # the bar advances a notch per line
    y = H * 0.60
    x0, x1 = px(260), W - px(260)
    cr.save()
    cr.set_line_width(px(3))
    cr.set_source_rgba(*c1, 0.30)
    cr.move_to(x0, y); cr.line_to(x1, y)
    cr.stroke()
    cr.restore()
    frac = (idx + 1) / 12.0
    xe = x0 + (x1 - x0) * frac
    cr.save()
    cr.set_line_width(px(8))
    cr.set_source_rgba(*c2, 0.95)
    cr.move_to(x0, y); cr.line_to(xe, y)
    cr.stroke()
    cr.restore()
    glow(cr, xe, y, px(160), c2, 0.75, key='g_sec')
    # twelve ticks
    for i in range(12):
        x = x0 + (x1 - x0) * (i + 1) / 12.0
        on = i <= idx
        cr.save()
        cr.set_line_width(px(2))
        cr.set_source_rgba(*(c2 if on else c1), 0.85 if on else 0.22)
        cr.move_to(x, y - px(22)); cr.line_to(x, y + px(22))
        cr.stroke()
        cr.restore()
    # a ring of twelve marks rotating
    for i in range(12):
        a = TAU * i / 12 + s.t * 0.5
        on = i <= idx
        r = px(230 + (18 if i == idx else 0))
        dot(cr, cx + r * math.cos(a), H * 0.34 + r * math.sin(a) * 0.5,
            px(7 if i == idx else 4.4), c2 if on else c1, 0.95 if on else 0.28)
    ring(cr, cx, H * 0.34, px(230), c1, 1.6, 0.25, dash=(10, 14))
    text_at(cr, cx, H * 0.34, '%02d / 12' % (idx + 1), px(52), c2, 'cc', FONT_EN,
            weight=800, alpha=0.9, spacing=6)
    text_at(cr, cx, y + px(70), 'counter = %d' % n, px(22), c1, 'ct', FONT_EN,
            alpha=0.5, spacing=2)


def count_es(cr, s):
    """Ein — one."""
    _count(cr, s, 1, 'EIN', '一')


def count_dos(cr, s):
    """dos — two."""
    _count(cr, s, 2, 'DOS', '二')


def count_tres(cr, s):
    """Trios — three."""
    _count(cr, s, 3, 'TRIOS', '三')


def count_ne(cr, s):
    """ne — four."""
    _count(cr, s, 4, 'NE', '四')


def count_fem(cr, s):
    """Fem — five."""
    _count(cr, s, 5, 'FEM', '五')


def count_liu(cr, s):
    """liu — six."""
    _count(cr, s, 6, 'LIU', '六')


def _count(cr, s, n, word, zh):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    # a heart filling up with each count
    pts = _heart_pts(cx, cy, px(360))
    poly(cr, pts, c2, 0.07, 1.0, close=True, fill=True)
    cr.save()
    cr.set_line_width(px(3))
    cr.set_source_rgba(*c2, 0.55)
    cr.new_path()
    for i, p in enumerate(pts):
        if i == 0:
            cr.move_to(*p)
        else:
            cr.line_to(*p)
    cr.stroke()
    cr.restore()
    # level fill
    k = ease_out(clamp01(s.p * 1.3), 1.8)
    lvl = (n - 1 + k) / 6.0
    cr.save()
    cr.rectangle(0, cy + px(400) - px(800) * lvl, W, px(800))
    cr.clip()
    poly(cr, pts, c2, 0.30, 1.0, close=True, fill=True)
    cr.restore()
    glow(cr, cx, cy, px(560) * (0.7 + 0.3 * k), c2, 0.22 * k, key='g_sec')
    text_glow(cr, cx, cy - px(40), word, px(150), (1, 1, 1), 'cc', FONT_EN,
              weight=900, alpha=0.95 * k, spacing=16)
    text_glow(cr, cx, cy + px(120), zh, px(46), c2, 'cc', FONT_ZH,
              alpha=0.85 * k, spacing=16, halo=0.9)
    # pie ticks
    for i in range(6):
        a = TAU * i / 6 - math.pi / 2
        on = i < n
        for j in range(2):
            rr = px(470 + j * 26)
            cr.save()
            cr.set_line_width(px(4 if i == n - 1 else 2.4))
            cr.set_source_rgba(*(c2 if on else c1), 0.85 if on else 0.18)
            cr.move_to(cx + rr * math.cos(a), cy + rr * math.sin(a))
            cr.line_to(cx + (rr + px(26)) * math.cos(a), cy + (rr + px(26)) * math.sin(a))
            cr.stroke()
            cr.restore()


def exec_one(cr, s):
    """Give them all the execution — every counter fires at once."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    hex_grid(cr, c1, alpha=0.05)
    cx, cy = W / 2, H * 0.5
    # six concentric execution rings all completing
    for i in range(6):
        rr = px(120 + i * 90)
        k = ease_out(clamp01(s.p * 1.4 - i * 0.07), 2.0)
        cr.save()
        cr.set_line_width(px(4))
        cr.set_source_rgba(*(c2 if i % 2 else c1), 0.8 * k)
        cr.arc(cx, cy, rr, -math.pi / 2, -math.pi / 2 + TAU * k)
        cr.stroke()
        cr.restore()
        if k > 0.98:
            dot(cr, cx, cy - rr, px(6), c2, 0.9)
    glow(cr, cx, cy, px(900), c1, 0.20, key='g_key')
    if s.p > 0.7:
        a = smoothstep(0.7, 1.0, s.p)
        _burst(cr, cx, cy, a, c2, c1)


def exec_one2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    _burst(cr, cx, cy, clamp01(s.p * 1.6), c2, c1, backwards=True)
    glow(cr, cx, cy, px(600) * (1 - s.p * 0.6), c2, 0.35 * (1 - s.p * 0.7), key='g_sec')


def _burst(cr, cx, cy, k, c2, c1, backwards=False):
    n = 90
    for i in range(n):
        a = rnd(409, i) * TAU
        sp = px(200 + rnd(419, i) * 900)
        t = (1 - k) if backwards else k
        x = cx + math.cos(a) * sp * t
        y = cy + math.sin(a) * sp * t * 0.8
        al = k * 0.85 if backwards else (1 - k) * 0.85
        dot(cr, x, y, px(2.4 + rnd(421, i) * 4.0), c2 if i % 3 else c1, max(0, al))


def final_if(cr, s):
    """Be your only execution — a single execution that matters."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    glow(cr, cx, cy, px(700 + 400 * k), c2, 0.28 * k, key='g_sec')
    for i in range(4):
        rr = px(150 + i * 130) * (0.4 + 0.9 * k)
        ring(cr, cx, cy, rr, c2 if i == 0 else c1, 3.4 - i * 0.7,
             (0.85 - i * 0.2) * k)
    cr.save()
    cr.set_line_width(px(6))
    cr.set_source_rgba(*(1, 1, 1), 0.9 * k)
    cr.move_to(cx - px(80), cy)
    cr.line_to(cx - px(24), cy)
    cr.line_to(cx - px(6), cy - px(46))
    cr.line_to(cx + px(14), cy + px(46))
    cr.line_to(cx + px(34), cy)
    cr.line_to(cx + px(84), cy)
    cr.stroke()
    cr.restore()


def final_exec(cr, s):
    """If I can have you back — the empty outline is revisited."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.54
    k = ease_out(clamp01(s.p * 1.1), 1.8)
    # hollow silhouette that slowly gains a pulse
    cr.save()
    cr.set_line_width(px(2.6))
    cr.set_source_rgba(*c1, 0.55)
    cr.arc(cx + px(300), cy, px(60), 0, TAU)
    cr.stroke()
    cr.rectangle(cx + px(248), cy + px(36), px(104), px(230))
    cr.stroke()
    cr.restore()
    # a signal line trying to reach it
    y = cy + px(150)
    cr.save()
    cr.set_line_width(px(3))
    cr.set_source_rgba(*c2, 0.75)
    cr.move_to(px(140), y)
    cr.line_to(cx + px(200), y)
    cr.stroke()
    cr.restore()
    # a pulse travelling along, dying at the edge
    u = (s.t * 0.6) % 1.0
    px_ = px(140) + (cx + px(200) - px(140)) * u
    col = c2 if u < 0.85 else (1, 0.4, 0.4)
    dot(cr, px_, y, px(8), col, 0.9 * (1 - max(0, u - 0.9) * 8))
    for i in range(int(9 * k)):
        dashed_line(cr, px(140) + i * px(60), y, px(140) + i * px(60), y + px(40),
                    5, 7, 1.4, c1, 0.30)
    glow(cr, cx + px(300), cy, px(520), c1, 0.12, key='g_key')


def final_then(cr, s):
    """I will run the execution — the machine commits."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.3), 2.0)
    # a big switch thrown
    for i in range(24):
        a = rnd(431, i) * TAU
        rr = px(700) * (1 - k)
        dot(cr, cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.7, px(3.4), c1,
            (1 - k) * 0.55)
    glow(cr, cx, cy, px(800) * k, c2, 0.4 * k, key='g_sec')
    ring(cr, cx, cy, px(330), c2, 4.0, 0.9 * k)
    ring(cr, cx, cy, px(380), c2, 1.6, 0.45 * k, dash=(16, 20))
    cr.save()
    cr.set_line_width(px(14))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(*(1, 1, 1), 0.92)
    cr.move_to(cx - px(120), cy)
    cr.line_to(cx + px(120), cy)
    cr.stroke()
    cr.restore()


def final_exec2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = clamp01(s.p * 1.2)
    # the execution counter running to completion, then overflowing
    n = int(12 * ease_out(k, 1.6))
    for i in range(12):
        on = i < n
        a = TAU * i / 12 - math.pi / 2
        rr = px(300)
        cr.save()
        cr.set_line_width(px(5))
        cr.set_source_rgba(*(c2 if on else c1), 0.9 if on else 0.20)
        cr.move_to(cx + (rr - px(30)) * math.cos(a), cy + (rr - px(30)) * math.sin(a))
        cr.line_to(cx + rr * math.cos(a), cy + rr * math.sin(a))
        cr.stroke()
        cr.restore()
    text_at(cr, cx, cy, '%d' % n, px(180), c2, 'cc', FONT_EN, weight=900,
            alpha=0.85, spacing=8)
    glow(cr, cx, cy, px(700), c2, 0.22 * k, key='g_sec')


def have_you_back(cr, s):
    """Though we are trapped — both figures, inside a box that does not open."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.52
    k = ease_out(clamp01(s.p * 1.1), 1.8)
    # the cage: a wireframe box drawn around the two of them
    ssz = px(360) * (0.6 + 0.4 * k)
    for i in range(3):
        s_ = ssz * (1 + i * 0.22)
        cr.save()
        cr.set_line_width(px(2.0))
        cr.set_source_rgba(*(c2 if i == 0 else c1), 0.6 - i * 0.14)
        # an isometric crate
        o = s_ * 0.5
        pts = [(cx - s_, cy - o * 0.6), (cx, cy - s_ * 0.6 - o * 0.6),
               (cx + s_, cy - o * 0.6), (cx + s_, cy + o * 0.6),
               (cx, cy + s_ * 0.6 + o * 0.6), (cx - s_, cy + o * 0.6)]
        cr.new_path()
        cr.move_to(*pts[0])
        for p in pts[1:]:
            cr.line_to(*p)
        cr.close_path()
        cr.stroke()
        cr.restore()
    # two dots inside, close but separate
    for sgn, col in ((-1, c1), (1, c2)):
        x = cx + sgn * px(60)
        glow(cr, x, cy, px(160), col, 0.45, key='g_%d' % sgn)
        dot(cr, x, cy, px(16), col, 0.95)
        ring(cr, x, cy, px(30), col, 1.8, 0.4)
    # a link between them that keeps flickering
    a = 0.4 + 0.4 * abs(math.sin(s.t * 4.0))
    dashed_line(cr, cx - px(44), cy, cx + px(44), cy, 6, 8, 2.4, (1, 1, 1), a * 0.8)


def run_exec(cr, s):
    """We are trapped, ah — the walls close in."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.1), 1.6)
    glow(cr, cx, cy, px(620), c1, 0.20, key='g_key')
    for i in range(7):
        u = i / 7.0
        w = px(1500) * (1 - u * 0.82 - k * 0.16)
        h = px(900) * (1 - u * 0.82 - k * 0.16)
        cr.save()
        cr.set_line_width(px(1.8))
        cr.set_source_rgba(*(c2 if i % 2 else c1), 0.55 - u * 0.05)
        cr.rectangle(cx - w / 2, cy - h / 2, w, h)
        cr.stroke()
        cr.restore()
    # two dots still inside
    for sgn, col in ((-1, c1), (1, c2)):
        dot(cr, cx + sgn * px(30) * (1 - k * 0.5), cy, px(13), col, 0.9)
    for i in range(50):
        u = ((s.t * 0.4 + rnd(439, i)) % 1.0)
        a = rnd(443, i) * TAU
        rr = px(1200) * (1 - k * 0.7)
        dot(cr, cx + rr * u * math.cos(a), cy + rr * u * math.sin(a), px(2.2),
            c1, (1 - u) * 0.35)


def still_trapped(cr, s):
    """I've studied, I've studied — pages of notes, repeated."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # a wall of stacked paper, each sheet carrying the same formula
    for r in range(5):
        for c in range(7):
            x = px(120) + c * px(245)
            y = px(120) + r * px(180)
            i = r * 7 + c
            w = px(205) * (0.4 + 0.6 * clamp01((s.p * 1.6 - i * 0.035)))
            cr.save()
            cr.translate(x, y)
            cr.rotate((rnd(449, i) - 0.5) * 0.10)
            cr.set_source_rgba(*shade(c1, 0.4), 0.55)
            cr.rectangle(0, 0, px(205), px(140))
            cr.fill()
            cr.set_line_width(px(1.2))
            cr.set_source_rgba(*c1, 0.5)
            cr.rectangle(0, 0, px(205), px(140))
            cr.stroke()
            cr.restore()
            if w > px(150):
                for j in range(4):
                    xx = x + px(16)
                    yy = y + px(28) + j * px(28)
                    L = px(170) * (0.4 + 0.6 * rnd(457, i * 5 + j))
                    cr.save()
                    cr.set_line_width(px(1.6))
                    cr.set_source_rgba(*(c2 if j == 0 else c1), 0.35)
                    cr.move_to(xx, yy); cr.line_to(xx + L, yy)
                    cr.stroke()
                    cr.restore()
    text_at(cr, px(120), H - px(70), 'revision %d  ·  still no answer' %
            int(s.t * 3), px(24), c2, 'lb', FONT_EN, alpha=0.55, spacing=2)


def we_trapped(cr, s):
    """How to properly lo-o-ove — the phrase stutters in the visual language."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    # the word LOVE drawn as a wave that keeps restarting
    for i in range(5):
        u = (s.t * 0.5 + i * 0.2) % 1.0
        rr = px(140 + i * 130)
        a = (1 - u) * 0.6
        ring(cr, cx, cy, rr, c2 if i % 2 else c1, 2.4, a)
    glow(cr, cx, cy, px(620), c2, 0.20, key='g_sec')
    text_at(cr, cx, cy, 'LO—O—OVE', px(130), (1, 1, 1), 'cc', FONT_EN, weight=900,
            alpha=0.22 + 0.10 * math.sin(s.t * 5), spacing=10)
    # a stutter meter
    n = int((s.t * 4) % 4) + 1
    for i in range(4):
        dot(cr, cx - px(90) + i * px(60), cy + px(150), px(9),
            c2 if i < n else c1, 0.85 if i < n else 0.2)


def studied(cr, s):
    """Question me, question me — a questionnaire, then an exam."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    hex_grid(cr, c1, alpha=0.04)
    qs = ['Q1  what is love?', 'Q2  why does it hurt?',
          'Q3  can it be computed?', 'Q4  is this enough?']
    for i, q in enumerate(qs):
        y = px(230) + i * px(130)
        k = clamp01(s.p * 2.0 - i * 0.35)
        e = ease_out(k, 2.0)
        text_at(cr, px(240) - px(60) * (1 - e), y, q, px(46), c1, 'lt', FONT_EN,
                alpha=0.85 * e, spacing=2)
        # a tick appears
        if k > 0.7:
            aa = smoothstep(0.7, 1.0, k)
            cr.save()
            cr.set_line_width(px(6))
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_source_rgba(*c2, aa)
            x0 = W - px(300)
            cr.move_to(x0, y + px(20))
            cr.line_to(x0 + px(34), y + px(54))
            cr.line_to(x0 + px(96), y - px(24))
            cr.stroke()
            cr.restore()
    text_at(cr, W - px(300), px(160), 'answered  %d/%d' %
            (min(4, int(s.p * 4.6)), 4), px(24), c2, 'rt', FONT_EN, alpha=0.6,
            spacing=2)


def properly(cr, s):
    """I can answer all lo-o-ove — the answer arrives as a huge number."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    glow(cr, cx, cy, px(820) * k, c2, 0.22 * k, key='g_sec')
    # digits raining into place
    for i in range(60):
        u = clamp01(k * 1.4 - rnd(461, i) * 0.5)
        x = rnd(463, i) * W
        y = px(120) + rnd(467, i) * (H - px(240))
        ch = '%d' % (i % 10)
        text_at(cr, x, y, ch, px(30 + rnd(479, i) * 40), c1, 'cc', FONT_EN,
                weight=800, alpha=0.10 + 0.25 * u, spacing=4)
    text_glow(cr, cx, cy, '= 42', px(200), (1, 1, 1), 'cc', FONT_EN, weight=900,
              alpha=0.9 * k, spacing=10)
    text_at(cr, cx, cy + px(180), 'the answer, at last', px(30), c2, 'cc',
            FONT_EN, alpha=0.65 * k, spacing=8)


def question(cr, s):
    """I know the algebraic expression — a graph is plotted point by point."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    grid_lines(cr, c1, 0.07, 60, 1.0)
    x0, y0 = px(180), H * 0.76
    x1, y1 = W - px(180), H * 0.16
    # axes
    cr.save()
    cr.set_line_width(px(2.4))
    cr.set_source_rgba(*c1, 0.6)
    cr.move_to(x0, y0); cr.line_to(x1, y0)
    cr.move_to(x0, y0); cr.line_to(x0, y1)
    cr.stroke()
    cr.restore()
    arrow(cr, x0, y0, x1, y0, c1, 1.6, 0.6, 12)
    arrow(cr, x0, y0, x0, y1, c1, 1.6, 0.6, 12)
    # the curve, drawn as the line is sung
    k = ease_out(clamp01(s.p * 1.15), 1.8)
    n = 260
    cr.save()
    cr.set_line_width(px(4))
    cr.set_source_rgba(*c2, 0.95)
    cr.new_path()
    cnt = int(n * k)
    for i in range(max(cnt, 2)):
        u = i / (n - 1.0)
        x = x0 + (x1 - x0) * u
        t = u * TAU * 1.6
        # a heart-ish closed form: r = 1 - sin(t) family
        v = 0.5 + 0.42 * math.sin(t) * math.cos(t * 0.5) + 0.14 * math.sin(t * 2.7)
        y = y0 - (y0 - y1) * clamp01(v)
        if i == 0:
            cr.move_to(x, y)
        else:
            cr.line_to(x, y)
    cr.stroke()
    cr.restore()
    if cnt < n:
        u = cnt / (n - 1.0)
        x = x0 + (x1 - x0) * u
        t = u * TAU * 1.6
        v = 0.5 + 0.42 * math.sin(t) * math.cos(t * 0.5) + 0.14 * math.sin(t * 2.7)
        y = y0 - (y0 - y1) * clamp01(v)
        dot(cr, x, y, px(10), (1, 1, 1), 1.0)
        glow(cr, x, y, px(120), c2, 0.7, key='g_sec')
    text_at(cr, x0 + px(20), y1 + px(10), 'lo-o-ove', px(30), c2, 'lt', FONT_EN,
            alpha=0.6, italic=True, spacing=2)


def answer_love(cr, s):
    """Though you are free — a bird / particle escaping the frame."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.55
    k = ease_out(clamp01(s.p * 1.1), 1.6)
    # the cage from before, now with the walls gone
    for i in range(5):
        u = i / 5.0
        w = px(900) * (1 - u * 0.6)
        h = px(560) * (1 - u * 0.6)
        a = 0.30 * (1 - k * 0.85)
        cr.save()
        cr.set_line_width(px(1.6))
        cr.set_source_rgba(*c1, max(0, a))
        cr.rectangle(cx - w / 2, cy - h / 2, w, h)
        cr.stroke()
        cr.restore()
    # one dot leaves
    u = ease_io(clamp01(s.p * 1.2))
    x = cx + (W * 1.15 - cx) * u
    y = cy - px(260) * math.sin(u * 2.2)
    glow(cr, x, y, px(200), c2, 0.5 * (1 - u * 0.5), key='g_sec')
    dot(cr, x, y, px(13), c2, 0.95)
    # trail
    for i in range(28):
        uu = clamp01(u - i * 0.012)
        xx = cx + (W * 1.15 - cx) * uu
        yy = cy - px(260) * math.sin(uu * 2.2)
        dot(cr, xx, yy, px(4.5 - i * 0.12), c2, (1 - uu) * 0.5 * (1 - i / 28.0))
    # the one left behind
    dot(cr, cx, cy, px(15), c1, 0.9)
    glow(cr, cx, cy, px(300), c1, 0.25, key='g_key')


def i_trapped(cr, s):
    """I am trapped — the frame becomes a cell."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.1), 1.6)
    # bars descend
    n = 13
    for i in range(n):
        x = px(60) + i * ((W - px(120)) / (n - 1))
        d = clamp01((k - i / n * 0.4) / 0.6)
        e = ease_out(d, 2.2)
        h = H * e
        cr.save()
        cr.set_line_width(px(14))
        cr.set_line_cap(cairo.LINE_CAP_BUTT)
        cr.set_source_rgba(*(shade(c1, 0.75)), 0.9)
        cr.move_to(x, cy - h / 2)
        cr.line_to(x, cy + h / 2)
        cr.stroke()
        cr.restore()
        # rivets
        for j in range(3):
            dot(cr, x, cy - h / 2 + h * (j + 0.5) / 3, px(3.4), c1, 0.5)
    # the trapped dot
    glow(cr, cx, cy, px(280), c2, 0.5, key='g_sec')
    dot(cr, cx, cy, px(15), c2, 0.95)
    for i in range(4):
        u = ((s.t * 0.6 + i / 4.0) % 1.0)
        ring(cr, cx, cy, px(40) + px(240) * u, c2, 1.8, (1 - u) ** 1.5 * 0.45)


def in_love(cr, s):
    """Trapped in lo-o-ove — the heart as a locked container."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    R = px(360)
    k = ease_out(clamp01(s.p * 1.0), 1.6)
    pts = _heart_pts(cx, cy, R)
    # heart outline, filled with a slow rotating field
    poly(cr, pts, c2, 0.08, 1.0, close=True, fill=True)
    cr.save()
    cr.new_path()
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.close_path()
    cr.clip()
    for i in range(60):
        a = rnd(487, i) * TAU
        rr = px(600) * rnd(491, i)
        x = cx + rr * math.cos(a + s.t * 0.2)
        y = cy + rr * math.sin(a + s.t * 0.2)
        dot(cr, x, y, px(3.2), c2 if i % 4 == 0 else c1, 0.20 + 0.35 * rnd(499, i))
    cr.restore()
    cr.save()
    cr.set_line_width(px(4.5))
    cr.set_source_rgba(*c2, 0.9)
    cr.new_path()
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.stroke()
    cr.restore()
    glow(cr, cx, cy, px(760), c2, 0.20, key='g_sec')
    # the trapped dot, inside
    dot(cr, cx, cy + px(30), px(14), (1, 1, 1), 0.95)
    for i in range(3):
        u = ((s.t * 0.5 + i / 3.0) % 1.0)
        ring(cr, cx, cy + px(30), px(40) + px(260) * u, (1, 1, 1), 1.6,
             (1 - u) ** 1.5 * 0.35)


def if_i_can3(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.6), 2.0)
    glow(cr, W / 2, H * 0.5, px(760) * k, c1, 0.24 * k, key='g_key')
    text_at(cr, W / 2, H / 2, 'IF', px(220), c1, 'cc', FONT_EN, weight=900,
            alpha=0.24 * k, spacing=30)


def if_i_can4(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.6), 2.0)
    glow(cr, W / 2, H * 0.5, px(760) * k, c2, 0.24 * k, key='g_sec')
    text_at(cr, W / 2, H / 2, 'CAN', px(220), c2, 'cc', FONT_EN, weight=900,
            alpha=0.24 * k, spacing=30)


def studied_note(cr, s):
    """Unused alias kept so the shot registry never raises."""
    return still_trapped(cr, s)


def algebraic(cr, s):
    """The algebraic expression of love — the whole song resolves into one curve."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.05), 1.6)
    # the parametric heart, drawn large and clean
    R = px(420)
    n = 420
    pts = []
    for i in range(n):
        t = i / (n - 1.0) * TAU
        x = 16 * math.sin(t) ** 3
        y = (13 * math.cos(t) - 5 * math.cos(2 * t)
             - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * R / 17.0, cy - y * R / 17.0))
    cnt = max(2, int(n * k))
    # glow trace
    glow(cr, cx, cy, px(900) * k, c2, 0.16 * k, key='g_sec')
    cr.save()
    cr.set_line_width(px(7))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(*c2, 0.95)
    cr.new_path()
    for i, p in enumerate(pts[:cnt]):
        if i == 0:
            cr.move_to(*p)
        else:
            cr.line_to(*p)
    cr.stroke()
    cr.restore()
    # fill once closed
    if cnt >= n - 1:
        a = smoothstep(0.97, 1.0, k)
        poly(cr, pts, c2, 0.14 * a, 1.0, close=True, fill=True)
    # points plotted on the curve
    for i in range(0, cnt, 12):
        dot(cr, pts[i][0], pts[i][1], px(5), (1, 1, 1), 0.7)
    # the pen tip
    if cnt < n:
        dot(cr, pts[cnt - 1][0], pts[cnt - 1][1], px(12), (1, 1, 1), 1.0)
        glow(cr, pts[cnt - 1][0], pts[cnt - 1][1], px(150), c2, 0.75, key='g_sec')
    # the formula, bottom-left, typing itself
    formula = 'x = 16 sin³t     y = 13 cos t − 5 cos 2t − 2 cos 3t − cos 4t'
    chars = int(len(formula) * clamp01(k * 1.2))
    text_at(cr, px(140), H - px(120), formula[:chars], px(30), c1, 'lb', FONT_EN,
            alpha=0.75, spacing=1.5)
    text_at(cr, W - px(140), H - px(200), 'lo-o-ove, expressed algebraically',
            px(24), c2, 'rb', FONT_EN, alpha=0.5 * k, spacing=4, italic=True)


def outro(cr, s):
    """Last beats — the heart settles and holds."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    pts = _heart_pts(cx, cy, px(400))
    breath = 1.0 + 0.02 * math.sin(s.t * 1.2)
    pts = [(cx + (x - cx) * breath, cy + (y - cy) * breath) for x, y in pts]
    glow(cr, cx, cy, px(1000), c2, 0.18, key='g_sec')
    poly(cr, pts, c2, 0.16, 1.0, close=True, fill=True)
    cr.save()
    cr.set_line_width(px(4))
    cr.set_source_rgba(*c2, 0.9)
    cr.new_path()
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.close_path()
    cr.stroke()
    cr.restore()
    for i in range(46):
        u = ((s.t * 0.22 + rnd(503, i)) % 1.0)
        a = rnd(509, i) * TAU
        rr = px(500) * (0.3 + rnd(521, i)) * (0.4 + u)
        dot(cr, cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.7, px(2.4), c1,
            (1 - u) * 0.35)


def gap_after(cr, s):
    """Instrumental after the last lyric — the world winds down."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # countdown 4·3·2·1 over the whole gap, then the last chord holds
    total = max(0.001, s.t1 - s.t0)
    frac = s.lt / total
    cx, cy = W / 2, H * 0.5
    if frac < 0.35:
        n = 4 - int(frac / 0.35 * 4)
        if n >= 1:
            k = (frac / 0.35 * 4) % 1.0
            glow(cr, cx, cy, px(700) * (1 - k * 0.5), c2, 0.35 * (1 - k), key='g_sec')
            text_at(cr, cx, cy, '%d' % n, px(300), c2, 'cc', FONT_EN, weight=900,
                    alpha=0.85 * (1 - k) ** 0.6, spacing=20)
            ring(cr, cx, cy, px(200) + px(400) * k, c2, 3.0, (1 - k) * 0.6)
    else:
        # the heart from the outro, fading into the dark
        f = (frac - 0.35) / 0.65
        a = (1 - f) ** 1.2
        pts = _heart_pts(cx, cy, px(380) * (1 + 0.05 * f))
        gl = 0.20 * a
        if gl > 0.002:
            glow(cr, cx, cy, px(900), c2, gl, key='g_sec')
        poly(cr, pts, c2, 0.14 * a, 1.0, close=True, fill=True)
        cr.save()
        cr.set_line_width(px(4))
        cr.set_source_rgba(*c2, 0.85 * a)
        cr.new_path()
        cr.move_to(*pts[0])
        for p in pts[1:]:
            cr.line_to(*p)
        cr.close_path()
        cr.stroke()
        cr.restore()
    # dust throughout
    for i in range(60):
        u = ((s.t * 0.10 + rnd(523, i)) % 1.0)
        x = rnd(541, i) * W
        y = H - u * H
        dot(cr, x, y, px(2.0), c1, (1 - u) * 0.20)


def gap_wake(cr, s):
    """03:8–29.8 placeholder — superseded by the title cards; kept as a fallback."""
    from shots_title import card_cover
    return card_cover(cr, s)


def gap_void(cr, s):
    """Instrumental 134.9–148.0 — the world resets behind the solo."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    total = max(0.001, s.t1 - s.t0)
    f = s.lt / total
    # an engine spooling: parts reassemble from fragments
    for i in range(150):
        a = rnd(547, i) * TAU
        rr = px(900) * (1 - f * 0.55) * (0.3 + rnd(557, i))
        x = cx + rr * math.cos(a + f * 2.0)
        y = cy + rr * math.sin(a + f * 2.0) * 0.7
        dot(cr, x, y, px(2.6), c2 if i % 5 == 0 else c1,
            0.15 + 0.35 * rnd(563, i) * (1 - f * 0.6))
    # the machine core rebuilding itself
    for i in range(6):
        rr = px(140 + i * 110) * (0.2 + f * 1.0)
        ring(cr, cx, cy, rr, c1, 2.0, 0.30 * (1 - i * 0.1) * min(1.0, f * 3))
    glow(cr, cx, cy, px(600) * f, c1, 0.16 * min(1.0, f * 2), key='g_key')
    # a progress readout
    text_at(cr, cx, cy + px(330), 'RESET  %d%%' % int(f * 100), px(26), c1,
            'ct', FONT_EN, alpha=0.5, spacing=4)


# ---------------------------------------------------------------- remaining --
# Shots referenced by the plan table.  Kept here so the registry is complete.

def trapped(cr, s):
    """Though we are trapped — the walls of the world first appear."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.1), 1.8)
    hex_grid(cr, c1, alpha=0.05)
    for i in range(6):
        u = i / 6.0
        w = px(1600) * (1 - u * 0.78) * (1 - k * 0.20)
        h = px(960) * (1 - u * 0.78) * (1 - k * 0.20)
        cr.save()
        cr.set_line_width(px(1.6))
        cr.set_source_rgba(*(c2 if i % 2 else c1), 0.45 - u * 0.04)
        cr.rectangle(cx - w / 2, cy - h / 2, w, h)
        cr.stroke()
        cr.restore()
    glow(cr, cx, cy, px(520) * k, c1, 0.16 * k, key='g_key')
    # a single node inside, starting to notice
    dot(cr, cx, cy, px(13), c2, 0.9)
    for i in range(3):
        u = ((s.t * 0.6 + i / 3.0) % 1.0)
        ring(cr, cx, cy, px(40) + px(260) * u, c2, 1.8, (1 - u) ** 1.5 * 0.4)


def trapped2(cr, s):
    """In this strange, strange simulation — the walls are now a diorama."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.52
    k = ease_out(clamp01(s.p * 1.0), 1.6)
    # the world seen as a small glass box on a stage
    bw, bh = px(760), px(500)
    # reflection floor
    grad_rect(cr, 0, cy + bh / 2, W, H - (cy + bh / 2), c1, (0, 0, 0), True, 0.10)
    for i in range(9):
        y = cy - bh / 2 + i * (bh / 8)
        a = 0.20 * (1 - abs(i - 4) / 5.0)
        cr.save()
        cr.set_line_width(px(1.4))
        cr.set_source_rgba(*c1, a)
        cr.move_to(cx - bw / 2, y)
        cr.line_to(cx + bw / 2, y)
        cr.stroke()
        cr.restore()
    for i in range(11):
        x = cx - bw / 2 + i * (bw / 10)
        cr.save()
        cr.set_line_width(px(1.4))
        cr.set_source_rgba(*c1, 0.14)
        cr.move_to(x, cy - bh / 2)
        cr.line_to(x, cy + bh / 2)
        cr.stroke()
        cr.restore()
    # the glass
    cr.save()
    cr.set_line_width(px(3.0))
    cr.set_source_rgba(*c2, 0.70)
    cr.rectangle(cx - bw / 2, cy - bh / 2, bw, bh)
    cr.stroke()
    cr.restore()
    cr.save()
    cr.set_line_width(px(1.6))
    cr.set_source_rgba(*c1, 0.35)
    cr.rectangle(cx - bw / 2 - px(26), cy - bh / 2 - px(26), bw + px(52), bh + px(52))
    cr.stroke()
    cr.restore()
    # a person-like node inside, pacing
    walk = math.sin(s.t * 0.9) * px(180)
    x, y = cx + walk, cy + px(60)
    dot(cr, x, y - px(60), px(20), c2, 0.9)
    poly(cr, [(x - px(26), y), (x - px(14), y - px(46)), (x + px(14), y - px(46)),
              (x + px(26), y)], c2, 0.9, 3.0)
    glow(cr, cx, cy, px(700), c1, 0.12, key='g_key')


def then2(cr, s):
    """Then I can — a hand closing."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.52
    k = ease_out(clamp01(s.p * 1.5), 2.2)
    glow(cr, cx, cy, px(600) * k, c2, 0.30 * k, key='g_sec')
    # fingers curling in
    for i in range(5):
        a0 = math.pi * 1.15 + i * 0.16
        L = px(240) * (0.5 + 0.5 * k)
        cr.save()
        cr.set_line_width(px(18))
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgba(*c2, 0.85)
        cr.new_path()
        for j in range(14):
            u = j / 13.0
            aa = a0 + u * (1.4 * k)
            rr = L * (0.4 + 0.6 * u)
            x = cx + rr * math.cos(aa)
            y = cy + rr * math.sin(aa) * 0.9
            if j == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
        cr.stroke()
        cr.restore()
    ring(cr, cx, cy, px(320) * k, c2, 3.0, 0.5 * k, dash=(14, 18))


def then3(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.52
    k = ease_out(clamp01(s.p * 1.4), 2.2)
    ring(cr, cx, cy, px(300) * k, c2, 3.0, 0.6 * k)
    glow(cr, cx, cy, px(700) * k, c2, 0.28 * k, key='g_sec')
    _burst2(cr, cx, cy, clamp01(s.p * 1.2), c2, c1)


def _burst2(cr, cx, cy, k, c2, c1):
    for i in range(70):
        a = rnd(601, i) * TAU
        sp = px(120 + rnd(607, i) * 800)
        t = ease_out(k, 2.0)
        dot(cr, cx + math.cos(a) * sp * t, cy + math.sin(a) * sp * t * 0.75,
            px(2.6 + rnd(613, i) * 3.6), c2 if i % 3 else c1, max(0, (1 - k) * 0.8))


def trance1(cr, s):
    """The trance — the frame starts to slip."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H / 2
    for i in range(26):
        u = ((s.t * 0.35 + i / 26.0) % 1.0)
        r = px(80) + px(1000) * u
        ring(cr, cx + px(60) * math.sin(s.t + i), cy, r, c2 if i % 4 == 0 else c1,
             2.4, (1 - u) ** 1.5 * 0.55)
    glow(cr, cx, cy, px(700), c2, 0.22, key='g_sec')
    # chromatic-ish ghosting to sell the slip
    for off in (px(18), -px(18)):
        ring(cr, cx + off, cy + off * 0.3, px(360), c1, 2.0, 0.16)


def trance2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H / 2
    for i in range(26):
        u = ((s.t * 0.45 + i / 26.0) % 1.0)
        r = px(60) + px(1100) * u
        ring(cr, cx, cy + px(50) * math.sin(s.t * 1.4 + i), r,
             c1 if i % 2 else c2, 2.2, (1 - u) ** 1.4 * 0.5)
    glow(cr, cx, cy, px(900), c1, 0.24, key='g_key')
    dot(cr, cx, cy, px(18), (1, 1, 1), 0.85)


def you_free(cr, s):
    """Trapped in lo-o-ove — the heart, with the bars of a cell across it."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    R = px(380)
    pts = _heart_pts(cx, cy, R)
    glow(cr, cx, cy, px(900), c2, 0.18, key='g_sec')
    poly(cr, pts, c2, 0.14, 1.0, close=True, fill=True)
    for i in range(9):
        x = cx - px(340) + i * px(85)
        cr.save()
        cr.set_line_width(px(11))
        cr.set_source_rgba(*(shade(c1, 0.7)), 0.85)
        cr.move_to(x, cy - px(300))
        cr.line_to(x, cy + px(300))
        cr.stroke()
        cr.restore()
    cr.save()
    cr.set_line_width(px(4.0))
    cr.set_source_rgba(*c2, 0.9)
    cr.new_path()
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.stroke()
    cr.restore()
    # one bar bends
    i = 4
    x = cx - px(340) + i * px(85)
    bend = px(40) * math.sin(s.t * 2.0)
    cr.save()
    cr.set_line_width(px(11))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(*(1, 1, 1), 0.85)
    cr.move_to(x, cy - px(300))
    cr.line_to(x + bend, cy)
    cr.line_to(x, cy + px(300))
    cr.stroke()
    cr.restore()
