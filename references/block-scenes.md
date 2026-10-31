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

## Build stages

- 1 to 3 stages, each progressively more complete than the last. `Apply Construction` assigns the Construction
  material; `Cut and Solidify` builds the scaffold look [HARD].
- The SBC lists them as `<BuildProgressModels><Model BuildPercentUpperBound="0.33" File="...Construction_1.mwm"/>`.
  Vanilla uses 0.50 / 1.00 for two stages (oxygen tanks) and ToolCore's example uses 0.33 / 0.66 / 1.00.
- Each stage's collision follows Main's; do not give BS its own collision model [HARD, wiki].
- Wall-style armor shapes are usually stage-less in modded blocks; decide per block with the user [SOFT].

## Vanilla reference numbers [HARD, SDK `OriginalContent` model XMLs]

| Model | LOD1 | LOD2 | LOD3 |
|---|---|---|---|
| Armor (`ArmorCenter`) | 60 m | 120 m | none |
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
