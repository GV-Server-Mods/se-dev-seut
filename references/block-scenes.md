# Ideal block scene layout: Main, LODs, build stages

What a complete SEUT block scene holds, and what vanilla does for each part. SEUT creates the collections;
this says what to put in them.

## Contents
- Scene layout
- LODs
- Build stages
- Collision
- Vanilla reference numbers
- Per-block-type checklist

## Scene layout [HARD, verified in SEUT 1.2.1]

| Collection | Holds | Notes |
|---|---|---|
| `Main (<id>)` | the finished block, one root object, detail parented under it | all empties and linked meshes live here |
| `Collision - Main (<id>)` | up to 10 convex objects with rigid bodies | build stages fall back to this one |
| `LOD1..LOD3 (<id>)` | simplified copies of Main | default distances 25 / 50 / 100 m, each higher than the last |
| `BS1..BS3 (<id>)` | build progress stages | scaffold looks; `BS1_LOD1` also exists |
| `Mountpoints`, `Mirroring`, `Render` | SEUT tool collections | managed by the mode toggles, not by hand |

Subpart scenes (moving parts) use the same layout without BS or mountpoints; see `weapons-turrets.md`.

## LODs

- Distances are per model, set in the scene's collection settings, strictly increasing (E011).
- LOD1 keeps the silhouette and the main shapes, drops bevels and sub-texel detail (SEUT `Remove Bevels`
  exists for this). Later LODs reduce further. Keep UVs and material names identical so materials do not pop.
- Empties (detectors, dummies, subpart links) live in Main only [SOFT, vanilla puts them there].
- Match the weight of the block: a tiny armor block needs fewer LODs than a turret [SOFT].
- Worked example, a bevelled armor cube [HARD, exported by a test run]: Main 56 verts (bevelled), LOD1 24 verts
  (one bevel segment) at 60 m, LOD2 a plain 8-vert cube at 120 m. A LOD3 identical to LOD2 exports and works
  (it was set to 240 m) but adds nothing: vanilla armor stops at two LODs (table below), so skip LOD3 for a
  cube and keep it for blocks with real detail to shed.
- Every LOD mesh needs the same material and real UVs, like Main. Each exports as its own
  `<SubtypeId>_LODn.mwm`, and Main's `.mwm` lists them.

## Build stages

- 1 to 3 stages, each progressively more complete than the last. `Apply Construction` assigns the Construction
  material; `Cut and Solidify` builds the scaffold look [HARD].
- The SBC lists them as `<BuildProgressModels><Model BuildPercentUpperBound="0.33" File="...Construction_1.mwm"/>`.
  Vanilla uses 0.50 / 1.00 for two stages (oxygen tanks) and ToolCore's example uses 0.33 / 0.66 / 1.00.
- Each stage's collision follows Main's; do not give BS its own collision model [HARD, wiki].
- Wall-style armor shapes are usually stage-less in modded blocks; decide per block with the user [SOFT].

### Designing the stages [owner brief; HARD for the build, SOFT until seen in game]

- **Every stage shows the whole outline** [owner]. A stage that starts small and grows collides with the player
  or a neighbouring grid when it grows. Since every stage uses Main's collision anyway, make every stage fill
  the same outline, and let detail grow, not size.
- **Grow detail, and show internals with basic shapes** [owner]: not just more and more frame. What worked on a
  large turret:
  - BS1: a strip frame over every major part (base slab, turntable, supports, plate, shell, barrel), plus a few
    solid core pieces (central column or mast, pivot shaft).
  - BS2: the lowest parts turn solid; mechanisms appear as plain solids (drum, drive and electrical boxes,
    feed parts, individual barrels, equipment inside the shell).
  - BS3: most of the outline is solid; leave a few panels and the top as open frame so the internals still
    show, and add the big recognisable parts (mantlet, muzzle, gearboxes).
- **Vanilla look** (the SDK's `GatlingTurretConstruction_1..3`: 2,040 / 2,952 / 3,643 faces, one `Construction`
  material, flat strips that trace the silhouette). Build a low-poly proxy per part from the finished model
  (octagon or 12-16-sided prisms from the part's bounds, a 2D convex hull of a support's side profile
  extruded through its thickness, a cylinder plus hemisphere for a dome), then per face `inset_individual`
  (about 7 cm on a large block), delete the original faces and `solidify` (about 2 cm). Solid pieces are the
  same proxies without the cut.
- One mesh per stage, `Construction` material only, flat shading, box UVs offset from the origin (a vertex on
  the axis at UV (0,0) repeated across a pole made SEUT warn about UVs at (0,0) on the smallest stage).
- **Nothing may float** [owner: a turntable frame and a shell-mounting plate looked like they hung in mid air
  in BS1]. Every stage needs the load path, even as frames: whatever carries a part in the finished model
  (bearing ring under a turntable, webs or brackets from a plate down to its pivot, hubs and bearings at the
  pivot) goes into BS1 as a frame or simple solid. Gaps that are fine in the finished model (a 1.5 cm
  clearance under a turntable) read as floating when the parts are bare frames, so fill them in the stages.
  A strip frame only has material at its outline: supports that meet the middle of a framed plate touch nothing
  and still look like they float [owner]. Add solid beams under a framed plate (along the supports, plus cross
  beams reaching the frame's edge strips and any central post) until every support visibly meets metal.
- **Merge outline points closer than the strip width** before insetting: a support's hull with 2 cm corner
  edges and a 7 cm inset exploded to 270 km.
- A stage mesh sits in its `BS<n>` collection; SEUT exports `<SubtypeId>_BS<n>.mwm` beside the main model.
  The finished turret came to 3,400 / 3,100 / 2,000 triangles per stage. Subparts are not shown while the block
  is under construction (the stage model has no subpart empties) [SOFT, check in game], so a turret's stages
  must include the moving parts in their rest pose.

## Vanilla reference numbers [HARD, SDK `OriginalContent` model XMLs]

| Model | LOD1 | LOD2 | LOD3 |
|---|---|---|---|
| Armor piece `ArmorCenter` (not the armor cube, which is built from `SquarePlate`) | 60 m | 120 m | none |
| Armor build stages (`ArmorCenterConstruction_N`) | 5 m | none | none |
| Small cargo container | 5 m | 60 m | none |
| Gatling turret and its subparts | 20 m | 60 m | 150 m |
| Turret build stages | 20 m | none | none |

SEUT's own defaults (25 / 50 / 100 m) are a starting point; set distances to the block's size and weight.
Vanilla stage models carry their own `.hkt` files; mods should not copy that (see Collision above).

## Per-block-type checklist

1. Block size and bounding box set; origin at block centre.
2. Main: single root, all detail parented; materials chosen with `materials-catalog.md`.
3. Interaction points as highlight empties (`interaction-highlights.md`); dummies from `weapons-turrets.md`.
4. Collision: few convex pieces inside the box.
5. LOD1..LOD3 with increasing distances; BS1..BS3 if the block uses build stages.
6. Mountpoints and mirroring set; run `errors.md` checklist; export.
