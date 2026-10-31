# bpy recipes for SEUT (verified on SEUT 1.2.1, Blender 4.5)

Run these through `execute_blender_code`. Work in small steps and print what changed.

## Scene and collections [verified]

```python
import bpy
sc = bpy.data.scenes.new("tmp")
bpy.context.window.scene = sc
s = sc.seut
s.sceneType = 'mainScene'      # also 'subpart', 'character', 'character_animation', 'planet_editor' (read the enum, don't trust this list)
s.subtypeId = "MyBlock"        # ASCII only; renames the scene to "MyBlock"
s.gridScale = 'large'          # or 'small'
s.bBox_X, s.bBox_Y, s.bBox_Z = 1, 1, 1   # in grid cells, not metres
bpy.ops.scene.recreate_collections()
sc = bpy.data.scenes["MyBlock"]          # the scene was renamed
```

Collections created for a main scene (SubtypeId in brackets): `Main`, `Collision - Main`, `LOD1..LOD3`
(`LOD distance` 25 / 50 / 100 by default, each doubling), `BS1..BS3`, `BS1_LOD1`, plus the view layer
named `SEUT`. Find them by type, never by display name:

```python
def seut_col(sc, col_type, index=0, ref=None):
    for c in bpy.data.collections:
        if c.seut.scene is sc and c.seut.col_type == col_type and c.seut.type_index == index and (ref is None or c.seut.ref_col == ref):
            return c
main = seut_col(sc, 'main')
hkt  = seut_col(sc, 'hkt', 1, main)      # collision for Main has type_index 1
lod1 = seut_col(sc, 'lod', 1, main)      # ALWAYS pass `main` for LODs, see below
```

`LOD1` (ref Main) and `BS1_LOD1` (ref BS1) are both `lod` with `type_index` 1. Without `ref=main` the lookup
can return `BS1_LOD1`, and the LOD mesh lands in the build-stage collection while `LOD1` stays empty; SEUT
raises no warning [HARD, hit in a test run]. After filling LODs, list each collection's object count to check.
Empty `LOD3` and `BS1..3` collections export without complaint.

`col_type` values: `seut main hkt lod bs mountpoints mirroring render`. Data lives in `col.seut`
(`lod_distance`, `ref_col`, `type_index`).

## Mesh into Main, bevel, UV, material [verified]

```python
import bmesh
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.5)      # large cell
me = bpy.data.meshes.new("Armor"); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("Armor", me); main.objects.link(ob)
bpy.context.view_layer.objects.active = ob
# modifier_apply needs the object selected and active
```

Apply modifiers (Bevel, Mirror) before export or collision: unapplied modifiers on collision objects are
E034. Use `uv.smart_project` only as a starting point; real blocks need islands placed on atlas regions.

## Link a vanilla material [verified]

```python
path = r"C:\SE_Assets\Materials\Materials.blend"    # <SEUT Assets>\Materials; read the real path from preferences
with bpy.data.libraries.load(path, link=True) as (src, dst):
    dst.materials = [n for n in src.materials if n == "PaintedMetal_Colorable"]
ob.data.materials.append(bpy.data.materials["PaintedMetal_Colorable"])
```

Linked materials are read-only. Textures resolve relative to the library
(`//..\Textures\Models\Cubes\<name>.TIF`), so keep the library in `<SEUT Assets>\Materials`.
Preferences: `bpy.context.preferences.addons['space-engineers-utilities'].preferences` has `asset_path`,
`game_path`, `havok_path`, `mwmb_path`, `quick_tools`.

## Collision object [verified]

```python
col = bpy.data.objects.new("Collision1", bpy.data.meshes.new("c1"))
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.45); bm.to_mesh(col.data); bm.free()   # slightly under the block
hkt.objects.link(col)
bpy.context.view_layer.objects.active = col
bpy.ops.object.select_all(action='DESELECT'); col.select_set(True)
bpy.ops.rigidbody.object_add()
col.rigid_body.collision_shape = 'BOX'      # BOX, SPHERE, CAPSULE, CYLINDER, CONVEX_HULL only
```

Apply scale and rotation first, because the rigid body does not follow them afterwards.

## Multi-piece blocks, diagonal members, UVs [HARD, built and exported in two test runs]

Main needs one unparented top-level object (E031). For several solids (rails plus a brace), build each as a
box in one bmesh and join them into a single mesh, or parent the parts under one root object or empty. Joined
bmesh boxes need no boolean; overlapping ends are fine for a game model.

```python
import bmesh, math
from mathutils import Matrix, Vector

def add_box(bm, size, center=(0, 0, 0), rot_y_deg=0.0):
    """Box of size (x, y, z) in metres, centred at `center`, rotated about Y by rot_y_deg."""
    m = Matrix.Translation(center) @ Matrix.Rotation(math.radians(rot_y_deg), 4, 'Y') @ Matrix.Diagonal((*size, 1))
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)

def box_project_uv(bm, uv_per_metre, origin=0.37):
    """Per-face box projection at a fixed texel density; overlapping islands are fine on tiling materials.
    `origin` is an offset: 0.5 puts every 2.5 m cell edge exactly on UV 0.0 at 0.4 UV/m and triggers W002."""
    uv = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for l in f.loops:
            l[uv].uv = (l.vert.co[a] * uv_per_metre + origin, l.vert.co[b] * uv_per_metre + origin)
```

Armor-style density is about 0.05 UV per metre, functional blocks about 0.40 (`materials.md`). Check the result
by comparing UV area to world area per triangle: `sqrt(uv_area / world_area)` is the UV per metre.

Collision for angled members: make one collision mesh per piece (a box is fine for an axis-aligned rail),
and for a diagonal member build the same rotated box, apply rotation and scale, then set the rigid body
shape to `CONVEX_HULL` (a rotated Box or Cylinder would ignore the rotation). A rail pair plus a brace is three
objects, well under the limit of 10. Collision meshes need UVs too (add the same box projection; any real,
non-degenerate coordinates work).

Collision meshes should be sized to the model's real extent. Do not inset a full cube.

## Export through the MCP [HARD, tested on SEUT 1.2.1, Blender 4.5]

`scene.export` polls for a 3D viewport in Object mode, which the MCP does not give by default, so override the
context. The .blend must be saved, and the Mod folder and Export Folder must exist (the folder must contain
`Models\`).

```python
s = scn.seut
s.mod_path = r"<mod folder>"; s.export_exportPath = r"<mod folder>\Models\Cubes\large"
s.export_sbc_type = 'none'            # 'update' / 'new' also write the CubeBlocks SBC
s.export_deleteLooseFiles = False     # keep *.mwm.log and *.hkt.*.log while debugging; True for the final run
win = bpy.context.window
area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')
with bpy.context.temp_override(window=win, area=area, region=region, scene=scn):
    result = bpy.ops.scene.export()
```

- `export_sbc_type = 'new'` writes `Data\CubeBlocks\<SubtypeId>.sbc` (`I004`) [HARD, tested]: TypeId `CubeBlock`,
  Size from the bounding box, Model path, one `SteelPlate` x10 component, a placeholder icon
  (`AstronautBackpack.dds`), and `{LOC:DisplayName_<SubtypeId>}` / `{LOC:Description_<SubtypeId>}` names that
  show as raw text in game unless a localization file supplies them. Edit the SBC for real blocks. Mount
  points, build stages and mirroring are written when the scene has them (next bullet).
- What `'new'` and `'update'` write beyond the basics [HARD, read in `seut_ot_export.py` and checked on a
  scratch block `S4Test`]:
  - `<MountPoints>` from `scene.seut.mountpointAreas`: each area has `side` (front/back/left/right/top/bottom),
    `x`, `y` (centre offset from the face centre, metres) and `xDim`, `yDim` (size, metres). A full face is a
    2.5 m area on a large block, written as `StartX=0.00 EndX=1.00`. The `Default="true"` flag lands on the
    first area.
  - `<BuildProgressModels>`: one entry per non-empty `BS<n>` collection, upper bounds split evenly (two stages
    give 0.50 and 1.00), files `<SubtypeId>_BS<n>.mwm` beside the main model.
  - `<MirroringX>`, `<MirroringY>`, `<MirroringZ>` from `scene.seut.mirroring_X/Y/Z`. Blender Z maps to SE Y, so
    `mirroring_Z` writes `MirroringY` and `mirroring_Y` writes `MirroringZ`. Values are axis letters (`Y`, `Z`...).
  - `'update'` rewrites only these geometry-owned elements (Size, Model, MountPoints, BuildProgressModels,
    mirroring, Icon path) and keeps hand edits (TypeId, names, components, PCU, IsAirTight). So: `'new'` once,
    edit the SBC by hand, then `'update'` on later exports.
- Icons [HARD, tested]: SEUT does not make one. The SBC `Icon` becomes `Textures\GUI\Icons\<SubtypeId>.dds` only
  when a `.dds` or `.png` of that name exists under the folder in `scene.render.filepath` (point it at the mod's
  `Textures\GUI\Icons` folder, which must contain `Textures`). Vanilla icons are 128 x 128 DDS. Recipe: add a
  camera, render a 128 x 128 PNG with Workbench and `film_transparent`, convert with Pillow
  (`Image.save('X.dds', pixel_format='DXT5')`, Pillow is in system Python, not in Blender's), put the DDS in
  the Icons folder. Do not hide or disable rendering of the `seut`-type collection, or the render is blank.
  The DXT5 icon loading in game is [SOFT, not yet seen].
- In game [HARD, owner test]: a local mod folder containing only this SBC and the `.mwm` loads and the block can
  be placed. Gaps seen: the placeholder icon is ugly (a real icon is not generated by SEUT's SBC export);
  BuildInfo hints `IsAirTight` is null, so add `<IsAirTight>true</IsAirTight>` (or `false`) for blocks that are
  airtight on all faces; plain-text `DisplayName` is easier than the `{LOC:...}` placeholders for a test mod.
- Reading a vanilla FBX with `bpy.ops.import_scene.fbx` prints a huge "could not find any file path" dump to
  stdout; wrap the call in `contextlib.redirect_stdout` / `redirect_stderr` to an `io.StringIO`.
- A clean run ends with `I007` and leaves only `<SubtypeId>.mwm` (plus `<SubtypeId>_LODn.mwm` files and the
  SBC) when `export_deleteLooseFiles` is True. With False the run ends at `I004` and leaves the FBX, XML,
  `.hkt` and log files. Always make the last run with True.
- Re-running with `export_sbc_type = 'new'` does not overwrite: it writes `<SubtypeId>_1.sbc` beside the first
  one. Use `'new'` once, then `'none'` (or `'update'`). Delete stray `_1.sbc` files.
- Export reads the scene in memory, not the file on disk. `bpy.data.filepath` only has to point at a saved
  .blend (E008). To leave the user's open file alone, write a copy with
  `bpy.ops.wm.save_as_mainfile(filepath=..., copy=True)`. [SOFT: only tested with a file that already had a path.]
- Making an SBC usable: replace the `{LOC:...}` names with plain text, add `<IsAirTight>`, and replace the
  placeholder icon before shipping.
- `{'FINISHED'}` is returned even when `E044` was reported. Read the Notifications output, and keep the logs
  to find the cause.
- Tools used: `FBXImporter.exe` ships inside the add-on (`tools\`), `MwmBuilder.exe` and Havok come from
  Addon Preferences. Havok warning `Calculated 'extra radius' for box shape is 0` is harmless.
- Check the result by searching the `.mwm` bytes: `Dummies` with your `detector_*` names and a `highlight`
  user property, `HavokCollisionGeometry`, and the material names.

## Operators seen in the addon source (signatures tested only where noted)

`scene.recreate_collections`, `scene.create_collection`, `scene.add_mountpoint_area`, `scene.add_dummy`,
`scene.add_preset_subpart`, `scene.add_custom_subpart`, `object.add_highlight_empty` (tested, see
`interaction-highlights.md`), `object.create_material`, `object.remapmaterials`, `wm.import_materials`,
`wm.convert_textures`, `scene.export` (tested, above), `scene.export_all_scenes`, `scene.export_materials`,
`scene.import_complete`,
`quicktools.add_bevels`, `quicktools.remove_bevels`, `quicktools.apply_transforms`,
`quicktools.mirror_apply`, `quicktools.origin_to_selected`, `quicktools.cut_and_solidify`,
`quicktools.apply_construction_material`, `scene.update_subpart_instances`.

Mirroring and mountpoint modes are toggles on `scene.seut` (`mirroringToggle`, `mountpointToggle`); the
wiki says turning the mode off saves the values. The values themselves (`mountpointAreas`, `mirroring_X/Y/Z`)
can be set from script and are exported to the SBC (see "Export through the MCP"); the interactive modes and
their empties were not exercised.

From the wiki Add & Context Menu page [HARD, wiki]: `Add Highlight Empty` needs the target object selected and
an index unique per highlight type; `Add Dummy` takes a dummy type and an index unique per dummy type (not all
types take an index); `Add Preset Subpart` takes the block's `TypeId`-based subpart type and an index; `Add
Custom Subpart` takes only a name (for subparts animated by script). The page lists no types: read them from
SEUT's `empties` module.
