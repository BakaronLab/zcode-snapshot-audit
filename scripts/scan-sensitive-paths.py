#!/usr/bin/env python3
"""Scan a directory for identity leakage before publication, and run the
SENSITIVE_KEY_PATTERN synthetic escape test (F-013) with --selftest.

Identity scan: pass the strings that must never appear with --identity
(repeatable). Generic scans run by default: secret-shaped patterns, private-key
blocks, long-hex residues (configurable).

Usage:
  python3 scripts/scan-sensitive-paths.py <dir> \
      --identity realname --identity 'C:\\Users\\realname' --identity devicemid-value \
      [--allow-hex-in 'SHA256SUMS','evidence/artifact-hashes.md'] [--max-hex 16]
  python3 scripts/scan-sensitive-paths.py --selftest
"""
import os
import re
import sys

SECRET_PATTERNS = [
    r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}",
    r"(?i)(authorization|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{16,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"\bghp_[A-Za-z0-9]{20,}\b",
    r"\bsk-[A-Za-z0-9]{16,}\b",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)(secret|password|token)\s*[:=]\s*['\"][^'\"]{12,}",
    r"(?i)accesskey(id|secret)?\s*[:=]",
    r"(?i)security[-_]?token\s*[:=]\s*['\"]?[A-Za-z0-9]{10,}",
    r"(?i)signature\s*[:=]\s*['\"]?[A-Za-z0-9+/=]{16,}",
    r"(?i)cookie\s*[:=]\s*[^;\s]{12,}",
]


def selftest():
    # Exact pattern from zcode-server.cjs:310362 (see EVIDENCE.md F-013).
    P = re.compile(r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password"
                   r"|credential|authorization|cookie|session[_-]?token|token)$", re.I)
    print("SENSITIVE_KEY_PATTERN synthetic escape test (synthetic key names only):\n")
    rows = [("LLM_KEY", False), ("CUSTOM_PROVIDER_CREDENTIAL", True), ("MY_AUTH", False),
            ("PROVIDER_CRED", False), ("MODEL_ACCESS", False), ("API_KEY", True),
            ("apiKey", True), ("access_token", True), ("AUTHORIZATION", True),
            ("my_secret", True), ("TOKEN", True), ("llm-apikey-value", False),
            ("openai_key_value", False), ("bearerValue", False),
            ("auth_header_value", False), ("service_account_json", False)]
    ok = True
    for name, expected_redacted in rows:
        got = bool(P.search(name))
        ok &= (got == expected_redacted)
        print(f"  {name:32s} -> {'REDACTED' if got else 'ESCAPES'}")
    print("\nNote: the client only redacts when the KEY NAME (end-anchored) matches;")
    print("values embedding secrets under non-matching keys are not redacted (F-013).")
    sys.exit(0 if ok else 1)


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        selftest()
        return
    if not args:
        print(__doc__)
        sys.exit(1)
    root = args[0]
    identities = []
    allow_hex = set()
    max_hex = 16
    i = 1
    while i < len(args):
        if args[i] == "--identity":
            identities.append(args[i + 1])
            i += 2
        elif args[i] == "--allow-hex-in":
            allow_hex |= {x.strip() for x in args[i + 1].split(",")}
            i += 2
        elif args[i] == "--max-hex":
            max_hex = int(args[i + 1])
            i += 2
        else:
            i += 1
    hexre = re.compile(r"[0-9a-fA-F]{%d,}" % max_hex)
    violations = []
    for dirpath, _dirs, files in os.walk(root):
        _dirs[:] = [d for d in _dirs if d != ".git"]
        for fn in files:
            if fn in ("PRIVATE_EVIDENCE_INDEX.md", "SHA256SUMS"):
                continue  # local-only index and self-referential sums are excluded by design
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            try:
                text = open(p, errors="ignore").read()
            except Exception:
                continue
            low = text.lower()
            for ident in identities:
                if ident and ident.lower() in low:
                    violations.append((rel, f"IDENTITY: {ident[:6]}…"))
            for pat in SECRET_PATTERNS:
                for m in re.finditer(pat, text):
                    frag = m.group(0)
                    # skip documentation examples that are obviously placeholders
                    if re.search(r"<[A-Z_]+>|REDACTED|your[_-]?token|example", frag, re.I):
                        continue
                    violations.append((rel, f"SECRET-PATTERN: {pat} :: {frag[:40]}…"))
            if rel not in allow_hex and not rel.endswith(("artifact-hashes.md",
                                                          "hashes.md", "cryptography-flow.md")):
                for m in hexre.findall(text):
                    violations.append((rel, f"HEX{max_hex}+: {m[:20]}…"))
    print(f"scanned {root}: {len(violations)} potential violations")
    for rel, why in violations[:40]:
        print(f"  {rel}: {why}")
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
