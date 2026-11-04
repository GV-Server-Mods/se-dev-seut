# Designing a turret or weapon model

What a turret or weapon block needs beyond any other block. Read `design-detailing.md` first: the workflow,
structure, surface detail and review loop there apply to turrets too. The look of the gun itself (barrels,
muzzle devices, shells) comes from the concept art and the owner, not from this file. Tags as in SKILL.md:
[owner] = owner design feedback, [HARD] = measured, rendered or read in code, [SOFT] = inferred.

## Contents
- Workflow additions
- Structure and moving parts
- Dummies
- Interaction and ammunition
- Checking

## Workflow additions

1. **The design doc also names the subpart chain**: which subpart each part moves with, the subpart and dummy
   names, and the elevation limits. If the model replaces an existing weapon, read its definition first and
   match its names, or plan the config change with it (`weapons-turrets.md`, "Splitting a turret into subpart
   scenes"), and fill in the replacement contract (`design-detailing.md`, "Replacing a block's model").
2. **Ask what drives the subparts.** Vanilla turret types hard-code names and spin; WeaponCore reads part names
   from its config, so any names work (`weapons-turrets.md`, "Spinning barrels").
3. **Keep pivot, muzzle and scope markers** as plain empties while detailing in one scene; they become the
   subpart empties and dummies at the split.

## Structure and moving parts

- **Clearance first.** The muzzle must clear the blocks in front at the lowest elevation. Reach that height with
  the base and support proportions or with a plinth under the turret; which one is a style choice, so ask.
- **Pivot below anything it carries**, so the bearings never cut into the part above them.
- **Elevation equipment stays inside the supports** and within reach of the pivot axis: anything in a swept corner
  hits the supports as soon as the gun tilts [owner]. A part centred on the pivot axis never clips. Run the
  sweep check before export (`weapons-turrets.md`, "Clearance for moving subparts").
- **The elevating part needs visible support** from the azimuth part (`design-detailing.md`, "Carried parts
  need visible support").
- **Nothing hangs past the turntable**: parts on the azimuth part stay inside its edge.
- **Sweep radius**: everything on the azimuth part stays within half the block's width of the azimuth axis,
  since it sweeps a full circle. Only the barrels reach past the block (a shipped 5-wide turret's muzzles sit
  12.7 m from its azimuth axis [HARD, read from its `.mwm`]). To keep long barrels from reaching further past
  the block, move the azimuth axis forward on the gunhouse so more of the gunhouse sits behind it [owner].
  Build stages show the barrels at rest like the rest of the outline; stages use Main's collision, which covers
  only the base, so the overhang cannot catch a neighbour.
- **Openings in the gunhouse (embrasures)**: whatever of the elevation part passes through an opening in the
  azimuth part (mantlet, cheeks, gun shields) clears the opening's edges across the whole elevation range. A
  drum or mantlet centred on the trunnion axis keeps one even gap at every angle, so make the part that fills
  the opening round about that axis, cut the opening's top edge back for maximum elevation, and check both
  limits numerically.
- **Collision for a housing that is not round** (a box gunhouse): all collision sits on the base and covers the
  turret at rest (`weapons-turrets.md`, step 4 of the split). Choose between a cylinder about the azimuth axis
  out to the housing's farthest corner, which covers it at every azimuth but is bigger than the housing at
  rest, and a hull of the housing at rest, which fits at rest but leaves turned corners uncovered and covers
  empty space [owner chose the cylinder for a box gunhouse].
- **Superfiring over a twin** [HARD, WeaponCore `WeaponTracking.RayCheckTest` and `WeaponTypes.cs`]: the
  line-of-sight ray from the scope stops on the lower turret's collision shapes, and a hit on the same construct
  pauses firing (`RayCheckSelfHit`). So collision, not cells or mesh, sets how low a twin mounted above and
  behind can fire. Keep the collision top at the roof, give roof equipment (periscopes, sensor domes) no
  collision, and keep that equipment out of the barrels' lanes.
- **Shallow bores, no rifling** [owner], as on every SE weapon (`weapons-turrets.md`, "Barrels on any weapon").
- **Radial symmetry on spinning parts** [owner]: build every repeated element from one pattern rotated by its
  position angle, so a spinning cluster looks the same at every angle.

## Dummies

- **Muzzle dummies** sit where rounds leave the barrel, pointing out along it (+Y in a subpart scene). When
  WeaponCore spins the barrel part, put the muzzle on the elevation part so it does not spin with it.
- **Scope dummy** (WeaponCore `Scope`, often `camera`) outside every collision shape at every elevation, since
  WeaponCore casts its line-of-sight ray from it (`weapons-turrets.md`, step 4 of the split). Just ahead of the
  muzzle on the barrel axis is a safe default.
- Verify each dummy's world position in a fresh update after moving it (`bpy-recipes.md`, "`matrix_world` in a
  scene that is not on screen is stale").

## Interaction and ammunition

- **Terminal, inventory and conveyor access on the fixed base** [HARD, game code: detectors in subparts are
  ignored], outside the turntable's sweep (`interaction-highlights.md`).
- **Show how ammunition reaches the gun** [owner]: a visible path from the fixed base, through the rotating
  joint, to the part that feeds the gun. A hatch with nothing behind it reads as a joke. If a feed part on the
  elevating part lines up with one on the base, check their clearance across the full elevation range.

## Checking

- **Left and right are the weapon's own**, facing its muzzle (`design-detailing.md`, "Checking and reviewing").
- Before export, sweep the elevation part through both limits, the recoiling barrels at minimum, zero and
  maximum elevation, and, for superfiring, a copy of the turret at the twin's offset: cast the upper scope's
  ray over the lower turret's collision at the lowest angle the twin should fire.
- Before the in-game test, list what is unverified: subpart facing, spin axis, muzzle direction, scope
  clearance, elevation limits matching the config, recoil gaps, and LOD switches.
