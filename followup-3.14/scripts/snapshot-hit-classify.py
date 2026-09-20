#!/usr/bin/env python3
"""Attribute every occurrence of a token in a bundle to its owning esbuild module.

Used in the ZCode 3.14.0 follow-up to classify all surviving occurrences of the word
`snapshot` in the new server bundle: each hit is attributed to its owning module (nearest
preceding `// path.ts` comment) and the local context is classified as identifier, string
literal, or comment. That turns "775 hits" into a per-module table in which every module
can be shown to belong to an unrelated subsystem.

Usage:
    python3 snapshot-hit-classify.py <bundle> [token]     # token defaults to "snapshot"

Counting convention: case-sensitive raw occurrences of `token` (pass `Snapshot` or
`SNAPSHOT` separately for the capitalized forms).

The script reads the bundle as UTF-8 text and does all offset arithmetic in character
space, so multi-byte content earlier in the file cannot misalign module attribution.
Context classification is deliberately crude -- it is a triage aid, not a parser: a hit on
a line containing a `//` before it is reported as a comment, a hit inside an unbalanced
quote character as a string literal, and everything else as identifier/code.
"""

import bisect
import re
import sys
from collections import Counter

MODULE_COMMENT = re.compile(r'^//\s+(\S+\.(?:ts|tsx|js|mjs|cjs|json))\s*$')


def analyse(path, token):
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8", "replace")

    segments = []          # (start_offset, module_name)
    offset = 0
    for line in text.split("\n"):
        match = MODULE_COMMENT.match(line)
        if match:
            segments.append((offset, match.group(1).replace("\\", "/")))
        offset += len(line) + 1
    segments.append((len(text), "<END>"))
    starts = [start for start, _ in segments]

    per_module = Counter()
    kinds = Counter()
    sample_lines = {}
    for found in re.finditer(re.escape(token), text):
        index = found.start()
        owner = segments[bisect.bisect_right(starts, index) - 1][1]
        per_module[owner] += 1
        line_start = text.rfind("\n", 0, index) + 1
        line_end = text.find("\n", index)
        line = text[line_start:line_end if line_end >= 0 else len(text)]
        before = text[line_start:index]
        if "//" in before:
            kind = "comment" if before.count('"') % 2 == 0 else "code/string"
        elif before.count('"') % 2 == 1 or before.count("'") % 2 == 1 or before.count("`") % 2 == 1:
            kind = "string-literal"
        else:
            kind = "identifier/code"
        kinds[kind] += 1
        if owner not in sample_lines and kind == "identifier/code":
            sample_lines[owner] = line.strip()[:120]
    return per_module, kinds, sample_lines


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__.strip(), file=sys.stderr)
        raise SystemExit(2)
    bundle = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) == 3 else "snapshot"
    per_module, kinds, sample_lines = analyse(bundle, token)
    total = sum(per_module.values())
    print(f"# token={token!r} bundle={bundle}")
    print(f"# total hits={total} across {len(per_module)} modules")
    print(f"# context kinds: {dict(kinds)}")
    print()
    print("| hits | module |")
    print("|---|---|")
    for module, count in per_module.most_common():
        print(f"| {count} | `{module}` |")
