# Kitbash from vanilla models first

When a block should look like a vanilla one (a cargo-style crate, a conveyor frame, a terminal panel, a
door, an armor edge), start from the vanilla model's own parts instead of modelling similar shapes from
scratch. Three reasons [owner request, SOFT]: the parts already carry Keen's bevels, UV density, material
choices and shading; it takes far fewer agent steps than rebuilding them; and the result matches the game's
look without effort. Model from scratch only for shapes that no vanilla part covers.

A model that reuses a vanilla part may reuse only parts, not the whole file: copy the pieces you need
(frame corners, port frame, terminal panel, handle) and leave the rest. Vanilla models are Keen's assets; for
a server mod that is shared or published, check the owner is happy with that [ask, do not assume].

## Where the parts are

`<ModSDK>\OriginalContent\Models\Cubes\large\*.FBX` and `...\small\*.FBX`, each with an `.xml` that lists
the materials and LODs (`C:\Program Files (x86)\Steam\steamapps\common\SpaceEngineersModSDK` on a Steam
install). Find the model a block uses by looking up its SubtypeId in `Content\Data\CubeBlocks\*.sbc` and
reading `<Model>`. Do not guess from the block's name (`ArmorCenter` is not the armor cube).
`CargoContainerSmall` has 55 meshes and 12 empties under one root, about 2.49 m across: six
`LargeConveyorFrame_00n` corner/frame meshes, six `detector_conveyor_section_00n` port frames, six
`detector_terminal_section_00n` panels, and the rest. Read `interaction-highlights.md` for its detectors.
`CargoContainerLarge` (the large-grid large container, 3x3x3 cells) has the same kit at a bigger size [HARD,
names read from the FBX]: the root, six `LargeConveyorFrame` meshes, six `detector_conveyor_section` port frames,
six `DoorTerminalFrame` keypad frames, six `detector_terminal_section` panels, eight `airtight_edge` pieces,
three `Line` meshes, `Protection_Bars` and `metal_pipe`. Its `_LOD1..3.fbx` and
`CargoContainerLargeConstruction_1..3.FBX` beside it are ready starting points for the LODs and build stages
of a block kitbashed from it.

Another source: you can export a grid from the game itself, including modded blocks [owner tip, credit to
Brd; video by Chipstix213]. Face the grid in game and press Ctrl+Alt+E. The warning says modded blocks cannot
be exported, but they can. The files land in a `SpaceEngineers_ExportedModels` folder on the desktop, and the
FBX files import into Blender like the SDK ones. Not tried by this skill.

## Preferred import: SEUT's own importer [HARD, run on SEUT 1.2.1 / Blender 4.5]

Use `scene.import` (SEUT's "Import FBX") first; the raw recipe below is the fallback. It converts the FBX with
the bundled FBX2glTF tool, imports it into the active collection, and remaps the materials to SEUT's library.
Run on `CargoContainerSmall.FBX` it took about 24 s and gave a far cleaner result than the raw import:

- 67 objects (55 meshes, 12 empties) under one root `CargoContainerSmall`, root scale 1.0 (the raw import has
  0.01 and a rotation), world Z up, true metres; 97 material slots in total (at most 4 per mesh, not ~100);
  materials are the linked library ones, with one stray local `Material` to delete; a single `UVMap` layer;
  custom normals kept, so no smoothing pass is needed.
- Highlight empties already have their `seut.highlight_objects` link, `CUBE` display, size 0.5.
- **It also gives the clean vanilla look**: the port frame comes out as `PaintedMetal_Yellow` 272, `Metal_Dull`
  476, `Conveyor` 2, the keypad frame and text banner as `PaintedMetal_Darker` only, and the grey outer frame as
  `PaintedMetal_Colorable` only. The raw FBX import instead gives `PaintedMetalScratched_*` on a share of the
  faces, which is what the owner saw as scratched edges that vanilla does not have (see "Match the vanilla look").
  So the importer's mapping is the one that matches the game.

```python
imp = getattr(bpy.ops.scene, 'import')          # `import` is a Python keyword
vl = scene.view_layers[0]                       # make the scene's Main layer collection active first
with bpy.context.temp_override(scene=scene, view_layer=vl, window=win, area=area, region=region):
    imp(filepath=FBX)                           # wrap in contextlib.redirect_stdout if it is chatty
```

Gotchas:
- **Object names are global to the .blend.** If an object of the same name already exists in another scene,
  Blender names the import's copy `Name.001`, and the highlight links of the imported empties then resolve to
  the *old* same-named objects: W007 "different parent objects" on export, for 8 of 12 empties in the test.
  Import into a scene of a clean file, or delete earlier imports of the same model first, and check
  `empty.seut.highlight_objects[0].obj.parent` equals `empty.parent`.
- The imported root is a mesh with the whole container as children, so keep the parts you want, reparent them
  under your own single root (E031), and delete the rest, as in step 3 onward below. Delete the imported scene,
  unused materials and the stray `Material` afterwards.
- A direct export of the imported model with no changes works (MWM written), so it is a safe base to cut down.

## Raw import recipe, fallback [HARD, tested on SEUT 1.2.1 / Blender 4.5]

Import into a throwaway scene, keep what you want, and clean up. A raw import is messy: it gives every
mesh a slot for every material in the file (about 100), creates the materials as plain local copies, and
leaves thousands of unused materials behind.

```python
import bpy, io, contextlib
FBX = r"<ModSDK>\OriginalContent\Models\Cubes\large\CargoContainerSmall.FBX"
MAT = r"C:\SE_Assets\Materials\Materials.blend"          # <SEUT Assets>\Materials
before = set(bpy.data.objects.keys())
tmp = bpy.data.scenes.new("kb_tmp"); bpy.context.window.scene = tmp
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    bpy.ops.import_scene.fbx(filepath=FBX)                # prints thousands of lines otherwise
new = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
meshes = [o for o in new if o.type == 'MESH']

# 1. drop the unused material slots on every mesh. Clearing the slots RESETS every face's material index to 0,
#    so save the new indices first and write them back after the slots are rebuilt.
def trim_slots(me):
    idx = [p.material_index for p in me.polygons]
    used = sorted(set(idx))
    mats = [me.materials[i] for i in used]
    remap = {old: new_i for new_i, old in enumerate(used)}
    new_idx = [remap[i] for i in idx]
    me.materials.clear()
    for m in mats: me.materials.append(m)
    for p, i in zip(me.polygons, new_idx): p.material_index = i
for o in meshes: trim_slots(o.data)

# 2. swap the local copies for the linked vanilla materials (names match)
names = sorted({m.name for o in meshes for m in o.data.materials if m and not m.library})
with bpy.data.libraries.load(MAT, link=True) as (src, dst):
    dst.materials = [n for n in names if n in src.materials]
linked = {m.name: m for m in bpy.data.materials if m.library}
for o in meshes:
    for i, m in enumerate(o.data.materials):
        if m and not m.library and m.name in linked: o.data.materials[i] = linked[m.name]
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)
```

Result in the test: 13 materials used, all 97 slots remapped to linked library materials, none missing,
3131 data blocks purged.

**Check the faces keep their materials.** The first version of this recipe cleared the slots before writing
the indices, so every vanilla part ended up with a single material: in game the port frame came out all
yellow, with no door panel texture and no metal handle edges, while the vanilla container beside it looked
right [HARD, owner screenshot]. After trimming, count faces per material on a multi-material part, for
example `detector_conveyor_section_004` imports with four (`PaintedMetal_Yellow` 160,
`PaintedMetalScratched_Yellow` 112, `Metal_Dull` 476, `Conveyor` 2). The same trap applies to LOD meshes
trimmed after a join: fix it the same way, or the LODs and the main model look different.

**Match the vanilla look, not the SDK FBX materials.** The owner compared the kitbashed port with a vanilla
container in game [HARD, owner screenshot]: the vanilla yellow frame is clean, ours had scratch and chip wear
along its edges. The raw FBX import gives 112 faces of the frame `PaintedMetalScratched_Yellow`, and the shipped
`CargoContainerSmall.mwm` also names that material, but SEUT's own importer (previous section) assigns the clean
materials, which matches what the owner sees in the game. If you use the raw route, fix it by hand: swap the scratched slot for `PaintedMetal_Yellow` on that
part and merge the duplicate slot (port frame result: `PaintedMetal_Yellow` 272, `Metal_Dull` 476,
`Conveyor` 2). The owner found the same on the keypad frame (`DoorTerminalFrame`) and the dark text banner
(`TextSign`): vanilla is clean, ours had `PaintedMetalScratched_Darker` on 208 and 196 faces, swapped to
`PaintedMetal_Darker`. The grey outer port frame (`LargeConveyorFrame`, `PaintedMetalScratched_Colorable`) was
left as imported and not compared. General rule: after a kitbash, put the new block next to the vanilla one in game, and where a
kitbashed part looks worn and the vanilla one does not, use the clean variant of the material. Do not
assume the FBX material names are what the game renders.

3. Move the parts you keep into the block. The imported root has scale 0.01 (the meshes are in cm), so
   unparent each kept object keeping its world transform, then apply scale:
   `mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw`, then select it and
   `bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)`. Link it into `Main (...)`
   with `main.objects.link(o)` and unlink it from the throwaway scene. World size is true metres
   afterwards (a `LargeConveyorFrame` piece measures 2.0 x 0.28 x 2.0 m).
4. Reparent the kept parts under your block's single root object (E031), delete the throwaway scene
   (`bpy.data.scenes.remove`) and purge orphans again.
5. Rename or delete vanilla empties you copy. Their names carry over (`detector_conveyor_5`, and `.001`
   suffixes when the name already exists), and object names are global to the file.

## Gotchas from the rebuilt antenna crate [HARD, run in Blender 4.5 and exported]

- After `scene.recreate_collections` the scene's only view layer is named `SEUT`. Once you switch the window
  to the throwaway scene, `bpy.context.view_layer` is that scene's `ViewLayer`, and select/active calls on
  objects of the block fail ("ViewLayer 'ViewLayer' does not contain object"). Switch back and use
  `scene.view_layers[0]`.
- Imported vanilla meshes are flat shaded (`use_smooth` false) but carry custom normals, so they already
  look right. Do not run `shade_smooth_by_angle` on them; smooth only the parts you built.
- Vanilla meshes name their UV layer `UVChannel_1`; yours is `UVMap`. Joining them (for a LOD) keeps both
  layers and leaves zeros in the one a part did not have, which gives zero-size UVs. Rename every part's
  single UV layer to `UVMap` before `bpy.ops.object.join()`.
- Raw-imported detector empties have no SEUT highlight link, only a `highlight` custom property holding the
  mesh name. Set `empty.seut.highlight_objects.add().obj = bpy.data.objects[empty['highlight']]` for each,
  and set the empties to `CUBE` display, size 0.5. Their object scale already holds the detector size.
- The vanilla container has a port frame, panel and terminal on every face. Remove the ones on a face that
  another part covers (the test crate's top, under the tower: `LargeConveyorFrame_005`,
  `detector_conveyor_section_005`, `detector_terminal_section_005`, their text/sign meshes and empties).
- Parts stick out about 0.04 m past the 2.5 m cell (port frames, text signs); the box collision stayed 2.5 m.
  On a mounting face, set the face about 5 cm inside the cell so they end flush (`design-detailing.md`, "Think
  about the neighbours").
- Size: the whole container was 13,929 polygons with the tower parts and the main `.mwm` came to 2.1 MB.
  A joined copy decimated with `ratio 0.25` gave 3,466 polygons for LOD1 and `ratio 0.06` of the big parts
  gave 349 for LOD2. A LOD must be one unparented object per LOD collection, with the materials trimmed to
  the used slots.
- To make a kitbashed block behave like the container (conveyor ports, inventory, terminal, and the debug draw
  of model dummies), give it the container's `TypeId`: `<Definition xsi:type="MyObjectBuilder_CargoContainerDefinition">`
  with `<TypeId>CargoContainer</TypeId>`. A plain `CubeBlock` draws no dummies in the debug overlay
  (`references/interaction-highlights.md`).
- **Conveyor-only vs inventory blocks** [SOFT, owner]: when kitbashing conveyor sections, distinguish between
  inventory-accessible ports and pure conveyor routing. For blocks with inventory (cargo, refinery, assembler),
  keep the full hatch style with crossbars, latch strips, and terminal. For blocks that are conveyored only for
  structural routing with no inventory (like the vanilla Structural Platform Conveyor or conveyor pipes), omit
  the crossbars and cargo hatch hardware — a clean port frame and recessed shutter is standard. The shutter uses
  `Conveyor_Yellow` (painted yellow, not dark grey `Conveyor`), and the conveyor empty must omit any mesh highlight.

## Kitbash rules

- Take the shell parts first (frames, corners, bevelled edge pieces, port frames, panels, handles), then
  add only what the design needs on top. Keep the vanilla part's materials and UVs as they are.
- Scale a vanilla part only when it must fit a different size, and keep the scale uniform so bevels and
  UV density stay consistent. To make a part longer or wider (a frame beam spanning more cells), cut it
  across its straight middle and move the vertices on one side of the cut; the ends, bevels and texture scale
  stay as Keen made them. The stretched faces stretch their texture with them: refit their UVs
  (`bpy-recipes.md`, "Moving vertices of a textured part").
- **Decals on a stretched part** [HARD, owner marked the faults on a render]. Keen's frame lines are often joined
  into one piece (a side, a chamfer and a corner), so moving each connected decal piece whole breaks the frame
  where the plate stretches. Stretch line decals vertex by vertex, with the same cut as the plate, and put the
  cut where only straight lines along the stretch cross it, never through a chamfer line (check that every
  outline edge crossing the cut runs along the stretch). Move vents, bolts and plates whole. Those by the
  part's root, where it meets the beam it hangs from, keep vanilla's place. Those by the free edge move with
  that edge.
- The vanilla parts bring their own bevels and smooth shading. Anything you add yourself must be bevelled
  and smooth shaded the same way (`modeling-rules.md`, "Geometry and shading"; normals that match theirs:
  `bpy-recipes.md`, "Matching vanilla shading"), or it will look like a different game next to them.
- Vanilla detector empties and their linked meshes come along with the container parts. Keep the pairs
  together, rename them to unused indices, and check each empty covers its mesh
  (`interaction-highlights.md`, "Detector size").
- **Kitbashed shells are open where the vanilla walls hid them** [HARD, owner saw daylight in game]: frames,
  edge beams and corner pieces used without their container's walls leave gaps behind them, and the game draws
  no back faces, so daylight shows through up close or looking up along a side. Put a dark backing (a liner)
  behind them, facing out: a wall just inside the shells, rings out to the beams at each band, fins behind
  corner rods, closed from below as well. Test each view with two Workbench renders against a magenta world,
  back-face culling on and off: magenta only in the culled render is a hole. Render the liner in its own colour
  too, to check it shows only through the gaps.
  A liner behind the shells does not close the shells themselves [HARD, owner saw it in game after a liner had
  passed 29 renders]. Where a profile (frame rim, corner post, edge beam) sat against the vanilla wall, it is open
  under its lip: at a grazing angle the eye goes in behind the rim and the inside reads as a hollow. A dark flipped
  copy of the shell in place (`bmesh.ops.reverse_faces`) does not fix it [HARD, owner saw no change in game]: the
  hollow is painted dark but is still a hollow. Close it instead [HARD, owner in game: "way better"]: take the shell's open
  edges along each lip (`edge.is_boundary` at the lip's offset) and sweep each straight back to the panel behind,
  facing out of the hollow, in the shell's paint. Built on the lip's own vertices, the new faces round exactly like
  the shell in game (SKILL.md, vertex rounding), so no crack opens. Grazing views are what renders miss: check with
  rays from eyes 1.5-4 m out along each side, counting rays whose first face points away with no face pointing back
  in the same place, on vertices rounded as the game stores them. On a 12 m kitbashed frame that count went from
  about 44,000 to under 40, each landing on the liner 1-2 cm behind.
- **LODs and build stages from vanilla's own files** [HARD, run on a 3 x 3 mount kitbashed from
  `Structural_5_platform`, exported; not yet seen in game]. The SDK has `<Model>_LOD1..3.fbx` and
  `<Model>Construction_1..3.fbx` beside the model.
  - LOD1 and LOD2 keep LOD0's part names and layout with fewer bevels and decals. A builder that cuts and moves
    vanilla parts by role runs on them unchanged, and the LODs then switch like the vanilla block beside them
    (the platform's: 10 / 45 / 90 m).
  - LOD3 can rename or merge parts (the platform's posts and struts swapped names). Check the builder's
    folded-face count and a render.
  - `Construction_3` is LOD0 with every opaque material set to `Construction`, its Atlas4 lines in
    `Atlas4_Chrome` and most other decals dropped. Make BS3 from the finished model the same way.
  - Stages 1 and 2 are scaffolds that repeat per cell. To shrink a multi-cell block, bisect at cell boundaries,
    drop whole cells and move the outer cells in.
  - Pick the variant whose features match the block: the conveyor platform's stages show port frames on the
    sides.
  - SEUT's importer triangulates: the platform's `Construction_1` is 9,153 polygons in the raw FBX and
    19,424 triangles after `scene.import`.
- State in the report which vanilla parts were reused and which shapes had to be built new.

## Not yet tested

- `scene.import_complete` (main model plus its build stages and LODs in one step) was not run; `scene.import`
  was, and is the preferred route above.
- Exporting a block made from kitbashed parts in game (the model exports like any other; only the look was
  not checked).
