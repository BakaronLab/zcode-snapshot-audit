#!/usr/bin/env python3
"""Summarize local ZCode repo-snapshot checkpoint artifacts (read-only).

Usage:
  python3 scripts/inspect-checkpoints.py ~/.zcode/v2/checkpoints
  python3 scripts/inspect-checkpoints.py --sqlite          # local CLI db stats
  python3 scripts/inspect-checkpoints.py --census          # file-type census
"""
import glob
import json
import os
import re
import sqlite3
import sys
from datetime import datetime

WORKSPACE_ID = re.compile(r"^[0-9a-f]{12}$")


def fmt_ts(ms):
    try:
        return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ms)


def inspect_checkpoints(root):
    dirs = sorted(d for d in glob.glob(os.path.join(root, "*")) if os.path.isdir(d))
    print(f"checkpoint roots: {len(dirs)}\n")
    for d in dirs:
        wid = os.path.basename(d)
        wid_disp = wid if WORKSPACE_ID.match(wid) else "<WORKSPACE_ID>"
        state_p = os.path.join(d, "state.json")
        print(f"== workspace {wid_disp} ==")
        if os.path.isfile(state_p):
            try:
                st = json.load(open(state_p))
            except Exception as e:
                print(f"  state.json: PARSE ERROR {e}")
                st = {}
            lcs = st.get("lastCompressedSize") or {}
            print(f"  lastAcceptedManifestHash present : {bool(st.get('lastAcceptedManifestHash'))}")
            print(f"  lastCompressedSize               : encrypted={lcs.get('encryptedSizeBytes')} "
                  f"workspace={lcs.get('workspaceSizeBytes')} at {fmt_ts(lcs.get('recordedAt', 0))}")
            print(f"  failureCount                     : {st.get('failureCount')}")
            ws = st.get("workspaceKey") or st.get("workspacePath") or ""
            print(f"  workspaceKey is a raw path       : {ws.startswith(('/', 'C:', 'F:'))} "
                  f"(identity empty at capture time)")
        manifests = glob.glob(os.path.join(d, "manifests", "*.json"))
        extras = glob.glob(os.path.join(d, "extra-manifests", "*.json"))
        print(f"  manifests: {len(manifests)}  extra-manifests: {len(extras)}")
        if manifests:
            try:
                m = json.load(open(sorted(manifests)[-1]))
                files = m.get("files", [])
                git = [f for f in files if str(f.get("path", "")).startswith(".git/")]
                print(f"  newest manifest: {len(files)} files, {len(git)} .git/** "
                      f"({100 * len(git) / max(1, len(files)):.1f}%)")
            except Exception:
                pass
        print()


def census(root):
    counts = {}
    for p in glob.glob(os.path.join(root, "**", "*"), recursive=True):
        if not os.path.isfile(p):
            continue
        base = os.path.basename(p)
        kind = "state.json" if base == "state.json" else re.sub(r"[0-9a-f]{16,}", "<64hex>", base)
        counts[kind] = counts.get(kind, 0) + 1
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"{v:6d}  {k}")
    enc = [k for k in counts if ".enc" in k or ".tar" in k or "tmp" in k]
    print("\npending/encrypted residue:", "NONE (post-success cleanup)" if not enc else enc)


def sqlite_stats():
    db = os.path.join(os.environ.get("ZCODE_HOME", os.path.expanduser("~/.zcode")),
                      "cli", "db", "db.sqlite")
    if not os.path.isfile(db):
        print(f"not found: {db}")
        return
    print(f"db: {db} ({os.path.getsize(db):,} bytes)  [opened read-only]")
    con = sqlite3.connect(f"file:{db}?mode=ro&immutable=1", uri=True)
    cur = con.cursor()
    tables = [r[0] for r in cur.execute("select name from sqlite_master where type='table' order by name")]
    for t in tables:
        try:
            n = cur.execute(f'select count(*) from "{t}"').fetchone()[0]
        except Exception:
            n = "?"
        print(f"  {t:24s} {n}")
    con.close()
    print("\n(note: schema only; message/prompt content is NOT printed and must not be published)")


def main():
    args = sys.argv[1:]
    if "--sqlite" in args:
        sqlite_stats()
        return
    root = next((a for a in args if not a.startswith("--")),
                os.path.join(os.environ.get("ZCODE_HOME", os.path.expanduser("~/.zcode")), "v2", "checkpoints"))
    if not os.path.isdir(root):
        print(f"checkpoints dir not found: {root}\n(set ZCODE_HOME or pass the path explicitly)")
        return
    if "--census" in args:
        census(root)
    else:
        inspect_checkpoints(root)
        print("--- file-type census ---")
        census(root)


if __name__ == "__main__":
    main()
