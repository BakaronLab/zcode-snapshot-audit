#!/usr/bin/env python3
"""Name-independent behavioural-equivalence scan over a source tree.

Question: does any single source module co-occur with the five signals that
characterised the audited repo-snapshot pipeline?

    A archive             : tar / gzip / targz / archiver
    B upload              : upload / postobject / putobject / multipart
    C manifest            : manifest
    D workspace enumerat. : ls-files / --cached / --others / exclude-standard / reflog
    E prompt trigger      : capturestage / beforeprompt / beforesend / prompt.content

Signals are matched case-insensitively as substrings against each file's text.
The score is the number of distinct signals present; it is a co-occurrence test,
not a semantic one, and a module scoring high is a *lead to read*, not a verdict.

Usage:
    python3 behavior-equivalence-scan.py <source-tree> [min-score]

Output: per-module scores at or above min-score (default 3), plus histograms.
Only paths and counts are emitted; no source content.
"""

import os
import re
import sys

SIGNALS = {
    # `tar` is a substring of start/target/avatar, so it is anchored as a word.
    "A_archive": [r"\btar\b", r"tar\.gz", r"targz", r"gzip", r"archiver"],
    "B_upload": [r"\bupload", r"postobject", r"putobject", r"multipart"],
    "C_manifest": [r"\bmanifest"],
    "D_enumeration": [
        r"ls-files",
        r"--cached",
        r"--others",
        r"exclude-standard",
        r"\breflog\b",
        r"packed-refs",
        r"lost-found",
    ],
    "E_trigger": [
        r"capturestage",
        r"\bbeforeprompt\b",
        r"\bbeforesend\b",
        r"prompt\.content",
        r"promptcontent",
    ],
}

# Repository-walk evidence: an *.git* metadata collection path. Anchored so that
# identifiers such as `gitDirtyFileCount` do not read as `gitdir`.
GIT_META = [r"\.git/objects", r"\.git/index", r"logs/HEAD", r"\bgitdir\b", r"\.git[/\"']"]

TEXT_EXT = {".ts", ".tsx", ".js", ".mjs", ".cjs", ".jsx", ".json", ".mts", ".cts"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", "out", ".next", "coverage", "__pycache__"}


def iter_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1] in TEXT_EXT:
                yield os.path.join(dirpath, fn)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = sys.argv[1]
    min_score = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    total = 0
    hist = {}
    high = []
    for path in iter_files(root):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read().lower()
        except OSError:
            continue
        total += 1
        hit = {}
        for name, pats in SIGNALS.items():
            for p in pats:
                if re.search(p, text):
                    hit[name] = p
                    break
        score = len(hit)
        hist[score] = hist.get(score, 0) + 1
        if score >= min_score:
            git_meta = any(re.search(p, text) for p in GIT_META)
            rel = os.path.relpath(path, root)
            high.append((score, git_meta, rel, sorted(hit.keys())))

    print(f"source tree : {root}")
    print(f"files scored: {total}")
    print()
    print("score histogram (distinct signals present):")
    for k in sorted(hist, reverse=True):
        print(f"  {k}/5 : {hist[k]}")
    print()
    print(f"modules scoring >= {min_score}/5  (score, .git-metadata-evidence, path):")
    for score, gm, rel, hits in sorted(high, key=lambda x: (-x[0], x[2])):
        flag = "GIT-META" if gm else "        "
        print(f"  [{score}/5] {flag} {rel}")
        print(f"          signals: {','.join(hits)}")
    if not high:
        print("  (none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
