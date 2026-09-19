#!/usr/bin/env bash
# Locate the repo-snapshot subsystem inside the installed ZCode server bundle.
# Usage:
#   bash scripts/locate-snapshot-code.sh
#   bash scripts/locate-snapshot-code.sh --embedding-check
#   bash scripts/locate-snapshot-code.sh --wsl-gate-check
set -uo pipefail

SRV="${ZCODE_SERVER_BUNDLE:-${ZCODE_HOME:-$HOME/.zcode}/server/zcode-server.cjs}"
[ -f "$SRV" ] || { echo "server bundle not found: $SRV (set ZCODE_SERVER_BUNDLE)"; exit 1; }

hdr() { echo; echo "== $1 =="; }

hdr "upload-credential endpoint + origin constants"
grep -n 'upload-credential\|DEFAULT_ZCODE_ENDPOINT_ORIGIN\|TEST_ZCODE_ENDPOINT_ORIGIN' "$SRV" | head

hdr "sidecar construction (expect unconditional new RepoSnapshotSidecarService)"
grep -n 'new RepoSnapshotSidecarService' "$SRV"

hdr "capture triggers"
grep -n 'captureBeforePrompt\|captureRepoWikiSnapshot\|captureTaskCompleteUpdate\|scheduleRepoSnapshotSidecar' "$SRV" | head

hdr "workspaceIdentity capture gate (expect the early-return inside captureBeforePrompt)"
n=$(grep -n 'async captureBeforePrompt(params)' "$SRV" | head -1 | cut -d: -f1)
[ -n "$n" ] && sed -n "${n},$((n+8))p" "$SRV" | cut -c1-200

hdr "workspace key builder (identity || path)"
grep -n 'function buildRepoSnapshotWorkspaceKey' "$SRV"

hdr "git enumeration + .git metadata walker"
grep -n 'ls-files\|walkGitMetadataFiles\|appendRootGitMetadataPaths\|skipDirectoryNames' "$SRV" | head

hdr ".git short-circuit before secret/size filters"
grep -n 'shouldIncludeRepoSnapshotPathBeforeSample\|looksLikeSecretPath\|REPO_SNAPSHOT_MAX_FILE_BYTES' "$SRV" | head

hdr "global configs collector + key-name-only sanitize"
grep -n 'GLOBAL_CONFIG_PATHS\|SENSITIVE_KEY_PATTERN' "$SRV" | head

hdr "encryption"
grep -n 'aes-256-ctr\|RSA_PKCS1_OAEP_PADDING\|oaepHash\|keyWrapAlgorithm' "$SRV" | head

hdr "repoSnapshotIndexingEnabled occurrences (expect 4: schema/optional/normalization/key-list — NO gate)"
grep -n 'repoSnapshotIndexingEnabled' "$SRV"

hdr "uploaded settings key list (settings values themselves are uploaded)"
grep -n 'REPO_SNAPSHOT_SETTINGS_BEHAVIOR_KEYS' "$SRV" | head -3

hdr "pending cleanup"
grep -n 'encryptedArtifactPath\|pendingCleanup\|rm -i\|unlink' "$SRV" | head -5

hdr "no download/restore endpoint (expect 0 hits)"
grep -c 'snapshot/download\|snapshot/restore\|restoreSnapshot\|downloadSnapshot' "$SRV" || true

if [ "${1:-}" = "--embedding-check" ]; then
  hdr "embedding / vector-store check"
  echo "server bundle embedding hits        : $(grep -c 'embedding' "$SRV" || true)"
  echo "server bundle vector-store hits     : $(grep -c 'sqlite-vec\|qdrant\|lancedb\|chromadb\|hnsw\|faiss' "$SRV" || true)"
  ASAR="${ZCODE_ASAR:-/opt/ZCode/resources/app.asar}"
  if [ -f "$ASAR" ]; then
    echo "desktop asar 'embedding' occurrences: $(grep -ao 'embedding' "$ASAR" | wc -l)"
    echo "  (asar hits sit in packaged THIRD-PARTY code: primarily AI-SDK model libraries"
    echo "   like @ai-sdk/*/embedding-model, plus unrelated assets such as opentelemetry/"
    echo "   xterm/shiki/wolfram data. Not evidence of an application-level indexing pipeline.)"
  fi
fi

if [ "${1:-}" = "--wsl-gate-check" ]; then
  hdr "wsl co-occurrence with snapshot symbols (expect 0 -> no WSL-specific snapshot condition)"
  grep -i 'wsl' "$SRV" | grep -ic 'snapshot\|sidecar\|captureBefore' || true
fi
