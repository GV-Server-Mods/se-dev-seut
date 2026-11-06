"""Check a SEUT model against Keen's measured block style (references/keen-style.md).

Measures the model as SEUT exports it (modifiers applied), counts shares on the surface that can be seen (a sample
point is visible when any of 162 ray directions escapes the model), and prints PASS / WARN / INFO per keen-style.md
table row against the vanilla ranges in references/keen-rules.json.

Blender, headless, on a COPY of the .blend (never the file open in Blender):
  blender -b <copy.blend> --python keen_check.py -- [--scene NAME] [--grid large|small] [--era newer|classic]
                                                     [--out DIR] [--name NAME]
  blender -b --python keen_check.py -- --model <file.glb|file.fbx> --grid large [...]   (an exported or vanilla model)
Plain Python, no Blender:
  python keen_check.py --compare DIR/NAME.survey.json [--era classic]    re-print a report from a saved survey
  python keen_check.py --build-rules DIR --meta blocks.json [--rules-out keen-rules.json]
                                                     rebuild the vanilla ranges from surveys of vanilla models

--scene picks the SEUT scene (default: the active one); its "Main (...)" collection is measured, so run once per
subpart scene. --grid defaults to the scene's SEUT grid scale. --era picks the vanilla style to compare with
(default newer). --out writes NAME.survey.json and NAME.report.txt. An .fbx goes through SEUT's FBX2glTF into a
temporary folder, like SEUT's importer; the model is turned 180 degrees about Z, as SEUT does.
"""
import json, math, os, re, sys, time, random
from collections import defaultdict, Counter, deque

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(os.path.dirname(HERE), 'references')
DECAL_PREFIX = ('Atlas', 'ButtonsAtlas', 'Decals', 'Paneling', 'TextAtlas')
LINE_PIECES = {('Atlas4', 3), ('Decals_Atlas_A_01', 51), ('Decals_Atlas_A_01', 54), ('Decals_Atlas_A_01', 58),
               ('Decals_Atlas_A_01', 61)}
BOLT_HEADS = {('Decals_Atlas_A_01', i) for i in range(1, 12)} | {('Atlas3', 14), ('Atlas3', 17)}
SIGN_PLATES = {('Atlas2', i) for i in (6, 13, 15, 17, 18, 30, 31, 37, 52)} | {('Decals_Atlas_A_01', 37)}
SIGN_PICTOS = {('Atlas2', 16), ('Atlas2', 54), ('Decals_Atlas_A_01', 38)}
CODES = {('Atlas2', i) for i in range(41, 52)}


def clean_name(n):
    return re.sub(r'\.\d{3}$', '', n)


def game_name(n):
    """the material SEUT and the game use: Keen's *Scratched* SDK materials map to the clean one"""
    return n.replace('Scratched_', '_').replace('_Scratched', '') if 'Scratched' in n else n


def is_decal(n):
    return n.startswith(DECAL_PREFIX) and n != 'AtlasGlass'


def atlas_of(n):
    for a in ('Atlas1', 'Atlas2', 'Atlas3', 'Atlas4', 'ButtonsAtlas', 'TextAtlas'):
        if n.startswith(a):
            return a
    if n.startswith(('Decals', 'Paneling')):
        return 'Decals_Atlas_A_01'
    return None


def family(m):
    """paint family of a base or decal material"""
    if not m:
        return None
    m = game_name(m)
    if 'Colorable' in m:
        return 'paint'
    if 'VeryDark' in m:
        return 'vdark'
    if 'Darker' in m:
        return 'dark'
    if 'Chrome' in m:
        return 'chrome'
    if 'Yellow' in m:
        return 'yellow'
    if m.startswith(('Metal_', 'MetalMilitary')):
        return 'metal'
    if is_decal(m):
        return 'plain'
    return 'other'


def variant_ok(dmat, hmat):
    """does the decal variant suit its host (keen-style.md, "Decal variant follows the host"); None = no variant"""
    sheet = atlas_of(dmat)
    if sheet in (None, 'Atlas2', 'TextAtlas') or dmat == 'Decals':
        return None
    d, h = family(dmat), family(hmat)
    plain1 = sheet == 'Atlas1' and d == 'plain'
    if h == 'paint':
        return d == 'paint'
    if h == 'dark':
        return d == 'dark' or plain1
    if h == 'vdark':
        return d in ('vdark', 'dark') or plain1
    if h == 'chrome':
        return d == 'chrome' or (sheet == 'ButtonsAtlas' and d == 'dark') or plain1
    if h == 'metal':
        return d in ('chrome', 'dark') or plain1
    return None


def piece_kind(desc):
    d = desc.lower()
    for k, words in (('seam', ('seam', 'groove')), ('weld', ('weld',)), ('rivet_band', ('rivet', 'dimple')),
                     ('bolt', ('bolt', 'screw', 'nut', 'rivet head')),
                     ('sign', ('danger', 'warning', 'hazard', 'voltage', 'sign', 'chevron', 'arrow', 'icon',
                               'sticker', 'logo', 'stripe')),
                     ('text', ('letter', 'digit', 'text', 'word', 'number')),
                     ('button', ('button', 'switch', 'led', 'keypad', 'connector', 'socket', 'knob', 'lamp')),
                     ('vent', ('vent', 'grille', 'slot', 'slat', 'louvre', 'louver', 'mesh')),
                     ('strip', ('strip', 'bar', 'band', 'trim')),
                     ('panel', ('panel', 'plate', 'hatch', 'frame', 'cover', 'lid', 'square', 'disc', 'ring'))):
        if any(w in d for w in words):
            return k
    return 'other'


# ======================================================================================== measures (plain Python)
def quant(xs, p):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    i = int(math.floor(k))
    return xs[i] if i + 1 >= len(xs) else xs[i] + (xs[i + 1] - xs[i]) * (k - i)


def wquant(pairs, p):
    pairs = sorted((x, w) for x, w in pairs if x is not None and w > 0)
    if not pairs:
        return None
    tot = sum(w for _, w in pairs)
    acc = 0.0
    for x, w in pairs:
        acc += w
        if acc >= tot * p:
            return x
    return pairs[-1][0]


def share(flags):
    flags = [f for f in flags if f is not None]
    return sum(1 for f in flags if f) / len(flags) if flags else None


def ratio(a, b):
    return a / b if b else None


def hist_median(groups):
    """area-weighted median UV/m from survey histograms {log-bin: area}, merged over several materials"""
    pairs = []
    for h in groups:
        for b, a in h.items():
            pairs.append((10 ** (int(b) / 200.0), a))
    return wquant(pairs, 0.5)


def measures(S):
    large = S['grid'] == 'large'
    M = {}
    mats = S['materials']
    tot = sum(m['area'] for m in mats.values())
    by_game = defaultdict(float)
    for n, m in mats.items():
        by_game[game_name(n)] += m['area']

    def area_where(f):
        return sum(a for g, a in by_game.items() if f(g))

    # ---- edges, rounds and shading
    # bevel size = its leg along each face (the Bevel modifier's width): facet width / (2 sin(half the turn));
    # keen-style.md sizes chamfers this way (a 7 mm chamfer on a 100 mm frame leaves an 86 mm flat)
    bv = [(b[0] / max(2 * math.sin(math.radians(b[3]) / 2), 1e-6), b[1], b[2], b[3])
          for b in S['bevels'] if b[4]]  # survey: [facet width_m, segments, length_m, turn between faces, convex]
    M['chamfer_mm'] = wquant([(b[0] * 1000, b[2]) for b in bv if b[1] == 1 and 80 <= b[3] <= 100], 0.5)
    t = S['bevel_len_m'] + S['unbevelled_len_m']
    M['bevelled_share'] = ratio(S['bevel_len_m'], t)
    lim = 0.012 if large else 0.008
    s_ = [(b[1] == 1, b[2]) for b in bv if b[0] < lim]
    M['one_facet_small'] = ratio(sum(l for ok, l in s_ if ok), sum(l for _, l in s_))
    hi = 0.07 if large else 0.05
    r_ = [(b[1] >= 3, b[2]) for b in bv if 0.02 <= b[0] < hi]
    M['round_3facet'] = ratio(sum(l for ok, l in r_ if ok), sum(l for _, l in r_)) if sum(l for _, l in r_) > 0.5 else None
    sh = S['shading']
    for k in ('lt35', 'b40_50', 'b60_80', 'b85_95_outer', 'b85_95_inner'):
        sm, al = sh.get(k, (0.0, 0.0))
        M['smooth_' + k] = sm / al if al > (0.5 if large else 0.1) else None

    # ---- surface layout
    vis_big = [f for f in S['big_faces'] if f['vis'] >= 0.5]
    M['plain_big_faces'] = share(f['n_dec'] == 0 for f in vis_big)
    M['dressed_cover'] = quant([f['dec_area'] / f['area'] for f in vis_big if f['n_dec']], 0.5)
    D = S['decals']
    flat = [d for d in D if not d['strip']]
    M['decal_mirror_twins'] = share(d['twin'] for d in flat) if len(flat) >= 4 else None

    # ---- standard parts
    em = [clean_name(e) for e in S['empties']]
    M['ports'] = sum(1 for e in em if re.match(r'detector_conveyor(?!_?section|line)', e, re.I))
    M['terminals'] = sum(1 for e in em if re.match(r'detector_terminal', e, re.I))

    # ---- panel lines
    li = [k for k, d in enumerate(D) if d['strip'] and (d['atlas'], d['pid']) in LINE_PIECES and d['uvw']
          and d['uvw'] < 0.5]
    L = [D[k] for k in li]
    if L:
        M['line_width_mm'] = wquant([(d['uvw'] * 1000, d['uvl'] or 0) for d in L], 0.5)
        M['line_variant'] = ratio(sum(d['uvl'] or 0 for d in L if variant_ok(d['mat'], d['hmat'])),
                                  sum(d['uvl'] or 0 for d in L if variant_ok(d['mat'], d['hmat']) is not None))
        ends = [e for d in L for e in d['ends']]
        M['line_ends_joined'] = share(e in ('joins_strip', 'at_face_edge') for e in ends) if len(ends) >= 4 else None
        # a stroke = line pieces joined end to end (corner facets, T-joins); dashes are strokes under 10 widths
        up = {k: k for k in li}

        def root(k):
            while up[k] != k:
                up[k] = up[up[k]]; k = up[k]
            return k
        for k in li:
            for j in D[k].get('joins', []):
                if j in up:
                    up[root(k)] = root(j)
        strokes = defaultdict(list)
        for k in li:
            strokes[root(k)].append(D[k])
        sl = [(sum(d['uvl'] or 0 for d in s), quant([d['uvw'] for d in s], 0.5)) for s in strokes.values()]
        if len(sl) >= 3:
            M['line_stroke_m'] = quant([l for l, w in sl], 0.5)
            M['line_dash_share'] = share(l < 10 * w for l, w in sl)

    # ---- bolts
    heads = [d for d in flat if (d['atlas'], d['pid']) in BOLT_HEADS]
    if heads:
        M['bolt_head_mm'] = quant([max(d['L'], d['W']) * 1000 for d in heads], 0.5)
        M['bolt_edge_heads'] = quant([d['c2e'] / max(d['L'], d['W']) for d in heads
                                      if d['c2e'] is not None and max(d['L'], d['W']) > 0], 0.5)
        byh = defaultdict(set)
        cnt = Counter()
        for d in heads:
            if d['host'] is not None:
                byh[d['host']].add((d['atlas'], d['pid'])); cnt[d['host']] += 1
        M['bolt_one_type'] = share(len(byh[h]) == 1 for h in byh if cnt[h] >= 2) if len(byh) >= 2 else None

    # ---- signs and markings
    plates = [d for d in flat if (d['atlas'], d['pid']) in SIGN_PLATES]
    pictos = [d for d in flat if (d['atlas'], d['pid']) in SIGN_PICTOS]
    M['sign_count'] = len(plates) + len(pictos)
    M['sign_width_mm'] = quant([d['L'] * 1000 for d in plates], 0.5)
    M['sign_inset_mm'] = quant([d['margin_mm'] for d in plates + pictos], 0.5)
    codes = [d for d in flat if (d['atlas'], d['pid']) in CODES]
    M['code_height_mm'] = quant([d['W'] * 1000 for d in codes], 0.5)
    text = plates + codes + [d for d in flat if d['atlas'] == 'TextAtlas']
    M['text_unmirrored'] = share(d['mir'] < 0.5 for d in text) if len(text) >= 3 else None
    side = [d for d in text if abs(d['n'][2]) < 0.5 and d['vz'] is not None]
    M['text_upright'] = share(d['vz'] > 0.5 for d in side) if len(side) >= 3 else None

    # ---- materials and decal sheets
    V = S['vis']
    va = V['visible_area']
    vg = defaultdict(float)
    for n, a in V['by_mat'].items():
        vg[game_name(n)] += a
    vf = defaultdict(float)
    for n, a in vg.items():
        vf[family(n)] += a
    if va > 0:
        M['vis_colorable'] = vg['PaintedMetal_Colorable'] / va
        M['vis_darker'] = vg['PaintedMetal_Darker'] / va
        M['vis_yellow'] = vf['yellow'] / va or None
        M['vis_metal'] = (vf['metal'] + vf['chrome']) / va or None
        M['vis_decal_cover'] = V['decal_visible'] / va
    dh = V['decal_by_host_family']
    dens = {k: dh.get(k, 0.0) / vf[k] for k in ('paint', 'dark', 'yellow') if vf[k] > 0.005 * va}
    if 'paint' in dens and 'dark' in dens and dens['paint'] > 0:
        M['darker_vs_paint'] = dens['dark'] / dens['paint']
    if 'yellow' in dens:
        M['yellow_decals'] = dens['yellow']
    b_ = S['mat_border']
    M['mat_step_share'] = ratio(b_['step_m'], b_['step_m'] + b_['flat_m']) if b_['step_m'] + b_['flat_m'] > 0.5 else None
    paint3 = [mats[n]['upm_hist'] for n in mats if game_name(n) in
              ('PaintedMetal_Colorable', 'PaintedMetal_Darker', 'PaintedMetal_VeryDark')]
    M['uv_paint'] = hist_median(paint3)
    for key, g in (('uv_yellow', 'PaintedMetal_Yellow'), ('uv_conveyor', 'Conveyor')):
        hs = [mats[n]['upm_hist'] for n in mats if game_name(n) == g]
        M[key] = hist_median(hs) if by_game[g] > 0.002 * tot else None
    if tot:  # accent materials: None when absent, so the vanilla range is over the models that use them
        M['share_verydark'] = by_game['PaintedMetal_VeryDark'] / tot or None
        M['share_chrome'] = by_game['Chrome'] / tot or None
        M['share_metal_dull'] = by_game['Metal_Dull'] / tot or None
        M['share_rubber'] = area_where(lambda g: 'Rubber' in g) / tot or None
        M['share_emissive'] = area_where(lambda g: g.startswith('Emissive')) / tot or None
    vv = [variant_ok(d['mat'], d['hmat']) for d in D]
    M['decal_variant'] = share(vv) if sum(1 for x in vv if x is not None) >= 5 else None
    st = [abs(d['stretch'] - 1) <= 0.05 for d in flat if d['stretch']]
    M['decal_stretch_ok'] = share(st) if len(st) >= 5 else None

    # ---- the skill's craft rules (SKILL.md), fixed limits
    # 1.5 mm holds within 2 m of the origin; farther out the game stores vertices on a coarser grid and
    # decal_snap.py lifts decals to it, so a gap may reach that grid step plus 1.5 mm
    near = [d['gap'] for d in D if d['gap'] is not None and max(abs(x) for x in d['c']) < 2.0]
    M['decal_gap_mm'] = quant(near, 0.5) if near else None
    M['decal_gap_high'] = sum(1 for d in D if d['gap'] is not None and d['gap'] > max(3.0, pack_step_mm(d) + 1.5))
    M['decal_gap_low'] = sum(1 for d in D if d['gmin'] is not None and d['gmin'] < 0.3)
    ins = [d['inside'] for d in flat if d['inside'] is not None and d['kind'] not in ('seam', 'weld', 'strip')]
    M['decals_inside'] = share(ins) if ins else None
    onto = behind = n_ax = 0
    for d in D:
        g = d['gap']
        if g is None or d['flat'] > 1:
            continue
        n = d['n']; k = max(range(3), key=lambda i: abs(n[i]))
        if abs(n[k]) < 0.999:
            continue
        c = d['c']; s = float(max(min(math.floor(max(abs(x) for x in c)), 2048), 1))
        yd = c[k]; yh = yd - math.copysign(1, n[k]) * g / 1000
        p = (half(yd / s) * s - half(yh / s) * s) * math.copysign(1, n[k]) * 1000
        n_ax += 1
        if abs(p) < 1e-6:
            onto += 1
        elif p < 0:
            behind += 1
    M['packing_lost'] = onto + behind if n_ax else None
    M['_n_decals'] = len(D)
    M['_packing_n'] = n_ax
    return M


def half(x):
    import struct
    return struct.unpack('e', struct.pack('e', x))[0]


def pack_step_mm(d):
    """the game's vertex grid step (mm) at a decal, along its normal's main axis (scripts/decal_snap.py, pack)"""
    c, n = d['c'], d['n']
    k = max(range(3), key=lambda i: abs(n[i]))
    s = float(max(min(math.floor(max(abs(x) for x in c)), 2048), 1))
    u = abs(c[k]) / s
    return (2.0 ** (math.frexp(u)[1] - 11) if u >= 2 ** -14 else 2.0 ** -24) * s * 1000


# ======================================================================================== checks
# (id, keen-style.md section, table, row "What" text, unit, warn when the value is 'out' of the band, too 'low' or
#  too 'high', or 'info' to report only)
CHECKS = [
    ('chamfer_mm', 'Edges, rounds and shading', 'Chamfers and rounds',
     'Chamfer hard edges with one flat 45-degree facet (median single-facet size, measured as the leg)', 'mm',
     'out'),
    ('bevelled_share', 'Edges, rounds and shading', 'Chamfers and rounds',
     'Bevel nearly every hard edge (share of hard convex edge length)', '%', 'low'),
    ('one_facet_small', 'Edges, rounds and shading', 'Chamfers and rounds',
     'Keep a bevel one flat 45-degree face up to about 12 mm (one-facet share under 12 mm, 8 mm small grid)', '%', 'low'),
    ('round_3facet', 'Edges, rounds and shading', 'Chamfers and rounds',
     'Above about 20 mm, round the edge with 3 facets (3+ facet share at 20-70 mm, 20-50 mm small grid)', '%', 'low'),
    ('smooth_lt35', 'Edges, rounds and shading', 'Shading', 'Edges under 35 degrees (shaded smooth)', '%', 'low'),
    ('smooth_b40_50', 'Edges, rounds and shading', 'Shading',
     '45-degree chamfer edges (shaded smooth; the skill smooths at 30 degrees, so these stay hard)', '%', 'info'),
    ('smooth_b60_80', 'Edges, rounds and shading', 'Shading', '60-80 degree edges (shaded smooth)', '%', 'info'),
    ('smooth_b85_95_outer', 'Edges, rounds and shading', 'Shading', 'Keep 90-degree edges hard (outer, shaded smooth)',
     '%', 'high'),
    ('smooth_b85_95_inner', 'Edges, rounds and shading', 'Shading', 'Keep 90-degree edges hard (inner, shaded smooth)',
     '%', 'high'),
    ('plain_big_faces', 'Surface layout', 'Decal detail on a face',
     'Leave some big faces with no decal detail (visible big faces with no decal; lines not counted)', '%', 'out'),
    ('dressed_cover', 'Surface layout', 'Decal detail on a face',
     'Keep a dressed face mostly plain metal (decal cover, median dressed big face)', '%', 'out'),
    ('decal_mirror_twins', 'Surface layout', 'Decal detail on a face',
     'Mirror detail groups across the centre line (flat decals with a mirror twin across the block)', '%', 'low'),
    ('ports', 'Standard parts', 'Modules on dummies', 'Fit about two ports per block (detector_conveyor empties)',
     'count', 'info'),
    ('terminals', 'Standard parts', 'Modules on dummies',
     'Use about two terminals per block (detector_terminal empties)', 'count', 'info'),
    ('line_width_mm', 'Panel lines', 'Panel lines', 'Make a full line this wide (Atlas4 #3, Decals #51/54/58/61 strips)',
     'mm', 'out'),
    ('line_variant', 'Panel lines', 'Panel lines', "Match the line's variant to the paint under it", '%', 'low'),
    ('line_ends_joined', 'Panel lines', 'Panel lines', 'End lines on an edge or another line (share of open ends)',
     '%', 'low'),
    ('line_stroke_m', 'Panel lines', 'Panel lines',
     'Draw long unbroken strokes, never dashes (median stroke: pieces joined end to end)', 'm', 'low'),
    ('line_dash_share', 'Panel lines', 'Panel lines',
     'Draw long unbroken strokes, never dashes (strokes under 10 widths long)', '%', 'high'),
    ('bolt_head_mm', 'Bolts and rivets', 'Bolt heads',
     'Size bolt heads to the part (median round head: Atlas3 #14/#17, Decals #1-11)', 'mm', 'out'),
    ('bolt_edge_heads', 'Bolts and rivets', 'Bolt heads',
     'Set each bolt centre about one head in from the face edge', 'heads', 'out'),
    ('bolt_one_type', 'Bolts and rivets', 'Bolt heads',
     'One head type per face (bolted faces with a single head type)', '%', 'low'),
    ('sign_count', 'Signs and markings', 'Warning signs',
     'Count signs per block (text warning plates and hazard triangles)', 'count', 'out'),
    ('sign_width_mm', 'Signs and markings', 'Warning signs', 'Size text warning plates at real size (width)', 'mm',
     'out'),
    ('sign_inset_mm', 'Signs and markings', 'Warning signs',
     'Inset each sign from the nearest panel edge (median gap to the face edge)', 'mm', 'out'),
    ('text_upright', 'Signs and markings', 'Warning signs',
     "Keep side-face text upright to the block's Up axis (signs, codes, TextAtlas)", '%', 'low'),
    ('text_unmirrored', 'Signs and markings', 'Warning signs', 'Leave sign and code UVs unmirrored', '%', 'low'),
    ('code_height_mm', 'Signs and markings', 'Codes and lettering',
     'Set stencil codes and serials (Atlas2 #41-51) at this cap height (measured as the whole piece height, '
     'margins included)', 'mm', 'out'),
    ('vis_colorable', 'Materials and decal sheets', 'Material shares and mapping',
     'Make about half the visible surface PaintedMetal_Colorable', '%', 'out'),
    ('vis_darker', 'Materials and decal sheets', 'Material shares and mapping',
     'Make a quarter to a third PaintedMetal_Darker (visible)', '%', 'out'),
    ('mat_step_share', 'Materials and decal sheets', 'Material shares and mapping',
     'Change material at a step or a turn (paint/Darker border length on a fold)', '%', 'low'),
    ('vis_yellow', 'Materials and decal sheets', 'Material shares and mapping',
     'Keep Yellow a small accent on the port frames (visible)', '%', 'high'),
    ('vis_metal', 'Materials and decal sheets', 'Material shares and mapping',
     'Keep bare metal a small accent (Chrome, Metal_*, visible)', '%', 'high'),
    ('uv_paint', 'Materials and decal sheets', 'Material shares and mapping',
     'Map the painted metals at 0.40 UV per metre (Colorable, Darker, VeryDark)', 'uv', 'out'),
    ('uv_yellow', 'Materials and decal sheets', 'Material shares and mapping', 'Map Yellow port frames denser', 'uv',
     'out'),
    ('uv_conveyor', 'Materials and decal sheets', 'Material shares and mapping', 'Map Conveyor denser', 'uv', 'out'),
    ('share_verydark', 'Materials and decal sheets', 'Material roles',
     'Use VeryDark mostly as a shadow fill (all faces)', '%', 'high'),
    ('share_chrome', 'Materials and decal sheets', 'Material roles',
     'Use Chrome for bare structural or moving metal (all faces)', '%', 'high'),
    ('share_metal_dull', 'Materials and decal sheets', 'Material roles',
     'Use Metal_Dull for small mechanism hardware (all faces)', '%', 'high'),
    ('share_rubber', 'Materials and decal sheets', 'Material roles',
     'Use Rubber for hoses, cables, seals and small pads (all faces)', '%', 'high'),
    ('share_emissive', 'Materials and decal sheets', 'Material roles',
     'Put plain Emissive on small, nearly flat panels (all faces)', '%', 'high'),
    ('vis_decal_cover', 'Materials and decal sheets', 'Decals',
     'Cover about 6% (large) to 9% (small) of the visible surface with decals', '%', 'out'),
    ('decal_variant', 'Materials and decal sheets', 'Decals', 'Use the decal variant that matches the face under it',
     '%', 'low'),
    ('darker_vs_paint', 'Materials and decal sheets', 'Decals',
     'Give Darker at least as many decals as paint (visible decal density, Darker / paint)', 'x', 'low'),
    ('yellow_decals', 'Materials and decal sheets', 'Decals',
     'Give Yellow no decals (visible decal area per Yellow area)', '%', 'high'),
    ('decal_stretch_ok', 'Materials and decal sheets', 'Decals',
     'Keep decal art unstretched (flat decals within 5% texel aspect)', '%', 'low'),
]
CRAFT = [
    ('decal_gap_mm', 'Decals sit about 1.5 mm off the surface (median gap within 2 m of the origin; PASS 1.0-2.5 mm)',
     'mm', lambda v: 1.0 <= v <= 2.5),
    ('decal_gap_high', 'No decal floats more than 3 mm off, or past 2 m more than the vertex grid step + 1.5 mm '
     '(they read as floating in game)', 'count', lambda v: v == 0),
    ('decal_gap_low', 'No decal comes within 0.3 mm of (or behind) its surface', 'count', lambda v: v == 0),
    ('decals_inside', 'Keep each flat decal fully inside its flat face', '%', lambda v: v >= 0.95),
    ('packing_lost', "No axis-aligned decal rounds onto or behind its surface in the game's vertex packing "
     '(else run scripts/decal_snap.py)', 'count', lambda v: v == 0),
]
NOT_CHECKED = ('Cylinders; Shading (normal weighting); Layers and silhouette (all tables); Surface layout: Areas, '
               'depths and bays, Matching the sides; Standard parts: port, terminal and screen sizes, Surface detail, '
               'Modelled extras; Panel lines: insets, axes, density, corners, rings, doubles, grooves; Rivets and '
               'bands; Own-hazard signs; Codes (choice and crops); Stripes and pointer marks. Check these by eye '
               'against keen-style.md.')


SUFFIX = {'%': '%', 'mm': ' mm', 'm': ' m', 'uv': ' UV/m', 'heads': ' heads', 'x': 'x', 'count': ''}


def num(v, unit):
    if unit == '%':
        x = v * 100
        return ('%.1f' if abs(x) < 10 else '%.0f') % x
    return {'mm': '%.1f', 'm': '%.2f', 'uv': '%.3f', 'heads': '%.2f', 'x': '%.2f'}.get(unit, '%g') % (
        v if unit != 'count' else round(v, 2))


def fmt(v, unit):
    return 'none' if v is None else num(v, unit) + SUFFIX[unit]


def compare(S, M, rules, era, out=print):
    grid = S['grid']
    gk = '%s-%s' % (era, grid)
    grp = rules['groups'].get(gk, {})
    out('Keen style check: %s (%s grid), against %d vanilla %s %s-grid models' % (
        S['name'], grid, len(grp.get('models', [])), era, grid))
    out('surface %.1f m2, visible %.1f m2 (%.0f%%); %d decal pieces; bounding box %s m' % (
        S['vis']['base_area'], S['vis']['visible_area'], 100 * S['vis']['visible_area'] / max(S['vis']['base_area'], 1e-9),
        M['_n_decals'], ' x '.join('%.2f' % x for x in S['bbox_size_m'])))
    out('PASS: inside the middle 80% of vanilla models (p10-p90); WARN: outside it on the side that matters; '
        'INFO: reported only. vanilla = median (p25-p75) over models that have the feature.')
    tally = Counter()
    sec = None
    for cid, section, table, row, unit, mode in CHECKS:
        if section != sec:
            out('\n== %s' % section); sec = section
        v = M.get(cid)
        r = rules['checks'].get(cid, {}).get(gk)
        if r:
            n, of, p10, p25, p50, p75, p90 = r
            van = 'vanilla %s%s (%s-%s), PASS band %s-%s, in %d of %d models' % (
                num(p50, unit), SUFFIX[unit], num(p25, unit), num(p75, unit), num(p10, unit), num(p90, unit), n, of)
        else:
            van = 'no vanilla value for this grid and era'
        if v is None:
            status = 'INFO'
            here = 'not used or too few to measure'
        else:
            here = fmt(v, unit)
            if mode == 'info' or not r or r[0] < 4:
                status = 'INFO'
            else:
                lo, hi = r[2], r[6]
                eps = 1e-9 + 0.01 * max(abs(lo), abs(hi))
                low, high = v < lo - eps, v > hi + eps
                bad = {'out': low or high, 'low': low, 'high': high}[mode]
                status = 'WARN' if bad else 'PASS'
        tally[status] += 1
        out('%-4s  %s: %s' % (status, table, row))
        out('      here %s; %s' % (here, van))
    out('\n== The skill\'s craft rules (SKILL.md), fixed limits')
    for cid, row, unit, ok in CRAFT:
        v = M.get(cid)
        status = 'INFO' if v is None else ('PASS' if ok(v) else 'WARN')
        tally[status] += 1
        extra = ' (%d axis-aligned decals tested)' % M['_packing_n'] if cid == 'packing_lost' and v is not None else ''
        out('%-4s  %s\n      here %s%s' % (status, row, fmt(v, unit), extra))
    out('\nNot checked by this script: ' + NOT_CHECKED)
    out('\n%d PASS, %d WARN, %d INFO' % (tally['PASS'], tally['WARN'], tally['INFO']))


def build_rules(survey_dir, meta_path, out_path):
    meta = {b['name']: b for b in json.load(open(meta_path, encoding='utf-8'))}
    per = defaultdict(dict)
    groups = defaultdict(list)
    for fn in sorted(os.listdir(survey_dir)):
        if not fn.endswith('.survey.json'):
            continue
        S = json.load(open(os.path.join(survey_dir, fn), encoding='utf-8'))
        b = meta.get(S['name'])
        if not b:
            print('skip (not in meta)', S['name']); continue
        gk = '%s-%s' % (b['era'], b['grid'])
        groups[gk].append(S['name'])
        per[gk][S['name']] = measures(S)
    checks = {}
    for cid, *_ in CHECKS:
        checks[cid] = {}
        for gk, ms in per.items():
            xs = [m.get(cid) for m in ms.values() if m.get(cid) is not None]
            if not xs:
                continue
            checks[cid][gk] = [len(xs), len(ms)] + [round(quant(xs, p), 4) for p in (0.1, 0.25, 0.5, 0.75, 0.9)]
    rules = {'about': 'Vanilla ranges for scripts/keen_check.py: per check and era-grid group, [models with the '
                      'feature, models in the group, p10, p25, median, p75, p90] over models, each weighted evenly. '
                      'Built by keen_check.py --build-rules from its own surveys of the ModSDK vanilla models '
                      '(the set keen-style.md measured), so every value is measured the same way as the model '
                      'checked. [HARD, measured]',
             'built': time.strftime('%Y-%m-%d'),
             'groups': {gk: {'models': sorted(v)} for gk, v in sorted(groups.items())},
             'checks': checks}
    with open(out_path, 'w', encoding='utf-8', newline='\r\n') as f:
        json.dump(rules, f, indent=1)
    print('wrote', out_path, {gk: len(v) for gk, v in groups.items()})


def load_rules(path):
    return json.load(open(path or os.path.join(REFS, 'keen-rules.json'), encoding='utf-8'))


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


# ======================================================================================== survey (Blender)
def survey(argv):
    import bpy, bmesh, subprocess, tempfile, addon_utils
    from mathutils import Vector, Matrix
    from mathutils.bvhtree import BVHTree
    from mathutils.kdtree import KDTree
    bpy.context.preferences.use_preferences_save = False
    T0 = time.time()

    def log(*a):
        print('[keen_check %6.1fs]' % (time.time() - T0), *a, flush=True)

    skill = arg(argv, '--skill', REFS)
    catalog = {}
    for line in open(os.path.join(skill, 'materials-catalog.md'), encoding='utf-8'):
        m = re.match(r'\|\s*([A-Za-z0-9_]+)\s*\|\s*(MESH|DECAL_CUTOUT|GLASS|ALPHA_MASKED|HOLO)\s*\|(.*)\|', line)
        if m:
            p = re.search(r'paint (\d+)%', m.group(3))
            catalog[m.group(1)] = {'tech': m.group(2), 'paint': int(p.group(1)) / 100 if p else 0.0}
    ATLAS = json.load(open(os.path.join(skill, 'atlas-regions.json'), encoding='utf-8'))

    # ---------------------------------------------------------------- collect the meshes, modifiers applied
    model = arg(argv, '--model')
    src_objs, empties = [], []
    if model:
        path = model
        if model.lower().endswith('.fbx'):
            exe = None
            for mod in addon_utils.modules():
                if mod.__name__ == 'space-engineers-utilities':
                    exe = os.path.join(os.path.dirname(mod.__file__), 'tools', 'FBX2glTF-windows-x64.exe')
            if not exe or not os.path.exists(exe):
                raise SystemExit('an .fbx needs the SEUT add-on (its FBX2glTF tool); pass a .glb instead')
            path = os.path.join(tempfile.mkdtemp(prefix='keen_check_'), 'model.glb')
            subprocess.run([exe, '-b', '--user-properties', '-i', model, '-o', path], capture_output=True, timeout=600)
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=path)
        new = [o for o in bpy.data.objects if o not in before]
        rz = Matrix.Rotation(math.pi, 4, 'Z')
        for r in [o for o in new if o.parent is None]:
            r.matrix_world = rz @ r.matrix_world
        bpy.context.view_layer.update()
        sc = bpy.context.scene
        deps = bpy.context.evaluated_depsgraph_get()
        src_objs = [o for o in new if o.type == 'MESH']
        empties = [o.name for o in new if o.type == 'EMPTY' and not o.name.startswith('RootNode')]
        name = arg(argv, '--name', os.path.splitext(os.path.basename(model))[0])
        grid = arg(argv, '--grid')
        source = os.path.basename(model)
    else:
        sname = arg(argv, '--scene')
        sc = bpy.data.scenes[sname] if sname else bpy.context.scene
        main = next((c for c in sc.collection.children_recursive if c.name.startswith('Main (')), None)
        if main is None:
            raise SystemExit('scene %s has no "Main (...)" collection (not a SEUT scene?)' % sc.name)
        if sc == bpy.context.scene:
            deps = bpy.context.evaluated_depsgraph_get()
        else:  # headless Blender keeps no depsgraph for other scenes; have one built for this view layer
            with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):
                deps = bpy.context.evaluated_depsgraph_get()
        src_objs = [o for o in main.all_objects if o.type == 'MESH']
        empties = [o.name for o in main.all_objects if o.type == 'EMPTY']
        grid = arg(argv, '--grid') or getattr(getattr(sc, 'seut', None), 'gridScale', None)
        name = arg(argv, '--name', sc.name)
        source = os.path.basename(bpy.data.filepath) + ' / ' + main.name
    if grid not in ('large', 'small'):
        raise SystemExit('pass --grid large or --grid small')
    CELL = 2.5 if grid == 'large' else 0.5
    meshes = []
    for o in src_objs:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        meshes.append((o.name, me, o.matrix_world.copy()))
    log(name, len(meshes), 'meshes', len(empties), 'empties, grid', grid)

    # ---------------------------------------------------------------- shading: smooth share by edge angle
    # Edges are matched by vertex position (imported models split vertices at hard edges); an edge is smooth when
    # both faces have the same corner normal at both of its ends.
    sh = defaultdict(lambda: [0.0, 0.0])
    for oname, me, mw in meshes:
        mats = [clean_name(m.name) if m else 'NONE' for m in me.materials]
        try:
            cn = [c.vector.copy() for c in me.corner_normals]
        except AttributeError:
            me.calc_normals_split(); cn = [l.normal.copy() for l in me.loops]
        co = [mw @ v.co for v in me.vertices]
        key = [tuple(round(x, 5) for x in c) for c in co]
        rot = mw.to_3x3()
        edges = defaultdict(list)
        for p in me.polygons:
            if is_decal(mats[p.material_index] if p.material_index < len(mats) else 'NONE'):
                continue
            ls = list(p.loop_indices)
            for i, li in enumerate(ls):
                lj = ls[(i + 1) % len(ls)]
                a, b = key[me.loops[li].vertex_index], key[me.loops[lj].vertex_index]
                if a != b:
                    edges[(a, b) if a < b else (b, a)].append((p.index, {a: li, b: lj}))
        for (a, b), fs in edges.items():
            if len(fs) != 2:
                continue
            (pa, la), (pb, lb) = fs
            na = (rot @ me.polygons[pa].normal).normalized(); nb = (rot @ me.polygons[pb].normal).normalized()
            if na.length < 0.5 or nb.length < 0.5:
                continue
            ang = math.degrees(na.angle(nb, 0))
            if ang < 1:
                continue
            smooth = all((rot @ cn[la[k]]).angle(rot @ cn[lb[k]], 0) < math.radians(1) for k in (a, b))
            if ang < 35:
                b_ = 'lt35'
            elif 40 <= ang <= 50:
                b_ = 'b40_50'
            elif 60 <= ang <= 80:
                b_ = 'b60_80'
            elif 85 <= ang <= 95:
                ca = sum((co[me.loops[l].vertex_index] for l in me.polygons[pa].loop_indices), Vector()) / len(
                    me.polygons[pa].loop_indices)
                cb = sum((co[me.loops[l].vertex_index] for l in me.polygons[pb].loop_indices), Vector()) / len(
                    me.polygons[pb].loop_indices)
                b_ = 'b85_95_outer' if (cb - ca).dot(na) < 0 else 'b85_95_inner'
            else:
                continue
            L = (Vector(a) - Vector(b)).length
            sh[b_][1] += L
            if smooth:
                sh[b_][0] += L
    log('shading measured')

    # ---------------------------------------------------------------- combine into a base mesh and a decal mesh
    MATS, MAT_ID = [], {}

    def mid(n):
        if n not in MAT_ID:
            MAT_ID[n] = len(MATS); MATS.append(n)
        return MAT_ID[n]

    def gather(want_decal):
        verts, faces, fm, uvs = [], [], [], []
        for oname, me, mw in meshes:
            uvl = me.uv_layers[0].data if me.uv_layers else None
            mats = [clean_name(m.name) if m else 'NONE' for m in me.materials]
            vmap = {}
            for p in me.polygons:
                n = mats[p.material_index] if p.material_index < len(mats) else 'NONE'
                if is_decal(n) != want_decal:
                    continue
                idx = []
                for li in p.loop_indices:
                    vi = me.loops[li].vertex_index
                    j = vmap.get(vi)
                    if j is None:
                        j = vmap[vi] = len(verts); verts.append(mw @ me.vertices[vi].co)
                    idx.append(j)
                    uvs.append(tuple(uvl[li].uv) if uvl else (0.0, 0.0))
                faces.append(idx); fm.append(mid(n))
        me2 = bpy.data.meshes.new('kc_decal' if want_decal else 'kc_base')
        me2.from_pydata(verts, [], faces)
        a = me2.attributes.new('mat', 'INT', 'FACE'); a.data.foreach_set('value', fm)
        uvlay = me2.uv_layers.new(name='UVMap')
        uvlay.data.foreach_set('uv', [c for uv in uvs for c in uv])
        me2.validate(clean_customdata=False)
        bm = bmesh.new(); bm.from_mesh(me2)
        return bm

    base_bm = gather(False)
    dec_bm = gather(True)
    log('base faces', len(base_bm.faces), 'decal faces', len(dec_bm.faces))

    bL_mat = base_bm.faces.layers.int.get('mat')
    bL_uv = base_bm.loops.layers.uv.active

    def uv_area(f, lay):
        uv = [l[lay].uv for l in f.loops]
        return sum(abs((uv[i] - uv[0]).x * (uv[i + 1] - uv[0]).y - (uv[i] - uv[0]).y * (uv[i + 1] - uv[0]).x) * 0.5
                   for i in range(1, len(uv) - 1))

    def face_jac(f, lay):
        ls = f.loops; su = sv = wsum = 0.0
        for i in range(1, len(ls) - 1):
            P0, P1, P2 = ls[0].vert.co, ls[i].vert.co, ls[i + 1].vert.co
            q0, q1, q2 = ls[0][lay].uv, ls[i][lay].uv, ls[i + 1][lay].uv
            E1, E2 = P1 - P0, P2 - P0; d1, d2 = q1 - q0, q2 - q0
            det = d1.x * d2.y - d2.x * d1.y
            ta = E1.cross(E2).length * 0.5
            if abs(det) < 1e-12 or ta < 1e-12:
                continue
            dPdu = (E1 * d2.y - E2 * d1.y) / det; dPdv = (E2 * d1.x - E1 * d2.x) / det
            if dPdu.length < 1e-12 or dPdv.length < 1e-12:
                continue
            su += ta / dPdu.length; sv += ta / dPdv.length; wsum += ta
        return (su / wsum, sv / wsum) if wsum > 0 else None

    bmesh.ops.remove_doubles(base_bm, verts=base_bm.verts[:], dist=1e-4)
    for seq in (base_bm.verts, base_bm.edges, base_bm.faces):
        seq.index_update(); seq.ensure_lookup_table()
    base_bm.normal_update()
    NF = len(base_bm.faces)
    mat_area = defaultdict(float)
    upm_hist = defaultdict(lambda: defaultdict(float))
    aniso = defaultdict(list)
    for f in base_bm.faces:
        n = MATS[f[bL_mat]]
        A = f.calc_area()
        mat_area[n] += A
        if A < 1e-8:
            continue
        ua = uv_area(f, bL_uv)
        if ua < 1e-12:
            continue
        upm_hist[n][int(round(math.log10(math.sqrt(ua / A)) * 200))] += A
        j = face_jac(f, bL_uv)
        if j and min(j) > 0:
            aniso[n].append((max(j) / min(j), A))
    fnorm = [f.normal.copy() for f in base_bm.faces]
    fcent = [f.calc_center_median() for f in base_bm.faces]
    farea = [f.calc_area() for f in base_bm.faces]
    fmat = [f[bL_mat] for f in base_bm.faces]
    bvh = BVHTree.FromBMesh(base_bm)

    # ---------------------------------------------------------------- flat regions
    COS1 = math.cos(math.radians(1.0))
    region = [-1] * NF
    reg_faces = []
    for f in base_bm.faces:
        if region[f.index] != -1:
            continue
        r = len(reg_faces); region[f.index] = r
        n0 = fnorm[f.index]; c0 = fcent[f.index]
        lst = [f.index]
        if n0.length > 0.5:
            q = deque([f])
            while q:
                g = q.popleft()
                for e in g.edges:
                    for h in e.link_faces:
                        hi = h.index
                        if region[hi] == -1 and fnorm[hi].dot(n0) > COS1 and abs((fcent[hi] - c0).dot(n0)) < 5e-4:
                            region[hi] = r; lst.append(hi); q.append(h)
        reg_faces.append(lst)
    NR = len(reg_faces)

    def basis(n):
        t1 = n.orthogonal().normalized()
        return t1, n.cross(t1).normalized()

    def hull2d(pts):
        pts = sorted(set(pts))
        if len(pts) <= 2:
            return pts

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        lo, up = [], []
        for p in pts:
            while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
                lo.pop()
            lo.append(p)
        for p in reversed(pts):
            while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
                up.pop()
            up.append(p)
        return lo[:-1] + up[:-1]

    def min_rect(pts):
        """min-area rectangle of 2D points -> (length, width, long-axis angle 0-180, centre, hull)"""
        h = hull2d([(round(x, 6), round(y, 6)) for x, y in pts])
        if len(h) < 2:
            return 0, 0, 0, (h[0] if h else (0, 0)), h
        best = None
        for i in range(len(h)):
            p, q = h[i], h[(i + 1) % len(h)]
            ex, ey = q[0] - p[0], q[1] - p[1]
            L = math.hypot(ex, ey)
            if L < 1e-9:
                continue
            ux, uy = ex / L, ey / L
            pu = [x * ux + y * uy for x, y in h]; pv = [-x * uy + y * ux for x, y in h]
            du, dv = max(pu) - min(pu), max(pv) - min(pv)
            if best is None or du * dv < best[0] - 1e-12:
                cu, cv = (max(pu) + min(pu)) / 2, (max(pv) + min(pv)) / 2
                ang = (math.degrees(math.atan2(uy, ux)) if du >= dv else math.degrees(math.atan2(ux, -uy))) % 180
                best = (du * dv, max(du, dv), min(du, dv), ang, (cu * ux - cv * uy, cu * uy + cv * ux))
        if best is None:
            return 0, 0, 0, h[0], h
        return best[1], best[2], best[3], best[4], h

    reg = []
    for r, fl in enumerate(reg_faces):
        A = sum(farea[i] for i in fl)
        n = fnorm[fl[0]]
        if n.length < 0.5 or A < 1e-9:
            reg.append({'area': A, 'n': n, 'L': 0, 'W': 0, 'ang': 0, 'c': fcent[fl[0]], 'basis': None, 'mats': {}})
            continue
        t1, t2 = basis(n)
        vs = {v.index: v.co for i in fl for v in base_bm.faces[i].verts}
        L, W, ang, c2, _ = min_rect([(co.dot(t1), co.dot(t2)) for co in vs.values()])
        mats = defaultdict(float)
        cen = Vector((0, 0, 0))
        for i in fl:
            mats[MATS[fmat[i]]] += farea[i]; cen += fcent[i] * farea[i]
        reg.append({'area': A, 'n': n, 'L': L, 'W': W, 'ang': ang, 'c': cen / A, 'basis': (t1, t2),
                    'mats': dict(mats)})

    # region adjacency, hard edges, paint/Darker borders
    adj = defaultdict(lambda: defaultdict(float))
    hard_edges = []
    border = {'step_m': 0.0, 'flat_m': 0.0}
    for e in base_bm.edges:
        lf = e.link_faces
        if len(lf) != 2:
            continue
        a, b = lf[0].index, lf[1].index
        ra, rb = region[a], region[b]
        l = e.calc_length()
        fa, fb = family(MATS[fmat[a]]), family(MATS[fmat[b]])
        if fa != fb and {fa, fb} == {'paint', 'dark'}:
            border['flat_m' if ra == rb else 'step_m'] += l
        if ra == rb:
            continue
        adj[ra][rb] += l; adj[rb][ra] += l
        if fnorm[a].length > 0.5 and fnorm[b].length > 0.5:
            hard_edges.append((l, ra, rb, math.degrees(fnorm[a].angle(fnorm[b], 0)),
                               (fcent[b] - fcent[a]).dot(fnorm[a]) < 0))

    # ---------------------------------------------------------------- bevels: chains of narrow regions
    BEV_MAX = 0.15 if grid == 'large' else 0.05
    narrow = [rg['basis'] is not None and 1e-5 < rg['W'] < BEV_MAX and rg['L'] > 3 * rg['W'] for rg in reg]

    def axis3(rg):
        t1, t2 = rg['basis']; a = math.radians(rg['ang'])
        return (t1 * math.cos(a) + t2 * math.sin(a)).normalized()

    bevels = []
    seen = set()
    for r in range(NR):
        if not narrow[r] or r in seen:
            continue
        ax = axis3(reg[r])
        chain = [r]; seen.add(r); q = deque([r])
        while q:
            s = q.popleft()
            for t, l in adj[s].items():
                if t in seen or not narrow[t] or l < 0.5 * min(reg[s]['L'], reg[t]['L']):
                    continue
                if abs(axis3(reg[t]).dot(ax)) < 0.95:
                    continue
                seen.add(t); chain.append(t); q.append(t)
        nb = defaultdict(float)
        for s in chain:
            for t, l in adj[s].items():
                if t not in chain and not narrow[t] and reg[t]['basis'] is not None:
                    nb[t] += l
        if len(nb) < 2:
            continue
        top = sorted(nb.items(), key=lambda kv: -kv[1])[:2]
        A_, B_ = top[0][0], top[1][0]
        nA, nB = reg[A_]['n'], reg[B_]['n']
        angAB = math.degrees(nA.angle(nB, 0))
        if not 30 <= angAB <= 150:
            continue
        if not all(abs(math.degrees(reg[s]['n'].angle(nA, 0)) + math.degrees(reg[s]['n'].angle(nB, 0)) - angAB) < 10
                   for s in chain):
            continue
        Lc = max(reg[s]['L'] for s in chain)
        if top[1][1] < 0.5 * Lc:
            continue
        bevels.append([round(sum(reg[s]['W'] for s in chain), 5), len(chain), round(Lc, 4), round(angAB, 1),
                       (reg[B_]['c'] - reg[A_]['c']).dot(nA) < 0])
    unbev = sum(l for l, a, b, ang, cv in hard_edges if cv and ang > 45 and not narrow[a] and not narrow[b]
                and reg[a]['W'] >= BEV_MAX and reg[b]['W'] >= BEV_MAX)
    bev_len = sum(b[2] for b in bevels if b[4])
    log('regions', NR, 'bevels', len(bevels))

    # ---------------------------------------------------------------- decal pieces
    dL_mat = dec_bm.faces.layers.int.get('mat')
    dL_uv = dec_bm.loops.layers.uv.active
    dec_bm.faces.ensure_lookup_table(); dec_bm.verts.ensure_lookup_table(); dec_bm.normal_update()
    pid = [-1] * len(dec_bm.faces)
    pieces = []
    for f in dec_bm.faces:
        if pid[f.index] != -1:
            continue
        p = len(pieces); pid[f.index] = p; q = deque([f]); fl = [f]
        m = f[dL_mat]
        while q:
            g = q.popleft()
            for v in g.verts:
                for h in v.link_faces:
                    if pid[h.index] == -1 and h[dL_mat] == m:
                        pid[h.index] = p; fl.append(h); q.append(h)
        pieces.append(fl)

    def match_atlas(atlas, ub):
        if atlas not in ATLAS:
            return None
        u0, v0, u1, v1 = ub
        wrapped = (u1 - u0) > 0.999
        if wrapped:
            u0, u1 = 0.0, 1.0
        else:
            k = math.floor(u0 + 1e-6); u0 -= k; u1 -= k
        if (v1 - v0) > 0.999:
            v0, v1 = 0.0, 1.0
        else:
            k = math.floor(v0 + 1e-6); v0 -= k; v1 -= k
        if u1 - u0 < 1e-4:
            u0 -= 5e-5; u1 += 5e-5
        if v1 - v0 < 1e-4:
            v0 -= 5e-5; v1 += 5e-5
        pa = max(u1 - u0, 1e-9) * max(v1 - v0, 1e-9)
        best = None
        for rr in ATLAS[atlas]['regions']:
            inter = max(0.0, min(u1, rr['u1']) - max(u0, rr['u0'])) * max(0.0, min(v1, rr['v1']) - max(v0, rr['v0']))
            if inter <= 0:
                continue
            ra = (rr['u1'] - rr['u0']) * (rr['v1'] - rr['v0'])
            score = 0.5 * inter / (pa + ra - inter) + 0.5 * inter / pa
            if best is None or score > best[0]:
                best = (score, rr)
        return {'id': best[1]['id'], 'piece': best[1]['piece'], 'wrapped': wrapped} if best else \
            {'id': None, 'piece': '', 'wrapped': wrapped}

    rb_cache = {}

    def region_boundary(r):
        if r not in rb_cache:
            fs = set(reg_faces[r]); segs = []
            for i in reg_faces[r]:
                for e in base_bm.faces[i].edges:
                    lf = e.link_faces
                    if len(lf) != 2 or any(g.index not in fs for g in lf):
                        segs.append((e.verts[0].co.copy(), e.verts[1].co.copy()))
            rb_cache[r] = segs
        return rb_cache[r]

    def seg_dist2d(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        t = 0 if L2 < 1e-18 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
        return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

    def pseg3(P, a, b):
        d = b - a; L2 = d.dot(d)
        t = 0 if L2 < 1e-18 else max(0.0, min(1.0, (P - a).dot(d) / L2))
        return (P - (a + d * t)).length

    def cast_offset(P, n):
        """gap between decal point P and the surface behind it (m, + = in front), host face index"""
        eps = 1e-5
        dn = bvh.ray_cast(P + n * eps, -n, 0.08)
        up = bvh.ray_cast(P - n * eps, n, 0.003)
        gd = dn[3] - eps if dn[0] is not None else None
        if up[0] is not None and (gd is None or gd > 0.003):
            return -(up[3] - eps), up[2]
        if gd is None:
            return None, None
        return gd, dn[2]

    decals, piece_of = [], []
    for p, fl in enumerate(pieces):
        mname = MATS[fl[0][dL_mat]]
        A = sum(f.calc_area() for f in fl)
        nsum = Vector((0, 0, 0)); csum = Vector((0, 0, 0))
        for f in fl:
            a = f.calc_area(); nsum += f.normal * a; csum += f.calc_center_median() * a
        if A < 1e-10 or nsum.length < 1e-12:
            continue
        n = nsum.normalized(); C = csum / A
        vs = {v.index: v.co.copy() for f in fl for v in f.verts}
        flat = max(abs((co - C).dot(n)) for co in vs.values())
        t1, t2 = basis(n)
        L, W, ang, c2, hull = min_rect([(co.dot(t1), co.dot(t2)) for co in vs.values()])
        uvs = [l[dL_uv].uv.copy() for f in fl for l in f.loops]
        ub = (min(u.x for u in uvs), min(u.y for u in uvs), max(u.x for u in uvs), max(u.y for u in uvs))
        atlas = atlas_of(mname)
        asz = ATLAS[atlas]['size'] if atlas in ATLAS else [2048, 2048]
        mpu, mpv, wts, mir_a = [], [], [], 0.0
        vdir = Vector((0, 0, 0))
        for f in fl:
            ls = f.loops
            for i in range(1, len(ls) - 1):
                P0, P1, P2 = ls[0].vert.co, ls[i].vert.co, ls[i + 1].vert.co
                q0, q1, q2 = ls[0][dL_uv].uv, ls[i][dL_uv].uv, ls[i + 1][dL_uv].uv
                E1, E2 = P1 - P0, P2 - P0; d1, d2 = q1 - q0, q2 - q0
                det = d1.x * d2.y - d2.x * d1.y
                ta = E1.cross(E2).length * 0.5
                if abs(det) < 1e-12:
                    continue
                dPdu = (E1 * d2.y - E2 * d1.y) / det; dPdv = (E2 * d1.x - E1 * d2.x) / det
                if dPdu.cross(dPdv).dot(f.normal) < 0:
                    mir_a += ta
                mpu.append(dPdu.length); mpv.append(dPdv.length); wts.append(ta)
                if dPdv.length > 1e-12:
                    vdir += dPdv.normalized() * ta

        def wmed(xs):
            return wquant(list(zip(xs, wts)), 0.5) if xs else None
        m_u, m_v = wmed(mpu), wmed(mpv)
        match = match_atlas(atlas, ub)
        desc = match['piece'] if match else ''
        kind = piece_kind(desc) if match else 'other'
        lu = m_u * (ub[2] - ub[0]) if m_u else None
        lv = m_v * (ub[3] - ub[1]) if m_v else None
        uv_w = min(lu, lv) if lu and lv else None
        uv_l = max(lu, lv) if lu and lv else None
        along = ('u' if lu >= lv else 'v') if lu and lv else None
        strip = bool((match and match['wrapped']) or L > 6 * max(W, 1e-6) or (uv_w and uv_l and uv_l > 6 * uv_w))
        if mname.startswith('Paneling') and kind not in ('weld', 'rivet_band', 'bolt') and strip:
            kind = 'seam'
        ends, closed = [], False
        if strip and along:
            fset = set(f.index for f in fl)
            bed = {e.index: e for f in fl for e in f.edges if sum(1 for g in e.link_faces if g.index in fset) == 1}
            vadj = defaultdict(list)
            for e in bed.values():
                a_, b_ = e.verts; vadj[a_.index].append(b_.index); vadj[b_.index].append(a_.index)
            seenv, loops = set(), 0
            for v0 in vadj:
                if v0 in seenv:
                    continue
                loops += 1; st = [v0]; seenv.add(v0)
                while st:
                    x = st.pop()
                    for y in vadj[x]:
                        if y not in seenv:
                            seenv.add(y); st.append(y)
            closed = loops >= 2
            if loops == 1:
                ax_i = 0 if along == 'u' else 1
                vc = {}
                for f in fl:
                    for l in f.loops:
                        vc[l.vert.index] = min(vc.get(l.vert.index, 1e9), l[dL_uv].uv[ax_i])
                lo, hi = min(vc.values()), max(vc.values())
                for target in (lo, hi):
                    ev = [dec_bm.verts[i].co for i, c in vc.items() if abs(c - target) < 1e-4]
                    if ev:
                        ends.append(sum(ev, Vector((0, 0, 0))) / len(ev))
                if len(ends) == 2 and uv_w and (ends[0] - ends[1]).length < 2 * uv_w:
                    closed = True; ends = []
        fill = A / (L * W) if L * W > 1e-12 else 1.0
        on_vertices = flat > 0.001 or fill < 0.7
        if not on_vertices:
            samples = [(C, n)] + [(t1 * hx + t2 * hy + n * C.dot(n) + (C - (t1 * hx + t2 * hy + n * C.dot(n))) * 0.1, n)
                                  for hx, hy in hull[:16]]
        else:
            vl = list(vs.keys()); step = max(1, len(vl) // 32)
            fset_ = set(f.index for f in fl)
            samples = []
            for vi in vl[::step]:
                v = dec_bm.verts[vi]
                fc = next((g for g in v.link_faces if g.index in fset_), None)
                if fc is not None:
                    samples.append((v.co + (fc.calc_center_median() - v.co) * 0.1,
                                    fc.normal if fc.normal.length > 0.5 else n))
        offs, hosts = [], []
        for s, sn in samples:
            o_, fi = cast_offset(s, sn)
            offs.append(o_); hosts.append(region[fi] if fi is not None else None)
        if on_vertices:
            g_ = sorted(o for o in offs if o is not None)
            offs = [g_[len(g_) // 2] if g_ else None] + offs
            cands = [h for h in hosts if h is not None]
            hosts = [max(set(cands), key=cands.count) if cands else None] + hosts
        host = hosts[0]
        if host is None:
            cands = [h for h in hosts if h is not None]
            host = max(set(cands), key=cands.count) if cands else None
        gaps = [o for o in offs if o is not None]
        rec = {'mat': mname, 'atlas': atlas, 'pid': match['id'] if match else None, 'piece': desc, 'kind': kind,
               'strip': strip, 'L': round(L, 4), 'W': round(W, 4), 'area': round(A, 6),
               'c': [round(x, 4) for x in C], 'n': [round(x, 3) for x in n], 'flat': round(flat * 1000, 2),
               'uvw': round(uv_w, 4) if uv_w else None, 'uvl': round(uv_l, 4) if uv_l else None,
               'stretch': round((asz[0] / m_u) / (asz[1] / m_v), 3) if m_u and m_v else None,
               'mir': round(mir_a / A, 3), 'vz': round(vdir.normalized().z, 3) if vdir.length > 1e-12 else None,
               'gap': round(offs[0] * 1000, 2) if offs[0] is not None else None,
               'gmin': round(min(gaps) * 1000, 2) if gaps else None, 'host': host, 'hmat': None,
               'margin_mm': None, 'c2e': None, 'inside': None, 'closed': closed, 'ends': [], 'joins': [],
               '_ends': ends, 'twin': False}
        if host is not None and reg[host]['basis'] is not None:
            rg = reg[host]
            h1, h2 = rg['basis']
            rec['hmat'] = max(rg['mats'].items(), key=lambda kv: kv[1])[0] if rg['mats'] else None
            rec['inside'] = all(h == host for h in hosts[1:]) if len(hosts) > 1 else None
            segs = region_boundary(host)
            if segs:
                seg2 = [((a.dot(h1), a.dot(h2)), (b.dot(h1), b.dot(h2))) for a, b in segs]
                ax3 = t1 * math.cos(math.radians(ang)) + t2 * math.sin(math.radians(ang))
                bx3 = n.cross(ax3)
                rc = t1 * c2[0] + t2 * c2[1] + n * C.dot(n)
                out8 = [rc + ax3 * (sa * L / 2) + bx3 * (sb * W / 2) for sa, sb in
                        ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1))]
                vp = [(co.dot(h1), co.dot(h2)) for co in out8]
                rec['margin_mm'] = round(1000 * min(seg_dist2d(q_, a, b) for a, b in seg2 for q_ in vp), 1)
                rec['c2e'] = round(min(seg_dist2d((C.dot(h1), C.dot(h2)), a, b) for a, b in seg2), 4)
        decals.append(rec); piece_of.append(p)
    log('decal pieces', len(decals))

    # what each open strip end runs into: another strip, the face edge, or nothing
    sidx = [i for i, d in enumerate(decals) if d['_ends']]
    if sidx:
        allv, owner = [], []
        for i, d in enumerate(decals):
            if d['strip']:
                for co in {v.index: v.co.copy() for f in pieces[piece_of[i]] for v in f.verts}.values():
                    allv.append(co); owner.append(i)
        kd_s = KDTree(len(allv))
        for i, co in enumerate(allv):
            kd_s.insert(co, i)
        kd_s.balance()
        for i in sidx:
            d = decals[i]
            n = Vector(d['n']); w_ = d['uvw'] or d['W']
            for P in d['_ends']:
                other = [(dist, owner[j]) for co, j, dist in kd_s.find_n(P, 64) if owner[j] != i]
                g, fi = cast_offset(P, n)
                to_edge = None
                if fi is not None:
                    segs = region_boundary(region[fi])
                    to_edge = min(pseg3(P - n * g, a, b) for a, b in segs) if segs else None
                if other and min(other)[0] < 1.5 * w_:
                    d['ends'].append('joins_strip'); d['joins'].append(min(other)[1])
                elif to_edge is not None and to_edge < w_ + 0.003:
                    d['ends'].append('at_face_edge')
                else:
                    d['ends'].append('free' if fi is not None else 'off_surface')
    for d in decals:
        del d['_ends']

    # mirror twins: the same piece and size at the mirrored spot across the block's X, Y or Z centre plane
    TOL = 0.012 if grid == 'large' else 0.004
    if decals:
        kd = KDTree(len(decals))
        for i, d in enumerate(decals):
            kd.insert(Vector(d['c']), i)
        kd.balance()

        def dkey(d):
            return d['mat'], d['pid'], round(d['L'] / TOL / 2), round(d['W'] / TOL / 2)
        for ax in range(3):
            for d in decals:
                P = Vector(d['c']); P[ax] = -P[ax]
                if any(dkey(decals[j]) == dkey(d) and decals[j] is not d for co, j, dist in kd.find_range(P, TOL)):
                    d['twin'] = True

    # ---------------------------------------------------------------- visible surface
    # A point is visible when any of 162 directions (icosphere vertices) in front of its face escapes the model.
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    DIRS = [v.co.normalized() for v in bm.verts]; bm.free()
    allv = [v.co for v in base_bm.verts]
    mn = Vector((min(v.x for v in allv), min(v.y for v in allv), min(v.z for v in allv))) if allv else Vector()
    mx = Vector((max(v.x for v in allv), max(v.y for v in allv), max(v.z for v in allv))) if allv else Vector()
    RAY = max((mx - mn).length * 1.5, 1.0)
    rnd = random.Random(int(arg(argv, '--seed', '7')))

    def visible(p, n):
        p = p + n * 0.002
        for d in DIRS:
            if d.dot(n) > 0.05 and bvh.ray_cast(p, d, RAY)[0] is None:
                return True
        return False

    def tri_sample(t):
        a, b = rnd.random(), rnd.random()
        if a + b > 1:
            a, b = 1 - a, 1 - b
        return t[0] + (t[1] - t[0]) * a + (t[2] - t[0]) * b

    def tris_of(bmx):
        out = []
        for lt in bmx.calc_loop_triangles():
            t = [l.vert.co for l in lt]
            a = (t[1] - t[0]).cross(t[2] - t[0]).length / 2
            if a > 1e-10:
                out.append((t, a, lt[0].face.index))
        return out

    btris = tris_of(base_bm)
    tot_area = sum(a for _, a, _ in btris)
    N = int(min(max(tot_area * 150, 20000), 80000))
    vis_mat = defaultdict(int)
    nvis = 0
    for t, a, fi in rnd.choices(btris, weights=[a for _, a, _ in btris], k=N) if btris else []:
        if visible(tri_sample(t), fnorm[fi]):
            vis_mat[MATS[fmat[fi]]] += 1; nvis += 1
    per = tot_area / N if N else 0
    # big faces: their own samples, visible when at least half the samples are
    BIG_W = 0.25 if grid == 'large' else 0.05
    big_tris = defaultdict(list)
    for t, a, fi in btris:
        if reg[region[fi]]['basis'] is not None and reg[region[fi]]['W'] >= BIG_W:
            big_tris[region[fi]].append((t, a))
    host_n, host_a = Counter(), defaultdict(float)
    for d in decals:
        if d['host'] is not None and not d['strip']:
            host_n[d['host']] += 1; host_a[d['host']] += d['area']
    big_faces = []
    for r, tl in big_tris.items():
        k = 8
        hits = sum(1 for t, a in rnd.choices(tl, weights=[a for _, a in tl], k=k) if visible(tri_sample(t), reg[r]['n']))
        rg = reg[r]
        big_faces.append({'area': round(rg['area'], 4), 'L': round(rg['L'], 3), 'W': round(rg['W'], 3),
                          'mat': max(rg['mats'].items(), key=lambda kv: kv[1])[0], 'vis': hits / k,
                          'n_dec': host_n[r], 'dec_area': round(host_a[r], 5)})
    # decals: visible area, and the base material under each visible sample
    dtris = tris_of(dec_bm)
    dtot = sum(a for _, a, _ in dtris)
    ND = int(min(max(dtot * 400, 5000), 40000)) if dtris else 0
    dvis = 0
    dhost = defaultdict(int)
    dfn = [f.normal.copy() for f in dec_bm.faces]
    for t, a, fi in rnd.choices(dtris, weights=[a for _, a, _ in dtris], k=ND) if dtris else []:
        n = dfn[fi]
        if n.length < 0.5:
            continue
        p = tri_sample(t)
        if not visible(p, n):
            continue
        dvis += 1
        h = bvh.ray_cast(p + n * 0.02, -n, 0.05)
        dhost[family(MATS[fmat[h[2]]]) if h[0] is not None else 'none'] += 1
    dper = dtot / ND if ND else 0
    log('visible %.1f of %.1f m2' % (nvis * per, tot_area))

    S = {'name': name, 'source': source, 'grid': grid, 'cell_m': CELL,
         'bbox_size_m': [round(x, 3) for x in (mx - mn)],
         'materials': {m: {'area': round(a, 5), 'upm_hist': {str(k): round(v, 5) for k, v in upm_hist[m].items()},
                           'aniso': round(wquant(aniso[m], 0.5), 3) if aniso[m] else None,
                           'tech': catalog.get(game_name(m), {}).get('tech', 'unknown')}
                       for m, a in mat_area.items()},
         'bevels': bevels, 'bevel_len_m': round(bev_len, 3), 'unbevelled_len_m': round(unbev, 3),
         'shading': {k: [round(v[0], 3), round(v[1], 3)] for k, v in sh.items()},
         'mat_border': {k: round(v, 3) for k, v in border.items()},
         'empties': empties, 'decals': decals, 'big_faces': big_faces,
         'vis': {'samples': N, 'base_area': round(tot_area, 3), 'visible_area': round(nvis * per, 3),
                 'by_mat': {m: round(c * per, 4) for m, c in vis_mat.items()},
                 'decal_area': round(dtot, 4), 'decal_visible': round(dvis * dper, 4),
                 'decal_by_host_family': {k: round(v * dper, 4) for k, v in dhost.items()}}}
    for _, me, _ in meshes:
        bpy.data.meshes.remove(me)
    return S


def report(S, argv):
    era = arg(argv, '--era', 'newer')
    rules = load_rules(arg(argv, '--rules'))
    M = measures(S)
    lines = []

    def out(s=''):
        lines.append(s); print(s)
    out()
    compare(S, M, rules, era, out)
    od = arg(argv, '--out')
    if od:
        with open(os.path.join(od, S['name'] + '.report.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')


def main():
    blender = 'bpy' in sys.modules or os.path.basename(sys.executable).lower().startswith('blender')
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    if '--build-rules' in argv:
        build_rules(arg(argv, '--build-rules'), arg(argv, '--meta'),
                    arg(argv, '--rules-out', os.path.join(REFS, 'keen-rules.json')))
        return
    if '--compare' in argv:
        report(json.load(open(arg(argv, '--compare'), encoding='utf-8')), argv)
        return
    if not blender:
        raise SystemExit(__doc__)
    S = survey(argv)
    od = arg(argv, '--out')
    if od:
        os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, S['name'] + '.survey.json'), 'w', encoding='utf-8') as f:
            json.dump(S, f)
    if '--survey-only' in argv:
        return
    report(S, argv)


if __name__ == '__main__':
    main()
