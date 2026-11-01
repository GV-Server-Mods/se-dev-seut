# Designing a turret or weapon model

Turret-only lessons from building a large-grid gatling turret (WeaponCore) end to end with an owner reviewing
every pass. Read `design-detailing.md` first: the workflow, structure, surface detail (bolts, wear, seams,
decals, labels) and review loop there apply to turrets too. Tags as in SKILL.md: [owner] = owner design
feedback, [HARD] = measured or rendered, [SOFT] = inferred.

## Contents
- Workflow additions
- Structure and moving parts
- The gun itself
- Equipment and ammunition
- Checking

## Workflow additions

1. **The design doc also names the subpart chain**: which subpart each part moves with, the subpart and dummy
   names, and the elevation limits. If the model replaces an existing weapon, read its definition first so the
   names match it (`weapons-turrets.md`, "Splitting a turret into subpart scenes").
2. **Ask what drives the subparts.** Vanilla turret types hard-code names and spin; WeaponCore reads part names
   from its config, so any names work and a spinning barrel can sit under a missile-style chain
   (`weapons-turrets.md`, "Spinning barrels").
3. **Keep pivot, muzzle and camera markers** as plain empties while detailing in one scene; they become the
   subpart empties and dummies at the split.

## Structure and moving parts

- **Clearance first.** The barrel or muzzle must clear blocks in front (the owner asked for the barrel at least
  1.75 to 2 m above the mount face on a large turret). Hit that with base and support proportions, not by
  stacking a tall plinth.
- **Pivot below anything it carries.** Put the elevation pivot low enough that the bearings never cut into the
  plate or shell above them.
- **Elevation equipment stays inside the supports** and within reach of the pivot axis; anything in a swept corner
  hits the legs as soon as the gun tilts [owner]. A part on the pivot axis (an ammo drum, a trunnion hub) never
  clips. Run the sweep check before export (`weapons-turrets.md`, "Clearance for moving subparts").
- **The elevation plate needs visible support** [owner]: solid yoke plates from the plate down to round hubs on
  the trunnion, with box beams along the plate underside, instead of a thin trunnion or open V-struts.
- **Nothing hangs past the turntable**: legs and pistons stay inside its edge.

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
  carries no muzzle when WeaponCore animates the spin. Camera dummy just in front of a recessed window in the
  shell, outside every collision shape.

## Equipment and ammunition

- **Fill the space under the elevation part** with one feature cylinder on the pivot axis (an ammo drum with
  bands) and machine boxes on a shared frame (`design-detailing.md`, "Equipment and filling space").
- **Show how ammo reaches the gun** [owner]. One good answer: a fixed docking column on the azimuth axis rising
  through the turntable centre (a rotary seal ring where the hub turns round it) and a matching receiver on the
  elevation part that lines up over it at 0 degrees. Check the receiver's closest pass over the column across the
  full elevation range; guide pins clipped at small angles, so the mouth and seal carry the docking look instead.
  Give the receiver a feed tube of the same style running on into the magazine (drum), with bolted collars at
  both ends, and clear whatever equipment sat in that path.
- **Terminal and inventory access on the fixed base** [HARD, game code: subpart detectors are ignored]: outside
  the turntable's sweep. A keypad embedded flat and centred in the base's back face, turned 90 degrees, read
  best [owner].
- **Calibre and unit stencils underneath** (an underside access panel), not on a front face [owner].

## Checking

- **Left and right are the weapon's own**, facing its muzzle: with the muzzle at Blender -Y, the turret's left is
  +X [owner].
- Before the in-game test, list what is unverified: subpart facing, spin axis, muzzle direction, elevation limits
  and LOD switches.
