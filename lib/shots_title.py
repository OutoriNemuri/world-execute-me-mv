# -*- coding: utf-8 -*-
"""shots_title — the film-style title sequence in the interlude (16.3–29.8s).

Five cards, like a credit sequence: studio → cover art → song title → artist →
album.  The cover art is used as an *object* (a framed plate), never as a
background, except for the deliberate slow push-in on the final card.
"""
import math
import cairo
from render_lib import (W, H, TAU, px, mix, shade, clamp01, smoothstep, ease_out,
                        ease_in, ease_io, pulse, text_at, text_glow, grad_rect,
                        dashed_line, dot, ring, poly, glow, blit, cached,
                        vignette, FONT_EN, FONT_ZH, surface_pattern, text_w)
from scene_paint import rnd, hex_grid, dot_field, grid_lines, crosshair, concentric

COVER = None
_COVER_BUF = [None]
SONG_TITLE = 'world.execute(me);'
SONG_ZH = '世界执行（我）'
ARTIST = 'MILI'
ALBUM = 'Miracle Milk'
STUDIO = 'A CODE-GENERATED FILM'


def load_cover(path):
    """Load the cover into a cairo surface, swapping PIL's RGBA to cairo BGRA."""
    global COVER
    from PIL import Image
    im = Image.open(path).convert('RGBA').resize((1024, 1024), Image.LANCZOS)
    ba = bytearray(im.tobytes())
    for i in range(0, len(ba), 4):
        ba[i], ba[i + 2] = ba[i + 2], ba[i]
    _COVER_BUF[0] = ba          # module-level ref: cairo does not own the buffer
    COVER = cairo.ImageSurface.create_for_data(
        _COVER_BUF[0], cairo.FORMAT_ARGB32, 1024, 1024, 1024 * 4)
    return COVER


def _cover():
    return COVER


def _frame_plate(cr, x, y, size, glow_col, k=1.0, corner=True):
    """A thin tech frame around an image plate."""
    cr.save()
    cr.set_line_width(px(1.6))
    for i, off in enumerate((0, -px(14))):
        a = (0.55 if i == 0 else 0.22) * k
        cr.set_source_rgba(glow_col[0], glow_col[1], glow_col[2], a)
        m = px(14) if i == 0 else px(28)
        cr.rectangle(x - m, y - m, size + m * 2, size + m * 2)
        cr.stroke()
    if corner:
        L = px(46) * k
        cr.set_line_width(px(3))
        cr.set_source_rgba(*glow_col, 0.9 * k)
        for cx, cy, sx, sy in ((x - px(28), y - px(28), 1, 1),
                               (x + size + px(28), y - px(28), -1, 1),
                               (x - px(28), y + size + px(28), 1, -1),
                               (x + size + px(28), y + size + px(28), -1, -1)):
            cr.move_to(cx, cy + L * sy)
            cr.line_to(cx, cy)
            cr.line_to(cx + L * sx, cy)
        cr.stroke()
    cr.restore()


def card_studio(cr, s):
    """First card: a studio / provenance slate, very restrained."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.6), 2.0)
    # blueprint paper
    grid_lines(cr, c1, 0.06, 96, 1.0)
    grid_lines(cr, c1, 0.035, 24, 1.0)
    # a big technical circle being drawn
    r = px(300) * ease_out(clamp01(s.p * 2.0), 2.4)
    ring(cr, W / 2, H / 2, r, c1, 1.6, 0.4 * k, dash=(10, 14))
    crosshair(cr, W / 2, H / 2, r * 0.34, c1, 0.35 * k, 1.2)
    a = smoothstep(0.30, 0.70, s.p)
    text_glow(cr, W / 2, H * 0.5 - px(20), STUDIO, px(38), c1, 'cc',
              FONT_EN, alpha=a, spacing=18)
    text_glow(cr, W / 2, H * 0.5 + px(52), '基于 MILI 同名歌曲', px(24), c2, 'cc',
              FONT_ZH, alpha=a * 0.85, spacing=6, halo=0.8)
    # little plate number, bottom-left, like a slate
    text_at(cr, px(90), H - px(80), 'PLATE 01', px(20), c1, 'lb', FONT_EN,
            alpha=0.42 * a, spacing=3)
    text_at(cr, W - px(90), H - px(80), '16.30 – 19.20', px(20), c1, 'rb',
            FONT_EN, alpha=0.42 * a, spacing=3)


def card_cover(cr, s):
    """Second card: the album cover rises into frame as a physical plate."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cov = _cover()
    size = px(560)
    x = W / 2 - size / 2
    rise = ease_out(clamp01(s.p * 1.5), 2.6)
    y = H * 0.5 - size / 2 + px(120) * (1 - rise)
    # stage spotlight behind the plate
    glow(cr, W / 2, H * 0.5, px(760), c1, 0.32 * rise, key='g_key')
    # reflection pool
    if cov:
        cr.save()
        pat = cairo.SurfacePattern(cov)
        pat.set_extend(cairo.EXTEND_PAD)
        m = cairo.Matrix()
        m.translate(x, y + size * 1.02, )
        m.scale(size / 1024.0, -size / 1024.0 * 0.30)
        pat.set_matrix(m)
        cr.set_source(pat)
        cr.rectangle(x, y + size * 1.02, size, size * 0.34)
        cr.clip()
        cr.paint_with_alpha(0.16 * rise)
        cr.restore()
    # the plate itself
    if cov:
        cr.save()
        cr.rectangle(x, y, size, size)
        cr.clip()
        blit(cr, cov, x, y, size, size, min(1.0, rise * 1.4))
        cr.restore()
    _frame_plate(cr, x, y, size, c2, rise)
    # scanning bar sweeping the plate
    if 0.15 < s.p < 0.95:
        yb = y + size * ((s.t - s.t0) * 0.55 % 1.0)
        grad_rect(cr, x, yb - px(24), size, px(48), c2, c1, True, 0.10)
        cr.save()
        cr.set_line_width(px(1.6))
        cr.set_source_rgba(*c2, 0.5)
        cr.move_to(x, yb); cr.line_to(x + size, yb)
        cr.stroke()
        cr.restore()
    text_at(cr, W / 2, y + size + px(72), 'ALBUM ARTWORK', px(24), c1, 'ct',
            FONT_EN, alpha=0.55 * rise, spacing=8)


def card_song(cr, s):
    """Third card: the song title, big and engraved."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    hex_grid(cr, c1, alpha=0.05)
    cov = _cover()
    size = px(300)
    x = W / 2 + px(430)
    y = H / 2 - size / 2
    k = ease_out(clamp01(s.p * 1.6), 2.2)
    if cov:
        # the cover has slid aside to make room for the title
        cr.save()
        cr.rectangle(x, y, size, size)
        cr.clip()
        blit(cr, cov, x, y, size, size, 0.85 * k)
        cr.restore()
        _frame_plate(cr, x, y, size, c1, k * 0.8)
    glow(cr, W * 0.34 + px(60) * k, H / 2, px(620), c2, 0.20 * k, key='g_sec')
    # title
    tx = px(150)
    text_glow(cr, tx, H * 0.5 - px(46), SONG_TITLE, px(96), (1, 1, 1), 'lc',
              FONT_EN, weight=900, alpha=k, spacing=1.0)
    text_glow(cr, tx, H * 0.5 + px(56), SONG_ZH, px(40), c2, 'lc', FONT_ZH,
              alpha=k * 0.92, spacing=10, halo=0.9)
    # a rule that draws itself under the title
    rw = px(560) * ease_out(clamp01((s.p - 0.25) * 1.8), 2.0)
    cr.save()
    cr.set_line_width(px(2.4))
    cr.set_source_rgba(c2[0], c2[1], c2[2], 0.75)
    cr.move_to(tx, H * 0.5 + px(122))
    cr.line_to(tx + rw, H * 0.5 + px(122))
    cr.stroke()
    cr.restore()
    text_at(cr, tx, H * 0.5 - px(140), 'TRACK 07', px(22), c1, 'lb', FONT_EN,
            alpha=0.55 * k, spacing=5)


def card_artist(cr, s):
    """Fourth card: the artist."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    k = ease_out(clamp01(s.p * 1.5), 2.2)
    # concentric stage rings, like a spotlight seen from above
    for i in range(6):
        rr = px(180 + i * 120) * (0.6 + 0.4 * k)
        ring(cr, W / 2, H * 0.52, rr, c1, 1.4, 0.16 * k, dash=(14, 18),
             a0=s.t * 0.25 + i * 0.6, a1=s.t * 0.25 + i * 0.6 + TAU * 0.8)
    glow(cr, W / 2, H * 0.52, px(620), c1, 0.26 * k, key='g_key')
    text_glow(cr, W / 2, H * 0.52 - px(30), ARTIST, px(190), (1, 1, 1), 'cc',
              FONT_EN, weight=900, alpha=k, spacing=24)
    text_glow(cr, W / 2, H * 0.52 + px(120), '演唱 / 词曲', px(28), c2, 'cc',
              FONT_ZH, alpha=k * 0.85, spacing=8, halo=0.8)
    # artist letterforms echoed faintly around
    for i in range(3):
        off = (px(340) + i * px(90)) * k
        text_at(cr, W / 2 - off, H * 0.52, ARTIST, px(60), c1, 'cc', FONT_EN,
                weight=900, alpha=0.10 * k, spacing=18)
        text_at(cr, W / 2 + off, H * 0.52, ARTIST, px(60), c1, 'cc', FONT_EN,
                weight=900, alpha=0.10 * k, spacing=18)


def card_album(cr, s):
    """Fifth card: the album.  The cover returns, small and precious."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cov = _cover()
    k = ease_out(clamp01(s.p * 1.6), 2.2)
    size = px(240)
    x = W / 2 - size / 2
    y = H * 0.42 - size / 2 - px(30) * (1 - k)
    # vinyl disc sliding out from behind the sleeve
    vx = W / 2 + px(30) + px(190) * ease_out(clamp01((s.p - 0.2) * 1.6), 2.4)
    vy = H * 0.42
    vr = size * 0.62
    cr.save()
    cr.set_source_rgba(shade(c1, 0.25)[0], shade(c1, 0.25)[1], shade(c1, 0.25)[2], 0.9)
    cr.arc(vx, vy, vr, 0, TAU)
    cr.fill()
    cr.restore()
    ring(cr, vx, vy, vr, c1, 2.0, 0.6)
    for i in range(9):
        ring(cr, vx, vy, vr * (0.35 + i * 0.07), c1, 1.0, 0.10)
    cr.save()
    cr.arc(vx, vy, vr * 0.13, 0, TAU)
    cr.set_source_rgba(*c2, 0.85)
    cr.fill()
    cr.restore()
    if cov:
        cr.save()
        cr.rectangle(x, y, size, size)
        cr.clip()
        blit(cr, cov, x, y, size, size, k)
        cr.restore()
    _frame_plate(cr, x, y, size, c2, k, corner=False)
    glow(cr, x, y, px(520), c2, 0.18 * k, key='g_sec')
    text_glow(cr, W / 2, H * 0.42 + px(200), ALBUM, px(76), (1, 1, 1), 'cc',
              FONT_EN, weight=800, alpha=k, spacing=12)
    text_glow(cr, W / 2, H * 0.42 + px(272), '专辑《Miracle Milk》', px(30), c2, 'cc',
              FONT_ZH, alpha=k * 0.9, spacing=8, halo=0.8)
    text_at(cr, W / 2, H * 0.42 + px(346), 'MILI  ·  2016', px(22), c1, 'cc',
            FONT_EN, alpha=0.55 * k, spacing=6)


def card_cover_return(cr, s):
    """Short reprise: the cover, centre, breathing — hands off to the song."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cov = _cover()
    k = ease_out(clamp01(s.p * 2.0), 2.0)
    size = px(470) * (1.0 + 0.02 * s.p)
    x = W / 2 - size / 2
    y = H / 2 - size / 2
    glow(cr, W / 2, H / 2, px(760), c1, 0.30 * k, key='g_key')
    if cov:
        cr.save()
        cr.rectangle(x, y, size, size)
        cr.clip()
        blit(cr, cov, x, y, size, size, k)
        cr.restore()
    _frame_plate(cr, x, y, size, c2, k, corner=False)
    # the plate dissolves into particles toward the end
    if s.p > 0.55:
        for i in range(60):
            a = rnd(41, i) * TAU
            rr = px(300) * smoothstep(0.55, 1.0, s.p) * (0.3 + rnd(41, i + 3))
            dot(cr, W / 2 + math.cos(a) * rr, H / 2 + math.sin(a) * rr,
                px(2.6), c2, 0.5 * (1 - smoothstep(0.55, 1.0, s.p)))


def titlecard(cr, s):
    """End card: the cover centred, title and album, credits."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cov = _cover()
    k = ease_out(clamp01((s.p) * 1.4), 2.0)
    size = px(520)
    x = W / 2 - size / 2
    y = H * 0.46 - size / 2
    glow(cr, W / 2, H * 0.46, px(900), c1, 0.34 * k, key='g_key')
    # fine particle drift
    dot_field(cr, c2, s.t, 5, 90, 0.22, 0.3, 1.4)
    if cov:
        cr.save()
        cr.rectangle(x, y, size, size)
        cr.clip()
        blit(cr, cov, x, y, size, size, k)
        cr.restore()
    _frame_plate(cr, x, y, size, c2, k)
    text_glow(cr, W / 2, y + size + px(96), SONG_TITLE, px(80), (1, 1, 1), 'ct',
              FONT_EN, weight=900, alpha=k, spacing=2)
    text_glow(cr, W / 2, y + size + px(186), SONG_ZH, px(34), c2, 'ct', FONT_ZH,
              alpha=k * 0.9, spacing=12, halo=0.9)
    text_at(cr, W / 2, y + size + px(248), '%s   ·   %s' % (ARTIST, ALBUM),
            px(26), c1, 'ct', FONT_EN, alpha=0.7 * k, spacing=8)
    vignette(cr, 0.6)
