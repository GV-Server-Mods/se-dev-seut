"""Compare the vertex normals of a modded .mwm with the vanilla .mwm it was built from.

Standard library only, any Python 3:

    python mwm_normals_vs_vanilla.py <vanilla.mwm> <modded.mwm> [more modded.mwm ...]

For every modded vertex that sits on a vanilla vertex position (to 1 mm), prints the angle to the nearest
vanilla normal at that position: median, 90th percentile, maximum and the count over 5 degrees. Vertices with
no vanilla vertex at their position (a part you added) are counted as unmatched and skipped. A vanilla main
model that only points at its LODs has no vertices: pass its `_LOD0.mwm` instead.

Normals are stored packed (`VF_Packer.PackNormal`), so an untouched vanilla mesh still reads up to about
1.4 degrees off. Anything over 5 degrees is a real change. The nearest-normal test is lenient: a corner that took
another face's normal at the same point reads 0, so it shows a broken mesh but undercounts it.
"""
import math
import struct
import sys
from collections import defaultdict


def r7(b, p):
    v = s = 0
    while True:
        c = b[p]; p += 1; v |= (c & 0x7F) << s
        if c < 0x80:
            return v, p
        s += 7


def rstr(b, p):
    n, p = r7(b, p)
    return b[p:p + n].decode("utf-8"), p + n


def tags(path):
    """-> {tag name: offset of the tag's data, after its name}"""
    b = open(path, "rb").read()
    p = rstr(b, 0)[1]
    nh = struct.unpack_from("<i", b, p)[0]; p += 4
    for _ in range(nh):
        p = rstr(b, p)[1]
    n = struct.unpack_from("<i", b, p)[0]; p += 4
    out = {}
    for _ in range(n):
        t, p = rstr(b, p)
        out[t] = rstr(b, struct.unpack_from("<i", b, p)[0])[1]; p += 4
    return b, out


def load(path):
    b, t = tags(path)
    if "Vertices" not in t:
        sys.exit(path + " has no vertices (a main model that only lists its LODs?): pass its _LOD0.mwm")
    p = t["Vertices"]; n = struct.unpack_from("<i", b, p)[0]
    r = struct.unpack_from("<%de" % (4 * n), b, p + 4)
    pos = [(r[i] * r[i + 3], r[i + 1] * r[i + 3], r[i + 2] * r[i + 3]) for i in range(0, 4 * n, 4)]
    p = t["Normals"]; n = struct.unpack_from("<i", b, p)[0]
    nrm = []
    for (v,) in struct.iter_unpack("<I", b[p + 4:p + 4 + 4 * n]):
        x = (v & 0x7FFF) / 32767 * 2 - 1; s = 1 if v & 0x8000 else -1; y = (v >> 16) / 32767 * 2 - 1
        nrm.append((x, y, s * math.sqrt(max(0.0, 1 - x * x - y * y))))
    return pos, nrm


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    key = lambda p: tuple(round(c * 1000) for c in p)
    van = defaultdict(list)
    for p, n in zip(*load(sys.argv[1])):
        van[key(p)].append(n)
    for path in sys.argv[2:]:
        angs, miss = [], 0
        for p, n in zip(*load(path)):
            cand = van.get(key(p))
            if not cand:
                miss += 1
                continue
            dots = (max(-1.0, min(1.0, sum(a * b for a, b in zip(n, c)))) for c in cand)
            angs.append(math.degrees(math.acos(max(dots))))
        angs.sort()
        print(path)
        if not angs:
            print("  no vertex sits on a vanilla vertex")
            continue
        print("  matched %d, unmatched %d; median %.1f, p90 %.1f, max %.1f deg; over 5 deg: %d"
              % (len(angs), miss, angs[len(angs) // 2], angs[int(len(angs) * 0.9)], angs[-1], sum(a > 5 for a in angs)))


if __name__ == "__main__":
    main()
