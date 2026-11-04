# Decal atlas region maps

Where each piece sits in the vanilla decal atlases, so a decal quad can be UV-mapped to a known piece instead of guessing.

- UV values use Blender's convention: (0, 0) is the **bottom left** of the image, so they can be typed straight into the UV editor.
- Boxes are bounding boxes of the piece's pixels in the `_alphamask` texture, reported as fractions of the full image.
- `px` is the piece size at the texture's full resolution.
- Ids change when an atlas is re-catalogued. When someone asks for a piece by number, look it up in this file
  every time, and never reuse an id or box from an earlier session [owner: a decal placed from a stale id was
  the wrong piece]. Confirm by the piece's description too.
- Every atlas was re-catalogued at its full resolution and checked piece by piece against the owner's markup
  [HARD]: faint faded edges are included, touching pieces are split on the emptiest line between them, pieces
  that cannot be boxed without catching a neighbour (diamonds, nested chevrons, diagonal splits, an L-shaped
  pipe, the X-panel triangles) have outlines, and a repeating pattern or a multi-part panel is one decal.
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

**Cropping a piece without Pillow** (for a contact sheet or a pixel check) [HARD, run on Windows]: PowerShell's
`System.Drawing` reads the asset TIFs (`<SEUT Assets>\Textures\Models\Cubes\*.TIF`, 2048 px). Pixel rows count
from the top, so a box's top row is `(1 - v1) * 2048`:

```powershell
Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Image]::FromFile('C:\SE_Assets\Textures\Models\Cubes\Decals_Atlas_A_01_cm.TIF')
$box = [System.Drawing.Rectangle]::new(0, 1689, 2048, 74)        # piece 55: x, top row, width, height
$out = [System.Drawing.Bitmap]::new($box.Width, $box.Height, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
[System.Drawing.Graphics]::FromImage($out).DrawImage($src, [System.Drawing.Rectangle]::new(0, 0, $box.Width, $box.Height), $box, [System.Drawing.GraphicsUnit]::Pixel)
$out.Save("$env:TEMP\piece55_cm.png", [System.Drawing.Imaging.ImageFormat]::Png)
```

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

Full size 2048 x 2048 px, 12 pieces, re-catalogued at full resolution and checked against the owner's markup. The schematic panel (11) is one decal: its plates, rings, bars, discs and cable run are not separate pieces. The X inside the octagon frame (8) also works on its own. Repeating patterns (five dots, six slots, 25 holes) are one decal each.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.0002 | 0.7371 | 0.3918 | 0.9998 | 802x538 | big plate with four tall slots (L-shaped outline; the six-slot comb sits in its corner) (outline below) |
| 2 | 0.4009 | 0.6113 | 0.4761 | 0.9976 | 154x791 | lattice truss column, four cells |
| 3 | 0.6807 | 0.8076 | 0.9956 | 0.9829 | 645x359 | louvre: horizontal slats in a rounded frame (the slats are in the normal map; the colour map is plain) |
| 4 | 0.5205 | 0.8208 | 0.6704 | 0.9702 | 307x306 | five-dot pattern |
| 5 | 0.2993 | 0.6162 | 0.3877 | 0.8354 | 181x449 | comb of six tall thin slots |
| 6 | 0.4888 | 0.6162 | 0.7134 | 0.7886 | 460x353 | plain scratched plate |
| 7 | 0.7549 | 0.5044 | 0.9976 | 0.7471 | 497x497 | octagon frame with an X (hazard-style) |
| 8 | 0.7939 | 0.543 | 0.9585 | 0.708 | 337x338 | X from the octagon frame, on its own [inside] |
| 9 | 0.001 | 0.6299 | 0.2773 | 0.7109 | 566x166 | field of 25 round holes with rims |
| 10 | 0 | 0.519 | 0.7085 | 0.5996 | 1451x165 | hazard stripe, grey and black (the `Atlas1` colour map is neutral grey; for yellow use Atlas2 66) |
| 11 | 0.0151 | 0.1211 | 0.9741 | 0.501 | 1964x778 | schematic panel (one decal: side plates, four rings, bars, two discs, cable run) |
| 12 | 0 | 0.0234 | 1 | 0.0562 | 2048x67 | thin full-width strip |

Outlines (UV points in order; the piece's polygon uses the same points as positions and UVs):

- 1 big plate with four tall slots (L-shaped outline; the six-slot comb sits in its corner): (0.0002, 0.7371), (0.281, 0.7371), (0.2815, 0.844), (0.3918, 0.844), (0.3918, 0.9998), (0.0002, 0.9998)

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

Full size 2048 x 2048 px, 46 pieces, re-catalogued at full resolution and checked against the owner's markup. The 6 x 10 rivet grid (46) is one decal.

The X panel is four independent decals (42-45), not one [owner; HARD, normal map read and seen in game]:
the top (42) and right (44) triangles are recessed (debossed) and the left (43) and bottom (45) are raised
(embossed), each pair at two different depths (deeper: 42 and 43) [SOFT, depth from edge steepness]. A whole
square placed on a flat face looks lopsided. For a symmetric X, pick one triangle and build the X from four
triangle faces that all use its outline as UVs, with the world triangles rotated 90 degrees apart (tangent
space follows the UVs, so each rotated copy keeps correct lighting) [SOFT, UV recipe not yet seen in game].
The four triangles together span 477 px of opaque art, so a 1.6 m X is about 0.0034 m per px.

Size the finished decal to the open area of its face with margin; the test crate's 1.8 m square looked
oversized against a 2.4 m face with corner brackets.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.3823 | 0.8154 | 0.4941 | 0.9966 | 229x371 | panel with dark rectangular window |
| 2 | 0.7529 | 0.8164 | 0.9331 | 0.9966 | 369x369 | large round speaker grille |
| 3 | 0.9404 | 0.8179 | 0.998 | 0.9976 | 118x368 | tall slot with knob and dot |
| 4 | 0.0088 | 0.8218 | 0.1772 | 0.9902 | 345x345 | round disc with centre hole and rings |
| 5 | 0.1929 | 0.8188 | 0.3071 | 0.9922 | 234x355 | plate with centre dot and a dark notched slot |
| 6 | 0.3257 | 0.8174 | 0.3623 | 0.9946 | 75x363 | slim dark trapezoid slot |
| 7 | 0.5029 | 0.8193 | 0.6211 | 0.9927 | 242x355 | clamp block with two rounded bars |
| 8 | 0.6504 | 0.8179 | 0.731 | 0.9946 | 165x362 | trapezoid wedge |
| 9 | 0.1782 | 0.688 | 0.248 | 0.8105 | 143x251 | small plain rectangle |
| 10 | 0.3774 | 0.6899 | 0.4976 | 0.8105 | 246x247 | disc with concentric rings |
| 11 | 0.5078 | 0.6904 | 0.5552 | 0.8096 | 97x244 | vertical strip with three holes |
| 12 | 0.5703 | 0.6904 | 0.6177 | 0.8096 | 97x244 | small rounded pill |
| 13 | 0.7554 | 0.6909 | 0.9326 | 0.8091 | 363x242 | plate with six round dimples |
| 14 | 0.9399 | 0.752 | 0.999 | 0.8105 | 121x120 | small round dimple |
| 15 | 0.0049 | 0.6929 | 0.0586 | 0.8071 | 110x234 | small dark slot pill |
| 16 | 0.0864 | 0.6924 | 0.1631 | 0.8076 | 157x236 | small tab with hex bolt |
| 17 | 0.2554 | 0.6929 | 0.3706 | 0.8076 | 236x235 | round cap with cross |
| 18 | 0.6235 | 0.6982 | 0.7515 | 0.7979 | 262x204 | horizontal clamp bar |
| 19 | 0.9463 | 0.689 | 0.999 | 0.749 | 108x123 | small slot with edge |
| 20 | 0.0049 | 0.4429 | 0.0586 | 0.6826 | 110x491 | tall dark slot |
| 21 | 0.3164 | 0.4404 | 0.373 | 0.6846 | 116x500 | tall plain strip |
| 22 | 0.3804 | 0.4429 | 0.6196 | 0.6821 | 490x490 | large panel with mesh grille and frame |
| 23 | 0.6289 | 0.4419 | 0.6831 | 0.6831 | 111x494 | tall narrow fluted bar |
| 24 | 0.6924 | 0.4424 | 0.8076 | 0.6826 | 236x492 | slatted vent (two groups) |
| 25 | 0.8184 | 0.4424 | 0.8696 | 0.6831 | 105x493 | tall panel with inset square |
| 26 | 0.8823 | 0.5645 | 0.9307 | 0.6851 | 99x247 | small pill |
| 27 | 0.9443 | 0.5679 | 0.9951 | 0.6826 | 104x235 | pill with cross bar |
| 28 | 0.8813 | 0.3818 | 0.9937 | 0.4937 | 230x229 | shallow round dish |
| 29 | 0.0024 | 0.2524 | 0.1851 | 0.4355 | 374x375 | triangular corner plate with diagonal slots |
| 30 | 0.1919 | 0.2544 | 0.3706 | 0.4336 | 366x367 | square plate, rounded corners, two slots |
| 31 | 0.3799 | 0.2559 | 0.4951 | 0.4312 | 236x359 | panel with hinge notch |
| 32 | 0.5049 | 0.2534 | 0.6201 | 0.4331 | 236x368 | panel with centre slot |
| 33 | 0.6245 | 0.2544 | 0.7505 | 0.4331 | 258x366 | panel with two inset blocks and a dot |
| 34 | 0.7637 | 0.2554 | 0.8613 | 0.4321 | 200x362 | tall panel with bands and four screws |
| 35 | 0.8867 | 0.2617 | 0.9883 | 0.3633 | 208x208 | square recess (pyramid) |
| 36 | 0.0088 | 0.189 | 0.4912 | 0.2485 | 988x122 | long trapezoid bar |
| 37 | 0.5039 | 0.1289 | 0.6211 | 0.2461 | 240x240 | 5x5 grid of holes |
| 38 | 0.6274 | 0.1274 | 0.8726 | 0.2476 | 502x246 | wide frame with dark slot |
| 39 | 0.8848 | 0.0073 | 0.9902 | 0.2432 | 216x483 | tall pill with dark vent slits |
| 40 | 0.0078 | 0.0088 | 0.1172 | 0.1777 | 224x346 | small plate with two holes |
| 41 | 0.1445 | 0.0068 | 0.2222 | 0.1797 | 159x354 | small tall window |
| 42 | 0.0867 | 0.572 | 0.2878 | 0.6819 | 412x225 | X-panel triangle, top (debossed, deeper; outline) (outline below) |
| 43 | 0.071 | 0.4607 | 0.1775 | 0.6643 | 218x417 | X-panel triangle, left (embossed, deeper; outline) (outline below) |
| 44 | 0.1975 | 0.4607 | 0.304 | 0.6643 | 218x417 | X-panel triangle, right (debossed, shallower; outline) (outline below) |
| 45 | 0.0891 | 0.4446 | 0.2859 | 0.5515 | 403x219 | X-panel triangle, bottom (embossed, shallower; outline) (outline below) |
| 46 | 0.2617 | 0.0063 | 0.3633 | 0.1807 | 208x357 | rivet pattern, 6 x 10 grid |

Outlines (UV points in order; the piece's polygon uses the same points as positions and UVs):

- 42 X-panel triangle, top (debossed, deeper; outline): (0.0867, 0.6707), (0.0881, 0.6658), (0.0916, 0.6609), (0.1755, 0.5769), (0.1843, 0.572), (0.1907, 0.572), (0.1995, 0.5769), (0.2834, 0.6609), (0.2869, 0.6658), (0.2878, 0.6702), (0.2878, 0.6746), (0.2849, 0.6785), (0.28, 0.6809), (0.2742, 0.6819), (0.1008, 0.6819), (0.095, 0.6809), (0.0901, 0.6785), (0.0872, 0.6746)
- 43 X-panel triangle, left (embossed, deeper; outline): (0.071, 0.4661), (0.0725, 0.4626), (0.0745, 0.4612), (0.0769, 0.4607), (0.0813, 0.4626), (0.1755, 0.5569), (0.1775, 0.5608), (0.1775, 0.5642), (0.1755, 0.5681), (0.0847, 0.6589), (0.0813, 0.6624), (0.0769, 0.6643), (0.0735, 0.6633), (0.071, 0.6589)
- 44 X-panel triangle, right (debossed, shallower; outline): (0.1975, 0.5608), (0.1995, 0.5569), (0.2937, 0.4626), (0.2991, 0.4607), (0.3025, 0.4626), (0.304, 0.4661), (0.304, 0.5642), (0.304, 0.6589), (0.3015, 0.6633), (0.2981, 0.6643), (0.2937, 0.6624), (0.1995, 0.5681), (0.1975, 0.5642)
- 45 X-panel triangle, bottom (embossed, shallower; outline): (0.0891, 0.4519), (0.093, 0.447), (0.1023, 0.4446), (0.2727, 0.4446), (0.28, 0.446), (0.2839, 0.4485), (0.2859, 0.4519), (0.2849, 0.4583), (0.281, 0.4646), (0.2, 0.5457), (0.1926, 0.5505), (0.1858, 0.5515), (0.1794, 0.5491), (0.175, 0.5457), (0.094, 0.4646), (0.0896, 0.4578)

## Atlas4

Full size 1024 x 1024 px, 6 pieces, re-catalogued at full resolution and checked against the owner's markup. The four trapezoid caps (1) are one decal that repeats along a line; the five bands tile horizontally.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.0068 | 0.6953 | 0.9932 | 0.7725 | 1010x79 | row of four trapezoid caps, alternating narrow and wide tops (repeats along a line) |
| 2 | 0 | 0.5693 | 1 | 0.6689 | 1024x102 | wide band with a row of eight bolt holes (tileable) |
| 3 | 0 | 0.4834 | 1 | 0.5166 | 1024x34 | thin double strip with a dark centre line (tileable) |
| 4 | 0 | 0.3359 | 1 | 0.4355 | 1024x102 | band with dark edge lines and a stained light centre (tileable) |
| 5 | 0 | 0.124 | 1 | 0.3027 | 1024x183 | wide band of perforated bare metal: raised rims round a field of small round holes (tileable) |
| 6 | 0 | 0.0166 | 1 | 0.1006 | 1024x86 | band with raised square blocks, gear-like (tileable) |

**Repeats along bands 2 and 6** [HARD, read from `Atlas4_Colorable_ng`]: band 2's holes are recessed, one every
128 px centred at `58 + 128 j`; band 6's blocks are raised, one every 128 px, about 62 px wide, centred at
`63 + 128 j`, on a raised base band, and read like a gear rim. Band 6's pitch is `1.49` times its height, so
stretch U a little to land one block per facet (or per two) of a faceted cylinder: a block on a fold bends.

**Band 5 is bare metal in every colour variant** [HARD, read from the `_cm` maps]: its colour averages 154 of
255 in `Atlas4_VeryDark`, 165 in `_Darker` and 196 in `_Colorable`, with metalness (alpha) 202, so
`Atlas4_VeryDark` 5 renders as light perforated steel. Band 6 does follow the variant (60, 93 and 181).

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
| 50 | 0 | 0.2744 | 1 | 0.2871 | 2048x26 | row of round rivets that read raised under light from above, full width (see "Riveted bands") |
| 51 | 0 | 0.2554 | 1 | 0.269 | 2048x28 | panel seam, V-groove (used for seams) |
| 52 | 0 | 0.2329 | 1 | 0.2461 | 2048x27 | full-width plain strip |
| 53 | 0 | 0.2119 | 1 | 0.2246 | 2048x26 | row of round recessed dimples, full width (see "Riveted bands") |
| 54 | 0 | 0.1929 | 1 | 0.2065 | 2048x28 | panel seam, V-groove (used on the gatling turret) |
| 55 | 0 | 0.1392 | 1 | 0.1753 | 2048x74 | weld bead, full width (capped ends: repeat texels 62 to 1931, "Weld lines") |
| 56 | 0.0288 | 0.0898 | 0.9937 | 0.1084 | 1976x38 | grime speck row |
| 57 | 0 | 0.0449 | 1 | 0.0552 | 2048x21 | full-width thin strip |
| 58 | 0 | 0.0073 | 1 | 0.0239 | 2048x34 | panel seam with one-sided bevel |
| 59 | 0 | 0.2554 | 1 | 0.3086 | 2048x109 | riveted band, raised rivets: strip + rivet row + strip as one decal (49+50+51) |
| 60 | 0 | 0.1929 | 1 | 0.2461 | 2048x109 | dimpled band, recessed dimples: strip + dimple row + strip as one decal (52+53+54) |
| 61 | 0 | 0.0073 | 1 | 0.0552 | 2048x98 | double strip: thin strip + bevelled seam as one decal (57+58) |

Outlines (UV points in order; the piece's quad or polygon uses the same points as positions and UVs):

- 23 pipe elbow (L-shaped outline; its box would cover the small square plate): (0.1252, 0.7434), (0.1965, 0.7439), (0.2092, 0.7483), (0.2175, 0.7556), (0.2219, 0.7629), (0.2244, 0.7727), (0.2244, 0.8435), (0.2205, 0.8435), (0.2117, 0.8435), (0.2117, 0.7742), (0.2083, 0.7644), (0.2024, 0.759), (0.1951, 0.7566), (0.1252, 0.7566)

**Panel lines** [HARD, read from the `_ng` and `_cm` textures, used on a model]: strips 51, 54 and 58 are
panel seams. Their colour is a flat mid grey and the line comes from the normal map, so put them on
`PanelingColorable` (takes the block's paint) for colorable surfaces or `PanelingDarker` for dark fixed metal,
not on `Decals` (which would paint a grey band). Map V across the band (about 0.025 to 0.03 m wide on hull-sized plates; scale it with the part, since
on a part about 1.3 m across 2 cm read heavy and 1 cm right [SOFT, one user's call]) and U along
its length; U past 1 wraps within the same strip, so a long ring or seam can use `u = length * 0.5`. Build the
band from many short quads that follow the surface (rings, meridians, radial lines), 1.5 mm off it like every
decal (SKILL.md). On a curved surface a flat quad's middle sits about `length² / (8 × radius)` below its
corners, so keep the quads short enough that this sag stays well under the offset, and check with a ray cast
(`bpy-recipes.md`, "Decal offset").
**Joins and ends** [HARD, rendered; owner asked]: a stem that stops square at a cross seam looks pasted on. Stop
the stem's band half a cross-width short, then close it with two triangles meeting at a tip on the cross
seam's centre line, tip UV at the middle of the strip (`v = (v0 + v1) / 2`), side corners at `v0` and `v1`.
Give the tip its own U as well (offset by its distance along the seam times the U scale): with one U for all
three corners the triangle has no tangent direction and the groove renders flipped (seen in a render).
That compresses each half of the groove into a 45-degree mitre against the cross groove. Lift the stem about
1 mm more than the cross seam so it draws on top. Free ends get the same pointed cap, extended half a width
past the end. Polyline corners mitre by themselves when each row's side vector comes from the averaged tangent.
The same cap works at any angle [HARD, rendered; owner: square T-ends were wrong]: end the stem's centre line on
the cross seam's centre line, stop each side of the band where it reaches the cross seam's near edge (a line in
the face), and close the end with the tip at the centre-line point. A stem that runs into the corner of two
seams (a diagonal into a T) stops each side on whichever near edge it reaches last and puts its tip where the
centre lines cross. A square end, even one cut flush along the cross seam, still reads as pasted on.

**Groove direction** [HARD, read from the `_ng` texture of `Decals_Atlas_A_01`; owner saw the jog]: piece 51's
groove is lopsided. Across the strip its normal map tilts towards `v1` over the first 11 px and towards `v0`
over the last 16 px, so the wide wall is on the `v1` side. Two strips laid in opposite directions meet with a
visible jog, most often where one seam wraps from one face onto the next. Pick one rule in world space and use it
for the whole model, for example `v1` towards the rear for seams running across the block, `v1` towards +X for
seams running front to back, and the same side (inside or outside) all the way round a closed outline. Apply it
when building each strip (reverse the polyline when its first segment's `v1` side breaks the rule), then check
it: from each seam face's positions and UVs, solve the world direction V increases in and count the faces that
break the rule. Piece 58 is one-sided by design; measure 54 the same way before using it.

**Seams over edges and bevels** [HARD, rendered; owner saw a gap at every edge]: a seam that stops short of an
edge leaves a gap at each bevel, and it shows from most angles. Run every seam that crosses a plate edge right
up to the edge, and carry it on across the next face at the same place along the edge (over a chamfer face too)
so the plates read as one cut. To follow the bevel, draw the strip flat up to the sharp edge, cut its last 4 cm
into 1 cm steps, then move each vertex to the nearest point of the bevelled mesh
(`BVHTree.FromObject(obj, depsgraph).find_nearest` on the object with its Bevel modifier, in object space) and
lift it 1.5 mm along that point's normal. The sharp corner lands on the middle of the bevel, so the strips from
the two faces meet there. Treat a vertex more than 3 cm from the surface as an error and report it. A seam end
that sits on a face edge needs no cap.

**Riveted bands** [HARD, read from the `_ng` and alpha textures; owner saw the difference]: 50 and 53 look
alike in colour but not in relief. In 53 (and band 60) both normal channels tilt in towards each dot, as in
`Atlas4` piece 2's bolt holes and opposite to piece 6's raised blocks, so they are recessed dimples. In 50 (and
band 59) the green channel tilts out like a dome, so with light from above or below the heads read raised; the
red channel still tilts in, so light from the side makes them read recessed [SOFT: 50 looks like 53 flipped top
to bottom with its green values left as they were]. Use 59 for raised rivets, 60 for dimples. Both rows: 23 px
dots every 68.27 px (30 per U span, the first centred at 6 px), filling the 26 px strip and centred in the
109 px band; the ends match, so they wrap cleanly. The band's pitch is `0.626` times its width (at `0.171` m
wide, one rivet per side of a 48-sided, 0.82 m radius drum).

**Weld lines** [HARD, read from the A_01 and A_02 colour, normal and alpha textures, and rendered; SOFT until
seen in game]: piece 55 is a weld bead (overlapping ripples in the colour and normal maps, ragged alpha edges),
and the bead sits at the same place on the `Decals_Atlas_A_02` sheet, so it works on `PanelingDarker` (dark
metal), `PanelingColorable` (paint) and `Decals`; compare them in the first render. Map V across the bead and U
along it, as for panel lines. At about 5 cm wide one U span covers about 1.4 m (the strip is 2048 x 74 px).

- **Repeat one way, from a window inside the capped ends** [owner: mirrored spans read as breaks where the bead
  turns round]. The ripples point one way, so alternate spans run backwards (U 0 to 1, then 1 to 0) show a break
  every span. The piece's ends are capped: texels 0 and 2047 are a crease in the normal map and the
  `PanelingDarker` colour fades dark from about texel 2020, so repeating the full width shows a dark crease at
  every joint. Repeat texels 62 to 1931 (u 0.0303 to 0.9429): that pair joins as smoothly as two neighbouring
  columns (A_01 normal, A_02 colour and alpha), about 1.26 m per repeat at 5 cm wide. Seam pieces 51 and 54 have
  no caps and wrap as they are. For another strip, compare each map's end columns with its median column, and
  search for the column pair that joins as smoothly as neighbours do.
- **One direction per line.** Lay every bead along one direction of its edge (say, the edge direction with its
  first non-zero component positive) and measure U from the world origin along it,
  `U = position · direction × UV per metre`, so separate beads on one line run on in step.
- **Joints between repeats.** Put a row of vertices at each repeat boundary and give each face the repeat it lies
  in, `u = u0 + U - n × window`. Cut those rows square across the strip, each side's vertex where its own U
  reaches the boundary: a mitred end shifts the side corners along the strip (5 cm seen), and a row lerped
  between them straddles the joint. Keep the window a few dozen texels inside the caps so a tip that reaches past
  a joint still lands on clean texture, then check that every bead UV lies in the clean range.
- **Beads round a bevel** [owner: the harsh welded edge needed "a little bevel", on the corner and on the weld
  decal both]. A rounder bevel alone changed nothing: the bead was still drawn in flat facets with a crease down
  its middle. Bevel welded corners rounder than plate edges (2.5 cm in 6 segments, each step under the 30 degree
  smoothing angle), lay the bead on the bevelled surface as in "Seams over edges and bevels" with 8 rows across
  (seams need 4), then merge its vertices and shade it smooth.
  - **Check the bevel is there under every weld** [HARD, measured; owner saw welded corners with no bevel at all]:
    the Bevel modifier's `use_clamp_overlap` (on by default) shrinks a bevel to fit the shortest neighbouring
    edge, and on a part with short edges near its welded corners it shrank them to zero width. Turn it off on
    welded parts, then check the evaluated mesh for flipped and self-intersecting faces. Take a cross-section
    under a few beads to confirm the bevel's steps are there.
  - **Keep the laid bead off the surface between its vertices** [HARD, measured; owner saw a bead 0.06 mm off the
    surface z-fight in game as a jagged line]. Each face is flat, so it dips into the bevel between vertices
    laid on it. Across the bead, a row crossing one of a 4-segment bevel's folds dipped about 1.1 mm; 6 segments
    fixed it. Along the bead, a long face dips wherever the bevel bends along the weld: corner patches where
    bevels meet, and mitred ends. Before laying, add cross-steps along the strip wherever an edge between two
    laid vertices dips more than 0.25 mm below its ends (sample every cm, halve the step until it passes). Give
    every row the same steps so the strip stays in one piece, and let a mitred end face blend into its tip across
    the steps so it can split too. Do not split faces after laying (bmesh `subdivide_edges`): faces that get only
    some edges cut become many-sided polygons, and they fold once their new vertices are laid.
  - In a concave groove the lifted point is nearer the other face: push it out along that face's normal until it
    clears both. Check every bead's gap at face centres and edge midpoints: aim for at least 0.7 mm with a 1.5 mm
    lift [SOFT until seen in game].

Round joints get a ring of short quads; a fillet weld in an inside corner is a strip at 45 degrees across the
corner, one edge on each face. Which joints get a weld: `design-detailing.md`, "Every joint says how it was
made".

## TextAtlas

Full size 1024 x 1024 px, 38 pieces, re-catalogued at full resolution. Letters and digits share a cap height (about 123 px); Q's tail drops below it.

| id | u0 | v0 | u1 | v1 | px | piece |
|---|---|---|---|---|---|---|
| 1 | 0.0205 | 0.8604 | 0.0977 | 0.9805 | 79x123 | letter A |
| 2 | 0.1709 | 0.8604 | 0.249 | 0.9805 | 80x123 | letter B |
| 3 | 0.3203 | 0.8604 | 0.3994 | 0.9805 | 81x123 | letter C |
| 4 | 0.4639 | 0.8604 | 0.542 | 0.9805 | 80x123 | letter D |
| 5 | 0.6143 | 0.8604 | 0.6855 | 0.9805 | 73x123 | letter E |
| 6 | 0.752 | 0.8604 | 0.8242 | 0.9805 | 74x123 | letter F |
| 7 | 0.8828 | 0.8604 | 0.9609 | 0.9805 | 80x123 | letter G |
| 8 | 0.0205 | 0.6943 | 0.0918 | 0.8164 | 73x125 | letter H |
| 9 | 0.168 | 0.6943 | 0.1836 | 0.8145 | 16x123 | letter I |
| 10 | 0.248 | 0.6943 | 0.3125 | 0.8164 | 66x125 | letter J |
| 11 | 0.3857 | 0.6943 | 0.46 | 0.8164 | 76x125 | letter K |
| 12 | 0.5215 | 0.6943 | 0.5801 | 0.8164 | 60x125 | letter L |
| 13 | 0.6348 | 0.6943 | 0.75 | 0.8164 | 118x125 | letter M |
| 14 | 0.8164 | 0.6943 | 0.8926 | 0.8164 | 78x125 | letter N |
| 15 | 0.0195 | 0.5283 | 0.0986 | 0.6484 | 81x123 | letter O |
| 16 | 0.1709 | 0.5283 | 0.2471 | 0.6484 | 78x123 | letter P |
| 17 | 0.3154 | 0.5107 | 0.3984 | 0.6484 | 85x141 | letter Q |
| 18 | 0.4668 | 0.5283 | 0.5439 | 0.6484 | 79x123 | letter R |
| 19 | 0.6094 | 0.5283 | 0.7031 | 0.6484 | 96x123 | letter S |
| 20 | 0.7539 | 0.5283 | 0.8389 | 0.6484 | 87x123 | letter T |
| 21 | 0.8984 | 0.5283 | 0.9746 | 0.6504 | 78x125 | letter U |
| 22 | 0.0156 | 0.3623 | 0.0986 | 0.4844 | 85x125 | letter V |
| 23 | 0.1641 | 0.3623 | 0.2871 | 0.4844 | 126x125 | letter W |
| 24 | 0.3516 | 0.3623 | 0.4375 | 0.4844 | 88x125 | letter X |
| 25 | 0.4961 | 0.3623 | 0.5811 | 0.4844 | 87x125 | letter Y |
| 26 | 0.6416 | 0.3623 | 0.7266 | 0.4824 | 87x123 | letter Z |
| 27 | 0.7822 | 0.3623 | 0.8564 | 0.4502 | 76x90 | small x (alternate X) |
| 28 | 0.041 | 0.1963 | 0.0752 | 0.3164 | 35x123 | digit 1 |
| 29 | 0.1602 | 0.1963 | 0.2461 | 0.3164 | 88x123 | digit 2 |
| 30 | 0.3037 | 0.1963 | 0.3867 | 0.3164 | 85x123 | digit 3 |
| 31 | 0.4521 | 0.1963 | 0.5342 | 0.3164 | 84x123 | digit 4 |
| 32 | 0.5879 | 0.1963 | 0.6768 | 0.3164 | 91x123 | digit 5 |
| 33 | 0.7402 | 0.1963 | 0.8281 | 0.3164 | 90x123 | digit 6 |
| 34 | 0.8779 | 0.1963 | 0.9648 | 0.3164 | 89x123 | digit 7 |
| 35 | 0.0156 | 0.0215 | 0.1016 | 0.1416 | 88x123 | digit 8 |
| 36 | 0.1572 | 0.0215 | 0.2422 | 0.1416 | 87x123 | digit 9 |
| 37 | 0.3027 | 0.0215 | 0.3877 | 0.1416 | 87x123 | digit 0 |
| 38 | 0.4688 | 0.0137 | 0.792 | 0.1641 | 331x154 | human silhouette |
