# world.execute(me); — MV

A fully code-generated music video for **MILI — world.execute(me);** (from *Miracle Milk*).

Nothing is filmed. Every frame is drawn from scratch with **cairo + Pango** and piped
straight into **ffmpeg**; the song is muxed back in at the end.

| | |
|---|---|
| Resolution | 1920×1080 |
| Frame rate | 30 fps |
| Duration | ≈ 211 s (full track) |
| Shots | 124 (one or more per lyric line) |
| Renderer | Python 3 · pycairo · Pango · Pillow |
| Encoder | ffmpeg / libx264 / yuv420p / AAC 320k |
| Render host | GitHub Actions (ubuntu-latest) |

## The idea

The song is a program that falls in love. It opens like a build log, turns into a
plea to be *something* — a set of points, a circle, a sine wave, an eggplant, a
tabby cat, a god — and ends debugging a trapped loop.

So the video is drawn as **a machine running the program**:

* the whole screen is a coordinate field, and every object is constructed out of
  it — hex grids, wireframes, phase-space streams, PCB traces, waveform scopes;
* the palette climbs from cold engineering blue (the build) through biological
  green (the vegetable cat) into violet (the romance) and finally ash grey (the
  trap);
* the lyrics are rendered as *specimens* — engraved specimen plates, terminal
  read-outs, burned-in phosphor — never as a karaoke bar;
* every object the song names is actually drawn: the point cloud, the circle and
  its circumference, the tangent line on a sine wave, the asymptote, AC/DC, the
  eggplant, the tomato, the tabby cat, the heart.

## Layout

```
lib/
  render_lib.py     canvas / gradient / text / caching primitives
  scene_paint.py    drawing primitives: rings, hex grids, waveforms, PCB, particles
  scenes.py         lyric-line → (scene, shot) timeline + palettes
  shots_*.py        the 124 shot functions, grouped by movement
  subtitles.py      Chinese translations, keyed by line
  mv_frame.py       the compositor: background → shot → lyrics → HUD
  testcards.py      still-frame sheet for a fast visual sanity check
tools/
  render_gha.py     CI entry point: streams BGRA to ffmpeg, muxes audio
  make_testcard.py  renders a grid of sample frames
```

## Render

```bash
# sample stills
python3 tools/make_testcard.py out/

# full video (streams raw frames into ffmpeg, ~7 min on GitHub Actions)
python3 tools/render_gha.py out/world.execute-me.mv.mp4
```

`assets/` holds the source audio; `fonts/` holds Inter and Source Han Sans CN so
the render is identical everywhere.

## Gotchas learned the hard way

1. **stdout is the video pipe.** Progress must go to *stderr*. A stray `print()`
   every 30 frames injects a few bytes mid-row: the picture wraps horizontally
   and the BGRA channels shift, which reads as a mysterious colour bug.
2. **cairo patterns need `EXTEND_PAD`**, or a magnified gradient tiles at the
   canvas edges.
3. **Aspect ratio has to be set per-axis** when blitting a scaled surface;
   one square surface forced into a 16:9 frame leaves the rest of the canvas
   filled with its edge colour.
4. **Pre-render gradients into small surfaces and cache them** — native radial
   gradients over 1080p cost ~300 ms each, and scaling blits cost ~200 ms.
   A cached pattern costs ~1 ms.
5. **Progress text goes to stderr** — see (1). Seriously.
