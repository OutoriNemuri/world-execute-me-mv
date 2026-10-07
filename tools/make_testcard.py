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

# one frame from each movement, plus every title card
SAMPLES = [
    1.0, 3.0, 6.5, 8.0, 11.0, 13.5,
    16.8, 20.2, 22.6, 25.6, 28.4,
    30.5, 34.5, 38.0, 40.2, 43.5,
    45.5, 47.5, 50.5, 52.5, 56.5, 58.5,
    61.5, 65.0, 69.0, 71.5, 74.0,
    76.0, 78.5, 81.0, 84.0, 86.0,
    89.5, 92.5, 95.0, 98.5, 101.0, 103.0,
    107.0, 110.0, 113.0, 116.5, 119.0,
    123.0, 127.0, 130.0, 133.0,
    149.0, 157.0, 160.0, 164.0, 168.0, 172.0, 176.0,
    182.0, 186.0, 189.0, 192.0, 210.0,
]


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
    for t in SAMPLES:
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
