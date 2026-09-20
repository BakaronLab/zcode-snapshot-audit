#!/usr/bin/env python3
"""Extract esbuild module-path comments from a bundle and diff the module sets.

Both ZCode server bundles preserve the original module paths as `// ../path/to/module.ts`
comments emitted by esbuild. Diffing those comment sets shows which *whole subsystems*
were deleted between two builds -- evidence that goes beyond individual symbols going to
zero.

Usage:
    python3 module-diff.py <old-bundle> <new-bundle>

Output is JSON: module-comment counts, unique-module counts, and the sorted removed and
added module lists. Nothing is written to disk.

Note: this script reads the bundles as UTF-8 text and never slices bytes with character
offsets, so multi-byte content earlier in the file cannot skew the results.
"""

import json
import re
import sys

MODULE_COMMENT = re.compile(r'^//\s+(\S+\.(?:ts|tsx|js|mjs|cjs|json))\s*$')


def modules(path):
    """Ordered list of (module_path, line_index) taken from the bundle's comments."""
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8", "replace")
    found = []
    for index, line in enumerate(text.split("\n")):
        match = MODULE_COMMENT.match(line)
        if match:
            found.append((match.group(1).replace("\\", "/"), index))
    return found


def main(old_path, new_path):
    old = modules(old_path)
    new = modules(new_path)
    old_set = {path for path, _ in old}
    new_set = {path for path, _ in new}
    return {
        "old_module_count": len(old),
        "new_module_count": len(new),
        "old_unique": len(old_set),
        "new_unique": len(new_set),
        "removed_count": len(old_set - new_set),
        "added_count": len(new_set - old_set),
        "removed": sorted(old_set - new_set),
        "added": sorted(new_set - old_set),
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(main(sys.argv[1], sys.argv[2]), indent=1))
