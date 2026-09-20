#!/usr/bin/env python3
"""Calibrated five-signal combination test.

Scores every module of an esbuild bundle on five behavioural signals and reports the
modules where they co-occur. The point of the test is that it is *calibrated*: run it on
the earlier build and it isolates exactly the module the published audit identified as the
repo-snapshot sidecar implementation; run it on ZCode 3.14.0 and it returns nothing.

    A archive                 tar, gzip
    B upload                  upload, postobject
    C manifest                manifest
    D workspace enumeration   ls-files, lsfiles, --cached, exclude-standard
    E prompt trigger          prompt.content, capturestage, beforeprompt, beforesend

Usage:
    python3 combination-test.py <bundle>

Prints the modules scoring >= 4 of 5 (the discriminating band) and the modules scoring
exactly 3 of 5 (disclosed so the boundary of the test is visible: the 3/5 band contains
unrelated modules in both builds and is therefore not a discriminator).

This is *calibrated negative evidence*, not a proof that no unknown implementation exists:
a functionally equivalent implementation written with entirely disjoint vocabulary and
structured so the five signals never co-occur in one module would not be detected.

Counting convention: signal matching is case-insensitive substring matching inside each
module's own text, and module boundaries come from the bundle's own `// path.ts` comments.
The script reads the bundle as UTF-8 text and slices in character space only, so multi-byte
content earlier in the file cannot misalign module attribution.
"""

import re
import sys

MODULE_COMMENT = re.compile(r'^//\s+(\S+\.(?:ts|tsx|js|mjs|cjs|json))\s*$')

SIGNALS = {
    "A_archive": ("tar", "gzip"),
    "B_upload": ("upload", "postobject"),
    "C_manifest": ("manifest",),
    "D_workspace_enumeration": ("ls-files", "lsfiles", "--cached", "exclude-standard"),
    "E_prompt_trigger": ("prompt.content", "capturestage", "beforeprompt", "beforesend"),
}


def segments(path):
    """(module_name, start, end) triples in character offsets."""
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8", "replace")
    found = []
    name = None
    start = 0
    offset = 0
    for line in text.split("\n"):
        match = MODULE_COMMENT.match(line)
        if match:
            if name is not None:
                found.append((name, start, offset))
            name = match.group(1).replace("\\", "/")
            start = offset
        offset += len(line) + 1
    if name is not None:
        found.append((name, start, len(text)))
    return text, found


def score(text, start, end):
    body = text[start:end].lower()
    matched = [key for key, tokens in SIGNALS.items() if any(t in body for t in tokens)]
    return len(matched), matched


def main(path):
    text, segs = segments(path)
    scored = []
    for name, start, end in segs:
        count, matched = score(text, start, end)
        if count >= 3:
            scored.append((count, name, end - start, matched))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return segs, scored


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        raise SystemExit(2)
    bundle = sys.argv[1]
    segments_found, scored = main(bundle)
    discriminating = [row for row in scored if row[0] >= 4]
    boundary = [row for row in scored if row[0] == 3]
    print(f"# {bundle}")
    print(f"# modules (esbuild comment segments): {len(segments_found)}")
    print(f"\n## modules scoring >= 4 of 5 (discriminating band): {len(discriminating)}")
    for count, name, size, matched in discriminating:
        print(f"  [{count}/5] {name}  ({size} B)  {','.join(matched)}")
    print(f"\n## modules scoring == 3 of 5 (disclosed boundary, not discriminating): {len(boundary)}")
    for count, name, size, matched in boundary:
        print(f"  [{count}/5] {name}  ({size} B)  {','.join(matched)}")
