# SOURCE-BINARY-MAPPING — official source ↔ frozen 3.14 binary, and the provenance boundary

Two questions, kept strictly apart:

1. **Do the frozen binaries and the published source describe the same software?** — answered
   structurally, with numbers, below.
2. **Are they the same commit?** — **not answered, and this round does not claim it.**

## Method

The shipped server bundle is an esbuild single-file output that preserves a `// <relative-path>`
comment above each bundled module. Those comments are relative to the bundle's entry directory, so the
original monorepo layout is recoverable:

```
../<pkg>/src/<rest>      →  packages/<pkg>/src/<rest>
../../node_modules/<x>   →  third-party, not part of the audited source tree
```

Each frozen bundle's comment set was mapped onto the official tree and classified. Reproduce with
[`scripts/source-binary-map.py`](scripts/source-binary-map.py):

```sh
python3 scripts/source-binary-map.py <bundle.cjs> <official-source-checkout>
```

Convention: comments are matched only as whole lines beginning `// ` and ending in
`.ts|.tsx|.js|.json`, then de-duplicated. Absolute counts therefore differ slightly from the binary
audit's `MODULE-CLUSTER-DIFF.md` extractor (which reported 1,086 comments for the same 3.14.0 bundle);
the load-bearing quantity is the composition of the difference, not the total.

## Result — 3.14.0 bundle vs official tree

| Metric | Value |
|---|---|
| Official tracked files | 6,973 |
| Bundle module comments | 1,012 |
| Third-party | 506 |
| Workspace | 506 |
| `DIRECT_NAME_MATCH` | **464 (91.7%)** |
| `MISSING_IN_SOURCE` | **42** |

## Result — old 3.12.3 bundle vs official tree (positive control)

| Metric | Value |
|---|---|
| Bundle module comments | 1,289 |
| Third-party | 783 |
| Workspace | 506 |
| `DIRECT_NAME_MATCH` | **429 (84.8%)** |
| `MISSING_IN_SOURCE` | **77** |

Among the 77, in the old bundle:

```
[20] packages/services/src/repo-snapshot
[22] packages/services/src/repo-wiki
[ 1] packages/shared/src/repo-snapshot-sidecar.ts
[ 1] packages/shared/src/repo-wiki.ts
```

**This is the control that makes the 3.14.0 result meaningful.** The same extractor, the same tree,
the same classifier: applied to the build that *had* the audited subsystem, it recovers that
subsystem by structure — 44 modules — without looking for a single symbol name. Applied to the
3.14.0 build it returns zero for both clusters.

## The 42 modules the 3.14.0 bundle has and the tree does not

| Cluster | Modules |
|---|---|
| `packages/services/src/bots/**` | 26 |
| `packages/services/src/cloud-content/**` | 3 |
| `packages/services/src/marketing-touch/**` | 3 |
| `packages/services/src/output-style/**` | 2 |
| `packages/services/src/session/sessionModeOptions.ts` | 1 |
| `packages/shared/src/{bots,cloudContent,coding-plan-signature-feature,marketingTouch,opencode-model-id,rewardsEmbedded,web-remote-control-rpc-transport}.ts` | 7 |

**None of the 42 is a repo-snapshot or Repo Wiki module.** They are unrelated feature clusters
(bots/channel integrations, cloud content bundles, marketing assets, output styles, entitlement-ish
shared flags).

## Static mapping table — required coverage

Classification vocabulary: `DIRECT_NAME_MATCH` (same path, same name, same role),
`STRUCTURAL_MATCH` (same role, structure recoverable, name or location shifted),
`BEHAVIOR_MATCH` (same declared behaviour, different code shape), `NOT_MAPPABLE` (no counterpart),
`CONFLICT` (counterpart exists and contradicts).

| Official source path | Frozen 3.14 bundle observation | Class |
|---|---|---|
| `packages/services/src/zcode-agent/zcodeAgentService.ts` (235,487 B) | Module comment `services/src/zcode-agent/zcodeAgentService.ts` present; host module survives; `snapshot` hits are session/provider state in both | **DIRECT_NAME_MATCH** |
| `packages/services/src/feedback/feedbackHttpClient.ts` (36,182 B) | Module comment present; `/feedback/attachment/upload-credential`, `oss.host`, `x-oss-*`, `success_action_status` all attributable to this module in the bundle | **DIRECT_NAME_MATCH** |
| `packages/services/src/git/gitCheckpoint.ts`, `gitCheckpointService.ts`, `git/repo/gitCheckpointHelpers.ts` | Checkpoint refs `refs/zcode/checkpoints/${workspaceHash}/${checkpointId}`; `git-checkpoint-index` path. Binary audit's F-023 (local checkpoint = pure-local git refs, `git restore`) | **DIRECT_NAME_MATCH** |
| `packages/services/src/git/repo/gitCliRepo.ts` | `ls-files`/`--cached` residuals in the 3.14 bundle attribute here (git staging UI), not to snapshot enumeration | **DIRECT_NAME_MATCH** |
| `packages/services/src/paths.ts` (`getGitCheckpointIndexRootDir`) | `git-checkpoint-index` storage entry in the binary's storage catalog | **DIRECT_NAME_MATCH** |
| `packages/desktop/src/main/appARMSBootstrap.ts`, `armsUserIdentity.ts`, `armsEventRedaction.ts`, `desktopNetworkTelemetry.ts` | Desktop bundle keeps `sdk.rum.aliyuncs.com` (8) and `log.aliyuncs.com` (2) unchanged old→new; ARMS RUM bootstrap present in source | **STRUCTURAL_MATCH** — the endpoint literals live in the third-party `@arms/rum-electron` package (not tracked in the tree), while the application-level wiring is open source |
| `packages/services/src/device/deviceMid.ts` | `deviceMid` 54→62 (server) and 90→116 (desktop); `X-Device-Mid` header 5→6 / 6→7. Source comment: deviceMid is a cross-surface device identity read by the billing header, feedback and onboarding | **DIRECT_NAME_MATCH** |
| `packages/desktop/src/main/manifestUpdateProvider.ts:222` (`"X-Device-Mid"`) | Header observed in the desktop bundle | **DIRECT_NAME_MATCH** |
| `packages/services/src/conversation-share/*` (8 files) | `conversationShareService.ts` present; `/shares/preparations`, `/shares/preparations/{id}/artifacts`, `/confirm`; rename-invariant old→new in the binary audit | **DIRECT_NAME_MATCH** |
| `packages/services/src/prompt-attachment-transfer/*` | Prompt-attachment pre-transfer to a remote execution host; local host returns a zero-copy path | **BEHAVIOR_MATCH** — this is the mechanism behind the observed "pre-transfer before send" surface; it is a host transfer, not a cloud capture |
| `packages/services/src/telemetry/telemetryCore.ts`, `apps/zcode-cli/packages/telemetry/*` | Telemetry surfaces survive in both bundles; no snapshot telemetry module | **STRUCTURAL_MATCH** |
| `packages/services/src/session/*`, `zcode-session/*` session-state snapshots | `snapshot` vocabulary in the 3.14 bundle classified as session/task state | **BEHAVIOR_MATCH** |
| `packages/provider/src/*`, `packages/provider-node/src/*`, `packages/model-option-map/src/*` | Provider/config revision snapshots — the binary audit's dominant `snapshot` category | **BEHAVIOR_MATCH** |
| `packages/shared/src/zcode-protocol-v4/*` | `kind:"snapshot"` protocol frame variant, `snapshotRowCount` | **BEHAVIOR_MATCH** |
| `packages/services/src/repo-snapshot/**` | — | **NOT_MAPPABLE** (absent from source; absent from 3.14 bundles; present only in old bundles) |
| `packages/services/src/repo-wiki/**`, `packages/shared/src/repo-wiki.ts`, `repo-snapshot-sidecar.ts` | — | **NOT_MAPPABLE** (same) |
| `packages/services/src/{bots,cloud-content,marketing-touch,output-style}/**` | Present in the 3.14.0 bundle; **absent from the tree** | **NOT_MAPPABLE** — a source-publication gap, not an audit finding |
| — | — | **CONFLICT**: none identified |

No `CONFLICT` row exists. The audited subsystem is `NOT_MAPPABLE` in both the source tree and the
3.14.0 binaries, and every surviving upload/telemetry/checkpoint surface maps to a source module that
is unrelated to it.

## Optional build

A server bundle was built from the frozen tree in an isolated copy. Classification
**`BUILD_COMPLETED_NONIDENTICAL`**; built bundle 5,757,271 B / `0ad8f300…03fa`, 466/466 workspace
modules `DIRECT_NAME_MATCH` against the tree, 0 hits for all 22 old symbols. Full detail, including
the unexplained third-party residual: [BUILD-CORRESPONDENCE.md](BUILD-CORRESPONDENCE.md).

## Provenance boundary — what is and is not established

The frozen Windows 3.14 desktop payload records its build commit in
`out/metadata/build-meta.json`: **`a1328db1`**. The official source HEAD is
**`872ad960de7ec172591f7e1952f7849229f94521`**.

| Question | Status |
|---|---|
| Is `a1328db1` an object in the official repository? | **No** — `git cat-file -t a1328db1` → `fatal: Not a valid object name`. |
| Does the string `a1328db1` occur anywhere in the frozen tree? | **No** — 0 occurrences. |
| Are the two identifiers the same? | **No.** They are different identifiers. |

**NOT PROVEN SOURCE-IDENTICAL.** What is established is high consistency — the same declared version
(3.14.0), the same monorepo layout, the same module names, the same symbols, the same surviving
upload paths and the same absence of the audited subsystem — and nothing stronger. **`872ad96` must
not be described as "the exact source commit of the shipped `app.asar`"**, and no such claim is made
anywhere in this repository.

The honest statement of the relationship, in decreasing order of confidence:

1. The frozen binaries and the published tree are the **same product line at the same declared
   version** — established (module names, symbols, version string, layout).
2. They are **semantically highly consistent** — established for the surfaces mapped above.
3. The tree is **not a complete mirror** of the shipped build's source — established: 42 workspace
   modules in the 3.14.0 bundle have no counterpart in the tree (§"The 42 modules…"). The vendor's own
   `NOTICE.md` §四 states that the repository does not promise to provide all functions of the official
   product and that the actually released source and build artifacts govern.
4. The shipped binaries were built **from this exact commit** — **not established, and not claimed.**
   Establishing it would require a reproducible build with a matching artifact hash or an equivalent
   provenance mapping. Neither was achieved (see `BUILD_COMPLETED_NONIDENTICAL`).

**Consequence for this round's conclusion.** The corroboration in
[SOURCE-CORROBORATION.md](SOURCE-CORROBORATION.md) does not rest on exact source identity. The
3.14.0 *binary* finding stands on the frozen bundles, which are independent of the source
publication; the *source* finding stands on the frozen tree. Their agreement on the absence of
`repo-snapshot` / `repo-wiki` is corroboration, and it is stated as corroboration.

**Limitation.** Module-path comments are a build artifact and could in principle be absent or altered
in a differently-configured build; the 91.7% match rate is evidence that they are intact for this
payload set, not a guarantee. The comparison covers the server bundle and, for symbol counts, the
desktop payload. It observes no runtime behaviour.
