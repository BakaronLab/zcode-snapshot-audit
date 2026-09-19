#!/usr/bin/env python3
"""Summarize a ZCode repo-snapshot manifest: totals, .git share, bytes (read-only).

Usage: python3 scripts/summarize-manifest.py <manifest.json> [more.json ...]
"""
import glob
import json
import os
import sys


def summarize(path):
    d = json.load(open(path))
    files = d.get("files", [])
    git = [f for f in files if str(f.get("path", "")).startswith(".git/")]
    objs = [f for f in git if "/objects/" in f.get("path", "")]
    logs = [f for f in git if f.get("path", "").startswith(".git/logs/")]
    gsum = sum(f["sizeBytes"] for f in git)
    tsum = sum(f["sizeBytes"] for f in files)
    print(f"== {os.path.basename(path)} ==")
    print(f"  schema          : {d.get('schema')}")
    print(f"  createdAt       : {d.get('createdAt')}")
    print(f"  total files     : {len(files)}")
    print(f"  .git/** entries : {len(git)} ({100 * len(git) / max(1, len(files)):.1f}% of entries)")
    print(f"  .git/objects/** : {len(objs)}   .git/logs/**: {len(logs)}")
    print(f"  .git bytes      : {gsum:,} ({100 * gsum / max(1, tsum):.1f}% of listed bytes)")
    print(f"  .git/config     : {any(f['path'] == '.git/config' for f in git)}")
    print(f"  lost-found      : {any('/lost-found/' in f['path'] for f in git)}")
    for f in sorted(git, key=lambda x: -x["sizeBytes"])[:3]:
        p = f["path"]
        if len(p) > 90:
            p = p[:45] + "…<redacted>…" + p[-20:]
        print(f"  largest .git    : {p}  {f['sizeBytes']:,} B")
    print()


def main():
    paths = []
    for a in sys.argv[1:]:
        paths.extend(sorted(glob.glob(a)) or [a])
    if not paths:
        print(__doc__)
        sys.exit(1)
    for p in paths:
        try:
            summarize(p)
        except Exception as e:
            print(f"{p}: ERROR {e}\n")


if __name__ == "__main__":
    main()
