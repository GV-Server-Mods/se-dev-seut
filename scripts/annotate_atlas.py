"""Draw numbered region boxes on the atlas previews written by extract_atlas_regions.py.

Usage: python annotate_atlas.py <dir containing regions.json and *_prev.png>

Needs Pillow. Writes <atlas>_annotated.png next to each preview (upscaled to 1024 px for legibility).
Region numbers match the `id` column in references/atlas-regions.md.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

SCALE = 1024


def main(folder):
    with open(os.path.join(folder, "regions.json")) as f:
        data = json.load(f)
    for name, info in data.items():
        prev = os.path.join(folder, name + "_prev.png")
        if "regions" not in info or not os.path.exists(prev):
            continue
        img = Image.open(prev).convert("RGB").resize((SCALE, SCALE), Image.LANCZOS)
        draw = ImageDraw.Draw(img)
        for r in info["regions"]:
            x0, x1 = r["u0"] * SCALE, r["u1"] * SCALE
            y0, y1 = (1 - r["v1"]) * SCALE, (1 - r["v0"]) * SCALE   # PNG rows run top to bottom
            draw.rectangle([x0, y0, x1, y1], outline=(255, 60, 60), width=2)
            draw.rectangle([x0, y0, x0 + 8 * len(str(r["id"])) + 6, y0 + 14], fill=(255, 60, 60))
            draw.text((x0 + 3, y0 + 1), str(r["id"]), fill=(255, 255, 255))
        img.save(os.path.join(folder, name + "_annotated.png"))
        print(name, len(info["regions"]))


if __name__ == "__main__":
    main(sys.argv[1])
