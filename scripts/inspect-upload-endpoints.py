#!/usr/bin/env python3
"""Extract upload/OSS endpoint evidence and callback fields from the server bundle,
and telemetry endpoints from the desktop asar (read-only binary grep).

Usage:
  python3 scripts/inspect-upload-endpoints.py              # server bundle
  python3 scripts/inspect-upload-endpoints.py --telemetry  # desktop asar
"""
import os
import re
import sys


def srv():
    p = os.environ.get("ZCODE_SERVER_BUNDLE",
                       os.path.join(os.environ.get("ZCODE_HOME", os.path.expanduser("~/.zcode")),
                                    "server", "zcode-server.cjs"))
    if not os.path.isfile(p):
        print(f"not found: {p}")
        sys.exit(1)
    src = open(p, errors="ignore").read()
    print(f"bundle: {p}\n")

    print("== endpoint constants ==")
    for m in re.finditer(r'"[^"]*upload-credential[^"]*"', src):
        print("  ", m.group(0))
    for m in re.finditer(r'https?://[a-zA-Z0-9._-]*zcode[a-zA-Z0-9._-]*', src):
        print("  origin-like host:", m.group(0))

    print("\n== getUploadCredential request shape ==")
    i = src.find("async getUploadCredential")
    if i > 0:
        print(src[i:i + 700].replace("\n", " ")[:700])

    print("\n== OSS form fields + callback keys ==")
    for pat in [r'"x-oss-[a-z-]+"', r'"success_action_status"', r'"x:encrypted_aes_key"',
                r'"x:base_snapshot_id"', r'"checksum"', r'"update_type"', r'"attribution"',
                r'"callback"']:
        keys = sorted(set(re.findall(pat, src)))
        if keys:
            print("  ", keys)

    print("\n== crypto ==")
    for pat in [r'"aes-256-ctr"', r'"RSA-OAEP-256"', r'oaepHash:\s*"[^"]+"',
                r'keyWrapAlgorithm:\s*"[^"]+"', r'contentAlgorithm:\s*"[^"]+"']:
        vals = sorted(set(re.findall(pat, src)))
        if vals:
            print("  ", vals)


def telemetry():
    p = os.environ.get("ZCODE_ASAR", "/opt/ZCode/resources/app.asar")
    if not os.path.isfile(p):
        print(f"not found: {p} (set ZCODE_ASAR)")
        sys.exit(1)
    print(f"asar: {p}  (binary grep, read-only)\n")
    pat = re.compile(rb'https?://[a-zA-Z0-9._-]*(?:rum|arms|sls|aliyuncs|xtrace|telemetry|beacon)[a-zA-Z0-9._-]*')
    hits = {}
    with open(p, "rb") as fh:
        data = fh.read()
    for m in pat.finditer(data):
        s = m.group(0).decode(errors="ignore")
        hits[s] = hits.get(s, 0) + 1
    for s, n in sorted(hits.items(), key=lambda kv: -kv[1]):
        print(f"  {n:4d}  {s}")
    print("\nendpoint presence confirmed; payload composition NOT extracted (UNKNOWN).")


if __name__ == "__main__":
    telemetry() if "--telemetry" in sys.argv else srv()
