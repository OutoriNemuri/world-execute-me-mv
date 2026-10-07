#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_testcard — render a grid of sample frames for a fast visual check.

This exists so a font / colour / geometry mistake is caught in ~40s on CI
instead of 7 minutes into a full render.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'lib'))

import cairo  # noqa: E402
from PIL import Image  # noqa: E402
import render_lib  # noqa: E402
import mv_frame  # noqa: E402

def sample_times():
    """One frame from the middle of EVERY shot, so a broken shot is caught
    here rather than 7 minutes into the full render."""
    import mv_frame
    tbl = mv_frame.load_timeline()
    ts = []
    for sh in tbl:
        mid = (sh['t0'] + sh['t1']) * 0.5
        ts.append(round(mid, 3))
    return ts


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else 'out/testcard'
    os.makedirs(outdir, exist_ok=True)

    cov = os.path.join(ROOT, 'assets', 'cover_art.png')
    if os.path.exists(cov):
        import shots_title
        shots_title.load_cover(cov)

    surf = mv_frame.make_surface()
    cr = cairo.Context(surf)

    tiles = []
    for t in sample_times():
        mv_frame.render(cr, t)
        surf.flush()
        im = Image.frombuffer('RGBA', (render_lib.W, render_lib.H),
                              surf.get_data(), 'raw', 'BGRA', 0, 1)
        tiles.append((t, im.convert('RGB').resize((480, 270), Image.LANCZOS)))
        im.close()

    cols = 5
    rows = (len(tiles) + cols - 1) // cols
    tw, th = 480, 270
    sheet = Image.new('RGB', (cols * tw, rows * th + rows * 22), (10, 10, 14))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(tiles):
        c, r = i % cols, i // cols
        sheet.paste(im, (c * tw, r * (th + 22)))
        d.text((c * tw + 6, r * (th + 22) + th + 4), '%06.2fs' % t, fill=(150, 160, 180))
        im.save(os.path.join(outdir, 'frame_%07.2f.png' % t))

    sheet.save(os.path.join(outdir, 'sheet.jpg'), quality=88)
    sys.stderr.write('testcard: %d tiles -> %s/sheet.jpg\n' % (len(tiles), outdir))


if __name__ == '__main__':
    main()
