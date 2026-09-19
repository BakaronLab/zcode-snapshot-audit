#!/usr/bin/env bash
# Canary verification of the checkpoint-directory mitigation.
# Implements steps 5-6 of docs/mitigation.md: search for snapshot artifacts
# created after a marker file, with and without an applied chattr lock.
# Usage:
#   bash scripts/verify-snapshot-disabled.sh prepare   # create marker (run BEFORE using ZCode on the canary)
#   bash scripts/verify-snapshot-disabled.sh check     # search for new artifacts; report verdict
set -euo pipefail

ZCODE_HOME="${ZCODE_HOME:-$HOME/.zcode}"
CKPT="${ZCODE_CHECKPOINTS:-$ZCODE_HOME/v2/checkpoints}"
MARKER="${TMPDIR:-/tmp}/zcode-canary-start.txt"

case "${1:-check}" in
  prepare)
    date -Is > "$MARKER"
    echo "marker written: $MARKER"
    echo "now: (1) lock with 'sudo chattr +i $CKPT' if desired,"
    echo "     (2) create/use a canary workspace in ZCode with a few prompts,"
    echo "     (3) run '$0 check'"
    if [ -d "$CKPT" ] && ! touch "$CKPT/.canary-write-test" 2>/dev/null; then
      echo "note: $CKPT is NOT writable (lock likely active)"
    else
      [ -f "$CKPT/.canary-write-test" ] && rm -f "$CKPT/.canary-write-test"
      echo "note: $CKPT is writable (no lock active)"
    fi
    ;;
  check)
    [ -f "$MARKER" ] || { echo "no marker; run '$0 prepare' first"; exit 1; }
    echo "== artifacts newer than $(cat "$MARKER") =="
    hits=0
    while IFS= read -r -d '' f; do
      echo "  NEW: $f"; hits=$((hits+1))
    done < <(find "$ZCODE_HOME/v2" -type f \( -name 'state.json' -o -name '*.enc' -o -name '*.tar.gz' \) \
              -newer "$MARKER" -print0 2>/dev/null)
    for win in /mnt/c/Users/*/.zcode/v2; do
      [ -d "$win" ] || continue
      while IFS= read -r -d '' f; do echo "  NEW(Win): $f"; hits=$((hits+1)); done < \
        <(find "$win" -type f \( -name 'state.json' -o -name '*.enc' \) -newer "$MARKER" -print0 2>/dev/null)
    done
    if [ "$hits" -eq 0 ]; then
      echo "MITIGATION VERIFIED on this build/machine: no new snapshot artifacts after marker."
      echo "Caveat: not a permanent guarantee; re-verify after every ZCode update (docs/mitigation.md)."
    else
      echo "MITIGATION NOT VERIFIED: $hits new snapshot artifact(s) appeared. Inspect the paths above."
      exit 1
    fi
    ;;
  *)
    echo "usage: $0 {prepare|check}"; exit 1 ;;
esac
