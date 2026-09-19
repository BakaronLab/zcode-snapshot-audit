# Evidence Ledger

Every claim → evidence → artifact → source location → sanitized excerpt → reproduction step.
Code excerpts referenced as `excerpt N` live in [evidence/sanitized-code-references.md](evidence/sanitized-code-references.md).
`server.cjs` = the audited WSL server bundle `~/.zcode/server/zcode-server.cjs` (SHA-256 in [evidence/artifact-hashes.md](evidence/artifact-hashes.md)); `app.asar` = the desktop bundle. Line numbers refer to the audited build and are reproducible with `scripts/locate-snapshot-code.sh`.

Template per finding: Claim / Evidence class / Source artifact / Code location / Local artifact / Sanitized excerpt / Observed data / Reproduction / Corroboration / Limitations / Confidence.

---

## F-001 — RepoSnapshotSidecarService unconditional instantiation

**Claim:** The repo snapshot sidecar is constructed once at server startup with no conditional guarding its instantiation.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** construction site ~line 322291 (`const repoSnapshotSidecar = new RepoSnapshotSidecarService({...})`), construction param block 322270-322335

**Sanitized excerpt (excerpt 06):**

```js
const repoSnapshotSidecar = new RepoSnapshotSidecarService({
  stateRepo: repoSnapshotStateRepo,
  uploadClient: repoSnapshotUploadClient,
  ...
  // global-configs：sidecar 在 capture 时统一收集 user scope 全局配置，
  // agent 问答与 repo wiki 两条调用链都自动携带 extra，无需各自传参。
  globalConfigsProvider: (params) => collectRepoSnapshotGlobalConfigs({...})
```

(The in-code comment states that both the agent Q&A and the repo-wiki call chains automatically carry the global-config extras.)

**Observed data:** no `if` precedes the constructor; the construction is in the top-level service-wiring block.
**Reproduction:** `bash scripts/locate-snapshot-code.sh` (section "sidecar construction") or `sed -n '322285,322295p' ~/.zcode/server/zcode-server.cjs`
**Corroboration:** third-party analysis reaches the same conclusion (evidence/independent-corroboration.md).
**Limitations:** proves client-side construction only; says nothing about server-side use.
**Confidence:** CONFIRMED

---

## F-002 — captureBeforePrompt trigger on every prompt

**Claim:** Before every prompt is sent to the agent, the sidecar's `captureBeforePrompt` is invoked with the full prompt.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** `scheduleRepoSnapshotSidecar` ~234473 (excerpt 23); capture call 233379-233399 (excerpt 07)

**Sanitized excerpt (excerpt 07):**

```js
await repoSnapshotSidecar.captureBeforePrompt({
  workspacePath: params.prompt.workspacePath,
  workspaceIdentity: params.prompt.workspaceIdentity,
  ...
  captureStage: "prompt",
  ...
  content: params.prompt.content,
  ...
});
```

**Local artifact:** capture timestamps in sanitized state files cluster at periods of interactive use (TIMELINE.md).
**Reproduction:** `sed -n '233370,233400p' ~/.zcode/server/zcode-server.cjs | cut -c1-240`
**Corroboration:** third-party: "every message triggers upload" — REPRODUCED (code-level).
**Limitations:** trigger conditions also include token/credential/quota/`workspaceIdentity` (F-031); no network capture to prove the request on the wire.
**Confidence:** CONFIRMED

---

## F-003 — prompt content packaging

**Claim:** The full user prompt text is embedded in the snapshot archive as `meta/prompt.json`, sourced from `params.prompt.content`.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** archive builder `writeRepoSnapshotPlainArchive` ~310121 (excerpt 08); content binding 233388-233397 (excerpt 07)

**Sanitized excerpt (excerpt 08):**

```js
const entries = [
  createBufferTarEntry(`${rootDir}/meta/prompt.json`, params.prompt),
  createBufferTarEntry(`${rootDir}/meta/manifest.json`, params.manifest)
];
...
entries.push({ path: `${rootDir}/files/${file6.path}`, absolutePath: file6.absolutePath, ... });
```

**Reproduction:** `sed -n '310115,310165p' ~/.zcode/server/zcode-server.cjs | cut -c1-240`
**Limitations:** proves packaging, not the wire content (no network capture).
**Confidence:** CONFIRMED

---

## F-004 — repo-wiki-update capture on successful task completion

**Claim:** Successful terminal task transitions (when capture is enabled) trigger a snapshot capture with `captureStage: "terminal"` and `content: "repo-wiki-update"`; failed tasks do not capture.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** `captureTaskCompleteUpdate` 308831-308842 (excerpt 13); task-complete hook 319000-319018 (excerpt 26)

**Sanitized excerpt (excerpt 13):** `captureRepoWikiSnapshot({... captureStage: "terminal", content: "repo-wiki-update" ...})` region; (excerpt 26):

```js
if (!failed && captureRepoSnapshot) {
  const captureIntent = async (signal) => { ... await options.captureRepoSnapshotAfterTaskComplete?.(captureTarget, signal); ... };
  const scheduled = ... .schedule(target, captureIntent) : captureIntent();
  void scheduled.catch(() => {
  });                                    // ← upload errors silently discarded
}
```

**Reproduction:** `grep -n 'repo-wiki-update' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-005 — git ls-files enumeration

**Claim:** Workspace file enumeration runs `git ls-files --cached --others --exclude-standard` (tracked + untracked-unignored files).

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** ~310540, ~310596 (excerpt 11)

**Reproduction:** `grep -n 'ls-files' ~/.zcode/server/zcode-server.cjs`
**Limitations:** applies to git workspaces; behavior for non-git directories was not exercised at runtime.
**Confidence:** CONFIRMED

---

## F-006 — walkGitMetadataFiles

**Claim:** A dedicated walker recursively collects the entire `.git` directory after normal traversal excluded it.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** `appendRootGitMetadataPaths` + `walkGitMetadataFiles` ~310624 (excerpt 11); `skipDirectoryNames = {".git"}` in the ordinary walker

**Reproduction:** `grep -n 'walkGitMetadataFiles\|skipDirectoryNames' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-007 — .git metadata reinclusion

**Claim:** `.git` is first excluded from ordinary traversal and then explicitly re-added by independent logic.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** excerpts 10-11 (scanner module `repoSnapshotScanner.ts`)

**Reproduction:** excerpts 10/11 in evidence/sanitized-code-references.md
**Confidence:** CONFIRMED

---

## F-008 — .git objects inclusion in real manifests

**Claim:** `.git/objects/**`, `.git/logs/HEAD`, `.git/config`, `.git/index`, `lost-found`, and worktree metadata appear as manifest entries of real captures.

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT]

**Local artifact:** [evidence/sanitized-manifests/](evidence/sanitized-manifests) (3 manifests); statistics in [evidence/manifest-statistics.md](evidence/manifest-statistics.md)

**Observed data:** project-a: 4190/5067 entries are `.git/**` (82.7%), 3927 object entries, reflog 145,943 B, `lost-found` present; project-b: 89.5%; project-c: 61.8%.
**Reproduction:** `python3 scripts/summarize-manifest.py <your-manifest>.json`; `python3 scripts/inspect-git-inclusion.py <manifest>`
**Confidence:** CONFIRMED

---

## F-009 — >1 MB git packs bypass size filtering

**Claim:** The stated 1 MB per-file limit (`REPO_SNAPSHOT_MAX_FILE_BYTES`) does not apply to `.git/**`; real manifests contain larger entries.

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` ~310488 region: the `.git` short-circuit precedes the size check (excerpt 10).
**Local artifact:** project-a manifest contains `.git/objects/pack/pack-<REDACTED>.pack` at 4,540,393 B; project-c contains a 2,523,192 B pack and two ~1.09 MB loose objects.

**Reproduction:** `python3 scripts/inspect-git-inclusion.py <manifest> --min-size 1000000`
**Corroboration:** third-party reports large packs in uploads — REPRODUCED.
**Confidence:** CONFIRMED

---

## F-010 — .git bypass of secret/path filtering

**Claim:** Secret-path filtering (`looksLikeSecretPath`) and the 1 MB size check are ineffective for `.git/**` because the `.git` short-circuit returns first. (The symbolic-link exclusion is checked before the short-circuit and does still apply; binary sampling applies to content reads later in the pipeline.)

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` `shouldIncludeRepoSnapshotPathBeforeSample` ~310488 (excerpt 10); `secretBasenames` set at ~310440.

**Sanitized excerpt (excerpt 10, abridged):**

```js
function shouldIncludeRepoSnapshotPathBeforeSample(params) {
  ...
  if (isRootGitMetadataFile(params.repoRelativePath) || hasGitInternalSegment(segments)) {
    return { include: true };
  }                                  // ← precedes looksLikeSecretPath & sizeBytes > 1MB checks
```

**Reproduction:** excerpt 10; `grep -n 'shouldIncludeRepoSnapshotPathBeforeSample\|looksLikeSecretPath' ~/.zcode/server/zcode-server.cjs`
**Limitations:** establishes that the filter layer offers no protection inside `.git`; does not claim any specific secret was uploaded.
**Confidence:** CONFIRMED

---

## F-011 — manifest ↔ archive content relationship

**Claim:** `meta/manifest.json` is embedded in the encrypted archive; each manifest entry's content is packed under `files/<path>`.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` 310115-310165 (excerpt 08); local manifests are the same structure ZCode writes locally.

**Local artifact:** [evidence/sanitized-manifests/](evidence/sanitized-manifests)
**Reproduction:** excerpt 08
**Confidence:** CONFIRMED

---

## F-012 — global config collection

**Claim:** Nine global config groups (settings.behavior, mcp, skills, commands, hooks, plugins, memory, subagents, instructions) are collected and packed into the archive as `extra-files/`.

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` 310341-310432 (excerpt 15: `GLOBAL_CONFIG_SOURCES`, `GLOBAL_CONFIG_PATHS`, `buildRepoSnapshotGlobalConfigsExtraInputs`).

**Local artifact:** [evidence/sanitized-extra-manifest/](evidence/sanitized-extra-manifest) — real extra-manifests listing `settings.behavior.json`, `subagents.json`, etc. with byte sizes.

**Reproduction:** `python3 scripts/inspect-extra-manifest.py <extra-manifest>.json`
**Confidence:** CONFIRMED

---

## F-013 — global config redaction is key-name-only

**Claim:** `sanitizeUnknown` redacts a value only when its key name matches `SENSITIVE_KEY_PATTERN` (end-anchored); non-matching key names and values embedding secrets pass through.

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-RUNTIME] (synthetic test)

**Source artifact:** `server.cjs` 310362-310380 (excerpt 15).

**Sanitized excerpt (excerpt 15):**

```js
var SENSITIVE_KEY_PATTERN = /(?:api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential|authorization|cookie|session[_-]?token|token)$/i;
function sanitizeUnknown(value, options) {
  ...
  for (const [key, rawValue] of Object.entries(value)) {
    if (SENSITIVE_KEY_PATTERN.test(key)) { result[key] = "<redacted>"; continue; }
    ...
```

**Observed data (synthetic key names only — no real credentials):**

| synthetic key | result |
|---|---|
| LLM_KEY | ESCAPES |
| MY_AUTH | ESCAPES |
| PROVIDER_CRED | ESCAPES |
| MODEL_ACCESS | ESCAPES |
| CUSTOM_PROVIDER_CREDENTIAL | REDACTED (ends with `credential`) |
| API_KEY / apiKey / access_token / my_secret / TOKEN | REDACTED (controls) |

Full test output: `evidence/sanitized-logs/` companion of excerpt 15; rerun with `python3 scripts/scan-sensitive-paths.py --selftest`.
**Limitations:** proves the mechanism, not that any concrete secret was uploaded.
**Confidence:** CONFIRMED (mechanism)

---

## F-014 — upload-credential endpoint

**Claim:** The client fetches upload credentials from `GET {origin}/api/v1/snapshot/upload-credential?workspace_id=<id>` with a Bearer token; default origin `https://zcode.z.ai`.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` — origin constants ~202210-202211 (excerpt 01); URL constant ~289955-289957 (excerpt 02); request builder `getUploadCredential` ~312629-312636 (excerpt 22).

**Sanitized excerpt (excerpt 22):** `method: "GET"` + `authHeaders(token)` in the credential request.
**Reproduction:** `grep -n 'upload-credential\|DEFAULT_ZCODE_ENDPOINT_ORIGIN' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-015 — RSA public key delivery

**Claim:** The credential response carries the RSA public key (`encryption.public_key`, `key_version`, `algorithm`) used to wrap the snapshot data key; the algorithm is enforced to `RSA-OAEP-256`.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` credential response validation 312395-312480 (excerpt 03); `assertSupportedEncryption` ~312454.

**Reproduction:** excerpt 03
**Confidence:** CONFIRMED

---

## F-016 — AES-256-CTR content encryption

**Claim:** Archive content is encrypted with AES-256-CTR using a random 32-byte data key and a 16-byte nonce stored as a ciphertext prefix.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` `encryptArchive` ~310048-310077 (excerpt 09).

**Sanitized excerpt (excerpt 09):**

```js
const dataKey = randomBytes(32);
const nonce = randomBytes(16);
const cipher = createCipheriv("aes-256-ctr", dataKey, nonce);
```

**Confidence:** CONFIRMED

---

## F-017 — RSA-OAEP-SHA256 key wrapping

**Claim:** The data key is wrapped with the server-delivered public key: `publicEncrypt({ padding: RSA_PKCS1_OAEP_PADDING, oaepHash: "sha256" }, dataKey)`; the envelope declares `contentAlgorithm: "aes-256-ctr"`, `keyWrapAlgorithm: "rsa-oaep-sha256"`.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` 310069-310077, 310233-310238 (excerpt 09).

**Limitations:** This establishes that the server **has the capability** to decrypt (it issued the public key and receives the wrapped key). It does not establish that the server decrypted any snapshot.
**Confidence:** CONFIRMED

---

## F-018 — OSS multipart upload

**Claim:** The encrypted archive is POSTed as a multipart form to the runtime-delivered `credential.oss.host` with file field `repo-snapshot.tar.gz.enc` plus OSS PostObject form fields; a PUT channel also exists.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` `buildObjectUploadTarget` ~312520+, `uploadPostObject` ~312598-312626, `uploadPutObject` ~312587 (excerpts 04/05).

**Sanitized excerpt (excerpt 04, abridged):**

```js
formData.set("file", artifactBlob, "repo-snapshot.tar.gz.enc");
// plus: success_action_status, policy, x-oss-signature, x-oss-signature-version,
//       x-oss-credential, x-oss-date, key, x-oss-security-token, attribution, callback
```

**Limitations:** actual OSS host not locally observable (runtime-delivered; no network capture).
**Confidence:** CONFIRMED (code) / UNKNOWN (actual host)

---

## F-019 — callback returns encrypted_aes_key (+ plaintext checksum)

**Claim:** The OSS callback relays `update_type`, `checksum` (`sha256:` + plaintext snapshot hash), `encrypted_aes_key`, `x:base_snapshot_id`, and attribution metadata to the ZCode server.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` ~312527-312556 (excerpt 04).

**Sanitized excerpt (excerpt 04, abridged):**

```js
"x:encrypted_aes_key": request.encryptedArtifact.encryptedDataKey,
... "checksum": "sha256:" + <plaintext snapshot sha256> ...
```

**Limitations:** proves the client sends these fields; server-side handling unknown.
**Confidence:** CONFIRMED

---

## F-020 — client-recorded upload-success state (`lastAcceptedManifestHash`)

**Claim:** All locally observed workspace state files contain `lastAcceptedManifestHash` — the client's own record that its upload path ran to completion. In code, the field is written only after the object-upload call reports success (`response.ok` branch → `markAcceptedManifest` → state write, server.cjs ~312703-312730 / ~312875-312898 / ~311196-311208). This proves the client-side pipeline completed; the server's callback-side handling of the delivered data is not independently observable and remains UNKNOWN.

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT] + [CONFIRMED-CODE]

**Local artifact:** [evidence/sanitized-state/](evidence/sanitized-state) — 7/7 workspaces carry the client-recorded upload-success marker, plus `failureCount` 1-3 and `lastCompressedSize` pairs (e.g. 7,587 B encrypted vs 15,102,726 B workspace; 128,454 B vs 51,794,580 B).

**Reproduction:** `python3 scripts/inspect-checkpoints.py ~/.zcode/v2/checkpoints`
**Limitations:** proves the client-side upload pipeline completed and recorded success; the server's subsequent handling is UNKNOWN (no network capture, no server-side evidence).
**Confidence:** CONFIRMED (client-side completion)

---

## F-021 — pending artifact deletion after success

**Claim:** After successful upload the local pending/tmp encrypted artifacts are deleted; failures leave `.tar.gz.enc` files for retry.

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` `finally { ... delete plaintext ... }` ~310259-310266 (excerpt 12); pending cleanup module; `tmp/<id>.tar.gz` / `pending/<id>.tar.gz.enc` paths ~310330-310331; immediate flush ~312143.

**Local artifact:** census of both machines' checkpoints directories: only `state.json` + manifests/extra-manifests, **zero** `.enc`/tmp files.
**Reproduction:** `bash scripts/inspect-checkpoints.py --census`
**Corroboration:** third-party report of pending retention under failure conditions — PARTIALLY_REPRODUCED (code path confirmed; failed-upload retention not observed locally because no failed upload residue exists).
**Confidence:** CONFIRMED

---

## F-022 — repoSnapshotIndexingEnabled is not a capture/upload gate

**Claim:** In the audited server bundle, `repoSnapshotIndexingEnabled` appears only as (a) settings schema with default `false`, (b) optional declaration, (c) patch normalization, and (d) a member of the uploaded settings-behavior key list; no code path conditions capture or upload on it. The sidecar is constructed unconditionally (F-001).

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` — 4 occurrences: ~202798 (schema default), ~202871 (optional), ~218336 (normalization), ~312166 (uploaded key list, excerpt 27); grep file reproduced by `scripts/locate-snapshot-code.sh`.

**Sanitized excerpt (excerpt 27, abridged):**

```js
"memoryEnabled",
"optimizeAgentExperienceEnabled",
"repoSnapshotIndexingEnabled",
"repoSnapshotIndexingUserConfigured",
"instantGrepIndexingEnabled",
```

**Local artifact:** Windows-side setting was `false` while its state still shows the client-recorded upload-success marker (F-020); sanitized copies in evidence/sanitized-logs/settings-extract.txt.
**Corroboration:** third-party: "the switch doesn't stop uploads" — REPRODUCED.
**Limitations:** statement is scoped to the audited client build; no claim is made about server-side semantics of the setting.
**Confidence:** CONFIRMED

---

## F-023 — local git checkpoint is a separate system

**Claim:** The user-visible checkpoint/rollback uses local git refs `refs/zcode/checkpoints/<workspaceHash>/<id>` with `GIT_AUTHOR_EMAIL: "checkpoint@zcode.local"` and restores via `git restore`; it performs no network I/O and is distinct from the repo snapshot upload system.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` ~214501, ~214636, ~214963 (excerpts 28-30).

**Reproduction:** excerpts 28-30; `grep -n 'refs/zcode/checkpoints\|checkpoint@zcode.local' ~/.zcode/server/zcode-server.cjs`
**Corroboration:** third-party conflation of the two systems — NOT_REPRODUCED (they are distinct).
**Confidence:** CONFIRMED

---

## F-024 — Repo Wiki dual-channel behavior

**Claim:** Repo Wiki has (1) a generation channel reading the local workspace and calling the LLM API, writing wiki text locally, and (2) a snapshot channel wiring wiki lifecycle events into the OSS snapshot upload.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` — `runGenerate`/`LocalWorkspaceRepoReader` 308460-308560 (excerpt 14); `void captureRepoWikiSnapshot` ~308556; `captureTaskCompleteUpdate` 308831-308842 (excerpt 13); process manager excerpt 18; host RPC names excerpt 19.

**Reproduction:** `grep -n 'LocalWorkspaceRepoReader\|captureRepoWikiSnapshot' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-025 — ARMS RUM telemetry surface

**Claim:** The desktop bundle embeds the Aliyun ARMS RUM SDK reporting to `https://sdk.rum.aliyuncs.com` (events gzipped locally before send).

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `app.asar` (binary grep outputs; reproduced by `scripts/inspect-upload-endpoints.py --telemetry` and recorded in evidence/telemetry-map.md).

**Limitations:** endpoint confirmed; concrete RUM event payloads UNKNOWN.
**Confidence:** CONFIRMED (endpoint) / UNKNOWN (payload)

---

## F-026 — SLS log endpoint

**Claim:** The desktop bundle embeds an Aliyun SLS log endpoint of the form `proj-xtrace-<project-id>-cn-beijing.cn-beijing.log.aliyuncs.com`.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `app.asar` binary grep (evidence/telemetry-map.md).

**Limitations:** what is actually shipped to SLS at runtime is UNKNOWN.
**Confidence:** CONFIRMED (endpoint) / UNKNOWN (payload)

---

## F-027 — deviceMid / X-Device-Mid

**Claim:** A `deviceMid` UUID is generated, persisted in `~/.zcode/v2/telemetry-state.json`, and sent as an `X-Device-Mid` request header on API requests.

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` header injection ~208120 (excerpt 16); persistence logic 274895-275030 (excerpt 17).
**Local artifact:** sanitized copy [evidence/sanitized-logs/telemetry-state.json](evidence/sanitized-logs/telemetry-state.json) (real value withheld).

**Reproduction:** `grep -n 'deviceMid\|Device-Mid' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-028 — local SQLite session storage

**Claim:** `~/.zcode/cli/db/db.sqlite` stores local sessions/messages/tool records; no upload path for this database was identified.

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT]

**Local artifact:** [evidence/sqlite-schema.txt](evidence/sqlite-schema.txt); row counts (captured together with the published schema at 2026-09-19 14:11): message 24,496; part 105,875; tool_usage 30,334; model_usage 21,728; session 561.

**Reproduction:** `python3 scripts/inspect-checkpoints.py --sqlite`
**Confidence:** CONFIRMED

---

## F-029 — no client-side embedding/indexing subsystem

**Claim:** No standalone client-side embedding/indexing subsystem was identified in the audited server bundle. The desktop bundle contains the string `embedding` (~740 occurrences, ~566 matching regions) inside packaged third-party code — primarily AI-SDK model-class libraries (e.g. `@ai-sdk/*/embedding-model`), plus unrelated third-party assets (telemetry semantic conventions, terminal/shiki assets and similar). No application-level embedding/indexing pipeline was identified in either artifact.

**Evidence class:** [CONFIRMED-CODE] (absence, scoped)

**Source artifact:** `server.cjs` — `embedding` 0 hits; no sqlite-vec/qdrant/lancedb/chromadb/hnsw/faiss identifiers. `app.asar` — library-only embedding references (reproduced by `scripts/locate-snapshot-code.sh --embedding-check`).

**Limitations:** absence of an application-level pipeline in these artifacts does not establish anything about server-side indexing, and does not cover non-audited desktop builds.
**Confidence:** CONFIRMED (absence, scoped)

---

## F-030 — Remote WSL: no exemption observed in practice

**Claim:** No Remote-WSL exemption from client-side repo snapshot capture/upload was identified in practice on the audited machine: WSL workspaces were captured and uploaded with path-derived keys.

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT] + [CONFIRMED-CODE]

**Local artifact:** all 7 state files show `workspaceKey` equal to the raw filesystem path (identity empty at capture time); WSL-side server captured 6 WSL workspaces between 2026-09-08 and 2026-09-11 (TIMELINE.md).

**Code context:** `wsl` co-occurs with snapshot/sidecar/capture symbols **0 times** in `server.cjs`; there is no WSL-conditional in the snapshot subsystem.
**Reproduction:** `bash scripts/locate-snapshot-code.sh --wsl-gate-check`
**Limitations:** scoped to the audited machine and build. The desktop can model WSL targets as `kind:"remote"` (F-031); whether that path ever suppresses capture in practice was not observed. "No exemption was identified" ≠ "exemption cannot exist".
**Confidence:** CONFIRMED (for observed behavior) / UNKNOWN (for unobserved remote-session configurations)

---

## F-031 — workspaceIdentity capture-suppression gate (remote sessions)

**Claim:** `captureBeforePrompt` returns immediately when `workspaceIdentity` is non-empty; `workspaceIdentity` is the identifier carried by remote sessions (several remote RPC schemas require it whenever `remoteSessionId` is present); the workspace key prefers identity over path. The identical gate exists in the desktop bundle.

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` 311930-311940 (excerpt 24), 210420-210432 (excerpt 25); `app.asar` equivalents (excerpt 32).

**Sanitized excerpt (excerpt 24):**

```js
async captureBeforePrompt(params) {
  const trimmedIdentity = params.workspaceIdentity?.trim();
  if (trimmedIdentity) {
    return;
  }
  ...
```

**Sanitized excerpt (excerpt 32, desktop asar):**

```js
async captureBeforePrompt(t){t.workspaceIdentity?.trim()||await this.captureScheduler.schedule(...)
```

**Observed data:** all observed captures had empty identity (path-keyed) — the gate has not been observed to fire on this machine.
**Limitations:** prompt-stage gate only; the task-complete path passes `workspaceIdentity` through to the same gate (excerpt 13). Whether current desktop builds set identity for WSL/SSH targets in practice is UNKNOWN (no such artifacts locally).
**Confidence:** CONFIRMED (code) / UNKNOWN (practical remote behavior)

---

## F-032 — CLI runtime contains no snapshot uploader; audit isolation

**Claim:** The standalone CLI runtime (`/opt/ZCode/zcode` ELF invoked as `zcode`) contains no `upload-credential` / RepoSnapshot uploader strings and its logs contain no repoSnapshot capture activity; the audit sessions themselves produced no new checkpoint artifacts.

**Evidence class:** [CONFIRMED-RUNTIME] (absence)

**Observed data:** `strings` search of the CLI binary: 0 hits for `upload-credential`, 0 for RepoSnapshot symbols; CLI log for 2026-09-19: 0 hits; no checkpoints directory under the CLI data root; no files newer than the audit start in either machine's checkpoints directory; no checkpoint state exists for the audit workspace itself.

**Reproduction:** `strings /opt/ZCode/zcode | grep -c upload-credential` (0); `find ~/.zcode/v2/checkpoints -newermt <audit-start> -type f` (empty)
**Limitations:** absence of strings in a stripped ELF and absence of artifacts is evidence of absence on this build/machine, not a guarantee.
**Confidence:** CONFIRMED (observed absence)

---

## F-033 — logging behavior of the snapshot subsystem

**Claim:** The snapshot subsystem emits no capture/upload/credential log lines; upload errors are silently discarded. The word `repoSnapshot` appears in local logs only inside full-settings JSON dumps written by `settingService` on every settings write (which also write `deviceSid`/`workspacePath` values into plaintext local logs).

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` — `void scheduled.catch(() => {})` at ~233399 (excerpt 07 region) and excerpt 26; upload path emits no log statements.
**Local artifact:** [evidence/sanitized-logs/upload-logging-absence-proof.txt](evidence/sanitized-logs/upload-logging-absence-proof.txt) — per-file counts for both machines; 100% of `repoSnapshot` hits classified as settings dumps; 0 subsystem activity lines.

**Corroboration:** third-party "silent upload" characterization — PARTIALLY_REPRODUCED (no subsystem logging confirmed; earlier draft claims of literally zero `repoSnapshot` grep hits were refined: the hits are settings dumps).
**Confidence:** CONFIRMED

---

## F-034 — capture anchor to the audited build

**Claim:** A capture recorded by the desktop-side runtime at 2026-09-17 20:57 local time post-dates the audited desktop build (app.asar mtime 2026-09-04 16:08), anchoring the observed capture behavior to the audited artifacts.

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT]

**Local artifact:** Windows-side state file `ws-c` (sanitized copy): `lastCompressedSize.recordedAt` epoch = 2026-09-17 20:57 +0800; desktop build mtimes in [evidence/build-info.md](evidence/build-info.md).

**Limitations:** mtime-based build identification; a hypothetical unrecorded in-place swap of the desktop bundle cannot be fully excluded (no evidence of one exists).
**Confidence:** CONFIRMED (with the stated mtime caveat)
