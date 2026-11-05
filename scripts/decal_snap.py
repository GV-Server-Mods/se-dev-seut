"""Snap a model's decals onto the grid the game stores vertex positions on, so none round into their surface.

SE stores each vertex as half floats times floor(max |x|, |y|, |z|) (`VRage.Import.PositionPacker`; the mwm
"Vertices" tag is HalfVector4), so a vertex lands on a grid of about 1 mm per whole metre of its largest coordinate,
along that axis: 3.9 mm at 4 m, 5.9 mm at 6 m. Model decals write no depth and draw only where they test in front of
the surface, so a decal 1.5 mm up can round onto or behind it and vanish, or break into wedges.

snap(collection) moves every decal vertex to the nearest stored grid point at least GMIN in front of the rounded
surface under it, so the game's rounding leaves it where it was checked, then restores the shading normals the
decal was built with. Run it as the last step of a scripted build, in the pose that is exported, on the exported
coordinates (a subpart's own origin, not the block's, when the part is a subpart scene). It returns, per object:
triangles broken by rounding before, after, and triangles already under KEEP in the design itself (reported, not
chased). Load it as a text block (`bpy.data.texts[...].as_module()`) or with `exec`.
"""
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

DEC = {"DECAL", "DECAL_NOPREMULT", "DECAL_CUTOUT"}
GMIN, RAISE, UP, KEEP = 0.0006, 0.0005, 0.0025, 0.0003
BARY = ((.96, .02, .02), (.02, .96, .02), (.02, .02, .96), (1 / 3, 1 / 3, 1 / 3), (.5, .5, 0), (0, .5, .5), (.5, 0, .5))


def pack(v):
    """Where the game puts these points (PositionPacker.PackPosition, then unpack)."""
    v = np.asarray(v, np.float32)
    s = np.maximum(np.minimum(np.floor(np.abs(v).max(-1, keepdims=True)), 2048), 1).astype(np.float32)
    return (v * (np.float32(1) / s)).astype(np.float16).astype(np.float32) * s


def grid(w, k):
    """Points the game stores exactly, within k half-float steps of w on each axis."""
    s = np.float32(max(min(np.floor(np.abs(w).max()), 2048), 1))
    axes = []
    for x in (np.asarray(w, np.float32) * (np.float32(1) / s)).astype(np.float16):
        lo = hi = x; vals = [x]
        for _ in range(k):
            lo = np.nextafter(lo, np.float16(-np.inf)); hi = np.nextafter(hi, np.float16(np.inf)); vals += [lo, hi]
        axes.append(np.array(vals, np.float32) * s)
    c = np.stack(np.meshgrid(*axes, indexing="ij"), -1).reshape(-1, 3); m = np.abs(c).max(1)
    # A point right on a whole metre can round to the next scale on export (6.0 came out 5.9999999): skip those.
    return c[(pack(c) == c).all(1) & (m - np.floor(m) > 1e-4)]


def tech(m):
    return getattr(getattr(m, "seut", None), "technique", "") if m else ""


def surfaces(col):
    """Every opaque face as exported (modifiers applied), as BVHs before and after the game's rounding; and the
    decal objects (objects with modifiers are skipped: their exported vertices are not the mesh's)."""
    pts, tris, dec, b = [], [], [], 0; dg = bpy.context.evaluated_depsgraph_get()
    for o in sorted((o for o in col.all_objects if o.type == "MESH"), key=lambda o: o.name):
        ev = o.evaluated_get(dg); me = ev.to_mesh(); me.calc_loop_triangles(); k = [tech(m) for m in me.materials]
        kind = lambda i, k=k: k[i] if i < len(k) else ""
        W = np.array([o.matrix_world @ v.co for v in me.vertices], np.float32).reshape(-1, 3)
        op = [tuple(t.vertices) for t in me.loop_triangles if kind(t.material_index) not in DEC | {"GLASS"}]
        if op:
            pts.append(W); tris += [tuple(b + i for i in t) for t in op]; b += len(W)
        if any(kind(p.material_index) in DEC for p in me.polygons) and not o.modifiers:
            dec.append((o, kind))
        ev.to_mesh_clear()
    P = np.concatenate(pts)
    return (BVHTree.FromPolygons([Vector(p) for p in pack(P)], tris),
            BVHTree.FromPolygons([Vector(p) for p in P], tris), dec)


def base(bvh, w, n):
    """The surface under w: hit point and normal, or None (nothing within reach, or not facing n)."""
    h = bvh.ray_cast(Vector(w) + n * UP, -n, UP + 0.01)
    if h[0] is None or h[3] < 1e-5:
        return None
    nh = h[1] if h[1].dot(n) > 0 else -h[1]
    return (np.array(h[0], np.float32), np.array(nh, np.float32)) if nh.dot(n) > 0.7 else None


def gaps(bvh, o, kind, rounded=True):
    """Lowest gap over each decal triangle (7 samples), by triangle index."""
    me = o.data; me.calc_loop_triangles(); M = o.matrix_world; N = M.inverted_safe().transposed().to_3x3()
    W = np.array([M @ v.co for v in me.vertices], np.float32).reshape(-1, 3); W = pack(W) if rounded else W
    out = {}
    for t in me.loop_triangles:
        if kind(t.material_index) not in DEC:
            continue
        n = (N @ t.normal).normalized(); lo = None
        for b in BARY:
            p = b[0] * W[t.vertices[0]] + b[1] * W[t.vertices[1]] + b[2] * W[t.vertices[2]]
            h = bvh.ray_cast(Vector(p) + n * UP, -n, UP + 0.01)
            if h[0] is not None and abs(h[1].dot(n)) > 0.7:
                lo = h[3] - UP if lo is None else min(lo, h[3] - UP)
        out[t.index] = (tuple(t.vertices), lo)
    return out


def snap(col, passes=3):
    """Snap every decal in col; returns {object: (broken by rounding before, after, design faults)}."""
    rb, tb, dec = surfaces(col); report = {}
    for o, kind in dec:
        me = o.data; M = o.matrix_world; Mi = M.inverted_safe(); N = Mi.transposed().to_3x3()
        W0 = np.array([M @ v.co for v in me.vertices], np.float32).reshape(-1, 3)
        cn = [tuple(c.vector) for c in me.corner_normals]   # shading as built, restored after the move
        design = {i for i, (v, g) in gaps(tb, o, kind, False).items() if g is not None and g < KEEP}
        was = sum(1 for i, (v, g) in gaps(rb, o, kind).items() if g is not None and g < KEEP and i not in design)
        groups = {}
        for p in me.polygons:
            if kind(p.material_index) in DEC:
                n = (N @ p.normal).normalized()
                for i in p.vertices:
                    g = groups.setdefault(tuple(np.round(W0[i] * 1e5).astype(np.int64)), [Vector(), set(), GMIN])
                    g[0] += n; g[1].add(i)
        todo, left, moved = list(groups), [], False
        for _ in range(passes):
            for key in todo:
                n, idx, need = groups[key]; w = W0[min(idx)]; hit = base(rb, w, n.normalized()); c = pack(w[None])[0]
                if hit is not None:
                    H, nh = hit
                    for k in (1, 2, 3):
                        C = grid(w, k); ok = (C - H) @ nh >= need
                        if ok.any():
                            c = C[ok][np.argmin(np.linalg.norm(C[ok] - w, axis=1))]
                            break
                for i in idx:
                    v = Mi @ Vector(c); moved |= (v - me.vertices[i].co).length > 0; me.vertices[i].co = v
            me.update()
            left = [v for i, (v, g) in gaps(rb, o, kind).items() if g is not None and g < KEEP and i not in design]
            if not left:
                break
            bad = {i for v in left for i in v}
            todo = [key for key, g in groups.items() if g[1] & bad]
            for key in todo:
                groups[key][2] += RAISE
        # The move tilts small faces by up to ~10 degrees; keep every corner's built normal so nothing shades in facets.
        # Only after a real move: re-setting unchanged custom normals drifts them a little on every rebuild.
        if moved:
            for p in me.polygons:
                p.use_smooth = True
            me.normals_split_custom_set(cn)
        report[o.name] = (was, len(left), len(design))
    return report
