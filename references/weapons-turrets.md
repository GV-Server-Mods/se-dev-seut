# Turrets, weapons and tools (ConveyorSorter, WeaponCore, ToolCore)

Modeling the parts a weapon or tool framework needs. The frameworks read the model by names, so the
subpart and dummy names must match the config exactly.

## Contents
- Barrels on any weapon
- Clearance for moving subparts
- Recoiling barrels and twin barrels
- Block type
- Subpart tree
- Dummies and empties
- What the configs expect
- Vanilla Gatling turret as a template
- Splitting a turret into subpart scenes
- Build checklist
- Unverified

## Barrels on any weapon [owner]

Applies to every SE weapon model: turrets, fixed guns and handheld weapons. Do not model a barrel's full
internal length; a short recess with a dark floor reads as a bore from any normal viewing angle. Skip rifling
and deep bores except on huge cannons (battleship scale) that players can actually look down; on small and
medium calibres they only waste triangles.

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

## Recoiling barrels and twin barrels [HARD: WeaponCore `SessionAnimationMgr.cs`, SEUT source, a shipped twin-barrel turret's models and animation]

- A WeaponCore movement adds its `Transformation(x, y, z)` (metres) to the subpart's local position, so it
  moves along the parent part's axes. With unrotated empties under the turned subpart scenes ("Splitting"
  below), +Z is backward: a 2 m recoil is `Transformation(0, 0, 2)` out and `(0, 0, -2)` back.
- Each recoiling barrel is its own subpart scene linked from the elevation part. The muzzle dummies stay on the
  part named as `MuzzlePartId` (the elevation part), so they do not travel with the recoil.
- The barrel mesh runs back into the mantlet or gun shield by more than the recoil travel, so no gap opens at
  full recoil (2.36 m of hidden barrel for a 2 m recoil on the shipped turret). Check that hidden end at the
  minimum and maximum elevation: it stays inside the elevation part and clear of the azimuth part.
- One subpart scene may be linked by several empties (twin barrels): SEUT has no check against it and writes
  the same `file` on each empty, and the game loads that one model for each dummy. Link each empty with the
  crash-safe recipe (`bpy-recipes.md`, "Subparts, dummies, mirroring and mountpoints from script") and give each
  its own collection instance for the icon (`bpy-recipes.md`, icons step 4).

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

Subpart direction: on vanilla turret types the game drops the subpart empty's rotation, so the content of each
subpart scene is turned 180 degrees (muzzle toward +Y); the rule and the sorter-turret case are in
`modeling-rules.md`, "Which way a subpart faces". Check the muzzle direction after any rotation.

## What the configs expect

**WeaponCore** [wiki: Weapon - Minimal Configuration, Weapon Block Types]:
`ModelAssignments > MountPoints` entries carry `SubtypeId`, `MuzzlePartId`, `AzimuthPartId`,
`ElevationPartId` and a `Muzzles` array of dummy names. Example turret: `AzimuthPartId` `MissileTurretBase1`,
`ElevationPartId` and `MuzzlePartId` `MissileTurretBarrels`, `Muzzles` `muzzle_missile_001`. A fixed
weapon uses `"None"` for all three part ids and takes its muzzle from the main model. Part ids are the
subpart names without the `subpart_` prefix. SBC fields for a sorter turret include aiming limits
(`MinElevationDegrees`, `MaxElevationDegrees`, `MinAzimuthDegrees`, `MaxAzimuthDegrees`), `RotationSpeed`,
`ElevationSpeed`, `MaxRangeMeters`, `BuildProgressModels` and `UseModelIntersection`.
Vanilla turret types under WeaponCore [HARD, WeaponCore `WeaponController.cs` and `MyLargeTurretBase`]:
WeaponCore drives the block through `SetManualAzimuthAndElevation` at its own `RotateRate`/`ElevateRate`, and
the game clamps the angle to the SBC `MinElevationDegrees`/`MaxElevationDegrees`. Keep those SBC limits equal
to WeaponCore's `HardWare` `MinElevation`/`MaxElevation`, or WeaponCore chases an angle the block cannot reach.
With `AiEnabled=false` the vanilla idle rotation never runs. Out-of-arc targets and return-to-home both show as
slow turning; that is WeaponCore behaviour, not a model fault.
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
   Z. The pivot goes to the scene origin, and the 180-degree turn makes up for the half turn the game drops on
   vanilla turret types (`modeling-rules.md`, "Which way a subpart faces"), so in each subpart scene the muzzle
   points +Y and every subpart empty and dummy keeps an identity rotation. The gatling turret this was done on
   shipped built this way. For a WeaponCore sorter turret, check the facing in game before detailing further.
2. Child empties sit at `R @ (child pivot - parent pivot)`. Muzzle and camera dummies get identity rotation,
   so their +Y lies along the barrels.
3. Parent every object in each Main under one root (E031 fires on subpart scenes too), including empties and
   highlight targets, then link each `linkedScene` with the crash-safe recipe in `bpy-recipes.md`, one per call.
4. Collision: vanilla turret code (`MyLargeTurretBase`) creates no physics for its subparts, so subpart collision
   is never used. All collision goes in the base model, as simple shapes covering the turret at rest [owner]:
   what worked on a domed turret was four shapes: a box for the slab, a hull prism for the turntable, one hull
   prism at the dome's radius from the turntable up to the dome's base (covering supports and shell together),
   and a sphere for the dome, with vertices placed in block space and each object left at the origin (`modeling-rules.md`, "Collision": a moved object's shape lands at the block
   centre). Build the slab hull from the slab's outline (an octagon prism for a cut-corner slab). The scope dummy (WeaponCore `Scope`, usually `camera`) must stay
   outside that static shell at every elevation: WeaponCore casts its line-of-sight ray from the scope, and a hit
   on its own grid resets the target (`RayCheckSelfHit`). With the scope behind the radome window it sat inside
   the shell from 2 to 90 degrees, and the turret turned a few degrees every few seconds instead of tracking
   [owner; SOFT: cause read from code, fix not yet confirmed in game]. Check the scope's path through the
   elevation range against the collision shapes before export. On vanilla turret types the game also uses a
   dummy named `camera` on the barrel subpart for the manual-control view (`MyLargeBarrelBase`), so keep
   `camera` where the player should look from (a camera recess) and point WeaponCore's `Scope` at a muzzle
   dummy instead. With no `Scope` set, WeaponCore falls back to the middle muzzle (`GetScope`).
5. Before choosing names, read the weapon definition the model replaces. A replacement model must match its
   subpart names (`AzimuthPartId`, `ElevationPartId`, `SpinPartId`), its `Muzzles` list and `Scope` (often
   `camera`), or the config has to change with it. The rest of the replacement contract (size, mount points,
   ports, shared files, the old dummies): `design-detailing.md`, "Replacing a block's model".
6. Check the split by rebuilding the turret in the main scene from temporary objects that share the LOD or Main
   meshes, placed with the inverse transforms, and render it before export.

## Build checklist

1. Plan the part chain and write the names down before modeling (names are the contract with the config).
2. One scene per moving part; link with `subpart_<Name>` empties; grid size identical across scenes (W001/W020).
3. Muzzle and camera dummies placed and rotated; test with `look` along the +Y axis.
4. No collision on subparts unless vanilla allows it (wiki); put collision on the base.
5. LODs and build stages per `block-scenes.md`.
6. Config names exactly match subpart names (minus the prefix) and dummy names.
7. SBC of a vanilla turret type under WeaponCore: `<AiEnabled>false</AiEnabled>` ("Block type"), elevation and
   azimuth limits equal to WeaponCore's `HardWare` ("What the configs expect"), and `<EmissiveColorPreset>` when
   the model has state lamps (`materials-catalog.md`, "Emissive presets and colors").

## Unverified

- Dummy-in-subpart naming for ToolCore; whether vanilla barrel FBX carries `muzzle_projectile_001`.
- Weapon-side dummies beyond the page list; the WeaponCore wiki's `Animation-Basics` page (the movement code
  above was read instead).
- Subpart facing on WeaponCore sorter turrets, and recoil clearance seen in game. The ToolCore notes have not
  been run through SEUT export or tested in game; the vanilla-type turret notes come from a SEUT-built
  WeaponCore turret loaded in game.
