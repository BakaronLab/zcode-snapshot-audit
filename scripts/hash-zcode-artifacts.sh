#!/usr/bin/env bash
# Identify and hash installed ZCode program artifacts (read-only).
# Usage: bash scripts/hash-zcode-artifacts.sh
set -euo pipefail

ZCODE_HOME="${ZCODE_HOME:-$HOME/.zcode}"
ASAR="${ZCODE_ASAR:-/opt/ZCode/resources/app.asar}"

hash_one() {
  local f="$1" label="$2"
  if [ -f "$f" ]; then
    printf '%-24s %12s bytes  %s  %s\n  sha256: %s\n' "$label" "$(stat -c %s "$f")" "$(stat -c %y "$f" | cut -d. -f1)" "$f" "$(sha256sum "$f" | cut -d' ' -f1)"
  else
    printf '%-24s NOT FOUND (%s)\n' "$label" "$f"
  fi
}

hash_one "$ZCODE_HOME/server/zcode-server.cjs" "server bundle"
hash_one "$ASAR" "desktop app.asar"
if [ -d /opt/ZCode ]; then
  for exe in /opt/ZCode/zcode /opt/ZCode/chrome-sandbox; do
    [ -f "$exe" ] && hash_one "$exe" "$(basename "$exe")"
  done
fi
echo
echo "Compare the server bundle hash with evidence/artifact-hashes.md in the audit repository:"
echo "  identical  -> every line-number citation applies verbatim to your install"
echo "  different  -> server auto-updated; re-run scripts/locate-snapshot-code.sh instead"
