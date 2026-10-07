#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_gha — CI entry point.

Renders every frame at 1920x1080 @ 30fps and streams raw BGRA straight into
ffmpeg's stdin, then muxes the original audio back in.

CRITICAL: stdout belongs to ffmpeg.  Every message goes to stderr.  A stray
print() injects bytes mid-row, which wraps the picture horizontally and shifts
the BGRA channels — it looks like a rendering bug but it is I/O pollution.
"""
import os, sys, time, subprocess, argparse, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'lib'))

import cairo  # noqa: E402
import render_lib  # noqa: E402
import mv_frame  # noqa: E402


def log(msg):
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out', help='output mp4 path')
    ap.add_argument('--fps', type=int, default=render_lib.FPS)
    ap.add_argument('--duration', type=float, default=render_lib.SONG_END)
    ap.add_argument('--start', type=float, default=0.0)
    ap.add_argument('--crf', type=int, default=17)
    ap.add_argument('--preset', default='medium')
    ap.add_argument('--audio', default=os.path.join(ROOT, 'assets',
                                                    'mili-world.execute-me.mp3'))
    ap.add_argument('--preview', action='store_true',
                    help='render 12s from 0:15 instead of the whole track')
    ap.add_argument('--frames-dir', default=None,
                    help='write PNG frames instead of encoding (debug)')
    ap.add_argument('--workers', type=int, default=0,
                    help='parallel render processes (0 = cpu count)')
    args = ap.parse_args()

    if args.preview:
        args.start, args.duration = 14.0, 12.0

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or '.', exist_ok=True)

    w, h, fps = render_lib.W, render_lib.H, args.fps
    n_total = int(round(args.duration * fps))
    log('render  %dx%d @ %dfps  %.2fs -> %d frames' % (w, h, fps, args.duration, n_total))

    # cover art for the title cards
    cov = os.path.join(ROOT, 'assets', 'cover_art.png')
    if os.path.exists(cov):
        import shots_title
        shots_title.load_cover(cov)
        log('cover   loaded %s' % cov)
    else:
        log('cover   MISSING %s' % cov)

    # font sanity: a silent font problem becomes tofu in the video
    try:
        import subprocess as sp
        for f in ('Inter', 'Source Han Sans CN'):
            r = sp.run(['fc-match', f], capture_output=True, text=True)
            log('font    %-18s -> %s' % (f, r.stdout.strip()))
    except Exception as e:
        log('font    check skipped: %s' % e)

    n_workers = args.workers or max(1, (os.cpu_count() or 2))
    log('workers %d' % n_workers)

    if args.frames_dir:
        surf = mv_frame.make_surface()
        cr = cairo.Context(surf)
        os.makedirs(args.frames_dir, exist_ok=True)
        for i in range(n_total):
            t = args.start + i / float(fps)
            mv_frame.render(cr, t)
            surf.write_to_png(os.path.join(args.frames_dir, 'f%06d.png' % i))
            if i % 30 == 0:
                log('  frame %5d / %d' % (i, n_total))
        log('done -> %s' % args.frames_dir)
        return

    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'rawvideo', '-pix_fmt', 'bgra',
        '-s', '%dx%d' % (w, h), '-r', str(fps),
        '-i', 'pipe:0',
        '-itsoffset', '%f' % args.start,
        '-i', args.audio,
        '-map', '0:v:0', '-map', '1:a:0',
        '-c:v', 'libx264', '-preset', args.preset, '-crf', str(args.crf),
        '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
        '-movflags', '+faststart',
        '-c:a', 'aac', '-b:a', '320k',
        '-shortest',
        args.out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    # Workers render frames into per-process temp files; the parent concatenates
    # them into the encoder in order.  A chunk is small enough that memory stays
    # flat regardless of how long the video is.
    chunk = 60                       # frames per temp file (~5.7 MB)
    tmp = tempfile.mkdtemp(prefix='wem-frames-')
    t_start = time.time()
    try:
        if n_workers == 1:
            surf = mv_frame.make_surface()
            cr = cairo.Context(surf)
            for i in range(n_total):
                t = args.start + i / float(fps)
                mv_frame.render(cr, t)
                surf.flush()
                proc.stdin.write(surf.get_data())
                if i % 30 == 0:
                    el = time.time() - t_start
                    log('  frame %5d / %d   %.1fs   eta %.0fs'
                        % (i, n_total, el, (el / max(1, i)) * (n_total - i) if i else 0))
        else:
            _render_parallel(args, fps, n_total, chunk, tmp, proc, log, t_start)
    except BrokenPipeError:
        log('ffmpeg closed the pipe early')
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass

    err = proc.stderr.read().decode('utf-8', 'replace')
    rc = proc.wait()
    if err.strip():
        log(err.strip()[-4000:])
    shutil.rmtree(tmp, ignore_errors=True)
    if rc != 0:
        log('ffmpeg exited %d' % rc)
        sys.exit(rc)

    log('wrote %s (%.1f MB) in %.0fs'
        % (args.out, os.path.getsize(args.out) / 1e6, time.time() - t_start))


def _render_worker(job):
    """Render frames [a, b) and write raw BGRA to path."""
    path, a, b, start, fps = job
    import cairo as _c
    import mv_frame as _m
    surf = _m.make_surface()
    cr = _c.Context(surf)
    with open(path, 'wb') as f:
        for i in range(a, b):
            t = start + i / float(fps)
            _m.render(cr, t)
            surf.flush()
            f.write(surf.get_data())
    return len(range(a, b))


def _render_parallel(args, fps, n_total, chunk, tmp, proc, log, t_start):
    import multiprocessing as mp
    n_workers = args.workers or max(1, (os.cpu_count() or 2))

    jobs = []
    for a in range(0, n_total, chunk):
        b = min(n_total, a + chunk)
        jobs.append((os.path.join(tmp, 'p%06d.raw' % a), a, b, args.start, fps))

    written = 0
    done_chunks = 0
    with mp.Pool(n_workers, initializer=_init_worker, initargs=(ROOT,)) as pool:
        # imap preserves order, so chunks stream to ffmpeg in the right sequence
        for (path, a, b, _s, _f), n in zip(jobs, pool.imap(_render_worker, jobs)):
            with open(path, 'rb') as f:
                shutil.copyfileobj(f, proc.stdin, 1 << 20)
            os.remove(path)
            written += n
            done_chunks += 1
            if done_chunks % 5 == 0 or written >= n_total:
                el = time.time() - t_start
                log('  frame %5d / %d   %.1fs   eta %.0fs'
                    % (written, n_total, el,
                       (el / max(1, written)) * (n_total - written)))


def _init_worker(root):
    sys.path.insert(0, os.path.join(root, 'lib'))
    cov = os.path.join(root, 'assets', 'cover_art.png')
    try:
        import shots_title
        if os.path.exists(cov):
            shots_title.load_cover(cov)
    except Exception:
        pass


