# -*- coding: utf-8 -*-
"""mv_frame — the compositor.

For a given time t it: picks the shot, paints the scene background, runs the
shot's draw function, then draws the lyric band (English + the sung word
highlighted + Chinese translation) and the HUD.

Draw order matters: the lyrics are an *overlay*, the picture is the subject.
"""
import math
import cairo
from render_lib import (W, H, TAU, px, mix, shade, clamp01, smoothstep, ease_out,
                        ease_in, ease_io, pulse, text_at, text_glow, grad_rect,
                        dashed_line, dot, ring, glow, bg_gradient, vignette,
                        scanlines, noise, blit, ShotClock, FONT_EN, FONT_ZH,
                        text_w, cached)
from scene_paint import rnd
import scenes

ZONE = None
_LINE_INDEX = {}


def _h(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def load_timeline():
    """Build (and cache) the shot table."""
    global ZONE, _LINE_INDEX
    if ZONE is None:
        ZONE, lines = scenes.build_timeline()
        ZONE.sort(key=lambda s: s['t0'])
        for s in ZONE:
            s['idx'] = ZONE.index(s) if False else s['idx']
        # assign a stable per-shot index for seeded variation
        for i, s in enumerate(ZONE):
            s['uid'] = i
        # group the twelve identical "exec_tick" shots so the shot can vary
        tick = 0
        for s in ZONE:
            if s['shot'] == 'exec_tick':
                s['tick'] = tick
                tick += 1
            else:
                s['tick'] = 0
        for s in ZONE:
            s['dur'] = max(0.001, s['t1'] - s['t0'])
    return ZONE


def shot_at(t):
    tbl = load_timeline()
    lo, hi = 0, len(tbl) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if tbl[mid]['t0'] <= t:
            lo = mid
        else:
            hi = mid - 1
    s = tbl[lo]
    if t >= s['t1'] and lo + 1 < len(tbl):
        s = tbl[lo + 1]
    return s


class Ctx:
    """Everything a shot needs that is not (cr, shot)."""

    def __init__(self, t):
        self.song = None
        self.style = None
        self._cache = {}
        self.lyric = None
        self.word_progress = 0.0
        self.hud = True

    def g(self, key, seed, lo, hi):
        """Deterministic slow value for a shot, so motion is smooth, not jittery."""
        k = '%s_%d' % (key, seed)
        if k not in self._cache:
            self._cache[k] = lo + (hi - lo) * rnd(seed, len(self._cache) + 1)
        return self._cache[k] if isinstance(self._cache[k], (list, tuple)) else \
            (self._cache[k], self._cache[k])


def _shot_module(name):
    """Resolve and import the module that owns a shot."""
    import importlib
    groups = ('shots_boot', 'shots_title', 'shots_math', 'shots_elec',
              'shots_life', 'shots_trance', 'shots_grief', 'shots_love',
              'shots_final')
    for g in groups:
        m = importlib.import_module(g)
        if hasattr(m, name):
            return m
    return None


_MODULE_CACHE = {}


def find_draw(name):
    if name in _MODULE_CACHE:
        return _MODULE_CACHE[name]
    m = _shot_module(name)
    fn = getattr(m, name, None) if m else None
    _MODULE_CACHE[name] = fn
    return fn


class ShotCtx:
    def __init__(self, t, shot):
        self.song = shot['style']
        self.style = shot['style']
        self.tick = shot.get('tick', 0)
        self.uid = shot.get('uid', 0)
        self._vals = {}

    def g(self, key, seed, lo, hi):
        """A stable pair of values for a shot, so camera motion is smooth."""
        k = '%s_%s' % (key, seed)
        if k not in self._vals:
            self._vals[k] = (lo + (hi - lo) * rnd(seed, len(self._vals) + 1),
                             lo + (hi - lo) * rnd(seed + 991, len(self._vals) + 3))
        return self._vals[k]


def render(cr, t):
    """Paint the complete frame for time t into cr."""
    tbl = load_timeline()
    sh = shot_at(t)

    style = sh['style']
    c1, c2 = style['key'], style['sec']
    bg0, bg1 = style['bg0'], style['bg1']

    # ---- background ------------------------------------------------------
    bg_gradient(cr, bg0, bg1, 0.5, 0.45, 1.30,
                key=('bg', bg0, bg1, sh['scene']))

    ctx = ShotCtx(t, sh)
    clock = ShotClock(t, sh['t0'], sh['t1'], sh.get('uid', 0), sh['line'], ctx)

    fn = find_draw(sh['shot'])
    if fn is not None:
        cr.save()
        fn(cr, clock)
        cr.restore()

    # ---- lyric overlay ---------------------------------------------------
    draw_lyric(cr, t, sh, style)

    # ---- HUD -------------------------------------------------------------
    if sh['scene'] not in ('title',):
        draw_hud(cr, t, sh, style)

    # ---- finishing -------------------------------------------------------
    vignette(cr, 0.50)
    scanlines(cr, 0.030, 3)


# ------------------------------------------------------------------ lyric ---

def _line_state(t, sh):
    """Which lyric line is live at t, and how far through its words we are."""
    line = sh['line']
    if not line['words']:
        return None, None, 0.0
    return line, sh, 0.0


def draw_lyric(cr, t, sh, style):
    """English line with the sung word lit, Chinese beneath."""
    line = sh['line']
    if not line['words']:
        return
    words = line['words']
    if not words:
        return

    # which shot is live for this line? (a line may own several shots)
    tbl = load_timeline()
    sibs = [s for s in tbl if s['li'] == sh['li'] and s['t0'] is not None]
    sibs.sort(key=lambda s: s['t0'])
    # words belonging to this shot's slice
    lo_t, hi_t = sh['t0'], sh['t1']
    mine = [(wt, w) for wt, w in words if wt >= lo_t - 0.35 and wt < hi_t]
    if not mine:
        mine = words

    text = line['text']
    size = px(50)
    if len(text) > 34:
        size = px(40)
    if len(text) > 44:
        size = px(34)
    spacing = 1.0

    # which word is currently being sung
    active = -1
    for i, (wt, w) in enumerate(mine):
        if t >= wt:
            active = i
        else:
            break
    # per-word progress for the highlight sweep
    if active >= 0:
        wt = mine[active][0]
        nxt = mine[active + 1][0] if active + 1 < len(mine) else sh['t1']
        wp = clamp01((t - wt) / max(0.05, nxt - wt))
    else:
        wp = 0.0

    # the line and the translation
    zh = ''
    try:
        import subtitles
        zh = subtitles.zh_for(text)
    except Exception:
        zh = ''

    tx = px(150)
    bx = px(150)
    by = H - px(150)
    # the whole band appears quickly and fades gently
    appear = smoothstep(lo_t, lo_t + 0.22, t)
    fade = 1.0 - smoothstep(sh['t1'] - 0.10, sh['t1'] + 0.18, t)
    band = clamp01(appear) * clamp01(fade)
    if band <= 0.01:
        return

    # right-aligned chinese on the same baseline
    tw = text_w(text, size, FONT_EN, 800, spacing)
    cr.save()
    cr.translate(0, px(14) * (1 - smoothstep(lo_t, lo_t + 0.4, t)))
    # english, word by word
    x = bx
    for i, (wt, w) in enumerate(mine):
        lit = i < active
        cur = i == active
        ww = text_w(w + ' ', size, FONT_EN, 800, spacing)
        col = (1, 1, 1) if not lit else mix((0.72, 0.80, 0.95), (1, 1, 1), 1)
        if cur:
            # the singing word glows in the scene's secondary colour
            col = c2_of(style)
            alpha = 1.0
        elif lit:
            col = (0.88, 0.92, 1.0)
            alpha = 0.92
        else:
            col = (0.62, 0.68, 0.82)
            alpha = 0.72
        text_glow(cr, x, by, w, size, col, 'la', FONT_EN,
                  alpha=alpha * band, spacing=spacing, halo=0.75, shadow=True)
        if cur:
            # underline sweep on the current word
            uw = text_w(w, size, FONT_EN, 800, spacing)
            cr.save()
            cr.set_line_width(px(4))
            cr.set_source_rgba(col[0], col[1], col[2], 0.9 * band)
            cr.move_to(x, by + px(12))
            cr.line_to(x + uw * wp, by + px(12))
            cr.stroke()
            cr.restore()
        x += ww
    # chinese line
    if zh:
        text_glow(cr, bx, by + px(74), zh, px(32), c2_of(style), 'la', FONT_ZH,
                  alpha=0.80 * band, spacing=5, halo=0.8, shadow=True)
    cr.restore()


def c2_of(style):
    return style['sec']


# -------------------------------------------------------------------- HUD ---

def draw_hud(cr, t, sh, style):
    c1, c2 = style['key'], style['sec']
    # corner brackets
    m, L = px(42), px(46)
    cr.save()
    cr.set_line_width(px(2.0))
    cr.set_source_rgba(c1[0], c1[1], c1[2], 0.28)
    for x, y, sx, sy in ((m, m, 1, 1), (W - m, m, -1, 1),
                         (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        cr.move_to(x, y + L * sy)
        cr.line_to(x, y)
        cr.line_to(x + L * sx, y)
    cr.stroke()
    cr.restore()

    # a slim progress hairline along the bottom
    total = 216.0
    pr = clamp01(t / total)
    cr.save()
    cr.set_line_width(px(2))
    cr.set_source_rgba(c1[0], c1[1], c1[2], 0.16)
    cr.move_to(0, H - px(2))
    cr.line_to(W, H - px(2))
    cr.stroke()
    cr.set_source_rgba(c2[0], c2[1], c2[2], 0.55)
    cr.move_to(0, H - px(2))
    cr.line_to(W * pr, H - px(2))
    cr.stroke()
    cr.restore()

    # shot slug, top-left, technical and small
    slug = sh['shot'].upper().replace('_', ' ')
    text_at(cr, m + px(14), m + px(10), slug, px(18), c1, 'lt', FONT_EN,
            alpha=0.30, spacing=3.0)
    text_at(cr, W - m - px(14), m + px(10), '%02d:%05.2f' % (int(t // 60), t % 60),
            px(18), c1, 'rt', FONT_EN, alpha=0.30, spacing=1.5)


# --------------------------------------------------------------- frame i/o --

def frame_bytes(cr, surf, t):
    """Render time t and return the raw BGRA bytes for the encoder."""
    render(cr, t)
    surf.flush()
    return surf.get_data()


def make_surface():
    return cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
