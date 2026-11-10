# Modeling rules for SE blocks

## Contents
- Scale and bounding box
- Geometry and shading
- Design style
- Collision
- LODs and build stages
- Empties, subparts, dummies
- Mountpoints
- Mirroring

## Scale and bounding box

- Large grid cell 2.5 m, small grid cell 0.5 m [HARD]. Blender grid is set to half a cell by SEUT's Grid Scale.
- Bounding box is `bBox_X/Y/Z` cells, centred on the origin. Keep every Main, Collision and mountpoint
  inside it. Mountpoint areas past the box are trimmed on save [HARD].
- Nothing may stick out past a mounting face (it would sit inside the neighbouring block). Detail a bottom or
  mounting face by recessing the field a few millimetres inside a rim and putting decals and pockets inside
  the recess [SOFT, applied on the gatling turret base].
- Armor-style blocks sit flush with the cell faces so neighbours join without gaps. Functional blocks
  usually keep a small inset on faces that do not need to touch [SOFT, vanilla convention].
- Set the grid scale to match the block, since it also scales SBC values [HARD].

- Which Blender side is the block's in-game front is not verified. SEUT's FBX export uses forward `Z` and up
  `Y` [HARD, `seut_export_utils.py`], but no test has placed a block and checked its front. Ask the owner, or
  test with an obvious marker, before putting a port on "the front".

## Geometry and shading

- Hard-surface with bevels: SEUT's `Add Bevels` quick tool adds bevel modifiers with Harden Normals on
  [HARD]. The same setup works from script: Bevel modifier, `harden_normals = True`, then apply.
- Shade curved and bevelled parts smooth [HARD, owner saw faceted cylinders in game]. Blender creates meshes
  flat shaded, and the exported model keeps that: a cylinder reads as a stack of flat panels. After
  building each part (and after applying bevels), run, with the object selected and active:
  `bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))` [tested, Blender 4.5]. That smooths faces
  and marks edges sharper than 30 degrees as sharp, so box corners stay crisp. Check with
  `sum(p.use_smooth for p in me.polygons)`, which should be close to the polygon count, and do it for LOD
  meshes too. Flat decal quads can stay flat. Smoothing alone tilts the normals of a big flat face that meets
  a smoothed bevel, which shows as a fake angled shade in game [owner]; finish every bevelled part with an
  applied Weighted Normal modifier (`bpy-recipes.md`, "Flat faces next to smoothed bevels"). Where built parts
  sit beside kitbashed vanilla ones, rebuild their normals by Keen's measured rule instead (`bpy-recipes.md`,
  "Matching vanilla shading").
- Every wide flat face shades flat [owner, HARD]. Soft folds of 10-30 degrees, wide faces beside thin strips,
  and lofted sides that follow the shapes under them each smeared or streaked large faces on a turret. The check
  that finds them, and the fixes, are in `bpy-recipes.md`, "Shading check"; run it before the decal pass.
- Bevel every hard edge of real geometry [SOFT, owner: the test block's plain box extrusions looked unlike the
  game]. Vanilla parts carry a visible chamfer on nearly every edge, including the large chamfers where a
  raised frame meets its panel. Hand-built boxes with sharp 90 degree edges stand out next to vanilla ones; use
  the Bevel modifier with Harden Normals, then smooth shade as above. Better still, take shell parts from a
  vanilla model (`kitbash.md`).
- Do not build a part as several nested or stacked boxes with a thin bevel each [owner: the test crate's
  bezel and handle looked like three separate rectangles in game, not one moulded piece]. Make each part one
  solid with a single consistent chamfer, sized to the part (clearly visible from a few metres, not a hairline;
  on a large-block slab 0.6 mm was invisible in game and 15 mm too heavy, and about 7 mm was asked for, so
  measure the bevel's width from the vertices rather than trusting the modifier value [owner]),
  or take the part from a vanilla model (`kitbash.md` has handles, keypad frames and port frames). Check
  hand-built parts in game next to a vanilla block, as the owner did, before calling them done.
- Bevel on thin or small parts leaves zero-area faces [HARD, hit in a test run]: a 0.03 m bevel on parts under
  0.1 m thick gave 34 to 60 degenerate faces per part, and MwmBuilder logged "degenerated triangle" and "UV with
  3 identical vectors in a row ... will cause SE to make the entire model shaderless". After applying a
  bevel, run `bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges[:])`, delete faces with
  `f.calc_area() < 1e-9`, and re-project the UVs. Read `<SubtypeId>.mwm.log` (export with
  `export_deleteLooseFiles = False`) and fix every WARNING; the clean run's `I007` does not mean the log is
  clean. One run still logged 5 identical-UV warnings after all measurable zero-area faces were gone and the
  source was not found, so treat that warning as unresolved until the block is seen in game.
- **Bent bars and handles: straight runs joined by true arcs** [owner: a U handle swept along a Catmull-Rom spline
  through eight points looked "really ugly and bent" in game]. A spline through sparse points bows the straight
  legs and flattens the corners; compute the centre line as lines and circular arcs (a few degrees a step). Give the
  tube enough sides that no edge passes the bevel's angle limit (24 at a 30 degree limit), shade it smooth with no
  bevel or Weighted Normal, and UV it along and round the bar: box projection streaks a round bar's texture and
  the bevel plus face-area normals make it read as flat facets.
- Triangulation is handled at export; model in quads where practical [SOFT].
- Recalculate normals outward and check Face Orientation before export [SOFT].
- LOD meshes may drop bevels (`Remove Bevels` exists for this) [HARD].
- Origin is the block centre unless the block is a subpart, whose origin is its pivot [SOFT].
- Keep object and material names ASCII [HARD, E033].

## Design style

How to make a block read like Space Engineers (silhouette first, breaking up flat faces, tones, shaped
mechanical parts, openings, equipment, bolts, wear, seams, decals and labels) is in `design-detailing.md`.

## Collision

- Collection `Collision - Main (<SubtypeId>)`; SEUT creates it. Build stages fall back to Main's collision
  [HARD].
- Max 10 objects (E022). Each must be convex. Use as few as possible.
- Allowed rigid body shapes: Box, Sphere, Capsule, Cylinder, Convex Hull. Never Cone, Mesh or Compound
  Parent (E054). Cost, high to low: Convex Hull, Box, Cylinder, Capsule, Sphere [HARD, wiki].
- Rigid bodies are axis fixed: a rotated cylinder will not work as modelled. Use Convex Hull for angled
  shapes.
- **Keep every collision object at the origin with its vertices in place** [HARD, owner's Physics Primitives
  view]: the exported shapes ignore the object's location. Shapes built centred on their own origin and then
  moved with `location` all landed stacked at the block centre in game, standing up to a foot above the dome
  and leaving the base with no collision, although Havok reported every rigid body. After building, bake the
  transform: `o.data.transform(o.matrix_world); o.matrix_world = Matrix()`. Check in game with the Physics
  Primitives debug draw (convex hulls draw red). SEUT only tags each mesh with its shape type and Havok fits the
  shape to the vertices; with the vertices in place, a `BOX` and a `SPHERE` came out of the Havok filter
  wrapped in `hkpConvexTranslateShape`/`hkpConvexTransformShape`, so they keep their offset [HARD in the .hkt,
  SOFT in game]. Prefer boxes and spheres where they fit; for wide, flat round parts use hull prisms, since a
  fitted cylinder may follow the mesh's longest dimension and lie on its side [SOFT].
- The wiki says collision appears slightly bigger in game, so shrink shapes a little. In a test of a 2.5 m
  bevelled cube, a 2.45 m box felt "a tad too small" against the model in game [HARD, tested by the owner].
  A 2.5 m box on the same cube felt right [HARD, tested by the owner]. Start from the model's real extent
  (2.5 m box for a full cube) and shrink only if it blocks neighbours.
- Debug in game: offline singleplayer, F11, Debug Draw, Physics Primitives. Red = hull, blue = box,
  white = sphere, orange = cylinder, yellow = capsule.
- Subparts only get collision if vanilla blocks of that type have it on subparts too.
- An external `.hkt` file set on the collection overrides objects and errors if objects also exist (E055).

## LODs and build stages

- `LOD1..3` hold lower-detail copies of Main; default distances 25 / 50 / 100 m, strictly increasing
  (E011) [HARD]. Collection indexes must be gap free (E006).
- Facts from the wiki Models reference [HARD, wiki]: use at least two LODs (three meshes in total). LODs
  carry no dummies, no collision and no LODs of their own; only the main model's dummies count. LOD1 (or the
  main model if there are no LODs) stays in memory for intersection checks (use objects, bullet decals,
  aiming), so keep LOD1 recognisably the same shape. Model quality "medium" and "low" cap at LOD1 and shorten
  the distances, so LOD1 is what many players see. Distances are metres at high quality, 1080p and 70 degree
  FOV; the game scales them by `tan(FovH/2) / tan(70/2) * 1080 / verticalResolution`. LOD links in the XML are
  relative to the mod root, so moving the `.mwm` files breaks them. The mod root must contain a `Models`
  folder; the game cuts the path at the first `Models`.
- What vanilla does [HARD, read from the SDK `CargoContainerSmall*.xml` / FBX]: LOD1 at 5 m is nearly the full
  model (5,852 faces, all materials kept, including `Decals` and `PaintedMetal_Yellow`); LOD2 at 60 m is a
  12-face box with one baked material (`CargoContainerSmall_LOD2`). SEUT's defaults of 25 / 50 m are only
  defaults. Do not decimate hard: keep every material the block shows from a distance, and never let a
  decimate pass delete decal or accent faces (`bpy-recipes.md`, "LOD from script").
- Without a collision model the game makes a box from the bounding box. Construction (BS) models should share
  the main block's collision. Dummy and collision changes need a full game restart [wiki; reload showed stale dummies, owner], and so do
  subpart changes [owner]; simple mesh and texture changes only need the Debug Draw "Reload models" /
  "Reload textures" buttons [HARD, owner].
- `BS1..BS3` are construction stages (typically shells with less geometry). `Apply Construction` assigns
  the Construction material; `Cut and Solidify` makes the scaffold look [HARD]. Both were run: Cut and Solidify
  leaves zero-area UVs that need a re-unwrap, `Add Bevels` uses a hairline 2.5 mm width whatever you ask for,
  and `Apply Transformations` strips the rigid body (details in `bpy-recipes.md`, "Quick tools").
- Armor blocks vanilla-style use build stages; simple blocks may skip them [SOFT].

## Empties, subparts, dummies

- Subpart empty links to a scene of type `Subpart`; the subpart scene must use the same grid export
  settings (W001, W020) and cannot loop into itself (E005) [HARD].
- Empties should have a parent object (W005) and the parent should itself be unparented (W006).
- **Which way a subpart faces** [HARD: SEUT `seut_export_utils.py`, the game code named below, and a shipped
  SEUT turret's .blend read against its exported .mwm]. SEUT exports main scenes with FBX forward `Z` and
  subpart scenes with `-Z`: a main scene's -Y becomes the model's forward (-Z), and so does a subpart scene's +Y.
  Every empty exports with its local +Y as the dummy's forward and +Z as its up, so an unrotated subpart empty in
  a main scene points backward, while one in a subpart scene exports unrotated (`scripts/mwm_dummies.py` prints
  both). The block's code decides whether that half turn reaches the game:
  - Vanilla turret types rebuild the azimuth and elevation subparts from pure yaw and pitch, keeping only the
    empty's position (`MyLargeTurretBase.RotateModels`), and doors rebuild theirs from the block origin
    (`MyDoor`, `MyAdvancedDoor`). The empty's rotation is dropped, so turn the content of each such subpart scene
    180 degrees about Z (front, muzzle or barrels toward +Y) and leave every empty unrotated, as that shipped
    turret does (it faces correctly in game). SEUT's subpart preview and icon instances then show those parts facing backward in the main
    scene; that is expected.
  - A subpart linked from a subpart scene (a barrel, a recoil part) keeps its empty's matrix, so with unrotated
    empties its frame matches its parent's.
  - WeaponCore sorter turrets keep the empty's rotation (`AzimuthPart.OriginalPosition` in
    `WeaponController.AimBarrel`), so the half turn reaches the game there; the right arrangement for them is
    unverified, so check the facing in game.
  Turret steps: `weapons-turrets.md`, "Splitting a turret into subpart scenes". Door SBC fields: `doors-subparts.md`.
- Highlight empties need an object in `Main` (E025) and share its parent (W007).
- Dummy and preset subpart empties come from `scene.add_dummy` / `scene.add_preset_subpart`. The wiki
  empty-properties page does not list dummy names; read them from SEUT's `empties` module when needed.

## Mountpoints

Workflow [HARD, wiki]: update the bounding box, enable Mountpoint Mode, edit the turquoise areas in Object
Mode (never move the side empties), add areas with `Add Area`, disable the mode to save. Mask options:
None, Protrudes, Narrow, Thin, Central, Custom. Areas are saved as X/Y size only, no rotation, no diagonals.
Verify in game with the BuildInfo mod overlay (yellow).

## Mirroring

Enable Mirroring Mode, rotate the three mirror empties in 90-degree steps until the instance looks like a
reflection, disable the mode to save. Only rotations from Keen's list work (E023 otherwise); try another
axis combination facing the same way. An asymmetric block needs a copy scene mirrored with Blender's tools,
set as `Mirror Model`, and added as its own block [HARD, wiki].
