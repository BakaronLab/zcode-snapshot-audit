# MODULE-CLUSTER-DIFF — structural module-set diff

This is the strongest structural evidence in the follow-up. The bundles preserve esbuild
module-path comments (for example `// ../services/src/repo-snapshot/repoSnapshotScanner.ts`), which
identify the original source layout. Diffing those comment sets shows *which whole subsystems* were
deleted — evidence that goes beyond individual symbols going to zero.

Method: [`scripts/module-diff.py`](scripts/module-diff.py) extracts the comment set from each frozen
bundle and diffs them. Reproduce with:

```sh
python3 scripts/module-diff.py <old/zcode-server.cjs> <new/zcode-server.cjs>
```

## Totals (server bundle)

| Metric | OLD server 3.12.3 | NEW server 3.14.0 | Δ |
|---|---|---|---|
| Module-path comments | 1377 | 1086 | −291 |
| Unique modules | 1297 | 1020 | −277 |
| Removed | — | — | **346** |
| Added | — | — | **69** |

## Removed clusters

| Cluster | Modules removed | Kind |
|---|---|---|
| `node_modules/zod` (×4 copies) | 300 | dependency consolidation |
| `services/src/repo-wiki/*` | **22** | application subsystem |
| `services/src/repo-snapshot/*` | **20** | application subsystem |
| `node_modules/@zcode/zcode-cua` | 2 | relocation |
| `shared/src/*` | **2** | application subsystem shared contracts |

**Apart from the zod consolidation (300 modules, offset by 16 added `zod/v4` modules) and the
2-module internal relocation, the only application-level clusters removed in 3.14.0 are
`repo-snapshot` and `repo-wiki`.** The removed set contains no other module.

## `services/src/repo-snapshot/*` — REMOVED (20 modules)

```
repoSnapshotArtifact.ts                 repoSnapshotPendingCleanup.ts
repoSnapshotCanonicalJson.ts            repoSnapshotPendingManager.ts
repoSnapshotCaptureIntentScheduler.ts   repoSnapshotReferences.ts
repoSnapshotDiskQuota.ts                repoSnapshotScanner.ts
repoSnapshotExtra.ts                    repoSnapshotSidecarService.ts
repoSnapshotFilter.ts                   repoSnapshotStateRepo.ts
repoSnapshotGlobalConfigsCollector.ts   repoSnapshotTarWriter.ts
repoSnapshotGlobalConfigsExtra.ts       repoSnapshotUploadClient.ts
repoSnapshotHasher.ts                   repoSnapshotUploadCredentialDiagnostics.ts
repoSnapshotPaths.ts                    repoSnapshotUploadWorker.ts
```

Every stage of the audited pipeline is represented: **scanner** (enumerate workspace), **filter**
(path/secret decisions), **hasher**, **tarWriter** (archive construction), **CanonicalJson**,
**GlobalConfigsCollector / GlobalConfigsExtra** (the nine config groups), **StateRepo**,
**PendingManager / PendingCleanup** (the tmp/pending `.enc` lifecycle), **CaptureIntentScheduler**
(the prompt/task trigger), **DiskQuota**, **Artifact**, **References**, and
**UploadClient / UploadWorker** (the OSS upload).

## `services/src/repo-wiki/*` — REMOVED (22 modules)

```
repoWiki.ts                             repoWikiPaths.ts
repoWikiCatalogNormalizer.ts            repoWikiPromptContext.ts
repoWikiCatalogPathValidation.ts        repoWikiProviderRegistryModelConfig.ts
repoWikiCatalogToolAgent.ts             repoWikiSafeFileRead.ts
repoWikiGenerator.ts                    repoWikiService.ts
repoWikiLimits.ts                       repoWikiSourceFileKinds.ts
repoWikiManifestHash.ts                 repoWikiStorage.ts
repoWikiModelClient.ts                  repoWikiStructure.ts
repoWikiModelRequestDeadline.ts         repoWikiWorkspaceAccess.ts
repoWikiPageBuilder.ts                  repoWikiWorkspaceProviderRegistry.ts
repoWikiPageToolAgent.ts                localWorkspaceRepoReader.ts
```

This is the complete Repo Wiki feature, not just its upload trigger: the generator, the model
client, the page builders, the storage layer, the workspace reader, and the
`repoWikiManifestHash` module that tied wiki output to the snapshot path.

## `shared/src/*` — REMOVED (2 modules)

```
shared/src/repo-snapshot-sidecar.ts
shared/src/repo-wiki.ts
```

These are the shared type/contract modules that both server and desktop consumed.

## Added clusters (69 modules)

| Cluster | Modules | Assessment |
|---|---|---|
| `node_modules/zod/v4` | 16 | dependency upgrade (offsets 300 removed) |
| `shared/src/*` | 20 | local file search/ignore, telemetry redaction, client config, onboarding records, plugin-store ordering, dynamic-workflow protocol support |
| `shared/src/zcode-protocol-v4/*` | 8 | new dynamic-workflow protocol |
| `node_modules/@zcode/zcode-cua` | 4 | relocation |
| `services/src/cloud-content/*` | 3 | **download-only** content bundle cache |
| `services/src/marketing-touch/*` | 3 | marketing assets |
| `services/src/client-config/*` | 2 | remote client config |
| `services/src/file/*` | 2 | local workspace search/ignore |
| `services/src/onboarding/*` | 2 | onboarding records |
| `services/src/zcode-agent/*` | 2 | agent stderr collection, plugin catalog request |
| `services/src/bigmodel/*` | 1 | entitlement |
| `services/src/feedback/*` | 1 | feedback log archive |
| `node_modules/{yauzl,buffer-crc32,ignore,pend}` | 5 | zip/ignore utilities |

**No added cluster is a repository-capture, archive-and-upload subsystem.** The two
name-suggestive additions were read directly:

- `cloud-content/*`: `download(bundle)`, `trustedUrl()`, a `bundle_download` error, and a cache
  write with an exclusive-create flag → cloud → client **download**. Direction is the opposite of
  an upload.
- `feedback/feedbackLogArchive.ts`: archives local logs for user-initiated feedback submission;
  the upload half is `feedbackHttpClient.ts` (feedback attachments, see
  [UPLOAD-SURFACE-ATTRIBUTION.md](UPLOAD-SURFACE-ATTRIBUTION.md)).
- `file/workspaceFileSearch.ts` / `workspaceFileIgnore.ts` and the two `shared/src` counterparts:
  local workspace search and ignore handling (grep-type features), no archive and no upload.

## Desktop side

The desktop `app.asar` does not retain application source paths for its own code: probing
`services/src/repo-snapshot`, `repo-snapshot/repoSnapshotScanner`,
`shared/src/repo-snapshot-sidecar` and the control fragments `services/src/git/gitService`,
`shared/src/channels` returns **0 in both old and new**. The desktop application code is emitted as
one chunk whose comment is `src/Emitter.ts`, so module-level attribution is unavailable there, and
the desktop side of the delta rests on symbol-level evidence with control validation (see
[SYMBOL-DIFF.md](SYMBOL-DIFF.md)).

Desktop module-comment totals still show a contraction consistent with the removal:
**3818 (old) → 3549 (new)**, a delta of −269. *(Absolute totals are extractor-dependent — the
audit's own extractor reported 3634 → 3365 for the same files. Both agree on the −269 delta, which
is the load-bearing quantity.)*

## Conclusion

`MODULE_CLUSTER_REMOVED` for both `services/src/repo-snapshot/*` (20 modules) and
`services/src/repo-wiki/*` (22 modules), plus their two `shared/src` contract modules. No
replacement cluster exists for either.

**Limitation.** This is a module-set difference, not a semantic proof about behavior. It establishes
that the named modules are absent from the examined bundles; it establishes nothing about server-side
behavior, which remains **UNKNOWN**; and it cannot exclude an equivalent implementation written with
entirely disjoint vocabulary in a module that is present. That scenario is addressed separately by
the calibrated combination test in [SNAPSHOT-HIT-CLASSIFICATION.md](SNAPSHOT-HIT-CLASSIFICATION.md).
