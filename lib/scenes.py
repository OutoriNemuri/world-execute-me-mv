"""scenes — the lyric timeline and the shot table.

Every sung line becomes at least one shot; several lines are split so that a
single line gets one shot per clause (the "one shot per storyboard" rule).
"""
import json, os, re, math

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LRC = os.path.join(BASE, 'lyrics.word.lrc')

# ---------------------------------------------------------------- palette --

def _h(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


STYLE = {
    'void':   dict(bg0=_h('05070c'), bg1=_h('121b2b'), key=_h('5f88ff'),
                   sec=_h('2fd8c8'), accent=_h('ebf2ff')),
    'boot':   dict(bg0=_h('070a10'), bg1=_h('16202f'), key=_h('7fa6ff'),
                   sec=_h('39d6b0'), accent=_h('ffffff')),
    'math':   dict(bg0=_h('050a16'), bg1=_h('14264a'), key=_h('83b4ff'),
                   sec=_h('9fe8ff'), accent=_h('ffffff')),
    'elec':   dict(bg0=_h('160709'), bg1=_h('3a1020'), key=_h('ff9a4d'),
                   sec=_h('ffe27a'), accent=_h('fff2e0')),
    'dizzy':  dict(bg0=_h('1a0620'), bg1=_h('4a1246'), key=_h('ff6ec7'),
                   sec=_h('8f7cff'), accent=_h('ffe9fb')),
    'life':   dict(bg0=_h('04120b'), bg1=_h('123a22'), key=_h('6ce69a'),
                   sec=_h('e8ff8a'), accent=_h('f2fff5')),
    'deity':  dict(bg0=_h('0b0714'), bg1=_h('2a1840'), key=_h('f0c96a'),
                   sec=_h('c9a2ff'), accent=_h('fffaf0')),
    'trance': dict(bg0=_h('0a0620'), bg1=_h('231250'), key=_h('b07bff'),
                   sec=_h('63e0ff'), accent=_h('f6f0ff')),
    'grief':  dict(bg0=_h('02040a'), bg1=_h('0b1526'), key=_h('7d9bc9'),
                   sec=_h('3d5c86'), accent=_h('e9eefb')),
    'rage':   dict(bg0=_h('0c0206'), bg1=_h('380a12'), key=_h('ff4b5c'),
                   sec=_h('ffb03a'), accent=_h('fff0f0')),
    'trap':   dict(bg0=_h('0a0407'), bg1=_h('2a0d16'), key=_h('ff5470'),
                   sec=_h('8a2b3d'), accent=_h('ffe8ec')),
    'love':   dict(bg0=_h('120416'), bg1=_h('4a0f3a'), key=_h('ff7ad0'),
                   sec=_h('ffd27a'), accent=_h('fff2fa')),
    'title':  dict(bg0=_h('03050a'), bg1=_h('101a2e'), key=_h('bcd6ff'),
                   sec=_h('8fb4ff'), accent=_h('ffffff')),
}

MOVEMENT_KEY = 'void boot math elec dizzy life deity trance grief rage trap love'.split()


# ------------------------------------------------------------- LRC parser --

_WORD = re.compile(r'<(\d+):(\d+(?:\.\d+)?)>([^<]*)')
_STAMP = re.compile(r'^\[(\d+):(\d+(?:\.\d+)?)\](.*)$')


def parse_lrc(path=None):
    """-> list of {start, end, text, words:[(t, w)]}"""
    path = path or LRC
    raw = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        m = _STAMP.match(line)
        if not m:
            continue
        t = int(m.group(1)) * 60 + float(m.group(2))
        words = [(int(w.group(1)) * 60 + float(w.group(2)), w.group(3))
                 for w in _WORD.finditer(m.group(3))]
        raw.append((t, words))
    out = []
    for i, (t, words) in enumerate(raw):
        text = ' '.join(w[1] for w in words).strip()
        end = raw[i + 1][0] if i + 1 < len(raw) else t + 3.2
        out.append(dict(start=t, end=end, text=text, words=words))
    return out


# ----------------------------------------------------------- timeline ------

# (line index in the LRC, split point in seconds or None, scene, shot)
# shot=None means "auto": the movement's generic shot for that index.
PLAN = [
    # ---- A. Boot sequence -------------------------------------------------
    #  idx  split   scene    shot
    (0,  None, 'boot',  'cold_open'),
    (1,  None, 'boot',  'breaker'),
    (2,  None, 'boot',  'cad_parts'),
    (3,  6.49, 'boot',  'assemble'),
    (3,  6.97, 'boot',  'assemble2'),
    (4,  None, 'boot',  'patchbay'),
    (5,  None, 'boot',  'init'),
    (6,  12.49, 'boot', 'blueprint'),
    (6,  13.08, 'boot', 'blueprint2'),
    (7,  14.19, 'boot', 'ignition'),
    (7,  14.67, 'boot', 'ignition2'),
    # the interlude after "simulation" is the film-style title sequence
    (8,  16.30, 'title', 'card_studio'),
    (8,  19.20, 'title', 'card_cover'),
    (8,  21.40, 'title', 'card_song'),
    (8,  24.90, 'title', 'card_artist'),
    (8,  27.40, 'title', 'card_album'),
    # ---- B. Geometry ------------------------------------------------------
    (9,  None, 'math',  'points'),
    (10, None, 'math',  'cube'),
    (11, None, 'math',  'circle'),
    (12, None, 'math',  'circumf'),
    (13, None, 'math',  'sine'),
    (14, None, 'math',  'tangent'),
    (15, None, 'math',  'infinity'),
    (16, None, 'math',  'limits'),
    # ---- C. Electric ------------------------------------------------------
    (17, None, 'elec',  'current'),
    (18, 46.48, 'elec', 'switch_ac'),
    (18, 47.12, 'elec', 'switch_dc'),
    (19, None, 'elec',  'blind'),
    (20, None, 'dizzy', 'spin'),
    (21, None, 'dizzy', 'travel'),
    (22, 53.79, 'elec', 'ad'),
    (22, 54.52, 'elec', 'bc'),
    (23, None, 'elec',  'unite'),
    (24, 57.54, 'elec', 'deep1'),
    (24, 58.20, 'elec', 'deep2'),
    # ---- D. Declaration ---------------------------------------------------
    (25, 59.79, 'grief', 'if_i_can'),
    (25, 60.18, 'grief', 'if_i_can2'),
    (26, None, 'grief',  'simulations'),
    (27, 63.50, 'trance', 'then_i_can'),
    (27, 63.94, 'trance', 'then_i_can2'),
    (28, None, 'trance', 'satisfaction'),
    (29, None, 'love',   'make_happy'),
    (30, None, 'boot',   'execution_run'),
    (31, None, 'trap',   'trapped'),
    (32, 72.19, 'trap',  'trapped2'),
    (33, None, 'life',   'eggplant'),
    (34, None, 'life',   'nutrients'),
    (35, None, 'life',   'tomato'),
    (36, None, 'life',   'antioxidants'),
    (37, None, 'life',   'tabby'),
    (38, None, 'deity',  'purr'),
    (39, None, 'deity',  'only_god'),
    (40, None, 'deity',  'proof'),
    # ---- E. Swap ----------------------------------------------------------
    (41, None, 'elec',   'gender'),
    (42, 90.73, 'elec',  'to_f'),
    (42, 91.48, 'elec',  'to_m'),
    (43, None, 'dizzy',  'whatever'),
    (44, None, 'dizzy',  'am_pm'),
    (45, None, 'dizzy',  'switch_role'),
    (46, 98.13, 'trance', 'to_s'),
    (46, 98.93, 'trance', 'to_m2'),
    (47, None, 'trance', 'enter'),
    (48, 101.83, 'trance', 'trance1'),
    (48, 102.50, 'trance', 'trance2'),
    # ---- F. Collapse ------------------------------------------------------
    (49, 104.18, 'grief', 'if_i_can3'),
    (49, 104.62, 'grief', 'if_i_can4'),
    (50, None, 'love',    'vibrations'),
    (51, 107.83, 'love',  'then2'),
    (51, 108.30, 'love',  'then3'),
    (52, None, 'deity',   'completion'),
    (53, None, 'grief',   'you_left'),
    (54, None, 'grief',   'left2'),
    (55, None, 'grief',   'left3'),
    (56, None, 'grief',   'left4'),
    (57, None, 'grief',   'left5'),
    (58, 117.00, 'grief',   'isolation'),
    # ---- G. Debug ---------------------------------------------------------
    (58, None, 'rage',    'if_can5'),
    (59, None, 'rage',    'fragments'),
    (60, 122.58, 'rage',  'maybe1'),
    (60, 123.04, 'rage',  'maybe2'),
    (61, None, 'rage',    'disheartened'),
    (62, None, 'rage',    'challenging'),
    (63, None, 'rage',    'made_some'),
    (64, 131.50, 'rage',  'illegal'),
    (65, 132.40, 'rage',  'solo1'),
    (65, 133.30, 'rage',  'solo2'),
    # ---- H. Execution -----------------------------------------------------
    (66, 148.05, 'boot', 'exec_tick'),
    (67, 148.89, 'boot', 'exec_tick'),
    (68, 149.85, 'boot', 'exec_tick'),
    (69, 150.74, 'boot', 'exec_tick'),
    (70, 151.69, 'boot', 'exec_tick'),
    (71, 152.57, 'boot', 'exec_tick'),
    (72, 153.53, 'boot', 'exec_tick'),
    (73, 154.43, 'boot', 'exec_tick'),
    (74, 155.35, 'boot', 'exec_tick'),
    (75, 156.25, 'boot', 'exec_tick'),
    (76, 157.20, 'boot', 'exec_tick'),
    (77, 158.15, 'boot', 'exec_tick'),
    # ---- I. Countdown -----------------------------------------------------
    (78, 159.03, 'love', 'count_es'),      # Execution
    (79, 160.08, 'love', 'count_dos'),     # Ein, dos
    (80, 161.00, 'love', 'count_tres'),    # Trios, ne
    (81, 161.93, 'love', 'count_ne'),      # Fem, liu
    (82, 162.76, 'love', 'count_fem'),     # Execution
    (83, 163.90, 'love', 'count_liu'),     # If I can, if I can
    (84, 165.00, 'boot', 'exec_one'),      # Give them all the execution
    (85, 166.40, 'boot', 'exec_one2'),     # Then I can, then I can
    # ---- J. Finale --------------------------------------------------------
    (86, 167.60, 'love',  'final_if'),       # Be your only execution
    (87, 170.05, 'love',  'final_exec'),     # If I can have you back
    (88, 172.01, 'love',  'final_then'),     # I will run the execution
    (89, 173.71, 'grief', 'have_you_back'),  # Though we are trapped
    (90, 175.20, 'grief', 'run_exec'),       # We are trapped, ah
    (91, 177.66, 'trap',  'still_trapped'),  # I've studied, I've studied
    (92, 179.31, 'trap',  'we_trapped'),     # How to properly lo-o-ove
    # ---- K. Love ----------------------------------------------------------
    (93, 181.12, 'love',  'studied'),        # Question me, question me
    (94, 183.00, 'love',  'properly'),       # I can answer all lo-o-ove
    (95, 184.95, 'love',  'question'),       # I know the algebraic expression
    (96, 188.53, 'love',  'answer_love'),    # Though you are free
    (97, 189.98, 'love',  'algebraic'),      # I am trapped
    (98, 190.93, 'love',  'you_free'),       # Trapped in lo-o-ove
    (99, 193.46, 'love',  'outro'),
]


def build_timeline():
    lines = parse_lrc()
    sched = []
    for i, (li, split, scene, shot) in enumerate(PLAN):
        line = lines[li] if li >= 0 else dict(start=0, end=0, text='', words=[])
        if split is None:
            t0 = line['start'] if li >= 0 else None
            t1 = line['end'] if li >= 0 else None
        else:
            t0, t1 = split, None
        sched.append(dict(line=line, li=li, t0=t0, t1=t1, scene=scene, shot=shot))

    # resolve the split boundaries
    for i, s in enumerate(sched):
        if s['t0'] is None:
            continue
        if s['t1'] is None:
            nxt = None
            for j in range(i + 1, len(sched)):
                if sched[j]['t0'] is not None:
                    nxt = sched[j]['t0']
                    break
            s['t1'] = nxt if nxt is not None else s['t0'] + 2.5
    # the placeholder line above
    # blank / interlude shots spanning the gaps
    ins = []
    bystart = sorted(sched + ins, key=lambda s: s['t0'])

    gaps = [
        (29.40, 29.82, 'title', 'card_cover_return'),
        (134.88, 148.0, 'rage', 'gap_void'),
        (193.96, 208.4, 'boot', 'gap_after'),
        (208.4, 216.0, 'title', 'titlecard'),
    ]
    for t0, t1, sc, sh in gaps:
        bystart.append(dict(line=dict(start=t0, end=t1, text='', words=[]),
                            li=-1, t0=t0, t1=t1, scene=sc, shot=sh))
    bystart.sort(key=lambda s: s['t0'])

    out = []
    for i, s in enumerate(bystart):
        # close every shot at the next start so coverage is gapless
        if i + 1 < len(bystart):
            s['t1'] = bystart[i + 1]['t0']
        s['idx'] = i
        s['style'] = STYLE[s['scene']]
        out.append(s)
    return out, lines


def shot_style(scene):
    return STYLE[scene]
