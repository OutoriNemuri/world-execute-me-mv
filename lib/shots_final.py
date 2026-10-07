

def enter(cr, s):
    """So we can enter — a threshold crossed."""
    st = s.ctx.song
    c1, c2 = st['key'], st['sec']
    cx, cy = W / 2, H * 0.5
    k = ease_out(clamp01(s.p * 1.2), 1.8)
    # a doorway of light widening
    w = px(90) + px(520) * k
    h = px(340) + px(420) * k
    grad_rect(cr, cx - w / 2, cy - h / 2, w, h, c2, c1, True, 0.22)
    cr.save()
    cr.set_line_width(px(3.4))
    cr.set_source_rgba(*c2, 0.85)
    cr.rectangle(cx - w / 2, cy - h / 2, w, h)
    cr.stroke()
    cr.restore()
    glow(cr, cx, cy, px(560) * k, c2, 0.34 * k, key='g_sec')
    # someone walking through: a silhouette that shrinks into the door
    u = ease_io(k)
    sx = cx - px(420) + (cx - px(420) - (cx - px(420))) * 0  # anchor
    px_ = px(300) + (cx - px(300)) * u
    sc = 1.0 - 0.45 * u
    dot(cr, px_, cy + px(60) * sc, px(26) * sc, shade(c1, 0.45), 0.9)
    poly(cr, [(px_ - px(34) * sc, cy + px(200) * sc),
              (px_ - px(20) * sc, cy + px(20) * sc),
              (px_ + px(20) * sc, cy + px(20) * sc),
              (px_ + px(34) * sc, cy + px(200) * sc)],
         shade(c1, 0.45), 0.9, 3.0)
    for i in range(5):
        ring(cr, cx, cy, px(200 + i * 130) * (0.5 + k), c2, 1.6, 0.25 * k, dash=(12, 16))
