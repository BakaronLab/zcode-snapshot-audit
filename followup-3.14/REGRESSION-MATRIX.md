# REGRESSION MATRIX — F-001 … F-034, old build → ZCode 3.14.0

This is the accepted regression matrix for the 34 findings published in [EVIDENCE.md](../EVIDENCE.md).
**The old findings themselves are unchanged.** The root [EVIDENCE.md](../EVIDENCE.md) and
[REPORT.md](../REPORT.md) remain the historical record for the earlier hashed builds; this file adds
a new-build status per finding.

Version relationship — each component against its own predecessor, never the desktop version against
the server bundle:

```
desktop   3.11.2 (Linux, audited)  →  3.14.0 (Windows, live)
server    3.12.3 (WSL,   audited)  →  3.14.0 (WSL,     live)
```

Primary new-side evidence used throughout: [MODULE-CLUSTER-DIFF.md](MODULE-CLUSTER-DIFF.md)
(whole-cluster deletion), [SYMBOL-DIFF.md](SYMBOL-DIFF.md) (20/20 probes zero with validated
controls), [SNAPSHOT-HIT-CLASSIFICATION.md](SNAPSHOT-HIT-CLASSIFICATION.md) (775 hits classified;
combination test calibrated and negative), plus the per-topic sections of [DELTA.md](DELTA.md).

## Status tally

| new status | count | findings |
|---|---|---|
| `STILL_PRESENT` | **7** | F-023, F-025, F-026, F-027, F-028, F-029, F-032 |
| `FIXED` | **0** | — |
| `FIXED_BY_REMOVAL` | **24** | F-001 … F-022, F-024, F-033 |
| `PARTIALLY_FIXED` | **0** | — |
| `CHANGED` | **0** | — |
| `NOT_APPLICABLE` | **3** | F-030, F-031, F-034 |
| `UNKNOWN` | **0** | — |
| **total** | **34** | |

`FIXED` is 0 on purpose. Nothing was repaired in place; the code paths that caused the findings
were deleted wholesale. Calling any of these "FIXED" would misdescribe the mechanism, so
`FIXED_BY_REMOVAL` is used throughout.

`UNKNOWN` is 0 because the structural evidence (module clusters deleted, 20/20 symbol probes at
zero, calibrated negative combination test) decides the *code* question for every finding. Where
residual uncertainty exists it is **server-side or runtime**, and it is recorded in each row's
interpretation as a limitation rather than inflating an `UNKNOWN` status. The one row where a
reviewer could reasonably prefer `UNKNOWN` is F-032 (the artifact it named no longer exists on this
platform); the reasoning is given inline.

## The matrix

| ID | old status | new status | new evidence | interpretation | conf |
|---|---|---|---|---|---|
| F-001 | PRESENT | **FIXED_BY_REMOVAL** | `RepoSnapshotSidecarService` 2→0 / 1→0; `repoSnapshotSidecarService.ts` module deleted | The unconditionally-constructed service no longer exists, so its unguarded instantiation cannot occur. Not "guarded"; removed. | HIGH |
| F-002 | PRESENT_OBSERVED | **FIXED_BY_REMOVAL** | `captureBeforePrompt` 5→0; `scheduleRepoSnapshotSidecar` 2→0; host module `zcodeAgentService.ts` survives with `capture` 13→0, `repoSnapshot` 26→0 | Hook removed from a surviving host — the strongest form of this evidence (see [DELTA.md](DELTA.md) §4). | HIGH |
| F-003 | PRESENT | **FIXED_BY_REMOVAL** | `writeRepoSnapshotPlainArchive` 2→0; `repoSnapshotTarWriter.ts` deleted; `meta/prompt.json` producer absent | No archive builder, so prompt text is not packaged by any repo-capture path. | HIGH |
| F-004 | PRESENT | **FIXED_BY_REMOVAL** | `captureRepoWikiSnapshot` 3→0; `repo-wiki` cluster (22 modules) deleted; `captureTaskCompleteUpdate` + `repo-wiki-update` 0 | Terminal-stage wiki capture path removed with the feature. | HIGH |
| F-005 | PRESENT | **FIXED_BY_REMOVAL** | `GIT_LIST_FILES_ARGS = ["ls-files","--cached","--others","--exclude-standard","-z"]` 0 in new; `--others`/`--exclude-standard` 0 in new server | The three-flag workspace enumeration is gone. Residual `ls-files --stage -z -- <paths>` is a different, path-scoped git-UI query. | HIGH |
| F-006 | PRESENT | **FIXED_BY_REMOVAL** | `walkGitMetadataFiles` 3→0; `appendRootGitMetadataPaths` 2→0; `skipDirectoryNames` 2→0; `repoSnapshotScanner.ts` deleted | The dedicated `.git` walker and the walker's `.git` skip-set are both gone. | HIGH |
| F-007 | PRESENT | **FIXED_BY_REMOVAL** | `repoSnapshotScanner.ts` / `repoSnapshotFilter.ts` deleted | The exclude-then-re-add construction lived entirely in deleted modules. | HIGH |
| F-008 | OBSERVED_ONLY | **FIXED_BY_REMOVAL** [CODE-LEVEL] | `repoSnapshotScanner`/`Hasher`/`TarWriter` deleted; 0 manifests produced by any 3.14.0 code path | Old manifests contained `.git/**`; the code that produced them is gone. **Runtime not independently observed** — no claim that 3.14.0 "never uploaded". | MED |
| F-009 | PRESENT_OBSERVED | **FIXED_BY_REMOVAL** | `REPO_SNAPSHOT_MAX_FILE_BYTES` 2→0; `repoSnapshotFilter.ts` deleted | The 1 MB limit and the `.git` short-circuit that bypassed it are gone together. | HIGH |
| F-010 | PRESENT | **FIXED_BY_REMOVAL** | `shouldIncludeRepoSnapshotPathBeforeSample` 3→0; `looksLikeSecretPath` 2→0; `secretBasenames` 2→0; `isRootGitMetadataFile`/`hasGitInternalSegment` 0 | The gate that returned `include:true` for `.git` before size/secret checks does not exist. No filter layer to bypass. | HIGH |
| F-011 | PRESENT | **FIXED_BY_REMOVAL** | `writeRepoSnapshotPlainArchive` 0; `meta/manifest.json` producer absent | No archive is constructed, so the manifest↔archive relationship has no instance. | HIGH |
| F-012 | PRESENT_OBSERVED | **FIXED_BY_REMOVAL** | `GLOBAL_CONFIG_SOURCES` 3→0; `GLOBAL_CONFIG_PATHS` 4→0; collector + `extra-files/` packer deleted | Nine-group collection removed; `settings.behavior.json`/`subagents.json`/`memory.json`/`skills.json` each 1→0. | HIGH |
| F-013 | PRESENT_OBSERVED | **FIXED_BY_REMOVAL** | `SENSITIVE_KEY_PATTERN` 2→0; `sanitizeUnknown` 4→0 | The key-name-only sanitizer was part of the removed global-config packer. `<redacted>` survives (4→3) in other redaction paths, so redaction as a family persists — but the F-013 mechanism does not. | HIGH |
| F-014 | PRESENT | **FIXED_BY_REMOVAL** | `ZCODE_REPO_SNAPSHOT_UPLOAD_CREDENTIAL_URL` constant **2→0** (declaration + use, both in deleted modules); endpoint string `/api/v1/snapshot/upload-credential` 1→0 server, 3→0 desktop; diagnostics module deleted | The snapshot credential endpoint is no longer requested. Residual `upload-credential` = feedback's own `/feedback/attachment/upload-credential`. (The old-side constant count is 2, not 1: the row is labelled with the constant *name*, which occurs twice; the *endpoint string* occurs once.) | HIGH |
| F-015 | PRESENT | **FIXED_BY_REMOVAL** | `assertSupportedEncryption` 2→0; credential-response validation module deleted | No credential response to validate; no RSA public key handling. | HIGH |
| F-016 | PRESENT | **FIXED_BY_REMOVAL** | `encryptArchive` 2→0; `aes-256-ctr` 0 in new server; residual desktop hit is an SSH library cipher table | No AES-256-CTR content encryption in ZCode code on the snapshot path. | HIGH |
| F-017 | PRESENT | **FIXED_BY_REMOVAL** | `RSA_PKCS1_OAEP_PADDING` 0; `oaepHash` 0; `rsa-oaep-sha256` 0; `publicEncrypt` 0 (server & desktop) | No key-wrapping path exists, so the old envelope cannot be produced. The old limitation (capability ≠ observed decryption) is moot. | HIGH |
| F-018 | PRESENT | **FIXED_BY_REMOVAL** | `buildObjectUploadTarget` 0; `uploadPostObject` 0; `uploadPutObject` 0; `PostObject` 0; `repo-snapshot.tar.gz.enc` 0 | The snapshot OSS upload path is gone. A separate feedback OSS upload exists (user-initiated attachments). | HIGH |
| F-019 | PRESENT | **FIXED_BY_REMOVAL** | `encrypted_aes_key` 2→0; `base_snapshot_id` 4→0 | The OSS callback fields the finding described are no longer sent by any ZCode path. | HIGH |
| F-020 | PRESENT_OBSERVED | **FIXED_BY_REMOVAL** [CODE-LEVEL] | `markAcceptedManifest` 3→0; `lastAcceptedManifestHash` 8→0; `repoSnapshotStateRepo.ts` deleted | The state write that recorded client-side upload success no longer exists. **Runtime not independently observed**; the finding's old runtime evidence stands historically. | MED |
| F-021 | PRESENT_OBSERVED | **FIXED_BY_REMOVAL** [CODE-LEVEL] | `repoSnapshotPendingManager` 6→0; `repoSnapshotPendingCleanup.ts` deleted; no `*.enc` present in `~/.zcode` | No pending/tmp artifact lifecycle exists. Runtime observation: 0 `*.enc` files after the update (a `NOT OBSERVED`-style check, not proof). | MED |
| F-022 | PRESENT | **FIXED_BY_REMOVAL** | `repoSnapshotIndexingEnabled` 4→0; `repoSnapshotIndexingUserConfigured` 4→0; `instantGrepIndexingEnabled` **3→0** | The setting and the subsystem it failed to gate are both gone. This is `FIXED_BY_REMOVAL`, not `FIXED` — the setting no longer exists to be a non-gate. | HIGH |
| F-023 | PRESENT | **STILL_PRESENT** | `checkpoint@zcode.local` 2→2 (both sides); `refs/zcode/checkpoints` 2→2, 1→1 | Control surface unchanged. The local git checkpoint system remains, still distinct from the (now removed) upload system. This is the control that proves the comparison is valid. | HIGH |
| F-024 | PRESENT | **FIXED_BY_REMOVAL** | `RepoWiki` 290→0; `repoWiki` 49→0; `repo-wiki` cluster 22 modules deleted; `LocalWorkspaceRepoReader` 4→0 | Both channels gone — the LLM-generation channel and the snapshot channel. Stronger than trigger removal. | HIGH |
| F-025 | PRESENT | **STILL_PRESENT** | `sdk.rum.aliyuncs.com` 8→8 (desktop, byte-identical) | ARMS RUM endpoint untouched by the removal. Telemetry surface survives — deliberately in scope only as a control. | HIGH |
| F-026 | PRESENT | **STILL_PRESENT** | `log.aliyuncs.com` 2→2 (desktop, byte-identical) | SLS endpoint untouched. | HIGH |
| F-027 | PRESENT_OBSERVED | **STILL_PRESENT** | `deviceMid` 54→62 (srv), 90→116 (dsk); `X-Device-Mid` 5→6, 6→7 | Mechanism persists and expanded slightly. Worth noting for any follow-up, but the finding's claim holds unchanged. | HIGH |
| F-028 | UNKNOWN_OLD → OBSERVED | **STILL_PRESENT** | `~/.zcode/cli/db/db.sqlite` present (21,835,776 B at 2026-09-20 11:30:21 +0800 — a live, growing DB); `~/.zcode/v2/tasks-index.sqlite` present; `taskIndexRepo` present in new bundle | Local SQLite session storage persists. No upload path for it was identified in 3.14.0 either. Size is a moving target and is timestamped here rather than asserted as a fixed value. | HIGH |
| F-029 | ABSENT_CONFIRMED | **STILL_PRESENT** | `embedding` 0 in new server; 554 in new desktop (library-only, was 738); `sqlite-vec`/`faiss`/`qdrant`/`lancedb`/`chromadb` all 0 in **both** artifacts; `hnsw` 0 in server but **6 in both desktops** (SurrealQL syntax-highlighting keyword in a bundled grammar, unchanged old→new) | Absence claim holds, scoped as before: no application-level embedding/indexing pipeline in either artifact. The `hnsw` hits are a third-party grammar, not an index implementation. | HIGH |
| F-030 | PRESENT_OBSERVED | **NOT_APPLICABLE** | WSL sandbox/enumeration code deleted with the subsystem | The finding concerned whether Remote WSL was exempt from capture. With no capture subsystem, there is nothing to exempt. Not a fix; the subject no longer exists. | HIGH |
| F-031 | PRESENT | **NOT_APPLICABLE** | `workspaceIdentity` 745→700 (concept survives for session/browser context); its capture-suppression early-return lived in the deleted `repoSnapshotSidecarService.ts` | `NOT_APPLICABLE_AFTER_REMOVAL`, explicitly **not** `FIXED`. The gate is not repaired — the function containing it is gone, and `workspaceIdentity` now serves unrelated purposes (it expanded desktop-side, 3362→3505). | HIGH |
| F-032 | ABSENT_CONFIRMED | **STILL_PRESENT** | new `ZCode.exe` (Windows PE): `upload-credential` 0, `RepoSnapshot` 0, `repo-snapshot` 0, `captureBeforePrompt` 0 — same as old ELF | The absence claim re-verified on the successor binary. **Caveat:** the exact artifact the finding named (`/opt/ZCode/zcode`, Linux ELF) no longer exists on this platform; this is corroboration on a different object format, not an identical reproduction. A reviewer could prefer `UNKNOWN`; `STILL_PRESENT` is chosen because the claim is an absence claim and absence is directly observable in the new binary. | MED |
| F-033 | PRESENT_OBSERVED | **FIXED_BY_REMOVAL** | the silent-error-swallowing hook is gone with `enqueueRepoSnapshotCaptureIntent`; `captureStage` 10→0 | The subsystem that emitted no logs and swallowed upload errors does not exist, so there is no logging behavior to characterise. | HIGH |
| F-034 | OBSERVED_ONLY | **NOT_APPLICABLE** | capture-anchoring runtime data has no current-build counterpart; `~/.zcode/v2/checkpoints` absent, 0 `*.enc` | The finding anchored old observed captures to the old build. That historical claim is unaffected, but it has no application to the current build — there is no capture behavior to anchor. | MED |

## Reading discipline

**Counting convention.** Every symbol count in this matrix is a **case-sensitive raw byte
occurrence** count against the frozen artifacts. The `zcodeAgentService.ts` table in
[DELTA.md](DELTA.md) is explicitly case-insensitive and is labelled there. Two figures in the
audit are extractor-dependent and only their **deltas** are load-bearing: the
`zcodeAgentService.ts` module size (audit 174,083 → 179,586 B; independent review 174,242 →
179,745 B; re-measurement for publication 173,993 → 179,496 B — all agree on **+5,503 B**) and the
desktop module-comment total (audit 3634 → 3365; independent 3818 → 3549 — both agree on **−269**).

- `FIXED_BY_REMOVAL` is used only where **the whole functional path** that produced the finding is
  deleted. It is not used for "the symptom is gone but the code remains".
- `NOT_APPLICABLE` is used where the finding's subject no longer exists and the finding was not
  itself a bug-fix claim (F-030 exemption, F-031 suppression gate, F-034 build anchor).
- `STILL_PRESENT` is used for findings whose subject survives, **including** the control findings
  (F-023, F-025, F-026) — these are the ones that make the other 24 credible.
- No finding is marked `FIXED`. Reporting 0 `FIXED` alongside 24 `FIXED_BY_REMOVAL` is the honest
  reading: this release removed a subsystem, it did not repair findings.

## Server-side caveat applying to all 34 rows

Every row above is a statement about **client artifacts**. Nothing here establishes what the ZCode
service does with data it received before the update, or with any data it receives from other
clients. That question was UNKNOWN before this follow-up and remains UNKNOWN after it.
