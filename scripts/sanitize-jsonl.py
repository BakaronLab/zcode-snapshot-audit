#!/usr/bin/env python3
"""Recursive redaction for JSONL/line-oriented logs destined for publication.

Applies user-supplied literal replacements plus generic id/hash/uuid scrubbing to
every line. Supports --window to keep only lines near a matching anchor
(e.g. T-5min..T+5min around an event).

Usage:
  python3 scripts/sanitize-jsonl.py <input> <output> \
      [--map 'REALNAME=<USER>'] [--map 'REALPROJECT=project-a'] \
      [--anchor 'regex-pattern'] [--context 300]
"""
import re
import sys

HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    src, dst = args[0], args[1]
    remaps = []
    anchor = None
    ctx = 300
    i = 2
    while i < len(args):
        if args[i] == "--map":
            a, b = args[i + 1].split("=", 1)
            remaps.append((a, b))
            i += 2
        elif args[i] == "--anchor":
            anchor = re.compile(args[i + 1])
            i += 2
        elif args[i] == "--context":
            ctx = int(args[i + 1])
            i += 2
        else:
            i += 1

    lines = open(src, errors="ignore").read().splitlines()
    keep = list(range(len(lines)))
    if anchor:
        hits = [i for i, ln in enumerate(lines) if anchor.search(ln)]
        keep = sorted({j for h in hits for j in range(max(0, h - ctx), min(len(lines), h + ctx + 1))})
    with open(dst, "w") as out:
        for i in keep:
            s = lines[i]
            for a, b in remaps:
                s = s.replace(a, b)
            s = HEX64.sub("<HASH>", s)
            s = UUID.sub("<UUID>", s)
            out.write(s + "\n")
    print(f"sanitized {len(keep)}/{len(lines)} lines -> {dst}")


if __name__ == "__main__":
    main()
