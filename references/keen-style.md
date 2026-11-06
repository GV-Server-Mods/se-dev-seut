# Keen's block style: measured sizes

The numbers that make a block look like Keen made it: edges and shading, how surfaces are layered and laid out,
the standard parts, panel lines, bolts, signs and materials. Use it to size a design (`design-detailing.md` is the
workflow; this file is the values) and to check a finished block against vanilla ("Checking a model").

[HARD, measured]: headless Blender scripts measured 60 vanilla ModSDK models (28 newer large grid, 12 newer small
grid, 20 classic), and a second, independent script re-measured every value. A value is the median across models,
each model weighted evenly, with the middle range in brackets; counts are per block. Cell edge: 2.5 m large,
0.5 m small. "Atlas3 #14" means piece 14 in `atlas-regions.md`. For people, the same rules with labelled pictures:
[Keen Block Style](https://claude.ai/artifact/Q3bq4kdc1ut2SMKCLEjHpt); share it when a user wants to see an example.

## Contents
- Which rules win
- Grid scale
- Edges, rounds and shading
- Layers and silhouette
- Surface layout
- Standard parts
- Panel lines
- Bolts and rivets
- Signs and markings
- Materials and decal sheets
- Checking a model

## Which rules win

- **Era.** Keen has two styles. The newer one (DLC-era reskins and recent blocks, models `N_*`) layers the geometry
  and dresses it with Atlas1-4 and ButtonsAtlas decals; the classic one (`L_*`, `S_*`) keeps big faces plain and uses
  the Decals, Paneling and TextAtlas sheets. Everything below is the newer style unless marked; build in it unless
  the user wants classic (each table's Classic column lists what changes).
- **Keen's numbers set the look**: sizes, spacing, line widths and part scale, so a new block matches the vanilla
  blocks beside it.
- **The skill's craft rules win where they differ from Keen**: decals sit 1.5 mm off the surface (Keen's sit almost
  flush), every seam end is pointed (Keen ends free lines square), round bolt heads get random angles (Keen leaves
  them square), parts smooth by angle at 30 degrees (Keen's newer blocks about 60; "Edges, rounds and shading"),
  and every decal passes the offset and snap checks in `bpy-recipes.md`.

## Grid scale

- **Small grid is not large grid divided by 5.** Surface details shrink to about a third: chamfers 8-10 to 3-5 mm,
  layers about 40 to 13 mm, plate thickness 44 to 15 mm, plate seams 11 to 3 mm, frames 80-100 to about 25 mm.
- **Decals shrink to about half** (0.4-0.65x) on small grid.
- **Fixed-size items keep their real size on both grids**: conveyor ports (1.36 m large port, 340 mm small port),
  the terminal face, screens, single ButtonsAtlas buttons, text warning plates (WARNING HIGH PRESSURE #18 is the
  exception, about half size). Codes shrink a little (30 to 20 mm).

## Edges, rounds and shading

### Chamfers and rounds

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Chamfer hard edges with one flat 45-degree facet | 8 mm (7-10); 10 most common, then 7 and 5; housings about 10, small parts about 7 | 3.4 mm (3-5), most often 3 or 5 | about 9 mm large grid, 5 mm small |
| Bevel nearly every hard edge, most as one facet | 90% (80-99) of hard edges; about 80% of them one flat 45-degree face | 85% (70-100); about 80% one face | same, mostly single chamfers |
| Give inner corners the same bevel or a little smaller | 7 mm (6.5-10) | 5 mm (3-9) | |
| Keep a bevel one flat 45-degree face up to | about 20 mm; under 12 mm one facet on 99-100% of edges | about 12 mm; one facet on 96% at 5-8 mm, 70% at 8-12 mm | same switch point |
| At 12-20 mm, mostly keep one 45-degree face (plain or creased), sometimes a true round | true round 37% (15-63), 45-degree face split by a slight 5-degree crease 30% (5-56), plain 45-degree face 14% (0-44); 61% one facet with all models pooled | one facet 54%, creased 45-degree face 26%, true round 16% | mostly creased 45-degree faces (61%), not rounds |
| Above about 20 mm, round the edge with 3 facets | 20-70 mm: a round on 79% (60-90), 3 facets on 79% of those; 70-150 mm: a round on 77% (23-100), 3 facets on 70%, 4-6 on 18% | 20-50 mm: rounds, 3 facets on 93% | 20-150 mm: rounds mostly 3 facets |
| Turn a 3-facet round on a 90-degree corner in four equal 22.5-degree steps | on 93% (77-100) of rounds; end facets 0.56 (0.38-0.80) of the middle facet's width | | |

- **A creased bevel still reads as one face**: a wide 45-degree bevel split into two strips by a slight 5-degree
  crease looks like a single 45-degree face.
- **Build the round by hand**: make a 45-degree middle facet, often the widest, and soften its two edges with
  22.5-degree end facets. A default 3-segment Blender bevel gives a different round (15 / 30 / 30 / 15-degree steps).

### Cylinders

Choose the side count from the diameter so the facets stay about 15 mm wide on thin rods, 30 mm on mid sizes and
60 mm on big drums. Use even counts, mostly multiples of 4, and shade the sides smooth.

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Give a rod under 60 mm across | 8 sides (8-9) | 8 under 30 mm; 10 (8-12) at 30-60 mm | 8 |
| Give a 60-120 mm cylinder | 8 or 16 (median 10, 8-14) | 16 (16-21) | 8 |
| Give a 120-250 mm cylinder | 16 most often (median 13, 10-16) | 24 (22-28) | 12 |
| Give a 250-500 mm cylinder | 20 (14-24) | | |
| Give a 0.5-1 m cylinder | 24 (20-32) | | |
| Give a 1-2 m cylinder | 32 | | |
| Give a cylinder over 2 m | 56 (36-64) | | |
| Check the facet width | 14 mm (12-18) under 60 mm; 31 (26-34) at 60-250 mm; 60 (50-78) at 0.25-1 m; 179 over 1 m | 9.5 mm (7.6-11.3) at 15-60 mm; 16 (12-19) at 60-250 mm | coarser on mid sizes |

### Shading

Keen shades by the angle between faces and weights the normals toward the bigger face, so flat faces stay flat and a
chamfer reads as a soft round. Values are the share of edge length shaded smooth, except the last row.

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Edges under 35 degrees | 93-100% | | |
| 45-degree chamfer edges | 93% (83-97) | 90% (76-94) | |
| 46-60 degree edges | 89% (55-96) | | |
| 60-80 degree edges | 52% (35-94) | 68% (27-99) | mostly smooth: 92% large grid, 97% small |
| Keep 90-degree edges hard | outer 7% (1-30), inner 5% (0-62) | outer 13% (2-84) | outer edges mostly smooth: 70% (15-94) on large grid |
| Weight the normals toward the bigger face | on 84% (68-91) of smooth 40-50 degree edge length; plain averaging 9% (4-25) | 88% (77-91) | same (88%) |

- **Smoothing angle**: the skill's default stands. Keen's value on newer blocks is about 60 degrees, 45-degree
  chamfers included, with normals weighted by face area. The skill smooths by angle at 30 degrees, then applies
  Weighted Normal (Face Area, Keep Sharp) (`modeling-rules.md`, "Geometry and shading"), which leaves 45-degree
  chamfers hard-shaded where Keen's read as soft rounds.

### Examples

- **Centred Door (N_L_CentredDoor)**: the frame is an 86 mm flat face with a single 7 mm 45-degree chamfer on each
  edge, 100 mm across in all.
- **Beacon (N_L_BeaconReskin)**: the 734 mm column has 32 sides (facets about 72 mm), the 234 mm lamp-housing bore 16
  (about 46 mm) and the 26 mm antenna rods 8 (about 10 mm).
- **Turret Control Block (N_L_TurretControlBlock)**: the block corner is a 38 mm 3-facet round, far larger than the
  usual 8-10 mm chamfer.
- **Flare Launcher (N_L_FlareLauncher)**: the end of the 134 mm frame band has 30 mm 3-facet rounds in even
  22.5-degree steps.

## Layers and silhouette

### Layers and depth

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Step surfaces in layers, raised plates and sunk panels alike | 30-50 mm: most near 33 (28-40), all steps 43 (31-62) | raised 13 mm (9-16), sunk 13.5 (10-16.5) | shallower: about 28 mm large grid, 7 mm small |
| Add deeper insets, about 100 mm, on turret and thruster bodies | 75-150 mm; about a third of all steps | | |
| Make separate plate parts | 44 mm thick (30-53) | 15 mm (14-31) | |
| Leave a flat frame round an inset panel, about 3-5% of the cell | 81 mm (59-125) round closed pockets, 97 (67-132) over all insets | 26 mm (17-39) | narrower: 30-40 mm on large grid (cargo-style 19 mm ribs: "Surface layout") |
| Split flush plates with a V seam, both plate edges chamfered at 45 degrees | 11 mm wall to wall (7-13), 21 (15-30) at the top, 12 deep (9-17); in 22 of 28 models | 3 mm wall to wall (2-3.5), about 9 (6-14) at the top, 3 deep (2.5-6); in 5 of 12 | rare between separate plates: about 6 mm (2 large models); grooves are cut into one part instead: V about 28 x 7 mm with 40-degree sides, flat-bottomed U about 37 x 5 mm in 8 of 10 models (about 1 groove in 8) |
| Give each face 3-4 depth levels, counting every level that holds at least 5% of its flat area ('Surface layout' names only the outer surface and the main recess depths) | 3.5 (3-4); faces with 2 levels 20%, 3 26%, 4 23%, 5 16% | 3.5 (2.9-5) | 3.1 (2-4.5) |
| Put two thirds to three quarters of the flat area on the top two levels | 64% (47-78) of the flat area; 72% (61-88) of the area on counted levels | 62% (41-86); 67% | |
| Keep each face's front-to-back depth about | 100 mm (40-171) on mostly mounted faces; 316 (183-704) over all faces | 41 mm (31-128) | not shallower: about 100 mm on mounted faces, 347 (99-1327) over all |

### Tilts, ramps and corner cuts

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Keep tilted faces to about a fifth of the big-face area | 23% (15-29) | 21% (17-35) | more: 32% (24-41) |
| Prefer 45 degrees for a tilted big face | a third of single-axis tilted area (33%; 42% counting 39-46 degrees), three times the next, 22.5 degrees (10%); then 17.5, 27.5 and 5 degrees at 5-6% each | 36% at 45 degrees | less at 45 degrees: 29% |
| Tilt round one axis only | compound tilts 8% (5-13) of tilted area | 3% (0-13) | |
| Make steps between layers walls with their chamfers, not ramps | a real 35-60 degree ramp on about 1 in 6 steps (14%, 10-19); of steps 10 mm or more, 60-69% steeper than 60 degrees (74-80% at 30 mm or more), 16-19% at 35-60 | ramps about 1 in 5 (20%, 16-28); 64-72% steeper than 60 degrees | ramps about 1 in 5 (19%, 7-25) |
| Cut an outer silhouette corner (some blocks) with one flat 45-degree face | in 9 of 27 models (about 16 of 28 counting 20- and 40-degree cuts); legs 261 mm (222-396), often 230-290, 0.10 (0.09-0.16) of the cell | in 4 of 12; legs 68 mm (50-84), 0.14 of the cell | in 7 of 12 large models; legs 236 mm (236-244) |
| Run the corner cut as far along the edge as the design needs | 0.42 cell (0.15-0.88): a sixth of the cell to most of it | | 0.63 cell |

### Mount faces

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Keep part of a fully mounted face flush with the cell boundary (rims, frames, plates); set the rest in | 56% (49-62), about half | 32% (23-43), about a third | large grid about the same (53%, 52-65); small grid much less (19%, 11-26) |
| Keep this share of the mount area flush | 0.58 (0.51-0.81), about 0.6 | 0.33 (0.29-0.48), about a third | 0.52 on large grid |
| On a partly mounted face, keep almost nothing flush outside the mount area | 56% (45-72) flush inside it, 2% (1-7) outside | 26% inside, 1% outside | |
| Set the main face plane on the boundary | 0 mm (0-18) back | | |
| Keep faces with no mount points off the boundary: the body sits back | 0% (0-1) flush | 0% | large grid not empty: 7% (1-23) flush |

### Joining parts

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Sink each part into the part it sits on by a quarter to a third of its thickness | 0.30 (0.20-0.42) | 0.25 (0.18-0.31) | same: 0.26 (0.14-0.30) large grid, 0.28 small |
| Sink a part this deep, by its size | 11 mm (4-29) for 30-150 mm parts, 17 (11-38) for 150-500 mm, 43 (29-73) over 500 mm | 7.5 mm (3.5-9.4) for 30-100 mm parts, 14 (8-21) over 100 mm | |
| Sink most parts; leave almost nothing floating | 71% (56-82) sunk over 0.5 mm, 91% (89-96) intersect a bigger neighbour; 14% (6-30) of sunk parts go deeper than their own thickness | 68% (47-73) sunk | 80% sunk on large grid |
| Keep a deliberate gap rare and thin | 2% of parts, 1.3 mm (1.0-3.1) wide | | |
| Overlap subparts with their parent | 22 of 27 subpart pairs | | |

### Examples

- **Turret Control Block**: the inset wall panel sits 30 mm below a 144 mm flat frame and climbs to it over a 50 mm
  S-shaped ramp.
- **Welder (N_L_WelderReskin)**: the fully mounted back is about 56% flush (the rims and the X frame). On the side
  and top the mount area covers only the box half of the 5 m face; about 45% of it is flush and under 5% outside it,
  and the hatches and panels sit in. The arm side has no mount points, and nothing on it comes within 15 mm of the
  boundary.
- **Flare Launcher**: the silhouette corner is one flat 45-degree face with 293 mm legs (307 mm to the virtual
  corner), a little over a tenth of the cell.

## Surface layout

### Areas, depths and bays

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Split each side into several flat areas, not one slab: frames and L-shapes round recesses | main areas (at least 0.2 cell wide) 1.0 x 1.7 m (0.4 x 0.7 cell; 0.82-1.25 x 1.44-2.0 m), filling only 56% (40-68) of their bounding rectangle | 187 x 381 mm (0.37 x 0.76 cell), filling 77% (60-84) | squarer: 1.08 x 1.34 m (0.43 x 0.54 cell) on large grid |
| Make rectangular inset plates longer than wide | 355 x 845 mm, 1.7 (1.4-2.2) times as long as wide; about 1 in 5 is a 3:1 strip | about 85-100 x 180-220 mm, 1.8 (1.7-2.0) | 1.4-1.6; about a quarter are 3:1 strips |
| Keep part of each side as outer surface, its top level (on the cell boundary only where the side has mount points: "Mount faces" in "Layers and silhouette") | 36% (22-49) of the side; 29% (21-45) within 4 mm of the boundary | 22% (16-25); 17% flush | |
| Sink one or two recess depths below the outer surface | 83 mm (50-95) and 122 mm (105-256) down | 14 mm (11-17) and 33 mm (23-47), sometimes a third at 51 mm | large grid: about 25 mm (20-29) and 100 mm (64-120) |
| Cut most recesses straight into the outer surface as closed pockets; the rest run out to the side edge through a groove or notch | 62% (37-81) closed (68% by area) | 51% (50-60) closed | 50% (39-78) closed on large grid, 49% on small |
| Put recesses of different depths side by side, rarely one inside another | 10% (0-27) nested, on 20% (0-50) of sides | 24% (0-53) nested, on 40% (0-100) of sides | 11% nested on large grid, none on small |
| Sink a few big recessed bays into each big face, almost never through-holes | 90% recessed; long side 1.08 m (0.43 cell, about half the face length), 58 mm (40-100) deep; the few through-holes are mostly on the industrial hydrogen tank and the beacon | long side 315 mm (0.63 cell, about 80% of the face), 45 mm (38-67) deep | large grid: 35 mm (23-54) deep |
| Keep each bay in from the face edge | 85 mm (60-116; single bays 43-145) | 23 mm (9-28; single bays 14-34) | large grid: 61 mm (59-141) |
| Leave a rib between neighbouring bays | 130 mm (82-199) | 52 mm (38-77) | cargo-style blocks (cargo containers, conveyor junction, assembler, reactor, gatling turret: 6 of 11 large models) share one frame with 19 mm ribs between recessed panels; the others leave 100-270 mm |

### Decal detail on a face

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Leave some big faces with no decal detail (seam lines may still cross them) | about a third (33%, 23-54) | half (50%, 39-75) | almost all (100% large, 98% small); classic blocks carry about a tenth as many decals for their area (about 3 vs 32 per square cell on large grid), most of them on small faces |
| Keep a dressed face mostly plain metal | 90% (84-92) plain; decals 5.4% (4.4-8.1) | 77% (62-86) plain; decals 10% (7-21) | |
| Dress a face with about 5 detail groups per square metre | 5 (3-5) groups per dressed face, 65 mm (47-87) across | 2-3 (1.8-3.5), about 32 mm across | rare (6 large models): bolt rows, about 12 groups per face, most on the slide door |
| Keep the groups near the face edge | nearest point 43 mm (30-81) in, centre about 78 mm; 73% reach within 100 mm of the edge, where 51% of the face lies | nearest point 11 mm (8-20) in; 71% within 20 mm of the edge, where 34% of the face lies | 70 mm (38-147) in |
| Favour the corners over the centre | corners hold 42% of groups on 30% of the area, the centre 12% on 18% | corners 54% on 25% of the area, the centre 7% on 20% | |
| Put decals more densely in recesses than on the flush surface | 1.7 (1.0-2.6) times as dense | 1.5 (1.3-6.1) times | |
| Mirror detail groups across the face's centre line, usually left to right | 59% (43-70) of groups have a twin (a centred group matching itself not counted): vents 74%, rivet bands 85%, bolts 87%, buttons 100%, signs 40%, text never (0 of 19 text groups); 63% of dressed faces have a mirror-symmetric outline; the mirror line is vertical on 71% of upright faces | 54% (44-69): vents 77%, rivet bands 71%, buttons only 6 of 27; 80% of dressed faces have a symmetric outline | bolt rows almost always mirrored (312 of 320 groups, mostly on the slide door) |

- **Corners and recess edges first**: put detail in the corners and along the edges of each recess, and leave the
  centres of recesses and faces plain.
- **Once only**: text, most warning signs and, on small grid, keypads and switches. A single keypad or sign may sit on
  an otherwise fully mirrored face.

### Matching the sides

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Dress mount faces like any other side (how much sits flush: "Mount faces" in "Layers and silhouette") | detail decals on 3.1% (2.0-4.4) of full-mount sides vs 2.7% (2.5-3.5) of part-mount sides | 3.9% (2.6-10.8) vs 6.1% (4.8-7.0), too few blocks to compare | mount sides carry almost no detail decals (0.8% large, 0.4% small), and that little sits on the flush surface (recesses 0.05-0.13 of its density) |
| Give the front and back about the same detail as the left and right sides (no show face); decal cover relative to them | front about 0.9 (0.51-1.28), back about 0.8 (0.51-1.18) | front 1.0 (0.86-1.27), back 1.8 (1.1-4.7) | every side about 1.0 |
| Give the top and bottom somewhat less (blocks vary widely) | top about 0.6 (0.39-1.19), bottom about 0.65 (0.36-1.38); 7 of 11 tops and 9 of 13 bottoms carry less than the sides | top about 1.0 (0.62-1.65), bottom about 0.6 (0.50-0.94) | every side about 1.0 |
| Make the left and right sides mirror copies | layouts agree on 93-95% (84-100) of the area; 10 of 12 blocks above 80% | 100% (98-100) | 96-100%, like every opposite pair; each side also mirrors 91-100% on itself |
| Repeat the front on the back on about half of blocks | 99% (41-100); 5 of 9 blocks at 99% or more | 100% | 96-100% |
| Give the top and bottom their own layouts on large grid; match them on small | agree on only 52-53% (17-81): 3 of 10 blocks above 80%, 3 below 10% | 98% (76-100) | 96-100% |
| Compose a side of two or more cells as one design, often round a central port, not a one-cell layout repeated | shifted by one cell, a side matches itself on only 23-26% (17-37), no better than at a half-cell shift (27-31%); level changes are 1.4 (1.0-1.8) times as dense within 30 mm of inner cell lines, above 1 on 3 of 4 blocks | one-cell shift 35% (30-41) vs half-cell 44-48%; level changes 1.4 (1.1-1.6) times as dense along cell lines | same: 18% vs 23% on large grid, 14% vs 23% on small |

### Examples (newer large grid)

- **Turret control block (N_L_TurretControlBlock), front, one cell**: one recessed panel 2.13 m wide and 30 mm
  deep, 100 mm in from the flat top edge and 145 mm from the sides, with a 130 mm rib below; a seam ring about 40 mm
  in from the edge.
- **Battery (N_L_BatteryReskin), side**: all 22 decal groups mirrored left to right, among them clamp bars at the top
  corners of the central bay and rivet rows near the bottom corners, their centre line about 80 mm above the bottom
  edge. The keypad (a raised box) and the warning sign (inside the recessed bay) appear once.
- **Industrial assembler (N_L_AssemblerIndustrial), front, lower cell**: the keypad (150 x 254 mm, 17 mm in) sits
  level with the port centre, 0.79 m to the side and just outside the yellow frame: at cell mid-height (1.25 m),
  0.46 m in from the face edge.
- **Bulky hydrogen tank (N_L_BulkyHydrogenTank), front, 3 x 3 cells**: one design over the whole side round the only
  conveyor port, at the centre. Round fittings (not ports) fill the corner cells and closed bays the edge cells (an
  80 mm deep frame round a 92 mm deep floor), all cut straight into an outer surface covering half the side. The
  keypad sits 0.83 m beside the port, level with its centre (3.75 m up, 22 mm in).
- **Heat vent (N_L_HeatVent), front, a full mount side**: the outer surface (corner, edge and centre plates, 52% of
  the side) is nearly plain, with two white arrows and a seam ring. A 66 mm deep ring round the centre plate opens to
  the left and right side edges, so it is not a closed pocket; a 250-320 mm deep niche is cut into the centre plate,
  beside the ring. The recesses carry 13% decal cover against 2% on the flush surface: a hatch-panel decal in the
  small upper-left pocket, vent slots in the ring, and button panels and a warning sign in the niche.

## Standard parts

Keen's newer blocks reuse a small kit of parts. The fixed modules are modelled and sit on their dummies: the conveyor
port, the Terminal panel and the screens (the same on both grids: "Grid scale"). Everything else is surface detail,
mostly Atlas3 decals with Atlas4 bands, Decals seams and bolts and some Atlas1, on flush, raised or recessed host
plates: vents, grilles and hatch panels in sets of about four; small dishes, dimples, rings, slots and bolt tabs by
the dozen. On small grid most modelled detail disappears. Classic blocks share the port, its bars and the 244 x 140
terminal to the mm, but use no Atlas3 or ButtonsAtlas decals: their vents and plates are geometry or the Doodads
texture. Model counts in brackets are out of 28 newer large or 12 newer small models.

### Modules on dummies

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Use the stock conveyor port unchanged, centred on the conveyor dummy: a PaintedMetal_Yellow frame with 45-degree corner chamfers | 1.36 m square (0.54 cell), 287 mm deep; face about 92 mm wide (80 flat plus small edge bevels) | 340 mm (0.68 cell), 72 mm deep; face about 24 mm (15 flat); the small reactor has a 314 mm variant, 66 mm deep | same to the mm (1358-1360 mm, 287 mm deep) |
| Recess a Conveyor shutter (slats with small hinge knuckles) in the frame | 1172 mm square, about 100-110 mm below the lip (104-115 over 17 blocks; a small 340 mm port on a large block: about 35 mm) | 288-290 mm, about 45-55 mm below the lip | same, about 100-115 mm below the lip |
| Keep the lip flush with the hull | within 15 mm in 14 of 19 models; the bulk cargo container, assembler, safe zone and survival kit ports stand 30-95 mm proud | flush or up to 37 mm proud, never below | flush |
| Ring the frame with a 45-degree chamfered moat | 119 mm deep on the stock version (advanced refinery, railgun, turrets), 10-240 mm elsewhere | 47 mm on the stock version | same 119 mm |
| On about half the blocks, set the port in a dark surround (the rest leave it in the Colorable hull) | Darker or VeryDark, 1.6-2.1 m across | | |
| Fit about two ports per block | 2 (2-3) | | more: 4-6 (median 4), on 7 of 15 large models |
| Give every port two yellow bars, 110 mm apart centre to centre | 45 mm wide x 57 mm tall, 1.0 m long plus 60 mm Metal_Dull end blocks (1.12 m overall), 13 mm proud of the lip | small port: 30 x 32 mm, 200 mm long, 11 mm proud; large ports keep the large bars | same to the mm |
| Seat the bars on Metal_Dull posts and foot plates, and line the frame's inner edge with Metal_Dull strips | posts 30 x 30 x 55 mm, foot plates 77 x 39 x 14, strips 482 x 52 (thinner on some newer variants) | | same to the mm |
| On blocks that take upgrade modules (assemblers, refineries), mark each mount with a half-size port frame, no bars, centred on detector_upgrade and standing proud of the face | 680 mm outer (0.27 cell), about 144 mm deep, a 584 mm Conveyor face 36 mm below the lip; about 85 mm proud on the advanced refinery; 8 each on the industrial assembler and advanced refinery | none (no upgrade dummies) | same, 8 each on the assembler and refinery (about 86 mm proud on the refinery); the ion thrusters' detector_upgrade has no frame |
| Put a Terminal panel (the block's keypad) on detector_terminal in one of two stock sizes, not scaled with the grid | 244 x 140 mm on a 24 mm box (the classic part, reused on the advanced refinery, drill, safe zone and welder) or 254 x 150 on a 28 mm box (battery, hydrogen engine, reactor, small cargo container); other blocks scale it to 158-283 mm long | the 254 x 150 face, only on the small cargo container | 244 x 140 on a 24 mm box |
| Back it with a dark plate | PaintedMetal_Darker on 22 of 37 panels (Colorable on the reactor, jump drive and gatling), about 350 x 220 (250-470 x 160-280) | VeryDark | a 320 x 216 PaintedMetal_Darker bezel |
| Place the keypad right beside a port, level with the port centre, just outside the yellow frame | edge 15-180 mm from the frame (about 70; industrial assembler 36), 0.8-0.95 m to one side of the port centre; face within 3-70 mm of the dummy; on a one-cell side 1.25 m up and 0.3-0.5 m from the edge; on a side with no port about 1.55-1.6 m up | about 130 mm from the port frame, 0.23 m above the port centre, in a 103 mm deep alcove (small cargo container) | at cell mid-height (1.25 m), 0.82-0.90 m beside the port |
| Sink it into the face, flat to it | 5-40 mm in, or a raised housing up to about 35 mm proud; most flat, a few tilted 10-14 degrees, 45 degrees on chamfers | | about 2 mm in (the refinery's stand 27 mm proud), turned 15 degrees off the face on 20 of 32 panels (assembler, both cargo containers, reactor) |
| Use about two per block, on one to three sides (usually two) | 2 (1-4); on half the blocks one also sits on the top or bottom | 2 | 4 (2-6), on 4-6 sides, top and bottom included |
| Use CockpitScreen_01-04 faces in a PaintedMetal_Darker or VeryDark bezel, sized to the block | survival kit 670 x 417, flat (the unit sits 78 mm back in a recess); medical room 400 x 213, tilted 10 degrees; turret control a 979 x 604 main and a 222 x 345 side screen, both tilted 18 degrees, plus two 174 x 290 on 45-degree chamfers; 1-4 per block | the same size (the small survival kit keeps 670 x 417) | no built-in screens |

- **A large port on a small block** keeps the 1.36 m frame (1.34 m on the small survival kit), the shutter and the
  large bars, but can be much shallower (small cargo container below). The classic small medium cargo container
  (S_CargoContainerMedium) mixes 2 large and 2 small ports.
- **Conveyor-only vs inventory ports** [SOFT, owner]: blocks with player inventory access (cargo containers,
  assemblers, reactors, welders) use the full port style with the two yellow crossbars, Metal_Dull latch strips,
  and a nearby terminal keypad. If a block is conveyored only for structural routing / passthrough and does not
  intend to have inventory or terminal access (similar to the vanilla Structural Platform Conveyor blocks or
  conveyor tubes), it does not need the crossbars, latch strips, or full cargo hatch dressing — a clean port
  frame and recessed Conveyor shutter without bars is standard.

### Surface detail

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Dress control areas with a few ButtonsAtlas panels | on 17 of 28 models, about 4 panels per block (1-11), each type 1-2 per block: #1 toggles 190 x 95, #2 seven keys 237 x 98, #3 six keys 149 x 98, #21 keypad 216 x 98, #34 knobs 177 x 175 | about 0.6x: #1 117 x 58, #2 140 x 70 | none (no ButtonsAtlas) |
| Add single buttons and LEDs at their real size | LEDs #17/#18 28-33 mm, big buttons #19/#20 40 mm, rockers #32/#33 50 x 30, jacks #46-48 34 mm, knob #50 40 x 34, slot #56 37 x 23, E-stop #58 69-82 mm, socket #65 69 mm | about the large size (E-stop 69 mm, rockers 52 x 30, LED #18 40 x 19); jacks and sockets 14-36 mm | none |
| Host the controls on Darker, Colorable or VeryDark, mostly on the flat host face | Darker about half, Colorable 40%, VeryDark 15%; a few in a recess or on a raised box | | none |
| Light with flat Emissive strips, flush or 2-5 mm proud of a Darker or VeryDark backing | about 0.5 m (175-650) x 60-70 mm (22-107); the industrial assembler flanks its port with two 982 x 113-133 strips; also light panels about 368 x 152 and round lamps | no strips | strips only on the merge block (8 strips, 652 x 104); other emissives are modelled lamps |
| Group status lamps (Emissive0-3) in rows of four | 126 x 99 each at 210 mm pitch (battery, jump drive); the jump drive also has rows of 95 x 74 at 157 mm, the bulky hydrogen tank 113 x 100 at 150, the industrial hydrogen tank 88 x 41 at 148; the medical room uses Emissive2 bars instead | one row of 112 x 96 at 260 mm pitch (battery bank) | the large battery has the same 126 x 99 rows at 210 mm; the small battery 78 x 61 at 130 mm |
| Show vents with Atlas3 #24 slatted vents, usually the whole piece, in sets of about four on a flat host, about 17 mm in from its edge | 278 x 125 mm (164-386 x 80-181), 4 per block (3-20); a quarter crop it to about half; Atlas3_Darker 54%, Atlas3_Colorable 40% | 171 x 80, 2 per block (3 models), usually cropped to about a fifth (one slat group) | no Atlas3: vents are geometry or the Doodads texture; the Decals #30 vent grille on 2 models (and 3 newer ones) |
| Vary vents with the other vent pieces | Atlas3 #39 vent pill 194 x 87 (8 models), Atlas1 #5 six-slot comb 283 x 81 (13 models) | Atlas1 #5 on 1 model | none |
| Fill a face or recess edge to edge (0-2 mm gap) with the Atlas3 #22 mesh grille | 328 x 263 mm (228-574 x 128-363), 4-5 per block, usually whole (a quarter a small crop); the host about as often flush or raised as recessed (recesses about 20-60 mm) | 138 x 50 (3 models) | none |
| Show perforation as rows of single Atlas3 #37 holes | one hole (one cell of the 5 x 5 grid), about 28-30 mm, about 60 per block | 14 mm, about 46 per block (7 models) | none |
| Use the other hole pieces where they fit | Atlas1 #9 hole field 130 x 63 (16 models, 10 per block); Atlas3 #2 speaker grille 78 mm across (13 models, 2 per block); Atlas4 #5 perforated band (6 models) | Atlas1 #9 77 x 30 (4 models) | none |
| Suggest access hatches with Atlas3 panel decals, about four per block, each on its own raised, recessed or flush plate | #31 hinge-notch panel 245 x 155 (17 models, 4 per block), #32 centre slot 233 x 124 (15), #33 two inset blocks 217 x 161 (14), #34 bands and screws 180 x 118, often cropped to about 70% (13), #30 square plate 304 x 272 (10), #25 tall inset 170 x 47 (14 models, 8 per block), #41 small window 162 x 82 (16); Atlas1 #3 louvre plate 423 x 200 (6) | about half size, 1-4 per block: #31 115 x 80, #32 157 x 101, #30 187 x 83, #41 85 x 38, #25 82 x 21 | no Atlas3: hatch plates are geometry or the Doodads texture |
| Imply fins and cooling with fluting decals | Atlas3 #23 fluted bar 334 x 65 (17 models, 13 per block); Atlas4 #6 raised-block band, tileable, 35-55 mm wide, as long as the face (80-760 mm), 9 models | #23 only as tiny 13-70 mm flutes | no Atlas3: fins and brackets are plain geometry or the Doodads texture |
| Imply clamps and brackets with Atlas3 clamp pieces | #7 clamp block 157 x 79 (9 models), #18 clamp bar 118 x 88 (13), #16 tab with hex bolt (21 models, 12 per block; size and placement in "Bolts and rivets") | #16 (5 models, 8 per block), #18 74 x 38 (3), #7 102 x 47 (1) | none |
| Break up big plates with small round Atlas3 pieces, by the dozen (size, then per block / models) | #28 dish 60 mm (38 / 25), #14 dimple 42 mm (44 / 21), #10 ring on a raised boss 77 (41-159) mm (10 / 24), #17 cross cap 25 mm (23 / 14) | about half size ("Grid scale"): #28 38 mm, #14 18, #10 45; each 3-36 per block, on 4-9 of 12 models | none: Decals #3 and #6 bolt heads ("Bolts and rivets") and #22 small square plates instead, with #58 and #61 bevelled seams |
| Break up big plates with small Atlas3 slots and pills too | #26 pill 87 x 38 (28 / 21), #3 slot with knob 128 x 54 (21 / 20), #20 dark slot 140 x 28 (12 / 21), #15 slot pill 78 x 37 (31 / 15), #19 slot with edge 62 x 53 (20 / 20), #36 trapezoid bar 329 (199-498) x 41 (10 / 20) | #26 54 x 22, #3 78 x 27, #15 37 x 18, #36 166 x 21; #20 167 x 20, larger than on large grid | none |
| Keep each kit piece clear of its face edge | 10-20 mm | about 5 mm | |
| Fill a narrow face or slot edge to edge (1-2 mm gap) with the Atlas1 #2 lattice truss; the slot depth varies | 471 x 100 (19 models, 8 per block) | 565 x 73 (3 models) | none |

- **Place controls where the layout needs them**: they sit 0.3-3.9 m from the terminal dummy, and the survival kit
  and medical room have no terminal at all.
- **Where the Atlas3 reliefs go** on large grid: the #10 ring disc, #14 dimple, #16 hex-bolt tab and #3 slot with
  knob in corners; the #20 tall slot, #36 trapezoid bar and the Atlas1 #2 truss (mostly on Darker) along edges; the
  #24 slatted vent and #22 grille on Darker or paint about equally.
- **Hinges** show only as the Atlas3 #31 notch and the port shutter's knuckles. The one modelled clevis lug (hydrogen
  engine) is about 41 mm thick and 190 mm long.

### Modelled extras

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Where pipes are used, run straight round pipes about 0.1-0.15 m across, 3-5 per block | 110-135 mm (about 70-200), about 4 per block (11 models); Colorable about 100 mm (industrial hydrogen tank), Rubber hoses 190-200 (bulky hydrogen tank), Chrome 25-112; decal stand-in: Decals #23 pipe elbow 192 x 93 (6 models) | almost none (the round parts on the autocannon, flare launcher and railgun are barrels and launch tubes) | few and low-poly (8-10 sides): the refinery has about 18 pipes of about 100 mm, the ion thruster six 109 mm Chrome rods |
| Size tanks and drums at about 0.2 cell across and repeat them in identical pairs or rows | about 0.5 m (0.4-0.9 m), 420-540 mm common (10 models); identical pairs at 0.42-0.54 m (welder 417, railgun 454, reactor 458, hydrogen thruster 500 and 539); whole-block tank bodies about 2-3.1 m (bulky hydrogen tank 3.1 m) | 128-140 mm (about 0.27 cell); barrels and tubes in sets of 3-4 (rocket launcher 4 x 133 mm) | few: the refinery has three identical columns about 1.0 m across, the large reactor a round core about 3.8 m |
| Model fins only where heat is the point, at a pitch 1.2-3 times the fin thickness (thickness / pitch) | industrial assembler 9 fins 44 / 130 mm, 222 deep and 333 long; centred door 10 / 30; industrial hydrogen tank 22 / 26; rocket turret 22 / 48 | none | plain geometry |
| On blocks a crew member walks up to (survival kit, safe zone, turrets), add a bent round-tube grab handle in Chrome or Metal_Dull (span x standoff) | 20-26 mm tube (49 with a grip sleeve), span about 275 mm (205-323), standoff 73-132 mm: survival kit 205 x 107 in 20 mm Chrome, gatling and rocket turrets 275 x 73 in 26 mm Metal_Dull, safe zone 323 x 132 with the 49 mm sleeve; similar Chrome bends on the jump drive (331 x 93) and advanced refinery (368 x 65) | the same size: small survival kit 212 x 111 in 21 mm tube; a similar Chrome bend (218 x 115) on the small railgun | none |

- **Pipe fittings are rare**: collars about 1.34 times the pipe diameter and 0.6 diameters long on only 2 models; the
  industrial hydrogen tank holds its pipe with a T-bracket and ring clamp.
- **Count the 1.5 m ring behind each classic port as part of the port**: it is the conveyor tube behind it, one per
  port on the classic cargo, assembler, junction, gatling and reactor blocks, not a drum.

### Examples

- **Survival kit (N_L_SurvivalKitReskin)**: the stock port sits in a VeryDark surround about 1.73 m across, flush
  with its lip. The console holds a 670 x 417 screen in a dark bezel, set 78 mm back in a recess; below it
  ButtonsAtlas #2 keys (140 x 70) and #1 toggles (117 x 58) on light Colorable inserts in a dark console, jacks and
  sockets on the Darker parts, and a bent 20 mm Chrome handle (205 x 107) beside it. It has no terminal.
- **Industrial assembler (N_L_AssemblerIndustrial)**: a port with bars, flanked by two 982 x 113-133 Emissive
  strips; the terminal 36 mm from the port frame; 8 half-size 0.68 m upgrade frames without bars; and a bank of 9
  modelled fins, 44 mm thick, 222 deep and 333 long, at 130 mm pitch.
- **Small cargo container (N_S_CargoContainerReskinSmall)**: four large ports keep the 1.36 m frame and bars but are
  only about 107 mm deep, held with Metal_Dull clips; the small port is 340 mm (72 mm deep) with 200 mm bars; two
  full-size 254 x 150 terminals sit about 130 mm from the port frame on a VeryDark plate.

## Panel lines

Pieces, UV mapping and seam-end geometry: `atlas-regions.md`, "Panel lines". Atlas4 #3 is a groove with a dark centre
line; Decals #58 is a seam with a one-sided bevel, #61 a thin strip plus that seam.

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Draw lines with Atlas4 #3 (classic: Decals #58 or #61) | 22 of 28 models; Decals #58 in 9 | 9 of 12 models | 7 of 15 large and 3 of 5 small models |
| Match the line's variant to the paint under it | 89% of pieces (83-99%) | 92% (79-95%) | same |
| Make a full line this wide | 13-23 mm (16), 0.65% of the cell | 7-12 mm (10), 2% of the cell | 29-51 mm (37) on large grid |
| Lay part of the length as a half strip (V 0.5-0.5166: the centre line to one edge) | about 7% of line length (0-29%); heavy only on the welder, drill, survival kit and beacon | about 40% (27-52%) | |
| Inset a line that follows an edge (edge to centre line) | 2.75 widths (2.5-3.4), 44 mm (32-63), most at 2.5-3 widths, from a bevel fold or the foot of a raised part; a little closer to a square step | 3.6 widths, 27 mm (23-46) | about 2.2 widths, 113 mm on large grid |
| Run about 2 in 5 straight lines along an edge | 41% of straight runs (25-62%); 4 in 5 of the edges followed are bevel folds | | |
| Line only part of the big painted area; leave most big faces without a line | 29% of the area (15-44%) but only 16% of the faces (8-29%); on faces at least 0.8 cell across, 43% of the area (13-62%) | 32% of the area (11-41%), 10% of the faces (2-18%) | almost none: 0% of the area (0-5%) |
| Give a lined face this much line per square metre | about 2-3 m: 1.9 (1.6-3.5), or 3.1 (1.8-4.3) by a second count | 5.5 m (3.9-9.1) | |
| Run lines along the block axes in the face plane | 84% of line length (76-90%); 5% at 45 degrees (2-8%); long runs (4 widths and up) at other angles 3% (2-16%) | 86% (66-100%); 1% at 45 degrees (0-4%) | same |
| Draw long unbroken strokes, never dashes | free-standing lines 1.18 m (0.84-1.52), about 57 widths; 0% under 10 widths (0-7%) | 0.68 m (0.27-0.87), about 71 widths | same |
| End lines on an edge or another line | 71% of ends (60-80%): 38% at an edge (24-62%), stopping within about 4 mm of it (1-5); 20% as T-stems (3-38%) | 90% (75-100%) | same |
| Carry lines straight over bevels and rounded edges, crossing each fold square, instead of stopping at the edge | 51% of lines cross a fold (31-68%), 93% of crossings within 7.5 degrees of square; 95% of the folds are 15-45 degree bevel facets | 60% (44-70%) | rare: 10% of lines (0-80%) |
| Facet 90-degree corners in 11.25- or 22.5-degree steps | 80% of corners (55-100%); sharp mitres 0% (0-15%); about half of all kinks are 11.25 or 22.5 degrees | every corner | faceted |
| Start the corner turn this far before the virtual corner | 36-83 mm (55), 3 widths (2.1-5); models range 12-132 mm | 13-37 mm (22), 4.2 widths | 66-137 mm (101), 2.1 widths on large grid |
| Ring a lined cylinder near its end, square to the axis | in 14 of 27 lined models; inset 2.4 widths (1.8-4.1), 44 mm (28-53), almost always from a bevel fold; one straight segment per facet, 22 per ring (18-32); 92% square to the axis, the rest wrap domes or tapers | in 4 of 10 models, about 38 segments | same |
| Double a line only as an accent: a steady 2-5 widths apart (4-5 most common), turning corners together | in 9 of 27 models; 4.5 widths (2.9-5.0), 81 mm (50-120), from 2.2 widths (medical room) to 6.9 (beacon); 0% of line length (0-6%), 2-40% in the models that use doubles | rare (1 model) | same |
| Model a panel break as a V groove only between separate plates | 11% of breaks (2-22%); 96% of 45-degree V grooves deeper than 6 mm sit between separate parts (80-100%); shallow one-part dips about 3 mm deep in about a quarter of models (80% between parts counting those, 14-95%) | 16% of breaks (6-27%); 98% between separate parts (93-100%) | cut into one part (0% between parts, 0-36%; sizes in "Layers and silhouette") |

- **Variant follows the paint.** Atlas4_Colorable on PaintedMetal_Colorable, _Darker on Darker; _VeryDark or _Darker
  on VeryDark (each leads in half the models), never _Colorable (only the medical room has a Colorable minority,
  36%); _Chrome on Chrome (5 of 5 models); _Chrome or _Darker on Metal_Dull (the bulk cargo container uses Darker);
  _VeryDark on MetalMilitary (centred door) and on rubber and plastic (3 of 4 models; the beacon uses Yellow). Each
  line takes the paint of the part it marks. Small grid the same (VeryDark on VeryDark paint on the survival kit and
  battery bank, Chrome on bare metal on the rocket launcher); classic the same.
- **Axis-parallel.** On a bevel, "along an axis" means along the fold or square across it. Keep 45 degrees for
  short links; use other angles mainly where the line follows an edge at that angle (about 3 in 4 long off-axis runs
  sit within 6 widths of a parallel edge, 25-92%).
- **Open ends** have no set gap: the next edge or line straight ahead is about 13 widths away (6-22, about 245 mm),
  and only a quarter stop within 6 widths of one.
- **Corner sequences**: 11.25 / 22.5 / 22.5 / 22.5 / 11.25, four 22.5-degree steps, or eight 11.25-degree steps
  with half steps at the ends. A plain 45-degree chamfer is a less common alternative (in 11 of 23 models).
- **T-joins**: end the stem on the cross line's centre line, at 90 degrees (Keen: 96% of stems), pointed
  (`atlas-regions.md`, "Joins and ends").
- **Keen's ends (fact only)**: T-stems are pointed in 13 of 22 newer large models (89% of stems in the median
  model, 13-100%) and square in six (jump drive 108 of 108, centred door 79 of 110, beacon, reactor, industrial
  assembler, safe zone); on small grid about a third are pointed (0-92%). Free ends are square: 73% (56-91%) on
  large grid with about 10% skew cuts, 91% on small grid, and on classic blocks. The skill's pointed ends stand.
- **Spacing**: parallel lines have no set spacing; it follows the panel size (doubles excepted).
- **Round a recess**: about 1 line in 10 on a big face rings a recess, 10-40 mm out from its edge.
- **On a seam**: a line centred on a seam or on the foot of a raised part is rare; most lines sit about 3 widths in.
- **Groove or line**: split a single plate with a decal line, and never lay a decal line along a modelled groove
  (V groove sizes in "Layers and silhouette"). A line that meets a groove may run over its chamfer into the gap.
- **Classic lines** go on PanelingColorable on paint, PanelingDarker on dark metal. Keen also puts them on plain
  Decals, which paints a grey band (`atlas-regions.md`, "Panel lines").

### Examples

- **Heavy calibre turret (N_L_HeavyCalibreTurretBody), top deck**: a 17 mm line runs 54 mm (3 widths) in from the
  fold where the deck's 22.5-degree bevel starts. Its corner is a 107 mm 45-degree diagonal with a 28 mm facet at
  each end, so every kink is 22.5 degrees; the turn starts about 6.5 widths before the corner, more than usual. A
  stem ends in a point on the outline's centre line.
- **The same turret's front edge**: the line crosses three 22.5-degree bevel facets square to the fold and ends in a
  pointed T-join on each face. The outlines sit 50 and 35 mm (about 3 and 2 widths) in from the bevel.
- **Reactor (N_L_ReactorReskinLarge), underside**: two separate plates meet in a modelled V groove 23 mm wide that
  drops into a 14 mm deep gap; one plate, the one carrying the line, is chamfered about 25 degrees, the other 45.
  Within one plate the break is a 14 mm Atlas4 #3 line, which runs over the chamfer into the gap instead of stopping
  short.
- **Centred door (N_L_CentredDoor)**: a 25 mm VeryDark frame band runs between a Darker inner plate (1 mm below the
  frame) and a Colorable panel it stands 25 mm proud of. The frame's 10 mm Atlas4_VeryDark line is centred on the
  frame-to-plate seam; the panel's Atlas4_Colorable line is centred on the frame's foot, half tucked under it. On the
  face two 10 mm lines 50 mm (5 widths) apart turn a corner together in 11.25-degree steps (eight facets of about
  45 and 53 mm, half steps at each end); the outer line stops square where it meets a round part.

## Bolts and rivets

Keen fakes almost every bolt with decals; only pipe flanges get 3D nuts.

### Bolt heads

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Size Atlas3 #14 round sunken heads to the part | 43 mm (28-52): 40-50 mm on panels, 20-30 mm on small parts; most blocks use 2-4 sizes (about 44% of heads 38-60 mm, 36% 15-38 mm), blocks range 16-126 mm | 19 mm (11-23), 18-23 mm in 4 of 6 models; the small reactor (5 mm) and rocket launcher (9 mm) use it as a rivet, the small cargo container at 53 mm | no Atlas3: Decals #3 round head (a dome in a recessed ring), 35 mm (25-46) |
| Size Atlas3 #17 cross-head screws | about 25 mm: 27 (22-34) | about 14 mm | |
| Size Decals #6 round domed heads | about 25 mm: 26 (16-32), on newer blocks that reuse it | | 15 mm in 8 of 9 models (assembler 20 mm) |
| Set each bolt centre about one head in from the face edge | 1.1 heads (0.9-1.4), 30 mm (23-45) | 0.7 heads (0.5-0.9), 16 mm (4-21) | same |
| Bolt a panel with a pair mirrored about its centre line | about a third of bolted faces; about 300 mm apart (287-306), about 4 pairs in 5 mirrored | about 1 bolted face in 6 | about two thirds of bolted faces; 315 mm apart, 86% mirrored |
| Or bolt it with four at its corners | about 1 bolted face in 10 (12-15% on average), in 19 of 25 models; short side 220-270 mm | about 1 face in 7 (9-26%); short side about 150 mm | |
| Put a lone head only on a narrow face, centred across it | about a third of bolted faces; face about 100 mm (2-4 heads) wide: 104 (43-147) | almost half of bolted faces (44%) | |
| On a small boss (55-80 mm), centre one head about 3/4 of its width | 30-40 mm head | | |
| On a strip about 35 mm wide, put a pair, each about 1 head in from its end | 25 mm heads | | |
| Space a tight row (usually 4 on a narrow strip) about 2 heads centre to centre | about 55 mm; rows of 4 at 1.8-2.1 heads (48-57 mm) on the advanced refinery, jump drive and heavy calibre turret | 2-3.5 heads, 19-32 mm | |
| Space bolts round a panel frame about 6 heads apart | 6 heads (3.6-9.8), 150-220 mm (about 200) | 6.4 heads, about 55 mm | much sparser: 11.6 heads (9.6-14.9), about 430 mm |
| Space long edge rows on doors and strips far apart | 280-600 mm (centred door, conveyor sorter, turret controller, industrial assembler, jump drive) | | |
| Hex-bolt tab Atlas3 #16: long axis square to the nearest edge, 3-5 mm from it; whole tab on the face or its flat end at the edge, never the head end | 61 x 42 mm (53-109 x 37-68), 5 mm (3-22) from the edge; whole tab inside and flat end at the edge each in 6 of 16 models (head end at the edge only on the heavy calibre turret body, tab wider than its face in 3); about 5 in 6 square to the face edges | 23 x 17 mm (15-42 x 11-28), 3 mm from the edge; flat end at the edge in 4 of 5 models; all square | no tab |
| Ring a pipe flange with 3D hex nuts | 8 per flange (9 on the advanced refinery), 30-37 mm across, 10-13 mm tall, about 3 nut widths (2.7-3.4) apart, centres about 25 mm in from the rim | no visible 3D nut ring | |
| Ring a round part with decal heads (uncommon) | in 6-8 of 25 models; 6-32 heads, 8 the most common (4 models); 2.6 heads (1.0-4.9) apart | rings of 8 (rivet-size #14 on the small reactor, Atlas3 #10 on the small survival kit) | rings of 8-11, about 8 heads apart (small ion thruster, merge block) |

- **One head type per face**: change type from part to part instead. Keen almost never mixes types on a face (6 of
  about 1300 bolted faces on large grid, 1 of 322 on small, none on classic). A large block uses 2-4 types in all
  (3; busy ones up to 7-9), a small one 1-3 (2), a classic one 1-2 (2).
- **Paint variant**: Atlas3 bolt decals follow the host as in "Materials and decal sheets" (92% (71-96) per block
  on large grid, 100% (62-100) on small), Atlas3_Darker on VeryDark; one or two small-grid blocks put Atlas3_Darker
  heads on paint. Decals-sheet heads mostly stay plain `Decals` (fixed grey) on any face: in 10 of 14 newer large
  blocks, on small grid and in 13 of 14 classic ones. Tinted ones follow the host about 85% of the time:
  PanelingColorable on paint, PanelingDarker on Darker (the battery's hex nuts, the classic S_Battery).
- **Other round 3D parts are not bolts**: Keen's only 3D nut rings sit on the flanges of the advanced refinery,
  industrial assembler and industrial hydrogen thruster (sizes in "Examples"). Pins, latch sockets, knobs, connector
  pins and pivot caps sit near bolts but follow no bolt pattern: the advanced refinery's 21 mm parts on a 23-27 mm
  grid are a connector field.
- **Angles (fact only)**: Keen keeps about 9 in 10 #14 and #17 heads square to the face edges, and all its Decals
  #3 and #6 round heads (and, on newer blocks, its #11 hex nuts on washers). It turns Decals #4 hex nuts (about 1 in
  5 square, the rest spread over 0-45 degrees), the few Decals #5 slotted heads and many Atlas3 #10 ring discs;
  classic blocks turn #11 too. The skill's rule stands: every round head, cross-heads included, gets a random angle
  (`bpy-recipes.md`, "Bolt decals").

### Rivets and bands

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Cut a short rivet row from one row of the Atlas3 #46 grid: 2-8 rivets, usually 2-3 | about half the rows are 2, then 3 and 6 (about 1 in 6 each) and 8 (1 in 8); a block's typical row 3 (2-4) | rows of 2-3 | no #46 rivets |
| Set the rivet pitch, the head about 0.6 of it | 33 mm (24-44), head about 20 mm | 22 mm (21-24) | |
| Run the row parallel to the nearest edge, its centre line about 1.5 pitches in | parallel: 100% per block (83-100); centre line 68 mm (36-91) in, 1.5 pitches (1.1-2.9); the row's outer edge 43 mm (12-58) in | centre line 27 mm (25-30) in | |
| Make a longer row one 6- or 8-rivet piece, or lay two pieces end to end | end to end in about 1 piece in 12, in 4 models (drill, welder, landing gear, safe zone) | | |
| Use a single #46 cell as a loose rivet, mostly on Darker or VeryDark | cell 30 mm (23-41), head 19 mm; singles and pairs, nearest neighbour 89 mm (50-250), about 7 pitches, or gapped rows 2.4 pitches apart; about 3 in 4 on Darker or VeryDark; in 10 models, most on the drill and welder | none | |
| Rivet a plate with the whole 10 x 6 grid or a block cut from it | pitch 33 mm (19-38); plate 188 x 107 mm (123-301 x 54-170), the whole grid about 300 x 180 mm; the whole grid in 10 of 16 models and the main shape in 6; the bulky hydrogen tank alone carries 657 plates | pitch 12 mm (10-13); the whole grid in 2 of 3 models | |
| Over about 0.5 m, rivet a seam with one Decals #59 band (raised rivets), not separate heads | 30 mm wide (27-36), rivets 21 mm (19-23) apart (0.63 band widths), pieces 0.8 m (0.5-1.1); in 4 models | 68 mm wide on the autocannon | only the small ion thruster: 86 mm wide |
| Use the dimpled Decals #60 band wider | 71 mm (60-216) wide, dimples 50 mm (37-135) apart; in 3 models; the medium calibre turret uses it in 41 mm pieces | autocannon: 28 mm wide, 19 mm pitch, about 440 short pieces (about 9 mm) | |
| Band a bolted rail or ring with Atlas4 #2 (bolt holes 1.25 band widths apart, so choose the width from the hole spacing) | 59 mm (47-87) wide, holes 76 mm (57-130) apart, pieces 0.8 m (0.2-1.7); closed rings in 3 models | 18 mm wide, holes 23 mm apart | |

- **Keep each band's art unstretched** (UV mapping and relief: `atlas-regions.md`, "Riveted bands").

### Examples

- **Reactor (N_L_ReactorReskinLarge) control panel**: a corner four of 34 mm #14 heads, 474 x 447 mm apart on a
  571 x 543 mm panel, centres 47-50 mm (about 1.4 heads) from the panel's own edges. A window frame in front covers
  the panel's outer 22 mm, so the heads show about 25 mm (0.75 heads) inside the opening.
- **Advanced refinery (N_L_AdvancedRefinery) flanges**: 35 flanges of 9 3D hex nuts, all 12.6 mm tall: 30 at a
  180 mm radius with 37 mm nuts 123 mm apart, and 5 at 151 mm with 31 mm nuts 104 mm apart (3.4 nut widths), centres
  26 mm in from the rim.
- **Industrial assembler (N_L_AssemblerIndustrial) flanges**: 9 flanges of 8 nuts, 33 mm across and 10 mm tall, on a
  124 mm radius, 95 mm apart, with rings of 17 mm 3D parts round the same flanges.
- **Industrial hydrogen thruster (N_L_HydrogenThrusterIndustrialLarge)**: 3 rings of 8 nuts 27-38 mm across and
  16-23 mm tall, 72-102 mm apart; 18 of its 19 Atlas4 #2 pieces are closed rings.
- **Landing gear (N_L_LandingGearReskin) top plate**: two #46 rows at a 25 mm pitch with 16 mm heads. The lower row
  of 8 is two pieces (2 + 6) laid end to end; the row of 6 sits centred on it, 32 mm higher, its centre line 47 mm
  from the plate's top edge.
- **Battery (N_L_BatteryReskin) front**: one head type per face. The dark recessed panel carries only Decals #4 hex
  nuts in PanelingDarker (four of five turned 15-40 degrees, one square), the light plate only 44 mm #14 heads in
  Atlas3_Colorable, the dark block only 44 mm #14 heads in Atlas3_Darker. A 29 mm wide Darker strip has a 16 mm
  Decals #6 head near each end, 315 mm apart, the lower one about 50 mm from the strip's end.
- **Jump drive (N_L_JumpDriveReskin) side**: a Decals #59 band, 32 mm wide with 7 mm rivets every 20 mm, runs 2.5 m
  along the foot of a 100 mm Darker rail. The rail's 80 mm flat face carries one lone 43 mm #14 head in
  Atlas3_Darker, centred across it, about 110 mm from the face's end.

## Signs and markings

Newer blocks carry a few small signs at real size; classic blocks have almost none. Sizes are the full piece,
width x height.

### Warning signs

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Put signs on most large blocks and about a third of small ones | 21 of 28 models | 4 of 12 models | 1 of 20 (the assembler) |
| Size text warning plates at real size, the same on both grids | 100-145 mm wide (120, about 1/20 cell), 45-85 mm tall; about 110 wide on 1-2 cell blocks, 115-225 (about 150) on blocks of 2x2 cells and up (safe zone 226, bulky hydrogen tank 177, medical room 170) | 97-114 mm wide (109, about 1/5 cell) | |
| Size pictogram-only triangles | 55-80 mm (68) | about 40-60 mm | |
| Count signs per block (repeats round a ring count once) | 4-9 (5), 2-5 different pieces, on 2-4 faces; 2-4 on the busiest face (keep to about 3) | 2-6, 1-3 per face | |
| Inset each sign from the nearest panel edge, square to it, not centred on the panel | 10-40 mm (18), about 5 in 6 within 1 degree of square; a few blocks 80-115 mm (centred door, battery, flare launcher, advanced refinery) | 10-20 mm (15) | |
| Choose a panel whose short side is about 4 times the sign height | 2.6-4.9 times | | |
| Butt related signs and codes together (an option: 10-25% of signs) | 5-10 mm apart edge to edge (8) | 2-12 mm | |
| Keep side-face text upright to the block's Up axis | 91% of signs, 84% of codes; 1% of signs and 4% of codes upside down (hydrogen thruster nozzle ring, bulky hydrogen tank) | 2 of 3 models; the small flare launcher's turn sideways | same |
| Leave sign and code UVs unmirrored | 98% | | same |
| Turn top-face text to read from a block edge | any side | the nearest block edge (6 of 6 models) | |

### Own-hazard signs

Give each signed block one readable sign for its own hazard (19 of 21 signed large models, 2 of 4 small), then add
generic extras anywhere. The groups are loose: a fitting generic sign is enough.

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Power and powered utility blocks (battery, jump drive, refinery, turret control, medical room, survival kit, safe zone): an electrical sign | 7 of 7: HV triangle Decals #38 66 x 55 mm, DANGER HIGH VOLTAGE Decals #37 119 x 84, HIGH VOLTAGE Atlas2 #13 54 x 31, CAUTION BATTERY BOX #31 119 x 62; the battery and turret control only through the HV triangle | battery bank carries #13, #31 and the HV triangle; small sizes: #13 88 x 50, #31 117 x 61, HV triangle 48 x 41 | assembler: four HV triangles, 91 x 75 |
| Hydrogen blocks: WARNING HIGH PRESSURE #18 or the flame triangle #16 | 4 of 4: #18 121 x 72, #16 65 x 57 (the hydrogen engine adds #17); the flame also suits hot blocks: the heat vent, welding, flares | | |
| Doors, tools and landing gear: CAUTION MOVING PARTS #17 | 5 of 6 (door, welder, drill, landing gear, flare launcher; the railgun carries only #18), 112 x 79 | | |
| Gun turrets: AMMUNITION #52 | 2 of 3 (gatling, rocket; the medium calibre turret has only a cropped #15), 137 x 65 | | |
| Life support (survival kit, medical room, safe zone): COMPRESSED OXYGEN #30 | 3 of 3, 170 x 87 | small survival kit: #30 129 x 66, with #31 | |
| Add generic extras on any block | #18 on 10 models (7 not hydrogen), HV triangle on 9 (5 not power), #17 on 9 (jump drive, safe zone and medical room have no moving parts), DANGER STRONG MAGNETIC FIELD #15 95 x 53 on 5 (medium calibre turret, welder, heat vent, turret control; the hydrogen thruster maps a scrap of it as a colour swatch) | #18 is 65 x 39 on small grid (about half its large size); the small railgun carries only #18, the small flare launcher only a #15 DANGER header | |
| Make a short CAUTION or WARNING tag from the header band and the bottom border | 4 of 21 signed models, all with #17 (drill, flare launcher, safe zone, welder): about 120 x 33 mm on 1-cell panels (flare launcher 121 x 35, four tags; welder 112 x 32 and 121 x 35), 200-300 wide on big panels (drill 207 x 59, safe zone 301 x 86); the drill adds two 93 x 27 #18 WARNING tags | small flare launcher: two #15 DANGER headers alone, 110 x 21 mm, no border | none |

- **Short tag UVs**: map only the coloured header band, the top third of the piece (v 0.66-1.00 within #17; the top
  43% of #18), and butt a second thin quad with the sign's bottom border (v 0-0.05) right under it, centred, with no
  gap; leave out the middle text.
- **Crop a sign to its text**: the welder and medium calibre turret map #15 without its header and pictogram
  (u 0.36-1.00, v 0-0.66 within the piece).
- **Atlas2 has no paint variants**: its signs keep their printed colours on any host (the medical room's sit on
  Darker).

### Codes and lettering

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Set stencil codes and serials (Atlas2 #41-51) at this cap height | 20-35 mm (30); a few at 12 mm (drill, survival kit) | 16-28 mm (20) | none |
| Inset codes from the nearest panel edge (a little further than signs on large grid) | 20-50 mm (42) | about 10-15 mm (11) | |
| Use these codes (models using each, both grids) | serial #49 198 x 22 (13), MXS-2859-B #41 216 x 32 (10), OB40-E #43 97 x 25 (8), ACG #45 91 x 38 (8), M.G.W. #48 111 x 32 (4); TYPE A barcode label #22 227 x 72 (4) | #49 116 x 13, #45 53 x 22, #22 93 x 29 | |
| Set codes as single lines | 92 of 99 code groups, and 12 of 16 code models use single lines only; 3-line stacks only on the drill and welder, 2-line on the safe zone and gatling turret | always | |
| Crop a code lengthwise for a shorter string, keeping its full height | on 6 of 13 code models, to 25-58% of its length (about half) | no crops | |
| Use TextAtlas letters for short IDs, instructions and gauge labels, never the full block name | IDs 40-85 mm (WLD0, DRL0, TERMINAL1; MX100 59 mm), instructions 18-22 mm (EMERGENCY DOOR RELEASE), gauge labels 13 mm (advanced refinery) | | the block name in letters 71-83 mm tall, on 6 of 20 models |

- **Printed code size varies widely**: #41 runs 73-531 mm wide and #49 75-684; the drill uses #41 at both 35-39 mm and
  12 mm line height.
- **Classic name lettering**: centred left-right, about 0.4 m below the top of a 1-cell face, on 4-6 faces including
  top and bottom: all 6 on the conveyor junction and small cargo container; front, back, top and bottom on the
  assembler and large reactor; one face on the small reactor (20 mm letters). The refinery's run 126-160 mm.

### Stripes and pointer marks

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Mark door thresholds, handles, recesses and access panels with the grey and black stripe band Atlas1 #10, unstretched, full piece height | 27-140 mm across the stripes (79), stretch 0.83-1.15 (mostly 1.0): about 30 mm as trim beside a handle or recess lip, 50-65 on small panels, 90-140 on thresholds and panel fills; on 8 models, half of them in Atlas1Colorable to take the paint | none | none |
| Point white triangles (Atlas2 #7) in facing pairs at a centre line, a face centre or a small part | 10 models, 7 with facing pairs; base 48 mm (17-114), about 50 x 30 typical | small survival kit: two single triangles, 46 x 30 mm | none |
| Across a face: centre the pair on the block's mirror line or face centre | 0.9-4.3 m apart, base about 55-80 mm (welder and beacon 54, safe zone 78), 110-115 on 3-cell blocks (bulk cargo, bulky hydrogen tank); or four at the corners or round a ring, pointing at its centre | | |
| Round a latch or piston fork | 0.1-0.3 m apart, about 30 x 20 mm (27-38) | | |
| Point white chevrons one way, singly or in a row, never in facing pairs; about 3/4 as deep as wide | solid #84 on 7 models, 53 mm across (22-93) x 39 deep; outline #83 on 5, 77 mm (45-85) x 57 | | none |
| Size the red down-triangle Atlas2 #33 | 39 x 33 mm (25-99), on 6 models | 19 x 16 (small survival kit) | |
| Size the octagon X frame Atlas1 #7, often as a mirrored left-right pair | 135 mm square (96-198), on 6 models, pairs on 4 | a 74 mm pair (small railgun) | |
| Size the three-dot cluster Atlas2 #20 | 53 x 51 mm (33-147), on 5 models | 46 mm (small gatling turret) | |
| Size the orange X square Atlas2 #24 | 48 mm (23-77), on 4 models | | |
| Scale marks up on 3-cell blocks | 2-3 times (bulk cargo: #33 99 mm, #20 147 mm) | | |

- **Yellow and black stripes** (Atlas2 #66) are a one-off, on the jump drive only.
- **Stripe widths by block**: door handle 27 mm and threshold 91, beacon-base recess 31, turret control 53, medical
  room 64, welder 42 and 94, advanced refinery 53-121, jump drive 55 and 132, drill panel fill 136.
- **Triangle layouts**: welder 0.94-0.99 m apart (its top pair 28 mm), safe zone 1.11, beacon 1.78 (four triangles
  0.89 m out, pointing at the bottom-face centre from four sides), centred door 2.90 (four on the diagonals,
  1.67 m across x 2.37 m up, pointing at the door centre; base only 23 mm), bulk cargo 4.28; landing gear latches
  0.11-0.16 m, drill piston forks 0.29 m. The bulky hydrogen tank points 16 of its 18 triangles out at the face
  corners instead.
- **Partner UV**: mirror or turn the partner's UV (mirrored on 4 of 7 pair models, turned on 3); #7 carries no text,
  so a mirrored UV is fine here.
- **Chevron layouts**: a lone chevron on a centre line points at the tool head (drill and welder tops); the drill's
  two bottom chevrons point away from it. The centred door jambs carry rows of 3 at a 54 mm pitch, the two rows on
  each jamb pointing away from each other. The outline #83 shrinks to 45 mm on the centred door and landing gear.

### Examples

- **Survival kit (N_L_SurvivalKitReskin) battery-box lid**: two signs 86 and 60 mm wide on one centre line, 9 mm
  apart; a two-line code block in 12 mm caps under the left sign, ending near its right edge; the group inset evenly,
  38 mm from the lid's right flat edge and 39 mm from its top.
- **Centred door (N_L_CentredDoor) emergency release**: TextAtlas EMERGENCY in 22 mm caps over DOOR RELEASE in 18 mm,
  both lines 183 mm wide and centred over the 200 mm handle recess on the panel above; a 28 mm Atlas1 #10 stripe sits
  8 mm above the recess (43 mm below the lettering, across the panel seam) and a matching stripe runs under it.
- **Drill (N_L_DrillReskin) top**: two pairs of 28 x 18 mm white triangles 294 mm apart point in at each piston fork;
  a 77 mm outline chevron #83 on the centre line points at the drill head; a 207 x 59 mm CAUTION tag (#17 header plus
  border); #41 cropped to S-2859-B on a 12 mm line, with the boxed 9 (#42) beside it in the same quad; 35 x 30 mm
  red triangles #33 on the metal plates at the drill-head end point outward.
- **Medical room (N_L_MedicalRoomReskin) oxygen box**: its own-hazard COMPRESSED OXYGEN #30 (171 x 90 mm) 12 mm from
  a generic WARNING HIGH PRESSURE #18 (124 x 76), bottoms within 3 mm of level, the pair roughly centred on the
  Darker box.
- **Welder (N_L_WelderReskin) underside**: two 54 x 35 mm white triangles 938 mm apart on the ledge below the vent
  strip, outboard of the two yellow lights, point in at the centre line; each side panel above carries an Atlas1 #10
  stripe fill, mirrored left and right, about 467 x 94 mm of stripes on a 500 mm wide quad.

## Materials and decal sheets

### Material shares and mapping

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Make about half the visible surface PaintedMetal_Colorable (the plates) | 56% (50-74) | 47% (37-58) | 55% (49-76) |
| Make a quarter to a third PaintedMetal_Darker (frames, end caps, pipes, inner bays) | 26% (11-37) | 38% (21-47) | only 7% (4-17) |
| Change material at a step or a turn, almost never in the middle of a flat face (share of paint/Darker borders) | 97% (87-100) | 90% (75-100) | 100% |
| Where paint and Darker lie parallel, stand one proud of the other (either one on top) | about 60 mm (35-100) | about 23 mm (17-34) | the Darker part is the proud one in about 94% of steps |
| Keep Yellow a small accent on the port frames | 1.1% of the surface (0.1-3.5); 95-100% of it on port frames in blocks with ports | 4.9% (0.4-6.2); only about two thirds (21-85%) on port frames, and 3 of 8 port blocks use it mostly as trim | in 7 of 15 large models, all on ports |
| Keep bare metal, rubber, glass and emissive small accents | metal 1.3% of the surface (0.2-2.2); rubber, glass and emissive 0.1% or less each | metal 1.3% (0.9-3.9) | metal 4.7% |
| Map the painted metals (Colorable, Darker, VeryDark) and Rubber at 0.40 UV per metre: one repeat per 2.5 m, so a large-grid cell face spans 1.0 UV | 0.40 (Darker 0.39-0.40) | 0.40 (0.40-0.41), the same as large grid | paint 0.40; Darker 0.44 (0.40-0.57); Metal_Dull 0.62 |
| Map Yellow port frames and Conveyor denser | Yellow 0.71 (0.41-0.72); Conveyor 0.85 | Yellow 0.51; Conveyor 0.85 | |
| Lay Conveyor with U level (its ribs run along U) | every Conveyor wall in every model; on floors, U along a world axis | every model | same |

- **The painted metals, Chrome and Rubber have no grain**, so their UV rotation is free; Conveyor's ribs fix its
  direction.

### Material roles

Shares in this table count every face, hidden ones included.

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Use VeryDark mostly as a shadow fill: recessed steps, inner frames, the far side of gaps | 2.2% of the area (0.5-7.6), in 21 of 28 models; parts about 300 x 140 mm | 12% (5-19), in 4 of 12 models, mostly as a body colour; it shows at about two thirds of its area share (0.67) | 5.4% (4.2-7.9), in 6 of 15 large models |
| Use Chrome for bare structural or moving metal (rods, pipes, hubs, rings, rails, handles), most pieces small | 2.1% (1.0-3.3), in 17 of 28; pieces about 180 x 105 mm, 60-110 mm thick (a typical piece about 64 mm; weighted by area, about 107) | 2.4% (1.5-3.3), in 8 of 12; about 35 mm thick (23-46) | 1.0% (0.5-4.7), in 12 of 15 large |
| Use Metal_Dull for small mechanism hardware: pads, clamps and the reused port latch kit | 0.34% (0.16-1.8), in 22 of 28; parts 43-50 mm thick | 1.9%, in 7 of 12; 30-35 mm thick | 1.6% (0.5-5.0), in 10 of 15 large; 50-70 mm thick |
| Use Rubber for hoses, cables, seals and small pads at clamps and gauges | 0.6% (0.4-1.2); parts about 51 mm thick (32-83) | 1.0%; about 15 mm thick | same |
| Put plain Emissive on small, nearly flat panels (strips, lamps and Emissive0-3 gauges: "Standard parts") | 0.15% (0.04-0.25), in 14 of 28; panels about 314 x 105 mm (long side 166-538, short side 45-186) | in 1 model only | 0.72%, in 4 of 15 large |

- **VeryDark reads as shade.** It shows at about half its area share (0.52, range 0.26-0.89; paint about 1.2 times
  its share, Darker 0.76), and 62% of its faces look at other geometry within 0.25 m (paint a third, Darker 45%); it
  sits more hemmed in than Darker in 15 of 21 models. Open faces and undersides are allowed: the heavy calibre turret
  (N_L_HeavyCalibreTurret) has 16%, all on the underside, and the hydrogen engine (N_L_HydrogenEngineReskin) 17%,
  more open than its Darker.
- **On small grid VeryDark is a body colour**, not a shadow fill: the rocket launcher (N_S_RocketLauncherReskin)
  22%, the survival kit (N_S_SurvivalKitReskinSmall) 18%. Its faces are no more hemmed in than Darker (a quarter of
  them look at geometry within 50 mm, a third for Darker).
- **Chrome runs can be long**: a few joined pieces reach 3 m (the bulky hydrogen tank).
- **The port latch kit** (Metal_Dull rails 480 x 50 x 20 mm, pins 56 x 28 x 28, latches 60 x 56 x 44, plates
  76 x 40 x 12) appears in 16-18 newer large models and 7 classic ones, but is over half the Metal_Dull area in only
  9 of 22 (about a fifth on a typical block). The rest is pads, clamps and other mechanism parts, such as the
  landing gear pads. Small grid mostly lacks the kit; about half its Metal_Dull (15-94%) sits within 0.25 m of a
  Conveyor face. Three classic models also carry long round Metal_Dull rods, 3.2 m x 80 mm.

### Decals

| What | Newer large grid | Newer small grid | Classic |
|---|---|---|---|
| Cover about 6% (large) to 9% (small) of the visible surface with decals | 6.1% (4.1-8.4); a single-cell block carries about 400-1000 decal pieces | 8.9% (5.8-14.5) | about 1%, on every host |
| Use the decal variant that matches the face under it | 87% of decals (82-94) | 84% (79-91) | |
| Give Darker at least as many decals as paint (decal area per host area) | Darker 5.8%, paint 4.5%: Darker about 1.1 times paint block by block, at least equal in 17 of 28 models; on the visible surface 10.1% against 6.0% (1.55 times, at least equal in 19 of 26) | paint 7.2%, Darker 5.1%, about equal block by block (1.03; Darker at least equal in 6 of 10) | about 1% on every host |
| Give VeryDark about as many as paint, bare metal fewer, Yellow none | VeryDark 4.5%, Chrome 2.8%, all bare metal 0.7%; Yellow 0% (17 of 24 models with Yellow have no decal on it) | VeryDark 3.7%, bare metal 0%, Yellow 0% (7 of 10 have none) | Yellow none |
| Use these sheets (newer large: models out of 28 that use each) | Atlas3 28, Atlas1 27, Atlas4 23, ButtonsAtlas 22, Atlas2 21, Decals (bolts, signs) 20, Paneling 15 | Atlas3 12 of 12, Atlas4 11 of 12 | only Decals (bolt heads, seams #58 and #61), Paneling (7 of 15 large) and TextAtlas; no Atlas1-4 or ButtonsAtlas |
| Use Atlas1 relief plates as slot or louvre inserts on Darker or paint | #5 comb: Darker 40%, paint 38%, Chrome 15%; #3: half on Darker, half on paint (both sized in "Standard parts"); #6 272 x 201 (253-322 x 180-268): two thirds on Darker | rare: #5 once, 829 x 78 | not used |
| Bend Atlas4 bands round curved and bevelled parts and carry them on over sharp edges | #4 striped band about 42 mm wide (34-64), #6 raised blocks about 50, #5 perforated about 58 (31-70); on paint, Darker and Chrome | only #4, in 4 of 12 models, as wide panel fill (0.05-1.6 m), not as bands | not used |

- **Decal variant follows the host**: _Colorable on paint (Atlas1Colorable for Atlas1, used for 75% of the Atlas1 on
  paint), _Darker on Darker, _Chrome on bare metal. Where a sheet has no variant for the host, use the closest one:
  - On VeryDark: _Darker for Atlas3 (87%; on small grid two thirds, the rest _Chrome) and for ButtonsAtlas (two
    thirds; on small grid, both models that put it on VeryDark), plain Atlas1 (68%). Atlas4 has a _VeryDark variant,
    but VeryDark hosts take _Darker (50%) about as often as _VeryDark (47%); small grid leans to _VeryDark (65%).
  - On Darker: plain Atlas1 (84%; two thirds on small grid), since Atlas1 comes only plain and Colorable.
  - On Chrome: ButtonsAtlas and Atlas1 have no Chrome variant; use ButtonsAtlas_Darker (every case) and plain
    Atlas1 (75%).
- **Atlas1 #3 and #6 carry their louvres in the normal map** (#6 also an A-frame); #5 is a comb of six tall slots.
- **Atlas4 bands stay bent or continuous.** Nearly every piece (94-100%) either bends more than 5 mm out of flat
  (#4 86%, #6 71%, #5 all) or carries on as the next piece of a chain round a turn of more than 20 degrees (#4 about
  two thirds, though 3 of 12 models never do it; #6 and #5 rarely). Closed rings round cylinders count.

### Examples

- **Industrial assembler (N_L_AssemblerIndustrial)**: Colorable plates about 47% and the Darker frame about 42% of
  the visible surface, far more Darker than most. Yellow is almost all port frames, apart from a few small latches.
  The big side port's Conveyor sits about 110 mm behind the frame front, the two small ports on top about 35 mm.
- **Heat vent (N_L_HeatVent)**, top corner: the #3 slot with knob sits right in the corner, its knob end a second
  #3 quad; the #10 ring disc sits just inside the corner, about 80 mm clear of the edge bevel. All are
  Atlas3_Colorable, because the face is paint.
- **Bulky hydrogen tank (N_L_BulkyHydrogenTank)**, side port: a bare yellow frame, the sunk Conveyor back face with
  its ribs level, an Emissive0-3 gauge of four tiles about 113 x 100 mm, Metal_Dull latch rails 481 x 50 mm, a
  Chrome pipe, a VeryDark step deep in the recess beside the port, and an Atlas3_Darker #36 trapezoid bar
  1062 x 67 mm on the Darker frame.
- **Landing gear (N_L_LandingGearReskin)**: black Rubber hoses 30-55 mm thick, a Chrome hub carrying the matching
  Atlas3_Chrome decal, a short Chrome bar at the edge, a Metal_Dull lock pad (not the port latch kit), and a plain
  Atlas1 #5 strip 387 x 60 mm on the edge of the Darker panel.

## Checking a model

`scripts/keen_check.py` measures a SEUT model and prints PASS, WARN or INFO for each table row above that a script
can measure, against the vanilla ranges in `keen-rules.json` [HARD, run]. The same script surveyed the 60 vanilla
models, so the model and the ranges are measured the same way; a range can differ a little from the tables above,
which other scripts measured. Run it headless on a copy of the .blend, never the file open in Blender:

```bash
blender -b <copy.blend> --python <skill>/scripts/keen_check.py -- --era newer --out <folder>
```

- **It measures what SEUT exports**: the `Main (...)` collection of the active scene (`--scene` picks another), with
  modifiers applied. Run it once per subpart scene. The grid comes from the SEUT scene; `--grid` overrides it.
- **Shares count the visible surface**: a sample point counts when any of 162 ray directions in front of it escapes
  the model, so faces inside housings or buried in other parts drop out. Hidden faces are 38% (28-47) of a vanilla
  model's area and were 70% on one large modded turret [HARD, measured], so shares over all faces mislead. The
  Material roles rows count every face, as that table does.
- **PASS** is inside the middle 80% of vanilla models of the same era and grid; **WARN** is outside it on the side
  that matters (too few bevelled edges, not too many); **INFO** is reported only. A WARN asks whether the difference
  is meant; it is not an error.
- **The craft-rule rows** (decal gap, decals inside their face, the game's vertex packing) use the skill's limits,
  not Keen's ("Which rules win"). The report ends with the rows it cannot measure; check those by eye.
- **Without Blender**: `--out` saves `<name>.survey.json`, and `python keen_check.py --compare <name>.survey.json
  --era classic` re-prints the report. `--model <file.glb or .fbx>` surveys an exported or vanilla model, and
  `--build-rules` rebuilds `keen-rules.json` from such surveys.
