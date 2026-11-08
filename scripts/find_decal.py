"""Find decal atlas pieces by tag or description word (references/atlas-regions.md, "Tags").

  python find_decal.py vent round          pieces matching every word (tag, variant word or description text)
  python find_decal.py fastener -hex       a leading '-' excludes a word
  python find_decal.py seam --sheet Decals_Atlas_A_01 --tags-only
  python find_decal.py                     list the tag words with their counts

A word matches a tag exactly, one of the sheet's variant words (plain, colorable, darker, verydark, chrome,
yellow), or any part of the description. --tags-only skips the description. Boxes print as u0 v0 u1 v1 in
Blender UV convention; an 'outline' piece needs the outline listed under its table in atlas-regions.md.
"""
import argparse, os, re, sys
from collections import Counter

MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'atlas-regions.md')
ROW = re.compile(r'^\| (\d+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| (\d+x\d+) \| ([^|]+)\| ([^|]+)\|\s*$')
MAT = re.compile(r'^\| `([^`]+)` \| ([^|]+)\|')


def load(path):
    """Return (pieces, variant words per sheet) parsed from atlas-regions.md."""
    pieces, variants, sheet, in_mats = [], {}, None, False
    for line in open(path, encoding='utf-8'):
        if line.startswith('## '):
            sheet = line[3:].strip(); in_mats = sheet.startswith('Which materials'); continue
        if in_mats and (m := MAT.match(line)):
            variants[m.group(1)] = set(re.findall(r'\((\w+)\)', m.group(2)))
        elif (m := ROW.match(line)):
            pieces.append(dict(sheet=sheet, id=int(m.group(1)), box=m.group(2, 3, 4, 5), px=m.group(6),
                               desc=m.group(7).strip(), tags=m.group(8).split()))
    return pieces, variants


def matches(p, words, variants, tags_only):
    known = set(p['tags']) | variants.get(p['sheet'], set())
    text = '' if tags_only else p['desc'].lower()
    hit = lambda w: w in known or (len(w) > 2 and w in text)
    return all(not hit(w[1:]) if w.startswith('-') else hit(w) for w in words)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('words', nargs='*', help='words that must all match; -word excludes')
    ap.add_argument('--sheet', help='only this atlas (prefix, case-insensitive)')
    ap.add_argument('--tags-only', action='store_true', help='match tags and variant words, not description text')
    ap.add_argument('--md', default=MD, help='path to atlas-regions.md')
    # pull out '-word' exclusions first so argparse does not read '-hex' as '-h'
    argv = sys.argv[1:]
    excl = [w for w in argv if re.fullmatch(r'-[^-].+', w)]
    a = ap.parse_args([w for w in argv if w not in excl])
    a.words += excl
    pieces, variants = load(a.md)
    if a.sheet: pieces = [p for p in pieces if p['sheet'].lower().startswith(a.sheet.lower())]
    if not a.words:
        c = Counter(t for p in pieces for t in p['tags'])
        print(' '.join(f'{t} {n}' for t, n in c.most_common())); return
    hits = [p for p in pieces if matches(p, [w.lower() for w in a.words], variants, a.tags_only)]
    for p in hits:
        print(f"{p['sheet']} {p['id']}  {' '.join(p['box'])}  {p['px']}  {p['desc']}  [{' '.join(p['tags'])}]")
    print(f'{len(hits)} pieces', file=sys.stderr)


if __name__ == '__main__':
    main()
