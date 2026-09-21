#!/usr/bin/env bash
# Source-symbol probe for the official-source corroboration of the ZCode snapshot audit.
#
# Re-runs, against a checkout of the official zai-org/ZCode source tree, the exact
# symbol / module-name / path probes used in the 3.14 binary regression audit.
#
# Usage:
#   bash source-symbol-probe.sh /path/to/zcode-source-checkout
#
# Exit status is 0 in all cases; this script reports, it does not gate. Read the
# POSITIVE CONTROL block: if the controls are zero, the probe is broken, not clean.
#
# Only paths, symbol names and counts are printed. No source content is emitted.

set -uo pipefail

TREE="${1:-.}"
cd "$TREE" || { echo "FATAL: cannot cd to $TREE"; exit 2; }

if [ ! -d .git ]; then
  echo "FATAL: $TREE is not a git checkout; this script uses git grep so that only"
  echo "       tracked files are searched and the revision under test is explicit."
  exit 2
fi

REV="$(git rev-parse HEAD)"
echo "checkout : $(pwd)"
echo "HEAD     : $REV"
echo "tree     : $(git rev-parse 'HEAD^{tree}')"
echo "tracked  : $(git ls-files | wc -l) files"
echo

# --- POSITIVE CONTROL ---------------------------------------------------------
# These MUST be non-zero. They prove git grep is reading the tree.
echo "===== POSITIVE CONTROL (must be > 0) ====="
for s in zcodeAgentService feedbackHttpClient upload-credential provider; do
  printf '  %-24s :: %s\n' "$s" "$(git grep -F -l -- "$s" "$REV" 2>/dev/null | wc -l)"
done
echo

# --- 20 exact symbols from the binary audit (SYMBOL-DIFF.md) -------------------
echo "===== 20 EXACT SYMBOLS (binary audit probe set) ====="
SYMBOLS=(
  RepoSnapshotSidecarService repoSnapshot RepoSnapshot captureBeforePrompt
  scheduleRepoSnapshotSidecar captureRepoWikiSnapshot repo-wiki-update
  walkGitMetadataFiles appendRootGitMetadataPaths
  shouldIncludeRepoSnapshotPathBeforeSample writeRepoSnapshotPlainArchive
  buildRepoSnapshotGlobalConfigsExtraInputs repoSnapshotIndexingEnabled
  lastAcceptedManifestHash markAcceptedManifest repo-snapshot.tar.gz.enc
  encrypted_aes_key base_snapshot_id /api/v1/snapshot/upload-credential
  repo-snapshot
)
for s in "${SYMBOLS[@]}"; do
  printf '  %-46s :: %s\n' "$s" "$(git grep -F -l -- "$s" "$REV" 2>/dev/null | wc -l)"
done
echo

# --- supplementary probes -----------------------------------------------------
echo "===== SUPPLEMENTARY PROBES ====="
SUPP=(
  captureStage SENSITIVE_KEY_PATTERN sanitizeUnknown skipDirectoryNames
  extra-files/ settings.behavior.json subagents.json memory.json skills.json
  RSA_PKCS1_OAEP_PADDING oaepHash rsa-oaep-sha256 publicEncrypt PostObject
  repoSnapshotIndexingUserConfigured instantGrepIndexingEnabled
  repoSnapshotUploadCredentialDiagnostics buildObjectUploadTarget uploadPostObject
  uploadPutObject
)
for s in "${SUPP[@]}"; do
  printf '  %-46s :: %s\n' "$s" "$(git grep -F -l -- "$s" "$REV" 2>/dev/null | wc -l)"
done
echo

# --- 42 removed module basenames ---------------------------------------------
echo "===== 42 REMOVED MODULE NAMES (repo-snapshot 20 + repo-wiki 22) ====="
MODULES=(
  repoSnapshotArtifact repoSnapshotCanonicalJson repoSnapshotCaptureIntentScheduler
  repoSnapshotDiskQuota repoSnapshotExtra repoSnapshotFilter
  repoSnapshotGlobalConfigsCollector repoSnapshotGlobalConfigsExtra repoSnapshotHasher
  repoSnapshotPaths repoSnapshotPendingCleanup repoSnapshotPendingManager
  repoSnapshotReferences repoSnapshotScanner repoSnapshotSidecarService
  repoSnapshotStateRepo repoSnapshotTarWriter repoSnapshotUploadClient
  repoSnapshotUploadCredentialDiagnostics repoSnapshotUploadWorker
  repoWiki repoWikiCatalogNormalizer repoWikiCatalogPathValidation
  repoWikiCatalogToolAgent repoWikiGenerator repoWikiLimits repoWikiManifestHash
  repoWikiModelClient repoWikiModelRequestDeadline repoWikiPageBuilder
  repoWikiPageToolAgent repoWikiPaths repoWikiPromptContext
  repoWikiProviderRegistryModelConfig repoWikiSafeFileRead repoWikiService
  repoWikiSourceFileKinds repoWikiStorage repoWikiStructure
  repoWikiWorkspaceAccess repoWikiWorkspaceProviderRegistry localWorkspaceRepoReader
)
ZERO=0
for s in "${MODULES[@]}"; do
  n="$(git grep -F -l -- "$s" "$REV" 2>/dev/null | wc -l)"
  [ "$n" -eq 0 ] && ZERO=$((ZERO + 1))
  printf '  %-46s :: %s\n' "$s" "$n"
done
echo "  --- zero-count modules: $ZERO/${#MODULES[@]} ---"
echo

# --- removed paths ------------------------------------------------------------
echo "===== REMOVED PATHS (checked in the tree, not by grep) ====="
PATHS=(
  packages/services/src/repo-snapshot packages/services/src/repo-wiki
  packages/shared/src/repo-snapshot-sidecar.ts packages/shared/src/repo-wiki.ts
  shared/src/repo-snapshot-sidecar shared/src/repo-wiki
)
for p in "${PATHS[@]}"; do
  if [ -e "$p" ]; then printf '  %-46s :: EXISTS\n' "$p"; else printf '  %-46s :: ABSENT\n' "$p"; fi
done
echo

# --- Repo Wiki cluster -------------------------------------------------------
echo "===== REPO WIKI CLUSTER ====="
for s in 'Repo Wiki' repo-wiki repoWiki RepoWiki '仓库百科' 'knowledge base'; do
  printf '  %-24s :: %s\n' "$s" "$(git grep -Fi -l -- "$s" "$REV" 2>/dev/null | wc -l)"
done
echo

# --- provenance: the shipped 3.14 desktop build commit ------------------------
echo "===== PROVENANCE: shipped-build commit a1328db1 ====="
if git cat-file -t a1328db1 >/dev/null 2>&1; then
  echo "  a1328db1 :: PRESENT as a git object"
else
  echo "  a1328db1 :: NOT A VALID OBJECT in this repository"
fi
printf '  %-24s :: %s\n' "literal 'a1328db1'" "$(git grep -F -l -- 'a1328db1' "$REV" 2>/dev/null | wc -l)"
echo
echo "done."
