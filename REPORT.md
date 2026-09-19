# ZCode Client Data Flow Audit

**Audit date:** 2026-09-19 · **Auditor:** independent local forensic audit (see METHODOLOGY.md) · **Audited build:** desktop `app.asar` mtime 2026-09-04, WSL server bundle `zcode-server.cjs` mtime 2026-09-17 (hashes in evidence/artifact-hashes.md)

## Executive Summary

In the audited build, a logged-in ZCode client captures a complete archive of the workspace — including the full `.git` directory (history objects, pack files, reflog, config), the full text of every user prompt, and the user's global agent configuration files — before each prompt and on successful task completion. The archive is encrypted with AES-256-CTR under a randomly generated data key, the data key is wrapped with an RSA public key delivered by the ZCode server, and the encrypted archive is uploaded to an Aliyun OSS host whose credentials the server delivers at upload time. Because the wrapped data key is returned to the server through the OSS callback, the server possesses the corresponding capability to decrypt every snapshot under this envelope-encryption design. The client-side setting `repoSnapshotIndexingEnabled` does not gate capture or upload anywhere in the audited server bundle; the snapshot sidecar is instantiated unconditionally. The user-visible "checkpoint" rollback feature is a separate, purely local git-refs mechanism.

These statements describe client-side behavior only. This audit makes no claims about server-side retention, indexing, training use, or personnel access; those are listed as unknowns.

## Scope

- In scope: client-side code (WSL server bundle `zcode-server.cjs`, desktop `app.asar`), local ZCode artifacts (checkpoint state/manifests, settings, logs, SQLite), and runtime observations on the audited machine.
- Out of scope: server-side behavior, network capture (none was performed), other machines' installations, the CLI runtime's non-snapshot functionality.

## Tested Build

| Component | Location (sanitized) | Size | mtime | SHA-256 |
|---|---|---|---|---|
| Desktop Electron app bundle | `/opt/ZCode/resources/app.asar` | 307,138,103 B | 2026-09-04 16:08 +0800 | `e260f753…a2d90081` |
| Desktop Electron executable | `/opt/ZCode/zcode` | 206,036,184 B | 2026-09-04 16:06 +0800 | `7f7881d0…7daf0b03b` |
| WSL server bundle | `~/.zcode/server/zcode-server.cjs` | 13,409,418 B | 2026-09-17 20:49 +0800 | `e4150318…778c6183c` |

Full hashes: [evidence/artifact-hashes.md](evidence/artifact-hashes.md). A separate Windows-side server bundle was not present; on the Windows side the desktop bundle contains equivalent snapshot code (code excerpt 32). The server bundle auto-updates independently of the desktop app.

## Artifact Identification

- `zcode-server.cjs` is a minified Node bundle; source-file comments inside it (e.g. `// ../services/src/repo-snapshot/repoSnapshotScanner.ts`) identify the original module layout of the repo-snapshot subsystem.
- `app.asar` contains the desktop application; the snapshot capture/upload logic appears in minified form there as well (identical `captureBeforePrompt` logic, see excerpt 32).
- Local artifacts: `~/.zcode/v2/checkpoints/<workspace-id>/{state.json, manifests/*.json, extra-manifests/*.json}` on both machines. A census found 6 state files + 28 JSON manifests on the WSL side, 1 state file + 3 manifests on the Windows side, and **zero** `.enc`/tar/tmp residues.

## Methodology

Static analysis of the minified bundles with line-numbered excerpts (long lines truncated at 240 columns), each excerpt reproducible by `scripts/locate-snapshot-code.sh`; cross-checking of every code path against local artifacts (manifests, state files, settings, logs, SQLite); runtime observation on the live machine. Raw artifacts were hashed and never modified; publication uses sanitized derivatives only. Evidence classes and chain of custody: [METHODOLOGY.md](METHODOLOGY.md). Limitation: no network capture was performed; the actual OSS host is runtime-delivered and not locally observable.

## Evidence Classification

- **[CONFIRMED-CODE]** — direct code evidence from the audited bundles (line-numbered excerpt).
- **[CONFIRMED-LOCAL-ARTIFACT]** — direct evidence from local state/manifest/DB/log/config artifacts.
- **[CONFIRMED-RUNTIME]** — direct observation of the running system on the audited machine.
- **[INDEPENDENT-CORROBORATION]** — an independent third-party report consistent with local evidence.
- **[INFERRED]** — strongly supported by code structure + known facts, without direct runtime/server proof.
- **[UNKNOWN]** — cannot be confirmed from local evidence.

Every finding: [EVIDENCE.md](EVIDENCE.md).

## Data Flow

```
workspace (incl. .git/**)
  │ (1) git ls-files --cached --others --exclude-standard        [server.cjs ~310540, ~310596]
  │ (2) appendRootGitMetadataPaths + walkGitMetadataFiles         [~310624] re-add the whole .git dir
  ▼
scanner/filter — excludes node_modules/.cache/.turbo/dist/build/out/.next/coverage,
  │              .env*/.npmrc/id_rsa*/token|secret paths, symlinks, binaries, files >1 MB
  │              BUT the .git short-circuit runs BEFORE all of these               [~310488]
  ▼
tar (self-implemented Node tar) + gzip                                           [~310121, ~309820]
  │   meta/prompt.json           ← full user prompt text                         [233388-233397]
  │   meta/manifest.json         ← {path,sizeBytes} of every included file
  │   meta/delta.json            ← incremental snapshots
  │   extra-meta/manifest.json   ← global config group listing
  │   files/<path>               ← full content of every included file (incl. .git/**)
  │   extra-files/<group>/<path> ← mcp/hooks/memory/instructions/subagents/skills/
  │                                commands/plugins/settings.behavior            [310341-310359]
  ▼
AES-256-CTR (random 32-byte dataKey, 16-byte nonce prefix)                       [~310048-310067]
  │   dataKey wrapped with server-delivered RSA public key (RSA-OAEP-SHA256)      [310069-310077]
  ▼
pending/<id>.tar.gz.enc  (deleted after successful upload; retained on failure)  [~310259-310266]
  ▼
POST → Aliyun OSS (host/credentials delivered at runtime by the server)          [~312598-312626]
  ▼
OSS callback → ZCode server: update_type, checksum (sha256 of PLAINTEXT),
               encrypted_aes_key, base_snapshot_id, attribution metadata         [~312527-312556]
```

No standalone client-side embedding/vector-index subsystem was identified (F-029). WebSocket endpoints: none found in the server bundle.

## Snapshot Triggering

- Before **every prompt**: `sendPrompt` → `scheduleRepoSnapshotSidecar` → `captureBeforePrompt` with `captureStage: "prompt"` and `content: params.prompt.content` (server.cjs ~233379, ~234473; excerpts 07/23). [CONFIRMED-CODE]
- On **successful task completion**: `captureTaskCompleteUpdate` → `captureRepoWikiSnapshot` → `captureBeforePrompt` with `captureStage: "terminal"`, `content: "repo-wiki-update"` (server.cjs ~308831-308842; excerpt 13). The task-completion hook fires only for terminal transitions where the task did not fail and capture is enabled (`!failed && captureRepoSnapshot`, excerpt 26); failed tasks do not capture. [CONFIRMED-CODE]
- **Suppression condition**: `captureBeforePrompt` returns immediately when `workspaceIdentity` (the remote-session workspace identifier) is non-empty (excerpt 24); the same check exists in the desktop bundle (excerpt 32). [CONFIRMED-CODE]
- Other preconditions observed in code: OAuth token present, credential obtainable from the server, disk-quota check (default per-snapshot max 2 GB, excerpt 31). [CONFIRMED-CODE]

## Workspace Enumeration

Enumeration starts from `git ls-files --cached --others --exclude-standard`, so untracked-but-unignored files are included; directory traversal then excludes `.git` via `skipDirectoryNames = {".git"}`, after which `appendRootGitMetadataPaths` + `walkGitMetadataFiles` explicitly re-add the entire `.git` tree (excerpt 11). [CONFIRMED-CODE]

## Git Metadata Handling

`walkGitMetadataFiles` recursively collects everything under `.git/`. The manifests of three real workspaces show `.git/**` entries at 61.8%–89.5% of all archive entries, including `.git/objects/**` (3927/427/161 entries), `.git/logs/HEAD` (reflog, up to 145,943 B), `.git/config`, `.git/index`, `.git/lost-found/**`, and `.git/worktrees/<name>/**` (excerpt 11; statistics in evidence/manifest-statistics.md; sanitized manifests included). [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

## Git Filter Behavior

In `shouldIncludeRepoSnapshotPathBeforeSample`, the check

```js
if (isRootGitMetadataFile(params.repoRelativePath) || hasGitInternalSegment(segments)) {
  return { include: true };
}
```

precedes the secret-path check (`looksLikeSecretPath`, ~310515) and the size check (`sizeBytes > REPO_SNAPSHOT_MAX_FILE_BYTES`, ~310518), so **those filters are ineffective for `.git/**`** (excerpt 10). One earlier filter does still apply: the symbolic-link exclusion (~310500) precedes the `.git` short-circuit, so symlinked entries are excluded even inside `.git` (no symlink entries occur in the observed manifests). Real manifests contain a 4,540,393-byte `.pack` and ~1.09 MB loose objects, proving the 1 MB limit does not apply to `.git`. [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

## Secret Filtering

The exclusion set (`secretBasenames = {.env, .env.local, .env.development, .env.production, .npmrc, id_rsa, id_dsa, id_ecdsa, id_ed25519}`, paths containing `token`/`secret`, symlinks, binaries) operates only outside `.git` (excerpt 10). Consequence: secrets that live inside git objects — e.g. credentials embedded in `.git/config` remote URLs, or secrets present in historical commits — are inside the upload scope. This audit does not claim any particular secret was uploaded; it establishes that the filter layer provides no protection inside `.git`. [CONFIRMED-CODE]

## Prompt Packaging

`meta/prompt.json` is built directly from `params.prompt` with `content: params.prompt.content` — the full user prompt text (excerpt 07/08). The same content is passed as the capture `content` field. [CONFIRMED-CODE]. Prompt texts themselves are not published in this repository.

## Global Configuration Packaging

`GLOBAL_CONFIG_PATHS` (excerpt 15) collects `settings.behavior.json`, `mcp.json`, `skills.json`, `commands.json`, `hooks.json`, `plugins.json`, `memory.json`, `subagents.json`, `instructions.json` from the user's global ZCode config, sanitizes values via `sanitizeUnknown`, and packs them as `extra-files/global-configs/<name>` (server.cjs 310341-310432; extra-manifest artifacts confirm real collection). [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

Redaction is **key-name based**: `SENSITIVE_KEY_PATTERN = /(?:api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential|authorization|cookie|session[_-]?token|token)$/i` replaces the *value* only when the key name ends with one of those forms. A synthetic escape test (evidence/sanitized-logs, script `scripts/scan-sensitive-paths.py --selftest`) shows key names such as `LLM_KEY`, `MY_AUTH`, `PROVIDER_CRED`, `MODEL_ACCESS`, or values embedding secrets under non-matching keys are not redacted. `CUSTOM_PROVIDER_CREDENTIAL` *is* caught (ends with `credential`). [CONFIRMED-CODE] + [CONFIRMED-RUNTIME] (synthetic)

Additionally, `REPO_SNAPSHOT_SETTINGS_BEHAVIOR_KEYS` (excerpt 27) uploads the values of behavior settings — including `repoSnapshotIndexingEnabled` and `repoSnapshotIndexingUserConfigured` themselves. [CONFIRMED-CODE]

## Repo Wiki Integration

Two distinct channels exist:

1. **Generation channel (local + LLM API):** `runGenerate` reads the workspace via `LocalWorkspaceRepoReader`, calls the configured model provider, and writes generated wiki text to local storage. This is the ordinary inference data flow (workspace content as model context).
2. **Snapshot channel:** wiki generation start (`void captureRepoWikiSnapshot`, ~308556) and successful task completion (`captureTaskCompleteUpdate` → `captureStage: "terminal"`, `content: "repo-wiki-update"`, ~308831-308842; gated on `!failed && captureRepoSnapshot`, excerpt 26) invoke the same `captureBeforePrompt` path as prompts, i.e. a full workspace snapshot upload including `.git/**`.

So no — Repo Wiki does not merely upload generated wiki text; its lifecycle is wired to the full snapshot pipeline. [CONFIRMED-CODE]

## Local Checkpoint vs Repo Snapshot

| | Local "checkpoint" (user-visible rollback) | Repo snapshot (this audit's subject) |
|---|---|---|
| Storage | git refs `refs/zcode/checkpoints/<workspaceHash>/<id>` in the workspace repo | encrypted `tar.gz` uploaded to OSS; local state/manifests only |
| Content | workspace files | file contents + all of `.git/**` + full prompt + global configs |
| Network | none observed | before every prompt + on successful task completion (capture-enabled transitions) |
| Restore | `git restore` (excerpt 30) | **no download/restore endpoint found** (`restore|download` grep: 0 hits in both bundles) |
| Identity | `GIT_AUTHOR_EMAIL: "checkpoint@zcode.local"` (excerpt 29) | attribution metadata in callback |

[CONFIRMED-CODE]; subagent audit report of the checkpoint subsystem, with all load-bearing citations re-extracted first-hand (excerpts 28–30).

## Encryption

- Archive: gzip, then AES-256-CTR with a cryptographically random 32-byte data key and a 16-byte nonce written as a ciphertext prefix (excerpt 09, server.cjs ~310048-310077).
- Key wrapping: `publicEncrypt({ key: credential.encryption.public_key, padding: RSA_PKCS1_OAEP_PADDING, oaepHash: "sha256" }, dataKey)`; the credential schema enforces `algorithm === "RSA-OAEP-256"` (~312454).
- The envelope declares `contentAlgorithm: "aes-256-ctr"`, `keyWrapAlgorithm: "rsa-oaep-sha256"`.
- The wrapped key (`encrypted_aes_key`) is delivered **back to the server** in the OSS callback form (~312533-312545).

Design consequence: the server possesses the corresponding capability to decrypt snapshots (it issues the wrapping key and receives the wrapped data key). This audit does **not** claim the server actually decrypted any snapshot. Data-at-rest confidentiality against the server is not provided by this design; confidentiality against third parties intercepting OSS traffic is provided. Details: [evidence/cryptography-flow.md](evidence/cryptography-flow.md). [CONFIRMED-CODE]

## Upload Credential Flow

`getUploadCredential` issues `GET {origin}/api/v1/snapshot/upload-credential?workspace_id=<id>` with `Authorization: Bearer <token>` (excerpt 22). Default origin `https://zcode.z.ai` (test: `https://zcode.chatglm.site`; overridable via environment variables, excerpt 01). The enforced response schema (excerpt 03) requires `oss.host/path/policy/x_oss_signature/x_oss_signature_version/x_oss_credential/x_oss_date/x_oss_security_token`, `encryption.public_key/key_version/algorithm`, `snapshot.snapshot_id`; optional `max_size`, `callback`. No real credentials are published. [CONFIRMED-CODE]

## OSS Upload

`uploadPostObject` POSTs a multipart form to `credential.oss.host` with file field name `repo-snapshot.tar.gz.enc` and OSS PostObject fields (`policy`, `x-oss-signature`, `x-oss-security-token`, …) plus `attribution` and `callback` (~312520-312626). The OSS callback relays `update_type` (full/incremental), `checksum = "sha256:" + sha256(plaintext snapshot)`, `encrypted_aes_key`, `x:base_snapshot_id`, and attribution (`sessionId`/`queryId`/`requestId`/`failureCount`/`captureStage`). A PUT channel (`uploadPutObject`) also exists. The actual OSS host is runtime-delivered and was not locally observable. [CONFIRMED-CODE]

## Upload-Completion State (client marker)

All 7 workspace state files on the audited machine contain the client-recorded upload-success marker `lastAcceptedManifestHash` (the field name is the product's own; values withheld as identifiers, presence published in sanitized copies) — direct local evidence that the client-side upload pipeline ran to completion: the code writes this field only after the object upload path reports success (server.cjs ~312703-312730 success branch → ~312875-312898 `markAcceptedManifest` → ~311196-311208 state write). It does not independently document the server's callback-side processing, which remains unobserved. `failureCount` values of 1–3 show the retry mechanism ran. `lastCompressedSize` pairs (e.g. `encryptedSizeBytes: 7,587` vs `workspaceSizeBytes: 15,102,726`) are consistent with the incremental (delta) mechanism. `pending/` and `tmp/` residues are absent, matching the code's post-success cleanup (excerpt 12). [CONFIRMED-LOCAL-ARTIFACT]

## Local vs Remote Behavior

`buildRepoSnapshotWorkspaceKey` uses `workspaceIdentity` if present, else `workspacePath` (excerpt 25). All observed captures on this machine used the raw filesystem path as the key (state `workspaceKey` equals the workspace path), i.e. they ran with an empty `workspaceIdentity` — the local-session configuration. [CONFIRMED-LOCAL-ARTIFACT] + [CONFIRMED-CODE]

## Remote WSL Behavior

- The desktop bundle models workspaces as `kind: "project"` or `kind: "remote"` with connection targets of kind `ssh` / `wsl` / `docker`; several remote RPC schemas require `workspaceIdentity` whenever a `remoteSessionId` is present (excerpt 32). [CONFIRMED-CODE]
- `captureBeforePrompt` skips capture when `workspaceIdentity` is set (excerpt 24; desktop equivalent in excerpt 32). [CONFIRMED-CODE]
- On the audited machine, WSL workspaces were in fact captured and uploaded (7/7 states carry the client-recorded upload-success marker, path-derived keys). No Remote-WSL exemption from client-side repo snapshot capture/upload was identified **in practice** on this machine; WSL here runs its own server bundle and its workspaces behave as local projects. Whether SSH-style remote sessions are exempt in the current build could not be observed (no SSH workspace artifacts on this machine) — see [docs/known-unknowns.md](docs/known-unknowns.md). [CONFIRMED-LOCAL-ARTIFACT] + [INFERRED] for the SSH case.

## Telemetry Surface

Independent of the snapshot system: (1) the desktop bundle embeds the Aliyun ARMS RUM SDK reporting to `https://sdk.rum.aliyuncs.com` (events locally gzipped before send); (2) an Aliyun SLS log endpoint (`proj-xtrace-…cn-beijing.log.aliyuncs.com`) is embedded; (3) a `deviceMid` UUID is persisted in `~/.zcode/v2/telemetry-state.json` and sent as an `X-Device-Mid` request header (excerpt 16/17). The specific RUM event payloads are UNKNOWN (SDK-internal, not locally reconstructed). No claim is made that RUM uploads source code. [CONFIRMED-CODE] (endpoints/headers) + [UNKNOWN] (payload details)

## Local SQLite / Session Storage

`~/.zcode/cli/db/db.sqlite` (~700 MB) stores local session data: 24,496 `message` rows, 105,875 `part` rows, 30,334 `tool_usage`, 21,728 `model_usage`, 561 sessions (counts captured together with the published schema at 2026-09-19 14:11; the live database grows continuously, see [evidence/sqlite-schema.txt](evidence/sqlite-schema.txt)). Schema in [evidence/sqlite-schema.txt](evidence/sqlite-schema.txt). This is local storage; no upload of this database was identified. [CONFIRMED-LOCAL-ARTIFACT]

## Client-side Indexing / Embedding

`embedding` has zero hits in the audited **server bundle**; no sqlite-vec/qdrant/lance/hnsw/faiss identifiers exist there. The desktop bundle (`app.asar`) does contain the string `embedding` (~740 occurrences) inside packaged third-party code — primarily AI-SDK model-class libraries (e.g. `@ai-sdk/*/embedding-model`), plus unrelated third-party assets (telemetry semantic conventions, terminal/shiki assets and similar). Statement: **no standalone client-side embedding/indexing subsystem was identified in the audited server bundle, and no application-level embedding pipeline was identified in either artifact.** This does not establish anything about server-side indexing. [CONFIRMED-CODE] (absence, scoped)

## Data Potentially Leaving Machine

Status vocabulary: CONFIRMED / PARTIALLY CONFIRMED / INFERRED / UNKNOWN / NOT OBSERVED.

| Data | Status | Evidence | Notes |
|---|---|---|---|
| source code | CONFIRMED | archive builder packs `files/<path>` full content (excerpt 08); manifests list source files | as part of workspace snapshots |
| Git history | CONFIRMED | manifests contain `.git/objects/**`, `.git/logs/HEAD` (61.8–89.5% of entries) | F-008 |
| Git objects | CONFIRMED | same | F-008 |
| Git pack files | CONFIRMED | 2.5–4.5 MB packs in manifests (>1 MB limit bypassed) | F-009 |
| reflog | CONFIRMED | `.git/logs/HEAD` 145,943 B in project-a manifest | — |
| commit metadata | CONFIRMED | `.git/logs/**`, `.git/config`, refs, worktree metadata in manifests | author emails reside inside git objects/logs; content not published here |
| file paths | CONFIRMED | `meta/manifest.json` = {path,sizeBytes} of every included file | — |
| prompt text | CONFIRMED | `meta/prompt.json` ← `params.prompt.content` (excerpt 07) | — |
| agent config | CONFIRMED | extra-files global-config group (excerpt 15; extra-manifest artifacts) | — |
| MCP config | CONFIRMED | `mcp.json` in GLOBAL_CONFIG_PATHS | — |
| hooks config | CONFIRMED | `hooks.json` in GLOBAL_CONFIG_PATHS | — |
| memory config | CONFIRMED | `memory.json` in GLOBAL_CONFIG_PATHS | — |
| instructions | CONFIRMED | `instructions.json` in GLOBAL_CONFIG_PATHS | — |
| API keys | PARTIALLY CONFIRMED | collector uploads mcp/hooks configs; redaction is key-name-only (excerpt 15 + synthetic escape test) | matching key names are redacted; non-matching secret-bearing keys/values may not be. It is **not** established that any concrete API key was uploaded |
| OAuth credential | NOT OBSERVED | `credentials.json` (OAuth) is not in the collector's source list; no upload evidence found | — |
| device identifier | CONFIRMED | `deviceMid` sent as `X-Device-Mid` header (excerpt 16); persisted locally (excerpt 17) | separate from snapshots |
| telemetry | PARTIALLY CONFIRMED | RUM/SLS endpoints embedded (asar grep); event payloads UNKNOWN | endpoints confirmed; payload contents unknown |
| OSS snapshot (the archive itself) | CONFIRMED | upload code (excerpts 04/22) + client-recorded upload-success state (F-020) | encrypted archive; server can decrypt by design |
| local DB contents | NOT OBSERVED (upload) | db.sqlite holds local sessions; no upload path identified | local storage confirmed |

## Confirmed Facts

1. Every prompt, and every successful capture-enabled task completion, (logged in, credential available, quota OK, non-remote workspace) produces a full workspace snapshot archive including all of `.git/**`, the prompt text, and global configs. [CONFIRMED-CODE + CONFIRMED-LOCAL-ARTIFACT]
2. The `.git` short-circuit bypasses secret-path, binary, and 1 MB size filtering; >1 MB pack files appear in real manifests. [CONFIRMED-CODE + CONFIRMED-LOCAL-ARTIFACT]
3. Envelope encryption wraps the random data key with a server-delivered RSA public key and returns it to the server via the OSS callback; the server possesses the decryption capability by design. [CONFIRMED-CODE]
4. `repoSnapshotIndexingEnabled` does not gate capture or upload in the audited server bundle; the sidecar is constructed unconditionally; the setting's value is itself uploaded. [CONFIRMED-CODE]
5. All 7 observed workspaces have `lastAcceptedManifestHash` — the client's own marker, written only after its upload path reports success (server-side processing beyond the callback delivery is unobserved). Pending artifacts are cleaned after success. [CONFIRMED-LOCAL-ARTIFACT]
6. The snapshot subsystem emits no capture/upload/credential log lines; upload errors are silently discarded (`void scheduled.catch(() => {})`, excerpt 26). The word `repoSnapshot` appears in logs only inside full-settings JSON dumps. [CONFIRMED-CODE + CONFIRMED-LOCAL-ARTIFACT]
7. There is no snapshot download/restore endpoint; the visible checkpoint rollback is a separate local git-refs mechanism. [CONFIRMED-CODE]
8. Telemetry surfaces (ARMS RUM, SLS endpoint, X-Device-Mid) exist independently of snapshots. [CONFIRMED-CODE]
9. No client embedding subsystem identified; local SQLite stores sessions/messages locally. [CONFIRMED-CODE (absence) + CONFIRMED-LOCAL-ARTIFACT]
10. A capture recorded by the desktop-side runtime at 2026-09-17 20:57 post-dates the audited desktop build (mtime 2026-09-04), anchoring the observed behavior to the audited artifacts (see TIMELINE.md). [CONFIRMED-LOCAL-ARTIFACT]

## Inferred Behavior

- Incremental snapshots upload only changed files relative to `base_snapshot_id` (`meta/delta.json` + strong size ratios). [INFERRED]
- The actual semantic of `repoSnapshotIndexingEnabled` is a server-side indexing preference (consistent with third-party analysis); locally it does not stop packaging/upload. [INFERRED]
- SSH-remote sessions (which must carry `workspaceIdentity`) are skipped at the prompt-stage capture. [INFERRED from code; not observed locally]

## Unknowns

See [docs/known-unknowns.md](docs/known-unknowns.md) for the full list: OSS bucket host; server-side storage/indexing/ACLs/retention; whether any specific secret ever left the machine; RUM payload contents; first-introduced version; SSH-remote capture behavior in practice; desktop-side consumption points of the indexing setting beyond the code paths listed.

## Mitigations

[docs/mitigation.md](docs/mitigation.md): making the checkpoints directory non-writable (`chattr +i ~/.zcode/v2/checkpoints`) is a **proposed** mitigation (could not be applied during this audit — root privileges unavailable); the document includes a canary verification protocol and `scripts/verify-snapshot-disabled.sh`. Setting `repoSnapshotIndexingEnabled=false` is **not** a mitigation for capture/upload in the audited build (F-022). Using remote/SSH workspace mode *may* suppress prompt-stage capture (F-031) but this is unverified — do not rely on it.

## Reproduction

[docs/reproduction.md](docs/reproduction.md) and `scripts/`. All scripts are read-only against the ZCode installation, contain no hard-coded identities, and work on any machine with the same layout (paths configurable via environment variables).

## Independent Corroboration

[evidence/independent-corroboration.md](evidence/independent-corroboration.md) maps third-party findings (ferstar blog analysis of the same behavior; public issue reports) to local reproduction statuses (REPRODUCED / PARTIALLY_REPRODUCED / NOT_REPRODUCED / NOT_TESTED). Third-party material is used only as corroboration, never as a substitute for local evidence.

## Disclosure Notes

- Every private identifier (usernames, hostnames, project names, workspace/manifest/snapshot ids, device ids, branch/remote/worktree names, git object ids) is redacted in published derivatives; raw artifacts were never uploaded and remain on the audited machine.
- No proprietary bundle (app.asar / zcode-server.cjs) is published in full; only minimum-necessary line-range excerpts with provenance.
- No real prompt text, no git objects, no database contents are published.
- Publication followed two secret-scan rounds (working tree + staged content) plus a fresh-clone re-audit; scripts used: `scripts/secret-scan.sh`, `scripts/scan-sensitive-paths.py`.
