# Snapshot-hit classification — every surviving `snapshot` occurrence in ZCode 3.14.0

**Question this file answers:** does any group of code in the new server bundle satisfy
`workspace/repository files` + `archive/tar/gzip` + `upload` + `manifest/delta` +
`pre-prompt/task trigger`?

**Answer: no.** Zero modules satisfy even 4 of those 5 signals, while the same test run against the
old bundle isolates exactly one module — the audited subsystem itself.

## Counting convention

`snapshot` occurs **775 times across 67 modules** in the frozen new server bundle. That is the
**case-sensitive lowercase** count (`grep -o 'snapshot' | wc -l`). The case-insensitive total is
**1266** (= 775 lowercase + 488 `Snapshot` + 3 `SNAPSHOT`). This file's per-module table accounts for
the lowercase token exactly; the 488 capitalized occurrences are covered by the symbol-probe
evidence ([SYMBOL-DIFF.md](SYMBOL-DIFF.md)) and by the module-cluster deletion
([MODULE-CLUSTER-DIFF.md](MODULE-CLUSTER-DIFF.md)) rather than by this table. The `Snapshot`
aggregate drops 760 → 488.

## Method

Rather than classifying 775 lines by hand, each occurrence was attributed to its owning esbuild
module (nearest preceding `// …/path.ts` comment) and the local context classified as identifier,
string literal, or comment:

| Context kind | Hits |
|---|---|
| identifier / code | 681 |
| string literal | 46 |
| comment | 48 |

Reproduce with [`scripts/snapshot-hit-classify.py`](scripts/snapshot-hit-classify.py):

```sh
python3 scripts/snapshot-hit-classify.py <new/zcode-server.cjs> snapshot
```

**Desktop residuals.** This file's standard — every occurrence attributed to its owning module — is
applied to the **server** bundle, which retains module-path comments. The desktop payload does not
retain application source paths (its own code is emitted as one chunk), so desktop occurrences cannot
be attributed the same way. The desktop's two hyphenated residuals are attributed in
[SYMBOL-DIFF.md](SYMBOL-DIFF.md) §"Disclosed desktop residuals": both are entries in a pre-existing
`isNonLogStateArchivePath` **exclusion deny-list** — name-only residue. Whole-asar per-file scanning
shows the old desktop spreading snapshot tokens across many chunks while the new desktop has 2 hits
total, both that deny-list.

## Classification result

Every one of the 67 modules falls into a category unrelated to repository capture:

| Category | Modules (top by hit count) | What the "snapshot" is |
|---|---|---|
| Session / task state | `zcode-agent/zcodeTaskServiceAdapter.ts` (206), `zcode-agent/zcodeTaskIndexSyncer.ts` (59), `zcode-session/zcodeSessionService.ts` (54), `session/taskChangeSummary.ts` (10), `session/taskIndexRepo.ts` (6), `zcode-session/zcodeSessionApiRetry.ts` (20) | in-memory or indexed snapshot of a conversation/task row |
| Provider / config state | `zcode-agent/zcodeAgentService.ts` (72), `provider/src/facades.ts` (35), `provider-node/src/personal-provider-config-repository.ts` (24), `provider/src/registry-service.ts` (23), `provider/src/account-provider-service.ts` (8) | provider registry/config revision snapshot |
| Protocol schemas | `shared/src/zcode-protocol-v4/*` (`transport` 10, `controller` 8, `rows` 6, `snapshot` 3, `core`, `input-intent`, `toolDisplay`, `command`), `shared/src/zcode-protocol/index.ts` (6), `zcode-protocol-legacy-types.ts` (5) | `kind:"snapshot"` frame variant in the v4 wire protocol; `snapshotRowCount`; legacy compatibility notes |
| Credentials / quota | `official-mcp/officialMcpCredentials.ts` (19), `usage-stats/providers/zcodeMcpQuotaProvider.ts` (7) | credential/plan-scope snapshot |
| Git / diff display | `git/gitService.ts` (22) | file-change snapshot for the diff UI |
| UI / formatting | `bots/statusFormatting.ts` (12), `conversation-share/conversationShareService.ts` (11), `hooks/workspaceHookSettingsModel.ts` (5) | render-state snapshot |
| Process control | `process/processTreeTerminator.ts` (7), `process/processTreeSnapshot.ts` (2) | OS process-tree snapshot |
| Client config / marketing | `client-config/clientConfigService.ts` (6), `marketing-touch/marketingTouchService.ts` (3), `marketingAssetRegistry.ts` (2) | remote config/content snapshot (download direction) |
| Browser automation | `shared/src/browser-use/{snapshot,commands,command-metadata,result}.ts` | DOM/browser snapshot |
| Third-party | `node_modules/@larksuiteoapi/node-sdk`, `node_modules/zod/v4/core/api.js`, `node_modules/@zcode/zcode-cua/*` | dependency-internal uses |
| Misc | `shared/src/{validation,channels,database-startup,localTtft}.ts`, `services/src/node.ts`, `zcode-agent/{zcodeStorageStartupGate,zcodeStdioTransport,zcodeConfigOptions,zcodeProtocolClient}.ts`, `session/{legacyTaskSessionFile,offPeakRuntimeModel}`, `runtime-tools/runtimeCommandEnv.ts`, `zcode-session/zcodeSessionDraftRegistry.ts`, `bots/botsService.ts`, `session/claude-native/importedClaudeHistoryRepair.ts`, `session/importedClaudeSessionRepair.ts`, `session/claude-native/persistImportedClaudeTask.ts`, `model-provider/*`, `provider-node/*`, `hooks/hooksService.ts`, `shared/src/zcode-session-task-status.ts`, `shared/src/task-realtime-core.ts` | as named |

No module in this list performs repository file enumeration, archive construction, or upload. The
full per-module hit table (67 rows) is the direct output of the reproduction script above.

## The combination test (calibration)

Five behavioural signals were scored per module:

| Signal | Tokens |
|---|---|
| A archive | `tar`, `gzip` |
| B upload | `upload`, `postobject` |
| C manifest | `manifest` |
| D workspace enumeration | `ls-files`, `lsfiles`, `--cached`, `exclude-standard` |
| E prompt trigger | `prompt.content`, `capturestage`, `beforeprompt`, `beforesend` |

Result (modules scoring ≥4 of 5):

```
OLD server 3.12.3:  [4/5] A,B,C,E  ../services/src/repo-snapshot/repoSnapshotSidecarService.ts  (10,088 B)
NEW server 3.14.0:  (none)
```

Reproduce with [`scripts/combination-test.py`](scripts/combination-test.py), which also prints the
modules scoring 3/5 so the boundary of the test is visible:

```sh
python3 scripts/combination-test.py <old/zcode-server.cjs>
python3 scripts/combination-test.py <new/zcode-server.cjs>
```

*Provenance of the test.* The five signals and their token lists above are exactly as specified when
this test was defined for the audit. The published script is this follow-up's own runnable
implementation of that specification — the original run used an equivalent ad-hoc implementation
that was not retained. This implementation reproduces the original result exactly (one module at
≥4/5 in the old bundle, none in the new), which is what makes the calibration claim checkable rather
than merely asserted.

The test is **calibrated**: applied to the old bundle it returns exactly the module that the
published audit identified as the sidecar implementation, and nothing else. Applied to 3.14.0 it
returns nothing. This is the strongest single piece of negative evidence in the follow-up — it is
name-independent (it looks for behaviour co-occurrence, not identifiers) and it is validated against
a known positive.

**Disclosed boundary detail.** The 3/5 band contains **11 modules in the old bundle and 2 in the new
one**. The two new-side entries are also present in the old bundle and are therefore not
discriminators: `conversation-share/conversationShareService.ts` (A,B,C — the user-initiated sharing
feature) and a bundled third-party `form-data`/`mime-db` JSON asset (A,B,C). On the old side the 3/5
band additionally contains `shared/src/repo-snapshot-sidecar.ts` and **seven**
`services/src/repo-snapshot/*` modules (`repoSnapshotArtifact`, `repoSnapshotPendingCleanup`,
`repoSnapshotPendingManager`, `repoSnapshotScanner`, `repoSnapshotStateRepo`,
`repoSnapshotUploadClient`, `repoSnapshotUploadWorker`), plus `zcode-agent/zcodeAgentService.ts`
(A,B,E — the hook host). Publishing the band makes clear that the threshold, not a single lucky
token, produces the result.

## Residual generic `snapshot` vocabulary

The word survives in ordinary technical senses (session snapshot, config snapshot, protocol
`snapshot` frame, process tree, browser DOM). `Snapshot` capitalised drops 760 → 488, and the
capitalised `Wiki` token drops 497 → 10. The residual `Wiki` hits are the bundled **Feishu/Lark
SDK** (`open.feishu.cn/open-apis/wiki/v2/spaces`, `moveDocsToWiki`, `知识空间`), i.e. a third-party
dependency, not ZCode's Repo Wiki. The tell for that attribution is that `知识空间` is **87 → 87**
(server) and **174 → 174** (desktop) — byte-identical, i.e. untouched dependency text — while every
Repo Wiki identifier goes to zero.

## Conclusion

No group of code in the 3.14.0 server bundle satisfies the five-signal combination that
characterised the audited repo-snapshot subsystem. The residual `snapshot` vocabulary is
attributable, module by module, to unrelated subsystems.

**Limitation.** String/behaviour co-occurrence cannot exclude a functionally equivalent
implementation written with entirely disjoint vocabulary *and* structured so that the five signals
never co-occur in one module. This is **calibrated negative evidence, not a mathematical proof that
no unknown implementation exists**. See [DELTA.md](DELTA.md) §"What would change this conclusion".
