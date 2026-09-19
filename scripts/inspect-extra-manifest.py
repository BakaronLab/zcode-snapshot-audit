#!/usr/bin/env python3
"""Summarize a ZCode extra-manifest (global-config group listing), read-only.

Usage: python3 scripts/inspect-extra-manifest.py <extra-manifest.json>
"""
import json
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    d = json.load(open(sys.argv[1]))
    print(f"schema   : {d.get('schema')}")
    print(f"createdAt: {d.get('createdAt')}")
    stats = d.get("stats") or {}
    print(f"stats    : {stats}")
    for g in d.get("groups", []):
        print(f"\ngroup: {g.get('groupId')}  changePolicy: {g.get('changePolicy')}")
        for f in g.get("files", []):
            name = f.get("path", "<redacted>")
            print(f"  - {name:28s} {f.get('sizeBytes', 0):>9,} B   source: {f.get('source')}")
    known = {"settings.behavior.json", "mcp.json", "skills.json", "commands.json", "hooks.json",
             "plugins.json", "memory.json", "subagents.json", "instructions.json"}
    names = {f.get("path") for g in d.get("groups", []) for f in g.get("files", [])}
    print(f"\ncollected global-config names present: {sorted(n for n in names if n)}")
    print(f"(client GLOBAL_CONFIG_PATHS covers: {sorted(known)})")


if __name__ == "__main__":
    main()
