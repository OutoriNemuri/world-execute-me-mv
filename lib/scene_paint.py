"""scene_paint — reusable drawing primitives for the shots.

Everything is deterministic: given (t, progress, seed) a primitive draws the
same thing every time, which keeps the render reproducible across machines.
"""
import math
import cairo
from render_lib import (W, H, TAU, px, U, mix, shade, rgba, clamp01, smoothstep,
                        ease_out, ease_io, poly, dot, ring, cached, blit, glow,
                        text_at, text_glow, grad_rect, dashed_line, arrow,
                        surface_pattern, FONT_EN, FONT_ZH)

# ------------------------------------------------------------------- rng ---

def rnd(seed, i):
    """Cheap deterministic hash → [0,1)."""
    x = (i * 1103515245 + seed * 12345) & 0x7FFFFFFF
    x ^= (x >> 13)
    x = (x * 1274126177) & 0x7FFFFFFF
    return ((x >> 7) & 0xFFFF) / 65536.0


# ----------------------------------------------------------------- grid ----

def hex_grid(cr, color, cam_t=0.0, alpha=0.16, radius=None, width=1.0,
             breathe=0.0, scroll=0.0):
    """Isometric-ish hex lattice filling the frame; scrolls for parallax."""
    R = radius if radius is not None else px(64)
    dx = R * math.sqrt(3)
    dy = R * 1.5
    off = (scroll * dy) % dy
    j = -2
    y = -R + off
    while y < H + R * 2:
        stagger = (R * math.sqrt(3) / 2) if (j % 2) else 0.0
        x = -R + stagger - (dx * breathe)
        while x < W + R * 2:
            _hexagon(cr, x, y, R * (1.0 + breathe * 0.05), color, alpha, width)
            x += dx
        y += dy
        j += 1


def _hexagon(cr, cx, cy, r, color, alpha, width):
    cr.save()
    pts = []
    for k in range(6):
        a = TAU * k / 6 + math.pi / 6
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly(cr, pts, color, alpha, width, close=True)
    cr.restore()


def dot_field(cr, color, t, seed=1, count=180, alpha=0.5, drift=1.0,
              radius=1.8, react=None):
    """Sparse star/particle field with parallax drift."""
    cr.save()
    for i in range(count):
        fx = rnd(seed, i)
        fy = rnd(seed + 77, i)
        sp = 0.25 + rnd(seed + 11, i) * 1.2
        x = (fx * W + t * 18 * sp * drift) % W
        y = fy * H
        a = alpha * (0.35 + 0.65 * rnd(seed + 5, i))
        if react:
            x, y, a = react(i, x, y, a)
        dot(cr, x, y, px(radius) * (0.6 + rnd(seed + 3, i)), color, a)
    cr.restore()


def grid_lines(cr, color, alpha=0.12, step=84, width=1.0, off=0.0, mask=None):
    cr.save()
    cr.set_line_width(px(width))
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    x = (off % px(step)) - px(step)
    while x < W + px(step):
        cr.move_to(x, 0)
        cr.line_to(x, H)
        x += px(step)
    y = (off % px(step)) - px(step)
    while y < H + px(step):
        cr.move_to(0, y)
        cr.line_to(W, y)
        y += px(step)
    cr.stroke()
    cr.restore()


def crosshair(cr, x, y, r, color, alpha=0.7, width=1.2):
    cr.save()
    cr.set_line_width(px(width))
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    cr.move_to(x - r, y); cr.line_to(x + r, y)
    cr.move_to(x, y - r); cr.line_to(x, y + r)
    cr.stroke()
    ring(cr, x, y, r * 0.52, color, width, alpha * 0.9)
    cr.restore()


# -------------------------------------------------------------- wave -------

def wave_path(cr, x0, x1, y, amp, freq, phase, decay=0.0):
    """Streams a sine path; returns the point list so callers can reuse it."""
    pts = []
    n = 240
    for i in range(n + 1):
        u = i / n
        x = x0 + (x1 - x0) * u
        yy = y + amp * math.sin(u * freq * TAU + phase) * math.exp(-decay * u)
        pts.append((x, yy))
    cr.new_path()
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    return pts


def waveform(cr, x0, x1, y, amp, freq, phase, color, alpha=0.9, width=2.0,
             decay=0.0):
    cr.save()
    wave_path(cr, x0, x1, y, amp, freq, phase, decay)
    cr.set_line_width(px(width))
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    cr.stroke()
    cr.restore()


def audio_bars(cr, x0, x1, base_y, max_h, t, seed, color, count=72, alpha=0.85,
               width=0.62):
    """Spectrum-ish bar read-out."""
    cr.save()
    span = x1 - x0
    bw = span / count
    for i in range(count):
        f = rnd(seed, i)
        env = 0.35 + 0.65 * f
        v = env * (0.55 + 0.45 * math.sin(t * (2.4 + f * 7.0) + f * 9.0))
        h = max_h * clamp01(abs(v)) ** 0.8
        x = x0 + i * bw
        cr.rectangle(x, base_y - h, bw * width, h)
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    cr.fill()
    cr.restore()


def oscilloscope(cr, cx, cy, r, t, color, alpha=0.8, arms=1, width=1.6,
                 freq=5.0):
    """Radial scope: polar plot of a couple of sine families."""
    cr.save()
    cr.set_line_width(px(width))
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    for k in range(arms):
        cr.new_path()
        n = 320
        for i in range(n + 1):
            u = i / n
            a = u * TAU
            rr = r * (0.55 + 0.42 * math.sin(freq * a + t * (2.0 + k)))
            x = cx + rr * math.cos(a + k * TAU / max(1, arms))
            y = cy + rr * math.sin(a + k * TAU / max(1, arms))
            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
        cr.close_path()
        cr.stroke()
    cr.restore()


# --------------------------------------------------------------- pcb -------

def pcb_trace(cr, pts, color, alpha=0.7, width=2.0, pads=True, r=4.0):
    cr.save()
    cr.set_line_width(px(width))
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    cr.new_path()
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    cr.stroke()
    if pads:
        for p in (pts[0], pts[-1]):
            dot(cr, p[0], p[1], px(r), color, alpha)
    cr.restore()


def pcb_network(cr, seed, t, color, alpha=0.34, count=22, width=1.6):
    """A board of right-angle traces with vias."""
    cr.save()
    for i in range(count):
        x = rnd(seed, i) * W
        y = rnd(seed + 3, i) * H
        pts = [(x, y)]
        ang = 0 if rnd(seed + 9, i) > 0.5 else math.pi / 2
        L = px(90 + rnd(seed + 4, i) * 220)
        for k in range(3):
            nx = pts[-1][0] + L * math.cos(ang)
            ny = pts[-1][1] + L * math.sin(ang)
            pts.append((nx, ny))
            ang += math.pi / 2 * (1 if rnd(seed + i * 5 + k, i) > 0.5 else -1)
            L *= 0.72
        a = alpha * (0.4 + 0.6 * abs(math.sin(t * 0.7 + i)))
        pcb_trace(cr, pts, color, a, width, pads=True)
    cr.restore()


# ------------------------------------------------------------- circles -----

def arc_seg(cr, cx, cy, r, a0, a1, color, width, alpha):
    ring(cr, cx, cy, r, color, width, alpha, a0=a0, a1=a1)


def concentric(cr, cx, cy, r0, r1, n, color, alpha=0.5, width=1.2, rot=0.0,
               arc=TAU):
    for i in range(n):
        rr = r0 + (r1 - r0) * (i / max(1, n - 1))
        ring(cr, cx, cy, rr, color, width, alpha * (1.0 - 0.5 * i / max(1, n)),
             a0=rot, a1=rot + arc)


def orbit_ring(cr, cx, cy, r, t, color, color2, alpha=0.8, dots=8, width=2.0):
    ring(cr, cx, cy, r, color, width, alpha * 0.7)
    for i in range(dots):
        a = TAU * i / dots + t * 0.6
        rr = r * (1.0 + 0.035 * math.sin(t * 2.0 + i))
        dot(cr, cx + rr * math.cos(a), cy + rr * math.sin(a), px(4.2), color2,
            alpha)


def target_rings(cr, cx, cy, r, t, color, alpha=0.6, n=4):
    for i in range(n):
        p = (t * 0.5 + i / n) % 1.0
        rr = r * (0.25 + p * 1.35)
        ring(cr, cx, cy, rr, color, 1.6, alpha * (1.0 - p) ** 1.6)


# ------------------------------------------------------------- polygons ----

def wire_poly(cr, pts3, color, alpha=0.8, width=1.6, fill_alpha=0.0):
    """Projected 3D polygon; callers do the projection."""
    if fill_alpha > 0:
        poly(cr, pts3, color, fill_alpha, width, close=True, fill=True)
    poly(cr, pts3, color, alpha, width, close=True)


def project(p, cam_rx, cam_ry, dist=3.2):
    """Simple rotating-camera projection of a unit-scale point."""
    x, y, z = p
    ca, sa = math.cos(cam_ry), math.sin(cam_ry)
    x, z = x * ca - z * sa, x * sa + z * ca
    cb, sb = math.cos(cam_rx), math.sin(cam_rx)
    y, z = y * cb - z * sb, y * sb + z * cb
    z += dist
    if z < 0.2:
        z = 0.2
    f = 1.0 / z
    return x * f, y * f, z


def cube_faces(size=1.0):
    s = size / 2
    v = [(-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
         (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)]
    faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
             (3, 2, 6, 7), (0, 3, 7, 4), (1, 2, 6, 5)]
    return v, faces


def wire_box(cr, cx, cy, scale, cam_rx, cam_ry, color, alpha=0.85, width=1.8):
    s = scale * px(150)
    s /= 3.2  # projection normalisation
    v, faces = cube_faces(1.0)
    proj = [project(p, cam_rx, cam_ry) for p in v]
    for f in faces:
        pts = [(cx + proj[i][0] * s, cy + proj[i][1] * s) for i in f]
        poly(cr, pts, color, alpha, width, close=True)
