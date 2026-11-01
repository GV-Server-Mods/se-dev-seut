---
name: se-dev-seut
description: >-
  Use this skill whenever you model, set up, check, or export a Space Engineers (version 1) block, subpart, or
  prop in Blender with the Space Engineers Utilities (SEUT) addon: SEUT scene and collection setup, grid scale and
  bounding box, armor and functional block geometry, UV layout, reusing vanilla SE materials and texture atlases
  instead of baking new textures, collision (HKT) objects, LODs and build stages, mountpoints, mirroring,
  subpart and dummy empties, turret and weapon models (ConveyorSorter, WeaponCore, ToolCore), interaction
  highlights, emissive and paintable materials, and SEUT error codes (E0xx / W0xx). Also covers driving a live
  Blender through the Blender MCP (execute_blender_code, look, get_scene_info): hard-surface modeling with
  bmesh and modifiers, working from reference images, and visual checking. Use it even when the user only says
  "make a block", "armor piece", "turret model", "SE model", "model this from the picture", "export to MWM",
  or "why does SEUT say E032", and not SEUT by name.
license: MIT
allowed-tools: Read
---

# SEUT block modeling (Space Engineers 1, Blender 4.x)

SEUT turns a Blender scene into an `.mwm` model plus an SBC block definition. The game ignores Blender's
look: shape, UVs, material *name*, collision, bounding box and empties are what ship. Model for those.

Tags: **[HARD]** read in SEUT source or the wiki. **[SOFT]** inferred or field-tested, verify before relying on it.
Everything below was checked against SEUT 1.2.1 on Blender 4.5 unless marked "unverified".

## Workflow

0. **Is it installed?** If the user has no Blender, SEUT, Havok, ModSDK or converted textures yet, or an
   export fails on a path or tool, read `references/setup.md` first and walk them through only what is missing.
1. **Scene.** Create a Blender scene, set `scene.seut.sceneType = 'mainScene'`, `subtypeId`, `gridScale`
   (`'large'` or `'small'`), then `bpy.ops.scene.recreate_collections()`. Setting `subtypeId` renames the
   scene to match, so look the scene up again by its new name. Recipes: `references/bpy-recipes.md`.
2. **Size the block first.** Cell edge is 2.5 m (large) or 0.5 m (small) [HARD, `seut_bbox.py`].
   `bBox_X/Y/Z` are in cells. Origin is the block centre, so a 1x1x1 large block spans +-1.25 m.
   Keep the model in metres at export scale 1.0 unless the user says otherwise.
3. **Model into `Main (<SubtypeId>)`.** One top-level (unparented) object per exported collection
   [HARD, E031]; parent detail objects under it. Details: `references/modeling-rules.md`. **Kitbash first**:
   when a vanilla model has the part you need (crate frame, port, panel, handle), import it and reuse its
   meshes instead of rebuilding them; build from scratch only what no vanilla part covers, then bevel and
   smooth shade it. Import with SEUT's `scene.import` (`getattr(bpy.ops.scene, 'import')`), not the raw FBX
   importer; recipe and traps: `references/kitbash.md`.
4. **UVs, then material.** Link a vanilla material from the SEUT material library and lay UVs onto its
   atlas. Do not bake. Details: `references/materials.md`.
5. **Collision** in `Collision - Main (...)`: at most 10 convex objects, inside the bounding box, rigid
   body shape Box / Sphere / Capsule / Cylinder / Convex Hull. `references/modeling-rules.md`.
6. **LODs and build stages** (`LOD1..3`, `BS1..3`), then mountpoints and mirroring if the block needs them.
7. **Check before export.** Run the checklist in `references/errors.md`; most failures are UVs,
   non-ASCII names, unapplied collision modifiers, or geometry outside the bounding box.
8. **Export** (`scene.export`) needs a saved .blend, a mod path and an `...\Models\...` export folder, and a
   3D viewport context override through the MCP. Tested end to end on SEUT 1.2.1 (model, LODs, collision, SBC);
   the exact recipe and its traps are in `references/bpy-recipes.md` ("Export through the MCP"). Loading the
   result in game is a separate check the owner does; say what has and has not been tested in game.
   **Fast in-game loop** [HARD, owner]: for simple model and texture updates, no game restart is needed. In
   offline singleplayer open the admin Debug Draw menu (Alt+F11 on the owner's keys) and press "Reload
   models" or "Reload textures". Do a full game restart after changing subparts [owner: reload has failed
   to pick up subpart changes], and after dummy or collision changes [HARD, owner]: after a reload the debug
   overlay still drew the block's old two dummies although the new `.mwm` held eleven, while the new meshes
   and SBC type had loaded. A reload that shows old dummies is stale data, not a model fault.

## Driving the live Blender (MCP)

The user's real Blender session is the workspace, and every call changes their file. Work in small,
checkable steps and leave the scene tidy.

1. `get_addon_status` once (Blender version, add-on match), then `get_scene_info`.
2. Plan from dimensions and the reference before writing geometry. With a picture, read
   `references/reference-images.md` first: extract proportions into a dimension table, then build to it.
3. One change per script; print only what you need (names, counts, dimensions).
4. `look` after each meaningful change: `mode=angles` with `views` for shape, `shading=wireframe` for
   topology, `max_size` 400-512 for quick checks. Compare with the reference, fix the largest difference first.
   LOD copies and collision sit on top of the Main model, so a bare `look` shows them stacked: hide the other
   collections (`layer_collection.hide_viewport`) or offset the objects temporarily before checking one.
5. Build new work in its own scene; do not delete or reshuffle the user's objects unless asked.

Script hygiene:
- Look shader nodes up by `type`, never by name (names are localized). Read enum values from `bl_rna`
  instead of hardcoding them.
- Prefer `bmesh` and the data API; operators like `modifier_apply` need the object active and selected.
- After `bmesh.to_mesh`, call `bm.free()`; return to Object Mode before reading mesh data.
- Setting a name-synced property (SEUT SubtypeId) renames the datablock; look it up again by its new name.
- Apply scale before rigid bodies, mirror modifiers or normal edits. Switch scenes with
  `bpy.context.window.scene = sc`; `look` shows the active scene.
- Never print a mesh's material list or every custom property of an imported FBX: tens of thousands of
  characters. Print counts, then a short slice.
- Study vanilla imports in a throwaway scene, then delete the scene, objects, meshes, images and unused
  materials (materials only drop after their meshes are removed). Raw `bpy.ops.import_scene.fbx` makes
  thousands of junk material slots; SEUT's importer is cleaner.

Hard-surface build order and bmesh and modifier snippets: `references/hard-surface.md`.

Asset libraries (`search_assets`, `import_asset`) and generators (`generate_3d`: Tripo, Hunyuan3D, Hyper3D,
Meshy) are off until the user enables them, and generation can cost credit. Generated meshes are triangulated
with unique baked textures at arbitrary scale, so they do not fit SE's grid or shared atlases; use them as
shape reference at most, and ask before spending credit.

## Rules that fail silently or late

- **UV-less or all-at-(0,0) UVs crash the game** [HARD, E032/E042]. Every mesh needs a real UV map, and that
  includes collision meshes (a UV-less collision mesh gives E044 and no collision in the MWM).
- **A highlight detector must cover its whole mesh** [HARD, owner test]: the outline shows only while the
  reticle is inside the `detector_*` empty, so any part of the mesh outside it is dead. Size the empty from
  the mesh bounds (`references/interaction-highlights.md`, "Detector size").
- **Decal materials (`DECAL_CUTOUT`: `Atlas*`, `ButtonsAtlas_*`, `Decals`, `Paneling*`, `TextAtlas*`) are for
  flat quads only** [HARD, seen in game]. On a 3D dome they render with broken transparency; keep each decal
  fully inside its flat face. `references/materials-catalog.md`.
- **Shade curved parts smooth and bevel hard edges** [HARD, owner saw faceted cylinders]:
  `bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))` on every part. `references/modeling-rules.md`.
- **A `detector_conveyor*` empty is also the conveyor connection point** [HARD, game code]: put it in the cell
  it belongs to, facing the neighbour. `references/interaction-highlights.md`.
- **Linking a subpart scene from script can crash Blender** [HARD, seen once on 4.5.10]: save first, set
  `linkSubpartInstances = False` on the main scene, make the subpart empty the active object, then set
  `empty.seut.linkedScene`. The add-dummy and add-subpart operators also leave the new empty unparented.
  `references/bpy-recipes.md` ("Subparts, dummies, mirroring and mountpoints from script").
- **Never loop over a live `collection.all_objects` / `bpy.data.objects` while creating or removing data**
  [HARD, two Blender 4.5.10 crashes in `pyrna_prop_collection_iter_next`]: copy first,
  `objs = list(col.all_objects)`, then build meshes, remove temp meshes, link objects. Save before each step.
  `references/bpy-recipes.md` ("Moving parts between .blend files, LODs from script"). At session start record
  `bpy.app.binary_path` and `bpy.data.filepath`; after a crash see `references/errors.md` ("When Blender
  crashes or the MCP connection drops").
- **Close the icon render preview window after `icon_render_preview`** [HARD]: leave only the user's main
  window open. Recipe in `references/bpy-recipes.md` (icons, step 4).
- **Do not call `scene.export_all_scenes` on a file with several scenes from script** [HARD, crashed Blender
  4.5.10 twice]: export each scene with `scene.export` instead. `references/bpy-recipes.md`.
- **A decal face whose corners all share one U (or one V) renders its normal map flipped** [HARD, seen on
  mitred seam tips]: the face has no tangent direction. Give every decal face real UV area in both directions.
  `references/atlas-regions.md` ("Panel lines").
- **Tiling texture scale depends on the kind of block** [HARD, owner-observed]: armor-style blocks want about
  0.05 UV per metre, functional blocks about 0.40. `references/materials.md`.
- **Re-exporting with `export_sbc_type = 'new'` writes `<SubtypeId>_1.sbc`** instead of overwriting. Use
  `'new'` once, then `'none'`.
- **ASCII only** in SubtypeId, material and object names [HARD, E033] or no MWM is written.
- **Collision outside the bounding box** makes the game fall back to cube collision [HARD, wiki].
- **Concave collision** gets filled in by Havok; split it into convex pieces [HARD, wiki].
- **Collision shapes ignore rotation.** Apply transforms, then add the rigid body; redo it after any edit
  [HARD, wiki]. Collision loads at game start, so restart the game to see collision changes (a model or texture reload does
  not cover it [SOFT, wiki; not tested]).
- **Custom shader node trees are ignored** and flagged (E053). Appearance comes from texture files plus
  the SEUT technique and parameters only [HARD].
- **One collision model per block.** Separate Main and BS collision models misbehave [HARD, wiki].
- **Mountpoint areas** are axis aligned, unrotated, trimmed to the bounding box, and never diagonal [HARD].
- **Mirroring is rotation based**, 90-degree steps from Keen's fixed list; an asymmetric block needs a
  separate mirror-model scene [HARD, wiki].

## Reusing SE textures

Default to reusing existing SE textures rather than baking new ones. SEUT already ships 165 linkable
vanilla materials in `<SEUT Assets>\Materials\Materials.blend` (marked Vanilla, no new DDS files needed).
Pick a material from `references/vanilla-materials.md`, link it (`link=True`), and move UV islands over the
atlas region you want. A model that uses only vanilla textures ships no textures of its own.

## Decals before geometry (default style)

Before modelling a surface detail in 3D (panel line, vent, hazard stripe, label, rivet row, button),
check whether a vanilla decal material already gives that look: `DECAL_CUTOUT` materials such as
`PanelingColorable`, `Atlas*`, `ButtonsAtlas_*`, `TextAtlas`, `Decals`. Use a decal quad on the surface when
one fits, and spend real geometry only on shape that has to read in the silhouette, catch light at
grazing angles, or affect collision. Decals cost almost nothing in triangles and keep blocks cheap and
consistent with vanilla. Say which decal you chose and why geometry was needed when you skip one.
Decal quads sit just off the surface (not coplanar) to avoid z-fighting [SOFT, 0.01 m exported cleanly, see
`references/materials-catalog.md` for normals and DLC pitfalls; confirm the offset used by
vanilla blocks before fixing a number].

## Interaction points highlight real geometry (default style)

Terminals, inventories, keypads and conveyor ports get a detector empty linked to a separate mesh
(the screen panel, keypad or port frame), so aiming at them outlines that part instead of a bare box.
Model the part as its own object, then use `add_highlight_empty`. Details and the vanilla small cargo
container breakdown: `references/interaction-highlights.md`.

## Reference files

| File | Read it when |
|---|---|
| `references/hard-surface.md` | building geometry: blockout, cuts, bevels, topology checks, bmesh snippets |
| `references/reference-images.md` | the user supplies a picture, blueprint or photo to match |
| `references/bpy-recipes.md` | scripting scenes, collections, materials, collision through the Blender MCP |
| `references/modeling-rules.md` | geometry, bevels and normals, collision, LOD, build stages, empties, mountpoints, mirroring |
| `references/materials.md` | picking or creating materials, texture types, techniques, atlas UV workflow |
| `references/setup.md` | the user has not installed Blender, SEUT, Havok or the ModSDK yet; first model; testing in game (credits Chipstix213's tutorial series) |
| `references/kitbash.md` | Reusing parts of vanilla models (crates, frames, ports, panels) instead of modelling them from scratch: import recipe |
| `references/atlas-regions.md` | UV-mapping a decal quad onto a specific piece of Atlas1-4, ButtonsAtlas, Decals or TextAtlas (UV boxes per piece) |
| `references/materials-catalog.md` | choosing a material by behaviour: paintable, decal, or emissive and state-driven glow; emissive presets and colours |
| `references/vanilla-materials.md` | choosing one of the 165 vanilla materials by name |
| `references/block-scenes.md` | laying out Main, LODs, build stages and collision for a complete block; vanilla LOD distances |
| `references/doors-subparts.md` | doors, hatches or any block with animated subparts: scene setup, orientation quirk, advanced door SBC fields |
| `references/characters-and-animation.md` | a playable/NPC character, creature, or handheld weapon animation controller (outline only) |
| `references/weapons-turrets.md` | turrets, weapons or tools (ConveyorSorter, WeaponCore, ToolCore): subpart chain, muzzle and camera dummies |
| `references/turret-design.md` | designing any turret or weapon model: design doc, blockout, supports, clearance, gun details, equipment, decals, review loop |
| `references/interaction-highlights.md` | any terminal, inventory, keypad, conveyor port or door interaction point |
| `references/errors.md` | any SEUT error or warning, and the pre-export checklist |
| `references/sources.md` | where each fact came from, and what is still unverified |
