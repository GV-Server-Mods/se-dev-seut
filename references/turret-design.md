# Designing a turret or weapon model

Lessons from building a large-grid gatling turret (WeaponCore) end to end with an owner reviewing every pass.
They apply to any turret, gun or weapon block. Tags as in SKILL.md: [owner] = owner design feedback,
[HARD] = measured or rendered, [SOFT] = inferred. Recipes live in the files linked below.

## Contents
- Workflow
- Structure and moving parts
- The gun itself
- Equipment and filling space
- Surface detail: bolts, wear, seams, decals
- Checking and reviewing

## Workflow

1. **Design document before Blender** [owner]. Write a short doc and get it confirmed: intent, block size and
   mount face, a parts table with heights above the mount face and which subpart each part moves with, the
   subpart chain and names, materials per part, elevation limits, and open questions. Concept art and notes
   disagree more often than they look; settling that on paper is far cheaper than in a model.
2. **Ask what drives the subparts.** Vanilla turret types hard-code names and spin; WeaponCore reads part names
   from its config, so any names work and a spinning barrel can sit under a missile-style chain
   (`weapons-turrets.md`, "Spinning barrels").
3. **Blockout, then iterate proportions only.** Plain shapes at the doc's heights, rendered at the concept art's
   angle and as an orthographic side view. Expect several rounds: on the gatling turret the base thickness,
   leg height and stance, pivot height and plate size changed seven times before detailing. Do not detail until
   the owner signs off the silhouette.
4. **Kitbash check, honestly.** Look for a vanilla part first (`kitbash.md`), but compare it with the concept: the
   vanilla gatling barrel was too short and stubby for a long-barrelled concept, so custom barrels were right.
5. **Detail in one scene, split into subpart scenes at the end.** Tag every object with its subpart (a custom
   property) so the split is mechanical, and keep pivot, muzzle and camera markers as plain empties until then.
6. **Small MCP steps.** Save before each step, never loop over a live collection while creating data, and keep a
   helper library in a Blender text block so every part gets the same bevel, cleanup, UV and material treatment
   (`bpy-recipes.md`, "Shaped parts and edge wear from script").

## Structure and moving parts

- **Clearance first.** The barrel or muzzle must clear blocks in front (the owner asked for the barrel at least
  1.75 to 2 m above the mount face on a large turret). Hit that with base and support proportions, not by
  stacking a tall plinth.
- **Pivot below anything it carries.** Put the elevation pivot low enough that the bearings never cut into the
  plate or shell above them.
- **Elevation equipment stays inside the supports** and within reach of the pivot axis; anything in a swept corner
  hits the legs as soon as the gun tilts [owner]. A part on the pivot axis (an ammo drum, a trunnion hub) never
  clips. Run the sweep check before export (`weapons-turrets.md`, "Clearance for moving subparts").
- **The carried part needs visible support** [owner]. A plate sitting on a thin trunnion looks wrong. Solid yoke
  plates from the plate down to round hubs on the trunnion, with box beams along the plate underside, read as
  structure; open V-struts left too much negative space.
- **Parallel lines for angled members** [owner]: an inset panel offset exactly inside an angled plate's outline,
  piston mounts lying in the sloped face they attach to, pistons running parallel to the edge they follow.
- **Tie protruding machinery to the structure it bolts onto** (pistons and drives on clevises and skids on the
  turntable), never floating in a recess.
- **Openings repeat the part's silhouette** with an even gap and a parallel frame (`modeling-rules.md`).

## The gun itself

- **Match the concept's muzzle**: a solid muzzle collar, then a muzzle device per barrel (slotted flash hider or
  brake). Build slots by construction, not with many small booleans (`bpy-recipes.md`, "Many small cuts").
- **Deep bores without internals** [owner]: recess each bore about 0.2 m with black metal walls and a matte black
  floor (`BlackMattePlastic`).
- **Radial symmetry on spinning parts** [owner]: every barrel's details come from one pattern rotated by its
  position angle. Clamps and rings round, not lobed, unless the concept shows otherwise.
- **Barrel mount**: a round mantlet collar with a bolted retaining ring reads as an assembly. Remove flanges that do
  not visibly attach to anything behind them, and keep the camera window clear of every ring and flange.
- **Muzzle dummy on the elevation part**, at the tip of the uppermost barrel, pointing out (+Y); the spin part
  carries no muzzle when WeaponCore animates the spin. Camera dummy behind a recessed window in the shell.

## Equipment and filling space

- **Fill negative space under the elevation part** with chunky equipment [owner]: one big feature cylinder at most
  (an ammo drum with bands), then chamfered machine boxes. Finned or ribbed cylinders lose their effect when
  repeated.
- **One mounting frame**: rails and cross ties under the boxes so they read as installed, not glued together.
- **Cable runs** need a fitting at each end and clamps along the way, and should follow the structure (parallel to a
  yoke edge). Segmented, misaligned hoses read as an afterthought [owner].
- **Terminal and inventory access on the fixed base** [HARD, game code: subpart detectors are ignored]. Corner
  consoles on the base slab, outside the turntable's sweep, work: a sloped terminal face with the `Terminal`
  keypad sheet and a frame, and a low box with a yellow-framed access hatch for `detector_inventory_1`
  (`interaction-highlights.md`).
- **Show how ammo reaches the gun** [owner]. A small hatch on the base reads as a joke. One good answer: a fixed
  docking column on the azimuth axis rising through the turntable centre (a rotary seal ring where the hub turns
  round it) and a matching receiver on the elevation part that lines up over it at 0 degrees. Check the receiver's
  closest pass over the column across the full elevation range; guide pins clipped at small angles, so the mouth
  and seal carry the docking look instead. A receiver with nothing behind it reads as a flat plate [owner]: give
  it a feed tube of the same style running on into the magazine (drum), with bolted collars at both ends, and
  clear whatever equipment sat in that path.
- **Terminal keypad**: embedded flat and centred in the base's back face, turned 90 degrees, in a rectangular
  pocket, read better than a console or a sloped corner pocket [owner].
- **Avoid boxes perched on top of the shell** and boxes hanging outside the plate outline [owner].

## Surface detail: bolts, wear, seams, decals

- **Bolts clamp something**: a ring, flange, lid, plate or lug over the part it holds. Mostly decal heads from
  `Decals_Atlas_A_01`, each at a random angle; few, low 3D bolts (`bpy-recipes.md`, "Bolt decals").
- **Wear on bevels only**: clean material on faces, the scratched sibling on bevel strips (`modeling-rules.md`).
- **Panel seams as decals**, not 3D grooves, with mitred T-joins and pointed ends; give the tip vertex its own U or
  the groove shades flipped (`atlas-regions.md`, "Panel lines").
- **Labels**: warning signs on flat faces, read checked in a render (mirrored text happens). Do not mirror one
  label symmetrically on the front; place labels on the sides and spread military stencils asymmetrically
  (`TextAtlas` letters and digits for unit numbers or calibre markings, chevron badges, gauges) [owner].
  Calibre and unit stencils sit best somewhere underneath (an underside access panel), not on a front face
  [owner]. Text on a downward face, read by someone looking up from in front (muzzle at -Y): letter right = +X,
  letter up = -Y (toward the front), face normal -Z [HARD, took three renders to get right]. Text direction is
  easy to get wrong on any face, so render every label once before calling it done.
- **On a painted shell, prefer paint-colour panel decals over lettering** [owner: stencilled numbers and
  marks on the radome were disliked]. `Atlas3_Colorable` access panels, window plates, hinge panels and slatted
  vents take the block's paint and get relief from the normal map, so they read as real panels. Add one or two
  bold hazard or warning signs (sized up: a 0.1 m diamond was far too small, 0.3 m worked), and skip decals
  from the light-grey `Decals` sheet on light paint (they nearly vanish). To choose, crop candidate regions into
  a labelled contact sheet (normal-map relief preview) and let the owner pick from it.
- **Symmetric trim, asymmetric marks** [owner]: panel and trim decals on structural edges (a plate's sides and
  chamfered corners) go symmetric: centred on each face, the same piece on every matching corner, a split pair
  either side of anything in the way (a gun notch). Only signs, labels and the odd hazard mark go asymmetric.
- **Keep a clean shell clean** [owner]: a smooth radome or cowl with seam decals, a recessed vent and a recessed
  camera reads better than strips, rivets, hatches and lifting eyes.
- **Holes and pockets follow the part they hold** [owner]: a square cut round a chamfered conveyor port left
  90-degree gaps at its corners. Measure the part's outline (for a chamfered square, max |x| and max |x|+|y| of its
  vertices give the half size and the chamfer), cut the hole with an even clearance (about 1 cm), and keep every
  surrounding step parallel to it.
- **Seams must sit on surface**: check each seam decal vertex with a short ray cast against the face behind it;
  a seam that crosses a recess or pocket floats [owner]. Route seams round pockets rather than over them.
- **Nothing past the mount face**: detail the bottom inside a shallow recess; direction arrows there should point
  to the weapon's front.

## Checking and reviewing

- Render each pass at the concept angle plus close-ups of what changed, in EEVEE (Workbench texture mode
  exaggerates wear). Ray-cast from the camera to identify a stray dark shape before guessing.
- Check every part against its support edge (no overhang past the turntable), every decal for floating or z-fighting,
  and every moving part with the sweep.
- **Decal obstruction check** [HARD, caught real clashes; owner: decals were hidden or colliding]: hide the decal
  objects and helper empties, then `scene.ray_cast` from each decal face centre along its normal for 0.3 m and list
  every hit. Anything within a few centimetres is hidden or colliding (bolts under a trunnion collar, labels behind
  a barrel ring, stencils on a drum hidden by rails). Move or drop those before showing renders. A decal can only
  be judged in a render from the angles players actually see it from.
- **Left and right are the weapon's own**, facing its muzzle: with the muzzle at Blender -Y, the turret's left is +X
  [owner, I had L and R swapped].
- Say what has not been seen in game (decals on curved shells, collision, subpart orientation).
