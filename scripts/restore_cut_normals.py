"""Repair a kitbashed vanilla mesh after an Exact boolean welded it (run inside Blender).

An Exact boolean merges every vertex that shares a position across the whole object, and Blender then reads
the vanilla custom normals against the new smooth fans, so the shading goes wrong far from the cut
(`references/kitbash.md`, "Cutting into a vanilla mesh"). `rebuild(cur, orig, name)` makes a new mesh from the
pre-cut copy `orig`: it deletes the faces the cut removed, adds the cut's new faces from `cur` as their own
islands (positions, UVs and material), and sets every corner normal. Kept faces get their pre-cut normals, new
faces the pre-cut normal interpolated where they lie. Faces are matched by their corner positions (0.1 mm), so
`cur` and `orig` must be in the same object space. Both meshes need the same material list.

    import bpy
    G = {}; exec(open(r"<skill>/scripts/restore_cut_normals.py").read(), G)
    with bpy.data.libraries.load(r"<pre-cut checkpoint>.blend", link=False) as (src, dst):
        dst.objects = list(names)      # a copy: Blender fills the list it is given with the loaded objects
    for n, ob in zip(names, list(dst.objects)):
        o = bpy.data.objects[n]
        new, info = G["rebuild"](o.data, ob.data, n + "_restored")
        print(n, info)                 # max_off and over_half_deg should be about 0
        o.data = new

Afterwards remove the loaded objects and orphan meshes, then export. The checkpoint copy must be unwelded: of
several checkpoints, take the latest where the object still has its full vertex count.
"""
import math

import bmesh
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc


def _r(v):
    return tuple(round(c, 4) for c in v)


def _key(me, p):
    return tuple(sorted(_r(me.vertices[v].co) for v in p.vertices))


def rebuild(cur, orig, name):
    ko = {_key(orig, p): p.index for p in orig.polygons}
    kc = {_key(cur, p): p.index for p in cur.polygons}
    removed = [i for k, i in ko.items() if k not in kc]
    added = [i for k, i in kc.items() if k not in ko]
    ocn = orig.corner_normals
    keep = {}
    for p in orig.polygons:
        k = _key(orig, p)
        if k in kc:
            for l in p.loop_indices:
                keep[(k, _r(orig.vertices[orig.loops[l].vertex_index].co))] = ocn[l].vector.copy()
    orig.calc_loop_triangles()
    verts = [v.co.copy() for v in orig.vertices]
    tris = [tuple(t.vertices) for t in orig.loop_triangles]
    tri_nrm = [tuple(ocn[l].vector.copy() for l in t.loops) for t in orig.loop_triangles]
    tri_face = [orig.polygons[t.polygon_index].normal.copy() for t in orig.loop_triangles]
    bvh = BVHTree.FromPolygons(verts, tris)

    new = orig.copy(); new.name = name
    bm = bmesh.new(); bm.from_mesh(new); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in removed], context='FACES')
    uv = bm.loops.layers.uv.active; cur_uv = cur.uv_layers.active.data
    slot = {m.name: i for i, m in enumerate(new.materials)}
    for i in added:
        p = cur.polygons[i]
        f = bm.faces.new([bm.verts.new(cur.vertices[v].co) for v in p.vertices])
        f.material_index = slot[cur.materials[p.material_index].name]
        f.smooth = p.use_smooth
        for loop, li in zip(f.loops, p.loop_indices):
            loop[uv].uv = cur_uv[li].uv
    bm.to_mesh(new); bm.free()

    targets, interp, flat = [], 0, 0
    for p in new.polygons:
        k = _key(new, p)
        for l in p.loop_indices:
            co = new.vertices[new.loops[l].vertex_index].co
            t = keep.get((k, _r(co)))
            if t is None:
                interp += 1
                hit = bvh.find_nearest(co + (p.center - co) * 0.02)   # nudge inside the face: the face's own side
                i = hit[2]
                if hit[0] is not None and hit[3] < 1e-3 and tri_face[i].dot(p.normal) > 0.99:
                    w = poly_3d_calc([verts[j] for j in tris[i]], hit[0])
                    t = (tri_nrm[i][0] * w[0] + tri_nrm[i][1] * w[1] + tri_nrm[i][2] * w[2]).normalized()
                else:
                    t = p.normal.copy(); flat += 1
            targets.append(t)
    new.normals_split_custom_set(targets)
    cn = new.corner_normals
    off = [math.degrees(cn[l].vector.angle(targets[l], 0)) for l in range(len(new.loops))]
    return new, dict(removed=len(removed), added=len(added), interpolated=interp, flat_fallback=flat,
                     verts=(len(orig.vertices), len(cur.vertices), len(new.vertices)),
                     max_off=round(max(off), 3), over_half_deg=sum(o > 0.5 for o in off))
