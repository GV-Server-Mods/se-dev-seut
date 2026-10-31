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

## Geometry and shading

- Hard-surface with bevels: SEUT's `Add Bevels` quick tool adds bevel modifiers with Harden Normals on
  [HARD]. The same setup works from script: Bevel modifier, `harden_normals = True`, then apply.
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
