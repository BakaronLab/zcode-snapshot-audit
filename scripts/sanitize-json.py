#!/usr/bin/env python3
"""Recursive redaction for JSON files destined for publication.

Replaces: home-directory paths, Windows user paths, drive-letter project paths,
64-hex manifest/content hashes, UUID-shaped device/session ids. Values can be
overridden per key name.

Usage:
  python3 scripts/sanitize-json.py <input.json> <output.json> \
      [--map '/home/OLDNAME=/home/<USER>'] [--map 'OLDPROJECT=project-a'] ...
"""
import json
import os
import re
import sys

DEFAULT_KEY_REDS = re.compile(
    r"(device|session|query|request|snapshot|workspace|task|user)id$", re.I)
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")


def build_remaps(pairs):
    out = []
    for p in pairs or []:
        if "=" in p:
            a, b = p.split("=", 1)
            out.append((a, b))
    return out


def sanitize(obj, remaps, key_reds=DEFAULT_KEY_REDS, depth=0):
    if depth > 24:
        return "<TRUNCATED>"
    if isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            if key_reds.search(str(k)) and isinstance(v, str) and len(v) > 24:
                res[k] = "<REDACTED>"
            else:
                res[k] = sanitize(v, remaps, key_reds, depth + 1)
        return res
    if isinstance(obj, list):
        return [sanitize(x, remaps, key_reds, depth + 1) for x in obj]
    if isinstance(obj, str):
        s = obj
        for a, b in remaps:
            if a in s:
                s = s.replace(a, b)
        s = HEX64.sub("<MANIFEST_HASH>", s)
        s = UUID.sub("<ID>", s)
        return s
    return obj


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    src, dst = args[0], args[1]
    remaps = build_remaps(args[2:])
    remaps_default = build_remaps([f"/home/{os.environ.get('AUDIT_REAL_USER', '')}=/home/<USER>"]) \
        if os.environ.get("AUDIT_REAL_USER") else []
    data = sanitize(json.load(open(src)), remaps + remaps_default)
    with open(dst, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    print(f"sanitized: {src} -> {dst}")


if __name__ == "__main__":
    main()
