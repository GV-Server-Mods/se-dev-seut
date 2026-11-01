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
col.data.uv_layers.new(name="UVMap")   # bmesh meshes have no UVs; without one MwmBuilder fails (E044)
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

- **Small-grid blocks** [HARD, run]: a scene with `gridScale = 'small'` exports as a *Large* block by default
  (`<CubeSize>Large</CubeSize>`, model path under `Models\Cubes\large\`), because the export flags default to
  `export_largeGrid = True`, `export_smallGrid = False`. Set `export_smallGrid = True` and
  `export_largeGrid = False` for a small block to get `<CubeSize>Small</CubeSize>` and `Models\Cubes\small\`. There
  is also `export_medium_grid` (the video's "large to medium", no scaling). The SBC model path comes from these
  flags, while the `.mwm` goes to `export_exportPath`, so a mismatch gives an SBC that points at a file that is
  not there; keep the folder's `large` or `small` in step with the flags. The SBC `Size` swaps Y and Z: a
  bounding box of 1 x 2 x 1 cells gave `Size x=1 y=1 z=2`.
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
- Icons [HARD, tested]: SEUT has its own icon renderer (`seut_icon_render.py`, the Icon Render panel). It
  builds a `Render (<SubtypeId>)` collection with an `Icon Render` empty, an `ICON` camera, key, fill and rim
  lights, and a compositor tree that gives the blue Space Engineers look (or the full colour render when
  `renderColorOverlay` is on), then `scene.icon_render_preview` renders the Main model only (LODs, build stages
  and collision are hidden for the render) and writes `<SubtypeId>.dds`, converted by SEUT's own texture
  converter (header DX10, format 99 = BC7 sRGB, 128 x 128, the same as vanilla icons). Script recipe:
  1. `scene.render.filepath = r"<mod>\Textures\GUI\Icons" + "\\"` (it must contain `Textures`; the folder is
     created if missing). The operator refuses to run while the path is still `/tmp\`.
  2. `scene.seut.render_output_type = 'dds'` (or `'png'`), `renderResolution = 128`, optionally
     `renderColorOverlay`, `renderZoom`, `renderDistance`, `renderEmptyLocation`, `renderEmptyRotation` to
     frame the shot (they move the `Icon Render` empty and camera).
  3. `scene.seut.renderToggle = 'on'` with a 3D viewport context override (as for export). Turning it on also
     activates every other scene's render setup (the video author calls that an unfortunate side effect; it
     does no damage). `look` through the `ICON` camera to check the framing.
  4. `bpy.ops.scene.icon_render_preview()` under the same override; it opens a render window and ends with
     `I018` and the file path. Then `renderToggle = 'off'`, which removes the helper objects again.
     **Close the preview window when the render is done** [HARD, tested; owner asked]: it is a small extra
     window (320 x 256, screen named `temp`) that stays open and in the way. Close every window except your own:
     `wm = bpy.context.window_manager; main = next(w for w in wm.windows if w.screen.name != 'temp')`, then
     `for w in [w for w in wm.windows if w != main]: with bpy.context.temp_override(window=w): bpy.ops.wm.window_close()`.
     Check `len(wm.windows) == 1` afterwards. Never close the user's main window.
  5. The next export with `'new'` or `'update'` writes `Icon` as `Textures\GUI\Icons\<SubtypeId>.dds` because
     that file exists under `scene.render.filepath`. Copy the file into the mod's `Textures\GUI\Icons`.
  Icon style [owner, 2026-10]: vanilla icons currently use the blue filter, which is SEUT's default. The
  owner says the Warfare III update (due the following month) changes all vanilla icons to full colour, so
  for new blocks set `renderColorOverlay = True`, which skips the blue conversion nodes (the video author also
  offers the full colour render as an option). Confirm against the game's current icons if the user is
  matching a specific version.
  `scene.copy_render_options` and `scene.copy_render_offset` copy these settings to every scene in the file.
  Run on scratch block `S4Test` [HARD, tested]. An earlier version of this skill said SEUT could not make an
  icon; that was wrong. The Pillow route (render a PNG, `Image.save('X.dds', pixel_format='DXT5')`) still
  works as a fallback [HARD, tested] but needs the `seut` collection left visible. Icon loading in game is
  [SOFT, not yet seen].
- In game [HARD, owner test]: a local mod folder containing only this SBC and the `.mwm` loads and the block can
  be placed. Gaps seen: the placeholder icon is ugly (render a real one with SEUT's icon renderer, above);
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

## Moving parts between .blend files, LODs from script [HARD, run on SEUT 1.2.1 / Blender 4.5.10]

- **Crash rule:** snapshot before mutating. A loop over `col.all_objects` that created and removed meshes
  crashed Blender (access violation in `pyrna_prop_collection_iter_next`, crash log in `%TEMP%`). Use
  `objs = list(col.all_objects)` first. Save the .blend before each step; the crash loses unsaved work.
- **Appending parts:** `bpy.data.libraries.load(path, link=False)` with `dst.objects = [names]` pulls the old
  parent in as `<Name>.001` as well. Compute the world matrix *before* removing that parent, from the parent's
  `matrix_basis`: `parent.matrix_basis @ o.matrix_parent_inverse @ o.matrix_basis` (for a one-level hierarchy).
  Do not trust `matrix_world` of appended objects that are not linked to a scene yet [HARD, seen]: a parent
  stored at z = -2.5 with a 180 degree turn reported an identity `matrix_world`, which put every child in the
  wrong place. (An earlier append looked fine only because that parent sat at the origin.) Then
  `o.parent = None; o.matrix_world = mw`, link to the target collection, `o.parent = new_root;
  o.matrix_parent_inverse = new_root.matrix_world.inverted()`. Remove the `.001` leftovers and
  `bpy.data.orphans_purge()`, or highlight links and W007 resolve to the wrong objects.
- **Rigid bodies survive an append** (`o.rigid_body` is kept) even with no rigid body world in the new scene.
- **Highlight links** (`empty.seut.highlight_objects[i].obj`) keep working when both the empty and the mesh
  are re-parented; reassign `.obj` by hand if the mesh was renamed.
- **LOD from script** without join/decimate operators: for each source mesh build a `bmesh`, apply
  `bmesh.ops.transform(bm, matrix=o.matrix_world, verts=bm.verts)`, remap `material_index` onto one shared
  material list, merge into one mesh, add a `DECIMATE` modifier (ratio about 0.35 for LOD1, 0.12 for LOD2),
  then `bpy.data.meshes.new_from_object(ob.evaluated_get(depsgraph))` and swap `ob.data`. Link the temporary
  object to the scene shown in the window (`bpy.context.scene`), not to the subpart scene you are building for:
  the evaluated depsgraph is the window's, so an object in another scene comes back undecimated [HARD, seen:
  every subpart LOD kept full detail on the first run]. Drop text and small
  pipes from LOD2. **Do not leave out `detector_*` meshes** [HARD, owner saw the yellow conveyor ports vanish
  at 50 m in game]: in a vanilla model the `detector_conveyor_section_*` meshes are the visible yellow port
  frames (272 `PaintedMetal_Yellow` faces each) and `detector_terminal_section_*` are the keypad panels, not
  hidden highlight helpers. A first LOD build skipped them, so both LODs had no ports or keypads; the fix was
  to include them. Compare the face count per material of every LOD against Main before exporting: a material
  that is in Main and missing from a LOD is a bug. **Protect flat decal faces from the decimation** [HARD, seen]:
  a global Decimate also collapsed all 60 `Decals` faces (flat quads just above a surface) to zero. Split the
  merged mesh by material, decimate only the shell, then add the untouched faces of `Decals`, `Terminal`,
  `TextAtlas` (LOD1), `ButtonsAtlas_*`, `Atlas3_*`, `Conveyor` and other tiny accent materials back. Link the
  object to the `LODn (...)` collection and the export wrote the LOD `.mwm` files and the
  `<Model><LOD Distance=...>` XML (25 / 50) with no other setup. Final crate: LOD1 7595 and LOD2 3415 faces
  (ratios 0.5 and 0.25 on the shell), export well under a second.
- A SEUT scene exported this way produced `Models\<Subtype>.mwm`, `_LOD1`, `_LOD2` (plus a `.hkt.mwm` that the earlier install of the same block did
  not need) directly under `Models`; copy the three `.mwm` files into the mod's `Models` folder (LOD paths are
  relative to the mod root).

### `import_complete` and `export_all_scenes` [HARD, run on SEUT 1.2.1 / Blender 4.5.10]

- **`scene.import_complete(filepath=<main .fbx>)`** imports the main FBX plus every `<name>_LODn.fbx`,
  `<name>_BSn.fbx` / `_Construction` file and a `<name>.hkt` found in the same folder, into the active scene
  (set its `sceneType` and run `recreate_collections` first). It sets the scene's SubtypeId to the file's base
  name, fills `Main`, `LOD1`, `LOD2`, and attaches the `.hkt` as the collection's external `hkt_file` (no
  collision objects). It returned `4 of 4 files successfully imported (I021)`. LOD and BS collections are left
  hidden in the view layer. Call it as `getattr(bpy.ops.scene, 'import_complete')(filepath=...)` under the
  usual `temp_override`.
- **Round trip:** a block exported, imported with `import_complete` into a fresh scene and exported again gave
  `.mwm` files of identical size, and the imported Main collection had the same 71 objects. `.mwm` sizes are
  not good evidence on their own: they came out as a power of two plus 428 bytes (1,049,004 = 1 MiB + 428;
  524,716; 131,500; 262,572), so a model with 50 percent more faces can have the same size. Compare object and
  face counts, or hash the files, instead.
- **`scene.export_all_scenes()`** (needs a VIEW_3D override and Object mode) loops every main, subpart,
  character and item scene and runs the normal export on each. With one scene in the file it worked
  (`I008`, `1 of 1 scenes`). **With a second scene in the file (here the one filled by `import_complete`)
  it crashed Blender 4.5.10 twice** (access violation in `BKE_base_eval_flags` on a depsgraph worker thread,
  right after the operator started). Exporting that second scene alone with `scene.export` worked. So from
  script, export scene by scene (set `window.scene` and `window.view_layer` yourself, `view_layer.update()`,
  save, then `scene.export` under the override) instead of calling `export_all_scenes` on a multi-scene file.
  Cause not established; it may only happen when the operator switches `window.scene` under a script override.
- `export_sbc_type` read back as `'new'` after a save and reload even though it was set to `'none'` before
  the save, and the export then wrote an extra `<Subtype>_1.sbc` next to the existing one. Read the value
  just before exporting and clear stray `_1.sbc` files.

### Shaped parts and edge wear from script [HARD, used on the gatling turret]

- **Profile prism:** build a 2D outline (rounded rectangle, clevis tab = base edge plus a half circle around
  the pin, U cradle = rectangle with an arc cut) and extrude it with a local frame matrix whose X and Y span the
  outline's plane: `M = Matrix((ex, ey, ex.cross(ey))).transposed().to_4x4(); M.translation = origin`. A pad
  "parallel to a sloped face" uses `ex` = the slope direction and `ey` = the world axis along the face.
  Triangulate the caps of concave outlines (`bmesh.ops.triangulate`) before export.
- **Booleans:** cut pockets into the *unbevelled* solid first, then bevel; an exact boolean on an already
  bevelled mesh produced stray geometry. A feature that pokes through the far side of a plate shows as a dark
  slot there: ray-cast from the camera (`scene.ray_cast`, with helper objects hidden) to find which object it is.
- **Triangle budget** [HARD, measured on a large turret]: the first full detail pass reached about 74,000
  triangles, almost all from over-segmented round parts. Segment counts that still read smooth at play distance:
  48 around a 2 m radome (14 rows in its cap), 64 for 2.7 m turned rings, 40 for 0.5-1 m rings and drums, 28-32
  for 0.5 m cylinders, 12-16 for barrels, pins and tubes under 0.15 m, 8 for hoses. That pass brought it to
  about 43,600 with no visible faceting. Count early (sum `len(p.vertices) - 2` over polygons per object).
- **Angle-limited bevels and segment counts**: a 12-sided cylinder's side edges meet at exactly 30 degrees, so a
  Bevel with `angle_limit = 30` bevels every side edge and multiplies the triangles. Use 14 or more sides, raise
  the limit, or skip the bevel on small cylinders (barrels, pins, piston bodies). Small hex bosses need no bevel.
  The same trap hits shading: a 30-degree smooth-by-angle marks every side edge of a 12-sided (and a 10-sided,
  36 degrees) cylinder sharp, so barrels and piston rods render faceted [owner]. On round parts, smooth edges
  under 40 degrees, then add a Weighted Normal modifier (`FACE_AREA`, weight 50, `keep_sharp`) and apply it so
  flat caps stay flat while sides and rim bevels read round. Leave boxes on the 30-degree rule, or their flat
  faces pick up gradients from smoothed bevels.
- **Buried faces** [HARD, took a turret from 43,600 to 39,000 triangles with no visible change]: a face is
  hidden when all its corners and its centre, nudged 0.5 mm along its normal, lie inside another closed solid.
  Split every mesh into connected islands in world space and keep only closed ones (every edge has two faces);
  build a `BVHTree.FromBMesh` per island and test points by ray parity in two directions (an odd hit count
  both times means inside). Compare only against solids of the same moving part, so no rotation can reveal a
  deleted face, and skip decals, glass, screens and vanilla parts. Do a dry run listing counts per object, then
  delete the faces plus loose edges and verts, and render the busiest areas (muzzle, hubs, drum) to check for
  holes. The biggest wins were rod and tube ends inside housings, flash hider bases inside the muzzle collar,
  bands and straps sunk into a drum or servo pack, and the radome's lower rim inside the plate.
- **Many small cuts:** an exact boolean that slots six small turned tubes at once collapsed them to fragments
  (two tries). Build such features by construction instead: a slotted flash hider is a base ring, three
  partial tube sections (wall rings swept over an angle range, capped at both ends) and a lip ring. Build each
  copy from a base pattern rotated by its position angle so a cluster stays radially symmetric [owner].
- **Odd-shaped decals:** to take one piece out of a sheet where its bounding box overlaps a neighbour (the solid
  chevron of the Atlas2 double arrow), make the decal face the piece's outline (six corners for a chevron) with
  UVs on the same outline in pixel space, then triangulate. The transparent gap around the piece keeps the
  edges clean.
- **Edge-only wear:** `md = ob.modifiers.new('bev','BEVEL'); md.material = 1`, then give the mesh the slots
  `[PaintedMetal_Darker, PaintedMetalScratched_Darker]` so only the bevel faces get scratches. For meshes that
  are already bevelled, set `material_index = 1` on faces where `area / longest edge < 0.03`.
- **Bolt decals:** `Decals_Atlas_A_01` row "eleven bolt and fitting heads" (`atlas-regions.md`, region 1), one
  head per quad. Measured boxes from the alpha mask: hex nut u 0.0957-0.1226 v 0.9722-0.9961, round domed head
  u 0.1587-0.1846 v 0.9717-0.9971, hex socket in a ring u 0.3135-0.3428 v 0.9697-0.9990. Material `Decals`,
  quad 1.5 mm off the surface (3 mm looked like floating heads in game [owner]). Turn every head to a random angle about its normal (and every 3D nut about its
  axis) so they look individually tightened [owner]. Keep real 3D bolts few and low (about 12 mm tall).
  A flat hex decal alone reads as a pale sticker on dark metal (the sheet's colour is light grey, and the darker
  `Decals_Atlas_A_02` sheet used by `PanelingDarker` has the same light bolt row) [owner]. What worked: bolts of
  5 cm and up sit on a low 3D hex boss (about 16 mm; 10 mm read too thin [owner]; the block's dark metal, wear on
  its bevel) with the hex decal on top at about 90% of the boss top's width. The hex in the decal has its corners
  on the decal's up axis, while a 6-segment cone has its first corner on local +X, so turn one of them 30 degrees
  about the normal [HARD, the owner saw every head 30 degrees off]. Smaller bolts get head 3 of the row (u
  0.0635-0.0928, v 0.9697-0.9990, a dome inside a recessed ring in the normal map) about 1.5 times their size
  underneath as a counterbore, about 1 mm lower. Fit each ring to its face: ray-cast 16 rim points down with a
  2 mm tolerance and a normal check, shrink until all land on flat face, drop it otherwise (a 2 cm tolerance let
  rings lap over a pad's bevel).
- **Decal offset** [HARD, measured; owner saw floating bolt heads in game]: build one `BVHTree` from every
  non-decal mesh in the scene (world space), then for each decal face `ray_cast(centre + n * 0.0001, -n, 0.06)`
  and list the gaps. To normalise, split each decal object into connected islands: a flat island moves as a
  whole by `target - min(gap)` along its normal (per-vertex rays would miss where a decal overhangs a small
  boss); an island on a curved surface sets each vertex to `hit + n * target` along its vertex normal. Targets
  1.5 mm, and 0.7 mm for rings under bolt heads. The first pass found heads at 3-4 mm, one ring 26 mm off its
  face and another at 0.1 mm (a z-fighting risk). Rebuild LODs afterwards, since they copy the decals.
- **Decals on curved surfaces:** split the quad into columns that follow the radius (8 columns for a 0.4 m
  sign on a 1.05 m cylinder) instead of one flat quad, which would float or sink by about 2 cm at the edges.
  Check text direction in a render: the first try read mirrored, fixed by reversing U (`u = u0 + u1 - u`).
- **Preview renders:** Workbench in Texture mode shows only one image of a SEUT material (often the mask) and
  exaggerates wear; EEVEE (`BLENDER_EEVEE_NEXT` in 4.5) with a sun lamp and a grey world reads closer to the
  game, but the in-game shader still differs.

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
wiki says turning the mode off saves the values. Both work from script (section below); the values
(`mountpointAreas`, `mirroring_X/Y/Z`) are exported to the SBC (see "Export through the MCP").

## Subparts, dummies, mirroring and mountpoints from script [HARD, run on SEUT 1.2.1 / Blender 4.5]

Test pair: a main scene `SPTurret` and a subpart scene `SPBarrel` (`sceneType = 'subpart'`, same
`recreate_collections` recipe as above), with every operator called under `bpy.context.temp_override(scene=...,
view_layer=scene.view_layers[0], window, area, region)` using the 3D viewport as for export.

- `scene.add_dummy(detector_type='muzzle_projectile_', index=1)` makes `muzzle_projectile_1`;
  `scene.add_custom_subpart(name="subpart_Barrel")` and `scene.add_preset_subpart(detector_type=..., index=..)`
  make an ARROWS empty with a `file` custom property. **None of them parent the new empty to the selected
  object**: the operators test `if 0 in context.selected_objects`, which is never true [HARD, source read and
  seen in the run]. The empty lands unparented in the active collection, so parent it yourself
  (`empty.parent = root; empty.matrix_parent_inverse = root.matrix_world.inverted()`) or you get W005 or W006,
  and rename it if the default is not what you want. Preset subpart names are fixed keys such as
  `subpart_DoorLeft`, `subpart_Barrel`, `subpart_GatlingTurretBase1`, `subpart_PistonSubpart1`,
  `subpart_HangarDoor_door` (23 presets in `empties['preset_subparts']`, none uses an index).
- **Linking a subpart scene to its empty** is the property `empty.seut.linkedScene = subpart_scene`, and its
  update callback is fragile [HARD]: it acts on `context.view_layer.objects.active` (not on the empty being set),
  writes `empty['file'] = <subpart scene name>`, and, when `scene.seut.linkSubpartInstances` is true, duplicates
  the subpart's objects into the main scene while switching `window.scene`. A scripted set with another
  object active crashed Blender 4.5.10 (access violation in the depsgraph, `rna_ViewLayer_update_tagged`; crash
  log supplied by the owner). Safe recipe, which ran clean: save the file first, set
  `main.seut.linkSubpartInstances = False`, make the empty the only selected and active object in the main
  scene's view layer, then set `linkedScene`. The export does not need the instance objects (see the
  `update_subpart_instances` note below).
- Exporting the subpart scene and then the main scene (same export folder) wrote `SPBarrel.mwm` and `SPTurret.mwm`;
  the main model's dummy list contains `subpart_Barrel` with the property `file = SPBarrel`, which is how the
  game finds the subpart model. The subpart scene exports FBX with `axis_forward = '-Z'` where main scenes use
  `'Z'` (`seut_export_utils.py`, with the comment that the other value breaks subpart orientation), so the
  subpart is deliberately turned 180 degrees about the up axis relative to a main model; see
  `doors-subparts.md` for what that means when placing empties. An FBX re-import could not show the difference
  (the importer reads the axes back), and the in-game result was not checked.
- Mirroring mode: `scene.seut.mirroringToggle = 'on'` creates three empties and three plane meshes (`Mirror
  LeftRight`, `Mirror FrontBack`, `Mirror TopBottom`) in a `Mirroring (<SubtypeId>)` collection. Rotate an
  empty in 90 degree steps and set the toggle to `'off'`: SEUT prints `I016` per empty and stores the result
  and removes the collection. Observed: LeftRight rotated 180 degrees about Z gave `mirroring_X = 'Y'`; TopBottom
  rotated 90 degrees about X gave `mirroring_Z = 'HalfX'`; FrontBack unrotated stayed `None`. In the SBC they
  came out as `<MirroringX>Y</MirroringX>` and `<MirroringY>HalfX</MirroringY>` (TopBottom is Blender Z, SBC Y).
- Mountpoint mode: `scene.seut.mountpointToggle = 'on'` creates six full-face plane meshes
  (`Mountpoint Area Front` and so on, 2.5 x 2.5 on a large cell). Move or scale them in Object Mode and turn the
  toggle off: SEUT prints `I017` per face and fills `mountpointAreas` (`side`, `x`, `y`, `xDim`, `yDim`, metres
  from the face centre). Check the sign: the front face area moved by +0.25 m on its X and halved in width
  (1.25 m) exported as `StartX=0.15 EndX=0.65`, which is a centre at -0.25 m, so the offset sign is inverted
  on that side. Verify each face's direction with the BuildInfo overlay in game, or pre-compute the expected
  numbers, before trusting a one-sided area.
- All six faces were written when only one was changed. Deleting an area object (`bpy.data.objects.remove`) while
  the mode is on removes that face from `mountpointAreas` when you turn it off, so a block with one mount face
  keeps just that one. `scene.add_mountpoint_area()` with an area object active makes a second full-face area
  on the same side (`Mountpoint Area Front.001`, saved as another `front` entry). Turning the mode on again
  reloads the stored areas.
- `scene.update_subpart_instances` only sets `linkSubpartInstances` False then True (`seut_utils.py`), which
  runs `link_subpart_scene` for every linked empty. Run from script it created no instance objects in the main
  scene and left the window on the subpart scene (restore it with `bpy.context.window.scene = main`); it did
  not crash with the empty active. The export does not need the instances, so for scripted work leave
  `linkSubpartInstances = False` and judge placement from the subpart scene itself. Seeing a subpart in place
  in Blender is a UI-only convenience for now [SOFT].

### Quick tools [HARD, source read and run]

All are `quicktools.*`, need `'SEUT' in scene.view_layers`, and behave like this:

- `add_bevels`: for each selected object runs `shade_smooth_by_angle()` (30 degrees) and adds a Bevel modifier
  with `harden_normals = True`, but the width is hard coded to **0.0025 m** and the `bevel_amount` property is
  ignored [source and run: asked for 0.05, got 0.0025]. That is a hairline bevel. Set `modifier.width` yourself
  to a visible chamfer (`modeling-rules.md`) and apply the modifier. `remove_bevels` only deletes Bevel modifiers,
  not bevels already applied.
- `apply_transforms`: removes the rigid body from each selected object, then applies location, rotation and
  scale. **The rigid body is not put back**, so a collision object loses its shape: re-add
  `bpy.ops.rigidbody.object_add()` and the collision shape afterwards [run: `rb after False`].
- `apply_construction_material`: the file must already contain a material named `Construction` (link it from the
  SEUT material library). Each selected object's slots become `<name>_Chrome` when that material is loaded in
  the file, otherwise `Construction`. Run: `PaintedMetal_Colorable` became `Construction`.
- `cut_and_solidify(inset_thickness=0.025, solidify_thickness=0.015)`: edit mode only, with faces selected; it
  insets each selected face individually, deletes the inner faces and applies a Solidify modifier, which gives
  the open scaffold shell. Run on a 2 x 2 x 1 m box with its four side faces selected: 6 faces became 52. The new
  faces get **zero-area UVs** (16 of 52), so re-run `uv.smart_project` on the mesh before export or the
  model risks the shaderless warning (E032 family).
- `mirror_apply(axis='x')`: object mode, mirrors the selected objects with `transform.mirror`, applies all
  transforms and flips normals. Run on a cube at x = 2: it ended at x = -2 (mirrored about the world origin,
  vertex x 1.8 became -1.8). `origin_to_selected`: edit mode with exactly one vertex, edge or face selected; run
  with the top face of a unit cube selected, the object's origin moved to that face's centre (location
  (-2, 0, 0.5)). Both ran without error from a script.
- Build stage export [HARD, run]: a mesh in `BS1` with the Construction material exported
  `<SubtypeId>_BS1.mwm` and an SBC `<BuildProgressModels>` with one `Model BuildPercentUpperBound="1.00"` entry
  (the path includes the export subfolder, here `Models\Cubes\large\turret\`). `BS1` needs no collision of its
  own.

From the wiki Add & Context Menu page [HARD, wiki]: `Add Highlight Empty` needs the target object selected and
an index unique per highlight type; `Add Dummy` takes a dummy type and an index unique per dummy type (not all
types take an index); `Add Preset Subpart` takes the block's `TypeId`-based subpart type and an index; `Add
Custom Subpart` takes only a name (for subparts animated by script). The page lists no types: read them from
SEUT's `empties` module.
