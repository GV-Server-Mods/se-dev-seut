"""Find the decal pieces in the vanilla SE decal atlases.

Run inside Blender (Blender's Python has numpy), for example through the Blender MCP:

    ASSET_TEXTURES = r"C:\\SE_Assets\\Textures\\Models\\Cubes"
    OUT_DIR = r"C:\\path\\to\\output"
    exec(open(r"<repo>\\scripts\\extract_atlas_regions.py").read())

For each atlas it reads the alpha mask (white = opaque), labels connected pieces, merges pieces whose
boxes overlap (inner holes, slats), and writes `regions.json` plus `<atlas>_prev.png` (the colour
texture over a dark background, mask applied). UV values use Blender's convention: (0, 0) is the bottom
left of the image, so they can be typed straight into the UV editor.

Then run `annotate_atlas.py` with a normal Python that has Pillow to draw numbered boxes on the previews.
"""
import json
import os

import bpy
import numpy as np

ASSET_TEXTURES = globals().get("ASSET_TEXTURES", r"C:\SE_Assets\Textures\Models\Cubes")
OUT_DIR = globals().get("OUT_DIR", os.path.join(os.path.expanduser("~"), "atlas_out"))
SIZE = 512          # analysis resolution; regions are reported as fractions of the full image
MIN_PIXELS = 12     # ignore specks smaller than this at SIZE x SIZE
ERODE = globals().get("ERODE", {"Atlas1": 1, "Atlas2": 2, "Decals_Atlas_A_01": 2})   # atlas -> erosion passes before labelling

# atlas name -> (alpha mask file, colour file) without extension
ATLASES = globals().get("ATLASES", {
    "Atlas1": ("Atlas1_alphamask", "Atlas1Colorable_cm"),
    "Atlas2": ("Atlas2_alphamask", "Atlas2_cm"),
    "Atlas3": ("Atlas3_alphamask", "Atlas3_Colorable_cm"),
    "Atlas4": ("Atlas4_alphamask", "Atlas4_Colorable_cm"),
    "ButtonsAtlas": ("ButtonsAtlas_alphamask", "ButtonsAtlas_Colorable_cm"),
    "Decals_Atlas_A_01": ("Decals_Atlas_A_01_alphamask", "Decals_Atlas_A_01_cm"),
    "TextAtlas": ("TextAtlas_alphamask", "TextAtlas_cm"),
})


def load(name):
    path = os.path.join(ASSET_TEXTURES, name + ".TIF")
    if not os.path.exists(path):
        return None, None
    img = bpy.data.images.load(path, check_existing=False)
    try:
        img.alpha_mode = 'CHANNEL_PACKED'
        full = tuple(img.size)
        img.scale(SIZE, SIZE)
        buf = np.empty(SIZE * SIZE * 4, dtype=np.float32)
        img.pixels.foreach_get(buf)
    finally:
        bpy.data.images.remove(img)
    return buf.reshape(SIZE, SIZE, 4), full   # row 0 is the bottom of the image (v = 0)


def label(mask):
    h, w = mask.shape
    lab = np.zeros(mask.shape, dtype=np.int32)
    count = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] == 0:
                count += 1
                lab[y, x] = count
                stack = [(y, x)]
                while stack:
                    cy, cx = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = count
                            stack.append((ny, nx))
    return lab, count


def boxes_from_labels(lab, count):
    boxes = []
    for i in range(1, count + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < MIN_PIXELS:
            continue
        boxes.append([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1, len(ys)])
    return boxes


def merge_overlapping(boxes):
    """Merge boxes that intersect, repeatedly, so a frame and the slats inside it become one piece."""
    boxes = [list(b) for b in boxes]
    changed = True
    while changed:
        changed = False
        out = []
        for b in boxes:
            for o in out:
                if b[0] < o[2] and o[0] < b[2] and b[1] < o[3] and o[1] < b[3]:
                    o[0], o[1] = min(o[0], b[0]), min(o[1], b[1])
                    o[2], o[3] = max(o[2], b[2]), max(o[3], b[3])
                    o[4] += b[4]
                    changed = True
                    break
            else:
                out.append(b)
        boxes = out
    return boxes


def cluster_specks(boxes, small=14, pad=5):
    """Group tiny neighbouring boxes (rivet or dot fields) into one piece."""
    tiny = [b for b in boxes if max(b[2] - b[0], b[3] - b[1]) <= small]
    rest = [b for b in boxes if max(b[2] - b[0], b[3] - b[1]) > small]
    padded = merge_overlapping([[b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad, b[4]] for b in tiny])
    clustered = [[b[0] + pad, b[1] + pad, b[2] - pad, b[3] - pad, b[4]] for b in padded]
    return merge_overlapping(rest + clustered)


def _runs(flags, min_gap):
    """Split a 1-D flag array into spans separated by at least min_gap false entries."""
    spans, start, gap = [], None, 0
    for i, f in enumerate(flags):
        if f:
            if start is None:
                start = i
            gap = 0
            end = i + 1
        elif start is not None:
            gap += 1
            if gap >= min_gap:
                spans.append((start, end))
                start = None
    if start is not None:
        spans.append((start, end))
    return spans


def xy_cut(mask, x0, y0, x1, y1, min_gap=3):
    """Split a box along empty rows and columns (guillotine cuts) until nothing more separates."""
    sub = mask[y0:y1, x0:x1]
    if not sub.any():
        return []
    ys, xs = np.where(sub)
    x0, x1, y0, y1 = x0 + xs.min(), x0 + xs.max() + 1, y0 + ys.min(), y0 + ys.max() + 1
    sub = mask[y0:y1, x0:x1]
    for axis in (1, 0):
        spans = _runs(sub.any(axis=axis), min_gap)
        if len(spans) > 1:
            out = []
            for a, b in spans:
                if axis == 1:
                    out += xy_cut(mask, x0, y0 + a, x1, y0 + b, min_gap)
                else:
                    out += xy_cut(mask, x0 + a, y0, x0 + b, y1, min_gap)
            return out
    return [[x0, y0, x1, y1, int(sub.sum())]]


def split_big(boxes, mask, min_area=0.12):
    """Boxes that cover a large part of the atlas are usually several touching pieces: cut them."""
    out = []
    for b in boxes:
        if (b[2] - b[0]) * (b[3] - b[1]) > min_area * SIZE * SIZE:
            out += xy_cut(mask, b[0], b[1], b[2], b[3])
        else:
            out.append(b)
    return out


def merge_thin_rows(boxes, thin=8, max_gap=12):
    """Join thin strips that sit on the same row (tileable trim broken into fragments)."""
    boxes = [list(b) for b in boxes]
    changed = True
    while changed:
        changed = False
        for i, a in enumerate(boxes):
            for j in range(i + 1, len(boxes)):
                b = boxes[j]
                if min(a[3] - a[1], b[3] - b[1]) > thin:
                    continue
                if a[1] < b[3] and b[1] < a[3] and a[0] < b[2] + max_gap and b[0] < a[2] + max_gap:
                    a[:] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), a[4] + b[4]]
                    del boxes[j]
                    changed = True
                    break
            if changed:
                break
    return boxes


# Pieces that touch cannot be separated automatically. Give rough rectangles (x0, y0, x1, y1) in the
# 1024 px annotated preview (y down); each is snapped to the opaque pixels inside it and replaces the
# automatic boxes it covers.
SPLIT_HINTS = globals().get("SPLIT_HINTS", {
    "Decals_Atlas_A_01": [
        (3, 160, 128, 226), (136, 172, 184, 210), (130, 160, 232, 262), (3, 227, 64, 284),
        (78, 231, 114, 280), (284, 178, 310, 292), (3, 318, 314, 545), (3, 547, 190, 705),
        (191, 543, 354, 705), (320, 322, 416, 417), (422, 320, 508, 417), (360, 419, 442, 609),
        (452, 419, 542, 609), (512, 163, 670, 384), (546, 390, 640, 452), (562, 458, 614, 600),
        (660, 390, 720, 450), (660, 470, 720, 530), (660, 552, 720, 605), (348, 622, 804, 670),
        (737, 193, 1023, 482), (744, 483, 794, 572), (798, 478, 1023, 705),
    ],
})


def apply_hints(boxes, mask, hints):
    snapped = []
    for x0, y0, x1, y1 in hints:
        sx0, sx1 = int(x0 / 1024 * SIZE), int(round(x1 / 1024 * SIZE))
        sy0, sy1 = int((1024 - y1) / 1024 * SIZE), int(round((1024 - y0) / 1024 * SIZE))   # mask rows run bottom to top
        ys, xs = np.where(mask[sy0:sy1, sx0:sx1])
        if len(ys):
            snapped.append([sx0 + xs.min(), sy0 + ys.min(), sx0 + xs.max() + 1, sy0 + ys.max() + 1, len(ys)])
    covered = lambda b: any(h[0] <= (b[0] + b[2]) / 2 <= h[2] and h[1] <= (b[1] + b[3]) / 2 <= h[3] for h in snapped)
    holder = lambda b: any(b[0] <= (h[0] + h[2]) / 2 <= b[2] and b[1] <= (h[1] + h[3]) / 2 <= b[3] for h in snapped)
    return [b for b in boxes if not covered(b) and not (holder(b) and (b[2] - b[0]) * (b[3] - b[1]) > 0.05 * SIZE * SIZE)] + snapped


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    result = {}
    for name, (mask_name, color_name) in ATLASES.items():
        mask_px, full = load(mask_name)
        color_px, _ = load(color_name)
        if mask_px is None or color_px is None:
            result[name] = {"error": "missing " + (mask_name if mask_px is None else color_name)}
            continue
        mask = mask_px[:, :, 0] > 0.5
        # Erode first for atlases whose pieces touch through thin bridges, then grow the boxes back.
        k = ERODE.get(name, 0)
        eroded = mask.copy()
        for _ in range(k):
            eroded = (eroded & np.roll(eroded, 1, 0) & np.roll(eroded, -1, 0)
                      & np.roll(eroded, 1, 1) & np.roll(eroded, -1, 1))
        lab, count = label(eroded)
        boxes = [[max(b[0] - k, 0), max(b[1] - k, 0), min(b[2] + k, SIZE), min(b[3] + k, SIZE), b[4]]
                 for b in boxes_from_labels(lab, count)]
        boxes = cluster_specks(merge_overlapping(boxes))
        boxes = merge_thin_rows(cluster_specks(split_big(boxes, mask)))
        if name in SPLIT_HINTS:
            boxes = apply_hints(boxes, mask, SPLIT_HINTS[name])
        regions = [{
            "u0": round(b[0] / SIZE, 3), "v0": round(b[1] / SIZE, 3),
            "u1": round(b[2] / SIZE, 3), "v1": round(b[3] / SIZE, 3),
            "w_px": int(round((b[2] - b[0]) / SIZE * full[0])),
            "h_px": int(round((b[3] - b[1]) / SIZE * full[1])),
        } for b in boxes]
        # reading order: top row to bottom, then left to right (row bands of 6% of the image)
        regions.sort(key=lambda r: (-round((r["v0"] + r["v1"]) / 2 / 0.06), r["u0"]))
        for i, r in enumerate(regions, 1):
            r["id"] = i
        result[name] = {"size": list(full), "regions": regions}

        rgb = np.where(mask[:, :, None], color_px[:, :, :3], 0.12)
        out = np.ones((SIZE, SIZE, 4), dtype=np.float32)
        out[:, :, :3] = np.clip(rgb, 0, 1) ** (1 / 2.2)
        img = bpy.data.images.new(name + "_prev", SIZE, SIZE, alpha=False)
        try:
            img.pixels.foreach_set(out.ravel())
            img.filepath_raw = os.path.join(OUT_DIR, name + "_prev.png")
            img.file_format = 'PNG'
            img.save()
        finally:
            bpy.data.images.remove(img)

    with open(os.path.join(OUT_DIR, "regions.json"), "w") as f:
        json.dump(result, f, indent=1)
    print({k: (v.get("error") or len(v["regions"])) for k, v in result.items()})


main()
