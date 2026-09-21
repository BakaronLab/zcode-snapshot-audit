#!/usr/bin/env python3
"""Map module-path comments in a frozen ZCode server bundle to official source paths.

The shipped server bundle is an esbuild single-file output. esbuild preserves a
`// <relative-path>` comment above each bundled module. Those comments are relative
to the bundle's entry directory (e.g. `// ../services/src/feedback/...`), which lets
us reconstruct the original monorepo layout as:

    ../<pkg>/src/<rest>      ->  packages/<pkg>/src/<rest>
    ../../node_modules/<x>   ->  (third-party, not part of the audited source tree)

This script compares that reconstructed set against a checkout of the official
source repository and classifies every bundle module.

Usage:
    python3 source-binary-map.py <bundle.cjs> <official-source-checkout>

Output is counts + path lists only. No source content is emitted.
"""

import os
import re
import subprocess
import sys

COMMENT_RE = re.compile(r"^// ((?:\.\./)+[A-Za-z0-9_@][A-Za-z0-9_./@-]*)\.(ts|tsx|js|json)$")

# Bundled workspace packages that live under packages/ in the official monorepo.
WORKSPACE_PKGS = {
    "services",
    "shared",
    "provider",
    "provider-node",
    "client",
    "server",
    "rpc",
    "web",
    "desktop",
    "ui",
    "zcode-cua",
    "zcode-server-cli",
    "model-option-map",
    "formal-proof",
}


def bundle_modules(bundle_path: str):
    """Return raw module comment paths found in the bundle (comments only)."""
    found = set()
    with open(bundle_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = COMMENT_RE.match(line.rstrip("\n"))
            if m:
                found.add(f"{m.group(1)}.{m.group(2)}")
    return found


def normalize(raw: str):
    """Map a bundle comment to ('workspace', source-path) or ('thirdparty', path)."""
    while raw.startswith("../"):
        raw = raw[3:]
    if raw.startswith("node_modules/") or "/node_modules/" in raw:
        return "thirdparty", raw
    top = raw.split("/", 1)[0]
    if top in WORKSPACE_PKGS:
        return "workspace", f"packages/{raw}"
    # e.g. `apps/zcode-cli/src/...` or other workspace roots
    return "workspace", raw


def source_files(checkout: str):
    out = subprocess.run(
        ["git", "-C", checkout, "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return set(p for p in out.split("\n") if p)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    bundle_path, checkout = sys.argv[1], sys.argv[2]

    raw = bundle_modules(bundle_path)
    norm = {}
    for r in raw:
        kind, path = normalize(r)
        norm.setdefault(kind, set()).add(path)

    src = source_files(checkout)

    ws = norm.get("workspace", set())
    tp = norm.get("thirdparty", set())

    # Direct match: the exact source path exists in the official tree.
    direct = sorted(p for p in ws if p in src)

    # Source-tree directories implied by the bundle but absent from the official tree.
    missing = sorted(p for p in ws if p not in src)

    # Group the missing ones by their top-level package directory, which is the
    # interesting quantity: an entire subsystem missing reads differently from a
    # handful of renamed files.
    missing_by_dir = {}
    for p in missing:
        parts = p.split("/")
        # packages/<pkg>/src/<sub>/<file> -> packages/<pkg>/src/<sub>
        key = "/".join(parts[:4]) if len(parts) >= 4 else "/".join(parts[:3])
        missing_by_dir.setdefault(key, []).append(p)

    print(f"bundle                  : {bundle_path}")
    print(f"official source checkout: {checkout}")
    print(f"official tracked files  : {len(src)}")
    print()
    print(f"bundle module comments  : {len(raw)}")
    print(f"  third-party           : {len(tp)}")
    print(f"  workspace             : {len(ws)}")
    print(f"    DIRECT_NAME_MATCH   : {len(direct)}")
    print(f"    MISSING_IN_SOURCE   : {len(missing)}")
    if ws:
        print(f"    match rate          : {100.0 * len(direct) / len(ws):.1f}%")
    print()
    print("MISSING_IN_SOURCE grouped by source directory:")
    for k in sorted(missing_by_dir):
        files = sorted(missing_by_dir[k])
        print(f"  [{len(files):3d}] {k}")
        if len(files) <= 12:
            for f in files:
                print(f"          {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
