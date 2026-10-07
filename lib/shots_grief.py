# -*- coding: utf-8 -*-
"""shots_grief — movements F/G: the leaving, the isolation, the rage."""
import math
from render_lib import (W, H, TAU, px, mix, shade, clamp01, smoothstep, ease_out,
                        ease_in, pulse, text_at, text_glow, grad_rect, dashed_line,
                        arrow, dot, ring, poly, glow, blit, FONT_EN, FONT_ZH)
from scene_paint import (rnd, hex_grid, dot_field, grid_lines, crosshair, waveform,
                         oscilloscope, pcb_network, concentric, orbit_ring,
                         target_rings, project)
import cairo


def if_i_can(cr, s):
    """If I can, if I can — a hand reaches, fingers not quite closing."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.4), 2.0)
    cx, cy = W / 2, H * 0.54
    # two silhouettes reaching toward each other
    for sgn, col in ((-1, c1), (1, c2)):
        bx = cx + sgn * px(340) * (1 - 0.18 * k)
        cr.save()
        cr.set_source_rgba(*col, 0.55)
        cr.arc(bx, cy, px(66), 0, TAU)
        cr.fill()
        cr.rectangle(bx - px(56), cy + px(40), px(112), px(260))
        cr.fill()
        cr.restore()
        # the arm
        cr.save()
        cr.set_line_width(px(46))
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgba(*col, 0.55)
        ax = bx - sgn * px(20)
        cr.move_to(ax, cy + px(80))
        cr.line_to(ax - sgn * px(180), cy + px(30))
        cr.stroke()
        cr.restore()
        # fingers
        for i in range(4):
            fx = bx - sgn * (px(200) + px(30) * i * 0.3)
            fy = cy - px(30) + i * px(28)
            cr.save()
            cr.set_line_width(px(13))
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_source_rgba(*col, 0.5)
            cr.move_to(fx, fy)
            cr.line_to(fx - sgn * px(70) * (0.4 + 0.6 * k), fy + px(6))
            cr.stroke()
            cr.restore()
    # the gap that never quite closes
    gap = px(300) * (1 - k)
    dashed_line(cr, cx - gap / 2, cy - px(60), cx - gap / 2, cy + px(300), 8, 10,
                1.6, c1, 0.35)
    dashed_line(cr, cx + gap / 2, cy - px(60), cx + gap / 2, cy + px(300), 8, 10,
                1.6, c1, 0.35)
    text_at(cr, cx, cy + px(330), 'gap = %.0f mm' % max(0, gap / px(1) * 0.4),
            px(22), c1, 'ct', FONT_EN, alpha=0.45, spacing=2)
    glow(cr, cx, cy, px(500), c2, 0.10, key='g_sec')


def if_i_can2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.6), 2.0)
    glow(cr, W / 2, H * 0.5, px(800) * k, c1, 0.22 * k, key='g_key')
    for i in range(5):
        ring(cr, W / 2, H * 0.5, px(120 + i * 130) * (0.3 + k), c1, 2.4,
             0.4 * k - i * 0.06, dash=(20, 26), a0=s.t * 0.6, a1=s.t * 0.6 + TAU)


def simulations(cr, s):
    """Give you all the simulations — many little worlds in a rack."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cols, rows = 8, 5
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            u = clamp01((k - i / (cols * rows) * 0.7) / 0.3)
            e = ease_out(u, 2.0)
            x = px(150) + c * ((W - px(300)) / (cols - 1))
            y = px(200) + r * ((H - px(420)) / (rows - 1))
            w, h = px(150) * e, px(110) * e
            if e <= 0:
                continue
            cr.save()
            cr.rectangle(x - w / 2, y - h / 2, w, h)
            cr.set_source_rgba(*shade(c1, 0.5), 0.5 * e)
            cr.fill()
            cr.set_line_width(px(1.6))
            cr.set_source_rgba(*(c2 if i % 5 == 0 else c1), 0.85 * e)
            cr.rectangle(x - w / 2, y - h / 2, w, h)
            cr.stroke()
            cr.restore()
            # a tiny world inside each
            if e > 0.6:
                cr.save()
                cr.rectangle(x - w / 2, y - h / 2, w, h)
                cr.clip()
                ph = i * 1.7
                for j in range(3):
                    rr = px(18 + j * 14) * e
                    ring(cr, x, y, rr, c2 if j == 0 else c1, 1.4, 0.5,
                         a0=s.t * (0.6 + j * 0.3) + ph, a1=s.t * (0.6 + j * 0.3) + ph + TAU * 0.7)
                dot(cr, x + math.cos(s.t + ph) * px(26), y + math.sin(s.t * 1.3 + ph) * px(18),
                    px(4), (1, 1, 1), 0.8)
                cr.restore()
    text_at(cr, W / 2, H - px(100), 'instances: %d   ·   all running' % (cols * rows),
            px(24), c1, 'cb', FONT_EN, alpha=0.55 * k, spacing=3)


def execution_run(cr, s):
    """Placeholder kept for the plan table; the boot movement owns this shot."""
    from shots_boot import execution_run as f
    return f(cr, s)


def you_left(cr, s):
    """Though you have left — an empty outline where someone was."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.54
    # the silhouette from if_i_can, now hollow, on one side only
    cr.save()
    cr.set_line_width(px(3))
    cr.set_source_rgba(*c1, 0.55)
    cr.arc(cx + px(340), cy, px(66), 0, TAU)
    cr.stroke()
    cr.rectangle(cx + px(284), cy + px(40), px(112), px(260))
    cr.stroke()
    cr.restore()
    # dust drifting out of it
    for i in range(70):
        u = ((s.t * 0.28 + rnd(149, i)) % 1.0)
        a = rnd(151, i) * TAU
        rr = px(140) * u ** 1.4
        x = cx + px(340) + rr * math.cos(a) * 1.6
        y = cy + px(150) + rr * math.sin(a) - u * px(200)
        dot(cr, x, y, px(2.6), c1, (1 - u) * 0.5)
    # a fading connection line
    dashed_line(cr, cx - px(180), cy + px(60), cx + px(260), cy + px(60), 10, 14,
                2.0, c1, 0.30)
    glow(cr, cx - px(120), cy, px(600), c1, 0.10, key='g_key')


def left2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # the phrase itself becomes the imagery: letters losing coherence
    cx, cy = W / 2, H * 0.5
    for i in range(56):
        a = rnd(157, i) * TAU
        rr = px(560) * (0.2 + rnd(163, i))
        x = cx + rr * math.cos(a)
        y = cy + rr * math.sin(a) * 0.6
        ch = 'YOU HAVE LEFT'[i % 13]
        if ch == ' ':
            continue
        text_at(cr, x, y, ch, px(16 + rnd(167, i) * 46), c1, 'cc', FONT_EN,
                weight=800, alpha=0.10 + 0.30 * rnd(173, i), spacing=6)
    glow(cr, cx, cy, px(700), c1, 0.10, key='g_key')


def left3(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # rows of the phrase scrolling away upward
    for r in range(14):
        y = H + px(80) - ((s.t * px(120) + r * px(96)) % (H + px(200)))
        a = (1 - abs(y - H * 0.5) / (H * 0.6)) * 0.5
        if a <= 0:
            continue
        text_at(cr, W / 2, y, 'YOU HAVE LEFT', px(34), c1, 'cc', FONT_EN,
                weight=800, alpha=max(0, a) * 0.55, spacing=20)
    glow(cr, W / 2, H * 0.5, px(620), c1, 0.10, key='g_key')


def left4(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # the two silhouettes, both hollow now, drifting apart
    k = ease_out(clamp01(s.p * 1.2), 1.6)
    cy = H * 0.54
    for sgn, col in ((-1, c1), (1, c1)):
        bx = W / 2 + sgn * (px(180) + px(220) * k)
        cr.save()
        cr.set_line_width(px(2.6))
        cr.set_source_rgba(*col, 0.45)
        cr.arc(bx, cy, px(56), 0, TAU)
        cr.stroke()
        cr.rectangle(bx - px(48), cy + px(34), px(96), px(220))
        cr.stroke()
        cr.restore()
    for i in range(40):
        u = ((s.t * 0.4 + rnd(179, i)) % 1.0)
        x = W / 2 + (rnd(181, i) - 0.5) * px(120)
        y = cy + px(160) - u * px(400)
        dot(cr, x, y, px(2.2), c1, (1 - u) * 0.35)


def left5(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # a grid that is missing cells where the other one used to be
    cols, rows = 16, 9
    k = clamp01(s.p * 1.3)
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            x = px(80) + c * ((W - px(160)) / (cols - 1))
            y = px(90) + r * ((H - px(180)) / (rows - 1))
            hole = 0.35 + 0.65 * rnd(191, (r * 3 + c * 7) % 60)
            present = hole > k * 0.9
            if present:
                dot(cr, x, y, px(3.4), c1, 0.55 * (1 - rnd(193, i) * 0.4))
            else:
                ring(cr, x, y, px(9), c2, 1.2, 0.30 * (1 - abs(k - 0.5) * 2 + 0.4))


def isolation(cr, s):
    """You have left me in isolation — one node, far from everything."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.52
    # the network recedes
    k = ease_out(clamp01(s.p), 1.4)
    for i in range(70):
        a = rnd(197, i) * TAU
        rr = px(260 + rnd(199, i) * 700) * (1 + 0.5 * k)
        x = cx + rr * math.cos(a)
        y = cy + rr * math.sin(a) * 0.7
        if 0 <= x <= W and 0 <= y <= H:
            dot(cr, x, y, px(3.0), c1, 0.35 * (1 - k * 0.5))
            cr.save()
            cr.set_line_width(px(1.0))
            cr.set_source_rgba(*c1, 0.10 * (1 - k * 0.6))
            cr.move_to(x, y)
            cr.line_to(cx, cy)
            cr.stroke()
            cr.restore()
    # the lonely node
    glow(cr, cx, cy, px(340), c2, 0.45, key='g_sec')
    dot(cr, cx, cy, px(16), c2, 1.0)
    for i in range(4):
        u = ((s.t * 0.5 + i / 4.0) % 1.0)
        ring(cr, cx, cy, px(60) + px(700) * u, c2, 2.0, (1 - u) ** 1.6 * 0.45)


def if_can5(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.5), 2.0)
    # a hand-shaped void, cracking
    cx, cy = W / 2, H * 0.52
    for i in range(26):
        a = rnd(211, i) * TAU
        rr = px(420) * rnd(223, i) * k
        x0 = cx + rr * math.cos(a); y0 = cy + rr * math.sin(a)
        L = px(160 + rnd(227, i) * 320) * k
        b = a + (rnd(229, i) - 0.5) * 0.5
        cr.save()
        cr.set_line_width(px(2.4))
        cr.set_source_rgba(*(c2 if i % 3 == 0 else c1), 0.7 * k)
        cr.move_to(x0, y0)
        cr.line_to(x0 + L * math.cos(b), y0 + L * math.sin(b))
        cr.stroke()
        cr.restore()
    glow(cr, cx, cy, px(600) * k, c1, 0.22 * k, key='g_key')


def fragments(cr, s):
    """Erase all the pointless fragments — pieces are swept away."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.1), 1.8)
    for i in range(120):
        x0 = rnd(233, i) * W
        y0 = rnd(239, i) * H
        sz = px(14 + rnd(241, i) * 70)
        rot = rnd(251, i) * TAU + s.t * 0.2
        # swept toward the right edge and off
        u = clamp01((k * 1.6 - rnd(257, i) * 0.6) / 1.0)
        e = ease_in(u, 2.2)
        x = x0 + e * (W * 1.3)
        y = y0 + e * px(140) * (rnd(263, i) - 0.5)
        a = (1 - e) * (0.25 + 0.55 * rnd(269, i))
        if a <= 0.005:
            continue
        cr.save()
        cr.translate(x, y)
        cr.rotate(rot + e * 3.0)
        poly(cr, [(-sz, -sz * 0.6), (sz, -sz * 0.7), (sz * 0.7, sz), (-sz * 0.8, sz * 0.8)],
             c2 if i % 4 == 0 else c1, a, 2.0, close=True)
        cr.restore()
    # the sweep line
    sx = px(100) + (W - px(200)) * ease_io(clamp01(s.p * 1.1))
    cr.save()
    cr.set_line_width(px(3))
    cr.set_source_rgba(*c2, 0.6)
    cr.move_to(sx, 0); cr.line_to(sx, H)
    cr.stroke()
    cr.restore()
    glow(cr, sx, H / 2, px(400), c2, 0.3, key='g_sec')


def maybe1(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # a probability field: dots resolving into certainty
    for i in range(160):
        x = rnd(271, i) * W
        y = rnd(277, i) * H
        a = 0.08 + 0.28 * rnd(281, i)
        dot(cr, x, y, px(2.6), c1, a)
    k = ease_out(clamp01(s.p * 1.4), 2.0)
    cr.save()
    cr.set_line_width(px(2.4))
    cr.set_source_rgba(*c2, 0.5)
    cr.move_to(px(160), H * 0.5)
    cr.line_to(px(160) + (W - px(320)) * k, H * 0.5)
    cr.stroke()
    cr.restore()
    text_at(cr, W / 2, H * 0.5 - px(60), 'P = %.2f' % (0.5 + 0.5 * k), px(40), c2,
            'cb', FONT_EN, alpha=0.7, spacing=4)


def maybe2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.4), 2.0)
    glow(cr, W / 2, H / 2, px(700) * k, c2, 0.24 * k, key='g_sec')
    text_at(cr, W / 2, H / 2, 'MAYBE', px(180), c2, 'cc', FONT_EN, weight=900,
            alpha=0.30 * (0.6 + 0.4 * math.sin(s.t * 3.0)), spacing=30)


def disheartened(cr, s):
    """You won't leave me so disheartened — a heart with a crack."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.52
    R = px(300)
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    # parametric heart
    pts = []
    for i in range(241):
        u = i / 240.0 * TAU
        x = 16 * math.sin(u) ** 3
        y = 13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u)
        pts.append((cx + x * R / 17.0, cy - y * R / 17.0))
    cr.save()
    cr.set_line_width(px(4.5))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(*c2, 0.9 * k)
    cr.new_path()
    for i, p in enumerate(pts):
        if i == 0:
            cr.move_to(*p)
        else:
            cr.line_to(*p)
    cr.stroke()
    cr.restore()
    # dim fill
    poly(cr, pts, c2, 0.10 * k, 1.0, close=True, fill=True)
    # the crack rips down the middle
    ck = clamp01((s.p - 0.25) * 1.5)
    cr.save()
    cr.set_line_width(px(6))
    cr.set_source_rgba(0.02, 0.03, 0.06, 0.95)
    cr.new_path()
    cr.move_to(cx, cy - R * 0.72)
    n = 9
    for i in range(1, n + 1):
        u = i / n
        yy = cy - R * 0.72 + R * 1.45 * u * ck
        xx = cx + math.sin(u * 9) * R * 0.10
        cr.line_to(xx, yy)
    cr.stroke()
    cr.restore()
    glow(cr, cx, cy, px(600), c2, 0.16 * k, key='g_sec')


def challenging(cr, s):
    """Challenging your God — lightning into the cathedral."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # rays from above, as in only_god, now in warning colours
    apex = (W / 2, -px(100))
    for i in range(20):
        a = math.pi * 0.25 + math.pi * 0.5 * (i / 19.0)
        cr.save()
        cr.set_line_width(px(24))
        cr.set_source_rgba(*(c2 if i % 3 == 0 else c1), 0.05 * (0.5 + 0.5 * math.sin(s.t + i)))
        cr.move_to(*apex)
        cr.line_to(apex[0] + px(1800) * math.cos(a), apex[1] + px(1800) * math.sin(a))
        cr.stroke()
        cr.restore()
    # three bolts
    for b in range(3):
        seed = 271 + b * 17
        cr.save()
        cr.set_line_width(px(4 - b))
        cr.set_source_rgba(*(c2 if b == 0 else c1), 0.85 - b * 0.22)
        cr.new_path()
        x, y = W / 2 + (b - 1) * px(180), 0
        cr.move_to(x, y)
        for i in range(22):
            x += (rnd(seed, i) - 0.5) * px(150)
            y += (H * 0.86) / 22
            cr.line_to(x, y)
        cr.stroke()
        cr.restore()
        glow(cr, W / 2 + (b - 1) * px(180), H * 0.45, px(400), c2, 0.16, key='g_sec')
    # the figure at the bottom, looking up
    fy = H - px(120)
    dot(cr, W / 2, fy - px(70), px(24), shade(c1, 0.6), 0.95)
    poly(cr, [(W / 2 - px(36), fy), (W / 2 - px(18), fy - px(60)),
              (W / 2 + px(18), fy - px(60)), (W / 2 + px(36), fy)],
         shade(c1, 0.6), 0.95, 3.0)


def made_some(cr, s):
    """You have made some — an error count climbing."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    hex_grid(cr, c1, alpha=0.05)
    k = ease_out(clamp01(s.p * 1.2), 2.0)
    n = int(7 * k)
    for i in range(n):
        y = px(200) + i * px(78)
        cr.save()
        cr.set_line_width(px(1.6))
        cr.set_source_rgba(*(c2 if i == n - 1 else c1), 0.55)
        cr.rectangle(px(200), y, W - px(400), px(58))
        cr.stroke()
        cr.restore()
        text_at(cr, px(230), y + px(29), 'ERROR  0x%04X' % (0x2F00 + i * 0x11),
                px(26), c2 if i == n - 1 else c1, 'lc', FONT_EN, alpha=0.8, spacing=2)
        text_at(cr, W - px(230), y + px(29), 'unhandled', px(22), c1, 'rc',
                FONT_EN, alpha=0.45)
    text_at(cr, px(200), H - px(120), 'total = %d' % n, px(30), c2, 'lb', FONT_EN,
            alpha=0.75 * k, spacing=3)


def illegal(cr, s):
    """Illegal arguments — arguments rejected by the parser."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.1), 1.8)
    # a redaction sweep crossing out a line of code
    text = 'void love(node &you) { return you; }'
    x0, y0 = px(160), H * 0.44
    text_at(cr, x0, y0, text, px(52), c1, 'lt', FONT_EN, alpha=0.7)
    for i in range(3):
        pass
    # the strike-through
    w = px(52) * 0.60 * len(text) * k
    cr.save()
    cr.set_line_width(px(9))
    cr.set_source_rgba(*c2, 0.9)
    cr.move_to(x0 - px(10), y0 + px(30))
    cr.line_to(x0 - px(10) + min(w, W - px(200)), y0 + px(30))
    cr.stroke()
    cr.restore()
    text_at(cr, x0, y0 + px(120), 'SYNTAX ERROR: illegal arguments', px(34), c2,
            'lt', FONT_EN, alpha=0.85 * k, spacing=2)
    # rejection stamps
    for i in range(18):
        x = rnd(283, i) * W
        y = rnd(293, i) * H
        a = 0.05 + 0.10 * rnd(307, i)
        cr.save()
        cr.translate(x, y)
        cr.rotate(-0.35 + rnd(311, i) * 0.7)
        cr.set_line_width(px(3))
        cr.set_source_rgba(*c2, a)
        cr.rectangle(-px(90), -px(26), px(180), px(52))
        cr.stroke()
        cr.restore()


def solo1(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # the code line, now fully struck through and burning at the ends
    text = 'void love(node &you) { return you; }'
    x0, y0 = px(160), H * 0.44
    text_at(cr, x0, y0, text, px(52), c1, 'lt', FONT_EN, alpha=0.25)
    cr.save()
    cr.set_line_width(px(9))
    cr.set_source_rgba(*c2, 0.9)
    cr.move_to(x0 - px(10), y0 + px(30))
    cr.line_to(x0 + px(52) * 0.60 * len(text), y0 + px(30))
    cr.stroke()
    cr.restore()
    for i in range(50):
        u = ((s.t * 0.9 + rnd(313, i)) % 1.0)
        x = x0 + rnd(317, i) * px(52) * 0.6 * len(text)
        y = y0 + px(30) - u * px(300)
        dot(cr, x, y, px(2.4), c2, (1 - u) * 0.6)
    glow(cr, W / 2, y0 + px(30), px(700), c2, 0.16, key='g_sec')


def solo2(cr, s):
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    # everything burns down to ash
    k = clamp01(s.p * 1.1)
    for i in range(140):
        x = rnd(331, i) * W
        y = rnd(337, i) * H
        u = ((s.t * 0.6 + rnd(347, i)) % 1.0)
        yy = y - u * px(400)
        a = (1 - u) * 0.5 * (1 - k * 0.7)
        dot(cr, x + math.sin(u * 5 + i) * px(20), yy, px(2.0 + rnd(349, i) * 3.0),
            c2 if i % 4 == 0 else c1, a)
    glow(cr, W / 2, H * 0.9, px(1100), c2, 0.20 * (1 - k), key='g_sec')
    for i in range(6):
        cr.save()
        cr.set_line_width(px(2))
        cr.set_source_rgba(*c1, 0.10 * (1 - k))
        yy = H * (0.1 + i * 0.15)
        cr.move_to(0, yy); cr.line_to(W, yy)
        cr.stroke()
        cr.restore()
