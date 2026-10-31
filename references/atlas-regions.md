# Decal atlas region maps

Where each piece sits in the vanilla decal atlases, so a decal quad can be UV-mapped to a known piece instead of guessing.

- UV values use Blender's convention: (0, 0) is the **bottom left** of the image, so they can be typed straight into the UV editor.
- Boxes are tight bounding boxes of the opaque pixels in the `_alphamask` texture, measured at 512 px and reported as fractions of the full image. Add a small margin in the UV editor if edges bleed.
- `px` is the piece size at the texture's full resolution.
- [SOFT] Boxes come from `scripts/extract_atlas_regions.py`; the description column was read by eye from `scripts/annotate_atlas.py` previews. Boxes are reliable, descriptions of small pieces less so (see the note under each atlas). The raw numbers are in `atlas-regions.json`.

## Which materials use which atlas

| Atlas | Materials | Content |
|---|---|---|
| `Atlas1` | Atlas1, Atlas1Colorable | Plate and panel decals. The Colorable variant is paintable. |
| `Atlas2` | Atlas2 | Sticker and label sheet: hazard signs, HUD marks, food and ship-system icons. |
| `Atlas3` | Atlas3_* | Mechanical detail plates: vents, slots, dishes, panels. Paintable. |
| `Atlas4` | Atlas4_* | Trim bands and trapezoid caps. Paintable. |
| `ButtonsAtlas` | ButtonsAtlas_* | Buttons, switches, LEDs, keypads and connectors for control panels. |
| `Decals_Atlas_A_01` | Decals, PanelingColorable, PanelingDarker | Large decal sheet: signs, fittings, plates, grime and trim strips. |
| `TextAtlas` | TextAtlas, TextAtlasDark | Capital letters, digits and a human silhouette. |

`PanelingDarker` uses `Decals_Atlas_A_02` colour and add maps with the A_01 alpha layout. [SOFT] Check the layout matches before reusing A_01 boxes on it.

## Mapping a piece onto a quad

```python
def map_quad_to_region(obj, u0, v0, u1, v1, uv_name='UVMap'):
    # obj: one quad mesh. Corners go bottom-left, bottom-right, top-right, top-left in loop order.
    uv = obj.data.uv_layers[uv_name].data
    for loop, (u, v) in zip(obj.data.polygons[0].loop_indices, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]):
        uv[loop].uv = (u, v)
```

Rotate the quad (or reorder the corner list) rather than flipping UVs when a piece is the wrong way up. Keep the quad's aspect ratio equal to the region's `px` ratio so the piece is not stretched.

## Regenerating

1. In Blender, run `scripts/extract_atlas_regions.py` through the Blender MCP (set `ASSET_TEXTURES` and `OUT_DIR` first). It writes `regions.json` and `<atlas>_prev.png`.
2. Run `python scripts/annotate_atlas.py <OUT_DIR>` to draw numbered boxes.
3. Read the annotated images and fix descriptions. For touching pieces, add rough rectangles to `SPLIT_HINTS`.

## Atlas1

Full size 2048 x 2048 px, 13 regions. Boxes checked by eye.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.521 | 0.922 | 0.568 | 0.969 | 96x96 | round dot (corner of five-dot pattern) |
| 2 | 0.623 | 0.922 | 0.668 | 0.969 | 92x96 | round dot |
| 3 | 0.572 | 0.873 | 0.619 | 0.918 | 96x92 | round dot (centre) |
| 4 | 0.682 | 0.809 | 0.996 | 0.982 | 644x356 | large plain rounded plate, upper right |
| 5 | 0.521 | 0.822 | 0.568 | 0.869 | 96x96 | round dot |
| 6 | 0.623 | 0.822 | 0.668 | 0.869 | 92x96 | round dot |
| 7 | 0.0 | 0.617 | 0.393 | 1.0 | 804x784 | big plate: four tall slots, a comb of thin slots, and a field of round holes (several pieces in one box) |
| 8 | 0.402 | 0.613 | 0.475 | 0.996 | 148x784 | lattice truss column (four stacked cells) |
| 9 | 0.488 | 0.617 | 0.713 | 0.789 | 460x352 | plain scratched plate |
| 10 | 0.756 | 0.504 | 0.998 | 0.746 | 496x496 | octagon frame with an X (hazard-style) |
| 11 | 0.0 | 0.52 | 0.709 | 0.6 | 1452x164 | yellow and black hazard stripe |
| 12 | 0.016 | 0.121 | 0.973 | 0.5 | 1960x776 | schematic panel: two large plates, wires, round pads, vents (several pieces in one box) |
| 13 | 0.0 | 0.029 | 1.0 | 0.049 | 2048x40 | thin full-width strip |

## Atlas2

Full size 2048 x 2048 px, 44 regions. Boxes found by script; labels read by eye. Box 15 is a merged group, and some pieces have no box (the medical kit caption, the serial-number text block, the red crossed-out WARNING, the red warning triangle, the logo marks at the right edge). Re-check small pieces in the UV editor before relying on them.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.0 | 0.873 | 0.127 | 0.996 | 260x252 | medical heart icon on a pink tile |
| 2 | 0.131 | 0.881 | 0.244 | 0.994 | 232x232 | disc: left arrow |
| 3 | 0.256 | 0.881 | 0.369 | 0.994 | 232x232 | disc: shopping cart / download |
| 4 | 0.381 | 0.881 | 0.494 | 0.994 | 232x232 | disc: skip back |
| 5 | 0.506 | 0.881 | 0.619 | 0.994 | 232x232 | disc: pause/step |
| 6 | 0.625 | 0.875 | 0.852 | 1.0 | 464x256 | WARNING tip-over hazard sign |
| 7 | 0.881 | 0.898 | 0.93 | 0.975 | 100x156 | white left-pointing triangle |
| 8 | 0.955 | 0.941 | 0.992 | 0.955 | 76x28 | vertical word fragment RIGHT (letters stacked) |
| 9 | 0.955 | 0.975 | 0.992 | 0.988 | 76x28 | vertical word fragment RIGHT, top letters |
| 10 | 0.955 | 0.885 | 0.992 | 0.898 | 76x28 | vertical word fragment RIGHT, bottom letters |
| 11 | 0.178 | 0.826 | 0.191 | 0.863 | 28x76 | tiny fragment inside the LEFT DOWN UP word line |
| 12 | 0.5 | 0.818 | 0.596 | 0.871 | 196x108 | HIGH VOLTAGE label |
| 13 | 0.25 | 0.691 | 0.389 | 0.812 | 284x248 | flame hazard triangle |
| 14 | 0.414 | 0.691 | 0.586 | 0.812 | 352x248 | CAUTION MOVING PARTS |
| 15 | 0.6 | 0.684 | 0.986 | 0.867 | 792x376 | merged box: Remote Operated System strip, WARNING HIGH PRESSURE, explosive diamond, dots (split by hand before use) |
| 16 | 0.0 | 0.688 | 0.225 | 0.812 | 460x256 | DANGER strong magnetic field |
| 17 | 0.389 | 0.611 | 0.592 | 0.686 | 416x152 | RESTRICTED AREA |
| 18 | 0.611 | 0.619 | 0.672 | 0.682 | 124x128 | X-mark hazard square |
| 19 | 0.688 | 0.623 | 0.746 | 0.682 | 120x120 | battery icon, orange |
| 20 | 0.764 | 0.609 | 0.844 | 0.676 | 164x136 | double chevron arrow |
| 21 | 0.938 | 0.609 | 0.992 | 0.67 | 112x124 | striped corner tile |
| 22 | 0.0 | 0.559 | 0.365 | 0.674 | 748x236 | TYPE A label with barcode |
| 23 | 0.387 | 0.561 | 0.586 | 0.596 | 408x72 | SIGNAL with radio waves |
| 24 | 0.6 | 0.568 | 0.639 | 0.605 | 80x76 | HUD corner arc fragment |
| 25 | 0.523 | 0.508 | 0.539 | 0.541 | 32x68 | small red square |
| 26 | 0.561 | 0.514 | 0.592 | 0.541 | 64x56 | small red down-triangle |
| 27 | 0.605 | 0.525 | 0.643 | 0.564 | 76x80 | HUD ring arc |
| 28 | 0.711 | 0.543 | 0.75 | 0.582 | 80x80 | square with diagonal split |
| 29 | 0.787 | 0.533 | 0.842 | 0.59 | 112x116 | striped diamond |
| 30 | 0.855 | 0.521 | 1.0 | 0.6 | 296x160 | ENERGY SOURCE, yellow |
| 31 | 0.008 | 0.416 | 0.268 | 0.547 | 532x268 | COMPRESSED OXYGEN label |
| 32 | 0.283 | 0.424 | 0.504 | 0.537 | 452x232 | CAUTION BATTERY BOX |
| 33 | 0.824 | 0.459 | 0.869 | 0.504 | 92x92 | X in square icon |
| 34 | 0.424 | 0.375 | 0.449 | 0.408 | 52x68 | small bottle shape |
| 35 | 0.166 | 0.289 | 0.404 | 0.402 | 488x232 | AMMUNITION label |
| 36 | 0.42 | 0.289 | 0.453 | 0.373 | 68x172 | white tube shape |
| 37 | 0.539 | 0.252 | 0.715 | 0.428 | 360x360 | RADIOACTIVE diamond |
| 38 | 0.725 | 0.146 | 0.795 | 0.428 | 144x576 | four food icons (utensils, water, wheat, mushroom) |
| 39 | 0.801 | 0.156 | 0.994 | 0.428 | 396x556 | MEAL PACK nutrition label with QR code |
| 40 | 0.166 | 0.211 | 0.309 | 0.281 | 292x144 | two icons: spider and steak |
| 41 | 0.006 | 0.113 | 0.305 | 0.203 | 612x184 | SEEDS label |
| 42 | 0.811 | 0.121 | 1.0 | 0.152 | 388x64 | SPORES strip |
| 43 | 0.0 | 0.055 | 0.25 | 0.105 | 512x104 | orange hazard stripes |
| 44 | 0.0 | 0.0 | 1.0 | 0.051 | 2048x104 | four stripe bands: yellow/black, white/black, pink/white, grey/black |

## Atlas3

Full size 2048 x 2048 px, 43 regions. Boxes checked by eye; descriptions are rough shape names.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.01 | 0.822 | 0.178 | 0.99 | 344x344 | round disc with centre hole and rings |
| 2 | 0.193 | 0.818 | 0.307 | 0.992 | 232x356 | plate with centre dot and notch |
| 3 | 0.326 | 0.818 | 0.363 | 0.994 | 76x360 | slim dark trapezoid slot |
| 4 | 0.383 | 0.816 | 0.494 | 0.996 | 228x368 | rounded plate with dark rectangular window |
| 5 | 0.504 | 0.82 | 0.621 | 0.992 | 240x352 | clamp block with two rounded bars |
| 6 | 0.65 | 0.818 | 0.73 | 0.994 | 164x360 | trapezoid wedge |
| 7 | 0.754 | 0.816 | 0.934 | 0.996 | 368x368 | large round speaker grille |
| 8 | 0.941 | 0.818 | 0.998 | 0.998 | 116x368 | tall slot with knob and dot |
| 9 | 0.256 | 0.693 | 0.371 | 0.809 | 236x236 | round cap with cross |
| 10 | 0.508 | 0.691 | 0.555 | 0.811 | 96x244 | vertical strip with three holes |
| 11 | 0.57 | 0.691 | 0.617 | 0.811 | 96x244 | small rounded pill |
| 12 | 0.939 | 0.752 | 1.0 | 0.811 | 124x120 | small round dimple |
| 13 | 0.006 | 0.693 | 0.059 | 0.807 | 108x232 | small dark slot pill |
| 14 | 0.086 | 0.693 | 0.162 | 0.807 | 156x232 | small tab with hex bolt |
| 15 | 0.178 | 0.688 | 0.248 | 0.811 | 144x252 | small plain rectangle |
| 16 | 0.377 | 0.689 | 0.498 | 0.811 | 248x248 | disc with concentric rings |
| 17 | 0.623 | 0.699 | 0.752 | 0.797 | 264x200 | horizontal clamp bar |
| 18 | 0.756 | 0.691 | 0.932 | 0.809 | 360x240 | plate with six round dimples |
| 19 | 0.947 | 0.689 | 1.0 | 0.748 | 108x120 | small slot with edge |
| 20 | 0.883 | 0.564 | 0.93 | 0.686 | 96x248 | small pill |
| 21 | 0.945 | 0.568 | 0.996 | 0.684 | 104x236 | pill with cross bar |
| 22 | 0.006 | 0.443 | 0.059 | 0.682 | 108x488 | tall dark slot |
| 23 | 0.07 | 0.445 | 0.305 | 0.682 | 480x484 | four-triangle panel (X pattern) |
| 24 | 0.316 | 0.441 | 0.373 | 0.686 | 116x500 | tall plain strip |
| 25 | 0.381 | 0.443 | 0.619 | 0.682 | 488x488 | large panel with mesh grille and frame |
| 26 | 0.629 | 0.441 | 0.684 | 0.684 | 112x496 | tall narrow bar |
| 27 | 0.693 | 0.443 | 0.809 | 0.684 | 236x492 | slatted vent (two groups) |
| 28 | 0.818 | 0.443 | 0.869 | 0.684 | 104x492 | tall panel with inset square |
| 29 | 0.881 | 0.383 | 0.994 | 0.494 | 232x228 | shallow round dish |
| 30 | 0.002 | 0.252 | 0.186 | 0.436 | 376x376 | triangular corner plate with diagonal slots |
| 31 | 0.191 | 0.254 | 0.371 | 0.434 | 368x368 | square plate, rounded corners, two slots |
| 32 | 0.381 | 0.256 | 0.496 | 0.432 | 236x360 | panel with hinge notch |
| 33 | 0.506 | 0.254 | 0.621 | 0.434 | 236x368 | panel with centre slot |
| 34 | 0.625 | 0.254 | 0.75 | 0.434 | 256x368 | panel with two inset blocks and a dot |
| 35 | 0.764 | 0.256 | 0.861 | 0.432 | 200x360 | tall panel with bands and four screws |
| 36 | 0.887 | 0.262 | 0.988 | 0.363 | 208x208 | square recess (pyramid) |
| 37 | 0.01 | 0.189 | 0.492 | 0.248 | 988x120 | long trapezoid bar |
| 38 | 0.504 | 0.129 | 0.621 | 0.246 | 240x240 | 5x5 grid of holes |
| 39 | 0.627 | 0.127 | 0.873 | 0.248 | 504x248 | wide frame with dark slot |
| 40 | 0.008 | 0.01 | 0.117 | 0.178 | 224x344 | small plate with two holes |
| 41 | 0.145 | 0.008 | 0.223 | 0.18 | 160x352 | small tall window |
| 42 | 0.262 | 0.006 | 0.363 | 0.182 | 208x360 | rivet pattern |
| 43 | 0.885 | 0.008 | 0.99 | 0.242 | 216x480 | tall pill with dark vent slits |

## Atlas4

Full size 1024 x 1024 px, 9 regions. Boxes checked by eye.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.008 | 0.695 | 0.244 | 0.773 | 242x80 | trapezoid, slants left |
| 2 | 0.256 | 0.695 | 0.494 | 0.773 | 244x80 | trapezoid, slants right |
| 3 | 0.508 | 0.695 | 0.744 | 0.773 | 242x80 | trapezoid, slants left |
| 4 | 0.756 | 0.695 | 0.994 | 0.773 | 244x80 | trapezoid, slants right |
| 5 | 0.0 | 0.57 | 1.0 | 0.67 | 1024x102 | plate strip with eight dimples |
| 6 | 0.0 | 0.484 | 1.0 | 0.518 | 1024x34 | thin strip with a dark line |
| 7 | 0.0 | 0.336 | 1.0 | 0.436 | 1024x102 | wide strip with a dark line |
| 8 | 0.0 | 0.125 | 1.0 | 0.303 | 1024x182 | wide plate band |
| 9 | 0.0 | 0.018 | 1.0 | 0.102 | 1024x86 | band with square pads |

## ButtonsAtlas

Full size 2048 x 2048 px, 32 regions. Boxes found by script; small pieces were not all confirmed.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.004 | 0.879 | 0.246 | 0.996 | 496x240 | panel: three round toggles with three LEDs |
| 2 | 0.254 | 0.879 | 0.496 | 0.996 | 496x240 | Panel 1: seven LEDs and seven buttons |
| 3 | 0.502 | 0.879 | 0.684 | 0.996 | 372x240 | F1-F6 button panel |
| 4 | 0.697 | 0.943 | 0.74 | 0.986 | 88x88 | green LED |
| 5 | 0.752 | 0.877 | 0.873 | 0.998 | 248x248 | white round button |
| 6 | 0.877 | 0.877 | 0.998 | 0.998 | 248x248 | yellow round button |
| 7 | 0.697 | 0.889 | 0.74 | 0.932 | 88x88 | red LED |
| 8 | 0.125 | 0.762 | 0.25 | 0.863 | 256x208 | two red rocker switches |
| 9 | 0.508 | 0.76 | 0.561 | 0.867 | 108x220 | slider switch, red |
| 10 | 0.568 | 0.76 | 0.621 | 0.867 | 108x220 | slider switch, green |
| 11 | 0.629 | 0.76 | 0.682 | 0.867 | 108x220 | slider switch, yellow |
| 12 | 0.689 | 0.76 | 0.74 | 0.867 | 104x220 | slider switch, blue |
| 13 | 0.754 | 0.756 | 0.871 | 0.871 | 240x236 | white square button |
| 14 | 0.879 | 0.756 | 0.996 | 0.871 | 240x236 | yellow square button |
| 15 | 0.004 | 0.629 | 0.121 | 0.871 | 240x496 | 12-key keypad (Esc, Spin, ...) |
| 16 | 0.129 | 0.691 | 0.184 | 0.746 | 112x112 | grey ring button |
| 17 | 0.191 | 0.691 | 0.246 | 0.746 | 112x112 | blue ring button |
| 18 | 0.254 | 0.629 | 0.496 | 0.871 | 496x496 | control panel: M1-M5 buttons, round pads, slider |
| 19 | 0.129 | 0.629 | 0.184 | 0.684 | 112x112 | orange ring button |
| 20 | 0.191 | 0.629 | 0.246 | 0.684 | 112x112 | green ring button |
| 21 | 0.506 | 0.629 | 0.756 | 0.75 | 512x248 | row of knobs, lever, joystick and two plug sockets (several pieces in one box) |
| 22 | 0.77 | 0.637 | 0.871 | 0.738 | 208x208 | round connector, dark socket |
| 23 | 0.885 | 0.639 | 0.988 | 0.74 | 212x208 | six-pin round connector |
| 24 | 0.383 | 0.551 | 0.449 | 0.617 | 136x136 | plain light square button |
| 25 | 0.455 | 0.551 | 0.523 | 0.619 | 140x140 | plain light square button |
| 26 | 0.531 | 0.547 | 0.611 | 0.619 | 164x148 | round jack, white |
| 27 | 0.619 | 0.547 | 0.699 | 0.619 | 164x148 | round jack, yellow and green |
| 28 | 0.707 | 0.547 | 0.785 | 0.619 | 160x148 | round jack, red |
| 29 | 0.793 | 0.547 | 0.873 | 0.619 | 164x148 | round jack, cyan |
| 30 | 0.254 | 0.5 | 0.371 | 0.617 | 240x240 | EMERGENCY STOP button |
| 31 | 0.881 | 0.504 | 0.992 | 0.621 | 228x240 | large round socket |
| 32 | 0.877 | 0.379 | 0.998 | 0.498 | 248x244 | large round button with red ring |

## Decals_Atlas_A_01

Full size 2048 x 2048 px, 42 regions. The left block has touching pieces, so its boxes come from hand-placed hints (SPLIT_HINTS in the script). Ids 36-42 are full-width strips; fine grime specks around v 0.1 have no boxes.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.004 | 0.971 | 0.342 | 0.998 | 692x56 | row of eleven bolt and fitting heads |
| 2 | 0.344 | 0.926 | 0.566 | 1.0 | 456x152 | grime streak overlay |
| 3 | 0.598 | 0.945 | 0.627 | 0.969 | 60x48 | grime speck |
| 4 | 0.627 | 0.945 | 0.646 | 0.969 | 40x48 | grime speck |
| 5 | 0.664 | 0.891 | 0.711 | 0.988 | 96x200 | tall rounded plate |
| 6 | 0.734 | 0.959 | 0.891 | 0.979 | 320x40 | thin bar |
| 7 | 0.33 | 0.857 | 0.389 | 0.889 | 120x64 | grime blob |
| 8 | 0.729 | 0.898 | 0.896 | 0.918 | 344x40 | thin bar |
| 9 | 0.912 | 0.83 | 0.994 | 0.982 | 168x312 | tall rounded panel |
| 10 | 0.002 | 0.781 | 0.125 | 0.844 | 252x128 | pipe cross fittings |
| 11 | 0.135 | 0.795 | 0.178 | 0.83 | 88x72 | small square plate |
| 12 | 0.664 | 0.783 | 0.713 | 0.873 | 100x184 | tall rounded plate |
| 13 | 0.734 | 0.834 | 0.893 | 0.854 | 324x40 | thin bar |
| 14 | 0.002 | 0.725 | 0.059 | 0.777 | 116x108 | rounded square plate |
| 15 | 0.127 | 0.744 | 0.225 | 0.844 | 200x204 | pipe elbow |
| 16 | 0.285 | 0.717 | 0.299 | 0.82 | 28x212 | scratch line |
| 17 | 0.078 | 0.727 | 0.109 | 0.773 | 64x96 | small rounded square |
| 18 | 0.502 | 0.627 | 0.654 | 0.838 | 312x432 | frame with window |
| 19 | 0.67 | 0.633 | 0.705 | 0.775 | 72x292 | tall pill plate |
| 20 | 0.314 | 0.594 | 0.404 | 0.686 | 184x188 | ring disc |
| 21 | 0.414 | 0.596 | 0.494 | 0.686 | 164x184 | rounded square plate |
| 22 | 0.719 | 0.529 | 1.0 | 0.812 | 576x580 | vent grille |
| 23 | 0.002 | 0.467 | 0.307 | 0.688 | 624x452 | DANGER HIGH VOLTAGE sign |
| 24 | 0.539 | 0.561 | 0.617 | 0.617 | 160x116 | circuit logo sticker |
| 25 | 0.646 | 0.562 | 0.697 | 0.615 | 104x108 | chevron badge |
| 26 | 0.646 | 0.488 | 0.699 | 0.539 | 108x104 | chevron badge |
| 27 | 0.354 | 0.41 | 0.43 | 0.59 | 156x368 | tall chamfered plate |
| 28 | 0.443 | 0.41 | 0.525 | 0.59 | 168x368 | tall octagon plate with side notches |
| 29 | 0.559 | 0.414 | 0.594 | 0.547 | 72x272 | vertical text, Good AI |
| 30 | 0.729 | 0.441 | 0.771 | 0.527 | 88x176 | pipe end |
| 31 | 0.188 | 0.312 | 0.346 | 0.469 | 324x320 | pressure gauge |
| 32 | 0.646 | 0.412 | 0.699 | 0.461 | 108x100 | chevron badge |
| 33 | 0.779 | 0.312 | 1.0 | 0.533 | 452x452 | heart on grunge tile |
| 34 | 0.004 | 0.312 | 0.184 | 0.465 | 368x312 | high-voltage triangle |
| 35 | 0.34 | 0.346 | 0.785 | 0.393 | 912x96 | chain / lattice strip |
| 36 | 0.0 | 0.295 | 1.0 | 0.309 | 2048x28 | full-width strips and bolt rows, stacked (36-42 each span u 0 to 1) |
| 37 | 0.0 | 0.232 | 1.0 | 0.246 | 2048x28 | full-width strip |
| 38 | 0.0 | 0.256 | 1.0 | 0.27 | 2048x28 | full-width strip |
| 39 | 0.0 | 0.141 | 1.0 | 0.174 | 2048x68 | full-width rolled-edge band |
| 40 | 0.0 | 0.193 | 1.0 | 0.207 | 2048x28 | full-width strip |
| 41 | 0.0 | 0.045 | 1.0 | 0.055 | 2048x20 | full-width strip |
| 42 | 0.0 | 0.008 | 1.0 | 0.023 | 2048x32 | full-width strip |

## TextAtlas

Full size 1024 x 1024 px, 38 regions. Boxes checked by eye.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.021 | 0.861 | 0.098 | 0.98 | 78x122 | letter A |
| 2 | 0.172 | 0.861 | 0.25 | 0.98 | 80x122 | letter B |
| 3 | 0.32 | 0.861 | 0.398 | 0.98 | 80x122 | letter C |
| 4 | 0.465 | 0.861 | 0.541 | 0.98 | 78x122 | letter D |
| 5 | 0.615 | 0.861 | 0.686 | 0.98 | 72x122 | letter E |
| 6 | 0.752 | 0.861 | 0.824 | 0.98 | 74x122 | letter F |
| 7 | 0.883 | 0.861 | 0.961 | 0.98 | 80x122 | letter G |
| 8 | 0.021 | 0.695 | 0.092 | 0.816 | 72x124 | letter H |
| 9 | 0.168 | 0.695 | 0.184 | 0.814 | 16x122 | letter I |
| 10 | 0.248 | 0.695 | 0.312 | 0.816 | 66x124 | letter J |
| 11 | 0.387 | 0.695 | 0.459 | 0.816 | 74x124 | letter K |
| 12 | 0.521 | 0.695 | 0.58 | 0.816 | 60x124 | letter L |
| 13 | 0.635 | 0.695 | 0.75 | 0.816 | 118x124 | letter M |
| 14 | 0.816 | 0.695 | 0.893 | 0.816 | 78x124 | letter N |
| 15 | 0.02 | 0.529 | 0.1 | 0.648 | 82x122 | letter O |
| 16 | 0.172 | 0.529 | 0.248 | 0.648 | 78x122 | letter P |
| 17 | 0.316 | 0.512 | 0.398 | 0.648 | 84x140 | letter Q |
| 18 | 0.467 | 0.529 | 0.545 | 0.648 | 80x122 | letter R |
| 19 | 0.611 | 0.529 | 0.703 | 0.648 | 94x122 | letter S |
| 20 | 0.754 | 0.529 | 0.84 | 0.648 | 88x122 | letter T |
| 21 | 0.898 | 0.529 | 0.975 | 0.65 | 78x124 | letter U |
| 22 | 0.016 | 0.363 | 0.1 | 0.484 | 86x124 | letter V |
| 23 | 0.164 | 0.363 | 0.287 | 0.484 | 126x124 | letter W |
| 24 | 0.352 | 0.363 | 0.438 | 0.484 | 88x124 | letter X |
| 25 | 0.496 | 0.363 | 0.582 | 0.484 | 88x124 | letter Y |
| 26 | 0.643 | 0.363 | 0.727 | 0.482 | 86x122 | letter Z |
| 27 | 0.783 | 0.363 | 0.855 | 0.451 | 74x90 | small x (alternate X) |
| 28 | 0.041 | 0.197 | 0.076 | 0.316 | 36x122 | digit 1 |
| 29 | 0.16 | 0.197 | 0.246 | 0.316 | 88x122 | digit 2 |
| 30 | 0.305 | 0.197 | 0.387 | 0.316 | 84x122 | digit 3 |
| 31 | 0.453 | 0.197 | 0.535 | 0.316 | 84x122 | digit 4 |
| 32 | 0.59 | 0.197 | 0.676 | 0.316 | 88x122 | digit 5 |
| 33 | 0.74 | 0.197 | 0.828 | 0.316 | 90x122 | digit 6 |
| 34 | 0.879 | 0.197 | 0.965 | 0.316 | 88x122 | digit 7 |
| 35 | 0.016 | 0.021 | 0.102 | 0.143 | 88x124 | digit 8 |
| 36 | 0.158 | 0.021 | 0.242 | 0.143 | 86x124 | digit 9 |
| 37 | 0.303 | 0.021 | 0.389 | 0.143 | 88x124 | digit 0 |
| 38 | 0.469 | 0.014 | 0.793 | 0.164 | 332x154 | human silhouette |

