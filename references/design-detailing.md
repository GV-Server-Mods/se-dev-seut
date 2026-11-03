# Designing and detailing a block

How to take any detailed block (machinery, functional block, turret, prop) from an idea to a model that reads
like Space Engineers. Built from community ship-building advice, what vanilla parts do, and a long build of a
large turret with an owner reviewing every pass. Turret-only points are in `turret-design.md`. Tags as in
SKILL.md: [owner] = owner design feedback, [HARD] = measured or rendered, [SOFT] = inferred or adapted.

## Contents
- Workflow
- Replacing a block's model
- Shape and structure
- Equipment and filling space
- Surface detail: bolts, wear, seams, decals, labels
- Checking and reviewing

## Workflow

1. **Design document before Blender** [owner]. Ask for style references first: screenshots of the owner's own
   blocks in the style they want, saved next to the concept art. If the concept art is perspective only, also
   ask for straight-on front, side and top views of it (`reference-images.md`). Then write a short doc and get it confirmed:
   intent, block size and mount faces, a parts table with heights above the mount face (and which subpart each
   part moves with, if any), materials per part, limits, and open questions. Add where they apply: the
   replacement contract (next section), kitbash candidates, a decal table per surface for large and small
   features with each piece of geometry kept and why (SKILL.md, "Decals before geometry"), and the review
   checkpoints (step 2). Concept art and notes disagree more often than they look; settling that on paper is far
   cheaper than in a model.
2. **Review checkpoints and a build log** [owner: check progress often]. List the checkpoints in the doc, each
   with an owner sign-off: blockout, kitbash, each part group, each decal group (contact sheet first), the
   split, LODs and stages, the icon. Render each at the concept art's angle, the owner's reference angle and
   orthographic views. Keep `build-log.md` beside the doc and update it at every checkpoint (done, decided,
   renders, next), so a context compaction or a fresh session continues from the files.
3. **Silhouette first: blockout, then iterate proportions only.** Plain shapes at the doc's sizes, rendered at
   the concept art's angle and as an orthographic side view. Expect several rounds (the turret's base thickness,
   leg height and stance, pivot height and plate size changed seven times). Do not detail until the owner
   signs off the silhouette.
4. **Kitbash check, honestly.** Look for a vanilla part first (`kitbash.md`), but compare its proportions with
   the concept: a vanilla gatling barrel was too short and stubby for a long-barrelled concept, so custom
   barrels were right.
5. **If anything moves, detail in one scene and split at the end.** Tag every object with the part it moves
   with (a custom property) so the split is mechanical, and keep pivots and dummies as plain marker empties
   until then (`weapons-turrets.md`, "Splitting a turret into subpart scenes").
6. **Small MCP steps.** Save before each step, never loop over a live collection while creating data, and keep
   a helper library in a Blender text block so every part gets the same bevel, cleanup, UV and material
   treatment (`bpy-recipes.md`, "Shaped parts and edge wear from script").
7. **Decal pass on every surface** before any flat 3D detail (SKILL.md, "Decals before geometry").
8. **Count triangles early** and cut over-segmented round parts and buried faces (`bpy-recipes.md`, "Triangle
   budget" and "Buried faces").

## Replacing a block's model

When the new model replaces an existing block, the old block is the contract, so grids already built with it
keep working. Put it in the design doc as a "fixed by the block it replaces" table:

- Keep the SubtypeIds (every SBC entry that uses the model, NPC copies included), `Size`, mount points, conveyor
  port cells and `BlockPairName`.
- Read the old SBC entries and, for a weapon, both WeaponCore files: the weapon definition (part names, muzzles,
  scope, limits) and its animation (`weapons-turrets.md`).
- Read the old model's dummies with `scripts/mwm_dummies.py`: names, positions and directions give the pivot
  heights, muzzle reach and port positions to keep or improve on.
- Before deleting the old model files, search the mod's data for every other block that names them: build-stage
  models are often shared (two different blocks used one pair of half-block stages).

## Shape and structure

- **Break up every large flat face**: a recess, a raised frame, panel lines or a decal. A blank face is the
  commonest reason a block looks unfinished. Prefer decals for this.
- **Two or three tones, not one**: a paintable base, a darker trim material, and one small accent (a lit strip,
  a warning stripe, a lamp). Vanilla blocks do this with `Colorable` plus `Darker` plus a small accent material.
  On a mostly dark mechanical block, give the player a few paintable spots [owner]: flat plates framed by dark
  trim read best (a hub plate inside a race ring, gearbox lids, bolted corner plates), switched to
  `PaintedMetal_Colorable` so they take paint and skins.
- **Small raised hatches and plates can be decals** [owner]: a pair of 3D coin hatches with handles cost 576
  triangles; an `Atlas3_Darker` hatch decal (handle slot and screws) replaced them. A later pass turned thin
  panels, pads and tabs into decals too (about 1,600 triangles), keeping the pieces that give real relief
  (round flanges, a small handle, cooling fins) [owner]. When a part becomes a decal: delete the bolt decals
  that sat on it, move any label it carried down onto the new surface just above the new decal (2.2 mm over
  1.5 mm), place the decal on the surface found by a ray cast, and check a 3x3 grid of points on it (each
  lands on the surface, nothing covers it within 5 cm). A decal may be stretched to fill a strip with equal
  margins when its art tolerates it (a frame with a slot did) [owner].
- **Decals on a structural outline look added on** [owner]: hazard stripes on a slab's chamfered corners read
  as an afterthought and were removed. Put marks where something happens (a moving joint, a port, a hatch).
- **Greeble with real parts only where they read from a few metres** (handles, vents, pipes, lamps); leave the
  rest to decals and textures.
- **Think about the neighbours**: flush faces, mount points and edge chamfers should let the block join
  cleanly. Armor-style blocks keep faces flush; functional blocks inset. Nothing may stick out past a mounting
  face: detail it inside a shallow recess (`modeling-rules.md`), and point any direction arrows there at the
  block's front. Kitbashed vanilla port frames and signs stand about 4 cm proud of their face (`kitbash.md`), so
  set a mounting face that carries them about 5 cm inside the cell and they end flush.
- **Pick the footprint with symmetry in mind**: an odd cell width puts a feature on the centre line, an even
  width cannot [community advice; vanilla blocks follow it].
- **Mechanical detail should look designed, not like stacked rectangles** [owner]. Use imaginative shaped
  profiles: rounded-corner plates, rounded clevis ears with pins and hex nuts, U cradles, gussets, drums with
  bell ends, conduits with elbows, pistons with eye ends and gland rings.
- **Carried parts need visible support** [owner]. A plate sitting on a thin pin looks wrong. Solid plates down
  to round hubs, with box beams along the underside, read as structure; open V-struts left too much negative
  space.
- **Parallel lines for angled members** [owner]: an inset panel offset exactly inside an angled plate's outline,
  mount pads lying in the sloped face they attach to, pistons running parallel to the edge they follow.
- **Tie protruding machinery to the structure it would bolt onto** (pistons and drives on clevises and skids),
  never floating in a recess.
- **Openings and holes repeat the part's silhouette** [owner]: a chamfered box sits in a chamfered opening with
  an even gap all round (about 4-7 cm on a large block), framed by a raised border offset parallel to it. A
  rounded pocket around a chamfered box looked out of place, and a square hole round a chamfered conveyor port
  left 90-degree gaps at its corners. Measure the part's outline (for a chamfered square, max |x| and
  max |x|+|y| of its vertices give the half size and the chamfer), cut a fitted hole with an even clearance
  (about 1 cm), and keep every surrounding step parallel to it.
- **Nothing perched or overhanging** [owner]: no boxes stuck on top of a smooth shell, and no parts hanging
  past the edge of the structure that carries them.
- **Keep a clean shell clean** [owner]: a smooth cowl or dome with seam decals and recessed vents or windows
  reads better than strips, rivets, hatches and lifting eyes.

## Equipment and filling space

- **Fill negative space with chunky equipment** [owner]: one big feature cylinder at most (a drum with bands),
  then chamfered machine boxes. Finned or ribbed cylinders lose their effect when repeated.
- **One mounting frame**: rails and cross ties under the boxes, so they read as installed, not as boxes glued to
  boxes [owner].
- **Cable runs** need a fitting at each end and clamps along the way, and should follow the structure (parallel
  to an edge). Segmented, misaligned hoses read as an afterthought [owner].
- **Show how things reach where they go** [owner]: ammunition, power or fluid needs a visible path. A small
  hatch with nothing behind it reads as a joke, and an intake with nothing behind it reads as a flat plate;
  run a tube or duct of the same style on into whatever it feeds, with fittings at both ends. A turret example
  is in `turret-design.md`.
- **Interaction points on a fixed part** [HARD, game code: detectors in subparts are ignored]. A terminal keypad
  embedded flat in a pocket in a face read better than a bolted-on console or a sloped corner pocket [owner]
  (`interaction-highlights.md`).

## Surface detail: bolts, wear, seams, decals, labels

- **Bolts clamp something** [owner]: a ring, flange, lid, plate or lug that visibly overlaps the part it holds,
  not heads scattered on a plain face. Mostly decal heads, each at a random angle so they look individually
  tightened; few, low 3D bolts (`bpy-recipes.md`, "Bolt decals").
- **One fastener plan for the whole model** [owner: bolts of random size and spacing looked inconsistent, and one
  part had a quarter of all the bolts]. Before placing any, measure the concept art (pixels to metres) and write
  down: one head size (a second, smaller size only where a part is too narrow, such as a ring band), one inset
  from the seam or plate edge, one pitch, and which edges get bolts at all (usually what the art draws: plate
  corners and the edge that clamps, not every edge). Place every row from those numbers. Never ring every face
  edge of a part with bolts, never put a bolt on a seam (keep the head about 1 cm clear of the groove), and never
  put two at a shared corner. Count bolts per part after each build: a part with far more than its share is the
  clutter the owner sees.
- **Rows, not scattered bolts** [owner: rows from neighbouring seams bunched at plate corners, and short joints
  got pairs a few cm apart, which looked random]. Lay each joint's row as one line at one pitch, and keep every
  bolt at least two insets (the pair across a seam) from any bolt of another row, measured over the surface.
  Lay the longest rows first; trim a later row to its clear stretches and re-space each stretch evenly instead of
  dropping single bolts, and skip a stretch shorter than two insets. Line up the two rows of a seam, and parallel
  rows on one plate, so the bolts pair across the joint.
- **Wear on bevels only, and sparingly** [owner]: a `*Scratched*` variant over whole faces looks bad. Clean
  material on faces, the scratched sibling on bevel strips (recipe in `bpy-recipes.md`, "Edge-only wear"). Even
  on bevels it was too obvious along long structural edges (a base slab, a turntable rim) and was removed
  there; keep it for small machinery, and ask before putting it on the block's main outline.
- **Panel seams as decals**, not 3D grooves, with mitred T-joins and pointed ends; give the tip vertex its own U
  or the groove shades flipped (`atlas-regions.md`, "Panel lines"). Seams must sit on surface: check each seam
  vertex with a short ray cast against the face behind it, and route seams round recesses and pockets, since a
  seam that crosses one floats [owner].
- **Every joint says how it was made** [owner]: a V-groove seam between removable cover plates, a weld line on
  permanent structural joints (around big mechanical parts: trunnion housings, bearing rings, frames, fillets in
  inside corners), bolts where a plate clamps something. Weld lines are decals too (`atlas-regions.md`, "Weld
  lines"): one direction along each line, no mirrored spans, and a welded corner gets a rounder bevel that the
  bead follows. Bolts kept clear of welds is a style preference, not a rule: one owner wanted panel bolts about
  0.3 m from any weld and none on a welded joint. Ask before applying it.
- **On a painted shell, prefer paint-colour panel decals over lettering** [owner: stencilled numbers and marks on
  a dome were disliked]. `Atlas3_Colorable` access panels, window plates, hinge panels and slatted vents take
  the block's paint and get relief from the normal map, so they read as real panels. Skip decals from the
  light-grey `Decals` sheet on light paint (they nearly vanish). To choose, crop candidate regions into a
  labelled contact sheet (normal-map relief preview) and let the owner pick from it.
- **Signs sized boldly**: one or two hazard or warning signs per side, big enough to read (a 0.1 m diamond was
  far too small on a large block, 0.3 m worked).
- **Symmetric trim, asymmetric marks** [owner]: panel and trim decals on structural edges (a plate's sides and
  chamfered corners) go symmetric: centred on each face, the same piece on every matching corner, a split pair
  either side of anything in the way. Only signs, labels and the odd hazard mark go asymmetric.
- **Labels**: do not mirror one label symmetrically on the front; place labels on the sides and spread stencils
  asymmetrically (`TextAtlas` letters and digits, badges, gauges) [owner]. Unit numbers and specification
  stencils sit best somewhere underneath (an underside access panel), not on a front face [owner]. Text
  direction is easy to get wrong on any face, so render every label once. On a downward face, read by someone
  looking up from in front (front at Blender -Y): letter right = +X, letter up = -Y, face normal -Z [HARD, took
  three renders to get right].

## Checking and reviewing

- Render each pass at the concept angle plus close-ups of what changed, in EEVEE (Workbench texture mode
  exaggerates wear). Ray-cast from the camera to identify a stray dark shape before guessing.
- Check every part against its support edge, every decal for floating or z-fighting, and every moving part
  through its full range (`weapons-turrets.md`, "Clearance for moving subparts").
- **Decal obstruction check** [HARD, caught real clashes; owner: decals were hidden or colliding]: hide the decal
  objects and helper empties, then `scene.ray_cast` from each decal face centre along its normal for 0.3 m and
  list every hit. Anything within a few centimetres is hidden or colliding (bolts under a collar, labels behind a
  ring, stencils hidden by rails). Move or drop those before showing renders. A decal can only be judged in a
  render from the angles players actually see it from.
- **Clear along the normal is not visible** [HARD, three decals placed with a 6 cm check ended up under a
  bearing, behind side covers and above a drum]: before placing, also cast from the spot toward a ring of
  viewpoints about 5 m out (several azimuths, below the horizon for undersides, every elevation a moving part
  reaches) and keep spots that several viewpoints see.
- **Removing a part under a decal strands the decal**: deleting 16 mm bosses left their bolt decals floating
  16 mm up. Re-cast every decal that sat on the removed part down to the new surface.
- **Left and right are the block's own**, facing its front: with the front at Blender -Y, the block's left is +X
  [owner: L and R were swapped on the turret's legs].
- Say what has not been seen in game (decals on curved shells, collision, subpart orientation).
