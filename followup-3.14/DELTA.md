# DELTA — old build → ZCode 3.14.0

Version relationship, stated once and correctly:

```
desktop   3.11.2 (Linux, audited)  →  3.14.0 (Windows, live)
server    3.12.3 (WSL,   audited)  →  3.14.0 (WSL,     live)
```

The server side moved **3.12.3 → 3.14.0**, not 3.11.2 → 3.14.0. The old server bundle
self-declares `ZCODE_VERSION = "3.12.3"`; the old desktop was 3.11.2. This is an independent
update-channel artifact, not an error in the published audit.

## Scope

Three 3.14.0 artifacts were frozen and examined:

| Side | Artifact | Size (B) | SHA-256 (short) |
|---|---|---|---|
| Server | `~/.zcode/server/zcode-server.cjs` | 11,527,731 | `99fcad13…71f003` |
| Server (second bundle) | `~/.zcode/server/agents/glm/zcode.cjs` | 14,796,490 | `8f5cfccf…11ba05` |
| Desktop | Windows install `resources/app.asar` | 326,893,098 | `8604b5f4…b628cb` |

Full hashes and provenance: [evidence/artifact-hashes-3.14.md](evidence/artifact-hashes-3.14.md).
The old-side comparison values are the already-published hashes of the 3.12.3 server bundle
(`e4150318…f6183c`) and the 3.11.2 Linux desktop payload (`e260f753…d90081`).

**All negative claims below are scoped to these three examined new artifacts.** No claim is made
about artifacts that were not examined.

## Headline finding

**The audited repo-snapshot capture/upload subsystem is absent from ZCode 3.14.0 — on both the WSL
server bundle and the Windows desktop payload — together with the entire Repo Wiki feature.**

Four independent lines of evidence:

### 1. Whole module clusters deleted

`services/src/repo-snapshot/*` (20 modules) and `services/src/repo-wiki/*` (22 modules), plus
`shared/src/repo-snapshot-sidecar.ts` and `shared/src/repo-wiki.ts`. Excluding a 300-module zod
v3→v4 dependency consolidation (offset by 16 added `zod/v4` modules) and a 2-module internal
relocation, these are **the only application-level clusters removed**.

Module set totals for the server bundle: 1377 → 1086 module-path comments, 1297 → 1020 unique
modules, **346 removed / 69 added**. → [MODULE-CLUSTER-DIFF.md](MODULE-CLUSTER-DIFF.md)

### 2. All 20 required symbol probes read zero across the audited 3.14.0 artifacts

`RepoSnapshotSidecarService`, `repoSnapshot`, `RepoSnapshot`, `captureBeforePrompt`,
`scheduleRepoSnapshotSidecar`, `captureRepoWikiSnapshot`, `repo-wiki-update`,
`walkGitMetadataFiles`, `appendRootGitMetadataPaths`, `shouldIncludeRepoSnapshotPathBeforeSample`,
`writeRepoSnapshotPlainArchive`, `buildRepoSnapshotGlobalConfigsExtraInputs`, `GLOBAL_CONFIG_SOURCES`,
`GLOBAL_CONFIG_PATHS`, `repoSnapshotIndexingEnabled`, `lastAcceptedManifestHash`,
`markAcceptedManifest`, `repo-snapshot.tar.gz.enc`, `encrypted_aes_key`, `base_snapshot_id`.

Every one: **OLD > 0, NEW = 0, on both server and desktop.** Controls survive byte-identically
(`checkpoint@zcode.local` 2→2, `sdk.rum.aliyuncs.com` 8→8, `log.aliyuncs.com` 2→2).
→ [SYMBOL-DIFF.md](SYMBOL-DIFF.md)

### 3. Calibrated negative combination test

Five behavioral signals were scored per module: **A** archive (`tar`, `gzip`), **B** upload
(`upload`, `postobject`), **C** manifest (`manifest`), **D** workspace enumeration (`ls-files`,
`lsfiles`, `--cached`, `exclude-standard`), **E** prompt trigger (`prompt.content`, `capturestage`,
`beforeprompt`, `beforesend`).

```
OLD server 3.12.3:  1 module at ≥4 of 5 →  ../services/src/repo-snapshot/repoSnapshotSidecarService.ts  (10,088 B)
NEW server 3.14.0:  0 modules at ≥4 of 5
```

The test is **calibrated**: on the old bundle it isolates exactly the module the published audit
identified as the sidecar implementation, and nothing else. It is name-independent — it looks for
behaviour co-occurrence, not identifiers — and it is validated against a known positive.
→ [SNAPSHOT-HIT-CLASSIFICATION.md](SNAPSHOT-HIT-CLASSIFICATION.md)

### 4. Hook removed from a surviving host module

The ordinary prompt path was hosted by `services/src/zcode-agent/zcodeAgentService.ts`. That module
**still exists in 3.14.0** and grew:

| probe inside `zcodeAgentService.ts` | OLD 3.12.3 | NEW 3.14.0 |
|---|---|---|
| module size (main segment) | 173,993 B | **179,496 B** |
| `capture` | 13 | **0** |
| `repoSnapshot` | 26 | **0** |
| `wiki` | 14 | **0** |
| `snapshot` | 153 | 104 (provider-readiness state snapshots) |
| `archive` / `.tar` / `upload` | 2 / 19 / 8 | 2 / 19 / 8 (unchanged, unrelated uses) |

*(counts in this table are case-insensitive; the module size is measured across the module's
segments and only its delta is load-bearing — see the caveat below)*

This is a stronger differential than "the whole module disappeared": the host survived an update,
and the capture hook did not survive with it. The hook functions themselves
(`scheduleRepoSnapshotSidecar`, `enqueueRepoSnapshotCaptureIntent`, `reserveRepoSnapshotSidecar`)
are absent, and their entire target module cluster is deleted.

## The four key questions

| # | Question | Answer |
|---|---|---|
| **Q1** | Do ordinary agent prompts still enter a repo/workspace snapshot upload path? | **NO** — hook removed from a surviving host module; no successor hook identified |
| **Q2** | Does Repo Wiki still trigger that path? | **NO** — the entire Repo Wiki feature (22 modules, including the local generation half) is removed, not just its upload trigger |
| **Q3** | Does the old repo-snapshot subsystem still exist in 3.14.0? | **NO_EQUIVALENT_FOUND** — no equivalent was identified under any name |
| **Q4** | If a repo capture existed, would `.git` regular files still enter scope? | **NO_REPO_CAPTURE_SUBSYSTEM_FOUND** — deliberately *not* phrased as ".git exclusion fixed" |

### On Q4 and the `.git` finding

The old mechanism was a dedicated `.git` walker that re-added what the ordinary workspace walk had
excluded, plus a short-circuit that bypassed the secret-path filter and the 1 MB per-file size check
for `.git` entries. The flags array that drove enumeration
(`["ls-files","--cached","--others","--exclude-standard","-z"]`), the walker
(`walkGitMetadataFiles`), its re-add helper (`appendRootGitMetadataPaths`), the skip-set
(`skipDirectoryNames`), the pre-sample decision function
(`shouldIncludeRepoSnapshotPathBeforeSample`) and the filter module itself are all **absent** from
3.14.0 (0 occurrences across the audited 3.14.0 artifacts).

The supported statement is therefore: **the old `.git` inclusion path is no longer reachable or
identifiable, because no equivalent repo-capture subsystem was identified.** This is a different
claim from "the `.git` exclusion was fixed", and only the former is made here. Nothing in this
follow-up establishes that no other ZCode feature ever reads `.git`.

### On Q2 and Repo Wiki

Both channels are gone: the local generation channel (generator, model client, page builders,
catalog tooling, storage, workspace reader) and the snapshot channel that fed it
(`captureRepoWikiSnapshot` 3→0, `repo-wiki-update` 1→0, `repoWikiManifestHash` module deleted).
Removing only the "abnormal upload" would have left the generator and reader in place; they are not
in place.

The residual `Wiki`/`wiki` vocabulary in 3.14.0 belongs to the bundled Feishu/Lark SDK
(`open-apis/wiki`), a third-party dependency. The tell: its non-ASCII product strings are
**byte-identical** old→new (`知识空间` 87→87 server, 174→174 desktop) while every Repo Wiki
identifier goes to zero.

The new desktop retains exactly **one** hyphenated `repo-wiki` and **one** `repo-snapshot`
occurrence. Both are entries in a pre-existing archive-exclusion **deny-list** consumed by
`isNonLogStateArchivePath` — a privacy-protective list of paths to *exclude* from diagnostic
archives, i.e. the opposite of a capture list. The identical list is present in the old desktop and
carries forward as strings only: no function, type, module or call path of the removed subsystem
exists behind them. → [SYMBOL-DIFF.md](SYMBOL-DIFF.md) §"Disclosed desktop residuals"

## Pipeline status, stage by stage

| Stage | Status in 3.14.0 |
|---|---|
| prompt/task capture trigger | REMOVED |
| workspace enumeration (`ls-files --cached --others --exclude-standard`) | REMOVED |
| `.git` metadata reinclusion walker | REMOVED |
| path/secret filter + 1 MB limit | REMOVED |
| hasher / canonical JSON | REMOVED |
| tar archive (`meta/prompt.json`, `meta/manifest.json`, `files/**`, `extra-files/**`) | REMOVED |
| global config collection (nine groups) | REMOVED |
| AES-256-CTR content encryption | REMOVED |
| RSA-OAEP-SHA256 key wrapping | REMOVED |
| snapshot credential endpoint | REMOVED |
| OSS `PostObject` upload | REMOVED |
| local pending/tmp `.enc` lifecycle + disk quota | REMOVED |
| `lastAcceptedManifestHash` state write | REMOVED |
| **local git checkpoint system** (`refs/zcode/checkpoints`) | **STILL PRESENT** (control) |
| **ARMS RUM + SLS telemetry endpoints** | **STILL PRESENT** (control) |
| **feedback attachment upload (OSS)** | **STILL PRESENT** (unrelated, user-initiated) |
| **conversation-share artifact upload** | **STILL PRESENT** (unrelated, user-initiated, unchanged) |

### Encryption, precisely

The old repo-snapshot encryption chain does not exist on its old use-path in 3.14.0:
`encryptArchive` 2→0, `aes-256-ctr` 0 in the new server (the single desktop residual is a bundled
SSH library's cipher table), `RSA_PKCS1_OAEP_PADDING` 0, `oaepHash` 0, `rsa-oaep-sha256` 0,
`publicEncrypt` 0, `encrypted_aes_key` 0, `base_snapshot_id` 0.

**This is not a statement that 3.14.0 contains no cryptography.** It does — the product has other
cryptographic code, and generic `node:crypto` usage remains (`createCipheriv` 2→1 server,
16→13 desktop, with no snapshot cipher call site). The claim is limited to the removal of the
audited envelope-encryption chain.

### The setting, precisely

`repoSnapshotIndexingEnabled` 4→0 (server) and 23→0 (desktop); its sibling
`repoSnapshotIndexingUserConfigured` 4→0 / 23→0. The old setting did not gate capture (F-022);
in 3.14.0 it **no longer exists**, because the subsystem it failed to gate was removed. That is
`FIXED_BY_REMOVAL`, not "the setting finally works".

### Global config, precisely

The chain COLLECTION → PACKAGE → UPLOAD is gone: `GLOBAL_CONFIG_SOURCES` 3→0,
`GLOBAL_CONFIG_PATHS` 4→0, the collector and packer modules deleted, the `extra-files/` archive
sub-path 1→0. Four of the nine group members drop to exactly zero
(`settings.behavior.json`, `subagents.json`, `memory.json`, `skills.json` — each 1→0).

Other config files persist in 3.14.0 — `mcp.json` 6→5 server / 13→14 desktop, `hooks.json` 2→1 /
2→1, `plugins.json` 3→2 / 7→6 — because **the product still reads those files for their own
features**. The files surviving is not evidence of upload, and no claim of continued collection is
made from their survival.

## Official "仓库百科异常上传修复" — independent classification

Assessed from the delta itself, not from changelog wording. (The changelog is external release
context; it is not used as evidence.)

**→ CASE B: the entire repo snapshot subsystem was deleted.**

Why B and not the alternatives:

- **Not CASE A (only the Repo Wiki trigger removed).** The trigger's target is gone:
  `captureBeforePrompt`, `repoSnapshotSidecarService.ts` and the whole 20-module `repo-snapshot`
  cluster do not exist. Removing only the wiki trigger would have left the per-prompt path intact;
  that path is absent too.
- **Not CASE C (subsystem retained behind a new gate).** No gate exists.
  `GLOBAL_CONFIG_*`, `repoSnapshotIndexingEnabled` (the old non-gate) and the entire filter module
  are gone; there is no conditional left to find. A gated subsystem still ships its code.
- **Not CASE D (rewritten as another upload mechanism).** Two unrelated upload paths survive:
  user-initiated **feedback attachments** (`POST /feedback/attachment/upload-credential`, one
  attachment, no archive, no manifest, no encryption — see
  [UPLOAD-SURFACE-ATTRIBUTION.md](UPLOAD-SURFACE-ATTRIBUTION.md)) and user-initiated
  **conversation sharing** (`POST /shares/preparations/{id}/artifacts`). Neither is new: the
  conversation-share path is semantically unchanged old→new (per-module string sets equal,
  `/shares/preparations` 3→3, `conversationShareArtifactSource` 2→2, `isInsideWorkspace` 5→5,
  `uploadArtifact` 2→2), and its only directory reads target a `.zcode-share` subdirectory of the
  workspace — it is not a repository walk. Neither surviving path is a successor to the removed
  subsystem.
- **Not CASE E (insufficient evidence).** The module-cluster deletion plus the calibrated negative
  combination test decide the code question.

**Scope note beyond the changelog's framing:** the removal is *broader* than "abnormal upload
fixed" — the entire Repo Wiki feature and the entire config-collection path were removed as well.
The delta does not show a targeted repair of an upload defect; it shows deletion of the subsystem.

## Attribution of the residual upload / OSS surface

| Residual | Owner in 3.14.0 | What it is |
|---|---|---|
| `upload-credential` (2 server / 3 desktop), `oss.host` (1), `x-oss-*` (5), `success_action_status`, `security-token` | `services/src/feedback/feedbackHttpClient.ts` | **user-initiated feedback attachment upload**, max attachment 100 MB |
| `ls-files` (2 server / 5 desktop) | `services/src/git/repo/gitCliRepo.ts` | `git ls-files --stage -z -- <paths>` — git staging UI, path-scoped, unchanged from old |
| `--others --exclude-standard` (1, desktop) | bundled third-party npm package | not ZCode code |
| `aes-256-ctr` (1, desktop) | bundled SSH library cipher table | not ZCode code |
| `PostObject`, `repo-snapshot.tar.gz.enc`, `encrypted_aes_key`, `base_snapshot_id`, `RSA_PKCS1_OAEP_PADDING`, `oaepHash`, `rsa-oaep-sha256`, `publicEncrypt` | — | **0 hits** — the audited pipeline is fully absent |

The old-side count for `upload-credential` drops 5→2 rather than to 0 because the endpoint string
also belonged to the surviving feedback subsystem, which posts to its own
`/feedback/attachment/upload-credential` path. The snapshot endpoint constant
`ZCODE_REPO_SNAPSHOT_UPLOAD_CREDENTIAL_URL` (2 occurrences) and the endpoint string
`/api/v1/snapshot/upload-credential` (1 server / 3 desktop) are **0** in 3.14.0.

**Stated plainly: OSS upload is not "completely removed" from ZCode.** It survives for
user-initiated features. What is absent is the audited automatic repo-snapshot upload.

## Tally of the 775 surviving `snapshot` hits

All 775 occurrences of the lowercase token across 67 modules in the new server bundle were
attributed to owning modules and classified. Every module falls into an unrelated category:
session/task state, provider/config registry state, v4 protocol `kind:"snapshot"` frames,
credential/plan snapshots, git-diff display, process-tree snapshots, browser DOM snapshots,
client-config/marketing content snapshots, and third-party dependency internals. **No group of code
satisfies the five-signal criterion.** Details: [SNAPSHOT-HIT-CLASSIFICATION.md](SNAPSHOT-HIT-CLASSIFICATION.md).

## Controls that validate the comparison

| Control | OLD server | NEW server | OLD desktop | NEW desktop |
|---|---|---|---|---|
| `checkpoint@zcode.local` | 2 | **2** | 2 | **2** |
| `refs/zcode/checkpoints` | 2 | **2** | 1 | **1** |
| `sdk.rum.aliyuncs.com` (ARMS RUM) | 0 | 0 | 8 | **8** |
| `log.aliyuncs.com` (SLS) | 0 | 0 | 2 | **2** |
| `deviceMid` | 54 | 62 | 90 | 116 |
| `X-Device-Mid` | 5 | 6 | 6 | 7 |
| `multipart/form-data` | 57 | **57** | 155 | 153 |

Without these, "everything went to zero" could be dismissed as minification or platform packaging.
The byte-identical matches across a Linux→Windows payload change are the strongest available proof
that a zero elsewhere is a real zero. The local git checkpoint system and the telemetry endpoints
are published **as controls only** — this follow-up does not extend the telemetry investigation.
→ [evidence/control-surfaces.md](evidence/control-surfaces.md)

## F-001 … F-034 tally

| status | count |
|---|---|
| `STILL_PRESENT` | 7 |
| `FIXED` | 0 |
| `FIXED_BY_REMOVAL` | 24 |
| `PARTIALLY_FIXED` | 0 |
| `CHANGED` | 0 |
| `NOT_APPLICABLE` | 3 |
| `UNKNOWN` | 0 |

`FIXED` is deliberately 0: nothing was repaired in place, so nothing is described as fixed. 29 rows
carry HIGH confidence, 5 carry MED. → [REGRESSION-MATRIX.md](REGRESSION-MATRIX.md)

## Runtime state (read-only, no prompts sent)

- `~/.zcode/v2/checkpoints` does **not exist**; `0` `*.enc` files anywhere under `~/.zcode`.
- Recorded as **NOT OBSERVED**, not "PROVEN ABSENT": the directory could have been removed by this
  update, by an earlier cleanup, or never have existed on this WSL profile.
- No prompt was sent and no behavior was triggered to test the new build.

## Size context (corroborating only)

Server bundle 13,409,418 → 11,527,731 B (−1,881,687 B, −14.0%); unique modules 1297 → 1020.
**Size decrease alone proves nothing** and is not used as evidence; the conclusion rests on module
sets, symbol probes and the combination test. The size change is corroborating context, consistent
with — but not proof of — a ~42-module cluster removal.

## Limitations (all of them)

1. **Static analysis only.** No packet capture, no TLS interception, no certificate bypass. Nothing
   here observes the wire.
2. **Server-side behavior is UNKNOWN** and was UNKNOWN before. Client absence says nothing about
   what the service retains, processes, or does with previously uploaded data. This applies to every
   row of the regression matrix.
3. **Desktop structural evidence is weaker than server evidence.** The desktop `app.asar` does not
   retain application source paths for its own code (controls also return 0 there), so desktop
   evidence is symbol-level with control validation rather than module-cluster-level. Desktop and
   server nevertheless agree independently.
4. **Absolute values that depend on the extractor are disclosed as such.** The
   `zcodeAgentService.ts` module size is reported here as 173,993 → 179,496 B; the audit's own
   convention gave 174,083 → 179,586 B and an independent reviewer measured 174,242 → 179,745 B.
   All three agree on **+5,503 B**, which is the load-bearing quantity. Likewise the desktop
   module-comment total (this extractor: 3818 → 3549; audit extractor: 3634 → 3365) — both agree on
   **−269**.
5. **Native executables were not compared semantically** (Linux ELF vs Windows PE). The new Windows
   `ZCode.exe` was probed only for the absence of specific strings (F-032), which is valid for an
   absence claim.
6. **Runtime not exercised.** No claim is made that 3.14.0 "never uploads" anything, only that the
   audited code path is not present in the three examined artifacts.

## What would change this conclusion

- A functional equivalent implemented with entirely disjoint vocabulary **and** structured so that
  the five signals never co-occur in one module. Mitigation attempted: reverse-tracing from prompt
  dispatch, Repo Wiki entry points, `.git` handling, config files and upload primitives; none led
  anywhere.
- An additional server-side component (not in the three examined artifacts) performing capture.
  That would be a different artifact, outside the audited surface — and it is precisely the kind of
  claim the original audit already marked UNKNOWN.
- A lazily-downloaded module that is not present in the shipped bundles.

## Post-review corrections applied to this delta (audit trail)

An independent reviewer returned **BLOCK** on supporting statements; the headline conclusion
survived every falsification attempt, and all blocking items were corrected and re-verified:

1. "The only surviving upload path is feedback attachments" was **false** — conversation sharing
   also survives (and is unchanged old→new), so CASE D still closes on the correct grounds.
2. "There is no second bundle where a subsystem could be hiding" was **false** — the second
   server-side bundle was frozen and probed (0 hits on every symbol).
3. Two desktop residuals (`repo-snapshot` 9→1, `repo-wiki` 99→1) were undisclosed — now attributed
   to the pre-existing archive-exclusion deny-list.
4. `instantGrepIndexingEnabled` was recorded 1→0; it is **3→0**.
5. `hnsw` was recorded 0 everywhere; it is **0 in the server but 6 in both desktops** (a SurrealQL
   syntax-highlighting keyword in a bundled grammar). The F-029 conclusion is unaffected.
6. Counting conventions were unstated — now labelled (this file's `zcodeAgentService.ts` table is
   case-insensitive; [SYMBOL-DIFF.md](SYMBOL-DIFF.md) and the matrix are case-sensitive).
7. Extractor-dependent absolute values are now disclosed with only their deltas load-bearing.
8. A bogus probe row (`embedded_aes_key`, 0 occurrences everywhere) was deleted.
9. `repo-snapshot` (hyphenated) OLD server was recorded 9; the actual count is **34**.
10. `REPO_WIKI_DELTA` carried a stale setting count — corrected.
11. The credential-URL row was relabelled: the constant *name*
    `ZCODE_REPO_SNAPSHOT_UPLOAD_CREDENTIAL_URL` occurs **2×** in the old server, and the endpoint
    *string* occurs separately (1 server / 3 desktop). Both are 0 in 3.14.0.
12. The reduced-counts table was server-scoped, hiding desktop values — rewritten with all four
    artifact columns.

After the final fixes the whole symbol table was re-audited cell-by-cell, and the independent
reviewer of this publication re-measured **every numeric cell of the published table: 61 numeric
rows × 4 artifact columns = 244 cells, 0 mismatches**, and confirmed no table in it remains
server-scoped. (The audit's internal review reconstructed 60 rows / 240 cells for its own copy of
the file; the published table carries one additional disclosed row — `--cached` in the
reduced-counts table — for 61 / 244.) Final verdict: **ACCEPT**.
