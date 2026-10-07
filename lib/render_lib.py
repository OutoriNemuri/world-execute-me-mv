"""render_lib — canvas, colour, gradient, text and cache primitives.

Everything here is platform independent: cairo for vector work, Pango for text,
Pillow only for reading bitmaps.  No ffmpeg dependency.
"""
import math, os, colorsys
import cairo
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo

W, H = 1920, 1080
FPS = 30
TAU = math.pi * 2
SONG_END = 216.0          # video length; audio is 211.96s, the rest is a black tail

FONT_EN = "Inter"
FONT_ZH = "Source Han Sans CN"

# ---------------------------------------------------------------- colour ----

def hexc(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def shade(c, f):
    return tuple(max(0.0, min(1.0, v * f)) for v in c)


def hsv(h, s, v):
    return colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))


def rgba(c, a):
    return (c[0], c[1], c[2], max(0.0, min(1.0, a)))


# ------------------------------------------------------------- easing ------

def clamp01(x):
    return 0.0 if x < 0 else (1.0 if x > 1 else x)


def smoothstep(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    t = clamp01((x - a) / (b - a))
    return t * t * (3 - 2 * t)


def ease_out(t, p=3.0):
    return 1.0 - (1.0 - clamp01(t)) ** p


def ease_in(t, p=3.0):
    return clamp01(t) ** p


def ease_io(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)


def pulse(t, f=1.0):
    """0..1 sine pulse."""
    return 0.5 - 0.5 * math.cos(TAU * f * t)


def flicker(t, seed=0.0, rate=17.0):
    return 0.5 + 0.5 * math.sin(t * rate + seed * 7.3)


# ------------------------------------------------------------ geometry -----

def unit():
    """Canvas geometry scaled off the frame HEIGHT so that 16:9 and square
    storyboards keep the same vertical rhythm."""
    return H / 1080.0


U = unit()


def px(v):
    return v * U


# ------------------------------------------------------------- cache -------

_CACHE = {}
_CACHE_ORDER = []
_CACHE_MAX = 90


def cached(key, builder):
    """Memoise an expensive surface.  builder() -> cairo.ImageSurface."""
    if key in _CACHE:
        return _CACHE[key]
    surf = builder()
    _CACHE[key] = surf
    _CACHE_ORDER.append(key)
    while len(_CACHE_ORDER) > _CACHE_MAX:
        old = _CACHE_ORDER.pop(0)
        _CACHE.pop(old, None)
    return surf


def clear_cache():
    _CACHE.clear()
    _CACHE_ORDER.clear()


# ------------------------------------------------------------ patterns -----

def surface_pattern(surf, x, y, w, h, alpha=1.0):
    """Draw `surf` into the rect (x, y, w, h) as a magnified pattern.

    EXTEND_PAD is mandatory: without it cairo *tiles* the pattern and the
    canvas edges turn into a repeating seam.
    """
    pat = cairo.SurfacePattern(surf)
    pat.set_extend(cairo.EXTEND_PAD)
    sx = w / surf.get_width()
    sy = h / surf.get_height()
    m = cairo.Matrix()
    m.translate(x, y)
    m.scale(sx, sy)
    pat.set_matrix(m)
    return pat


def blit(cr, surf, x, y, w, h, alpha=1.0):
    cr.save()
    cr.set_source(surface_pattern(surf, x, y, w, h))
    if alpha < 1.0:
        cr.paint_with_alpha(alpha)
    else:
        cr.paint()
    cr.restore()


# ------------------------------------------------------------- gradient ----

def radial_surface(n, stops, size=256):
    """Pre-render a radial gradient to a small surface (cheap to reuse)."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    cr = cairo.Context(surf)
    g = cairo.RadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
    for pos, col in stops:
        g.add_color_stop_rgba(pos, col[0], col[1], col[2], col[3] if len(col) > 3 else 1.0)
    cr.set_source(g)
    cr.paint()
    return surf


def glow(cr, cx, cy, r, col, alpha=1.0, key=None, falloff=1.0):
    """Radial glow, cached by key."""
    def build():
        stops = []
        n = 12
        for i in range(n + 1):
            p = i / n
            a = (1.0 - p) ** (2.2 * falloff)
            stops.append((p, (col[0], col[1], col[2], a)))
        return radial_surface(n, stops, 192)
    surf = cached(key or ('glow', col, round(falloff, 2)), build)
    blit(cr, surf, cx - r, cy - r, r * 2, r * 2, alpha)


def bg_gradient(cr, c_in, c_out, cx=0.5, cy=0.45, r=1.25, key=None):
    """Full-frame radial background gradient (pre-rendered + cached)."""
    def build():
        stops = [(0.0, (c_in[0], c_in[1], c_in[2], 1.0)),
                 (0.55, (mix(c_in, c_out, 0.55)[0], mix(c_in, c_out, 0.55)[1],
                         mix(c_in, c_out, 0.55)[2], 1.0)),
                 (1.0, (c_out[0], c_out[1], c_out[2], 1.0))]
        return radial_surface(3, stops, 128)
    surf = cached(key or ('bg', c_in, c_out), build)
    cr.save()
    # fill everything, then paint the (circular) gradient over it
    cr.set_source_rgb(*c_out)
    cr.paint()
    cr.restore()
    R = px(1150) * r
    blit(cr, surf, W * cx - R, H * cy - R, R * 2, R * 2, 1.0)


def grad_rect(cr, x, y, w, h, col_a, col_b, vertical=True, alpha=1.0):
    g = cairo.LinearGradient(x, y, x, y + h) if vertical else cairo.LinearGradient(x, y, x + w, y)
    g.add_color_stop_rgba(0, col_a[0], col_a[1], col_a[2], alpha)
    g.add_color_stop_rgba(1, col_b[0], col_b[1], col_b[2], alpha)
    cr.set_source(g)
    cr.rectangle(x, y, w, h)
    cr.fill()


# ---------------------------------------------------------------- text -----

def layout(cr, text, size, color, font=FONT_EN, weight=None, alpha=1.0,
           spacing=None, italic=False):
    lay = PangoCairo.create_layout(cr)
    desc = Pango.FontDescription(font)
    desc.set_absolute_size(size * Pango.SCALE)
    if weight:
        desc.set_weight(weight)
    if italic:
        desc.set_style(Pango.Style.ITALIC)
    lay.set_font_description(desc)
    if spacing is not None:
        lay.set_spacing(spacing * Pango.SCALE)
    lay.set_text(text, -1)
    return lay


def text_at(cr, x, y, text, size, color, anchor='lt', font=FONT_EN, weight=None,
            alpha=1.0, spacing=None, shadow=0.0, glow_r=0.0, italic=False):
    """Draw text. anchor is a 2-char string: l/c/r + t/c/b (baseline 'a' too)."""
    lay = layout(cr, text, size, color, font, weight, alpha, spacing, italic)
    tw, th = lay.get_pixel_size()
    ax, ay = anchor[0], anchor[1]
    if ax == 'c':
        x -= tw / 2.0
    elif ax == 'r':
        x -= tw
    if ay == 'c':
        y -= th / 2.0
    elif ay == 'b':
        y -= th
    elif ay == 'a':
        y -= th * 0.78
    cr.save()
    if shadow > 0:
        cr.save()
        cr.move_to(x + px(2.5), y + px(3.0))
        cr.set_source_rgba(0, 0, 0, 0.72 * alpha)
        PangoCairo.show_layout(cr, lay)
        cr.restore()
    cr.move_to(x, y)
    if glow_r > 0:
        g = cairo.RadialGradient(0, 0, 0, 0, 0, 0)  # placeholder, unused
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    PangoCairo.show_layout(cr, lay)
    cr.restore()
    return tw, th


def text_w(text, size, font=FONT_EN, weight=None, spacing=None):
    """Measure text width without a live context (uses a 1x1 scratch surface)."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8)
    cr = cairo.Context(surf)
    lay = layout(cr, text, size, (1, 1, 1), font, weight, 1.0, spacing)
    return lay.get_pixel_size()[0]


def text_glow(cr, x, y, text, size, color, anchor='cc', font=FONT_EN, weight=None,
              alpha=1.0, spacing=None, halo=1.0, shadow=True, italic=False):
    """Text with a soft coloured halo — the default lyric look."""
    lay = layout(cr, text, size, color, font, weight, alpha, spacing, italic)
    tw, th = lay.get_pixel_size()
    ax, ay = anchor[0], anchor[1]
    if ax == 'c':
        x -= tw / 2.0
    elif ax == 'r':
        x -= tw
    if ay == 'c':
        y -= th / 2.0
    elif ay == 'b':
        y -= th
    elif ay == 'a':
        y -= th * 0.78
    cr.save()
    if shadow:
        cr.move_to(x + px(3), y + px(3.6))
        cr.set_source_rgba(0, 0, 0, 0.78 * alpha)
        PangoCairo.show_layout(cr, lay)
    # halo pass: same glyphs, drawn fat via a stroke
    if halo > 0:
        cr.save()
        cr.move_to(x, y)
        cr.set_line_width(px(9 * halo))
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        PangoCairo.layout_path(cr, lay)
        cr.set_source_rgba(0, 0, 0, 0.55 * alpha)
        cr.stroke()
        cr.restore()
    cr.move_to(x, y)
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    PangoCairo.show_layout(cr, lay)
    cr.restore()
    return tw, th


# ---------------------------------------------------------------- misc -----

def dashed_line(cr, x1, y1, x2, y2, dash=10, gap=8, width=1.5, color=(1, 1, 1),
                alpha=0.4):
    cr.save()
    cr.set_dash([px(dash), px(gap)])
    cr.set_line_width(px(width))
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    cr.move_to(x1, y1)
    cr.line_to(x2, y2)
    cr.stroke()
    cr.restore()


def arrow(cr, x1, y1, x2, y2, color, width=2.0, alpha=0.8, head=12.0):
    cr.save()
    cr.set_line_width(px(width))
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    cr.move_to(x1, y1)
    cr.line_to(x2, y2)
    cr.stroke()
    a = math.atan2(y2 - y1, x2 - x1)
    hs = px(head)
    cr.move_to(x2, y2)
    cr.line_to(x2 - hs * math.cos(a - 0.4), y2 - hs * math.sin(a - 0.4))
    cr.line_to(x2 - hs * math.cos(a + 0.4), y2 - hs * math.sin(a + 0.4))
    cr.close_path()
    cr.fill()
    cr.restore()


def dot(cr, x, y, r, color, alpha=1.0):
    cr.save()
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    cr.arc(x, y, r, 0, TAU)
    cr.fill()
    cr.restore()


def ring(cr, x, y, r, color, width=2.0, alpha=1.0, dash=None, a0=0, a1=TAU):
    cr.save()
    if dash:
        cr.set_dash([px(dash[0]), px(dash[1])])
    cr.set_line_width(px(width))
    cr.set_source_rgba(color[0], color[1], color[2], alpha)
    cr.arc(x, y, r, a0, a1)
    cr.stroke()
    cr.restore()


def poly(cr, pts, color, alpha=1.0, width=2.0, close=False, fill=False):
    if not pts:
        return
    cr.save()
    cr.new_path()
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    if close:
        cr.close_path()
    if fill:
        cr.set_source_rgba(color[0], color[1], color[2], alpha)
        cr.fill()
    else:
        cr.set_line_width(px(width))
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.set_source_rgba(color[0], color[1], color[2], alpha)
        cr.stroke()
    cr.restore()


def vignette(cr, strength=0.55, key='vig'):
    surf = cached(key, lambda: _vignette_surface())
    blit(cr, surf, 0, 0, W, H, strength)


def _vignette_surface():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 256, 144)
    cr = cairo.Context(surf)
    g = cairo.RadialGradient(128, 72, 40, 128, 72, 160)
    g.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
    g.add_color_stop_rgba(0.62, 0, 0, 0, 0.10)
    g.add_color_stop_rgba(1.0, 0, 0, 0, 0.92)
    cr.set_source(g)
    cr.paint()
    return surf


def scanlines(cr, alpha=0.05, step=3):
    cr.save()
    cr.set_source_rgba(0, 0, 0, alpha)
    y = 0
    while y < H:
        cr.rectangle(0, y, W, px(1.1))
        y += step
    cr.fill()
    cr.restore()


def noise(cr, t, alpha=0.035, seed=0, cells=220):
    cr.save()
    cr.set_source_rgba(1, 1, 1, alpha)
    for i in range(cells):
        f = (i * 2654435761 + seed * 40503) % 1000003
        x = (f % 1920)
        y = ((f // 1920 + int(t * 37)) % 1080)
        cr.rectangle(x, y, px(1.4), px(1.4))
    cr.fill()
    cr.restore()


def clip_rect(cr, x, y, w, h):
    cr.rectangle(x, y, w, h)
    cr.clip()


# -------------------------------------------------------------- timeline ---

class ShotClock:
    """Per-shot local time helper handed to every shot function."""

    __slots__ = ('t', 't0', 't1', 'dur', 'lt', 'p', 'idx', 'line', 'ctx')

    def __init__(self, t, t0, t1, idx, line, ctx):
        self.t = t
        self.t0 = t0
        self.t1 = t1
        self.dur = max(1e-3, t1 - t0)
        self.lt = t - t0                      # local time, seconds
        self.p = clamp01(self.lt / self.dur)  # 0..1 progress
        self.idx = idx
        self.line = line
        self.ctx = ctx
