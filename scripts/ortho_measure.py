"""Measured silhouettes: turn straight-on reference views into scaled masks, then score a model against them.

Two commands, both in a background Blender (it ships numpy; nothing to install):

    blender -b --factory-startup --python ortho_measure.py -- sheet <sheet.json>
    blender -b <copy>.blend --python ortho_measure.py -- check <sheet.json> [<label>]

or inside a live Blender (the MCP); it renders in a temporary scene and leaves the user's scenes as they were:

    ns = {"__name__": "ortho_measure"}; exec(open(r"<path>\\ortho_measure.py").read(), ns)
    ns["check"](r"<sheet.json>", "blockout2")

sheet.json (paths relative to it; axes are Blender world axes; a view's axis is the side its camera sits on):

    {"bounds": {"min": [x, y, z], "max": [x, y, z]},   the model's planned outer extents (m)
     "ppm": 100, "margin": 0.5,                         canvas pixels per metre; canvas margin round the bounds (m)
     "views": {"front": {"image": "front.png", "axis": "-Y"},
               "side":  {"image": "side.png", "axis": "+X", "ignore": [[0.0, 0.85, 0.25, 1.0]]},
               "top":   {"image": "top.png", "axis": "+Z"}},
     "check": {"collections": ["Main (MyBlock)"], "tolerance_cm": 5, "exclude": ["Plinth*"],
               "accept": [{"view": "front", "h": [1.0, 1.4], "v": [2.0, 2.3], "why": "user: the art is wrong here"}]}}

Optional per view: "rotate" (degrees counter-clockwise, in 90 steps: a top view drawn with the front pointing
left), "flip" (mirror it), "threshold" (background colour distance 0-1, default 0.12), "keep" ("largest", the
default, keeps only the biggest connected piece, so loose arrows and numbers drop out; "all"),
"ignore" (rectangles to blank, image fractions x0 y0 x1 y1 from the top left of the image as given, before any
rotate: labels, dimension lines, shadows),
"fit" ({"h": [lo, hi], "v": [lo, hi]}: the world range the silhouette's box maps to, when a view shows less than
the bounds). Image axes: -Y right +X up +Z; +Y right -X; +X right +Y; -X right -Y; +Z right +X up +Y; -Z right +X
up -Y. "accept" ranges are world metres along the view's right (h) and up (v) axes. "exclude": object name
patterns left out of the check, for parts the art does not show (a block-size base under a round one), with
the art's matching part blanked by "ignore". "shadow" (per view, e.g. 0.55): also treat a drop shadow, the
background darkened evenly down to that fraction, as background; it relies on the art's ink outlines to stop
at the object and leaves dark shadows in. Art without shadows, or cut out to transparency, beats it. Top level:
"near_cm" (default 40), how far apart two views' edges may lie and still be reported as one feature drawn twice.

Landmarks, for details inside the outline (top level, a list):

     "landmarks": [{"name": "rear hatch", "view": "back", "h": [-0.8, 0.6], "v": [0.3, 1.6],
                    "parts": ["RearHatch*"], "snap_cm": 15, "near_cm": 30, "tolerance_cm": 5}]

h and v: a rough box in world metres along the view's right and up axes, read off grid_<view>.png. sheet moves
each edge to the nearest clear line in the art within snap_cm (0: keep the box as written). check measures the
mesh pieces (connected islands) of the objects matching "parts" that come within near_cm of the art's box, so a
detail inside a joined mesh (a decal sheet) is measured alone. "tolerance_cm" defaults to the check's.

sheet writes <sheet dir>/measure/: mask_<view>.png and ref_<view>.png on a metric canvas, grid_<view>.png (a
0.5 m grid labelled each metre, landmark boxes: grey as written, cyan snapped), edges_<view>.png where views
disagree, pair_<view>_<view>.png per mirror pair, sheet_report.md (stretch per view, mirror pairs, shared edges,
landmarks) and sheet_data.json.
check writes <sheet dir>/measure/check_<label>/: overlay_<view>.png (grey both, red model only, blue reference
only, yellow accepted), overlays.png (the views side by side, in sheet order), board_<view>.png (the art and the
model lit, each part its own colour, side by side at one scale with the grid), detail_<n>.png (each landmark
enlarged, art and model, a finer grid; cyan the art's box, orange the model's), report.md and report.json.
"""
import bpy, sys, os, json, math, time, fnmatch, traceback
from collections import Counter
import numpy as np
from mathutils import Vector, Matrix

AXES = {"-Y": ("x", 1, "z", 1), "+Y": ("x", -1, "z", 1), "+X": ("y", 1, "z", 1), "-X": ("y", -1, "z", 1),
        "+Z": ("x", 1, "y", 1), "-Z": ("x", 1, "y", -1)}          # camera side: right axis and sign, up axis and sign
PAIRS = (("-Y", "+Y"), ("+X", "-X"), ("+Z", "-Z"))
I3 = {"x": 0, "y": 1, "z": 2}
UNIT = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}
STRETCH_FLAG = 0.03


class Frame:
    """A pixel grid over two world axes, rows counted from the bottom: pixel (row i, column j) is centred at
    h = h0 + hs (j + 0.5) / ppm, v = v0 + vs (i + 0.5) / ppm."""
    KEYS = ("ha", "hs", "va", "vs", "h0", "v0", "w", "h", "ppm")

    def __init__(self, ha, hs, va, vs, h0, v0, w, h, ppm):
        self.ha, self.hs, self.va, self.vs = ha, hs, va, vs
        self.h0, self.v0, self.w, self.h, self.ppm = float(h0), float(v0), int(w), int(h), float(ppm)

    def dict(self):
        return {k: getattr(self, k) for k in self.KEYS}

    def hw(self, j):
        return self.h0 + self.hs * (np.asarray(j, float) + 0.5) / self.ppm

    def vw(self, i):
        return self.v0 + self.vs * (np.asarray(i, float) + 0.5) / self.ppm

    def col(self, h):
        """World h as a continuous column, pixel edges on integers; row(v) likewise, h_at and v_at back."""
        return (h - self.h0) * self.hs * self.ppm

    def row(self, v):
        return (v - self.v0) * self.vs * self.ppm

    def h_at(self, c):
        return self.h0 + self.hs * c / self.ppm

    def v_at(self, r):
        return self.v0 + self.vs * r / self.ppm

    def where(self, j0, j1, i0, i1):
        h = sorted((self.h0 + self.hs * j0 / self.ppm, self.h0 + self.hs * (j1 + 1) / self.ppm))
        v = sorted((self.v0 + self.vs * i0 / self.ppm, self.v0 + self.vs * (i1 + 1) / self.ppm))
        return "%s %.2f..%.2f, %s %.2f..%.2f" % (self.ha, h[0], h[1], self.va, v[0], v[1]), h, v


def canvas(axis, lo, hi, margin, ppm):
    ha, hs, va, vs = AXES[axis]
    a, b = I3[ha], I3[va]
    return Frame(ha, hs, va, vs, lo[a] - margin if hs > 0 else hi[a] + margin,
                 lo[b] - margin if vs > 0 else hi[b] + margin,
                 round((hi[a] - lo[a] + 2 * margin) * ppm), round((hi[b] - lo[b] + 2 * margin) * ppm), ppm)


def remap(src, sf, df):
    """Nearest-pixel copy of src (frame sf) into frame df over the same two world axes; outside src reads 0."""
    assert (sf.ha, sf.va) == (df.ha, df.va), (sf.ha, sf.va, df.ha, df.va)
    j = np.floor((df.hw(np.arange(df.w)) - sf.h0) * sf.hs * sf.ppm).astype(int)
    i = np.floor((df.vw(np.arange(df.h)) - sf.v0) * sf.vs * sf.ppm).astype(int)
    out = src[np.clip(i, 0, sf.h - 1)][:, np.clip(j, 0, sf.w - 1)]
    out[(i < 0) | (i >= sf.h)] = 0
    out[:, (j < 0) | (j >= sf.w)] = 0
    return out


def load(path):
    """RGBA float array, rows from the bottom, raw values (no colour transform)."""
    img = bpy.data.images.load(os.path.abspath(path), check_existing=False)
    try:
        img.colorspace_settings.name = "Non-Color"
    except TypeError:
        pass
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(h, w, 4)


def save(arr, path):
    arr = np.asarray(arr, np.float32)
    if arr.ndim == 2:
        arr = np.dstack([arr, arr, arr])
    if arr.shape[2] == 3:
        arr = np.dstack([arr, np.ones(arr.shape[:2], np.float32)])
    h, w = arr.shape[:2]
    img = bpy.data.images.new("om_out", w, h, alpha=True)
    try:
        img.colorspace_settings.name = "Non-Color"
    except TypeError:
        pass
    img.pixels.foreach_set(np.ascontiguousarray(np.clip(arr, 0, 1)).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def run_fill(reach, cand):
    """Every run of cand along a row that touches reach becomes reached."""
    h, w = cand.shape
    c = cand.ravel()
    s = c.copy()
    s[1:] &= ~c[:-1]
    s = s.reshape(h, w)
    s[:, 0] = cand[:, 0]
    rid = np.cumsum(s.ravel()) * c
    hit = np.zeros(int(rid.max()) + 1, bool)
    hit[rid[reach.ravel() & c]] = True
    hit[0] = False
    return hit[rid].reshape(h, w)


def border_fill(cand):
    """The cand pixels connected to the image border through cand."""
    reach = np.zeros_like(cand)
    for sl in ((0, slice(None)), (-1, slice(None)), (slice(None), 0), (slice(None), -1)):
        reach[sl] = cand[sl]
    n = -1
    while reach.sum() != n:
        n = reach.sum()
        reach = run_fill(reach, cand)
        reach = run_fill(reach.T, cand.T).T
    return reach


def silhouette(rgba, cfg):
    """The object's pixels: alpha when the image has transparency, else everything the border's background
    colour cannot reach (so light patches inside the object stay solid)."""
    a = rgba[..., 3]
    if (a < 0.5).mean() > 0.01:
        return a >= 0.5
    rgb = rgba[..., :3]
    bg = np.median(np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]), axis=0)
    cand = np.abs(rgb - bg).max(axis=2) < cfg.get("threshold", 0.12)
    if cfg.get("shadow"):                    # a drop shadow: the background darkened evenly, a touch warmer
        r = rgb / np.maximum(bg, 1e-3)
        cand |= ((r.min(axis=2) >= cfg["shadow"]) & (r.max(axis=2) - r.min(axis=2) <= 0.12)
                 & (r[..., 2] <= r[..., 0] + 0.01))
    return ~border_fill(cand)


def bilinear(src, x, y):
    """src (rows from the bottom) sampled at continuous columns x (1D) and rows y (1D), integers on pixel edges;
    outside the image reads 0."""
    h, w = src.shape[:2]
    fx, fy = np.asarray(x) - 0.5, np.asarray(y) - 0.5
    x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = (fx - x0)[None, :], (fy - y0)[:, None]
    if src.ndim == 3:
        tx, ty = tx[..., None], ty[..., None]

    def at(yy, xx):
        v = src[np.clip(yy, 0, h - 1)][:, np.clip(xx, 0, w - 1)]
        ok = ((yy >= 0) & (yy < h))[:, None] & ((xx >= 0) & (xx < w))[None, :]
        return v * (ok[..., None] if src.ndim == 3 else ok)
    return ((at(y0, x0) * (1 - tx) + at(y0, x0 + 1) * tx) * (1 - ty)
            + (at(y0 + 1, x0) * (1 - tx) + at(y0 + 1, x0 + 1) * tx) * ty)


def _morph(m, grow):
    p, (h, w), out = np.pad(m, 1), m.shape, m.copy()
    for dy in range(3):
        for dx in range(3):
            if grow:
                out |= p[dy:dy + h, dx:dx + w]
            else:
                out &= p[dy:dy + h, dx:dx + w]
    return out


def components(m):
    """The connected pieces of a bool mask (8 neighbours), each as an array of flat pixel indices."""
    W = m.shape[1]
    todo = set(np.flatnonzero(m).tolist())
    while todo:
        k = todo.pop()
        comp, stack = [k], [k]
        while stack:
            k = stack.pop()
            x = k % W
            nb = [k - W, k + W]
            if x > 0:
                nb += [k - 1, k - W - 1, k + W - 1]
            if x < W - 1:
                nb += [k + 1, k - W + 1, k + W + 1]
            for q in nb:
                if q in todo:
                    todo.remove(q)
                    comp.append(q)
                    stack.append(q)
        yield np.array(comp)


def regions(diff, fr, min_cm=0.0, clean=False):
    """Connected regions of diff, deepest first. depth_cm: the most pixels across the region's short direction;
    mean_cm: area over length. clean: drop slivers 2 px thin first (anti-aliased edges)."""
    m = _morph(_morph(diff, False), True) & diff if clean else diff
    W, out = m.shape[1], []
    for comp in components(m):
        ys, xs = comp // W, comp % W
        j0, j1, i0, i1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
        cnt = np.bincount(xs - j0) if j1 - j0 >= i1 - i0 else np.bincount(ys - i0)
        depth = cnt.max() / fr.ppm * 100
        if depth < min_cm:
            continue
        k = int(np.argmin((xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2))
        where, h, v = fr.where(j0, j1, i0, i1)
        out.append(dict(where=where, ha=fr.ha, va=fr.va, h=[round(t, 3) for t in h], v=[round(t, 3) for t in v],
                        depth_cm=round(depth, 1),
                        mean_cm=round(len(comp) / (max(j1 - j0, i1 - i0) + 1) / fr.ppm * 100, 1),
                        area_m2=round(len(comp) / fr.ppm ** 2, 4), px=(int(xs[k]), int(ys[k])),
                        box=(j0, j1, i0, i1)))
    out.sort(key=lambda r: -r["depth_cm"])
    return out


def bands(regs, ppm):
    """One row per cause: regions of one view and kind with the same depth that line up across or along the view
    (a roof edge split by the towers on it) merge, with their pieces counted."""
    out, eps = [], 1.5 / ppm
    for g in regs:
        for m in out:
            if (m["view"], m["kind"]) != (g["view"], g["kind"]) or abs(m["depth_cm"] - g["depth_cm"]) > 1:
                continue
            same_v = abs(m["v"][0] - g["v"][0]) <= eps and abs(m["v"][1] - g["v"][1]) <= eps
            same_h = abs(m["h"][0] - g["h"][0]) <= eps and abs(m["h"][1] - g["h"][1]) <= eps
            if not (same_v or same_h):
                continue
            k = "h" if same_v else "v"
            m[k] = [min(m[k][0], g[k][0]), max(m[k][1], g[k][1])]
            m["pieces"] += 1
            m["area_m2"] = round(m["area_m2"] + g["area_m2"], 4)
            m["parts"] |= {g["part"]} - {None}
            break
        else:
            out.append(dict(g, pieces=1, parts={g["part"]} - {None}))
    for m in out:
        m["where"] = "%s %.2f..%.2f, %s %.2f..%.2f%s" % (m["ha"], m["h"][0], m["h"][1], m["va"], m["v"][0], m["v"][1],
                                                       " (%d pieces)" % m["pieces"] if m["pieces"] > 1 else "")
        m["part"] = ", ".join(sorted(m.pop("parts"))) or None
    return out


def edges(M, fr, axis, step_m=0.15):
    """Places along a world axis where the silhouette's width jumps: [(coordinate, width change in m)], in
    increasing coordinate; a jump is at least step_m or 8% of the widest point, measured across 4 px."""
    if fr.va == axis:
        p, c = M.sum(1) / fr.ppm, fr.vw(np.arange(fr.h))
    else:
        p, c = M.sum(0) / fr.ppm, fr.hw(np.arange(fr.w))
    o = np.argsort(c)
    p, c = p[o], c[o]
    d = np.zeros_like(p)
    d[2:-2] = p[4:] - p[:-4]
    a, thr, out, k = np.abs(d), max(step_m, 0.08 * p.max()), [], 0
    while k < len(d):
        if a[k] >= thr and a[k] == a[max(0, k - 6):k + 7].max():
            k2 = k
            while k2 + 1 < len(d) and a[k2 + 1] == a[k]:
                k2 += 1
            out.append((float((c[k] + c[k2]) / 2), float(d[k])))
            k = k2 + 7
        else:
            k += 1
    return out


def near_misses(ea, eb, tol_m, near_m):
    """Mutually nearest edges of the same kind (both widening or both narrowing) that lie more than tol_m and at
    most near_m apart: [(a, change a, b, change b, distance)]."""
    out = []
    for ca, da in ea:
        cand = [(abs(cb - ca), cb, db) for cb, db in eb if cb is not None and da * db > 0]
        if not cand:
            continue
        dist, cb, db = min(cand)
        if min((abs(c2 - cb), c2) for c2, d2 in ea if d2 * db > 0)[1] == ca and tol_m < dist <= near_m:
            out.append((ca, da, cb, db, dist))
    return out


def line(img, fr, axis, coord, col):
    if fr.va == axis:
        i = int((coord - fr.v0) * fr.vs * fr.ppm)
        img[max(0, i - 1):i + 2, :] = col
    else:
        j = int((coord - fr.h0) * fr.hs * fr.ppm)
        img[:, max(0, j - 1):j + 2] = col


FONT = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111",
        "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001001001001",
        "8": "111101111101111", "9": "111101111001111", "-": "000000111000000", ".": "000000000000010"}
GRID, CYAN, ORANGE = np.array((0.85, 0.9, 0.3), np.float32), (0.0, 0.85, 1.0), (1.0, 0.45, 0.0)


def label(img, j, top, s, col, k=2):
    """s in a 3x5 pixel font, k times enlarged, on a dark box; j: its left column, top: the row of its top edge
    (rows count from the bottom, as everywhere here)."""
    H, W = img.shape[:2]
    j, top = int(min(max(j, 0), W - 1)), int(min(max(top, 7 * k - 1), H - 1))
    img[top - 7 * k + 1:top + 1, j:j + (4 * len(s) + 1) * k] = 0.05
    for n, ch in enumerate(s):
        g = FONT.get(ch, "")
        for r in range(5):
            for c in range(3):
                if g[r * 3 + c:r * 3 + c + 1] == "1":
                    y, x = top - (r + 2) * k + 1, j + (n * 4 + c + 1) * k
                    img[y:y + k, x:x + k] = col


def rect(img, fr, h, v, col, t=1):
    """The outline of the world box h, v ([lo, hi] each), t px thick. Returns its left column and top row."""
    H, W = img.shape[:2]
    j0, j1 = sorted(int(round(min(max(fr.col(x), 0), W))) for x in h)
    i0, i1 = sorted(int(round(min(max(fr.row(x), 0), H))) for x in v)
    for sl in ((slice(i0, i1), slice(j0, j0 + t)), (slice(i0, i1), slice(max(j0, j1 - t), j1)),
               (slice(i0, i0 + t), slice(j0, j1)), (slice(max(i0, i1 - t), i1), slice(j0, j1))):
        img[sl] = col
    return j0, i1


def grid(img, fr, step, every=2, k=2):
    """Lines every step metres along both axes, labelled every `every` lines, so positions read off the picture."""
    H, W = img.shape[:2]
    for n, at, pos, across in ((W, fr.hw, fr.col, True), (H, fr.vw, fr.row, False)):
        lo, hi = sorted((float(at(0)), float(at(n - 1))))
        for m in range(int(math.ceil(lo / step - 1e-6)), int(math.floor(hi / step + 1e-6)) + 1):
            p = int(pos(m * step))
            if not 0 <= p < n:
                continue
            sl = (slice(None), p) if across else (p, slice(None))
            img[sl] = img[sl] * 0.45 + GRID * 0.55
            if m % every == 0:
                s = "%g" % round(m * step, 3)
                label(img, *((p + 2, 7 * k - 1) if across else (1, p + 7 * k)), s, GRID, k)


def draw_marks(img, fr, g, t=2, k=2):
    """A landmark on a picture: cyan the art's box, orange the model's, its number above the art's box."""
    if g.get("model_h"):
        rect(img, fr, g["model_h"], g["model_v"], ORANGE, t)
    j, top = rect(img, fr, g["h"], g["v"], CYAN, t)
    label(img, j, top + 7 * k - 1, str(g["n"]), CYAN, k)


def box_text(fr, h, v):
    return "%s %.2f..%.2f, %s %.2f..%.2f" % (fr.ha, h[0], h[1], fr.va, v[0], v[1])


def snap(ref, fr, h, v, reach_m):
    """Each edge of the world box (h, v) moved to the nearest clear straight line in the picture within reach_m
    (at most 40% of the box across): a peak of the brightness change across the edge, averaged along the middle
    70% of the edge and smoothed over 3 px so an ink line reads as one line, at least 35% of the window's strongest
    and 1.5x its median. An edge with no such line stays where it was written. Returns sorted world h and v,
    moves in cm, unclear edges."""
    L = ref[..., :3] @ np.array((0.3, 0.59, 0.11), np.float32)
    gx, gy = np.zeros_like(L), np.zeros_like(L)
    gx[:, 1:-1], gy[1:-1] = np.abs(L[:, 2:] - L[:, :-2]), np.abs(L[2:] - L[:-2])
    px = {"h": sorted((fr.col(h[0]), fr.col(h[1]))), "v": sorted((fr.row(v[0]), fr.row(v[1])))}
    new, weak = {"h": list(px["h"]), "v": list(px["v"])}, []
    for k, G, o in (("h", gx, "v"), ("v", gy.T, "h")):
        a0, a1 = px[o]
        span = slice(max(0, int(a0 + 0.15 * (a1 - a0))), max(1, int(math.ceil(a1 - 0.15 * (a1 - a0)))))
        reach = min(reach_m * fr.ppm, 0.4 * (px[k][1] - px[k][0]))
        for e in (0, 1):
            c0 = max(1, int(px[k][e] - reach))
            c1 = min(G.shape[1] - 2, int(math.ceil(px[k][e] + reach)))
            prof = G[span, c0:c1 + 1].mean(0) if c1 - c0 >= 2 else np.zeros(1)
            prof = np.convolve(prof, np.ones(3) / 3, "same")
            floor = max(0.35 * prof.max(), 1.5 * np.median(prof), 0.02)   # the nearest clear line, not the
            pk = [q for q in range(len(prof)) if prof[q] >= floor               # strongest: an outline in reach
                  and prof[q] >= prof[max(0, q - 1)] and prof[q] >= prof[min(len(prof) - 1, q + 1)]]  # outshines
            if not pk:                                                          # a panel edge
                sign = fr.hs if k == "h" else fr.vs
                weak.append("%s %s" % (fr.ha if k == "h" else fr.va, ("min", "max")[e if sign > 0 else 1 - e]))
                continue
            m = min(pk, key=lambda q: abs(c0 + q + 0.5 - px[k][e]))
            off = 0.0                                  # the peak's centre between pixels, from a parabola
            if 0 < m < len(prof) - 1 and prof[m - 1] - 2 * prof[m] + prof[m + 1] < 0:
                off = float(np.clip(0.5 * (prof[m - 1] - prof[m + 1]) / (prof[m - 1] - 2 * prof[m] + prof[m + 1]),
                                    -0.5, 0.5))
            new[k][e] = c0 + m + 0.5 + off
    wh = sorted(float(fr.h_at(c)) for c in new["h"])
    wv = sorted(float(fr.v_at(r)) for r in new["v"])
    moved = {"h": [round((a - b) * 100, 1) for a, b in zip(wh, sorted(h))],
             "v": [round((a - b) * 100, 1) for a, b in zip(wv, sorted(v))]}
    return dict(h=[round(x, 3) for x in wh], v=[round(x, 3) for x in wv], moved=moved, weak=weak)


def islands(n, E):
    """Connected pieces of a mesh: a label per vertex, shared by the vertices joined through edges E (m x 2)."""
    lab = np.arange(n)
    while True:
        new = lab.copy()
        m = np.minimum(lab[E[:, 0]], lab[E[:, 1]])
        np.minimum.at(new, E[:, 0], m)
        np.minimum.at(new, E[:, 1], m)
        new = new[new]
        if (new == lab).all():
            return lab
        lab = new


def part_box(objs, pats, dg, fr, h, v, near):
    """World range along the frame's h and v axes of the matching objects' mesh pieces (connected islands) that
    come within near metres of the art's box h, v, so one detail inside a joined mesh (a decal sheet, a panel with
    its frame) is measured alone; when no piece comes that near, all of them. Returns h, v, pieces used, pieces
    in all, and whether none came near."""
    boxes = []
    for o in objs:
        if o.type not in {"MESH", "CURVE", "SURFACE", "FONT", "META"} or not any(
                fnmatch.fnmatchcase(o.name, p) for p in pats):
            continue
        oe = o.evaluated_get(dg)
        me = oe.to_mesh()
        try:
            if me is None or not len(me.vertices):
                continue
            co = np.empty(len(me.vertices) * 3)
            me.vertices.foreach_get("co", co)
            mw = np.array(oe.matrix_world)
            P = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
            E = np.empty(len(me.edges) * 2, np.int64)
            me.edges.foreach_get("vertices", E)
        finally:
            oe.to_mesh_clear()
        _, inv = np.unique(islands(len(P), E.reshape(-1, 2)), return_inverse=True)
        bx = np.empty((inv.max() + 1, 4))
        bx[:, 0::2], bx[:, 1::2] = np.inf, -np.inf
        for c, x in ((0, P[:, I3[fr.ha]]), (2, P[:, I3[fr.va]])):
            lo, hi = bx[:, c].copy(), bx[:, c + 1].copy()
            np.minimum.at(lo, inv, x)
            np.maximum.at(hi, inv, x)
            bx[:, c], bx[:, c + 1] = lo, hi
        boxes.append(bx)
    if not boxes:
        return None, None, 0, 0, False
    B = np.vstack(boxes)
    sel = ((B[:, 1] >= h[0] - near) & (B[:, 0] <= h[1] + near) & (B[:, 3] >= v[0] - near) & (B[:, 2] <= v[1] + near))
    far = not sel.any()
    if far:
        sel[:] = True
    S = B[sel]
    return ([round(float(S[:, 0].min()), 3), round(float(S[:, 1].max()), 3)],
            [round(float(S[:, 2].min()), 3), round(float(S[:, 3].max()), 3)], int(sel.sum()), len(B), far)


def crop(fr, h, v, px=400):
    """A frame over the world box h, v plus padding, enlarged a whole number of times to about px across, and a
    grid step that gives at most 12 lines."""
    pad = max(0.2, 0.3 * max(h[1] - h[0], v[1] - v[0]))
    sh, sv = h[1] - h[0] + 2 * pad, v[1] - v[0] + 2 * pad
    k = max(1, min(8, int(px / (max(sh, sv) * fr.ppm))))
    p2 = fr.ppm * k
    cf = Frame(fr.ha, fr.hs, fr.va, fr.vs, h[0] - pad if fr.hs > 0 else h[1] + pad,
               v[0] - pad if fr.vs > 0 else v[1] + pad, round(sh * p2), round(sv * p2), p2)
    step = next((s for s in (0.05, 0.1, 0.25, 0.5, 1.0) if max(sh, sv) / s <= 12), 2.0)
    return cf, step


def read_sheet(path):
    path = os.path.abspath(path)
    with open(path, encoding="utf-8") as f:
        return json.load(f), os.path.dirname(path)


def table(head, rows):
    return ("| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n"
            + "".join("| " + " | ".join(str(c) for c in r) + " |\n" for r in rows))


def tint(ref, layers):
    """The reference picture dimmed, with (mask, colour or None for a light wash) layers painted over it."""
    img = ref[..., :3] * 0.4
    for m, col in layers:
        img[m] = img[m] * 0.5 + 0.45 if col is None else col
    return img


def sheet(path):
    S, base = read_sheet(path)
    lo, hi = S["bounds"]["min"], S["bounds"]["max"]
    ppm, margin = S.get("ppm", 100), S.get("margin", 0.5)
    tol = float(S.get("check", {}).get("tolerance_cm", 5))
    out = os.path.join(base, "measure")
    os.makedirs(out, exist_ok=True)
    frames, masks, refs, data, rows = {}, {}, {}, {}, []
    for name, v in S["views"].items():
        rgba = load(os.path.join(base, v["image"]))
        m = silhouette(rgba, v)
        H, W = m.shape
        for x0, y0, x1, y1 in v.get("ignore", []):
            m[int(H * (1 - y1)):math.ceil(H * (1 - y0)), int(W * x0):math.ceil(W * x1)] = False
        k = int(v.get("rotate", 0)) // 90 % 4
        if k:                                                  # counter-clockwise as seen; rows run from the bottom
            rgba, m = np.rot90(rgba, -k), np.rot90(m, -k)
        if v.get("flip"):
            rgba, m = rgba[:, ::-1], m[:, ::-1]
        if v.get("keep", "largest") == "largest" and m.any():
            big = max(components(m), key=len)
            m = np.zeros(m.shape, bool)
            m.ravel()[big] = True
        if not m.any():
            raise RuntimeError("%s: no silhouette found; check threshold and ignore" % name)
        r, c = np.flatnonzero(m.any(1)), np.flatnonzero(m.any(0))
        r0, r1, c0, c1 = r[0], r[-1] + 1, c[0], c[-1] + 1
        fr = canvas(v["axis"], lo, hi, margin, ppm)
        fit = v.get("fit", {})
        fh = fit.get("h", [lo[I3[fr.ha]], hi[I3[fr.ha]]])
        fv = fit.get("v", [lo[I3[fr.va]], hi[I3[fr.va]]])
        left, bottom = (fh[0] if fr.hs > 0 else fh[1]), (fv[0] if fr.vs > 0 else fv[1])
        xs = c0 + (fr.hw(np.arange(fr.w)) - left) * fr.hs / (fh[1] - fh[0]) * (c1 - c0)
        ys = r0 + (fr.vw(np.arange(fr.h)) - bottom) * fr.vs / (fv[1] - fv[0]) * (r1 - r0)
        mask = bilinear(m.astype(np.float32), xs, ys) >= 0.5
        ref = bilinear(rgba, xs, ys)
        ref = ref[..., :3] * ref[..., 3:] + 0.5 * (1 - ref[..., 3:])
        save(mask, os.path.join(out, "mask_%s.png" % name))
        save(ref, os.path.join(out, "ref_%s.png" % name))
        stretch = ((c1 - c0) / (r1 - r0)) / ((fh[1] - fh[0]) / (fv[1] - fv[0])) - 1
        frames[name], masks[name], refs[name] = fr, mask, ref
        data[name] = dict(axis=v["axis"], frame=fr.dict(), mask="mask_%s.png" % name, ref="ref_%s.png" % name,
                          stretch=round(stretch, 4), source_px=[int(c1 - c0), int(r1 - r0)])
        low = " low resolution" if min(c1 - c0, r1 - r0) < 300 else ""
        rows.append((name, v["axis"], "%d x %d%s" % (c1 - c0, r1 - r0, low),
                     "%+.1f%%%s" % (stretch * 100, " **check**" if abs(stretch) > STRETCH_FLAG else "")))
    rep = ["# Reference sheet%s\n\n" % (": " + S["name"] if S.get("name") else ""),
           "Bounds (m): x %.2f..%.2f, y %.2f..%.2f, z %.2f..%.2f. Canvas 1 px = %.1f cm, margin %.2f m.\n"
           % (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], 100 / ppm, margin),
           "\n## Views\n\n", table(("View", "Axis", "Silhouette (source px)", "Stretch"), rows),
           "\nStretch: how much wider (+) or narrower (-) the silhouette is for its height than the bounds. Over "
           "%d%%, the view is not straight-on or the bounds are wrong.\n" % (STRETCH_FLAG * 100)]
    by_axis = {d["axis"]: n for n, d in data.items()}
    pair_rows = []
    for a, b in PAIRS:
        if a in by_axis and b in by_axis:
            na, nb = by_axis[a], by_axis[b]
            A, B = masks[na], remap(masks[nb], frames[nb], frames[na])
            iou = (A & B).sum() / max(1, (A | B).sum())
            regs = regions(A ^ B, frames[na], tol / 2, clean=True)
            save(tint(refs[na], [(A & B, None), (A & ~B, (1.0, 0.55, 0.0)), (B & ~A, (0.0, 0.85, 1.0))]),
                 os.path.join(out, "pair_%s_%s.png" % (na, nb)))
            pair_rows.append((na + " / " + nb, "%.1f%%" % (iou * 100), len(regs),
                              "; ".join("%s (%.0f cm)" % (g["where"], g["depth_cm"]) for g in regs[:4]) or "none"))
            data[na].setdefault("mirror", []).extend(regs)
    if pair_rows:
        rep += ["\n## Mirror pairs\n", "Views from opposite sides must have the same outline, mirrored. pair_<a>_<b>.png, on the "
                "first view's picture: orange only in the first view, cyan only in the second.\n\n",
                table(("Pair", "Overlap", "Differences over %.1f cm" % (tol / 2), "Worst (world m)"), pair_rows)]
    near = float(S.get("near_cm", 40))
    edge_rows, marks, names = [], {}, list(data)
    for x, na in enumerate(names):
        for nb in names[x + 1:]:
            fa, fb = frames[na], frames[nb]
            for ax in sorted({fa.ha, fa.va} & {fb.ha, fb.va}):
                if {fa.ha, fa.va} == {fb.ha, fb.va}:
                    continue                                   # a mirror pair: compared whole above
                ea, eb = edges(masks[na], fa, ax), edges(masks[nb], fb, ax)
                miss = near_misses(ea, eb, tol / 100, near / 100)
                agree = sum(1 for ca, da in ea if any(abs(cb - ca) <= tol / 100 and da * db > 0 for cb, db in eb))
                edge_rows.append((na + " / " + nb, ax, agree, "; ".join(
                    "%s %s %.2f (%+.2f m) vs %s %.2f (%+.2f m): %.0f cm apart"
                    % (na, ax, ca, da, nb, cb, db, dd * 100) for ca, da, cb, db, dd in miss) or "none"))
                for ca, da, cb, db, dd in miss:
                    marks.setdefault(na, []).append((ax, ca, cb))
                    marks.setdefault(nb, []).append((ax, cb, ca))
                data[na].setdefault("near_misses", []).extend(
                    dict(other=nb, axis=ax, here=ca, there=cb, apart_cm=round(dd * 100, 1)) for ca, _, cb, _, dd in miss)
                data[nb].setdefault("near_misses", []).extend(
                    dict(other=na, axis=ax, here=cb, there=ca, apart_cm=round(dd * 100, 1)) for ca, _, cb, _, dd in miss)
    for nm, ms in marks.items():
        img = tint(refs[nm], [(masks[nm], None)])
        for ax, here, there in ms:
            for coord, col in ((there, (0.0, 0.85, 1.0)), (here, (1.0, 0.55, 0.0))):
                line(img, frames[nm], ax, coord, col)
        save(img, os.path.join(out, "edges_%s.png" % nm))
    if edge_rows:
        rep += ["\n## Shared edges\n",
                "Two views from different sides share one axis: a height (front and side), a width (front and top) "
                "or a length (side and top). Where a view's outline widens or narrows sharply, the other view usually "
                "changes at the same place. Agree: such edges within the tolerance. Near misses: the closest edges of "
                "the same kind %.0f-%.0f cm apart, most likely one feature drawn at two places; decide which is right. "
                "edges_<view>.png: orange this view's edge, cyan the other view's.\n\n" % (tol, near),
                table(("Views", "Axis", "Agree", "Near misses (world m, width change)"), edge_rows)]
    lms = []
    for n, lm in enumerate(S.get("landmarks", []), 1):
        nm = lm["view"]
        if nm not in frames:
            raise RuntimeError("landmark %d (%s): no view called %s" % (n, lm.get("name"), nm))
        reach = float(lm.get("snap_cm", 15)) / 100
        r = (snap(refs[nm], frames[nm], lm["h"], lm["v"], reach) if reach > 0
             else dict(h=sorted(lm["h"]), v=sorted(lm["v"]), moved=None, weak=[]))
        lms.append(dict(n=n, name=lm.get("name", "landmark %d" % n), view=nm, parts=lm.get("parts", []),
                        tolerance_cm=lm.get("tolerance_cm"), rough_h=sorted(lm["h"]), rough_v=sorted(lm["v"]), **r))
    for nm in data:
        img = refs[nm][..., :3].copy()
        grid(img, frames[nm], 0.5)
        for g in lms:
            if g["view"] == nm:
                rect(img, frames[nm], g["rough_h"], g["rough_v"], (0.6, 0.6, 0.6))
                draw_marks(img, frames[nm], g)
        save(img, os.path.join(out, "grid_%s.png" % nm))
    if lms:
        rep += ["\n## Landmarks\n",
                "Details inside the outline, as boxes in world metres. Each edge moved to the strongest line in the "
                "art within snap_cm. grid_<view>.png: grey the box as written, cyan as snapped, grid lines every "
                "0.5 m, labelled each metre. Check every cyan box sits on its detail; where it does not, correct the "
                "box as written, or set snap_cm to 0 to keep it exactly.\n\n",
                table(("#", "Name", "View", "As written (m)", "Snapped (m)", "Moved (cm, min/max)", "No clear line"),
                      [(g["n"], g["name"], g["view"], box_text(frames[g["view"]], g["rough_h"], g["rough_v"]),
                        box_text(frames[g["view"]], g["h"], g["v"]),
                        "%s %+d/%+d, %s %+d/%+d" % (frames[g["view"]].ha, *map(round, g["moved"]["h"]),
                                                  frames[g["view"]].va, *map(round, g["moved"]["v"]))
                        if g["moved"] else "kept", ", ".join(g["weak"]) or "-") for g in lms])]
    with open(os.path.join(out, "sheet_data.json"), "w", encoding="utf-8") as f:
        json.dump(dict(bounds=S["bounds"], ppm=ppm, margin=margin, views=data, landmarks=lms), f, indent=1)
    with open(os.path.join(out, "sheet_report.md"), "w", encoding="utf-8") as f:
        f.write("".join(rep))
    print("ortho_measure sheet: %s" % os.path.join(out, "sheet_report.md"))
    return os.path.join(out, "sheet_report.md")


def render_mask(sc, cam, fr, axis, lo, hi, tmp):
    """The visible objects of sc through an orthographic camera fitted to the frame's pixels: a bool mask."""
    ha, hs, va, vs = AXES[axis]
    d, ds = axis[1].lower(), (1 if axis[0] == "+" else -1)
    right, up = UNIT[ha] * hs, UNIT[va] * vs
    back = right.cross(up)
    assert (back - UNIT[d] * ds).length < 1e-6
    ext = max(hi[k] - lo[k] for k in range(3))
    dist = ext + 10.0
    c = Vector((0.0, 0.0, 0.0))
    c[I3[ha]] = fr.h0 + fr.hs * fr.w / (2 * fr.ppm)
    c[I3[va]] = fr.v0 + fr.vs * fr.h / (2 * fr.ppm)
    c[I3[d]] = (hi[I3[d]] if ds > 0 else lo[I3[d]]) + ds * dist
    M = Matrix((right, up, back)).transposed().to_4x4()
    M.translation = c
    cam.matrix_world = M
    cam.data.ortho_scale = fr.w / fr.ppm
    cam.data.clip_start, cam.data.clip_end = 0.01, 2 * dist + 2 * ext
    sc.render.resolution_x, sc.render.resolution_y = fr.w, fr.h
    sc.render.filepath = tmp
    bpy.ops.render.render(write_still=True, scene=sc.name)
    return load(tmp)[..., 3] >= 0.5, back, c[I3[d]]


def render_shaded(sc, tmp):
    """The same camera, lit, each part its own colour (a plate facing the camera shades like the face behind it)
    with cavity, so the parts inside the outline show: RGB on grey."""
    s = sc.display.shading
    s.light, s.color_type, s.show_cavity, s.cavity_type = "STUDIO", "RANDOM", True, "BOTH"
    sc.display.render_aa = "8"
    try:
        bpy.ops.render.render(write_still=True, scene=sc.name)
    finally:
        s.light, s.color_type, s.show_cavity, sc.display.render_aa = "FLAT", "SINGLE", False, "OFF"
    a = load(tmp)
    return a[..., :3] * a[..., 3:] + 0.15 * (1 - a[..., 3:])


def check(sheet_path, label=None):
    S, base = read_sheet(sheet_path)
    mdir = os.path.join(base, "measure")
    with open(os.path.join(mdir, "sheet_data.json"), encoding="utf-8") as f:
        D = json.load(f)
    C = S.get("check", {})
    tol = float(C.get("tolerance_cm", 5))
    names = C.get("collections") or []
    gone = [n for n in names if n not in bpy.data.collections]
    if not names or gone:
        raise RuntimeError("check.collections %s not found; this file has: %s"
                           % (gone or "(none given)", [c.name for c in bpy.data.collections][:40]))
    label = label or time.strftime("%Y%m%d-%H%M%S")
    out = os.path.join(mdir, "check_" + label)
    os.makedirs(out, exist_ok=True)
    lo, hi = D["bounds"]["min"], D["bounds"]["max"]
    tmp = os.path.join(out, "_render.png")
    sc = bpy.data.scenes.new("om_check")
    cd = bpy.data.cameras.new("om_cam")
    cd.type, cd.sensor_fit = "ORTHO", "HORIZONTAL"
    cam = bpy.data.objects.new("om_cam", cd)
    view_rows, worst, res, tiles = [], [], {}, []
    pats, tc, mc, shaded, refs, lm_res = C.get("exclude", []), None, None, {}, {}, []
    try:
        if pats:                       # only the parts the art shows, in a temporary collection of their own
            tc = bpy.data.collections.new("om_parts")
            sc.collection.children.link(tc)
            for o in {o for n in names for o in bpy.data.collections[n].all_objects}:
                if not any(fnmatch.fnmatchcase(o.name, p) for p in pats):
                    tc.objects.link(o)
        else:
            for n in names:
                sc.collection.children.link(bpy.data.collections[n])
        sc.collection.objects.link(cam)
        sc.camera = cam
        try:
            sc.render.engine = "BLENDER_WORKBENCH"
        except TypeError as e:
            raise RuntimeError("no Workbench engine: %s" % e)
        sc.display.shading.light, sc.display.shading.color_type = "FLAT", "SINGLE"
        sc.display.render_aa = "OFF"
        sc.render.film_transparent = True
        sc.render.resolution_percentage = 100
        sc.render.image_settings.file_format, sc.render.image_settings.color_mode = "PNG", "RGBA"
        try:
            sc.view_settings.view_transform = "Standard"
        except TypeError:
            pass
        dg = sc.view_layers[0].depsgraph
        for name, v in D["views"].items():
            fr = Frame(**v["frame"])
            M, back, depth = render_mask(sc, cam, fr, v["axis"], lo, hi, tmp)
            dg.update()
            shaded[name] = render_shaded(sc, tmp)
            R = load(os.path.join(mdir, v["mask"]))[..., 0] >= 0.5
            ref = load(os.path.join(mdir, v["ref"]))
            refs[name] = ref[..., :3]
            acc = np.zeros_like(R)
            for a in C.get("accept", []):
                if a.get("view") == name:
                    hw, vw = fr.hw(np.arange(fr.w)), fr.vw(np.arange(fr.h))
                    acc |= (((vw >= min(a["v"])) & (vw <= max(a["v"])))[:, None]
                            & ((hw >= min(a["h"])) & (hw <= max(a["h"])))[None, :])
            extra, short = M & ~R, R & ~M

            def part(j, i):
                o = Vector((0.0, 0.0, 0.0))
                o[I3[fr.ha]], o[I3[fr.va]], o[I3[v["axis"][1].lower()]] = float(fr.hw(j)), float(fr.vw(i)), depth
                hit, _, _, _, ob, _ = sc.ray_cast(dg, o, -back)
                return ob.name if hit else None
            regs = []
            for kind, diff in (("model extra", extra), ("model missing", short)):
                for g in regions(diff & ~acc, fr, tol / 2, clean=3 / fr.ppm * 100 <= tol):
                    g["view"], g["kind"], g["fail"] = name, kind, bool(g["depth_cm"] > tol)
                    if kind == "model extra":
                        g["part"] = part(*g["px"])
                    else:
                        j0, j1, i0, i1 = g["box"]
                        sub = M[max(0, i0 - 4):i1 + 5, max(0, j0 - 4):j1 + 5]
                        ii, jj = np.nonzero(sub)
                        near = Counter()
                        if len(ii):
                            ii, jj = ii + max(0, i0 - 4), jj + max(0, j0 - 4)
                            order = np.argsort((jj - g["px"][0]) ** 2 + (ii - g["px"][1]) ** 2)[:5]
                            near = Counter(p for p in (part(jj[k], ii[k]) for k in order) if p)
                        g["part"] = "next to " + near.most_common(1)[0][0] if near else None
                    regs.append(g)
            regs = bands(sorted(regs, key=lambda g: -g["depth_cm"]), fr.ppm)
            iou = (M & R).sum() / max(1, (M | R).sum())
            img = tint(ref, [(M & R, None), (extra & ~acc, (0.95, 0.15, 0.1)), (short & ~acc, (0.15, 0.45, 1.0)),
                             ((extra | short) & acc, (0.95, 0.85, 0.1))])
            save(img, os.path.join(out, "overlay_%s.png" % name))
            tiles.append(img)
            res[name] = dict(axis=v["axis"], overlap=round(float(iou), 4),
                             extra_m2=round(float((extra & ~acc).sum()) / fr.ppm ** 2, 3),
                             missing_m2=round(float((short & ~acc).sum()) / fr.ppm ** 2, 3), regions=regs)
            view_rows.append((name, v["axis"], "%.1f%%" % (iou * 100), "%.3f" % res[name]["extra_m2"],
                              "%.3f" % res[name]["missing_m2"], "%.0f cm" % regs[0]["depth_cm"] if regs else "-"))
            worst += regs
        if D.get("landmarks"):          # every part of the model, the excluded ones too, in the depsgraph
            objs = {o for n in names for o in bpy.data.collections[n].all_objects}
            mc = bpy.data.collections.new("om_marks")
            sc.collection.children.link(mc)
            for o in objs:
                if o.name not in sc.objects:
                    mc.objects.link(o)
            dg.update()
            for L in D["landmarks"]:
                fr = Frame(**D["views"][L["view"]]["frame"])
                tl = float(L.get("tolerance_cm") or tol)
                mh, mv, used, total, far = part_box(objs, L["parts"], dg, fr, L["h"], L["v"],
                                                    float(L.get("near_cm", 30)) / 100)
                g = dict(L, model_h=mh, model_v=mv, pieces=[used, total], none_near=far, tolerance_cm=tl,
                         edges_cm=None)
                if mh is None:
                    g.update(worst_cm=None, fail=True)
                else:
                    d = [(mh[0] - L["h"][0]) * 100, (mh[1] - L["h"][1]) * 100,
                         (mv[0] - L["v"][0]) * 100, (mv[1] - L["v"][1]) * 100]
                    w = max(abs(x) for x in d)
                    g.update(edges_cm=[round(x, 1) for x in d], worst_cm=round(w, 1), fail=bool(w > tl))
                lm_res.append(g)
    finally:
        if mc:
            bpy.data.collections.remove(mc)
        if tc:
            bpy.data.collections.remove(tc)
        bpy.data.scenes.remove(sc)
        bpy.data.objects.remove(cam)
        bpy.data.cameras.remove(cd)
        if os.path.exists(tmp):
            os.remove(tmp)
    hmax = max(t.shape[0] for t in tiles)
    gap = np.full((hmax, 16, 3), 0.1, np.float32)
    row = []
    for t in tiles:
        row += [np.vstack([t, np.full((hmax - t.shape[0], t.shape[1], 3), 0.1, np.float32)]), gap]
    save(np.hstack(row[:-1]), os.path.join(out, "overlays.png"))
    for name, v in D["views"].items():               # art and model side by side, same scale, one grid
        fr, halves = Frame(**v["frame"]), []
        for src in (refs[name], shaded[name]):
            img = src.copy()
            grid(img, fr, 0.5)
            for g in lm_res:
                if g["view"] == name:
                    draw_marks(img, fr, g)
            halves.append(img)
        save(np.hstack([halves[0], np.full((fr.h, 12, 3), 0.1, np.float32), halves[1]]),
             os.path.join(out, "board_%s.png" % name))
    for g in lm_res:                                 # each landmark enlarged, art left, model right
        fr = Frame(**D["views"][g["view"]]["frame"])
        bh, bv = list(g["h"]), list(g["v"])
        if g["model_h"]:
            bh = [min(bh[0], g["model_h"][0]), max(bh[1], g["model_h"][1])]
            bv = [min(bv[0], g["model_v"][0]), max(bv[1], g["model_v"][1])]
        cf, step = crop(fr, bh, bv)
        halves = []
        for src in (refs[g["view"]], shaded[g["view"]]):
            img = remap(src, fr, cf)
            grid(img, cf, step)
            draw_marks(img, cf, g)
            halves.append(img)
        save(np.hstack([halves[0], np.full((cf.h, 12, 3), 0.1, np.float32), halves[1]]),
             os.path.join(out, "detail_%d.png" % g["n"]))
    worst.sort(key=lambda g: -g["depth_cm"])
    fails = [g for g in worst if g["fail"]]
    lm_fails = [g for g in lm_res if g["fail"]]
    rep = ["# Silhouette check: %s\n\n" % label,
           "Model: %s. Tolerance %.1f cm; 1 px = %.1f cm.\n\n" % (", ".join(names), tol, 100 / D["ppm"]),
           "**%s**: %d outline difference(s) and %d landmark(s) over the tolerance.\n\n"
           % ("FAIL" if fails or lm_fails else "PASS", len(fails), len(lm_fails)),
           table(("View", "Axis", "Overlap", "Model extra (m²)", "Model missing (m²)", "Worst"), view_rows),
           "\n## Differences over %.1f cm, deepest first\n\n" % (tol / 2),
           "Where: world metres along the view's right and up axes. Depth: the most centimetres across the "
           "difference; mean: its average thickness.\n\n",
           table(("#", "View", "Kind", "Where (m)", "Depth / mean (cm)", "Area (m²)", "Part", "Over tol"),
                 [(k + 1, g["view"], g["kind"], g["where"], "%.0f / %.0f" % (g["depth_cm"], g["mean_cm"]),
                   "%.3f" % g["area_m2"], g["part"] or "-", "yes" if g["fail"] else "") for k, g in
                  enumerate(worst[:25])]) if worst else "None.\n",
           "\nOverlays: grey both, red model only, blue reference only, yellow accepted. overlays.png has the views "
           "left to right: %s.\n" % ", ".join(D["views"])]
    if lm_res:
        def diff(g):
            if g["edges_cm"] is None:
                return "no part matches %s" % ", ".join(g["parts"])
            a, b, c, d = g["edges_cm"]
            fr = Frame(**D["views"][g["view"]]["frame"])
            return "centre %s %+d, %s %+d; size %s %+d, %s %+d" % (
                fr.ha, round((a + b) / 2), fr.va, round((c + d) / 2), fr.ha, round(b - a), fr.va, round(d - c))
        def model(g):
            if not g["model_h"]:
                return "-"
            u, t = g["pieces"]
            return box_text(Frame(**D["views"][g["view"]]["frame"]), g["model_h"], g["model_v"]) + (
                " (none near: all %d pieces)" % t if g["none_near"] else " (%d of %d pieces)" % (u, t) if u < t else "")
        rep += ["\n## Landmarks\n",
                "Each detail's box in the art (signed off in the sheet) against its model parts in that view: the "
                "mesh pieces of the named parts within near_cm (default 30) of the art's box. Centre: how far the "
                "model's part sits from the art's, along world axes; size: how much bigger (+) or smaller (-) it is. "
                "Worst: the edge furthest off.\n\n",
                table(("#", "Name", "View", "Art (m)", "Model (m)", "Model against art (cm)", "Worst", "Over tol"),
                      [(g["n"], g["name"], g["view"], box_text(Frame(**D["views"][g["view"]]["frame"]), g["h"], g["v"]),
                        model(g), diff(g), "%.0f cm" % g["worst_cm"] if g["worst_cm"] is not None
                        else "-", "yes" if g["fail"] else "") for g in lm_res])]
        for name in D["views"]:
            e = [g["edges_cm"] for g in lm_res if g["view"] == name and g["edges_cm"]]
            if len(e) >= 3:
                fr = Frame(**D["views"][name]["frame"])
                mh, mv = (float(np.median([(a + b) / 2 for a, b, _, _ in e])),
                          float(np.median([(c + d) / 2 for _, _, c, d in e])))
                rep.append("\n%s: the median centre offset of its %d landmarks is %s %+d, %s %+d cm. A shift most of "
                           "a view's landmarks share points at the view (a lean, a cut line, a stretch) before the "
                           "parts.\n" % (name, len(e), fr.ha, round(mh), fr.va, round(mv)))
    rep += ["\nboard_<view>.png: the art (left) and the model, lit (right), at the same scale with a grid every 0.5 m "
            "labelled each metre; detail_<n>.png: each landmark enlarged, with a finer grid. Cyan: the art's box; "
            "orange: the model's.\n"]
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write("".join(rep))
    passed = not fails and not lm_fails
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(dict(label=label, passed=passed, tolerance_cm=tol, views=res, landmarks=lm_res), f, indent=1)
    print("ortho_measure check: %s %s" % ("PASS" if passed else "FAIL", os.path.join(out, "report.md")))
    return os.path.join(out, "report.md")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    try:
        if len(args) >= 2 and args[0] == "sheet":
            sheet(args[1])
        elif len(args) >= 2 and args[0] == "check":
            check(args[1], args[2] if len(args) > 2 else None)
        else:
            print(__doc__)
            sys.exit(2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
