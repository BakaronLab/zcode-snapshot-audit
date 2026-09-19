#!/usr/bin/env python3
"""List .git-related entries in a repo-snapshot manifest (read-only).

Shows that .git/objects, .git/logs, .git/config, pack files and >1 MB entries
are inside the snapshot scope (EVIDENCE.md F-008/F-009).

Usage: python3 scripts/inspect-git-inclusion.py <manifest.json> [--min-size N]
"""
import json
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    min_size = 0
    if "--min-size" in sys.argv:
        min_size = int(sys.argv[sys.argv.index("--min-size") + 1])
    d = json.load(open(sys.argv[1]))
    files = d.get("files", [])
    git = [f for f in files if str(f.get("path", "")).startswith(".git/")]

    print(f"total entries: {len(files)}   .git/** entries: {len(git)}\n")

    def count(prefix):
        sub = [f for f in git if f["path"].startswith(prefix)]
        return len(sub), sum(f["sizeBytes"] for f in sub)

    for label, prefix in [(".git/objects/**", ".git/objects/"), (".git/logs/**", ".git/logs/"),
                          (".git/refs/**", ".git/refs/"), (".git/worktrees/**", ".git/worktrees/")]:
        n, b = count(prefix)
        print(f"  {label:22s} {n:6d} entries  {b:,} bytes")

    print(f"\n  .git/config present : {any(f['path'] == '.git/config' for f in git)}")
    print(f"  .git/index present  : {any(f['path'] == '.git/index' for f in git)}")

    packs = sorted((f for f in git if "/pack/" in f["path"] and f["path"].endswith(".pack")),
                   key=lambda f: -f["sizeBytes"])
    if packs:
        print(f"\n  pack files ({len(packs)}):")
        for f in packs[:5]:
            print(f"    {f['sizeBytes']:>12,} B  (name redacted)")

    big = [f for f in git if f["sizeBytes"] > max(min_size, 1024 * 1024)]
    print(f"\n  .git entries LARGER than 1 MB: {len(big)}   "
          f"(scanner limit REPO_SNAPSHOT_MAX_FILE_BYTES = 1,024*1,024 does not stop these — F-009)")
    for f in sorted(big, key=lambda x: -x["sizeBytes"])[:10]:
        print(f"    {f['sizeBytes']:>12,} B  {f['path']}")


if __name__ == "__main__":
    main()
