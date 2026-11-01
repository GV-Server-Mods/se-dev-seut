# Decal atlas region maps

Where each piece sits in the vanilla decal atlases, so a decal quad can be UV-mapped to a known piece instead of guessing.

- UV values use Blender's convention: (0, 0) is the **bottom left** of the image, so they can be typed straight into the UV editor.
- Boxes are bounding boxes of the piece's pixels in the `_alphamask` texture, reported as fractions of the full image.
- `px` is the piece size at the texture's full resolution.
- Atlas2, ButtonsAtlas and Decals_Atlas_A_01 were re-catalogued at full resolution (2048 px) and checked piece by
  piece against the owner's markup [HARD]: faint faded edges are included, touching pieces are split on the
  emptiest line between them, and pieces that cannot be boxed without catching a neighbour (diamonds, nested
  chevrons, diagonal splits, an L-shaped pipe) have outlines. Atlas1, Atlas3, Atlas4 and TextAtlas still come from
  the older 512 px pass [SOFT]: boxes from `scripts/extract_atlas_regions.py`, descriptions read by eye.
  The raw numbers, outlines included, are in `atlas-regions.json`.

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

How the full-resolution pass worked, and what the owner's review caught [HARD]:
- Draw a generous rectangle per piece, then snap it to the pixels inside at 2048 px. Snapping only shrinks a box,
  so a hint drawn too small stays clipped; draw them large but clear of neighbours.
- Snap at a low alpha (0.02), grown only through pixels connected to the piece: a 0.5 cutoff dropped soft edges
  (bolt halos, faded grunge borders, bevel strips), while a global low cutoff caught haze and neighbours.
- Where pieces touch (a gauge tile against a chain strip, grime drips under a scratched strip), cut both boxes on
  the emptiest row or column between them, then check every pair of boxes for overlap.
- Use an outline when a box cannot avoid a neighbour: a diamond's four corners, nested chevrons, a square or
  diamond split along a diagonal, an L-shaped pipe, a tile stepping around a strip's end.
- Pieces inside a sign or panel cannot be snapped (the background is opaque): measure them from the colour
  texture (dark pixels for a barcode, red for a prohibition circle) and give icons a square centred on the icon.
- Tiles laid edge to edge (four food icons on one strip, colour bands in one stripe row) get equal boxes from the
  strip they sit on, split at the real colour changes, not by eye.
- Draw review outlines just outside each box; a line on the box edge hides the piece's outermost pixels and makes
  the box look clipped.

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

Full size 2048 x 2048 px, 89 pieces. Re-catalogued at full resolution and checked piece by piece against the owner's markup. Boxes are snapped to every pixel with alpha above 0.02 that is connected to the piece, so faint edges are inside; where two pieces touch, the boundary sits on the emptiest line between them. `inside` rows are pieces within a larger sign (no transparent border to snap to; measured from the colour texture). Pieces whose box would overlap a neighbour have an outline instead (listed under the table; use the outline as the decal face's shape with the same points as UVs, then triangulate).

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0 | 0.8721 | 0.127 | 0.9971 | 260x256 | medical heart icon, pink rounded tile |
| 2 | 0.1289 | 0.8789 | 0.2461 | 0.9961 | 240x240 | disc icon: left arrow |
| 3 | 0.2539 | 0.8789 | 0.3711 | 0.9961 | 240x240 | disc icon: shopping cart with down arrow |
| 4 | 0.3789 | 0.8789 | 0.4961 | 0.9961 | 240x240 | disc icon: skip back |
| 5 | 0.5039 | 0.8789 | 0.6211 | 0.9961 | 240x240 | disc icon: play/pause |
| 6 | 0.6245 | 0.875 | 0.8516 | 1 | 465x256 | WARNING TIP OVER HAZARD sign (orange header, pictogram, small print) |
| 7 | 0.8794 | 0.897 | 0.9312 | 0.9766 | 106x163 | white left-pointing triangle |
| 8 | 0.9536 | 0.8306 | 0.9927 | 0.9878 | 80x322 | word RIGHT, vertical (letters rotated 90 degrees) |
| 9 | 0.0244 | 0.8149 | 0.0981 | 0.855 | 151x82 | words "medical kit", red, two lines |
| 10 | 0.1226 | 0.8267 | 0.2324 | 0.8643 | 225x77 | word LEFT, black |
| 11 | 0.2441 | 0.8271 | 0.3926 | 0.8657 | 304x79 | word DOWN, black |
| 12 | 0.4233 | 0.8257 | 0.4897 | 0.8643 | 136x79 | word UP, black |
| 13 | 0.5 | 0.8174 | 0.5957 | 0.8721 | 196x112 | HIGH VOLTAGE label, black on white |
| 14 | 0.6074 | 0.8179 | 0.8604 | 0.8677 | 518x102 | Engine / Remote Operated System label, white on black |
| 15 | 0 | 0.687 | 0.2251 | 0.813 | 461x258 | DANGER STRONG MAGNETIC FIELD sign |
| 16 | 0.2495 | 0.6904 | 0.3887 | 0.813 | 285x251 | flame hazard triangle, yellow |
| 17 | 0.4131 | 0.6899 | 0.5869 | 0.813 | 356x252 | CAUTION MOVING PARTS sign, yellow |
| 18 | 0.5991 | 0.6899 | 0.8071 | 0.813 | 426x252 | WARNING HIGH PRESSURE sign, yellow |
| 19 | 0.8228 | 0.6821 | 0.9878 | 0.8477 | 338x339 | explosive hazard diamond, orange, division 1 (diamond outline) (outline below) |
| 20 | 0.8135 | 0.6855 | 0.8691 | 0.7383 | 114x108 | three white dots, triangle cluster (box cut along the diamond edge) (outline below) |
| 21 | 0.9395 | 0.6787 | 0.9937 | 0.7227 | 111x90 | red ring (box cut along the diamond edge) (outline below) |
| 22 | 0 | 0.5571 | 0.3657 | 0.6733 | 749x238 | TYPE A label with barcode |
| 23 | 0.3872 | 0.6099 | 0.5928 | 0.6855 | 421x155 | RESTRICTED AREA sign, red |
| 24 | 0.6099 | 0.6191 | 0.6724 | 0.6816 | 128x128 | X-mark hazard square, orange |
| 25 | 0.688 | 0.6216 | 0.748 | 0.6816 | 123x123 | battery icon, red tile |
| 26 | 0.8628 | 0.6079 | 0.9263 | 0.6719 | 130x131 | square with corner triangle |
| 27 | 0.9365 | 0.6084 | 0.9927 | 0.6699 | 115x126 | small striped corner mark |
| 28 | 0.3857 | 0.5601 | 0.5488 | 0.5957 | 334x73 | word SIGNAL on white plate |
| 29 | 0.8555 | 0.5215 | 1 | 0.6021 | 296x165 | ENERGY SOURCE sign, yellow with lightning |
| 30 | 0.0078 | 0.4146 | 0.2681 | 0.5469 | 533x271 | COMPRESSED OXYGEN label, green |
| 31 | 0.2832 | 0.4224 | 0.5044 | 0.5376 | 453x236 | CAUTION BATTERY BOX label, red stripes |
| 32 | 0.5234 | 0.5078 | 0.5396 | 0.5415 | 33x69 | small red square |
| 33 | 0.5576 | 0.5088 | 0.5947 | 0.5405 | 76x65 | small red down-triangle |
| 34 | 0.5264 | 0.4355 | 0.5894 | 0.4985 | 129x129 | red prohibition circle (crossed out) |
| 35 | 0.5947 | 0.4707 | 0.7266 | 0.4858 | 270x31 | word WARNING, red outline letters |
| 36 | 0.5952 | 0.4561 | 0.6875 | 0.4639 | 189x16 | words DO NOT OPEN, red |
| 37 | 0.5947 | 0.4443 | 0.8047 | 0.4517 | 430x15 | words AUTHORIZED PERSONNEL ONLY, red |
| 38 | 0.8237 | 0.4492 | 0.8701 | 0.5132 | 95x131 | X icon in white frame |
| 39 | 0.873 | 0.4399 | 0.9512 | 0.5088 | 160x141 | white triangle outline |
| 40 | 0.9517 | 0.4404 | 0.9917 | 0.5112 | 82x145 | white bracket, left-pointing |
| 41 | 0.0127 | 0.3862 | 0.1284 | 0.4033 | 237x35 | text MXS-2859-B |
| 42 | 0.1353 | 0.3809 | 0.1533 | 0.4082 | 37x56 | digit 9 in a box |
| 43 | 0.061 | 0.3643 | 0.1284 | 0.3818 | 138x36 | text OB40-E |
| 44 | 0.0117 | 0.3394 | 0.0327 | 0.3569 | 43x36 | number 52 |
| 45 | 0.0391 | 0.3394 | 0.0811 | 0.3569 | 86x36 | text ACG |
| 46 | 0.0132 | 0.3086 | 0.0488 | 0.3257 | 73x35 | word NET |
| 47 | 0.0137 | 0.2852 | 0.0601 | 0.3027 | 95x36 | word TARE |
| 48 | 0.0137 | 0.2637 | 0.0737 | 0.2812 | 123x36 | text M.G.W. |
| 49 | 0.0132 | 0.2373 | 0.123 | 0.2495 | 225x25 | serial 20124D0000E4 |
| 50 | 0.1274 | 0.2373 | 0.1533 | 0.2495 | 53x25 | number 210 |
| 51 | 0.0127 | 0.2236 | 0.1123 | 0.2344 | 204x22 | words MADE IN SPACE |
| 52 | 0.1646 | 0.2881 | 0.4058 | 0.4028 | 494x235 | AMMUNITION label (heavy caliber, tare mass, warfare) |
| 53 | 0.4189 | 0.2866 | 0.4551 | 0.4121 | 74x257 | bullet / shell icon, white |
| 54 | 0.4648 | 0.354 | 0.5342 | 0.4141 | 142x123 | red warning triangle outline with ! |
| 55 | 0.5391 | 0.2515 | 0.7153 | 0.4282 | 361x362 | RADIOACTIVE II diamond, transport class 7 |
| 56 | 0.7236 | 0.3584 | 0.7959 | 0.4287 | 148x144 | food icon: knife and fork, grey tile |
| 57 | 0.7236 | 0.2881 | 0.7959 | 0.3584 | 148x144 | food icon: heat waves, cyan tile |
| 58 | 0.7236 | 0.2173 | 0.7959 | 0.2881 | 148x145 | food icon: wheat, orange tile |
| 59 | 0.7236 | 0.147 | 0.7959 | 0.2173 | 148x144 | food icon: mushroom, brown tile |
| 60 | 0.8008 | 0.1553 | 0.9951 | 0.4287 | 398x560 | DEHYDRATED MEAL PACK nutrition label |
| 61 | 0.1655 | 0.21 | 0.2383 | 0.2808 | 149x145 | icon: spider, purple tile |
| 62 | 0.2383 | 0.21 | 0.3096 | 0.2808 | 146x145 | icon: steak, red tile |
| 63 | 0.0059 | 0.1138 | 0.3052 | 0.2036 | 613x184 | SEEDS label with apple icon |
| 64 | 0.8101 | 0.1211 | 1 | 0.1528 | 389x65 | word SPORES, black on white |
| 65 | 0 | 0.0552 | 0.25 | 0.105 | 512x102 | orange and black hazard stripes |
| 66 | 0 | 0 | 0.25 | 0.0498 | 512x102 | yellow and black hazard stripes (tileable band) |
| 67 | 0.25 | 0 | 0.5 | 0.0498 | 512x102 | white and black stripes (tileable band) |
| 68 | 0.5 | 0 | 0.75 | 0.0498 | 512x102 | red and white stripes (tileable band) |
| 69 | 0.75 | 0 | 1 | 0.0498 | 512x102 | grey and black stripes (tileable band) |
| 70 | 0.9082 | 0.2422 | 0.9766 | 0.3105 | 140x140 | leaf icon, green tile (inside MEAL PACK) |
| 71 | 0.9082 | 0.1699 | 0.9766 | 0.2383 | 140x140 | QR code (inside MEAL PACK) |
| 72 | 0.0273 | 0.127 | 0.0898 | 0.1895 | 128x128 | apple icon, green tile (inside SEEDS) |
| 73 | 0.0449 | 0.5801 | 0.2056 | 0.6143 | 329x70 | barcode (inside TYPE A) |
| 74 | 0.627 | 0.8784 | 0.7031 | 0.9551 | 156x157 | pictogram: person pushing tipping crate (inside TIP OVER sign) |
| 75 | 0.0049 | 0.6929 | 0.0767 | 0.7646 | 147x147 | magnet pictogram (inside DANGER magnetic sign) |
| 76 | 0.103 | 0.3076 | 0.1519 | 0.3257 | 100x37 | weights: 39.480 KGS / 67.200 LBS |
| 77 | 0.1079 | 0.2852 | 0.1519 | 0.3027 | 90x36 | weights: 2.180 KGS / 4.810 LBS |
| 78 | 0.1016 | 0.2637 | 0.1509 | 0.2812 | 101x36 | weights: 20.800 KGS / 64.100 LBS |
| 79 | 0.5991 | 0.5684 | 0.6387 | 0.6069 | 81x79 | target icon quarter, top left |
| 80 | 0.6431 | 0.5635 | 0.6826 | 0.6035 | 81x82 | target icon quarter, top right |
| 81 | 0.6045 | 0.5254 | 0.6431 | 0.5645 | 79x80 | target icon quarter, bottom left |
| 82 | 0.6475 | 0.5239 | 0.6831 | 0.5591 | 73x72 | target icon quarter, bottom right |
| 83 | 0.7605 | 0.6091 | 0.8098 | 0.675 | 101x135 | chevron, left (one of a double chevron; outline, boxes overlap) (outline below) |
| 84 | 0.7947 | 0.6091 | 0.8435 | 0.675 | 100x135 | chevron, right (one of a double chevron; outline, boxes overlap) (outline below) |
| 85 | 0.7021 | 0.5303 | 0.7637 | 0.5918 | 126x126 | square split diagonally, upper-left half, cut along the diagonal (outline below) |
| 86 | 0.7021 | 0.5303 | 0.7637 | 0.5918 | 126x126 | square split diagonally, lower-right half, cut along the diagonal (outline below) |
| 87 | 0.7764 | 0.5234 | 0.8491 | 0.5962 | 149x149 | striped diamond, upper-right half, cut along the diagonal (outline below) |
| 88 | 0.7764 | 0.5234 | 0.8491 | 0.5962 | 149x149 | striped diamond, lower-left half, cut along the diagonal (outline below) |
| 89 | 0.5488 | 0.5601 | 0.5859 | 0.5957 | 76x73 | radio-wave icon, orange square (right end of the SIGNAL label) |

Outlines (UV points in order; the piece's quad or polygon uses the same points as positions and UVs):

- 19 explosive hazard diamond, orange, division 1 (diamond outline): (0.9048, 0.8477), (0.9878, 0.7642), (0.9048, 0.6821), (0.8228, 0.7642)
- 20 three white dots, triangle cluster (box cut along the diamond edge): (0.8135, 0.6855), (0.8691, 0.6855), (0.8691, 0.7122), (0.843, 0.7383), (0.8135, 0.7383)
- 21 red ring (box cut along the diamond edge): (0.9395, 0.6787), (0.9937, 0.6787), (0.9937, 0.7227), (0.9539, 0.7227), (0.9395, 0.7083)
- 83 chevron, left (one of a double chevron; outline, boxes overlap): (0.7605, 0.6091), (0.7839, 0.6091), (0.8098, 0.6414), (0.7839, 0.6746), (0.7605, 0.675), (0.7864, 0.6423)
- 84 chevron, right (one of a double chevron; outline, boxes overlap): (0.7947, 0.6091), (0.8176, 0.6091), (0.8435, 0.6418), (0.8176, 0.675), (0.7947, 0.675), (0.8206, 0.6423)
- 85 square split diagonally, upper-left half (cut along the diagonal): (0.7021, 0.5303), (0.7637, 0.5918), (0.7021, 0.5918)
- 86 square split diagonally, lower-right half (cut along the diagonal): (0.7021, 0.5303), (0.7637, 0.5303), (0.7637, 0.5918)
- 87 striped diamond, upper-right half (cut along the diagonal): (0.7764, 0.5962), (0.8491, 0.5962), (0.8491, 0.5234)
- 88 striped diamond, lower-left half (cut along the diagonal): (0.7764, 0.5962), (0.8491, 0.5234), (0.7764, 0.5234)

## Atlas3

Full size 2048 x 2048 px, 43 regions. Boxes checked by eye; descriptions are rough shape names.

Region 23 (the X panel) is not one symmetric decal [HARD, normal map read and seen in game]: the top and
right triangles are recessed (debossed) and the left and bottom triangles are raised (embossed), so a whole
square placed on a flat face looks lopsided. Pick one relief and build the X from four triangle faces that
all use that one triangle's UVs, with the world triangles rotated 90 degrees apart (tangent space follows the
UVs, so each rotated copy keeps correct lighting) [SOFT, UV recipe not yet seen in game]. Pixel corners
(2048 px atlas, y up from the bottom) and UVs; the opaque art is 477 px wide, so a 1.6 m X is
about 0.0034 m per px, and the whole region box is 481 px (do not scale the box to the face):

| piece | corner px | corner UV (u, v) |
|---|---|---|
| top triangle (debossed) | (176,1397) (591,1397) apex (383,1169) | (0.086,0.682) (0.289,0.682) (0.187,0.571) |
| bottom triangle (embossed) | (180,909) (587,909) apex (383,1131) | (0.088,0.444) (0.287,0.444) (0.187,0.552) |
| X centre | (383.5, 1153) | (0.187, 0.563) |

Size the finished decal to the open area of its face with margin; the test crate's 1.8 m square looked
oversized against a 2.4 m face with corner brackets.

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

Full size 2048 x 2048 px, 66 pieces, re-catalogued at full resolution. Panels are snapped to their pixels; single keys on a panel are `inside` rows (the panel is opaque around them, so the box is measured, not snapped) and can be used as small decals on their own.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.0034 | 0.8784 | 0.2471 | 0.9966 | 499x242 | panel: three rotary toggles with green LEDs |
| 2 | 0.2534 | 0.8784 | 0.4966 | 0.9966 | 498x242 | panel "Panel 1": 7 keys C1-C7 with LEDs |
| 3 | 0.5024 | 0.8789 | 0.6846 | 0.9966 | 373x241 | panel: 6 keys F1-F6 |
| 4 | 0.2754 | 0.9131 | 0.3008 | 0.9375 | 52x50 | key C1 [inside] |
| 5 | 0.3047 | 0.9131 | 0.3301 | 0.9375 | 52x50 | key C2 [inside] |
| 6 | 0.333 | 0.9131 | 0.3584 | 0.9375 | 52x50 | key C3 [inside] |
| 7 | 0.3623 | 0.9131 | 0.3877 | 0.9375 | 52x50 | key C4 [inside] |
| 8 | 0.3906 | 0.9131 | 0.416 | 0.9375 | 52x50 | key C5 [inside] |
| 9 | 0.4199 | 0.9131 | 0.4453 | 0.9375 | 52x50 | key C6 [inside] |
| 10 | 0.4482 | 0.9131 | 0.4736 | 0.9375 | 52x50 | key C7 [inside] |
| 11 | 0.5176 | 0.9414 | 0.5625 | 0.9707 | 92x60 | key F1 [inside] |
| 12 | 0.5723 | 0.9414 | 0.6172 | 0.9707 | 92x60 | key F2 [inside] |
| 13 | 0.625 | 0.9414 | 0.6699 | 0.9707 | 92x60 | key F3 [inside] |
| 14 | 0.5176 | 0.8926 | 0.5625 | 0.9219 | 92x60 | key F4 [inside] |
| 15 | 0.5723 | 0.8926 | 0.6172 | 0.9219 | 92x60 | key F5 [inside] |
| 16 | 0.625 | 0.8926 | 0.6699 | 0.9219 | 92x60 | key F6 [inside] |
| 17 | 0.6968 | 0.9424 | 0.7407 | 0.9863 | 90x90 | LED, green |
| 18 | 0.6968 | 0.8892 | 0.7407 | 0.9331 | 90x90 | LED, red |
| 19 | 0.752 | 0.8774 | 0.873 | 0.9976 | 248x246 | big round button, white |
| 20 | 0.877 | 0.8774 | 0.998 | 0.9976 | 248x246 | big round button, yellow |
| 21 | 0.0029 | 0.6279 | 0.1216 | 0.8716 | 243x499 | panel: keypad of 10 labelled keys |
| 22 | 0.0195 | 0.8232 | 0.0557 | 0.8584 | 74x72 | key Esc [inside] |
| 23 | 0.0693 | 0.8232 | 0.1055 | 0.8584 | 74x72 | key Spin [inside] |
| 24 | 0.0195 | 0.7783 | 0.0557 | 0.8135 | 74x72 | key If [inside] |
| 25 | 0.0693 | 0.7783 | 0.1055 | 0.8135 | 74x72 | key YoU [inside] |
| 26 | 0.0195 | 0.7334 | 0.0557 | 0.7686 | 74x72 | key Rea [inside] |
| 27 | 0.0693 | 0.7334 | 0.1055 | 0.7686 | 74x72 | key DTh [inside] |
| 28 | 0.0195 | 0.6885 | 0.0557 | 0.7236 | 74x72 | key iSHa [inside] |
| 29 | 0.0693 | 0.6885 | 0.1055 | 0.7236 | 74x72 | key VEan [inside] |
| 30 | 0.0195 | 0.6436 | 0.0557 | 0.6787 | 74x72 | key Ice [inside] |
| 31 | 0.0693 | 0.6436 | 0.1055 | 0.6787 | 74x72 | key dAy [inside] |
| 32 | 0.125 | 0.7607 | 0.187 | 0.8638 | 127x211 | rocker switch, red (left) |
| 33 | 0.1875 | 0.7607 | 0.2495 | 0.8638 | 127x211 | rocker switch, red (right) |
| 34 | 0.2534 | 0.6284 | 0.4966 | 0.8716 | 498x498 | panel: keys N1-N5, three knobs Field1/Field2/Subfield, three knobs WPS/MOD/SRC, slider |
| 35 | 0.2803 | 0.79 | 0.3057 | 0.8135 | 52x48 | key N1 [inside] |
| 36 | 0.3096 | 0.79 | 0.335 | 0.8135 | 52x48 | key N2 [inside] |
| 37 | 0.3379 | 0.79 | 0.3633 | 0.8135 | 52x48 | key N3 [inside] |
| 38 | 0.3672 | 0.79 | 0.3926 | 0.8135 | 52x48 | key N4 [inside] |
| 39 | 0.3955 | 0.79 | 0.4209 | 0.8135 | 52x48 | key N5 [inside] |
| 40 | 0.5083 | 0.7588 | 0.5605 | 0.8667 | 107x221 | slide switch with light, red |
| 41 | 0.5684 | 0.7588 | 0.6206 | 0.8667 | 107x221 | slide switch with light, green |
| 42 | 0.6289 | 0.7588 | 0.6812 | 0.8667 | 107x221 | slide switch with light, yellow |
| 43 | 0.689 | 0.7588 | 0.7412 | 0.8667 | 107x221 | slide switch with light, blue |
| 44 | 0.7539 | 0.7544 | 0.8711 | 0.8706 | 240x238 | big square button, white |
| 45 | 0.8789 | 0.7544 | 0.9961 | 0.8706 | 240x238 | big square button, yellow |
| 46 | 0.1274 | 0.6904 | 0.1846 | 0.7476 | 117x117 | round jack, white |
| 47 | 0.1904 | 0.6904 | 0.2476 | 0.7476 | 117x117 | round jack, blue |
| 48 | 0.1274 | 0.6274 | 0.1846 | 0.6846 | 117x117 | round jack, orange |
| 49 | 0.1904 | 0.6274 | 0.2476 | 0.6846 | 117x117 | round jack, green |
| 50 | 0.5044 | 0.6841 | 0.564 | 0.752 | 122x139 | rotary knob, grey |
| 51 | 0.5688 | 0.689 | 0.6289 | 0.749 | 123x123 | round push button, fluted |
| 52 | 0.6328 | 0.689 | 0.6924 | 0.7485 | 122x122 | round push button, plain |
| 53 | 0.6968 | 0.6763 | 0.7563 | 0.7476 | 122x146 | toggle lever (outline notched around the slot corner) (outline below) |
| 54 | 0.7681 | 0.6353 | 0.8716 | 0.7388 | 212x212 | round connector, 4 pins |
| 55 | 0.8838 | 0.6367 | 0.9893 | 0.7417 | 216x215 | round connector, 6 pins |
| 56 | 0.5181 | 0.6274 | 0.603 | 0.6802 | 174x108 | dark slot |
| 57 | 0.6167 | 0.6274 | 0.7031 | 0.6802 | 177x108 | slot with white light |
| 58 | 0.2534 | 0.4995 | 0.3716 | 0.6177 | 242x242 | EMERGENCY STOP button |
| 59 | 0.3818 | 0.5503 | 0.4497 | 0.6187 | 139x140 | square push button (left) |
| 60 | 0.4556 | 0.5508 | 0.5234 | 0.6187 | 139x139 | square push button (right) |
| 61 | 0.5303 | 0.5459 | 0.6113 | 0.6196 | 166x151 | round jack, white (large) |
| 62 | 0.6182 | 0.5459 | 0.6992 | 0.6196 | 166x151 | round jack, orange and green (large) |
| 63 | 0.7051 | 0.5459 | 0.7861 | 0.6196 | 166x151 | round jack, red (large) |
| 64 | 0.7915 | 0.5459 | 0.8726 | 0.6196 | 166x151 | round jack, cyan (large) |
| 65 | 0.8804 | 0.5015 | 0.9937 | 0.623 | 232x249 | large socket, open bore |
| 66 | 0.877 | 0.3779 | 0.998 | 0.4995 | 248x249 | large socket, closed with clips, red ring |

Outlines (UV points in order; the piece's quad or polygon uses the same points as positions and UVs):

- 53 toggle lever (outline notched around the slot corner): (0.7031, 0.6763), (0.7563, 0.6763), (0.7563, 0.7476), (0.6968, 0.7476), (0.6968, 0.6802), (0.7031, 0.6802)

## Decals_Atlas_A_01

Full size 2048 x 2048 px, 61 pieces, re-catalogued at full resolution and checked against the owner's markup. Boxes include the faint faded edges connected to each piece. Rows 59-61 are combined strips (a riveted band and a double strip); their parts are also listed on their own for variety.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.0034 | 0.9712 | 0.0278 | 0.9971 | 50x53 | bolt head 1: hex nut, slot |
| 2 | 0.0332 | 0.9707 | 0.0605 | 0.998 | 56x56 | bolt head 2: round with cross |
| 3 | 0.0635 | 0.9697 | 0.0928 | 0.999 | 60x60 | bolt head 3: dome in recessed ring |
| 4 | 0.0957 | 0.9722 | 0.123 | 0.9966 | 56x50 | bolt head 4: hex nut |
| 5 | 0.127 | 0.9717 | 0.1538 | 0.9971 | 55x52 | bolt head 5: oval slotted |
| 6 | 0.1587 | 0.9712 | 0.1851 | 0.9976 | 54x54 | bolt head 6: round domed |
| 7 | 0.1904 | 0.9727 | 0.2158 | 0.9961 | 52x48 | bolt head 7: hex socket |
| 8 | 0.2217 | 0.9717 | 0.2471 | 0.9971 | 52x52 | bolt head 8: slotted screw |
| 9 | 0.2505 | 0.9697 | 0.2803 | 0.999 | 61x60 | bolt head 9: Phillips screw |
| 10 | 0.2842 | 0.9717 | 0.3096 | 0.9971 | 52x52 | bolt head 10: plain round dome |
| 11 | 0.313 | 0.9692 | 0.3428 | 0.999 | 61x61 | bolt head 11: hex socket in a ring |
| 12 | 0.3438 | 0.9688 | 0.5312 | 1 | 384x64 | scratched light metal strip (one opaque rectangle; the scratches are in its colour) |
| 13 | 0.4121 | 0.8672 | 0.6489 | 0.9688 | 485x208 | dark grime drips overlay |
| 14 | 0.3262 | 0.8535 | 0.3916 | 0.8965 | 134x88 | grime blob |
| 15 | 0.021 | 0.8574 | 0.2637 | 0.9609 | 497x212 | scattered scratch specks |
| 16 | 0.6636 | 0.8896 | 0.7109 | 0.9883 | 97x202 | tall pill plate |
| 17 | 0.7324 | 0.9575 | 0.8936 | 0.9795 | 330x45 | thin bar, top |
| 18 | 0.7266 | 0.8965 | 0.8979 | 0.9185 | 351x45 | thin bar, middle |
| 19 | 0.7319 | 0.832 | 0.895 | 0.856 | 334x49 | thin bar, bottom |
| 20 | 0.9102 | 0.8281 | 0.9966 | 0.9849 | 177x321 | tall rounded panel |
| 21 | 0 | 0.7812 | 0.125 | 0.8438 | 256x128 | pipe cross fitting |
| 22 | 0.1338 | 0.7935 | 0.1777 | 0.8315 | 90x78 | small square plate |
| 23 | 0.1252 | 0.7434 | 0.2244 | 0.8435 | 203x205 | pipe elbow (L-shaped outline; its box would cover the small square plate) (outline below) |
| 24 | 0.0024 | 0.7241 | 0.0591 | 0.7793 | 116x113 | rounded square plate |
| 25 | 0.0781 | 0.7261 | 0.1084 | 0.7725 | 62x95 | small rounded square |
| 26 | 0.2705 | 0.7041 | 0.3145 | 0.8291 | 90x256 | scratch line |
| 27 | 0.5015 | 0.6274 | 0.6543 | 0.8379 | 313x431 | frame with window |
| 28 | 0.6636 | 0.7822 | 0.7134 | 0.874 | 102x188 | tall rounded plate, notched top |
| 29 | 0.6704 | 0.6318 | 0.7056 | 0.7759 | 72x295 | tall pill plate, slim |
| 30 | 0.7188 | 0.5273 | 1 | 0.8125 | 576x584 | vent grille |
| 31 | 0.3135 | 0.5928 | 0.4043 | 0.6885 | 186x196 | ring disc |
| 32 | 0.4141 | 0.5947 | 0.4946 | 0.6865 | 165x188 | rounded square plate, large |
| 33 | 0.3525 | 0.4097 | 0.4302 | 0.5903 | 159x370 | tall chamfered plate |
| 34 | 0.4429 | 0.4102 | 0.5264 | 0.5894 | 171x367 | tall octagon plate with side notches |
| 35 | 0.729 | 0.4404 | 0.7715 | 0.5273 | 87x178 | zip-pull / pipe end |
| 36 | 0.3442 | 0.3438 | 0.7812 | 0.3955 | 895x106 | chain lattice strip |
| 37 | 0 | 0.4692 | 0.3066 | 0.6875 | 628x447 | DANGER HIGH VOLTAGE sign (whole) |
| 38 | 0.0034 | 0.3125 | 0.1846 | 0.4648 | 371x312 | high-voltage warning triangle, yellow |
| 39 | 0.1875 | 0.3125 | 0.3442 | 0.4688 | 321x320 | pressure gauge, bar 0-6, coloured zones |
| 40 | 0.7812 | 0.3125 | 1 | 0.5278 | 448x441 | heart on grunge tile, red |
| 41 | 0.5391 | 0.5596 | 0.6191 | 0.6167 | 164x117 | circuit logo sticker, green |
| 42 | 0.5591 | 0.4575 | 0.5938 | 0.5474 | 71x184 | vertical text GOOD (dark) |
| 43 | 0.5581 | 0.4141 | 0.5947 | 0.4526 | 75x79 | letters AI, green |
| 44 | 0.646 | 0.563 | 0.6987 | 0.6147 | 108x106 | chevron badge, triple |
| 45 | 0.646 | 0.4873 | 0.6987 | 0.5396 | 108x107 | chevron badge, double |
| 46 | 0.6465 | 0.4116 | 0.6987 | 0.4639 | 107x107 | chevron badge, single |
| 47 | 0.0176 | 0.5977 | 0.2891 | 0.6738 | 556x156 | DANGER red oval on black band (inside sign) |
| 48 | 0.0469 | 0.4961 | 0.2617 | 0.5859 | 440x184 | words HIGH VOLTAGE (inside sign) |
| 49 | 0 | 0.2954 | 1 | 0.3086 | 2048x27 | full-width plain strip (top) |
| 50 | 0 | 0.2744 | 1 | 0.2871 | 2048x26 | row of round dots (rivets), full width |
| 51 | 0 | 0.2554 | 1 | 0.269 | 2048x28 | panel seam, V-groove (used for seams) |
| 52 | 0 | 0.2329 | 1 | 0.2461 | 2048x27 | full-width plain strip |
| 53 | 0 | 0.2119 | 1 | 0.2246 | 2048x26 | row of round dots (rivets), full width, second |
| 54 | 0 | 0.1929 | 1 | 0.2065 | 2048x28 | panel seam, V-groove (used on the gatling turret) |
| 55 | 0 | 0.1392 | 1 | 0.1753 | 2048x74 | rolled-edge band, full width |
| 56 | 0.0288 | 0.0898 | 0.9937 | 0.1084 | 1976x38 | grime speck row |
| 57 | 0 | 0.0449 | 1 | 0.0552 | 2048x21 | full-width thin strip |
| 58 | 0 | 0.0073 | 1 | 0.0239 | 2048x34 | panel seam with one-sided bevel |
| 59 | 0 | 0.2554 | 1 | 0.3086 | 2048x109 | riveted band: strip + rivet row + strip as one decal (49+50+51) |
| 60 | 0 | 0.1929 | 1 | 0.2461 | 2048x109 | riveted band, second copy (52+53+54) |
| 61 | 0 | 0.0073 | 1 | 0.0552 | 2048x98 | double strip: thin strip + bevelled seam as one decal (57+58) |

Outlines (UV points in order; the piece's quad or polygon uses the same points as positions and UVs):

- 23 pipe elbow (L-shaped outline; its box would cover the small square plate): (0.1252, 0.7434), (0.1965, 0.7439), (0.2092, 0.7483), (0.2175, 0.7556), (0.2219, 0.7629), (0.2244, 0.7727), (0.2244, 0.8435), (0.2205, 0.8435), (0.2117, 0.8435), (0.2117, 0.7742), (0.2083, 0.7644), (0.2024, 0.759), (0.1951, 0.7566), (0.1252, 0.7566)

**Panel lines** [HARD, read from the `_ng` and `_cm` textures, used on a model]: strips 51, 54 and 58 are
panel seams. Their colour is a flat mid grey and the line comes from the normal map, so put them on
`PanelingColorable` (takes the block's paint) for colorable surfaces or `PanelingDarker` for dark fixed metal,
not on `Decals` (which would paint a grey band). Map V across the band (about 0.025 to 0.03 m wide) and U along
its length; U past 1 wraps within the same strip, so a long ring or seam can use `u = length * 0.5`. Build the
band from many short quads that follow the surface (rings, meridians, radial lines), 3 to 4 mm off it.
**Joins and ends** [HARD, rendered; owner asked]: a stem that stops square at a cross seam looks pasted on. Stop
the stem's band half a cross-width short, then close it with two triangles meeting at a tip on the cross
seam's centre line, tip UV at the middle of the strip (`v = (v0 + v1) / 2`), side corners at `v0` and `v1`.
Give the tip its own U as well (offset by its distance along the seam times the U scale): with one U for all
three corners the triangle has no tangent direction and the groove renders flipped (seen in a render).
That compresses each half of the groove into a 45-degree mitre against the cross groove. Lift the stem about
1 mm more than the cross seam so it draws on top. Free ends get the same pointed cap, extended half a width
past the end. Polyline corners mitre by themselves when each row's side vector comes from the averaged tangent.

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

