# Modeling rules for SE blocks

## Contents
- Scale and bounding box
- Geometry and shading
- Collision
- LODs and build stages
- Empties, subparts, dummies
- Mountpoints
- Mirroring

## Scale and bounding box

- Large grid cell 2.5 m, small grid cell 0.5 m [HARD]. Blender grid is set to half a cell by SEUT's Grid Scale.
- Bounding box is `bBox_X/Y/Z` cells, centred on the origin. Keep every Main, Collision and mountpoint
  inside it. Mountpoint areas past the box are trimmed on save [HARD].
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
  meshes too. Flat decal quads can stay flat.
- Bevel every hard edge of real geometry [SOFT, owner: the test block's plain box extrusions looked unlike the
  game]. Vanilla parts carry a visible chamfer on nearly every edge, including the large chamfers where a
  raised frame meets its panel. Hand-built boxes with sharp 90 degree edges stand out next to vanilla ones; use
  the Bevel modifier with Harden Normals, then smooth shade as above. Better still, take shell parts from a
  vanilla model (`kitbash.md`).
- Bevel on thin or small parts leaves zero-area faces [HARD, hit in a test run]: a 0.03 m bevel on parts under
  0.1 m thick gave 34 to 60 degenerate faces per part, and MwmBuilder logged "degenerated triangle" and "UV with
  3 identical vectors in a row ... will cause SE to make the entire model shaderless". After applying a
  bevel, run `bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges[:])`, delete faces with
  `f.calc_area() < 1e-9`, and re-project the UVs. Read `<SubtypeId>.mwm.log` (export with
  `export_deleteLooseFiles = False`) and fix every WARNING; the clean run's `I007` does not mean the log is
  clean. One run still logged 5 identical-UV warnings after all measurable zero-area faces were gone and the
  source was not found, so treat that warning as unresolved until the block is seen in game.
- Triangulation is handled at export; model in quads where practical [SOFT].
- Recalculate normals outward and check Face Orientation before export [SOFT].
- LOD meshes may drop bevels (`Remove Bevels` exists for this) [HARD].
- Origin is the block centre unless the block is a subpart, whose origin is its pivot [SOFT].
- Keep object and material names ASCII [HARD, E033].

## Collision

- Collection `Collision - Main (<SubtypeId>)`; SEUT creates it. Build stages fall back to Main's collision
  [HARD].
- Max 10 objects (E022). Each must be convex. Use as few as possible.
- Allowed rigid body shapes: Box, Sphere, Capsule, Cylinder, Convex Hull. Never Cone, Mesh or Compound
  Parent (E054). Cost, high to low: Convex Hull, Box, Cylinder, Capsule, Sphere [HARD, wiki].
- Rigid bodies are axis fixed: a rotated cylinder will not work as modelled. Use Convex Hull for angled
  shapes.
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
- `BS1..BS3` are construction stages (typically shells with less geometry). `Apply Construction` assigns
  the Construction material; `Cut and Solidify` makes the scaffold look [HARD].
- Armor blocks vanilla-style use build stages; simple blocks may skip them [SOFT].

## Empties, subparts, dummies

- Subpart empty links to a scene of type `Subpart`; the subpart scene must use the same grid export
  settings (W001, W020) and cannot loop into itself (E005) [HARD].
- Empties should have a parent object (W005) and the parent should itself be unparented (W006).
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
