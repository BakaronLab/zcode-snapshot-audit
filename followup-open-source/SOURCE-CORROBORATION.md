# SOURCE-CORROBORATION — official source tree vs the 3.14 binary regression

**Question.** The binary audit (`../followup-3.14/`) concluded that the client-side `repo-snapshot`
and Repo Wiki subsystems present in the earlier builds are absent from the audited 3.14.0 artifacts.
ZCode has since published source. Does the published source tree independently corroborate that
conclusion?

**Answer: yes — at name level, at module-structure level, and by build.** The frozen official source
tree contains none of the 20 audited symbols, none of the 42 removed module names, and none of the
removed paths; it contains no Repo Wiki feature cluster under any searched name; and a bundle built
from that tree reproduces the same absence. The source tree also independently confirms the
*surviving* `feedback` attachment upload path that the binary audit had attributed the residual
upload vocabulary to.

This is corroboration of *absence of the audited subsystem*, not a clean bill of health for the
product. See the closing boundaries.

Evidence class for everything below: **[CONFIRMED-OFFICIAL-SOURCE]**, read directly from
`872ad960de7ec172591f7e1952f7849229f94521` / tree `d185a9a893c00d51fc3fe51fe7371b9eea7de143`.
All searches were run against the frozen revision with `git grep` (tracked files only), so the
revision under test is explicit and `node_modules` cannot contribute hits. Reproduce with
[`scripts/source-symbol-probe.sh`](scripts/source-symbol-probe.sh). Full matrix:
[`evidence/source-search-matrix.md`](evidence/source-search-matrix.md).

## 1. Exact-symbol search — 20 audited symbols

The 20 probes are exactly the required probe set of the binary audit's `SYMBOL-DIFF.md`, which
returned `OLD > 0, NEW = 0` on both the server bundle and the desktop payload.

| Symbol | Official source tree | Binary audit (3.14.0) |
|---|---|---|
| `RepoSnapshotSidecarService` | 0 | 0 |
| `repoSnapshot` | 0 | 0 |
| `RepoSnapshot` | 0 | 0 |
| `captureBeforePrompt` | 0 | 0 |
| `scheduleRepoSnapshotSidecar` | 0 | 0 |
| `captureRepoWikiSnapshot` | 0 | 0 |
| `repo-wiki-update` | 0 | 0 |
| `walkGitMetadataFiles` | 0 | 0 |
| `appendRootGitMetadataPaths` | 0 | 0 |
| `shouldIncludeRepoSnapshotPathBeforeSample` | 0 | 0 |
| `writeRepoSnapshotPlainArchive` | 0 | 0 |
| `buildRepoSnapshotGlobalConfigsExtraInputs` | 0 | 0 |
| `repoSnapshotIndexingEnabled` | 0 | 0 |
| `lastAcceptedManifestHash` | 0 | 0 |
| `markAcceptedManifest` | 0 | 0 |
| `repo-snapshot.tar.gz.enc` | 0 | 0 |
| `encrypted_aes_key` | 0 | 0 |
| `base_snapshot_id` | 0 | 0 |
| `/api/v1/snapshot/upload-credential` | 0 | 0 |
| `repo-snapshot` (hyphenated) | 0 | 0 server / 1 desktop deny-list string |

**Positive controls** (must be non-zero, and are): `zcodeAgentService` 53 files,
`feedbackHttpClient` 1, `upload-credential` 2, `provider` 933. The zero counts are real absences,
not a broken probe.

### Never-claimed

A name-level zero is a **name-level** result. It does not by itself establish that no functionally
equivalent implementation exists. That is why the module-structure test and the behavioural scan
below were run; and even together they remain calibrated negative evidence rather than proof. The
binary audit's own limitation statement carries over unchanged.

### One disclosed non-zero

`SENSITIVE_KEY_PATTERN` returns **1** file in the official tree, where the binary audit recorded 0 in
both 3.14.0 bundles. **Classification: `PRESENT_UNRELATED`.** The single hit is a different, unrelated
constant in the CLI's terminal-UI layer —
`apps/zcode-cli/packages/tui/src/app-tool-transcript.ts` line 11 declares
`const SENSITIVE_KEY_PATTERN = /token|secret|password|api[_-]?key|authorization|credential|cookie/i;`
and line 376 uses it to replace a sensitive key's value with `[redacted]` when rendering a **tool
transcript in the terminal UI**. It is a display redaction helper, not the snapshot sanitizer, and it
lives in the CLI TUI, which is not part of either audited bundle (the server bundle and the desktop
`app.asar`), so its absence from both bundles and presence in the tree are consistent. No snapshot
sanitizer, no archive path and no capture logic is associated with it.

## 2. Module-structure search — 42 removed module names and 4 removed paths

The binary audit's `MODULE-CLUSTER-DIFF.md` established, from esbuild module-path comments, that
`services/src/repo-snapshot/*` (20 modules), `services/src/repo-wiki/*` (22 modules) and their two
`shared/src` contract modules were removed from the bundles. Probed against the official tree:

| Probe | Result |
|---|---|
| 42 removed module basenames (`repoSnapshot*` ×20, `repoWiki*`/`localWorkspaceRepoReader` ×22) | **42/42 → 0 occurrences** |
| `packages/services/src/repo-snapshot/` | **ABSENT** |
| `packages/services/src/repo-wiki/` | **ABSENT** |
| `packages/shared/src/repo-snapshot-sidecar.ts` | **ABSENT** |
| `packages/shared/src/repo-wiki.ts` | **ABSENT** |
| Any file or directory named `*repo-snapshot*`, `*repo_snapshot*`, `*repo-wiki*`, `*repowiki*` | **none found** |

This is a stronger result than the symbol probes because it is structural: the whole subsystem's file
set is absent, not just its identifiers.

## 3. Repo Wiki — source-level cluster search

| Probe | Result |
|---|---|
| `Repo Wiki` | 0 |
| `repo-wiki` | 0 |
| `repoWiki` | 0 |
| `RepoWiki` | 0 |
| `仓库百科` | 0 |
| `repoWikiService` | 0 |
| `knowledge base` | 0 |

**`REPO_WIKI_SOURCE_CLUSTER_NOT_IDENTIFIED`.**

`wiki` (case-insensitive, any sense) occurs in exactly four tracked files, and none is a ZCode feature:
`THIRD-PARTY-NOTICES.md` (Wikipedia/CC URLs inside third-party license link references),
`apps/zcode-cli/packages/core/src/tool/handlers/generated/bash-command-registry.ts`,
`packages/rpc/src/serialization.ts` (a comment citing `https://en.wikipedia.org/wiki/Variable-length_quantity`),
and `scripts/license-texts/CC-BY-4.0.txt`.

This is deliberately **not** equated with anything else. The search looked for the Repo Wiki feature
cluster, found no source-level cluster, and stops there. Knowledge, workspace context, search, memory
and indexing are different features and are **not** offered as substitutes.

## 4. `zcodeAgentService` — surviving host, removed hook

`packages/services/src/zcode-agent/zcodeAgentService.ts` **exists** (235,487 B). This is the
source-level counterpart of the host module in which the binary delta placed the old prompt hook.

Probed inside that file:

| Symbol | Occurrences |
|---|---|
| `captureBeforePrompt` | 0 |
| `repoSnapshot` / `RepoSnapshot` | 0 / 0 |
| `RepoWiki` | 0 |
| `repo-wiki-update` | 0 |
| `upload-credential` | 0 |
| `captureStage` | 0 |
| `beforePrompt` / `beforeSend` | 0 / 0 |
| `snapshot` | 117 (case-insensitive, which is `Snapshot`-inclusive; exact-case lowercase is 74) |

The 117 case-insensitive `snapshot` occurrences are a **different concept**, and their contexts were read rather than
inferred: they are session- and provider-state snapshots — `snapshot.session.sessionId`,
`snapshot.settings.model.current`, `readinessSnapshot` / `createProviderReadinessSnapshotFromSelectionView`,
`forceSnapshot`, `basedOnZCodeBuiltinRevision`. This matches the binary audit's own classification of
`zcodeAgentService.ts`'s 72 `snapshot` hits as "provider registry/config revision snapshot". There is
no capture trigger, no archive, no manifest and no upload in the module.

The only hook-related identifiers in the file are workspace-hook trust machinery
(`zcodeWorkspaceHookTrustGrantResultSchema`, `hookDeclarationDigest`, `workspaceHookTrustGrant`,
`WorkspaceHookReviewRequested`) — the lifecycle-hook trust feature, unrelated to any capture hook.

**Result: `SOURCE_CORROBORATES_SURVIVING_HOST_HOOK_REMOVAL`** — the host module survives in the
published source, and the audited capture hook that the binary delta removed is absent from it.

The desktop-side counterpart was checked too: `packages/desktop/src/host/index.ts` (111,529 B) returns
0 for `captureBeforePrompt`, `RepoSnapshot`, `repoSnapshot`, `repo-snapshot`, `RepoWiki`, `repo-wiki`.

## 5. Residual upload attribution — feedback attachment upload

The binary audit attributed the surviving `upload-credential` / `oss.host` / `x-oss-*` vocabulary in
3.14.0 to `services/src/feedback/feedbackHttpClient.ts` (user-initiated feedback attachment upload),
not to the removed snapshot pipeline. The published source **directly confirms** that attribution.

`packages/services/src/feedback/feedbackHttpClient.ts` (36,182 B) contains:

- line 513 — the request path `"/feedback/attachment/upload-credential"` with `method: "POST"`;
- line 280 — the same string used to recognise a response for summarisation/diagnostics;
- lines 1054–1075 — `buildOssFormFields(credential)`, emitting the OSS PostObject form fields
  `key`, `policy`, `x-oss-signature`, `x-oss-signature-version`, `x-oss-credential`,
  `x-oss-security-token`, `x-oss-date`, `callback`, `success_action_status`.

The re-established chain, in source:

```
user submits feedback  (packages/ui/src/feedback/feedbackSubmissionJob.ts)
  → uploadFile(ticketId, kind, filePath, filename, contentType)     feedbackHttpClient.ts:494
      (the service-level wrapper is `uploadAttachment` in feedbackService.ts:165)
      POST /feedback/attachment/upload-credential  {ticket_id, message_id?, file_name, size}
      ← credential { oss{path,policy,x_oss_signature,…,x_oss_date}, callback{url,body,content_type},
                     attachment_id, max_size }
  → uploadOssForm(credential, filePath, …)  → single-file multipart POST to credential.oss.host
```

Confirmed characteristics, each checkable in source:

- **Trigger is user action.** The only callers are the feedback submission job in the UI layer.
  No prompt hook, no task-completion hook, no scheduler.
- **Payload is one file.** `stat(filePath)` on a single caller-supplied path, size-checked against
  `getFeedbackMaxAttachmentBytes(kind)` and against `credential.max_size`.
- **Attachment kinds** are `"log" | "image" | "other"` (`packages/shared/src/feedback.ts:14`).
- **No repo chain.** The module contains no workspace enumeration, no `tar`/gzip, no manifest
  construction, no `.git` metadata collection, no delta computation.
- **The log variant does not archive a workspace.** `compactLogArchive.ts` → `prepareCompactLogArchive`
  passes `sources: [{ directory: join(sourceDir, "logs"), archivePrefix: "logs" }]` where
  `sourceDir = getAppConfigDir()` = `{zcodeDataRoot}/v2` — i.e. the application config directory's
  `logs` subdirectory, not a workspace. The archive is ZIP built by `yazl`, bounded by
  `maxTotalBytes` 2 MiB (compact path) and `MAX_FILE_BYTES` 8 MiB / `MAX_TOTAL_BYTES` 32 MiB
  (`feedbackLogArchive.ts`), and text passes through `redactFeedbackText`. The module's own comment
  states it is 反馈上传唯一归档入口 — the only archive entry point for feedback upload — with
  whitelisted sources and bounded reads.

This matches the binary audit's `UPLOAD-SURFACE-ATTRIBUTION.md` on every point, now from source
rather than from bundle strings. The attribution is **confirmed, not corrected**.

## 6. Behaviour-equivalence scan of the source tree

A source-level analogue of the binary audit's five-signal combination test
(`../followup-3.14/SNAPSHOT-HIT-CLASSIFICATION.md`): score each source module by how many of
`A archive` / `B upload` / `C manifest` / `D workspace enumeration` / `E prompt trigger` it contains.
Reproduce with [`scripts/behavior-equivalence-scan.py`](scripts/behavior-equivalence-scan.py).

Result over `packages/**` (2,539 text files scored):

| Score | Files |
|---|---|
| 5/5 | 0 |
| 4/5 | 0 |
| 3/5 | 5 |
| 2/5 | 17 |
| 1/5 | 96 |
| 0/5 | 2,421 |

**No source module satisfies the combination. `NO_EQUIVALENT_IDENTIFIED`.**

Every 3/5 lead was read, not waved away:

| Module | Signals | What it actually is |
|---|---|---|
| `desktop/electron-builder.config.js` | A,B,C | Packaging config: `.pkg.tar.zst` (Arch package extension), `multipart/byteranges` (electron-updater HTTP range fallback), `.zcode-install-manifest` (installer manifest file name). Build-time, not runtime. |
| `desktop/src/host/index.ts` | A,B,E | `pendingFeedbackLogArchiveRequest` (the feedback log archive above) and `remoteBackend.upload` / `remoteMediaPreviewFactory` (remote-backend media preview). No workspace walk. |
| `server/src/remote/remoteAssetInstaller.ts` | A,B,C | Remote **deployment**: stages `<componentId>-<ts>-<uuid>.tar.gz` locally, mode `"local-download-upload"`, and reads a `manifest-<platformArch>.json` from the remote asset root (`remoteAssetCache.ts` `MANIFEST_FILE_NAME_PREFIX = "manifest-"`) — transfers *product* assets to a remote host, not workspace content. |
| `server/src/remote/zcodeAgentDevDeploy.ts` | A,B,C | Dev deploy: `uploadDevelopmentOfficialPluginPackage`, `<plugin-dir>.tar.gz` — payload is a plugin package. |
| `ui/src/i18n/locales/{en-US,zh-CN}.ts` | A,B,C | Translation strings. |

Two calibration notes, disclosed because they cut against the test rather than for it:

1. **A false positive was found and resolved.** Under an earlier, unanchored token set, exactly one
   module scored 4/5: `ui/src/v4/SessionPane.tsx`. Reading it resolved every signal:
   `beforesend` came from `prewarmTargetBeforeSend` / `ensureDraftPrewarmConfigBeforeSend` (UI draft
   pre-warm), `tar` from the substring inside `start` / `target`, `manifest` from workflow-notification
   and CLI-v4 projection manifests, `upload` from conversation-share progress labels (`"uploading"`).
   It is a React UI component with no capture logic. The token set was then anchored (`\btar\b`,
   `\bbeforesend\b`) and the scan re-run, which is what produced the table above. The lead was read
   and attributed, not discarded because it was inconvenient.
2. **Signal co-occurrence is weak evidence** and the binary audit says so about its own version of
   this test. It is included here for parity, not as the load-bearing result. The load-bearing
   source-level results are §1–§3 (exact) and §7 (structural, with a positive control).

## 7. Structural correspondence with a positive control

The strongest source-level corroboration is the module-set test in
[SOURCE-BINARY-MAPPING.md](SOURCE-BINARY-MAPPING.md): the esbuild module-path comments of each frozen
bundle are mapped onto the official tree as `../<pkg>/src/...` → `packages/<pkg>/src/...`.

Because this test must be able to *detect* the subsystem if present, it was run on the **old 3.12.3
bundle** as a positive control. It reported, as missing from the official tree:

```
[20] packages/services/src/repo-snapshot
[22] packages/services/src/repo-wiki
[ 1] packages/shared/src/repo-snapshot-sidecar.ts
[ 1] packages/shared/src/repo-wiki.ts
```

— i.e. exactly the audited subsystem, recovered by structure and by a method that does not look for
symbol names. Run on the **3.14.0 bundle**, the same test reports `repo-snapshot` and `repo-wiki` at
**zero**. The method finds the subsystem when it is there and does not find it when it is not.

Details, including the 42 modules the 3.14.0 bundle has and the tree does not, are in
[SOURCE-BINARY-MAPPING.md](SOURCE-BINARY-MAPPING.md). That file also records the provenance boundary
this round does **not** cross.

## Boundaries of this corroboration

- **Not a statement that no upload exists.** Other upload and network surfaces are present and are
  catalogued in [CURRENT-UPLOAD-SURFACES.md](CURRENT-UPLOAD-SURFACES.md).
- **Not a statement about the server.** Nothing here observes server-side retention, processing,
  training use or deletion. Server-side behaviour remains **UNKNOWN**, unchanged from the original
  audit.
- **Not a statement about earlier releases.** This says what the frozen 3.14.0-era source tree
  contains, not what any earlier build did or when the subsystem left the product.
- **Not exact source identity.** See [SOURCE-BINARY-MAPPING.md](SOURCE-BINARY-MAPPING.md)
  §"Provenance boundary".
- **Not a mathematical proof of non-existence.** Name, structure and signal tests are all
  vocabulary- and shape-sensitive. An implementation with disjoint vocabulary and a different shape
  would evade all three. This is calibrated negative evidence.

## Statement this file supports

> The official ZCode 3.14.0 source tree independently corroborates the 3.14 binary regression result:
> the previously audited client-side repo-snapshot and Repo Wiki implementation is not identified in
> the frozen official source tree, while the surviving feedback attachment upload path maps directly
> to the residual upload surface previously attributed in the binary audit.

> ZCode 官方公开的 3.14.0 源码树独立印证了此前的 3.14 二进制回归结论：先前审计到的客户端 repo-snapshot
> 与 Repo Wiki 实现未在固定的官方源码树中识别到；与此同时，源码中仍存在的 feedback 附件上传路径与此前
> 二进制审计中归因的残余上传面直接对应。
