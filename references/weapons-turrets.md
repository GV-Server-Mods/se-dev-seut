# Turrets, weapons and tools (ConveyorSorter, WeaponCore, ToolCore)

Modeling the parts a weapon or tool framework needs. The frameworks read the model by names, so the
subpart and dummy names must match the config exactly.

## Contents
- Block type
- Subpart tree
- Dummies and empties
- What the configs expect
- Vanilla Gatling turret as a template
- Build checklist
- Unverified

## Clearance for moving subparts [HARD, measured on a gatling turret model; owner design feedback]

- Anything on the elevation subpart that sits outside the azimuth supports (legs, yokes) hits them as soon as
  the gun tilts [owner]. Keep elevation equipment between the supports, and within the distance from the
  pivot axis to the nearest fixed surface below (coin or deck), so it can never reach it. A part on the
  pivot axis (an ammo drum, a trunnion hub) never clips at any angle.
- Check numerically before export: rotate every elevation vertex about the pivot axis through the real range
  and record the lowest point. Mind the sign: with Blender +Y as the back and -Y as the muzzle side, a positive
  rotation about +X lowers the muzzle, so the range -20 down / +85 up is `range(-85, 21)` degrees.
- Equipment that would otherwise hang in a swept corner can go on top of the elevation plate instead, as one
  asymmetric detail.

## Block type [HARD, WeaponCore and ToolCore wikis]

WeaponCore weapons and ToolCore tools are defined as `ConveyorSorter` blocks (`MyObjectBuilder_ConveyorSorterDefinition`)
so Keen's weapon and tool code does not run in the background. The sorter can be fixed, a turret, or both.
Vanilla-class turret types (`LargeGatlingTurret`, `LargeMissileTurret`, `InteriorTurret`) need
`<AiEnabled>false</AiEnabled>` in the SBC. Sorter turrets need no required subparts for fixed use; a turret
needs a subpart tree you define.

## Subpart tree [HARD, SEUT source and vanilla FBX; WeaponCore wiki]

Each moving part is its own scene of type `Subpart` linked by a subpart empty named `subpart_<Name>`.
Vanilla Gatling turret: the base model holds `subpart_GatlingTurretBase1`; that subpart holds
`subpart_GatlingTurretBase2`; that holds `subpart_GatlingBarrel`. Chain depth is arbitrary.

| Vanilla type | Subparts | Role |
|---|---|---|
| Interior turret | `InteriorTurretBase1` (azimuth), `InteriorTurretBase2` (elevation, muzzle) | |
| Gatling turret | `GatlingTurretBase1` (azimuth), `GatlingTurretBase2` (elevation), `GatlingBarrel` (muzzle; spin hard-coded) | vanilla node required if you want vanilla spin |
| Missile turret | `MissileTurretBase1` (azimuth), `MissileTurretBarrels` (elevation, muzzle) | |
| Gatling gun | `Barrel` (spin hard-coded, muzzle) | |

SEUT ships these as one-click presets: `scene.add_preset_subpart` includes `subpart_InteriorTurretBase1/2`,
`subpart_MissileTurretBase1`, `subpart_MissileTurretBarrels`, `subpart_GatlingTurretBase1/2`,
`subpart_GatlingBarrel`, `subpart_Barrel` and others (23 presets in 1.2.1). For custom turrets use
`scene.add_custom_subpart` with your own names.

Pivot rule [SOFT]: place each subpart's origin on its rotation axis so rotation looks right in game; set
the empty's location where the part attaches.

## Dummies and empties [HARD, SEUT 1.2.1 preset list]

Add with `scene.add_dummy` (UI: Add > Empty > Dummy). Relevant presets:

| Name prefix | Use |
|---|---|
| `muzzle_projectile_` | where projectiles start; fire direction is always the empty's +Y axis |
| `muzzle_missile_` | where missiles start; keep some distance from the mesh or they collide |
| `dummy_camera` | camera position and orientation for cockpit-type blocks and turret-type blocks |
| `dummy_head` | overrides head camera position in cockpit-type blocks |
| `dummy_detector_shiptool_` | origin of ship tool effects (not visual) |
| `dummy_particles1` / `dummy_particles2` | welder / grinder particle origins |
| `light_` | light source origin |
| `thruster_flame_` | thruster flame point; empty size is flame width |
| `Center`, `MirroringCenter` | block centre and mirroring pivot |
| `dummy_detector_conveyorline_*`, `detector_conveyor_*` | conveyor connection points (`interaction-highlights.md` for the highlighted kind) |

Rotate each muzzle so its +Y axis points the way the weapon fires. Muzzle empties live in the subpart that
moves with the barrel (the part named as the muzzle part in the config), or in the main model for fixed weapons.

Subpart direction [SOFT]: a subpart scene's forward is +Y while a main scene's is -Y, so a subpart linked the
normal way can come out turned round (the owner saw this on an earlier weapon model, and a door tutorial describes
the same fix: rotate the subpart empty 180 degrees about Z). Check each turret subpart's facing in game, and
check the muzzle direction after any rotation. Details: `doors-subparts.md`.

## What the configs expect

**WeaponCore** [wiki: Weapon - Minimal Configuration, Weapon Block Types]:
`ModelAssignments > MountPoints` entries carry `SubtypeId`, `MuzzlePartId`, `AzimuthPartId`,
`ElevationPartId` and a `Muzzles` array of dummy names. Example turret: `AzimuthPartId` `MissileTurretBase1`,
`ElevationPartId` and `MuzzlePartId` `MissileTurretBarrels`, `Muzzles` `muzzle_missile_001`. A fixed
weapon uses `"None"` for all three part ids and takes its muzzle from the main model. Part ids are the
subpart names without the `subpart_` prefix. SBC fields for a sorter turret include aiming limits
(`MinElevationDegrees`, `MaxElevationDegrees`, `MinAzimuthDegrees`, `MaxAzimuthDegrees`), `RotationSpeed`,
`ElevationSpeed`, `MaxRangeMeters`, `BuildProgressModels` and `UseModelIntersection`.
Spinning barrels [HARD, WeaponCore source `Coreparts/Definitions/Gatlings.cs`, `WeaponState.cs`]: the mount
point entry also has `SpinPartId` (the subpart that spins, `"None"` otherwise). The vanilla gatling example
uses `SpinPartId` and `MuzzlePartId` `GatlingBarrel`, `AzimuthPartId` `GatlingTurretBase1`, `ElevationPartId`
`GatlingTurretBase2`. `HardPoint.Other.RotateBarrelAxis` picks the spin axis in the spin part's own frame
(1 = X, 2 = Y, 3 = Z; the gatling uses 3), and `Loading.SpinFree = true` spins it while not firing. So any
subpart names work for a WeaponCore turret, including a spinning barrel under a missile-style chain; keep the
barrels along the spin axis and the muzzles on the spin part.

**ToolCore** [wiki: Definition Fields, Turret Fields, Example Turret Definition, Required Files]:
tools are also sorters. A turret lists one or two `Subpart` entries with `Name` (no `subpart_` prefix),
`RotationAxis` (`Up`, `Forward` or `Right`), `RotationSpeed`, `MinRotation`, `MaxRotation`, plus `TargetRadius`.
Work shape fields use an `Emitter` dummy (for example `muzzle_projectile_001`) as the origin. For a dummy
inside a subpart the wiki says the name must include `subpart_`; the exact form is unclear, test it.
Definitions list in `Data\ToolCoreFiles.txt`, one file name per line, all directly in `Data`. Add the tool to the
`ShipTools` category (`ConveyorSorter/<Subtype>`) to bind left and right click.

## Vanilla Gatling turret as a template [verified by import]

SDK files `<ModSDK>\OriginalContent\Models\Cubes\large\GatlingTurret*.FBX` (+ `.xml`, `.hkt`):
- `GatlingTurret` (base): one root plus parts for terminal and conveyor detectors, and `subpart_GatlingTurretBase1`.
- `GatlingTurretBase1`: 3 meshes (body, chrome, colorable) and `subpart_GatlingTurretBase2`.
- `GatlingTurretBase2`: 6 meshes (including `_lenses`, `_stuff`, `_darker`) and `subpart_GatlingBarrel`.
- Each part has its own LOD1..LOD3 (20 / 60 / 150 m) and the base has Construction_1..3 stages.
- Separate meshes per material (`_chrome`, `_colorable`, `_darker`) keep each mesh on one material.
- Base materials: `PaintedMetal_Colorable`, `PaintedMetalScratched_*`, `PaintedMetal_Darker`, `Chrome`,
  `Decals`, `Terminal`, `Conveyor`, `Metal_Dull` (from its model XML).

## Splitting a turret into subpart scenes [HARD for the export, SOFT for the in-game result]

Done on a large gatling turret built in one scene with a `part` tag on every object:

1. Create one `subpart` scene per moving part (`recreate_collections` each), then move each object into its
   scene's Main and set `matrix_world = R @ Translation(-pivot) @ old_matrix_world`, with `R` = 180 degrees about
   Z. The pivot goes to the scene origin, and the 180-degree turn makes up for SEUT's `-Z` forward axis on subpart
   scenes (`doors-subparts.md`), so in each subpart scene the muzzle points +Y. That way every subpart empty and
   dummy keeps an identity rotation and each part's forward matches the block's. If parts show up backwards in
   game, take the turn out of the subpart scenes and turn the main scene's first subpart empty instead.
2. Child empties sit at `R @ (child pivot - parent pivot)`. Muzzle and camera dummies get identity rotation,
   so their +Y lies along the barrels.
3. Parent every object in each Main under one root (E031 fires on subpart scenes too), including empties and
   highlight targets, then link each `linkedScene` with the crash-safe recipe in `bpy-recipes.md`, one per call.
4. Collision: vanilla turret code (`MyLargeTurretBase`) creates no physics for its subparts, so subpart collision
   is never used. Give the base model a few shapes (slab, turntable, a cylinder over the azimuth part below the
   elevation sweep), and keep them clear of the scope or camera dummy at every elevation (WeaponCore checks line
   of sight from it).
5. Before choosing names, read the weapon definition the model replaces. A replacement model must match its
   subpart names (`AzimuthPartId`, `ElevationPartId`, `SpinPartId`), its `Muzzles` list and `Scope` (often
   `camera`), or the config has to change with it.
6. Check the split by rebuilding the turret in the main scene from temporary objects that share the LOD or Main
   meshes, placed with the inverse transforms, and render it before export.

## Build checklist

1. Plan the part chain and write the names down before modeling (names are the contract with the config).
2. One scene per moving part; link with `subpart_<Name>` empties; grid size identical across scenes (W001/W020).
3. Muzzle and camera dummies placed and rotated; test with `look` along the +Y axis.
4. No collision on subparts unless vanilla allows it (wiki); put collision on the base.
5. LODs and build stages per `block-scenes.md`.
6. Config names exactly match subpart names (minus the prefix) and dummy names.

## Unverified

- Dummy-in-subpart naming for ToolCore; whether vanilla barrel FBX carries `muzzle_projectile_001`.
- Weapon-side dummies beyond the page list; WeaponCore animation basics (`Animation-Basics`) not read.
- Nothing here has been run through SEUT export or tested in game.
