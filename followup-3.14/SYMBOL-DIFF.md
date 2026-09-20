# SYMBOL-DIFF — old repo-snapshot symbol regression

## Counting convention

All counts in this file are **case-sensitive raw byte occurrences** (`grep -ao -- "<token>" | wc -l`
equivalents) computed against the frozen artifacts. Other documents in this follow-up state their
own convention where it differs ([DELTA.md](DELTA.md)'s `zcodeAgentService.ts` table is
case-insensitive). A token's count is only comparable with another count taken under the same
convention — this file is internally consistent.

Artifacts: `old/zcode-server.cjs` (3.12.3), `new/zcode-server.cjs` (3.14.0),
`old/…/resources/app.asar` (3.11.2 Linux), `new/desktop/app.asar` (3.14.0 Windows).

## Required probes

| # | symbol | OLD srv | NEW srv | OLD dsk | NEW dsk | status | new equivalent candidate |
|---|---|---|---|---|---|---|---|
| 1 | `RepoSnapshotSidecarService` | 2 | 0 | 1 | 0 | **REMOVED** | none found |
| 2 | `repoSnapshot` | 92 | 0 | 67 | 0 | **REMOVED** | none found |
| 3 | `RepoSnapshot` | 160 | 0 | 60 | 0 | **REMOVED** | none found |
| 4 | `captureBeforePrompt` | 5 | 0 | 5 | 0 | **REMOVED** | none found |
| 5 | `scheduleRepoSnapshotSidecar` | 2 | 0 | 1 | 0 | **REMOVED** | none found |
| 6 | `captureRepoWikiSnapshot` | 3 | 0 | 1 | 0 | **REMOVED** | none found |
| 7 | `repo-wiki-update` | 1 | 0 | 1 | 0 | **REMOVED** | none found |
| 8 | `walkGitMetadataFiles` | 3 | 0 | 1 | 0 | **REMOVED** | none found |
| 9 | `appendRootGitMetadataPaths` | 2 | 0 | 1 | 0 | **REMOVED** | none found |
| 10 | `shouldIncludeRepoSnapshotPathBeforeSample` | 3 | 0 | 1 | 0 | **REMOVED** | none found |
| 11 | `writeRepoSnapshotPlainArchive` | 2 | 0 | 1 | 0 | **REMOVED** | none found |
| 12 | `buildRepoSnapshotGlobalConfigsExtraInputs` | 2 | 0 | 1 | 0 | **REMOVED** | none found |
| 13 | `GLOBAL_CONFIG_SOURCES` | 3 | 0 | 0 | 0 | **REMOVED** | none found |
| 14 | `GLOBAL_CONFIG_PATHS` | 4 | 0 | 0 | 0 | **REMOVED** | none found |
| 15 | `repoSnapshotIndexingEnabled` | 4 | 0 | 23 | 0 | **REMOVED** | none found |
| 16 | `lastAcceptedManifestHash` | 8 | 0 | 8 | 0 | **REMOVED** | none found |
| 17 | `markAcceptedManifest` | 3 | 0 | 3 | 0 | **REMOVED** | none found |
| 18 | `repo-snapshot.tar.gz.enc` | 1 | 0 | 1 | 0 | **REMOVED** | none found |
| 19 | `encrypted_aes_key` | 2 | 0 | 2 | 0 | **REMOVED** | none found |
| 20 | `base_snapshot_id` | 4 | 0 | 4 | 0 | **REMOVED** | none found |

All 20 required probes: **OLD > 0, NEW = 0, on both server and desktop.** Not a single probe
returned `RENAMED` or `RELOCATED`; the equivalent-candidate column is empty because no candidate was
identified by the module diff or by any reverse-trace search.

## Supplementary probes (added because they discriminate)

| symbol | OLD srv | NEW srv | OLD dsk | NEW dsk | note |
|---|---|---|---|---|---|
| `captureStage` | 10 | 0 | 10 | 0 | prompt-stage capture marker |
| `SENSITIVE_KEY_PATTERN` | 2 | 0 | 0 | 0 | snapshot sanitizer |
| `sanitizeUnknown` | 4 | 0 | 1 | 0 | snapshot sanitizer |
| `skipDirectoryNames` | 2 | 0 | 0 | 0 | `.git` exclusion set in the snapshot walker |
| `ZCODE_REPO_SNAPSHOT_UPLOAD_CREDENTIAL_URL` (constant name) | **2** | 0 | 0 | 0 | declaration in `apiEndpoints.ts` + use in `repoSnapshotUploadClient.ts`; both modules removed. The desktop minifies to a different local name in each chunk, hence 0/0 there |
| `/api/v1/snapshot/upload-credential` (endpoint string) | 1 | 0 | **3** | **0** | the string occurs once in the server; separately 3→0 on the desktop |
| `extra-files/` | 1 | 0 | 1 | 0 | snapshot archive extra payload path |
| `settings.behavior.json` | 1 | 0 | 1 | 0 | global-config group member |
| `subagents.json` | 1 | 0 | 1 | 0 | global-config group member |
| `memory.json` | 1 | 0 | 1 | 0 | global-config group member |
| `skills.json` | 1 | 0 | 1 | 0 | global-config group member |
| `RSA_PKCS1_OAEP_PADDING` | 1 | 0 | 1 | 0 | snapshot key wrap |
| `oaepHash` | 1 | 0 | 1 | 0 | snapshot key wrap |
| `rsa-oaep-sha256` | 2 | 0 | 2 | 0 | envelope algorithm label |
| `publicEncrypt` | 1 | 0 | 3 | 0 | snapshot key wrap |
| `PostObject` | 2 | 0 | 1 | 0 | snapshot OSS upload form |
| `repoSnapshotIndexingUserConfigured` | 4 | 0 | **23** | **0** | sibling setting; zeroed on both sides |
| `instantGrepIndexingEnabled` | **3** | 0 | **21** | **0** | sibling setting (3, not 1 — corrected after review); zeroed on both sides |
| `repo-snapshot` (hyphenated) | **34** | 0 | 9 | **1** | desktop residual attributed below |
| `repo-wiki` (hyphenated) | 43 | 0 | 99 | **1** | desktop residual attributed below |

## Disclosed desktop residuals

The new desktop retains exactly **one** occurrence each of the hyphenated `repo-snapshot` and
`repo-wiki`. Both are inside a diagnostic-log-archive **exclusion** deny-list consumed by
`isNonLogStateArchivePath`:

```js
["agent-config","certs","repo-snapshots","repo-wiki","sessions","session-bindings","checkpoints"]
```

That is a **privacy-protective list of paths to exclude** from archives — the opposite of a capture
list. The identical list literal is present in the OLD 3.11.2 desktop (one occurrence, same
function name), so it is pre-existing and merely carries the names forward as strings. It is a
**name-only residue, not code**: no function, type, module or call path of the removed subsystem
exists behind it.

Whole-asar per-file scanning corroborates the disappearance: the OLD desktop spreads snapshot tokens
across many chunks (`out/host/index.js`, renderer chunks, preloads), while the NEW desktop has **2
hits total**, both the deny-list strings above. Counts: OLD dsk `repo-snapshot` 9 → NEW 1; OLD dsk
`repo-wiki` 99 → NEW 1.

*(The exclusion-list snippet above is the minimum necessary to make this attribution checkable. No
other code from the desktop payload is reproduced in this follow-up.)*

## Control probes (must NOT drop — used to validate the zeros)

| symbol | OLD srv | NEW srv | OLD dsk | NEW dsk | verdict |
|---|---|---|---|---|---|
| `checkpoint@zcode.local` | 2 | 2 | 2 | 2 | CONTROL_SURVIVES |
| `refs/zcode/checkpoints` | 2 | 2 | 1 | 1 | CONTROL_SURVIVES |
| `sdk.rum.aliyuncs.com` | 0 | 0 | 8 | 8 | CONTROL_SURVIVES (identical) |
| `log.aliyuncs.com` | 0 | 0 | 2 | 2 | CONTROL_SURVIVES (identical) |
| `deviceMid` | 54 | 62 | 90 | 116 | CONTROL_SURVIVES (grew) |
| `X-Device-Mid` | 5 | 6 | 6 | 7 | CONTROL_SURVIVES (grew) |
| `multipart/form-data` | 57 | 57 | 155 | 153 | CONTROL_SURVIVES |

## Symbols that survive with reduced counts — attributed, NOT treated as survivors of the subsystem

All four artifacts are shown, so no residual is left undisclosed.

| symbol | OLD srv | NEW srv | OLD dsk | NEW dsk | attribution / verdict |
|---|---|---|---|---|---|
| `upload-credential` | 5 | 2 | 7 | 3 | `services/src/feedback/feedbackHttpClient.ts` — **DIFFERENT SUBSYSTEM** (feedback attachment upload) |
| `oss.host` | 3 | 1 | 3 | 1 | `services/src/feedback/feedbackHttpClient.ts` — **DIFFERENT SUBSYSTEM** |
| `x-oss-` (prefix) | 10 | 5 | 10 | 5 | `services/src/feedback/feedbackHttpClient.ts` — **DIFFERENT SUBSYSTEM** |
| `ls-files` | 3 | 2 | 6 | 5 | `services/src/git/repo/gitCliRepo.ts` (`--stage -z -- <paths>`) — **DIFFERENT PURPOSE** (git staging UI) |
| `--cached` | 4 | 3 | 4 | 3 | generic git flag used by the staging UI on both sides — not discriminating; disclosed here for parity with its two sibling flags |
| `--others` | 1 | 0 | 2 | 1 | server: removed. Desktop residual is a bundled third-party npm package |
| `--exclude-standard` | 1 | 0 | 2 | 1 | server: removed. Desktop residual is the same third-party npm package |
| `aes-256-ctr` | 2 | 0 | 3 | 1 | server: removed. Desktop residual is the bundled SSH library cipher table |
| `publicEncrypt` | 1 | 0 | 3 | 0 | snapshot usage removed; no RSA key wrap remains on either side |
| `createCipheriv` | 2 | 1 | 16 | 13 | generic `node:crypto` use elsewhere; no snapshot cipher call site |
| `<redacted>` | 4 | 3 | 12 | 11 | other redaction paths (e.g. telemetry); the snapshot sanitizer itself is gone |
| `SENSITIVE_KEY_PATTERN` | 2 | 0 | 0 | 0 | snapshot sanitizer removed |
| `sanitizeUnknown` | 4 | 0 | 1 | 0 | snapshot sanitizer removed |
| `workspaceIdentity` | 745 | 700 | **3362** | **3505** | session/browser workspace context — the concept SURVIVES (and grew desktop-side); its capture-suppression role is gone with the subsystem |

Note on `workspaceIdentity`: the concept does not merely survive, it **expanded** on the desktop
(3362 → 3505). That is consistent with F-031's `NOT_APPLICABLE` status — the identifier now serves
unrelated purposes and no longer gates any capture. The desktop increase cannot indicate a revived
capture gate, because the module that contained the gate does not exist on either side.

## Old-side attribution of the removed endpoint constant

In the old server the 5 `upload-credential` hits split as:

| OLD hit | Module | Status in 3.14.0 |
|---|---|---|
| 1 | `services/src/providers/api/apiEndpoints.ts` — the snapshot credential URL constant | **REMOVED** |
| 1 | `services/src/repo-snapshot/repoSnapshotUploadCredentialDiagnostics.ts` | **REMOVED** (module gone) |
| 2 | `services/src/feedback/feedbackHttpClient.ts` | survives |
| 1 | `services/src/feedback/compactLogArchive.ts` | survives |

This is why the naive count drops 5 → 2 rather than to 0: **the endpoint string survives only in the
unrelated feedback subsystem**, which posts to its own `/feedback/attachment/upload-credential`
path.

## Honest statement of the negative result

The old `.git` inclusion path is **not reachable or identifiable** in 3.14.0 — because no equivalent
repo-capture subsystem was identified at all. This is deliberately **not** phrased as ".git exclusion
was fixed": those are different claims, and only the former is supported.

**Limitation.** Byte-count probes are a name-level test. They cannot exclude a functionally
equivalent implementation that uses entirely disjoint vocabulary; that scenario is addressed by the
module-set diff and by the calibrated combination test in
[SNAPSHOT-HIT-CLASSIFICATION.md](SNAPSHOT-HIT-CLASSIFICATION.md). All counts here are static
properties of the shipped bundles; nothing here observes runtime or network behavior.
