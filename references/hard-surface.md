# Hard-surface build order with bmesh and modifiers

## Contents
- Order of work
- Snippets
- Common failures

## Order of work

1. **Blockout.** Primitives at exact dimensions from the target table. Correct proportions here beat any
   later detail.
2. **Primary cuts.** Boolean-style cuts done as geometry (bmesh bisect, inset, extrude) or Boolean modifier
   then applied. Keep cuts aligned to the grid.
3. **Bevels.** One bevel width per scale of feature (large, medium, small), `harden_normals` on, applied
   last-ish. Edges that must stay sharp get no bevel.
4. **Panel detail.** Insets and shallow extrudes; avoid detail smaller than a texel can show.
5. **Topology check.** `get_scene_info` with `fields=["topology"]` reports tris, quads, ngons, non-manifold
   edges and loose verts. Fix non-manifold edges and loose verts before export.
6. **UVs.** Unwrap after the shape is final; scale islands to consistent texel density.

## Snippets

```python
import bpy, bmesh
# primitive at an exact size, centred
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
bmesh.ops.scale(bm, vec=(2.5, 2.5, 1.2), verts=bm.verts)
me = bpy.data.meshes.new("part"); bm.to_mesh(me); bm.free()

# bevel modifier with hardened normals
m = ob.modifiers.new("Bevel", 'BEVEL'); m.width = 0.05; m.segments = 2; m.limit_method = 'ANGLE'
m.harden_normals = True

# inset every selected face, in bmesh
bmesh.ops.inset_region(bm, faces=[f for f in bm.faces if f.select], thickness=0.05, depth=-0.02)

# mirror about X, merge on the seam
mm = ob.modifiers.new("Mirror", 'MIRROR'); mm.use_axis[0] = True; mm.use_clip = True
```

## Common failures

- Flipped normals after mirroring: recalculate outside (`bmesh.ops.recalc_face_normals`).
- Bevel looks wrong after non-uniform scale: apply scale first.
- Modifier left unapplied when a downstream tool needs real geometry (collision, export): apply it.
- Tiny faces and coincident verts after booleans: `bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)`.
