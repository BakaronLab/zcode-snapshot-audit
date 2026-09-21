# Source search matrix — full result set against the frozen official source tree

Frozen revision: `872ad960de7ec172591f7e1952f7849229f94521`, tree
`d185a9a893c00d51fc3fe51fe7371b9eea7de143` (6,973 tracked files).
Method: `git grep -F` against the frozen revision, so results are tracked-files-only and cannot be
influenced by `node_modules` or build output. Reproduce with
[`../scripts/source-symbol-probe.sh`](../scripts/source-symbol-probe.sh) — the probe prints this
matrix plus the controls. Evidence class: `[CONFIRMED-OFFICIAL-SOURCE]`.

Classification vocabulary (per the round's requirement): `ABSENT_EXACT_SYMBOL`, `ABSENT_PATH`,
`PRESENT_UNRELATED`, `PRESENT_EQUIVALENT`, `UNKNOWN`.

## 0. Positive controls — must be non-zero, or the probe is broken rather than clean

| Control | Files |
|---|---|
| `zcodeAgentService` | 53 |
| `feedbackHttpClient` | 1 |
| `upload-credential` | 2 |
| `provider` | 933 |

## 1. The 20 audited symbols

| # | Symbol | Official source | Class |
|---|---|---|---|
| 1 | `RepoSnapshotSidecarService` | 0 | `ABSENT_EXACT_SYMBOL` |
| 2 | `repoSnapshot` | 0 | `ABSENT_EXACT_SYMBOL` |
| 3 | `RepoSnapshot` | 0 | `ABSENT_EXACT_SYMBOL` |
| 4 | `captureBeforePrompt` | 0 | `ABSENT_EXACT_SYMBOL` |
| 5 | `scheduleRepoSnapshotSidecar` | 0 | `ABSENT_EXACT_SYMBOL` |
| 6 | `captureRepoWikiSnapshot` | 0 | `ABSENT_EXACT_SYMBOL` |
| 7 | `repo-wiki-update` | 0 | `ABSENT_EXACT_SYMBOL` |
| 8 | `walkGitMetadataFiles` | 0 | `ABSENT_EXACT_SYMBOL` |
| 9 | `appendRootGitMetadataPaths` | 0 | `ABSENT_EXACT_SYMBOL` |
| 10 | `shouldIncludeRepoSnapshotPathBeforeSample` | 0 | `ABSENT_EXACT_SYMBOL` |
| 11 | `writeRepoSnapshotPlainArchive` | 0 | `ABSENT_EXACT_SYMBOL` |
| 12 | `buildRepoSnapshotGlobalConfigsExtraInputs` | 0 | `ABSENT_EXACT_SYMBOL` |
| 13 | `repoSnapshotIndexingEnabled` | 0 | `ABSENT_EXACT_SYMBOL` |
| 14 | `lastAcceptedManifestHash` | 0 | `ABSENT_EXACT_SYMBOL` |
| 15 | `markAcceptedManifest` | 0 | `ABSENT_EXACT_SYMBOL` |
| 16 | `repo-snapshot.tar.gz.enc` | 0 | `ABSENT_EXACT_SYMBOL` |
| 17 | `encrypted_aes_key` | 0 | `ABSENT_EXACT_SYMBOL` |
| 18 | `base_snapshot_id` | 0 | `ABSENT_EXACT_SYMBOL` |
| 19 | `/api/v1/snapshot/upload-credential` | 0 | `ABSENT_EXACT_SYMBOL` |
| 20 | `repo-snapshot` (hyphenated) | 0 | `ABSENT_EXACT_SYMBOL` |

Also swept case-insensitively: `repo-snapshot`, `reposnapshot`, `repo-wiki`, `repowiki` — all 0 files.

## 2. Supplementary probes from the binary audit

| Symbol | Official source | Class / note |
|---|---|---|
| `captureStage` | 0 | `ABSENT_EXACT_SYMBOL` |
| `SENSITIVE_KEY_PATTERN` | **1** | **`PRESENT_UNRELATED`** — CLI TUI display redaction, see below |
| `sanitizeUnknown` | 0 | `ABSENT_EXACT_SYMBOL` |
| `skipDirectoryNames` | 0 | `ABSENT_EXACT_SYMBOL` |
| `extra-files/` | 0 | `ABSENT_EXACT_SYMBOL` |
| `settings.behavior.json` | 0 | `ABSENT_EXACT_SYMBOL` |
| `subagents.json` | 0 | `ABSENT_EXACT_SYMBOL` |
| `memory.json` | 0 | `ABSENT_EXACT_SYMBOL` |
| `skills.json` | 0 | `ABSENT_EXACT_SYMBOL` |
| `RSA_PKCS1_OAEP_PADDING` | 0 | `ABSENT_EXACT_SYMBOL` |
| `oaepHash` | 0 | `ABSENT_EXACT_SYMBOL` |
| `rsa-oaep-sha256` | 0 | `ABSENT_EXACT_SYMBOL` |
| `publicEncrypt` | 0 | `ABSENT_EXACT_SYMBOL` |
| `PostObject` | 0 | `ABSENT_EXACT_SYMBOL` |
| `repoSnapshotIndexingUserConfigured` | 0 | `ABSENT_EXACT_SYMBOL` |
| `instantGrepIndexingEnabled` | 0 | `ABSENT_EXACT_SYMBOL` |
| `repoSnapshotUploadCredentialDiagnostics` | 0 | `ABSENT_EXACT_SYMBOL` |
| `buildObjectUploadTarget` | 0 | `ABSENT_EXACT_SYMBOL` |
| `uploadPostObject` | 0 | `ABSENT_EXACT_SYMBOL` |
| `uploadPutObject` | 0 | `ABSENT_EXACT_SYMBOL` |

### The single disclosed non-zero, resolved by reading

`SENSITIVE_KEY_PATTERN` → 1 file: `apps/zcode-cli/packages/tui/src/app-tool-transcript.ts`, line 11
declares it and line 376 uses it to substitute `[redacted]` for a sensitive key's value when rendering
a **tool transcript in the terminal UI**. `PRESENT_UNRELATED`: a display-redaction helper, not the
snapshot sanitizer; it lives in the CLI TUI, which is not part of either audited bundle, so its
presence in the tree and absence from both bundles are consistent.

## 3. The 42 removed module names

`repoSnapshot*` (20): `repoSnapshotArtifact`, `repoSnapshotCanonicalJson`,
`repoSnapshotCaptureIntentScheduler`, `repoSnapshotDiskQuota`, `repoSnapshotExtra`,
`repoSnapshotFilter`, `repoSnapshotGlobalConfigsCollector`, `repoSnapshotGlobalConfigsExtra`,
`repoSnapshotHasher`, `repoSnapshotPaths`, `repoSnapshotPendingCleanup`, `repoSnapshotPendingManager`,
`repoSnapshotReferences`, `repoSnapshotScanner`, `repoSnapshotSidecarService`, `repoSnapshotStateRepo`,
`repoSnapshotTarWriter`, `repoSnapshotUploadClient`, `repoSnapshotUploadCredentialDiagnostics`,
`repoSnapshotUploadWorker`.

`repoWiki*` / reader (22): `repoWiki`, `repoWikiCatalogNormalizer`, `repoWikiCatalogPathValidation`,
`repoWikiCatalogToolAgent`, `repoWikiGenerator`, `repoWikiLimits`, `repoWikiManifestHash`,
`repoWikiModelClient`, `repoWikiModelRequestDeadline`, `repoWikiPageBuilder`, `repoWikiPageToolAgent`,
`repoWikiPaths`, `repoWikiPromptContext`, `repoWikiProviderRegistryModelConfig`,
`repoWikiSafeFileRead`, `repoWikiService`, `repoWikiSourceFileKinds`, `repoWikiStorage`,
`repoWikiStructure`, `repoWikiWorkspaceAccess`, `repoWikiWorkspaceProviderRegistry`,
`localWorkspaceRepoReader`.

**Result: 42/42 → 0 occurrences.** Class `ABSENT_EXACT_SYMBOL` for every one.

## 4. Path probes

| Path | Result | Class |
|---|---|---|
| `packages/services/src/repo-snapshot` | ABSENT | `ABSENT_PATH` |
| `packages/services/src/repo-wiki` | ABSENT | `ABSENT_PATH` |
| `packages/shared/src/repo-snapshot-sidecar.ts` | ABSENT | `ABSENT_PATH` |
| `packages/shared/src/repo-wiki.ts` | ABSENT | `ABSENT_PATH` |
| `shared/src/repo-snapshot-sidecar` | ABSENT | `ABSENT_PATH` |
| `shared/src/repo-wiki` | ABSENT | `ABSENT_PATH` |
| any path matching `*repo-snapshot*`, `*repo_snapshot*`, `*repo-wiki*`, `*repowiki*` | none found | `ABSENT_PATH` |

## 5. Repo Wiki cluster

| Probe | Files | Class |
|---|---|---|
| `Repo Wiki` | 0 | `ABSENT_EXACT_SYMBOL` |
| `repo-wiki` | 0 | `ABSENT_EXACT_SYMBOL` |
| `repoWiki` | 0 | `ABSENT_EXACT_SYMBOL` |
| `RepoWiki` | 0 | `ABSENT_EXACT_SYMBOL` |
| `仓库百科` | 0 | `ABSENT_EXACT_SYMBOL` |
| `repoWikiService` | 0 | `ABSENT_EXACT_SYMBOL` |
| `knowledge base` | 0 | `ABSENT_EXACT_SYMBOL` |

`REPO_WIKI_SOURCE_CLUSTER_NOT_IDENTIFIED.` `wiki` in any sense occurs in 4 files, none a ZCode
feature: `THIRD-PARTY-NOTICES.md`,
`apps/zcode-cli/packages/core/src/tool/handlers/generated/bash-command-registry.ts`,
`packages/rpc/src/serialization.ts` (a Wikipedia citation in a comment),
`scripts/license-texts/CC-BY-4.0.txt`. Knowledge / workspace context / search / memory / indexing are
**not** treated as Repo Wiki equivalents.

## 6. Module-set structural test (summary)

Method and full tables: [SOURCE-BINARY-MAPPING.md](../SOURCE-BINARY-MAPPING.md).

| Bundle | Comments | Workspace | `DIRECT_NAME_MATCH` | `MISSING_IN_SOURCE` | repo-snapshot / repo-wiki present? |
|---|---|---|---|---|---|
| old 3.12.3 server | 1,289 | 506 | 429 (84.8%) | 77 | **yes — 20 + 22 + 2 shared** |
| new 3.14.0 server | 1,012 | 506 | 464 (91.7%) | 42 | **no — 0** |
| built from source | 789 | 466 | 466 (100.0%) | 0 | **no — 0** |

## 7. Behavioural-equivalence scan (summary)

Method: [SOURCE-CORROBORATION.md](../SOURCE-CORROBORATION.md) §6; script
[`../scripts/behavior-equivalence-scan.py`](../scripts/behavior-equivalence-scan.py).

Scan of `packages/**` (2,539 text files) for co-occurrence of
`A archive` / `B upload` / `C manifest` / `D workspace enumeration` / `E prompt trigger`:

```
5/5 : 0
4/5 : 0
3/5 : 5
2/5 : 17
1/5 : 96
0/5 : 2421
```

**`NO_EQUIVALENT_IDENTIFIED`.** All five 3/5 leads were read and attributed: build packaging config,
desktop host (feedback log archive + remote media preview), remote asset deployment ×2, and i18n
translation strings. A single 4/5 false positive found under an earlier unanchored token set
(`ui/src/v4/SessionPane.tsx`) was resolved by reading it — `prewarmTargetBeforeSend`, the substring
`tar` inside `start`/`target`, workflow-notification manifests and conversation-share `"uploading"`
labels in a React component — and the token set was then anchored.

## 8. Provenance probes

| Probe | Result |
|---|---|
| `a1328db1` as a git object in the official repo | **not a valid object** (`git cat-file -t` fails) |
| literal string `a1328db1` anywhere in the frozen tree | 0 |
| official HEAD `872ad96` == shipped build commit `a1328db1`? | **no — different identifiers** |

Status: **NOT PROVEN SOURCE-IDENTICAL** ([SOURCE-BINARY-MAPPING.md](../SOURCE-BINARY-MAPPING.md)).

## Global classification summary

| Class | Count | Note |
|---|---|---|
| `ABSENT_EXACT_SYMBOL` | 20 required + 19 supplementary + 42 module names + 7 Repo Wiki names | the audited subsystem is absent at name level |
| `ABSENT_PATH` | 4 named paths + all wildcard matches | absent at structure level |
| `PRESENT_UNRELATED` | 1 (`SENSITIVE_KEY_PATTERN`) | CLI TUI display redaction — read and attributed |
| `PRESENT_EQUIVALENT` | **0** | no equivalent implementation identified |
| `UNKNOWN` | — | reserved for questions the tree cannot answer; those are listed in [OPEN-QUESTIONS.md](../OPEN-QUESTIONS.md), not here |

**Never claimed:** that searching for a name and not finding it proves a subsystem does not exist. The
name-level result is why the structural test (§6, with its old-bundle positive control) and the
behavioural scan (§7) were run, and why the top scoring leads were read individually. Even together
these are calibrated negative evidence, not proof: an implementation with disjoint vocabulary and a
different shape would evade all three tests.
