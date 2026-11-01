"""Print the dummies (empties) and bounding box stored in Space Engineers .mwm models.

Standard library only, any Python 3:

    python mwm_dummies.py <model.mwm> [more.mwm ...] [--blender main|subpart]

Reads the file the way the game does (`VRageRender.Import.MyModelImporter`: `LoadTagData`,
`ReadIndexDictionary`, `ReadDummies`). Values are in the model's own space as the game sees it: metres,
+Y up, forward -Z, right +X. For each dummy it prints:

- pos: the matrix translation.
- fwd, up: the matrix's Forward (minus the third row) and Up (second row), normalised.
- size: the length of each matrix row. A `detector_*` box is a unit cube scaled by the matrix
  (`MyUseObjectsComponent.RecreatePhysics`), so size is the box's edge lengths.
- custom data, such as `file` on a `subpart_*` dummy (the model it loads).

--blender main|subpart also prints pos, fwd and up in the axes of the SEUT scene type that exported the
file. SEUT exports main scenes with axis_forward 'Z' and subpart scenes with '-Z' (`seut_export_utils.py`),
so the two differ by a half turn about the up axis. Checked against a SEUT .blend and its exported .mwm: an
unrotated empty prints fwd (0, 1, 0) in both scene types, because a dummy's forward is the empty's local +Y.
"""
import argparse
import math
import struct

INDEXED_VERSION = 1066002   # files from this version on start with a tag index

# SE model space -> Blender scene space, per SEUT scene type
TO_BLENDER = {
    "main": lambda x, y, z: (-x, z, y),
    "subpart": lambda x, y, z: (x, -z, y),
}


def read_7bit_int(f):
    result = shift = 0
    while True:
        byte = f.read(1)[0]
        result |= (byte & 0x7F) << shift
        if byte < 0x80:
            return result
        shift += 7


def read_string(f):
    return f.read(read_7bit_int(f)).decode("utf-8")


def read_int(f):
    return struct.unpack("<i", f.read(4))[0]


def read_floats(f, count):
    return struct.unpack("<%df" % count, f.read(4 * count))


def read_dummies(f):
    dummies = []
    for _ in range(read_int(f)):
        name = read_string(f)
        matrix = read_floats(f, 16)
        data = {}
        for _ in range(read_int(f)):
            key = read_string(f)
            data[key] = read_string(f)
        dummies.append((name, matrix, data))
    return dummies


def read_model(path):
    """Return (version, bounding box or None, dummies)."""
    with open(path, "rb") as f:
        read_string(f)                                    # header tag name
        header = [read_string(f) for _ in range(read_int(f))]
        version = 0
        if header and "Version:" in header[0]:
            version = int(header[0].replace("Version:", ""))
        if version < INDEXED_VERSION:
            read_string(f)                                # old files start with the dummies
            return version, None, read_dummies(f)
        index = {}
        for _ in range(read_int(f)):
            tag = read_string(f)
            index[tag] = read_int(f)
        box = dummies = None
        if "BoundingBox" in index:
            f.seek(index["BoundingBox"])
            read_string(f)
            box = read_floats(f, 6)
        if "Dummies" in index:
            f.seek(index["Dummies"])
            read_string(f)
            dummies = read_dummies(f)
        return version, box, dummies or []


def fmt(vec):
    return "(" + ", ".join("%7.3f" % (v + 0.0) for v in vec) + ")"


def unit(vec):
    length = math.sqrt(sum(v * v for v in vec)) or 1.0
    return tuple(v / length for v in vec)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("models", nargs="+")
    parser.add_argument("--blender", choices=sorted(TO_BLENDER))
    args = parser.parse_args()
    for path in args.models:
        version, box, dummies = read_model(path)
        print("%s  (version %d, %d dummies)" % (path, version, len(dummies)))
        if box:
            size = [box[i + 3] - box[i] for i in range(3)]
            print("  bounding box min %s max %s size %s" % (fmt(box[:3]), fmt(box[3:]), fmt(size)))
        for name, m, data in dummies:
            pos = m[12:15]
            fwd = unit((-m[8], -m[9], -m[10]))
            up = unit(m[4:7])
            size = [math.sqrt(sum(v * v for v in m[r:r + 3])) for r in (0, 4, 8)]
            extra = "  " + " ".join("%s=%s" % kv for kv in sorted(data.items())) if data else ""
            print("  %s\n    pos %s  fwd %s  up %s  size %s%s" % (name, fmt(pos), fmt(fwd), fmt(up), fmt(size), extra))
            if args.blender:
                conv = TO_BLENDER[args.blender]
                print("    blender %s: pos %s  fwd %s  up %s" % (
                    args.blender, fmt(conv(*pos)), fmt(conv(*fwd)), fmt(conv(*up))))
        print()


if __name__ == "__main__":
    main()
