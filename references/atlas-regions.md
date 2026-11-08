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

| Atlas | Materials (variant word) | Content |
|---|---|---|
| `Atlas1` | `Atlas1` (plain), `Atlas1Colorable` (colorable) | Plate and panel decals. |
| `Atlas2` | `Atlas2` (plain) | Sticker and label sheet: hazard signs, HUD marks, food and ship-system icons. |
| `Atlas3` | `Atlas3_Colorable` (colorable), `Atlas3_Darker` (darker), `Atlas3_Chrome` (chrome) | Mechanical detail plates: vents, slots, hatches, hubs, panels. |
| `Atlas4` | `Atlas4_Colorable` (colorable), `Atlas4_Darker` (darker), `Atlas4_VeryDark` (verydark), `Atlas4_Chrome` (chrome), `Atlas4_Yellow` (yellow) | Trim bands and a row of trapezoid pockets. |
| `ButtonsAtlas` | `ButtonsAtlas_Colorable` (colorable), `ButtonsAtlas_Darker` (darker) | Buttons, switches, LEDs, keypads and connectors for control panels. |
| `Decals_Atlas_A_01` | `Decals` (plain), `PanelingColorable` (colorable), `PanelingDarker` and `PanelingDarkerNoReskin` (darker) | Large decal sheet: signs, fittings, plates, grime and trim strips. |
| `TextAtlas` | `TextAtlas` (plain), `TextAtlasDark` (darker) | Capital letters, digits and a human silhouette. |

Every material of an atlas uses that atlas's `_alphamask`, so every box in this file fits every variant
[HARD, material definitions in `vanilla-materials.md`]. Only the colorable material has a paint mask; every
other variant keeps its own colours [HARD, `_add` alpha read]. `PanelingDarker` and `PanelingDarkerNoReskin`
take the `Decals_Atlas_A_02` colour map: its plates and bars are darker, its signs, bolt heads, chevrons and
weld bead match A_01, and its scratches (15, 26) and vent grille (30) are lighter [HARD, measured]. On Atlas1
only the thin rib (12) differs: mid grey on `Atlas1Colorable`, dark on `Atlas1`. The `chrome` variant reads
as brushed steel in game, not a mirror (`materials-catalog.md`).

## Tags

Each row's `tags` cell uses only the words below, in facet order, so a search by word finds every candidate:
`python scripts/find_decal.py vent round` (all words must match; `-h` for options). The function, shape, relief
and surface words describe hard-surface parts in general, so other part catalogues can reuse them.

- **function**, what the piece is: `fastener` (bolt, screw, rivet), `vent`, `grille` (mesh, perforation,
  speaker), `slot` (black opening or window), `panel` (plate, pocket, pad), `hatch` (lid or access cover),
  `clamp` (latch, bracket, lug, handle), `hinge`, `seam` (panel line, groove, weld bead, bevel), `frame` (rim
  round an opening), `hub` (disc, cap, dish), `pipe` (pipe, bar, rod, cable), `truss` (lattice or struts),
  `pattern` (repeated dimples, holes or links), `socket` (jack or connector), `button` (key, switch, knob,
  lever), `light` (LED or lamp), `sign` (warning or label plate), `marking` (icon, stripe, arrow, badge),
  `text` (words, codes, letters, digits), `grime` (stains and scratches).
- **shape**, its outline: `round`, `ring` (annulus or arc), `square`, `rect`, `pill` (rounded ends), `strip`
  (long and thin: a bar, band or line), `triangle`, `trapezoid`, `polygon` (hex, octagon, diamond, chevron,
  L), `glyph` (a letter or symbol).
- **relief**, from the normal map [HARD]: `raised`, `recessed`, `flat`. The score is the mean outward tilt of
  the normal about each connected part's centre: +0.12 or more is raised, -0.12 or less recessed, and a piece
  with under 8 % of its texels tilted is flat; checked against the X panel (42-45) and bolt heads seen in game.
  Atlas2 and TextAtlas are stickers with almost no relief, so all flat. A piece that mixes both, or scores in
  between, has no relief word (Atlas1 6, Atlas4 2, Decals 57).
- **surface**, where it suits [SOFT, suggestion from what the piece shows]: `hull` (armour and outer plating),
  `machine` (engines, machinery, functional blocks), `console` (control panels, interiors), `trim` (edges and
  bands along seams), `cargo` (containers and storage).
- **variant** [HARD, measured]: `paint` takes the player's colour on the colorable material (over half the
  piece is in its paint mask). `fixed` looks the same whichever variant you pick: each variant shifts its
  luminance less than 60 % as much as it shifts the sheet's paintable plates. A piece with neither shifts with
  the variant. Only Atlas3, Atlas4, ButtonsAtlas and Decals rows carry `fixed`: Atlas2 has one colour map,
  every TextAtlas glyph darkens on `TextAtlasDark`, and Atlas1's two colour maps match except at the rib (12).
- **flags**: `tileable` (repeats cleanly along its long axis: the end columns join like neighbours [HARD,
  measured]), `seethrough` (transparent holes inside the piece), `outline` (use the outline under the table:
  the box would catch a neighbour, or a key needs rounded corners), `inside` (sits inside a larger opaque piece;
  box measured from the colour or normal map).

The variant words (plain, colorable, darker, verydark, chrome, yellow) come from the materials table, not the
rows: `find_decal.py` adds each sheet's words, so `find_decal.py slot chrome` lists slots on chrome sheets.

## Mapping a piece onto a quad

```python
def map_quad_to_region(obj, u0, v0, u1, v1, uv_name='UVMap'):
    # obj: one quad mesh. Corners go bottom-left, bottom-right, top-right, top-left in loop order.
    uv = obj.data.uv_layers[uv_name].data
    for loop, (u, v) in zip(obj.data.polygons[0].loop_indices, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]):
        uv[loop].uv = (u, v)
```

Rotate the quad (or reorder the corner list) rather than flipping UVs when a piece is the wrong way up. Keep the quad's aspect ratio equal to the region's `px` ratio so the piece is not stretched.

**Cropping a round piece to a smaller circle** [SOFT, built and ray-checked, not yet seen in game]: a square crop
leaves the ring's outer lip in the corners. Lay a disc instead, a 48-gon whose vertices sit at radius `k * size` round
the piece's centre, with UVs `(cu + k * (u1 - u0) * cos t, cv + k * (v1 - v0) * sin t)`, where `k` is the cut as a
fraction of the piece's width. Pick `k` from a radial profile of the lit texture (colour, alpha and normal map
averaged over angle) instead of by eye. To make the edge the darkest line, cut at the bottom of the outer groove,
where the normal map's z is lowest and the colour darkest. Atlas3 10 (concentric rings) has that groove at
k = 0.4675; its alpha runs out at 0.497.

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
  diamond split along a diagonal, an L-shaped pipe, a tile stepping around a strip's end. Cut a diagonal pair
  down the middle of the gap between its halves, which need not run corner to corner (Atlas2 85-88).
- Check every box and every outline for alpha it cuts, down to 1 px: the owner saw 1-2 px cuts on letter
  bottoms, triangle corners and diagonal halves that a check hiding growth under 3 px had passed. Widen an
  outline until it holds every texel of its piece and none of a neighbour's.
- Pieces inside a sign or panel cannot be snapped (the background is opaque): measure them from the colour
  texture (dark pixels for a barcode, red for a prohibition circle) and give icons a square centred on the icon.
- Tiles laid edge to edge (four food icons on one strip, colour bands in one stripe row) get equal boxes from the
  strip they sit on, split at the real colour changes, not by eye.
- Draw review outlines just outside each box; a line on the box edge hides the piece's outermost pixels and makes
  the box look clipped.

## Atlas1

Full size 2048 x 2048 px, 12 pieces, re-catalogued at full resolution and checked against the owner's markup. The schematic panel (11) is one decal: its plates, rings, bars, discs and cable run are not separate pieces. The X inside the octagon frame (8) also works on its own. Repeating patterns (five dimples, six slots, 25 holes) are one decal each.

| id | u0 | v0 | u1 | v1 | px | piece | tags |
|---|---|---|---|---|---|---|---|
| 1 | 0.0002 | 0.7371 | 0.3918 | 0.9998 | 802x538 | big dark plate with four tall see-through slots; L-shaped, the six-slot comb (5) sits in its notch (outline below) | slot panel rect flat hull machine paint seethrough outline |
| 2 | 0.4003 | 0.6113 | 0.4766 | 0.9976 | 156x791 | truss column: tall frame with a cross-braced lattice in four cells, see-through | frame truss strip hull machine paint seethrough |
| 3 | 0.6807 | 0.8076 | 0.9956 | 0.9829 | 645x359 | louvre: horizontal slats in a rounded frame (the slats are in the normal map; the colour map is plain) | vent grille rect hull machine paint |
| 4 | 0.5205 | 0.8208 | 0.6704 | 0.9702 | 307x306 | five round dimples in a dice-five layout | pattern round recessed hull machine paint |
| 5 | 0.2993 | 0.6162 | 0.3877 | 0.8354 | 181x449 | comb of six tall see-through slots in a dark frame | vent slot rect recessed hull machine paint seethrough |
| 6 | 0.4888 | 0.6162 | 0.7134 | 0.7886 | 460x353 | louvred plate: horizontal slats crossed by a raised A-frame of two diagonal struts | vent panel truss rect hull machine paint |
| 7 | 0.7549 | 0.5044 | 0.9976 | 0.7471 | 497x497 | octagonal frame round an X of recessed pill grooves (one long, two short; hazard-style) | frame marking polygon recessed hull machine paint |
| 8 | 0.7939 | 0.543 | 0.9585 | 0.708 | 337x338 | the X from the octagon frame on its own: one long and two short recessed pill grooves [inside] | marking pill recessed hull machine paint inside |
| 9 | 0.001 | 0.6299 | 0.2773 | 0.7109 | 566x166 | perforation field: 25 black rimmed round holes in staggered rows | vent grille pattern round strip recessed hull machine paint |
| 10 | 0 | 0.519 | 0.7085 | 0.5996 | 1451x165 | hazard stripes: grey diagonal bands with see-through gaps (the `Atlas1` colour map is neutral grey; for yellow use Atlas2 66) | marking strip flat hull trim seethrough |
| 11 | 0.0151 | 0.1211 | 0.9741 | 0.501 | 1964x778 | schematic panel (one decal: side plates, four rings, bars, two discs, cable run) | panel pipe rect machine console paint |
| 12 | 0 | 0.0234 | 1 | 0.0562 | 2048x67 | thin raised rib: dark, soft-edged half-round ridge, full width | seam pipe strip raised trim tileable |

Outlines (UV points in order; the piece's polygon uses the same points as positions and UVs):

- 1 big dark plate with four tall see-through slots; L-shaped, the six-slot comb (5) sits in its notch: (0.0002, 0.7371), (0.281, 0.7371), (0.2815, 0.844), (0.3918, 0.844), (0.3918, 0.9998), (0.0002, 0.9998)

## Atlas2

Full size 2048 x 2048 px, 89 pieces. Re-catalogued at full resolution and checked piece by piece against the owner's markup. Boxes are snapped to every pixel with alpha above 0.02 that is connected to the piece, so faint edges are inside; where two pieces touch, the boundary sits on the emptiest line between them. `inside` rows are pieces within a larger sign (no transparent border to snap to; measured from the colour texture). Pieces whose box would overlap a neighbour have an outline instead (listed under the table; use the outline as the decal face's shape with the same points as UVs, then triangulate).

| id | u0 | v0 | u1 | v1 | px | piece | tags |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 0.8721 | 0.127 | 0.9971 | 260x256 | medical icon: white heart with a pulse line on a worn dark red rounded tile | marking square flat console cargo |
| 2 | 0.1289 | 0.8789 | 0.2461 | 0.9961 | 240x240 | disc icon: left arrow, grey on a black disc with a grey ring | marking round flat console |
| 3 | 0.2539 | 0.8789 | 0.3711 | 0.9961 | 240x240 | disc icon: shopping cart with a down arrow | marking round flat console |
| 4 | 0.3789 | 0.8789 | 0.4961 | 0.9961 | 240x240 | disc icon: skip back | marking round flat console |
| 5 | 0.5039 | 0.8789 | 0.6211 | 0.9961 | 240x240 | disc icon: play/pause | marking round flat console |
| 6 | 0.6245 | 0.875 | 0.8516 | 1 | 465x256 | WARNING TIP OVER HAZARD sign (orange header, no-pushing pictogram, small print) | sign rect flat hull machine cargo |
| 7 | 0.8794 | 0.897 | 0.9312 | 0.9766 | 106x163 | white left-pointing triangle (arrow mark) | marking triangle flat hull machine console |
| 8 | 0.9536 | 0.8306 | 0.9927 | 0.9878 | 80x322 | word RIGHT, black, vertical (letters rotated 90 degrees) | text strip flat hull console |
| 9 | 0.0244 | 0.8149 | 0.0981 | 0.855 | 151x82 | words "medical kit", red, two lines | text rect flat console cargo |
| 10 | 0.1226 | 0.8267 | 0.2324 | 0.8643 | 225x77 | word LEFT, black | text rect flat hull console |
| 11 | 0.2441 | 0.8271 | 0.4107 | 0.8657 | 341x79 | word DOWN, black | text rect flat hull console |
| 12 | 0.4233 | 0.8257 | 0.4897 | 0.8643 | 136x79 | word UP, black | text rect flat hull console |
| 13 | 0.5 | 0.8174 | 0.5957 | 0.8721 | 196x112 | HIGH VOLTAGE label, black on a white plate | sign rect flat hull machine |
| 14 | 0.6074 | 0.8179 | 0.8604 | 0.8677 | 518x102 | Engine / Remote Operated System label, white on black | sign strip flat machine console |
| 15 | 0 | 0.687 | 0.2251 | 0.813 | 461x258 | DANGER STRONG MAGNETIC FIELD sign (red header, magnet pictogram, small print) | sign rect flat hull machine |
| 16 | 0.2495 | 0.6904 | 0.3887 | 0.813 | 285x251 | flame hazard triangle, yellow | sign triangle flat hull machine cargo |
| 17 | 0.4131 | 0.6899 | 0.5869 | 0.813 | 356x252 | CAUTION MOVING PARTS sign, black on yellow | sign rect flat machine |
| 18 | 0.5991 | 0.6899 | 0.8071 | 0.813 | 426x252 | WARNING HIGH PRESSURE sign, black on yellow | sign rect flat machine cargo |
| 19 | 0.8218 | 0.6811 | 0.9888 | 0.8487 | 343x345 | explosive hazard diamond, orange, division 1 (diamond outline) (outline below) | sign polygon flat machine cargo outline |
| 20 | 0.8134 | 0.6854 | 0.8692 | 0.7384 | 116x110 | three white dots, triangle cluster (box cut along the diamond edge) (outline below) | marking round flat hull console outline |
| 21 | 0.9395 | 0.6787 | 0.9937 | 0.7227 | 111x90 | red ring between two arcs, like (( O )) (box cut along the diamond edge) (outline below) | marking ring flat console outline |
| 22 | 0 | 0.5571 | 0.3657 | 0.6733 | 749x238 | TYPE A label: barcode and corner brackets, black on white | sign rect flat cargo |
| 23 | 0.3872 | 0.6099 | 0.5928 | 0.6855 | 421x155 | RESTRICTED AREA sign, white on red | sign rect flat hull |
| 24 | 0.6099 | 0.6191 | 0.6724 | 0.6816 | 128x128 | irritant hazard: black X on an orange square in a black frame | sign square flat machine cargo |
| 25 | 0.688 | 0.6216 | 0.748 | 0.6816 | 123x123 | battery icon on a red rounded tile | marking square flat machine console |
| 26 | 0.8628 | 0.6079 | 0.9263 | 0.6719 | 130x131 | white square outline with a chamfered corner and a small solid triangle in the opposite corner | frame marking square flat hull console |
| 27 | 0.9365 | 0.6084 | 0.9927 | 0.6699 | 115x126 | white tile crossed by three diagonal see-through stripes (corner mark) | marking square flat hull seethrough |
| 28 | 0.3857 | 0.5595 | 0.5473 | 0.5958 | 331x74 | word SIGNAL on a white plate | sign strip flat console |
| 29 | 0.8555 | 0.5215 | 1 | 0.6021 | 296x165 | ENERGY SOURCE sign, black on yellow with a lightning bolt | sign rect flat machine |
| 30 | 0.0078 | 0.4146 | 0.2681 | 0.5469 | 533x271 | COMPRESSED OXYGEN label, green and white, small print | sign rect flat cargo |
| 31 | 0.2832 | 0.4224 | 0.5044 | 0.5376 | 453x236 | CAUTION BATTERY BOX label, red on white with a striped border | sign rect flat machine cargo |
| 32 | 0.5234 | 0.5078 | 0.5396 | 0.5415 | 33x69 | small red rectangle, tall | marking rect flat console |
| 33 | 0.5576 | 0.5088 | 0.5947 | 0.5405 | 76x65 | small red down-pointing triangle | marking triangle flat hull console |
| 34 | 0.5264 | 0.4355 | 0.5894 | 0.4985 | 129x129 | red prohibition circle (crossed-out ring) | sign ring flat hull |
| 35 | 0.5947 | 0.4707 | 0.7266 | 0.4858 | 270x31 | word WARNING, red outline letters | text strip flat hull |
| 36 | 0.5952 | 0.4561 | 0.689 | 0.4639 | 192x16 | words DO NOT OPEN, red | text strip flat hull |
| 37 | 0.5947 | 0.4443 | 0.8047 | 0.4517 | 430x15 | words AUTHORIZED PERSONNEL ONLY, red | text strip flat hull |
| 38 | 0.8237 | 0.4492 | 0.8701 | 0.5132 | 95x131 | white X with a small triangle above and below (no frame) | marking polygon flat hull console |
| 39 | 0.873 | 0.4399 | 0.9517 | 0.5088 | 161x141 | white triangle outline, broken at the lower left | marking triangle flat hull console |
| 40 | 0.9517 | 0.4404 | 0.9917 | 0.5112 | 82x145 | white left-pointing chevron beside a short split bar | marking polygon flat hull console |
| 41 | 0.0126 | 0.3857 | 0.1285 | 0.4034 | 237x36 | stencil code MXS-2859-B | text strip flat hull cargo |
| 42 | 0.1353 | 0.3809 | 0.1533 | 0.4082 | 37x56 | digit 9 in a box outline | text square flat cargo |
| 43 | 0.061 | 0.3643 | 0.1284 | 0.3818 | 138x36 | stencil code OB40-E | text strip flat cargo |
| 44 | 0.0117 | 0.3394 | 0.0327 | 0.3569 | 43x36 | number 52 | text rect flat cargo |
| 45 | 0.0391 | 0.3394 | 0.0811 | 0.3569 | 86x36 | stencil code .ACG | text rect flat cargo |
| 46 | 0.0132 | 0.3086 | 0.0488 | 0.3257 | 73x35 | word NET | text rect flat cargo |
| 47 | 0.0137 | 0.2852 | 0.0601 | 0.3027 | 95x36 | word TARE | text rect flat cargo |
| 48 | 0.0137 | 0.2637 | 0.0737 | 0.2812 | 123x36 | stencil M.G.W. | text rect flat cargo |
| 49 | 0.0132 | 0.2373 | 0.123 | 0.2495 | 225x25 | serial D0124D0000E4 | text strip flat cargo |
| 50 | 0.1274 | 0.2373 | 0.1533 | 0.2495 | 53x25 | number 210 | text rect flat cargo |
| 51 | 0.0127 | 0.2236 | 0.1123 | 0.2344 | 204x22 | words MADE IN SPACE | text strip flat cargo |
| 52 | 0.1646 | 0.2881 | 0.4058 | 0.4028 | 494x235 | AMMUNITION label (heavy calibre rounds, tare mass, warfare) | sign rect flat cargo |
| 53 | 0.4189 | 0.2866 | 0.4551 | 0.4121 | 74x257 | bullet / shell icon, white | marking pill flat cargo |
| 54 | 0.4648 | 0.354 | 0.5342 | 0.4141 | 142x123 | red warning triangle outline with ! | sign triangle flat hull machine |
| 55 | 0.5391 | 0.2515 | 0.7153 | 0.4282 | 361x362 | RADIOACTIVE II diamond, transport class 7 | sign polygon flat machine cargo |
| 56 | 0.7236 | 0.3584 | 0.7959 | 0.4287 | 148x144 | food icon: knife and fork, grey tile | marking square flat console cargo |
| 57 | 0.7236 | 0.2881 | 0.7959 | 0.3584 | 148x144 | food icon: heat waves, cyan tile | marking square flat console cargo |
| 58 | 0.7236 | 0.2173 | 0.7959 | 0.2881 | 148x145 | food icon: wheat, orange tile | marking square flat console cargo |
| 59 | 0.7236 | 0.147 | 0.7959 | 0.2173 | 148x144 | food icon: mushroom, brown tile | marking square flat console cargo |
| 60 | 0.8008 | 0.1553 | 0.9951 | 0.4287 | 398x560 | DEHYDRATED MEAL PACK nutrition label (leaf icon, QR code) | sign rect flat cargo |
| 61 | 0.1655 | 0.21 | 0.2383 | 0.2808 | 149x145 | icon: spider, purple tile | marking square flat console cargo |
| 62 | 0.2383 | 0.21 | 0.3096 | 0.2808 | 146x145 | icon: steak, red tile | marking square flat console cargo |
| 63 | 0.0059 | 0.1138 | 0.3052 | 0.2036 | 613x184 | SEEDS label with apple icon | sign strip flat cargo |
| 64 | 0.8101 | 0.1211 | 1 | 0.1528 | 389x65 | word SPORES, black on a white plate | sign strip flat cargo |
| 65 | 0 | 0.0552 | 0.25 | 0.105 | 512x102 | orange diagonal stripes with see-through gaps | marking strip flat hull trim seethrough |
| 66 | 0 | 0 | 0.25 | 0.0498 | 512x102 | yellow and black hazard stripes | marking strip flat hull trim tileable |
| 67 | 0.25 | 0 | 0.5 | 0.0498 | 512x102 | white diagonal stripes with see-through gaps | marking strip flat hull trim tileable seethrough |
| 68 | 0.5 | 0 | 0.75 | 0.0498 | 512x102 | red and white diagonal stripes | marking strip flat hull trim tileable |
| 69 | 0.75 | 0 | 1 | 0.0498 | 512x102 | black diagonal stripes with see-through gaps | marking strip flat hull trim tileable seethrough |
| 70 | 0.9082 | 0.2422 | 0.9766 | 0.3105 | 140x140 | leaf icon, green tile (inside MEAL PACK) | marking square flat cargo inside |
| 71 | 0.9082 | 0.1699 | 0.9766 | 0.2383 | 140x140 | QR code (inside MEAL PACK) | marking square flat cargo inside |
| 72 | 0.0273 | 0.127 | 0.0898 | 0.1895 | 128x128 | apple icon, green tile (inside SEEDS) | marking square flat cargo inside |
| 73 | 0.0449 | 0.5801 | 0.2056 | 0.6143 | 329x70 | barcode (inside TYPE A) | marking strip flat cargo inside |
| 74 | 0.627 | 0.8784 | 0.7031 | 0.9551 | 156x157 | no-pushing pictogram: person pushing a tipping crate in a red crossed circle (inside TIP OVER sign) | sign round flat cargo inside |
| 75 | 0.0049 | 0.6929 | 0.0767 | 0.7646 | 147x147 | magnet pictogram (inside DANGER magnetic sign) | marking square flat machine inside |
| 76 | 0.103 | 0.3076 | 0.1519 | 0.3262 | 100x38 | weights: 30.480 KGS / 67.200 LBS | text rect flat cargo |
| 77 | 0.1079 | 0.2852 | 0.1519 | 0.3027 | 90x36 | weights: 2.180 KGS / 4.810 LBS | text rect flat cargo |
| 78 | 0.1015 | 0.2631 | 0.1509 | 0.2813 | 101x37 | weights: 20.800 KGS / 64.100 LBS | text rect flat cargo |
| 79 | 0.5991 | 0.5684 | 0.6387 | 0.6069 | 81x79 | target icon quarter, top left: solid quarter disc | marking round flat console |
| 80 | 0.6431 | 0.5635 | 0.6826 | 0.6035 | 81x82 | target icon quarter, top right: two quarter arcs | marking ring flat console |
| 81 | 0.6045 | 0.5254 | 0.6431 | 0.5645 | 79x80 | target icon quarter, bottom left: thick quarter ring | marking ring flat console |
| 82 | 0.6475 | 0.5239 | 0.6831 | 0.5591 | 73x72 | target icon quarter, bottom right: thin quarter ring | marking ring flat console |
| 83 | 0.7577 | 0.6078 | 0.8115 | 0.6764 | 111x142 | chevron, left: black, white-outlined, pointing right (one of a double chevron; outline, boxes overlap) (outline below) | marking polygon flat hull outline |
| 84 | 0.7924 | 0.608 | 0.8449 | 0.6761 | 109x140 | chevron, right: white, pointing right (one of a double chevron; outline, boxes overlap) (outline below) | marking polygon flat hull outline |
| 85 | 0.7021 | 0.5302 | 0.7642 | 0.5923 | 127x127 | square frame with a solid triangle, upper-left half, cut along the diagonal (outline below) | marking triangle flat hull outline |
| 86 | 0.7021 | 0.5302 | 0.7642 | 0.5923 | 127x127 | the same square frame, lower-right half (only its bottom and right edges), cut along the diagonal (outline below) | marking triangle flat hull outline |
| 87 | 0.7753 | 0.5224 | 0.8492 | 0.5967 | 151x152 | striped badge, upper-right half, cut along the diagonal (outline below) | marking triangle flat hull outline |
| 88 | 0.7753 | 0.5224 | 0.8492 | 0.5967 | 151x152 | striped badge, lower-left half, cut along the diagonal (outline below) | marking triangle flat hull outline |
| 89 | 0.5508 | 0.5595 | 0.5865 | 0.5958 | 73x74 | radio-wave icon, orange square (right end of the SIGNAL label) | marking square flat console |

Outlines (UV points in order; the piece's quad or polygon uses the same points as positions and UVs):

- 19 explosive hazard diamond, orange, division 1 (diamond outline): (0.9048, 0.8487), (0.8218, 0.7642), (0.9048, 0.6811), (0.9888, 0.7642)
- 20 three white dots, triangle cluster (box cut along the diamond edge): (0.8134, 0.6854), (0.8692, 0.6854), (0.8692, 0.7123), (0.8431, 0.7384), (0.8134, 0.7384)
- 21 red ring between two arcs, like (( O )) (box cut along the diamond edge): (0.9395, 0.6787), (0.9937, 0.6787), (0.9937, 0.7227), (0.9539, 0.7227), (0.9395, 0.7083)
- 83 chevron, left: black, white-outlined, pointing right (one of a double chevron; outline, boxes overlap): (0.7577, 0.6078), (0.7845, 0.6078), (0.8115, 0.6414), (0.7846, 0.6759), (0.7577, 0.6764), (0.7847, 0.6423)
- 84 chevron, right: white, pointing right (one of a double chevron; outline, boxes overlap): (0.7924, 0.608), (0.8181, 0.608), (0.8449, 0.6418), (0.8181, 0.6761), (0.7924, 0.6761), (0.8192, 0.6423)
- 85 square frame with a solid triangle, upper-left half, cut along the diagonal: (0.7021, 0.5923), (0.7642, 0.5923), (0.7642, 0.5874), (0.707, 0.5303), (0.7021, 0.5303)
- 86 the same square frame, lower-right half (only its bottom and right edges), cut along the diagonal: (0.7642, 0.5874), (0.7642, 0.5303), (0.707, 0.5303)
- 87 striped badge, upper-right half, cut along the diagonal: (0.7786, 0.5967), (0.8491, 0.5967), (0.8491, 0.5261)
- 88 striped badge, lower-left half, cut along the diagonal: (0.7754, 0.5967), (0.7786, 0.5967), (0.8491, 0.5261), (0.8491, 0.5225), (0.7754, 0.5225)

## Atlas3

Full size 2048 x 2048 px, 46 pieces, re-catalogued at full resolution and checked against the owner's markup. The 6 x 10 dimple grid (46) is one decal.

The X panel is four independent decals (42-45), not one [owner; HARD, normal map read and seen in game]:
the top (42) and right (44) triangles are recessed (debossed) and the left (43) and bottom (45) are raised
(embossed), each pair at two different depths (deeper: 42 and 43) [SOFT, depth from edge steepness]. A whole
square placed on a flat face looks lopsided. For a symmetric X, pick one triangle and build the X from four
triangle faces that all use its outline as UVs, with the world triangles rotated 90 degrees apart (tangent
space follows the UVs, so each rotated copy keeps correct lighting) [SOFT, UV recipe not yet seen in game].
The four triangles together span 477 px of opaque art, so a 1.6 m X is about 0.0034 m per px.

Size the finished decal to the open area of its face with margin; the test crate's 1.8 m square looked
oversized against a 2.4 m face with corner brackets.

| id | u0 | v0 | u1 | v1 | px | piece | tags |
|---|---|---|---|---|---|---|---|
| 1 | 0.3823 | 0.8154 | 0.4941 | 0.9966 | 229x371 | rectangular plate with a tall black window | slot panel rect recessed hull machine paint |
| 2 | 0.7529 | 0.8164 | 0.9331 | 0.9966 | 369x369 | speaker grille: round plate with four rings of curved black slots round a centre boss | vent grille round raised machine console paint |
| 3 | 0.9404 | 0.8179 | 0.998 | 0.9976 | 118x368 | slide latch: tall narrow plate, a recessed slot above a small ringed knob | slot clamp rect recessed machine paint |
| 4 | 0.0088 | 0.8218 | 0.1772 | 0.9902 | 345x345 | hub cap: wide domed disc with a ringed hub and a black centre hole | hub round machine paint |
| 5 | 0.1929 | 0.8188 | 0.3071 | 0.9922 | 234x355 | plate cut across by a black notched slot, a small ring screw on its upper part | slot panel rect recessed machine paint |
| 6 | 0.3257 | 0.8174 | 0.3623 | 0.9946 | 75x363 | slim black slot, its right side chamfered (trapezoid) | slot strip trapezoid recessed hull machine paint |
| 7 | 0.5029 | 0.8193 | 0.6211 | 0.9927 | 242x355 | clamp block: a square block between two rounded bars, in a tray | clamp rect recessed machine paint |
| 8 | 0.6504 | 0.8179 | 0.731 | 0.9946 | 165x362 | trapezoid wedge: tall plate, its right side chamfered | panel trapezoid hull machine paint |
| 9 | 0.1782 | 0.688 | 0.248 | 0.8105 | 143x251 | plain rectangular pocket, bottom corners chamfered | panel rect recessed hull machine paint |
| 10 | 0.3774 | 0.6899 | 0.4976 | 0.8105 | 246x247 | ring disc on a boss: concentric rings round a ringed hub with a keyed bore | hub round ring recessed machine paint |
| 11 | 0.5078 | 0.6904 | 0.5552 | 0.8096 | 97x244 | pill strip: one round dome over two ringed black holes | socket light pill recessed machine console paint |
| 12 | 0.5703 | 0.6904 | 0.6177 | 0.8096 | 97x244 | plain pill pocket | panel pill recessed hull machine paint |
| 13 | 0.7554 | 0.6909 | 0.9326 | 0.8091 | 363x242 | plate with six round dimples (2 x 3) | panel pattern rect hull machine paint |
| 14 | 0.9399 | 0.752 | 0.999 | 0.8105 | 121x120 | round sunken head: a dome in a recessed ring (not a dimple) | fastener round hull machine paint |
| 15 | 0.0049 | 0.6929 | 0.0586 | 0.8071 | 110x234 | black pill slot | slot pill recessed hull machine paint |
| 16 | 0.0864 | 0.6924 | 0.1631 | 0.8076 | 157x236 | tab with a hex socket bolt: round top, flared base | fastener clamp rect recessed machine paint |
| 17 | 0.2554 | 0.6929 | 0.3706 | 0.8076 | 236x235 | cross-head screw cap: a cross in a black ring groove | fastener round recessed machine paint fixed |
| 18 | 0.6235 | 0.6982 | 0.7515 | 0.7979 | 262x204 | clamp bar: two horizontal round bars in a rounded tray | clamp pipe rect machine paint |
| 19 | 0.9463 | 0.689 | 0.999 | 0.749 | 108x123 | small plate with a black slot down its right edge, curved top | slot panel rect machine paint |
| 20 | 0.0049 | 0.4429 | 0.0586 | 0.6826 | 110x491 | tall black pill slot | slot pill strip recessed hull machine paint |
| 21 | 0.3164 | 0.4404 | 0.373 | 0.6846 | 116x500 | tall plain channel with rounded ends | panel pill strip recessed hull machine paint |
| 22 | 0.3804 | 0.4429 | 0.6196 | 0.6821 | 490x490 | square vent cover: chamfered corners, a two-part mesh grille in the middle, small edge slots and bars | vent grille hatch square recessed hull machine paint |
| 23 | 0.6289 | 0.4419 | 0.6831 | 0.6831 | 111x494 | fluted bar: tall dark channel with two vertical ribs | vent strip recessed machine paint fixed |
| 24 | 0.6924 | 0.4424 | 0.8076 | 0.6826 | 236x492 | slatted vent: two banks of vertical black slots in a rounded frame | vent rect recessed hull machine paint |
| 25 | 0.8184 | 0.4424 | 0.8696 | 0.6831 | 105x493 | tall pill bar with a square recess in the middle | panel pill strip recessed machine paint |
| 26 | 0.8823 | 0.5645 | 0.9307 | 0.6851 | 99x247 | plain pill pocket, short | panel pill recessed hull machine paint |
| 27 | 0.9443 | 0.5679 | 0.9951 | 0.6826 | 104x235 | pill pocket with a round bar across its middle (handle or hinge pin) | clamp hinge pill recessed machine paint |
| 28 | 0.8813 | 0.3818 | 0.9937 | 0.4937 | 230x229 | shallow round dish | hub round recessed hull machine paint |
| 29 | 0.0024 | 0.2524 | 0.1851 | 0.4355 | 374x375 | corner bracket: triangular frame with two diagonal black slots | slot frame triangle recessed hull machine paint |
| 30 | 0.1919 | 0.2544 | 0.3706 | 0.4336 | 366x367 | square hatch: rounded square frame round an inner panel with two short handle slots and side tabs | hatch square raised hull machine paint |
| 31 | 0.3799 | 0.2559 | 0.4951 | 0.4312 | 236x359 | hinged lid: hinge barrel along the top, a seam across the lower third with a short handle slot, two screws | hatch hinge rect recessed hull machine paint |
| 32 | 0.5049 | 0.2534 | 0.6201 | 0.4331 | 236x368 | plate with four corner screws and a tall recessed slot in the middle | fastener slot panel rect recessed machine paint |
| 33 | 0.6245 | 0.2544 | 0.7505 | 0.4331 | 258x366 | access panel: two stacked inset rectangles, a ringed round screw, a small edge tab, corner rivets | panel hatch rect recessed machine paint |
| 34 | 0.7637 | 0.2554 | 0.8613 | 0.4321 | 200x362 | tall plate with a groove across the middle and four corner screws | fastener panel rect recessed hull machine paint |
| 35 | 0.8867 | 0.2617 | 0.9883 | 0.3633 | 208x208 | square stepped recess (two steps) | panel square recessed hull machine paint |
| 36 | 0.0088 | 0.189 | 0.4912 | 0.2485 | 988x122 | long bar with chamfered ends (trapezoid) | panel strip trapezoid recessed machine trim paint |
| 37 | 0.5039 | 0.1289 | 0.6211 | 0.2461 | 240x240 | perforated plate: 5 x 5 black round holes in a rounded square frame | vent grille pattern square recessed hull machine paint |
| 38 | 0.6274 | 0.1274 | 0.8726 | 0.2476 | 502x246 | wide rounded frame round a black rectangular opening | slot frame rect recessed hull machine paint |
| 39 | 0.8848 | 0.0073 | 0.9902 | 0.2432 | 216x483 | tall pill rim round a black slot holding three twisted strands (Keen uses it as a vent) | vent slot pipe pill recessed machine paint |
| 40 | 0.0078 | 0.0088 | 0.1172 | 0.1777 | 224x346 | plate with a round mounting hole notched into its top and bottom edges | panel clamp rect machine paint |
| 41 | 0.1445 | 0.0068 | 0.2222 | 0.1797 | 159x354 | small tall window: black slot in a rounded frame | slot frame rect recessed machine paint |
| 42 | 0.0858 | 0.5711 | 0.2887 | 0.6828 | 417x230 | X-panel triangle, top (debossed, deeper; outline) (outline below) | panel triangle recessed hull machine paint outline |
| 43 | 0.0703 | 0.4599 | 0.1782 | 0.6651 | 222x422 | X-panel triangle, left (embossed, deeper; outline) (outline below) | panel triangle raised hull machine paint outline |
| 44 | 0.1966 | 0.4598 | 0.3049 | 0.6652 | 223x422 | X-panel triangle, right (debossed, shallower; outline) (outline below) | panel triangle recessed hull machine paint outline |
| 45 | 0.0881 | 0.4436 | 0.2869 | 0.5525 | 408x224 | X-panel triangle, bottom (embossed, shallower; outline) (outline below) | panel triangle raised hull machine paint outline |
| 46 | 0.2617 | 0.0063 | 0.3633 | 0.1807 | 208x357 | field of 6 x 10 small recessed dimples (countersunk holes) in an even grid; Keen cuts short rows of it as rivets | fastener grille pattern rect recessed hull machine paint |

Outlines (UV points in order; the piece's polygon uses the same points as positions and UVs):

- 42 X-panel triangle, top (debossed, deeper; outline): (0.0858, 0.6706), (0.0873, 0.6654), (0.0909, 0.6603), (0.175, 0.5762), (0.1841, 0.5711), (0.1909, 0.5711), (0.2, 0.5762), (0.2841, 0.6603), (0.2877, 0.6655), (0.2887, 0.6701), (0.2887, 0.6749), (0.2855, 0.6792), (0.2803, 0.6817), (0.2743, 0.6828), (0.1007, 0.6828), (0.0947, 0.6817), (0.0895, 0.6792), (0.0864, 0.6749)
- 43 X-panel triangle, left (embossed, deeper; outline): (0.0703, 0.4659), (0.0719, 0.4621), (0.0742, 0.4605), (0.077, 0.4599), (0.0817, 0.462), (0.1761, 0.5565), (0.1782, 0.5606), (0.1782, 0.5644), (0.1761, 0.5685), (0.0817, 0.663), (0.0769, 0.6651), (0.073, 0.6639), (0.0703, 0.6591)
- 44 X-panel triangle, right (debossed, shallower; outline): (0.1966, 0.5606), (0.1988, 0.5564), (0.2932, 0.4619), (0.2992, 0.4598), (0.3032, 0.462), (0.3049, 0.4659), (0.3049, 0.6591), (0.3021, 0.664), (0.298, 0.6652), (0.2932, 0.6631), (0.1988, 0.5686), (0.1966, 0.5644)
- 45 X-panel triangle, bottom (embossed, shallower; outline): (0.0881, 0.4516), (0.0924, 0.4461), (0.1022, 0.4436), (0.2728, 0.4436), (0.2804, 0.4451), (0.2846, 0.4478), (0.2869, 0.4517), (0.2858, 0.4586), (0.2818, 0.4652), (0.2006, 0.5465), (0.193, 0.5514), (0.1857, 0.5525), (0.1789, 0.55), (0.1744, 0.5464), (0.0932, 0.4652), (0.0886, 0.4581)

## Atlas4

Full size 1024 x 1024 px, 6 pieces, re-catalogued at full resolution and checked against the owner's markup. The four trapezoid pockets (1) are one decal that repeats along a line; the five bands tile horizontally.

| id | u0 | v0 | u1 | v1 | px | piece | tags |
|---|---|---|---|---|---|---|---|
| 1 | 0.0068 | 0.6953 | 0.9932 | 0.7725 | 1010x79 | row of four recessed trapezoid pockets, alternately wide side up and down (repeats along a line) | panel strip trapezoid recessed machine trim paint tileable |
| 2 | 0 | 0.5693 | 1 | 0.6689 | 1024x102 | wide band with a row of eight recessed bolt holes | fastener strip machine trim paint tileable |
| 3 | 0 | 0.4834 | 1 | 0.5166 | 1024x34 | thin panel line: V groove with a dark centre line (Keen's panel line on newer blocks, see "Panel lines") | seam strip recessed hull trim paint tileable |
| 4 | 0 | 0.3359 | 1 | 0.4355 | 1024x102 | band with dark edge lines and a stained light centre; light in every variant | seam strip recessed hull trim paint fixed tileable |
| 5 | 0 | 0.124 | 1 | 0.3027 | 1024x183 | wide band of perforated bare metal: raised rims round a field of small round holes; bare metal in every variant | vent grille strip raised machine trim paint fixed tileable |
| 6 | 0 | 0.0166 | 1 | 0.1006 | 1024x86 | band with raised square blocks on a raised base, gear-like | pattern strip raised machine trim paint tileable |

**Repeats along bands 2 and 6** [HARD, read from `Atlas4_Colorable_ng`]: band 2's holes are recessed, one every
128 px centred at `58 + 128 j`; band 6's blocks are raised, one every 128 px, about 62 px wide, centred at
`63 + 128 j`, on a raised base band, and read like a gear rim. Band 6's pitch is `1.49` times its height, so
stretch U a little to land one block per facet (or per two) of a faceted cylinder: a block on a fold bends.

**Band 5 is bare metal in every colour variant** [HARD, read from the `_cm` maps]: its colour averages 154 of
255 in `Atlas4_VeryDark`, 165 in `_Darker` and 196 in `_Colorable`, with metalness (alpha) 202, so
`Atlas4_VeryDark` 5 renders as light perforated steel. Band 6 does follow the variant (60, 93 and 181).

## ButtonsAtlas

Full size 2048 x 2048 px, 66 pieces, re-catalogued at full resolution. Panels are snapped to their pixels; single keys on a panel are `inside` rows (the panel is opaque around them, so the box is measured, not snapped) and can be used as small decals on their own. Each key's box runs to the
outer edge of its recess: the outer of the light lip in the colour map and the last tilted texel of the bevel
in the normal map [HARD, measured; owner: colour alone stopped short on the dark keys, whose faces are darker
than the recess line]. Its outline rounds the corners (radius 4 px, 11 px on F1-F6) so no square panel
corner shows round the key [owner].

| id | u0 | v0 | u1 | v1 | px | piece | tags |
|---|---|---|---|---|---|---|---|
| 1 | 0.0034 | 0.8784 | 0.2471 | 0.9966 | 499x242 | panel: three bar-grip rotary knobs with green LEDs, a screw at each end | panel button light rect raised console paint |
| 2 | 0.2534 | 0.8784 | 0.4966 | 0.9966 | 498x242 | panel "Panel 1": 7 keys C1-C7 with green and red LEDs | panel button light rect raised console paint |
| 3 | 0.5024 | 0.8789 | 0.6846 | 0.9966 | 373x241 | panel: 6 keys F1-F6, an indicator slot over each | panel button rect raised console paint |
| 4 | 0.2749 | 0.9125 | 0.3018 | 0.9395 | 55x55 | key C1 [inside] (outline below) | button square console fixed outline inside |
| 5 | 0.3037 | 0.9125 | 0.3306 | 0.9395 | 55x55 | key C2 [inside] (outline below) | button square console fixed outline inside |
| 6 | 0.333 | 0.9125 | 0.3594 | 0.9395 | 54x55 | key C3 [inside] (outline below) | button square console fixed outline inside |
| 7 | 0.3618 | 0.9125 | 0.3882 | 0.9395 | 54x55 | key C4 [inside] (outline below) | button square console fixed outline inside |
| 8 | 0.3906 | 0.9125 | 0.4175 | 0.9395 | 55x55 | key C5 [inside] (outline below) | button square console fixed outline inside |
| 9 | 0.4194 | 0.9125 | 0.4463 | 0.9395 | 55x55 | key C6 [inside] (outline below) | button square console fixed outline inside |
| 10 | 0.4482 | 0.9125 | 0.4756 | 0.9395 | 56x55 | key C7 [inside] (outline below) | button square console fixed outline inside |
| 11 | 0.5185 | 0.9414 | 0.563 | 0.9708 | 91x60 | key F1 [inside] (outline below) | button rect raised console fixed outline inside |
| 12 | 0.5717 | 0.9414 | 0.6158 | 0.9708 | 90x60 | key F2 [inside] (outline below) | button rect console fixed outline inside |
| 13 | 0.6245 | 0.9414 | 0.669 | 0.9708 | 91x60 | key F3 [inside] (outline below) | button rect console fixed outline inside |
| 14 | 0.5185 | 0.892 | 0.563 | 0.9209 | 91x59 | key F4 [inside] (outline below) | button rect raised console fixed outline inside |
| 15 | 0.5717 | 0.892 | 0.6158 | 0.9209 | 90x59 | key F5 [inside] (outline below) | button rect raised console fixed outline inside |
| 16 | 0.6245 | 0.892 | 0.669 | 0.9209 | 91x59 | key F6 [inside] (outline below) | button rect raised console fixed outline inside |
| 17 | 0.6968 | 0.9424 | 0.7407 | 0.9863 | 90x90 | LED, green: domed lens in a dark ring | light round raised machine console |
| 18 | 0.6968 | 0.8892 | 0.7407 | 0.9331 | 90x90 | LED, red: domed lens in a dark ring | light round raised machine console |
| 19 | 0.752 | 0.8774 | 0.873 | 0.9976 | 248x246 | big round push button, white, in a black collar | button round raised machine console fixed |
| 20 | 0.877 | 0.8774 | 0.998 | 0.9976 | 248x246 | big round push button, yellow, in a black collar | button round raised machine console fixed |
| 21 | 0.0029 | 0.6279 | 0.1216 | 0.8716 | 243x499 | panel: keypad of 10 labelled keys, 2 x 5 | panel button rect raised console paint |
| 22 | 0.019 | 0.8212 | 0.0557 | 0.858 | 75x75 | key Esc [inside] (outline below) | button square console outline inside |
| 23 | 0.0693 | 0.8212 | 0.106 | 0.858 | 75x75 | key Spin [inside] (outline below) | button square console outline inside |
| 24 | 0.019 | 0.7763 | 0.0557 | 0.813 | 75x75 | key If [inside] (outline below) | button square console outline inside |
| 25 | 0.0693 | 0.7763 | 0.106 | 0.813 | 75x75 | key YoU [inside] (outline below) | button square console outline inside |
| 26 | 0.019 | 0.7314 | 0.0557 | 0.7681 | 75x75 | key Rea [inside] (outline below) | button square console outline inside |
| 27 | 0.0693 | 0.7314 | 0.106 | 0.7681 | 75x75 | key DTh [inside] (outline below) | button square console outline inside |
| 28 | 0.019 | 0.6865 | 0.0557 | 0.7232 | 75x75 | key iSHa [inside] (outline below) | button square console outline inside |
| 29 | 0.0693 | 0.6865 | 0.106 | 0.7232 | 75x75 | key VEan [inside] (outline below) | button square console outline inside |
| 30 | 0.019 | 0.6411 | 0.0557 | 0.6783 | 75x76 | key Ice [inside] (outline below) | button square console outline inside |
| 31 | 0.0693 | 0.6411 | 0.106 | 0.6783 | 75x76 | key dAy [inside] (outline below) | button square console outline inside |
| 32 | 0.125 | 0.7607 | 0.187 | 0.8638 | 127x211 | rocker switch, red, in a black bezel (left) | button rect raised console |
| 33 | 0.1875 | 0.7607 | 0.2495 | 0.8638 | 127x211 | rocker switch, red, in a black bezel (right) | button rect raised console |
| 34 | 0.2534 | 0.6284 | 0.4966 | 0.8716 | 498x498 | panel: keys N1-N5 with LEDs, three knobs Field1/Field2/Subfield, three knobs WPS/MOD/SRC, slider | panel button light square raised console paint |
| 35 | 0.2792 | 0.7885 | 0.3062 | 0.8155 | 55x55 | key N1 [inside] (outline below) | button square raised console fixed outline inside |
| 36 | 0.3081 | 0.7885 | 0.335 | 0.8155 | 55x55 | key N2 [inside] (outline below) | button square raised console fixed outline inside |
| 37 | 0.3374 | 0.7885 | 0.3638 | 0.8155 | 54x55 | key N3 [inside] (outline below) | button square raised console fixed outline inside |
| 38 | 0.3662 | 0.7885 | 0.3931 | 0.8155 | 55x55 | key N4 [inside] (outline below) | button square raised console fixed outline inside |
| 39 | 0.395 | 0.7885 | 0.4219 | 0.8155 | 55x55 | key N5 [inside] (outline below) | button square raised console fixed outline inside |
| 40 | 0.5083 | 0.7588 | 0.5605 | 0.8667 | 107x221 | slide switch, red body: green lamp, grey push button, lever up | button light rect raised console fixed |
| 41 | 0.5684 | 0.7588 | 0.6206 | 0.8667 | 107x221 | slide switch, green body: green lamp, grey push button, lever up | button light rect raised console fixed |
| 42 | 0.6289 | 0.7588 | 0.6812 | 0.8667 | 107x221 | slide switch, yellow body: red lamp, grey push button, lever down | button light rect raised console fixed |
| 43 | 0.689 | 0.7588 | 0.7412 | 0.8667 | 107x221 | slide switch, blue body: red lamp, grey push button, lever down | button light rect raised console fixed |
| 44 | 0.7539 | 0.7544 | 0.8711 | 0.8706 | 240x238 | big square push button, white, in a black collar | button square raised machine console fixed |
| 45 | 0.8789 | 0.7544 | 0.9961 | 0.8706 | 240x238 | big square push button, yellow, in a black collar | button square raised machine console fixed |
| 46 | 0.1274 | 0.6904 | 0.1846 | 0.7476 | 117x117 | round jack, white ring, on a studded flange | socket round raised machine console paint |
| 47 | 0.1904 | 0.6904 | 0.2476 | 0.7476 | 117x117 | round jack, blue ring, on a studded flange | socket round raised machine console paint |
| 48 | 0.1274 | 0.6274 | 0.1846 | 0.6846 | 117x117 | round jack, orange ring, on a studded flange | socket round raised machine console paint |
| 49 | 0.1904 | 0.6274 | 0.2476 | 0.6846 | 117x117 | round jack, green ring, on a studded flange | socket round raised machine console paint |
| 50 | 0.5044 | 0.6841 | 0.564 | 0.752 | 122x139 | rotary selector knob with a bar grip, grey | button round raised machine console |
| 51 | 0.5688 | 0.689 | 0.6289 | 0.749 | 123x123 | round push button, fluted ring | button round raised console |
| 52 | 0.6328 | 0.689 | 0.6924 | 0.7485 | 122x122 | round push button, plain | button round raised console |
| 53 | 0.6968 | 0.6763 | 0.7563 | 0.7476 | 122x146 | lever handle on a round hub with a slotted screw (outline notched around the slot corner) (outline below) | clamp button round raised machine console outline |
| 54 | 0.7681 | 0.6353 | 0.8716 | 0.7388 | 212x212 | round bayonet socket: four key notches, red-ringed centre, side lugs | socket round raised machine console |
| 55 | 0.8838 | 0.6367 | 0.9893 | 0.7417 | 216x215 | round five-pin socket on a lugged flange | socket round raised machine console |
| 56 | 0.5181 | 0.6274 | 0.603 | 0.6802 | 174x108 | card slot: black slot in a grey bezel | slot rect recessed console |
| 57 | 0.6167 | 0.6274 | 0.7031 | 0.6802 | 177x108 | slot with a small white light bar | slot light rect recessed console |
| 58 | 0.2534 | 0.4995 | 0.3716 | 0.6177 | 242x242 | EMERGENCY STOP button: red mushroom in a yellow ring, four screws | button sign square raised machine console fixed |
| 59 | 0.3818 | 0.5503 | 0.4497 | 0.6187 | 139x140 | square push button, dark (left) | button square raised console fixed |
| 60 | 0.4556 | 0.5508 | 0.5234 | 0.6187 | 139x139 | square push button, dark (right) | button square raised console fixed |
| 61 | 0.5303 | 0.5459 | 0.6113 | 0.6196 | 166x151 | round jack, white (large), on a dark rounded tab | socket round raised machine console |
| 62 | 0.6182 | 0.5459 | 0.6992 | 0.6196 | 166x151 | round jack, orange and green (large), on a dark rounded tab | socket round raised machine console |
| 63 | 0.7051 | 0.5459 | 0.7861 | 0.6196 | 166x151 | round jack, red (large), on a dark rounded tab | socket round raised machine console |
| 64 | 0.7915 | 0.5459 | 0.8726 | 0.6196 | 166x151 | round jack, cyan (large), on a dark rounded tab | socket round raised machine console |
| 65 | 0.8804 | 0.5015 | 0.9937 | 0.623 | 232x249 | large socket, open bore: round collar on a square flange | socket round machine console |
| 66 | 0.877 | 0.3779 | 0.998 | 0.4995 | 248x249 | large socket, closed: four clips round a cap, red ring | socket round machine console |

Outlines (UV points in order; the piece's quad or polygon uses the same points as positions and UVs):

- 4 key C1 [inside], rounded corners: (0.2998, 0.9395), (0.3006, 0.9393), (0.3012, 0.9389), (0.3016, 0.9382), (0.3018, 0.9375), (0.3018, 0.9146), (0.3016, 0.9138), (0.3012, 0.9132), (0.3006, 0.9127), (0.2998, 0.9126), (0.2769, 0.9126), (0.2761, 0.9127), (0.2755, 0.9132), (0.2751, 0.9138), (0.2749, 0.9146), (0.2749, 0.9375), (0.2751, 0.9382), (0.2755, 0.9389), (0.2761, 0.9393), (0.2769, 0.9395)
- 5 key C2 [inside], rounded corners: (0.3286, 0.9395), (0.3294, 0.9393), (0.33, 0.9389), (0.3304, 0.9382), (0.3306, 0.9375), (0.3306, 0.9146), (0.3304, 0.9138), (0.33, 0.9132), (0.3294, 0.9127), (0.3286, 0.9126), (0.3057, 0.9126), (0.3049, 0.9127), (0.3043, 0.9132), (0.3039, 0.9138), (0.3037, 0.9146), (0.3037, 0.9375), (0.3039, 0.9382), (0.3043, 0.9389), (0.3049, 0.9393), (0.3057, 0.9395)
- 6 key C3 [inside], rounded corners: (0.3574, 0.9395), (0.3582, 0.9393), (0.3588, 0.9389), (0.3592, 0.9382), (0.3594, 0.9375), (0.3594, 0.9146), (0.3592, 0.9138), (0.3588, 0.9132), (0.3582, 0.9127), (0.3574, 0.9126), (0.335, 0.9126), (0.3342, 0.9127), (0.3336, 0.9132), (0.3332, 0.9138), (0.333, 0.9146), (0.333, 0.9375), (0.3332, 0.9382), (0.3336, 0.9389), (0.3342, 0.9393), (0.335, 0.9395)
- 7 key C4 [inside], rounded corners: (0.3862, 0.9395), (0.387, 0.9393), (0.3876, 0.9389), (0.388, 0.9382), (0.3882, 0.9375), (0.3882, 0.9146), (0.388, 0.9138), (0.3876, 0.9132), (0.387, 0.9127), (0.3862, 0.9126), (0.3638, 0.9126), (0.363, 0.9127), (0.3624, 0.9132), (0.362, 0.9138), (0.3618, 0.9146), (0.3618, 0.9375), (0.362, 0.9382), (0.3624, 0.9389), (0.363, 0.9393), (0.3638, 0.9395)
- 8 key C5 [inside], rounded corners: (0.4155, 0.9395), (0.4163, 0.9393), (0.4169, 0.9389), (0.4173, 0.9382), (0.4175, 0.9375), (0.4175, 0.9146), (0.4173, 0.9138), (0.4169, 0.9132), (0.4163, 0.9127), (0.4155, 0.9126), (0.3926, 0.9126), (0.3918, 0.9127), (0.3912, 0.9132), (0.3908, 0.9138), (0.3906, 0.9146), (0.3906, 0.9375), (0.3908, 0.9382), (0.3912, 0.9389), (0.3918, 0.9393), (0.3926, 0.9395)
- 9 key C6 [inside], rounded corners: (0.4443, 0.9395), (0.4451, 0.9393), (0.4457, 0.9389), (0.4461, 0.9382), (0.4463, 0.9375), (0.4463, 0.9146), (0.4461, 0.9138), (0.4457, 0.9132), (0.4451, 0.9127), (0.4443, 0.9126), (0.4214, 0.9126), (0.4206, 0.9127), (0.42, 0.9132), (0.4196, 0.9138), (0.4194, 0.9146), (0.4194, 0.9375), (0.4196, 0.9382), (0.42, 0.9389), (0.4206, 0.9393), (0.4214, 0.9395)
- 10 key C7 [inside], rounded corners: (0.4736, 0.9395), (0.4744, 0.9393), (0.475, 0.9389), (0.4754, 0.9382), (0.4756, 0.9375), (0.4756, 0.9146), (0.4754, 0.9138), (0.475, 0.9132), (0.4744, 0.9127), (0.4736, 0.9126), (0.4502, 0.9126), (0.4494, 0.9127), (0.4488, 0.9132), (0.4484, 0.9138), (0.4482, 0.9146), (0.4482, 0.9375), (0.4484, 0.9382), (0.4488, 0.9389), (0.4494, 0.9393), (0.4502, 0.9395)
- 11 key F1 [inside], rounded corners: (0.5576, 0.9707), (0.5597, 0.9703), (0.5614, 0.9691), (0.5626, 0.9674), (0.563, 0.9653), (0.563, 0.9468), (0.5626, 0.9447), (0.5614, 0.943), (0.5597, 0.9418), (0.5576, 0.9414), (0.5239, 0.9414), (0.5219, 0.9418), (0.5201, 0.943), (0.519, 0.9447), (0.5186, 0.9468), (0.5186, 0.9653), (0.519, 0.9674), (0.5201, 0.9691), (0.5219, 0.9703), (0.5239, 0.9707)
- 12 key F2 [inside], rounded corners: (0.6104, 0.9707), (0.6124, 0.9703), (0.6141, 0.9691), (0.6153, 0.9674), (0.6157, 0.9653), (0.6157, 0.9468), (0.6153, 0.9447), (0.6141, 0.943), (0.6124, 0.9418), (0.6104, 0.9414), (0.5771, 0.9414), (0.5751, 0.9418), (0.5734, 0.943), (0.5722, 0.9447), (0.5718, 0.9468), (0.5718, 0.9653), (0.5722, 0.9674), (0.5734, 0.9691), (0.5751, 0.9703), (0.5771, 0.9707)
- 13 key F3 [inside], rounded corners: (0.6636, 0.9707), (0.6656, 0.9703), (0.6674, 0.9691), (0.6685, 0.9674), (0.6689, 0.9653), (0.6689, 0.9468), (0.6685, 0.9447), (0.6674, 0.943), (0.6656, 0.9418), (0.6636, 0.9414), (0.6299, 0.9414), (0.6278, 0.9418), (0.6261, 0.943), (0.6249, 0.9447), (0.6245, 0.9468), (0.6245, 0.9653), (0.6249, 0.9674), (0.6261, 0.9691), (0.6278, 0.9703), (0.6299, 0.9707)
- 14 key F4 [inside], rounded corners: (0.5576, 0.9209), (0.5597, 0.9205), (0.5614, 0.9193), (0.5626, 0.9176), (0.563, 0.9155), (0.563, 0.8975), (0.5626, 0.8954), (0.5614, 0.8937), (0.5597, 0.8925), (0.5576, 0.8921), (0.5239, 0.8921), (0.5219, 0.8925), (0.5201, 0.8937), (0.519, 0.8954), (0.5186, 0.8975), (0.5186, 0.9155), (0.519, 0.9176), (0.5201, 0.9193), (0.5219, 0.9205), (0.5239, 0.9209)
- 15 key F5 [inside], rounded corners: (0.6104, 0.9209), (0.6124, 0.9205), (0.6141, 0.9193), (0.6153, 0.9176), (0.6157, 0.9155), (0.6157, 0.8975), (0.6153, 0.8954), (0.6141, 0.8937), (0.6124, 0.8925), (0.6104, 0.8921), (0.5771, 0.8921), (0.5751, 0.8925), (0.5734, 0.8937), (0.5722, 0.8954), (0.5718, 0.8975), (0.5718, 0.9155), (0.5722, 0.9176), (0.5734, 0.9193), (0.5751, 0.9205), (0.5771, 0.9209)
- 16 key F6 [inside], rounded corners: (0.6636, 0.9209), (0.6656, 0.9205), (0.6674, 0.9193), (0.6685, 0.9176), (0.6689, 0.9155), (0.6689, 0.8975), (0.6685, 0.8954), (0.6674, 0.8937), (0.6656, 0.8925), (0.6636, 0.8921), (0.6299, 0.8921), (0.6278, 0.8925), (0.6261, 0.8937), (0.6249, 0.8954), (0.6245, 0.8975), (0.6245, 0.9155), (0.6249, 0.9176), (0.6261, 0.9193), (0.6278, 0.9205), (0.6299, 0.9209)
- 22 key Esc [inside], rounded corners: (0.0537, 0.8579), (0.0545, 0.8578), (0.0551, 0.8573), (0.0555, 0.8567), (0.0557, 0.856), (0.0557, 0.8232), (0.0555, 0.8225), (0.0551, 0.8219), (0.0545, 0.8214), (0.0537, 0.8213), (0.021, 0.8213), (0.0202, 0.8214), (0.0196, 0.8219), (0.0192, 0.8225), (0.019, 0.8232), (0.019, 0.856), (0.0192, 0.8567), (0.0196, 0.8573), (0.0202, 0.8578), (0.021, 0.8579)
- 23 key Spin [inside], rounded corners: (0.104, 0.8579), (0.1048, 0.8578), (0.1054, 0.8573), (0.1058, 0.8567), (0.106, 0.856), (0.106, 0.8232), (0.1058, 0.8225), (0.1054, 0.8219), (0.1048, 0.8214), (0.104, 0.8213), (0.0713, 0.8213), (0.0705, 0.8214), (0.0699, 0.8219), (0.0695, 0.8225), (0.0693, 0.8232), (0.0693, 0.856), (0.0695, 0.8567), (0.0699, 0.8573), (0.0705, 0.8578), (0.0713, 0.8579)
- 24 key If [inside], rounded corners: (0.0537, 0.813), (0.0545, 0.8128), (0.0551, 0.8124), (0.0555, 0.8118), (0.0557, 0.811), (0.0557, 0.7783), (0.0555, 0.7776), (0.0551, 0.7769), (0.0545, 0.7765), (0.0537, 0.7764), (0.021, 0.7764), (0.0202, 0.7765), (0.0196, 0.7769), (0.0192, 0.7776), (0.019, 0.7783), (0.019, 0.811), (0.0192, 0.8118), (0.0196, 0.8124), (0.0202, 0.8128), (0.021, 0.813)
- 25 key YoU [inside], rounded corners: (0.104, 0.813), (0.1048, 0.8128), (0.1054, 0.8124), (0.1058, 0.8118), (0.106, 0.811), (0.106, 0.7783), (0.1058, 0.7776), (0.1054, 0.7769), (0.1048, 0.7765), (0.104, 0.7764), (0.0713, 0.7764), (0.0705, 0.7765), (0.0699, 0.7769), (0.0695, 0.7776), (0.0693, 0.7783), (0.0693, 0.811), (0.0695, 0.8118), (0.0699, 0.8124), (0.0705, 0.8128), (0.0713, 0.813)
- 26 key Rea [inside], rounded corners: (0.0537, 0.7681), (0.0545, 0.7679), (0.0551, 0.7675), (0.0555, 0.7669), (0.0557, 0.7661), (0.0557, 0.7334), (0.0555, 0.7327), (0.0551, 0.732), (0.0545, 0.7316), (0.0537, 0.7314), (0.021, 0.7314), (0.0202, 0.7316), (0.0196, 0.732), (0.0192, 0.7327), (0.019, 0.7334), (0.019, 0.7661), (0.0192, 0.7669), (0.0196, 0.7675), (0.0202, 0.7679), (0.021, 0.7681)
- 27 key DTh [inside], rounded corners: (0.104, 0.7681), (0.1048, 0.7679), (0.1054, 0.7675), (0.1058, 0.7669), (0.106, 0.7661), (0.106, 0.7334), (0.1058, 0.7327), (0.1054, 0.732), (0.1048, 0.7316), (0.104, 0.7314), (0.0713, 0.7314), (0.0705, 0.7316), (0.0699, 0.732), (0.0695, 0.7327), (0.0693, 0.7334), (0.0693, 0.7661), (0.0695, 0.7669), (0.0699, 0.7675), (0.0705, 0.7679), (0.0713, 0.7681)
- 28 key iSHa [inside], rounded corners: (0.0537, 0.7231), (0.0545, 0.723), (0.0551, 0.7226), (0.0555, 0.7219), (0.0557, 0.7212), (0.0557, 0.6885), (0.0555, 0.6877), (0.0551, 0.6871), (0.0545, 0.6867), (0.0537, 0.6865), (0.021, 0.6865), (0.0202, 0.6867), (0.0196, 0.6871), (0.0192, 0.6877), (0.019, 0.6885), (0.019, 0.7212), (0.0192, 0.7219), (0.0196, 0.7226), (0.0202, 0.723), (0.021, 0.7231)
- 29 key VEan [inside], rounded corners: (0.104, 0.7231), (0.1048, 0.723), (0.1054, 0.7226), (0.1058, 0.7219), (0.106, 0.7212), (0.106, 0.6885), (0.1058, 0.6877), (0.1054, 0.6871), (0.1048, 0.6867), (0.104, 0.6865), (0.0713, 0.6865), (0.0705, 0.6867), (0.0699, 0.6871), (0.0695, 0.6877), (0.0693, 0.6885), (0.0693, 0.7212), (0.0695, 0.7219), (0.0699, 0.7226), (0.0705, 0.723), (0.0713, 0.7231)
- 30 key Ice [inside], rounded corners: (0.0537, 0.6782), (0.0545, 0.6781), (0.0551, 0.6777), (0.0555, 0.677), (0.0557, 0.6763), (0.0557, 0.6431), (0.0555, 0.6423), (0.0551, 0.6417), (0.0545, 0.6413), (0.0537, 0.6411), (0.021, 0.6411), (0.0202, 0.6413), (0.0196, 0.6417), (0.0192, 0.6423), (0.019, 0.6431), (0.019, 0.6763), (0.0192, 0.677), (0.0196, 0.6777), (0.0202, 0.6781), (0.021, 0.6782)
- 31 key dAy [inside], rounded corners: (0.104, 0.6782), (0.1048, 0.6781), (0.1054, 0.6777), (0.1058, 0.677), (0.106, 0.6763), (0.106, 0.6431), (0.1058, 0.6423), (0.1054, 0.6417), (0.1048, 0.6413), (0.104, 0.6411), (0.0713, 0.6411), (0.0705, 0.6413), (0.0699, 0.6417), (0.0695, 0.6423), (0.0693, 0.6431), (0.0693, 0.6763), (0.0695, 0.677), (0.0699, 0.6777), (0.0705, 0.6781), (0.0713, 0.6782)
- 35 key N1 [inside], rounded corners: (0.3042, 0.8154), (0.3049, 0.8153), (0.3056, 0.8149), (0.306, 0.8142), (0.3062, 0.8135), (0.3062, 0.7905), (0.306, 0.7898), (0.3056, 0.7891), (0.3049, 0.7887), (0.3042, 0.7886), (0.2812, 0.7886), (0.2805, 0.7887), (0.2799, 0.7891), (0.2794, 0.7898), (0.2793, 0.7905), (0.2793, 0.8135), (0.2794, 0.8142), (0.2799, 0.8149), (0.2805, 0.8153), (0.2812, 0.8154)
- 36 key N2 [inside], rounded corners: (0.333, 0.8154), (0.3338, 0.8153), (0.3344, 0.8149), (0.3348, 0.8142), (0.335, 0.8135), (0.335, 0.7905), (0.3348, 0.7898), (0.3344, 0.7891), (0.3338, 0.7887), (0.333, 0.7886), (0.3101, 0.7886), (0.3093, 0.7887), (0.3087, 0.7891), (0.3083, 0.7898), (0.3081, 0.7905), (0.3081, 0.8135), (0.3083, 0.8142), (0.3087, 0.8149), (0.3093, 0.8153), (0.3101, 0.8154)
- 37 key N3 [inside], rounded corners: (0.3618, 0.8154), (0.3626, 0.8153), (0.3632, 0.8149), (0.3636, 0.8142), (0.3638, 0.8135), (0.3638, 0.7905), (0.3636, 0.7898), (0.3632, 0.7891), (0.3626, 0.7887), (0.3618, 0.7886), (0.3394, 0.7886), (0.3386, 0.7887), (0.338, 0.7891), (0.3376, 0.7898), (0.3374, 0.7905), (0.3374, 0.8135), (0.3376, 0.8142), (0.338, 0.8149), (0.3386, 0.8153), (0.3394, 0.8154)
- 38 key N4 [inside], rounded corners: (0.3911, 0.8154), (0.3919, 0.8153), (0.3925, 0.8149), (0.3929, 0.8142), (0.3931, 0.8135), (0.3931, 0.7905), (0.3929, 0.7898), (0.3925, 0.7891), (0.3919, 0.7887), (0.3911, 0.7886), (0.3682, 0.7886), (0.3674, 0.7887), (0.3668, 0.7891), (0.3664, 0.7898), (0.3662, 0.7905), (0.3662, 0.8135), (0.3664, 0.8142), (0.3668, 0.8149), (0.3674, 0.8153), (0.3682, 0.8154)
- 39 key N5 [inside], rounded corners: (0.4199, 0.8154), (0.4207, 0.8153), (0.4213, 0.8149), (0.4217, 0.8142), (0.4219, 0.8135), (0.4219, 0.7905), (0.4217, 0.7898), (0.4213, 0.7891), (0.4207, 0.7887), (0.4199, 0.7886), (0.397, 0.7886), (0.3962, 0.7887), (0.3956, 0.7891), (0.3952, 0.7898), (0.395, 0.7905), (0.395, 0.8135), (0.3952, 0.8142), (0.3956, 0.8149), (0.3962, 0.8153), (0.397, 0.8154)
- 53 lever handle on a round hub with a slotted screw (outline notched around the slot corner): (0.7031, 0.6763), (0.7563, 0.6763), (0.7563, 0.7476), (0.6968, 0.7476), (0.6968, 0.6802), (0.7031, 0.6802)

## Decals_Atlas_A_01

Full size 2048 x 2048 px, 61 pieces, re-catalogued at full resolution and checked against the owner's markup. Boxes include the faint faded edges connected to each piece. Rows 59-61 are combined strips (a riveted band, a dimpled band and a double strip); their parts are also listed on their own for variety.

| id | u0 | v0 | u1 | v1 | px | piece | tags |
|---|---|---|---|---|---|---|---|
| 1 | 0.0034 | 0.9712 | 0.0278 | 0.9971 | 50x53 | bolt head 1: round head with two opposed notches (clutch drive) | fastener round raised hull machine paint fixed |
| 2 | 0.0332 | 0.9707 | 0.0605 | 0.998 | 56x56 | bolt head 2: round head, a ring groove round a raised centre boss | fastener round raised hull machine paint fixed |
| 3 | 0.0635 | 0.9697 | 0.0928 | 0.999 | 60x60 | bolt head 3: dome in a recessed ring | fastener round raised hull machine paint fixed |
| 4 | 0.0957 | 0.9722 | 0.123 | 0.9966 | 56x50 | bolt head 4: hex head with a domed top (acorn nut) | fastener polygon raised hull machine paint fixed |
| 5 | 0.127 | 0.9717 | 0.1538 | 0.9971 | 55x52 | bolt head 5: round head with a wide lens-shaped slot | fastener round raised hull machine paint fixed |
| 6 | 0.1587 | 0.9712 | 0.1851 | 0.9976 | 54x54 | bolt head 6: round head, a raised rim round a sunken flat centre | fastener round ring raised hull machine paint fixed |
| 7 | 0.1904 | 0.9727 | 0.2158 | 0.9961 | 52x48 | bolt head 7: hex head with a six-lobe (star) socket | fastener polygon raised hull machine paint fixed |
| 8 | 0.2217 | 0.9717 | 0.2471 | 0.9971 | 52x52 | bolt head 8: round head with a straight slot | fastener round raised hull machine paint fixed |
| 9 | 0.2505 | 0.9697 | 0.2803 | 0.999 | 61x60 | bolt head 9: hex socket head on a round washer | fastener round raised hull machine paint fixed |
| 10 | 0.2842 | 0.9717 | 0.3096 | 0.9971 | 52x52 | bolt head 10: plain round dome | fastener round raised hull machine paint fixed |
| 11 | 0.313 | 0.9692 | 0.3428 | 0.999 | 61x61 | bolt head 11: hex nut on a round washer | fastener round raised hull machine paint fixed |
| 12 | 0.3438 | 0.9688 | 0.5312 | 1 | 384x64 | light scratched metal strip with a step near its left end (one opaque rectangle; the scratches are in its colour) | panel strip recessed machine trim paint fixed |
| 13 | 0.4091 | 0.8461 | 0.6534 | 0.9688 | 500x251 | grime drips: dark stains running down from a top edge | grime rect hull machine |
| 14 | 0.3237 | 0.852 | 0.397 | 0.9625 | 150x226 | soot stain: dark smudge with a fading plume rising above it | grime round flat hull machine |
| 15 | 0.0126 | 0.8466 | 0.3062 | 0.9649 | 601x242 | scattered fine scratches, light | grime rect flat hull machine |
| 16 | 0.6636 | 0.8896 | 0.7109 | 0.9883 | 97x202 | tall pill plate | panel pill raised hull machine paint |
| 17 | 0.7324 | 0.9575 | 0.8936 | 0.9795 | 330x45 | thin bar, plain, rounded ends | panel pill strip raised machine trim paint |
| 18 | 0.7266 | 0.8965 | 0.8979 | 0.9185 | 351x45 | thin bar with a meander (square-wave) groove | panel pill strip machine trim paint |
| 19 | 0.7319 | 0.832 | 0.895 | 0.856 | 334x49 | thin bar with cross grooves (segmented) | panel pill strip raised machine trim paint |
| 20 | 0.9102 | 0.8281 | 0.9966 | 0.9849 | 177x321 | tall rounded plate with three long vertical ribs | panel rect raised machine paint |
| 21 | 0 | 0.7812 | 0.125 | 0.8438 | 256x128 | pipes: a horizontal pipe crossed by two vertical pipes | pipe rect machine paint |
| 22 | 0.1338 | 0.7935 | 0.1777 | 0.8315 | 90x78 | small rounded square pocket | panel square recessed hull machine paint |
| 23 | 0.1239 | 0.742 | 0.2257 | 0.8448 | 210x212 | pipe elbow: thin bent pipe, L-shaped (outline; its box would cover the small square plate) (outline below) | pipe polygon machine paint outline |
| 24 | 0.0024 | 0.7241 | 0.0591 | 0.7793 | 116x113 | rounded square pocket with a raised lower half (a step) | panel square machine paint |
| 25 | 0.0781 | 0.7261 | 0.1084 | 0.7725 | 62x95 | small tall pad with a slanted side and a step at the bottom | panel rect machine paint |
| 26 | 0.2529 | 0.6958 | 0.3438 | 0.8384 | 186x292 | scratch cluster: fine light scratches round a vertical line | grime strip hull machine |
| 27 | 0.5015 | 0.6274 | 0.6543 | 0.8379 | 313x431 | hatch frame: rectangular frame with a hinge strip along the top, see-through centre | hatch hinge frame rect hull machine paint seethrough |
| 28 | 0.6636 | 0.7822 | 0.7134 | 0.874 | 102x188 | buckle latch: tall plate with a raised tab, a slot in its top, side lugs | clamp rect machine paint |
| 29 | 0.6704 | 0.6318 | 0.7056 | 0.7759 | 72x295 | tall slim pill frame | frame pill strip raised machine paint |
| 30 | 0.7188 | 0.5273 | 1 | 0.8125 | 576x584 | vent grille: dense grid of short black slots | vent grille square hull machine |
| 31 | 0.3135 | 0.5928 | 0.4043 | 0.6885 | 186x196 | round hatch: ring frame round a disc split down the middle | hatch round ring hull machine paint |
| 32 | 0.4141 | 0.5947 | 0.4946 | 0.6865 | 165x188 | rounded square plate with a raised U-shaped bracket and two hooks | panel clamp square machine paint |
| 33 | 0.3525 | 0.4097 | 0.4302 | 0.5903 | 159x370 | tall chamfered plate with four vertical grooves | panel polygon hull machine paint |
| 34 | 0.4429 | 0.4102 | 0.5264 | 0.5894 | 171x367 | tall capsule plate with end tabs and side notches | panel polygon machine paint |
| 35 | 0.729 | 0.4404 | 0.7715 | 0.5273 | 87x178 | lifting lug: rounded tab with a round hole near one end (eyelet, zip pull) | clamp pill machine fixed |
| 36 | 0.3442 | 0.3438 | 0.7812 | 0.3955 | 895x106 | chain strip: interlocking dog-bone links between two thin rails | pattern strip machine trim fixed |
| 37 | 0 | 0.4687 | 0.3067 | 0.6875 | 628x448 | DANGER HIGH VOLTAGE sign (whole) | sign rect flat hull machine fixed |
| 38 | 0.0034 | 0.3125 | 0.1846 | 0.4648 | 371x312 | high-voltage warning triangle, yellow | sign triangle flat hull machine fixed |
| 39 | 0.1875 | 0.3125 | 0.3442 | 0.4688 | 321x320 | pressure gauge: dial 0-6 bar with green, yellow and red zones | sign round flat machine console fixed |
| 40 | 0.7812 | 0.3125 | 1 | 0.5278 | 448x441 | medical heart with a pulse line, red on a grunge tile | marking square flat console cargo fixed |
| 41 | 0.5391 | 0.5596 | 0.6191 | 0.6167 | 164x117 | circuit logo sticker: dark traces over green circuit shapes | marking rect flat console fixed |
| 42 | 0.5591 | 0.4575 | 0.5938 | 0.5474 | 71x184 | vertical text GOOD (dark) | text strip flat hull cargo fixed |
| 43 | 0.5581 | 0.4141 | 0.5947 | 0.4526 | 75x79 | letters AI, green (a logo: the A lies on its side) | text square flat console fixed |
| 44 | 0.646 | 0.563 | 0.6987 | 0.6147 | 108x106 | rank badge: dark pentagon outline with three chevrons | marking polygon flat hull fixed |
| 45 | 0.646 | 0.4873 | 0.6987 | 0.5396 | 108x107 | rank badge: dark pentagon outline with two chevrons | marking polygon flat hull fixed |
| 46 | 0.6465 | 0.4116 | 0.6987 | 0.4639 | 107x107 | rank badge: dark pentagon outline with one chevron | marking polygon flat hull fixed |
| 47 | 0.0176 | 0.5977 | 0.2891 | 0.6738 | 556x156 | DANGER red oval on black band (inside sign) | sign strip flat hull fixed inside |
| 48 | 0.0469 | 0.4961 | 0.2617 | 0.5859 | 440x184 | words HIGH VOLTAGE (inside sign) | text rect flat hull fixed inside |
| 49 | 0 | 0.2954 | 1 | 0.3086 | 2048x27 | groove strip with near-symmetric walls, full width (the top strip of band 59; reads as a seam) | seam strip recessed hull trim paint tileable |
| 50 | 0 | 0.2744 | 1 | 0.2871 | 2048x26 | row of round rivets that read raised under light from above, full width (see "Riveted bands") | fastener strip raised hull machine trim paint tileable |
| 51 | 0 | 0.2554 | 1 | 0.269 | 2048x28 | panel seam, lopsided groove (no vanilla model uses it as a seam) | seam strip recessed hull trim paint tileable |
| 52 | 0 | 0.2329 | 1 | 0.2461 | 2048x27 | groove strip with near-symmetric walls, full width (the top strip of band 60) | seam strip recessed hull trim paint tileable |
| 53 | 0 | 0.2119 | 1 | 0.2246 | 2048x26 | row of round recessed dimples, full width (see "Riveted bands") | pattern strip recessed hull machine trim paint tileable |
| 54 | 0 | 0.1929 | 1 | 0.2065 | 2048x28 | panel seam, groove with the same relief as 51 (no vanilla model uses it as a seam) | seam strip recessed hull trim paint tileable |
| 55 | 0 | 0.1392 | 1 | 0.1753 | 2048x74 | weld bead, full width (capped ends: repeat texels 62 to 1931, "Weld lines") | seam strip raised hull machine trim fixed |
| 56 | 0.0268 | 0.0664 | 1 | 0.1221 | 1993x114 | grime speck row: a band of light specks and fine scratches | grime strip flat hull trim paint |
| 57 | 0 | 0.0449 | 1 | 0.0552 | 2048x21 | thin bevel strip: one slope across its width, no groove, full width | seam strip hull trim paint tileable |
| 58 | 0 | 0.0073 | 1 | 0.0239 | 2048x34 | panel seam with one-sided bevel (Keen's classic panel line) | seam strip recessed hull trim paint tileable |
| 59 | 0 | 0.2554 | 1 | 0.3086 | 2048x109 | riveted band, raised rivets: groove + rivet row + groove as one decal (49+50+51) | fastener seam strip raised hull machine trim paint tileable |
| 60 | 0 | 0.1929 | 1 | 0.2461 | 2048x109 | dimpled band, recessed dimples: groove + dimple row + groove as one decal (52+53+54) | seam pattern strip recessed hull machine trim paint tileable |
| 61 | 0 | 0.0073 | 1 | 0.0552 | 2048x98 | double strip: bevel strip + bevelled seam as one decal (57+58) | seam strip recessed hull trim paint tileable |

Outlines (UV points in order; the piece's quad or polygon uses the same points as positions and UVs):

- 23 pipe elbow: thin bent pipe, L-shaped (outline; its box would cover the small square plate): (0.1239, 0.742), (0.1967, 0.7426), (0.2099, 0.7471), (0.2185, 0.7547), (0.2232, 0.7624), (0.2257, 0.7725), (0.2257, 0.8448), (0.2104, 0.8448), (0.2104, 0.7744), (0.2071, 0.7652), (0.2017, 0.7602), (0.1949, 0.7579), (0.1239, 0.7579)

**Panel lines** [HARD, read from the `_ng` and `_cm` textures, used on a model]: strips 51, 54 and 58 here and
Atlas4 piece 3 are panel seams. Their colour is a flat mid grey and the line comes from the normal map, so put
them on the paintable variant (`PanelingColorable`, `Atlas4_Colorable`) on painted surfaces or the dark one
(`PanelingDarker`, `Atlas4_Darker`) on dark fixed metal, not on `Decals` (which would paint a grey band).
Keen's choice [HARD, measured on 60 vanilla models]: newer blocks use Atlas4 piece 3, in the variant that matches
the surface under it; classic blocks use strip 58 or 61; no vanilla model uses 51 or 54 as a seam. Keen's line width:
13-23 mm (median 16) on newer large-grid blocks, 7-12 mm (median 10) on small grid, 29-51 mm (median 37) on classic
blocks (one user also found 1 cm right and 2 cm heavy on a part about 1.3 m across [SOFT]). Map V exactly across
the piece's box (Atlas4 piece 3 is transparent outside it, so a quad whose V runs past the box draws narrower than
the quad) and U along
its length; U past 1 wraps within the same strip, so a long ring or seam can use `u = length * 0.5`. Where Keen
puts lines (insets, spacing, corners, how much of a face): `keen-style.md`, "Panel lines". Build the
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
**Lines on a material border** [owner, rendered: a chrome plate outlined in a dark gap]: a seam line that separates
two textures (a plate's outline where the material changes, the foot of a raised part) is centred on that border,
half on each side, never inset inside one of them. Inset, the strip leaves a sliver of the inner surface between its
outer edge and the border, and the sliver shows as a thin light (or dark) edge on the wrong side of the line. Build
the material border and the line from the same centre polyline so they cannot drift apart. At the foot of a raised
part (a pad, a lip) lay only the half strip on the open side: centre line on the foot, V from the middle of the box
to its outer edge; the other half would lie under the part. Keen's centred door does the same (`keen-style.md`,
"Panel lines", Examples).
**Inherited seams** [owner: had to ask for every junction to be mitred on a deck another author laid]: these
rules cover every seam on the model, not only the ones you lay. When you take over a model (another author's
pass, a vanilla kitbash), list its seam junctions and line ends first and fix them before adding decals. Seen:
single quads with square ends overlapping at every join, rim lines stopping inside a corner pad, and a vanilla
joint line tapering to nothing just past a cross seam. Rebuild such a network as closed, mitred outlines plus
pointed stems, outlines first in the mesh.
**Pointing a vanilla half strip** [HARD, rendered]: Keen often lays a line as two half-width strips whose outer V
runs past the piece's box into transparent atlas, so only part of each quad's width shows. Cut to a point the
plain way, its visible edge ends short of the tip and leaves a dark notch. Move each side corner back from the
tip by the cross seam's half-width divided by `frac`, the visible share of the strip's width:
`frac = (box_edge - v_centre) / (v_outer - v_centre)` in V.

**Groove direction** [HARD, read from the `_ng` texture of `Decals_Atlas_A_01`; owner saw the jog]: piece 51's
groove is lopsided. Across the strip its normal map tilts towards `v1` over the first 11 px and towards `v0`
over the last 16 px, so the wide wall is on the `v1` side. Two strips laid in opposite directions meet with a
visible jog, most often where one seam wraps from one face onto the next. Pick one rule in world space and use it
for the whole model, for example `v1` towards the rear for seams running across the block, `v1` towards +X for
seams running front to back, and the same side (inside or outside) all the way round a closed outline. Apply it
when building each strip (reverse the polyline when its first segment's `v1` side breaks the rule), then check
it: from each seam face's positions and UVs, solve the world direction V increases in and count the faces that
break the rule. Piece 58 is one-sided by design; measure 54 the same way before using it.
**Mirrored faces** [HARD, rendered]: to copy a face's decals onto its mirror (the bottom deck of a two-sided
plate, the far side of a symmetric block), negate the mirrored axis, reverse each face's vertex order and keep
the UVs. Negating alone flips the face to point inward and mirrors the art; with the winding reversed, (U, V,
normal) stays right-handed, text and arrows read the right way and the groove keeps its side.
**Overlap order inside one decal mesh** [SOFT: GPUs draw a mesh's triangles in index order; seen in a render,
not yet in game]: where a stem's tip overlaps its cross seam, the face drawn later shows. Sort the faces so the
cross seams and outlines come first (`bm.faces.sort(key=...)`, then `bm.faces.index_update()`), and keep the 1 mm
lift above for the Blender view.

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

| id | u0 | v0 | u1 | v1 | px | piece | tags |
|---|---|---|---|---|---|---|---|
| 1 | 0.0205 | 0.8604 | 0.0977 | 0.9805 | 79x123 | letter A | text glyph flat hull console cargo |
| 2 | 0.1709 | 0.8604 | 0.249 | 0.9805 | 80x123 | letter B | text glyph flat hull console cargo |
| 3 | 0.3203 | 0.8604 | 0.3994 | 0.9805 | 81x123 | letter C | text glyph flat hull console cargo |
| 4 | 0.4639 | 0.8604 | 0.542 | 0.9805 | 80x123 | letter D | text glyph flat hull console cargo |
| 5 | 0.6143 | 0.8604 | 0.6855 | 0.9805 | 73x123 | letter E | text glyph flat hull console cargo |
| 6 | 0.752 | 0.8604 | 0.8242 | 0.9805 | 74x123 | letter F | text glyph flat hull console cargo |
| 7 | 0.8828 | 0.8604 | 0.9609 | 0.9805 | 80x123 | letter G | text glyph flat hull console cargo |
| 8 | 0.0205 | 0.6943 | 0.0918 | 0.8164 | 73x125 | letter H | text glyph flat hull console cargo |
| 9 | 0.168 | 0.6943 | 0.1836 | 0.8145 | 16x123 | letter I | text glyph flat hull console cargo |
| 10 | 0.248 | 0.6943 | 0.3125 | 0.8164 | 66x125 | letter J | text glyph flat hull console cargo |
| 11 | 0.3857 | 0.6943 | 0.46 | 0.8164 | 76x125 | letter K | text glyph flat hull console cargo |
| 12 | 0.5215 | 0.6943 | 0.5801 | 0.8164 | 60x125 | letter L | text glyph flat hull console cargo |
| 13 | 0.6348 | 0.6943 | 0.75 | 0.8164 | 118x125 | letter M | text glyph flat hull console cargo |
| 14 | 0.8164 | 0.6943 | 0.8926 | 0.8164 | 78x125 | letter N | text glyph flat hull console cargo |
| 15 | 0.0195 | 0.5283 | 0.0986 | 0.6484 | 81x123 | letter O | text glyph flat hull console cargo |
| 16 | 0.1709 | 0.5283 | 0.2471 | 0.6484 | 78x123 | letter P | text glyph flat hull console cargo |
| 17 | 0.3154 | 0.5107 | 0.3984 | 0.6484 | 85x141 | letter Q | text glyph flat hull console cargo |
| 18 | 0.4668 | 0.5283 | 0.5439 | 0.6484 | 79x123 | letter R | text glyph flat hull console cargo |
| 19 | 0.6094 | 0.5283 | 0.7031 | 0.6484 | 96x123 | letter S | text glyph flat hull console cargo |
| 20 | 0.7539 | 0.5283 | 0.8389 | 0.6484 | 87x123 | letter T | text glyph flat hull console cargo |
| 21 | 0.8984 | 0.5283 | 0.9746 | 0.6504 | 78x125 | letter U | text glyph flat hull console cargo |
| 22 | 0.0156 | 0.3623 | 0.0986 | 0.4844 | 85x125 | letter V | text glyph flat hull console cargo |
| 23 | 0.1641 | 0.3623 | 0.2871 | 0.4844 | 126x125 | letter W | text glyph flat hull console cargo |
| 24 | 0.3516 | 0.3623 | 0.4375 | 0.4844 | 88x125 | letter X | text glyph flat hull console cargo |
| 25 | 0.4961 | 0.3623 | 0.5811 | 0.4844 | 87x125 | letter Y | text glyph flat hull console cargo |
| 26 | 0.6416 | 0.3623 | 0.7266 | 0.4824 | 87x123 | letter Z | text glyph flat hull console cargo |
| 27 | 0.7822 | 0.3623 | 0.8564 | 0.4502 | 76x90 | small x, below cap height (alternate X) | text glyph flat hull console cargo |
| 28 | 0.041 | 0.1963 | 0.0752 | 0.3164 | 35x123 | digit 1 | text glyph flat hull console cargo |
| 29 | 0.1602 | 0.1963 | 0.2461 | 0.3164 | 88x123 | digit 2 | text glyph flat hull console cargo |
| 30 | 0.3037 | 0.1963 | 0.3867 | 0.3164 | 85x123 | digit 3 | text glyph flat hull console cargo |
| 31 | 0.4521 | 0.1963 | 0.5342 | 0.3164 | 84x123 | digit 4 | text glyph flat hull console cargo |
| 32 | 0.5879 | 0.1963 | 0.6768 | 0.3164 | 91x123 | digit 5 | text glyph flat hull console cargo |
| 33 | 0.7402 | 0.1963 | 0.8281 | 0.3164 | 90x123 | digit 6 | text glyph flat hull console cargo |
| 34 | 0.8779 | 0.1963 | 0.9648 | 0.3164 | 89x123 | digit 7 | text glyph flat hull console cargo |
| 35 | 0.0156 | 0.0215 | 0.1016 | 0.1416 | 88x123 | digit 8 | text glyph flat hull console cargo |
| 36 | 0.1572 | 0.0215 | 0.2422 | 0.1416 | 87x123 | digit 9 | text glyph flat hull console cargo |
| 37 | 0.3027 | 0.0215 | 0.3877 | 0.1416 | 87x123 | digit 0 | text glyph flat hull console cargo |
| 38 | 0.4688 | 0.0137 | 0.792 | 0.1641 | 331x154 | human silhouette, lying on its side (head to the right, one arm raised) | marking glyph flat console cargo |
