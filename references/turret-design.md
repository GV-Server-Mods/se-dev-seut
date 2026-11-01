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
   scenes").
2. **Ask what drives the subparts.** Vanilla turret types hard-code names and spin; WeaponCore reads part names
   from its config, so any names work (`weapons-turrets.md`, "Spinning barrels").
3. **Keep pivot, muzzle and scope markers** as plain empties while detailing in one scene; they become the
   subpart empties and dummies at the split.

## Structure and moving parts

- **Clearance first.** The muzzle must clear the blocks in front at the lowest elevation. Reach that height with
  the base and support proportions rather than a tall plinth [owner].
- **Pivot below anything it carries**, so the bearings never cut into the part above them.
- **Elevation equipment stays inside the supports** and within reach of the pivot axis: anything in a swept corner
  hits the supports as soon as the gun tilts [owner]. A part centred on the pivot axis never clips. Run the
  sweep check before export (`weapons-turrets.md`, "Clearance for moving subparts").
- **The elevating part needs visible support** from the azimuth part (`design-detailing.md`, "Carried parts
  need visible support").
- **Nothing hangs past the turntable**: parts on the azimuth part stay inside its edge.
- **Shallow bores, no rifling** [owner]: do not model a barrel's full internal length. A short recess with a dark
  floor reads as a bore from any normal viewing angle. Rifling and deep bores only pay off on huge cannons
  (battleship scale) that players can actually look down; on small calibres they waste triangles.
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
- Before the in-game test, list what is unverified: subpart facing, spin axis, muzzle direction, scope
  clearance, elevation limits matching the config, and LOD switches.
