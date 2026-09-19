#!/usr/bin/env bash
# Pre-publication secret scan for THIS repository (two-round workflow).
# Round 1: working tree. Round 2 (after `git add`): run with --staged.
# Usage:
#   bash scripts/secret-scan.sh            # scan working tree (tracked + untracked)
#   bash scripts/secret-scan.sh --staged   # scan `git diff --cached` staged content
set -uo pipefail
cd "$(dirname "$0")/.."

if [ "${1:-}" = "--staged" ]; then
  echo "== round 2: staged content scan =="
  diff_target="$(git diff --cached --unified=0)"
  if [ -z "$diff_target" ]; then echo "nothing staged"; exit 0; fi
  scan() { printf '%s' "$diff_target" | grep -inE -e "$1" && return 1; return 0; }
else
  echo "== round 1: working-tree scan =="
  scan() { grep -rniE --exclude-dir=.git --exclude=SHA256SUMS --exclude=PRIVATE_EVIDENCE_INDEX.md -e "$1" . && return 1; return 0; }
fi

fail=0
check() {
  local label="$1" pattern="$2"
  if scan "$pattern"; then
    echo "  ok    : $label"
  else
    echo "  HIT   : $label"
    fail=1
  fi
}

check "api keys          " "api[_-]?key['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}"
check "bearer/authorization" "(bearer\s+[A-Za-z0-9_\-\.]{16,}|authorization:\s*['\"]?[A-Za-z0-9_\-\.]{16,})"
check "github tokens     " "github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,}"
check "openai-style keys " "\bsk-[A-Za-z0-9]{16,}\b"
check "aws access keys   " "\bAKIA[0-9A-Z]{16}\b"
check "private key blocks" "-----BEGIN [A-Z ]*PRIVATE KEY-----"
check "passwords/secrets " "(password|secret)['\"]?\s*[:=]\s*['\"][^'\"]{12,}"
check "oss signatures    " "(x-oss-signature|security[_-]?token)['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9+/]{16,}"
check "cookies           " "se[t]-coo[k]ie|coo[k]ie:\s"
check "jwt-shaped tokens " "\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"

echo
echo "NOTE: generic identity scans (usernames, hostnames, project names, device ids)"
echo "must be run with scripts/scan-sensitive-paths.py --identity ... because the"
echo "withheld values are machine-specific and are NOT embedded in this repository."
echo
[ "$fail" -eq 0 ] && echo "SECRET SCAN: PASS" || { echo "SECRET SCAN: FAIL — do not push; fix first"; exit 1; }
