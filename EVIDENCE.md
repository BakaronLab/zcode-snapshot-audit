# Evidence Ledger · 证据台账

Every claim → evidence → artifact → source location → sanitized excerpt → reproduction step. English is canonical; 中文为逐条对照译文（代码摘录、命令与行号为语言无关内容，两种语言共用）。

Code excerpts referenced as `excerpt N` live in [evidence/sanitized-code-references.md](evidence/sanitized-code-references.md). 以 `excerpt N` 引用的代码摘录位于 [evidence/sanitized-code-references.md](evidence/sanitized-code-references.md)。

`server.cjs` = the audited WSL server bundle `~/.zcode/server/zcode-server.cjs` (SHA-256 in [evidence/artifact-hashes.md](evidence/artifact-hashes.md)); `app.asar` = the desktop bundle. Line numbers refer to the audited build and are reproducible with `scripts/locate-snapshot-code.sh`.

`server.cjs` = 被审计的 WSL server bundle `~/.zcode/server/zcode-server.cjs`（SHA-256 见 [evidence/artifact-hashes.md](evidence/artifact-hashes.md)）；`app.asar` = 桌面 bundle。行号对应被审计构建，可用 `scripts/locate-snapshot-code.sh` 复现。

Template per finding: Claim / Evidence class / Source artifact / Code location / Local artifact / Sanitized excerpt / Observed data / Reproduction / Corroboration / Limitations / Confidence.

每条 finding 的模板：Claim（声明）/ Evidence class（证据等级）/ Source artifact（来源工件）/ Code location（代码位置）/ Local artifact（本地工件）/ Sanitized excerpt（脱敏摘录）/ Observed data（观察数据）/ Reproduction（复现）/ Corroboration（佐证）/ Limitations（限制）/ Confidence（置信度）。

---

## F-001 — RepoSnapshotSidecarService unconditional instantiation

**Claim:** The repo snapshot sidecar is constructed once at server startup with no conditional guarding its instantiation.

**声明：** repo 快照 sidecar 在服务器启动时构造一次，没有任何条件保护其实例化。

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

（代码内注释说明：agent 问答与 repo-wiki 两条调用链都自动携带全局配置 extra。）

**Observed data:** no `if` precedes the constructor; the construction is in the top-level service-wiring block.

**观察数据：** 构造器之前没有 `if`；该构造位于顶层服务装配块中。

**Reproduction:** `bash scripts/locate-snapshot-code.sh` (section "sidecar construction") or `sed -n '322285,322295p' ~/.zcode/server/zcode-server.cjs`
**Corroboration:** third-party analysis reaches the same conclusion (evidence/independent-corroboration.md).

**佐证：** 第三方分析得出相同结论（evidence/independent-corroboration.md）。

**Limitations:** proves client-side construction only; says nothing about server-side use.

**限制：** 仅证明客户端构造；不说明服务器端用途。

**Confidence:** CONFIRMED

---

## F-002 — captureBeforePrompt trigger on every prompt

**Claim:** Before every prompt is sent to the agent, the sidecar's `captureBeforePrompt` is invoked with the full prompt.

**声明：** 在每条提示词发送给 agent 之前，提示词路径都会以完整提示词调用 sidecar 的 `captureBeforePrompt`（这是对调用点的陈述——调用本身无条件发生；捕获是否继续进行取决于 F-031 的门槛）。

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

**本地工件：** 脱敏状态文件中的捕获时间戳聚集在交互使用时段（TIMELINE.md）。

**Reproduction:** `sed -n '233370,233400p' ~/.zcode/server/zcode-server.cjs | cut -c1-240`
**Corroboration:** third-party: "every message triggers upload" — REPRODUCED (code-level).

**佐证：** 第三方："every message triggers upload"——REPRODUCED（代码层面）。

**Limitations:** trigger conditions also include token/credential/quota/`workspaceIdentity` (F-031); no network capture to prove the request on the wire.

**限制：** 触发条件还包括 token/凭据/配额/`workspaceIdentity`（F-031）；无网络抓包来证明线上请求。

**Confidence:** CONFIRMED

---

## F-003 — prompt content packaging

**Claim:** The full user prompt text is embedded in the snapshot archive as `meta/prompt.json`, sourced from `params.prompt.content`.

**声明：** 捕获发生时，完整用户提示词文本作为 `meta/prompt.json` 嵌入快照归档，来源于 `params.prompt.content`。

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

**限制：** 证明打包行为，而非线上内容（无网络抓包）。

**Confidence:** CONFIRMED

---

## F-004 — repo-wiki-update capture on successful task completion

**Claim:** Successful terminal task transitions (when capture is enabled) trigger a snapshot capture with `captureStage: "terminal"` and `content: "repo-wiki-update"`; failed tasks do not capture.

**声明：** 成功的终态任务转换（在捕获启用时）触发一次 `captureStage: "terminal"`、`content: "repo-wiki-update"` 的快照捕获；失败的任务不捕获。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** `captureTaskCompleteUpdate` 308831-308842 (excerpt 13); task-complete hook 319000-319018 (excerpt 26)

**Sanitized excerpt (excerpt 13):** `captureRepoWikiSnapshot({... captureStage: "terminal", content: "repo-wiki-update" ...})` region; (excerpt 26):

**脱敏摘录（excerpt 13）：** `captureRepoWikiSnapshot({... captureStage: "terminal", content: "repo-wiki-update" ...})` 区域；（excerpt 26）：

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

**声明：** 工作区文件枚举运行 `git ls-files --cached --others --exclude-standard`（已跟踪 + 未被忽略的未跟踪文件）。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** ~310540, ~310596 (excerpt 11)

**Reproduction:** `grep -n 'ls-files' ~/.zcode/server/zcode-server.cjs`
**Limitations:** applies to git workspaces; behavior for non-git directories was not exercised at runtime.

**限制：** 适用于 git 工作区；非 git 目录的行为未在运行时检验。

**Confidence:** CONFIRMED

---

## F-006 — walkGitMetadataFiles

**Claim:** A dedicated walker recursively enumerates `.git` metadata after normal traversal excluded it; regular files under `.git` are added to snapshot scope (the symlink exclusion still applies — F-010).

**声明：** 在普通遍历排除 `.git` 之后，一个专用 walker 递归枚举 `.git` 元数据；`.git` 下的常规文件进入快照范围（symlink 排除仍然生效——见 F-010）。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** `appendRootGitMetadataPaths` + `walkGitMetadataFiles` ~310624 (excerpt 11); `skipDirectoryNames = {".git"}` in the ordinary walker

**Reproduction:** `grep -n 'walkGitMetadataFiles\|skipDirectoryNames' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-007 — .git metadata reinclusion

**Claim:** `.git` is first excluded from ordinary traversal and then explicitly re-added by independent logic.

**声明：** `.git` 先被普通遍历排除，随后被独立逻辑显式重新加入。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs`
**Code location:** excerpts 10-11 (scanner module `repoSnapshotScanner.ts`)

**Reproduction:** excerpts 10/11 in evidence/sanitized-code-references.md
**Confidence:** CONFIRMED

---

## F-008 — .git objects inclusion in real manifests

**Claim:** `.git/objects/**`, `.git/logs/HEAD`, `.git/config`, `.git/index`, `lost-found`, and worktree metadata appear as manifest entries of real captures.

**声明：** `.git/objects/**`、`.git/logs/HEAD`、`.git/config`、`.git/index`、`lost-found` 与 worktree 元数据作为真实捕获的 manifest 条目出现。

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT]

**Local artifact:** [evidence/sanitized-manifests/](evidence/sanitized-manifests) (3 manifests); statistics in [evidence/manifest-statistics.md](evidence/manifest-statistics.md)

**本地工件：** [evidence/sanitized-manifests/](evidence/sanitized-manifests)（3 个 manifest）；统计见 [evidence/manifest-statistics.md](evidence/manifest-statistics.md)。

**Observed data:** project-a: 4190/5067 entries are `.git/**` (82.7%), 3927 object entries, reflog 145,943 B, `lost-found` present; project-b: 89.5%; project-c: 61.8%.

**观察数据：** project-a：4190/5067 条目为 `.git/**`（82.7%），3927 个 object 条目，reflog 145,943 B，`lost-found` 存在；project-b：89.5%；project-c：61.8%。

**Reproduction:** `python3 scripts/summarize-manifest.py <your-manifest>.json`; `python3 scripts/inspect-git-inclusion.py <manifest>`
**Confidence:** CONFIRMED

---

## F-009 — >1 MB git packs bypass size filtering

**Claim:** The stated 1 MB per-file limit (`REPO_SNAPSHOT_MAX_FILE_BYTES`) does not apply to `.git/**`; real manifests contain larger entries.

**声明：** 声明的单文件 1 MB 限制（`REPO_SNAPSHOT_MAX_FILE_BYTES`）不适用于 `.git/**`；真实 manifest 中包含更大的条目。

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` ~310488 region: the `.git` short-circuit precedes the size check (excerpt 10).

**来源工件：** `server.cjs` ~310488 区域：`.git` 短路分支先于大小检查（excerpt 10）。

**Local artifact:** project-a manifest contains `.git/objects/pack/pack-<REDACTED>.pack` at 4,540,393 B; project-c contains a 2,523,192 B pack and two ~1.09 MB loose objects.

**本地工件：** project-a manifest 含 4,540,393 B 的 `.git/objects/pack/pack-<REDACTED>.pack`；project-c 含 2,523,192 B 的 pack 和两个 ~1.09 MB 的松散对象。

**Reproduction:** `python3 scripts/inspect-git-inclusion.py <manifest> --min-size 1000000`
**Corroboration:** third-party reports large packs in uploads — REPRODUCED.

**佐证：** 第三方报告上传中存在大 pack——REPRODUCED。

**Confidence:** CONFIRMED

---

## F-010 — .git bypass of secret/path filtering

**Claim:** Secret-path filtering (`looksLikeSecretPath`) and the 1 MB size check are ineffective for `.git/**` because the `.git` short-circuit returns first. (The symbolic-link exclusion is checked before the short-circuit and does still apply; binary sampling applies to content reads later in the pipeline.)

**声明：** secret 路径过滤（`looksLikeSecretPath`）与 1 MB 大小检查对 `.git/**` 无效，因为 `.git` 短路分支先行返回。（symlink 排除在短路之前检查、仍然生效；binary 采样作用于流水线后续阶段的内容读取。）

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

**限制：** 确立过滤层在 `.git` 内部不提供保护；不断言任何具体 secret 曾被上传。

**Confidence:** CONFIRMED

---

## F-011 — manifest ↔ archive content relationship

**Claim:** `meta/manifest.json` is embedded in the encrypted archive; each manifest entry's content is packed under `files/<path>`.

**声明：** `meta/manifest.json` 被嵌入加密归档；每条 manifest 条目的内容打包在 `files/<path>` 之下。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` 310115-310165 (excerpt 08); local manifests are the same structure ZCode writes locally.

**Local artifact:** [evidence/sanitized-manifests/](evidence/sanitized-manifests)

**本地工件：** [evidence/sanitized-manifests/](evidence/sanitized-manifests)

**Reproduction:** excerpt 08
**Confidence:** CONFIRMED

---

## F-012 — global config collection

**Claim:** Nine global config groups (settings.behavior, mcp, skills, commands, hooks, plugins, memory, subagents, instructions) are collected and packed into the archive as `extra-files/`.

**声明：** 九个全局配置组（settings.behavior、mcp、skills、commands、hooks、plugins、memory、subagents、instructions）被收集并以 `extra-files/` 打包进归档。

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` 310341-310432 (excerpt 15: `GLOBAL_CONFIG_SOURCES`, `GLOBAL_CONFIG_PATHS`, `buildRepoSnapshotGlobalConfigsExtraInputs`).

**Local artifact:** [evidence/sanitized-extra-manifest/](evidence/sanitized-extra-manifest) — real extra-manifests listing `settings.behavior.json`, `subagents.json`, etc. with byte sizes.

**本地工件：** [evidence/sanitized-extra-manifest/](evidence/sanitized-extra-manifest)——真实 extra-manifest 列出 `settings.behavior.json`、`subagents.json` 等及字节大小。

**Reproduction:** `python3 scripts/inspect-extra-manifest.py <extra-manifest>.json`
**Confidence:** CONFIRMED

---

## F-013 — global config redaction is key-name-only

**Claim:** `sanitizeUnknown` redacts a value only when its key name matches `SENSITIVE_KEY_PATTERN` (end-anchored); non-matching key names and values embedding secrets pass through.

**声明：** `sanitizeUnknown` 仅在键名匹配 `SENSITIVE_KEY_PATTERN`（尾部锚定）时才脱敏值；不匹配的键名以及内嵌秘密的值直接通过。

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

**观察数据（仅合成键名——无真实凭据）：**

| synthetic key | result |
|---|---|
| LLM_KEY | ESCAPES |
| MY_AUTH | ESCAPES |
| PROVIDER_CRED | ESCAPES |
| MODEL_ACCESS | ESCAPES |
| CUSTOM_PROVIDER_CREDENTIAL | REDACTED (ends with `credential`) |
| API_KEY / apiKey / access_token / my_secret / TOKEN | REDACTED (controls) |

Full test output: `evidence/sanitized-logs/` companion of excerpt 15; rerun with `python3 scripts/scan-sensitive-paths.py --selftest`.

完整测试输出：`evidence/sanitized-logs/` 中 excerpt 15 的配套文件；可用 `python3 scripts/scan-sensitive-paths.py --selftest` 重跑。

**Limitations:** proves the mechanism, not that any concrete secret was uploaded.

**限制：** 证明机制本身，而非任何具体 secret 曾被上传。

**Confidence:** CONFIRMED (mechanism)

---

## F-014 — upload-credential endpoint

**Claim:** The client fetches upload credentials from `GET {origin}/api/v1/snapshot/upload-credential?workspace_id=<id>` with a Bearer token; default origin `https://zcode.z.ai`.

**声明：** 客户端以 Bearer token 从 `GET {origin}/api/v1/snapshot/upload-credential?workspace_id=<id>` 获取上传凭据；默认 origin `https://zcode.z.ai`。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` — origin constants ~202210-202211 (excerpt 01); URL constant ~289955-289957 (excerpt 02); request builder `getUploadCredential` ~312629-312636 (excerpt 22).

**Sanitized excerpt (excerpt 22):** `method: "GET"` + `authHeaders(token)` in the credential request.

**脱敏摘录（excerpt 22）：** 凭据请求中的 `method: "GET"` + `authHeaders(token)`。

**Reproduction:** `grep -n 'upload-credential\|DEFAULT_ZCODE_ENDPOINT_ORIGIN' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-015 — RSA public key delivery

**Claim:** The credential response carries the RSA public key (`encryption.public_key`, `key_version`, `algorithm`) used to wrap the snapshot data key; the algorithm is enforced to `RSA-OAEP-256`.

**声明：** 凭据响应携带用于封装快照数据密钥的 RSA 公钥（`encryption.public_key`、`key_version`、`algorithm`）；算法被强制为 `RSA-OAEP-256`。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` credential response validation 312395-312480 (excerpt 03); `assertSupportedEncryption` ~312454.

**Reproduction:** excerpt 03
**Confidence:** CONFIRMED

---

## F-016 — AES-256-CTR content encryption

**Claim:** Archive content is encrypted with AES-256-CTR using a random 32-byte data key and a 16-byte nonce stored as a ciphertext prefix.

**声明：** 归档内容以 AES-256-CTR 加密，使用随机 32 字节数据密钥与作为密文前缀存储的 16 字节 nonce。

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

**声明：** 数据密钥用服务器下发的公钥封装：`publicEncrypt({ padding: RSA_PKCS1_OAEP_PADDING, oaepHash: "sha256" }, dataKey)`；信封声明 `contentAlgorithm: "aes-256-ctr"`、`keyWrapAlgorithm: "rsa-oaep-sha256"`。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` 310069-310077, 310233-310238 (excerpt 09).

**Limitations:** This establishes that the server **has the capability** to decrypt (it issued the public key and receives the wrapped key). It does not establish that the server decrypted any snapshot.

**限制：** 这确立服务器**具备**解密能力（它签发公钥并接收被封装的密钥）。它不确立服务器曾解密任何快照。

**Confidence:** CONFIRMED

---

## F-018 — OSS multipart upload

**Claim:** The encrypted archive is POSTed as a multipart form to the runtime-delivered `credential.oss.host` with file field `repo-snapshot.tar.gz.enc` plus OSS PostObject form fields; a PUT channel also exists.

**声明：** 加密归档以 multipart form POST 到运行时下发的 `credential.oss.host`，文件字段为 `repo-snapshot.tar.gz.enc`，附带 OSS PostObject 表单字段；还存在一条 PUT 通道。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` `buildObjectUploadTarget` ~312520+, `uploadPostObject` ~312598-312626, `uploadPutObject` ~312587 (excerpts 04/05).

**Sanitized excerpt (excerpt 04, abridged):**

```js
formData.set("file", artifactBlob, "repo-snapshot.tar.gz.enc");
// plus: success_action_status, policy, x-oss-signature, x-oss-signature-version,
//       x-oss-credential, x-oss-date, key, x-oss-security-token, attribution, callback
```

**Limitations:** actual OSS host not locally observable (runtime-delivered; no network capture).

**限制：** 实际 OSS host 无法本地观察（运行时下发；无网络抓包）。

**Confidence:** CONFIRMED (code) / UNKNOWN (actual host)

---

## F-019 — callback returns encrypted_aes_key (+ plaintext checksum)

**Claim:** The OSS callback relays `update_type`, `checksum` (`sha256:` + plaintext snapshot hash), `encrypted_aes_key`, `x:base_snapshot_id`, and attribution metadata to the ZCode server.

**声明：** OSS 回调向 ZCode 服务器转发 `update_type`、`checksum`（`sha256:` + 明文快照哈希）、`encrypted_aes_key`、`x:base_snapshot_id` 与归因元数据。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` ~312527-312556 (excerpt 04).

**Sanitized excerpt (excerpt 04, abridged):**

```js
"x:encrypted_aes_key": request.encryptedArtifact.encryptedDataKey,
... "checksum": "sha256:" + <plaintext snapshot sha256> ...
```

**Limitations:** proves the client sends these fields; server-side handling unknown.

**限制：** 证明客户端发送这些字段；服务器端处理未知。

**Confidence:** CONFIRMED

---

## F-020 — client-recorded upload-success state (`lastAcceptedManifestHash`)

**Claim:** All locally observed workspace state files contain `lastAcceptedManifestHash` — the client's own record that its upload path ran to completion. In code, the field is written only after the object-upload call reports success (`response.ok` branch → `markAcceptedManifest` → state write, server.cjs ~312703-312730 / ~312875-312898 / ~311196-311208). This proves the client-side pipeline completed; the server's callback-side handling of the delivered data is not independently observable and remains UNKNOWN.

**声明：** 本地观察到的全部工作区状态文件都含 `lastAcceptedManifestHash`——客户端自己对其上传路径运行完成的记录。在代码中，该字段仅在对象上传调用报告成功后写入（`response.ok` 分支 → `markAcceptedManifest` → 状态写入，server.cjs ~312703-312730 / ~312875-312898 / ~311196-311208）。这证明客户端侧流水线完成；服务器对所交付数据的回调侧处理无法独立观察，仍为 UNKNOWN。

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT] + [CONFIRMED-CODE]

**Local artifact:** [evidence/sanitized-state/](evidence/sanitized-state) — 7/7 workspaces carry the client-recorded upload-success marker, plus `failureCount` 1-3 and `lastCompressedSize` pairs (e.g. 7,587 B encrypted vs 15,102,726 B workspace; 128,454 B vs 51,794,580 B).

**本地工件：** [evidence/sanitized-state/](evidence/sanitized-state)——7/7 个工作区携带客户端记录的上传成功标记，另有 `failureCount` 1-3 与 `lastCompressedSize` 数对（如 7,587 B 加密 vs 15,102,726 B 工作区；128,454 B vs 51,794,580 B）。

**Reproduction:** `python3 scripts/inspect-checkpoints.py ~/.zcode/v2/checkpoints`
**Limitations:** proves the client-side upload pipeline completed and recorded success; the server's subsequent handling is UNKNOWN (no network capture, no server-side evidence).

**限制：** 证明客户端上传流水线完成并记录成功；服务器后续处理为 UNKNOWN（无网络抓包、无服务器侧证据）。

**Confidence:** CONFIRMED (client-side completion)

---

## F-021 — pending artifact deletion after success

**Claim:** After successful upload the local pending/tmp encrypted artifacts are deleted; failures leave `.tar.gz.enc` files for retry.

**声明：** 上传成功后，本地 pending/tmp 加密工件被删除；失败则留下 `.tar.gz.enc` 文件供重试。

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` `finally { ... delete plaintext ... }` ~310259-310266 (excerpt 12); pending cleanup module; `tmp/<id>.tar.gz` / `pending/<id>.tar.gz.enc` paths ~310330-310331; immediate flush ~312143.

**Local artifact:** census of both machines' checkpoints directories: only `state.json` + manifests/extra-manifests, **zero** `.enc`/tmp files.

**本地工件：** 两台机器 checkpoints 目录的清点：只有 `state.json` + manifests/extra-manifests，**零** `.enc`/tmp 文件。

**Reproduction:** `bash scripts/inspect-checkpoints.py --census`
**Corroboration:** third-party report of pending retention under failure conditions — PARTIALLY_REPRODUCED (code path confirmed; failed-upload retention not observed locally because no failed upload residue exists).

**佐证：** 第三方关于失败条件下 pending 保留的报告——PARTIALLY_REPRODUCED（代码路径已确认；本地无失败上传残留可供观察，故未观察到失败保留行为）。

**Confidence:** CONFIRMED

---

## F-022 — repoSnapshotIndexingEnabled is not a capture/upload gate

**Claim:** In the audited server bundle, `repoSnapshotIndexingEnabled` appears only as (a) settings schema with default `false`, (b) optional declaration, (c) patch normalization, and (d) a member of the uploaded settings-behavior key list; no code path conditions capture or upload on it. The sidecar is constructed unconditionally (F-001).

**声明：** 在被审计的 server bundle 中，`repoSnapshotIndexingEnabled` 仅以如下形式出现：(a) 默认 `false` 的设置 schema，(b) 可选声明，(c) patch 规范化，(d) 上传的 settings-behavior 键列表成员；没有任何代码路径以它作为捕获或上传的条件。sidecar 被无条件构造（F-001）。

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

**本地工件：** Windows 侧设置曾为 `false`，而其状态文件仍显示客户端记录的上传成功标记（F-020）；脱敏副本见 evidence/sanitized-logs/settings-extract.txt。

**Corroboration:** third-party: "the switch doesn't stop uploads" — REPRODUCED.

**佐证：** 第三方："the switch doesn't stop uploads"——REPRODUCED。

**Limitations:** statement is scoped to the audited client build; no claim is made about server-side semantics of the setting.

**限制：** 陈述仅限于被审计的客户端构建；不对该设置的服务器端语义做任何断言。

**Confidence:** CONFIRMED

---

## F-023 — local git checkpoint is a separate system

**Claim:** The user-visible checkpoint/rollback uses local git refs `refs/zcode/checkpoints/<workspaceHash>/<id>` with `GIT_AUTHOR_EMAIL: "checkpoint@zcode.local"` and restores via `git restore`; it performs no network I/O and is distinct from the repo snapshot upload system.

**声明：** 用户可见的 checkpoint/回滚使用本地 git refs `refs/zcode/checkpoints/<workspaceHash>/<id>`，`GIT_AUTHOR_EMAIL: "checkpoint@zcode.local"`，通过 `git restore` 恢复；它不执行任何网络 I/O，与 repo 快照上传系统是两个系统。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` ~214501, ~214636, ~214963 (excerpts 28-30).

**Reproduction:** excerpts 28-30; `grep -n 'refs/zcode/checkpoints\|checkpoint@zcode.local' ~/.zcode/server/zcode-server.cjs`
**Corroboration:** third-party conflation of the two systems — NOT_REPRODUCED (they are distinct).

**佐证：** 第三方对两个系统的混同——NOT_REPRODUCED（它们是独立的）。

**Confidence:** CONFIRMED

---

## F-024 — Repo Wiki dual-channel behavior

**Claim:** Repo Wiki has (1) a generation channel reading the local workspace and calling the LLM API, writing wiki text locally, and (2) a snapshot channel wiring wiki lifecycle events into the OSS snapshot upload.

**声明：** Repo Wiki 有 (1) 一条生成通道——读取本地工作区、调用 LLM API、在本地写入 wiki 文本；(2) 一条快照通道——把 wiki 生命周期事件接入 OSS 快照上传。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `server.cjs` — `runGenerate`/`LocalWorkspaceRepoReader` 308460-308560 (excerpt 14); `void captureRepoWikiSnapshot` ~308556; `captureTaskCompleteUpdate` 308831-308842 (excerpt 13); process manager excerpt 18; host RPC names excerpt 19.

**Reproduction:** `grep -n 'LocalWorkspaceRepoReader\|captureRepoWikiSnapshot' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-025 — ARMS RUM telemetry surface

**Claim:** The desktop bundle embeds the Aliyun ARMS RUM SDK reporting to `https://sdk.rum.aliyuncs.com` (events gzipped locally before send).

**声明：** 桌面 bundle 内嵌阿里云 ARMS RUM SDK，上报至 `https://sdk.rum.aliyuncs.com`（事件在发送前于本地 gzip）。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `app.asar` (binary grep outputs; reproduced by `scripts/inspect-upload-endpoints.py --telemetry` and recorded in evidence/telemetry-map.md).

**Limitations:** endpoint confirmed; concrete RUM event payloads UNKNOWN.

**限制：** 端点已确认；具体 RUM 事件载荷 UNKNOWN。

**Confidence:** CONFIRMED (endpoint) / UNKNOWN (payload)

---

## F-026 — SLS log endpoint

**Claim:** The desktop bundle embeds an Aliyun SLS log endpoint of the form `proj-xtrace-<project-id>-cn-beijing.cn-beijing.log.aliyuncs.com`.

**声明：** 桌面 bundle 内嵌形如 `proj-xtrace-<project-id>-cn-beijing.cn-beijing.log.aliyuncs.com` 的阿里云 SLS 日志端点。

**Evidence class:** [CONFIRMED-CODE]

**Source artifact:** `app.asar` binary grep (evidence/telemetry-map.md).

**Limitations:** what is actually shipped to SLS at runtime is UNKNOWN.

**限制：** 运行时实际发送到 SLS 的内容 UNKNOWN。

**Confidence:** CONFIRMED (endpoint) / UNKNOWN (payload)

---

## F-027 — deviceMid / X-Device-Mid

**Claim:** A `deviceMid` UUID is generated, persisted in `~/.zcode/v2/telemetry-state.json`, and sent as an `X-Device-Mid` request header on API requests.

**声明：** 生成 `deviceMid` UUID，持久化在 `~/.zcode/v2/telemetry-state.json`，并作为 API 请求的 `X-Device-Mid` 请求头发送。

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` header injection ~208120 (excerpt 16); persistence logic 274895-275030 (excerpt 17).

**Local artifact:** sanitized copy [evidence/sanitized-logs/telemetry-state.json](evidence/sanitized-logs/telemetry-state.json) (real value withheld).

**本地工件：** 脱敏副本 [evidence/sanitized-logs/telemetry-state.json](evidence/sanitized-logs/telemetry-state.json)（真实值保留不发）。

**Reproduction:** `grep -n 'deviceMid\|Device-Mid' ~/.zcode/server/zcode-server.cjs`
**Confidence:** CONFIRMED

---

## F-028 — local SQLite session storage

**Claim:** `~/.zcode/cli/db/db.sqlite` stores local sessions/messages/tool records; no upload path for this database was identified.

**声明：** `~/.zcode/cli/db/db.sqlite` 存储本地会话/消息/工具记录；未发现该数据库的上传路径。

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT]

**Local artifact:** [evidence/sqlite-schema.txt](evidence/sqlite-schema.txt); row counts (captured together with the published schema at 2026-09-19 14:11): message 24,496; part 105,875; tool_usage 30,334; model_usage 21,728; session 561.

**本地工件：** [evidence/sqlite-schema.txt](evidence/sqlite-schema.txt)；行数（2026-09-19 14:11 与已发布 schema 一并采集）：message 24,496；part 105,875；tool_usage 30,334；model_usage 21,728；session 561。

**Reproduction:** `python3 scripts/inspect-checkpoints.py --sqlite`
**Confidence:** CONFIRMED

---

## F-029 — no client-side embedding/indexing subsystem

**Claim:** No standalone client-side embedding/indexing subsystem was identified in the audited server bundle. The desktop bundle contains the string `embedding` (~740 occurrences, ~566 matching regions) inside packaged third-party code — primarily AI-SDK model-class libraries (e.g. `@ai-sdk/*/embedding-model`), plus unrelated third-party assets (telemetry semantic conventions, terminal/shiki assets and similar). No application-level embedding/indexing pipeline was identified in either artifact.

**声明：** 在被审计的 server bundle 中未发现独立的客户端 embedding/索引子系统。桌面 bundle 在打包的第三方代码中含字符串 `embedding`（约 740 次出现，约 566 个匹配区域）——主要是 AI-SDK 模型类库（如 `@ai-sdk/*/embedding-model`），另有无关联的第三方资产（遥测语义约定、terminal/shiki 资产等）。两个工件中均未发现应用级 embedding/索引流水线。

**Evidence class:** [CONFIRMED-CODE] (absence, scoped)

**Source artifact:** `server.cjs` — `embedding` 0 hits; no sqlite-vec/qdrant/lancedb/chromadb/hnsw/faiss identifiers. `app.asar` — library-only embedding references (reproduced by `scripts/locate-snapshot-code.sh --embedding-check`).

**Limitations:** absence of an application-level pipeline in these artifacts does not establish anything about server-side indexing, and does not cover non-audited desktop builds.

**限制：** 这些工件中应用级流水线的缺失，不确立任何关于服务器端索引的结论，也不覆盖未被审计的桌面构建。

**Confidence:** CONFIRMED (absence, scoped)

---

## F-030 — Remote WSL: no exemption observed in practice

**Claim:** No Remote-WSL exemption from client-side repo snapshot capture/upload was identified in practice on the audited machine: WSL workspaces were captured and uploaded with path-derived keys.

**声明：** 在被审计机器上，实践中未发现 Remote-WSL 对客户端 repo 快照捕获/上传的豁免：WSL 工作区以路径派生键被捕获并上传。

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT] + [CONFIRMED-CODE]

**Local artifact:** all 7 state files show `workspaceKey` equal to the raw filesystem path (identity empty at capture time); WSL-side server captured 6 WSL workspaces between 2026-09-08 and 2026-09-11 (TIMELINE.md).

**本地工件：** 全部 7 个状态文件的 `workspaceKey` 等于原始文件系统路径（捕获时 identity 为空）；WSL 侧 server 在 2026-09-08 至 2026-09-11 之间捕获了 6 个 WSL 工作区（TIMELINE.md）。

**Code context:** `wsl` co-occurs with snapshot/sidecar/capture symbols **0 times** in `server.cjs`; there is no WSL-conditional in the snapshot subsystem.

**代码上下文：** `server.cjs` 中 `wsl` 与 snapshot/sidecar/capture 符号**零次**共现；快照子系统中没有 WSL 条件分支。

**Reproduction:** `bash scripts/locate-snapshot-code.sh --wsl-gate-check`
**Limitations:** scoped to the audited machine and build. The desktop can model WSL targets as `kind:"remote"` (F-031); whether that path ever suppresses capture in practice was not observed. "No exemption was identified" ≠ "exemption cannot exist".

**限制：** 仅限于被审计机器与构建。桌面端可以把 WSL 目标建模为 `kind:"remote"`（F-031）；该路径在实践中是否曾抑制捕获未被观察到。"未发现豁免" ≠ "豁免不可能存在"。

**Confidence:** CONFIRMED (for observed behavior) / UNKNOWN (for unobserved remote-session configurations)

---

## F-031 — workspaceIdentity capture-suppression gate (remote sessions)

**Claim:** `captureBeforePrompt` returns immediately when `workspaceIdentity` is non-empty; `workspaceIdentity` is the identifier carried by remote sessions (several remote RPC schemas require it whenever `remoteSessionId` is present); the workspace key prefers identity over path. The identical gate exists in the desktop bundle.

**声明：** 当 `workspaceIdentity` 非空时 `captureBeforePrompt` 立即返回；`workspaceIdentity` 是远程会话携带的标识符（若干远程 RPC schema 在 `remoteSessionId` 存在时要求它）；工作区键优先使用 identity 而非路径。桌面 bundle 中存在完全相同的门槛。

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

**脱敏摘录（excerpt 32，桌面 asar）：**

```js
async captureBeforePrompt(t){t.workspaceIdentity?.trim()||await this.captureScheduler.schedule(...)
```

**Observed data:** all observed captures had empty identity (path-keyed) — the gate has not been observed to fire on this machine.

**观察数据：** 全部被观察捕获的 identity 为空（路径键控）——该门槛在本机上未被观察到触发。

**Limitations:** prompt-stage gate only; the task-complete path passes `workspaceIdentity` through to the same gate (excerpt 13). Whether current desktop builds set identity for WSL/SSH targets in practice is UNKNOWN (no such artifacts locally).

**限制：** 仅提示词阶段门槛；任务完成路径将 `workspaceIdentity` 传递给同一门槛（excerpt 13）。当前桌面构建在实践中是否为 WSL/SSH 目标设置 identity 属于 UNKNOWN（本地无此类工件）。

**Confidence:** CONFIRMED (code) / UNKNOWN (practical remote behavior)

---

## F-032 — CLI runtime contains no snapshot uploader; audit isolation

**Claim:** The standalone CLI runtime (`/opt/ZCode/zcode` ELF invoked as `zcode`) contains no `upload-credential` / RepoSnapshot uploader strings and its logs contain no repoSnapshot capture activity; the audit sessions themselves produced no new checkpoint artifacts.

**声明：** 独立 CLI 运行时（以 `zcode` 调用的 `/opt/ZCode/zcode` ELF）不含 `upload-credential` / RepoSnapshot 上传器字符串，其日志不含 repoSnapshot 捕获活动；审计会话本身未产生新的 checkpoint 工件。

**Evidence class:** [CONFIRMED-RUNTIME] (absence)

**Observed data:** `strings` search of the CLI binary: 0 hits for `upload-credential`, 0 for RepoSnapshot symbols; CLI log for 2026-09-19: 0 hits; no checkpoints directory under the CLI data root; no files newer than the audit start in either machine's checkpoints directory; no checkpoint state exists for the audit workspace itself.

**观察数据：** CLI 二进制的 `strings` 搜索：`upload-credential` 0 命中，RepoSnapshot 符号 0 命中；2026-09-19 的 CLI 日志：0 命中；CLI 数据根目录下无 checkpoints 目录；两台机器的 checkpoints 目录中均无晚于审计开始的文件；审计工作区本身不存在 checkpoint 状态。

**Reproduction:** `strings /opt/ZCode/zcode | grep -c upload-credential` (0); `find ~/.zcode/v2/checkpoints -newermt <audit-start> -type f` (empty)
**Limitations:** absence of strings in a stripped ELF and absence of artifacts is evidence of absence on this build/machine, not a guarantee.

**限制：** stripped ELF 中字符串的缺失与工件的缺失，是该构建/机器上的 absence 证据，不是保证。

**Confidence:** CONFIRMED (observed absence)

---

## F-033 — logging behavior of the snapshot subsystem

**Claim:** The snapshot subsystem emits no capture/upload/credential log lines; upload errors are silently discarded. The word `repoSnapshot` appears in local logs only inside full-settings JSON dumps written by `settingService` on every settings write (which also write `deviceSid`/`workspacePath` values into plaintext local logs).

**声明：** 快照子系统不发出任何 capture/upload/credential 日志行；上传错误被静默丢弃。本地日志中 `repoSnapshot` 一词仅出现在 `settingService` 每次设置写入时产生的完整设置 JSON 转储中（这些转储同时把 `deviceSid`/`workspacePath` 值写入明文本地日志）。

**Evidence class:** [CONFIRMED-CODE] + [CONFIRMED-LOCAL-ARTIFACT]

**Source artifact:** `server.cjs` — `void scheduled.catch(() => {})` at ~233399 (excerpt 07 region) and excerpt 26; upload path emits no log statements.

**Local artifact:** [evidence/sanitized-logs/upload-logging-absence-proof.txt](evidence/sanitized-logs/upload-logging-absence-proof.txt) — per-file counts for both machines; 100% of `repoSnapshot` hits classified as settings dumps; 0 subsystem activity lines.

**本地工件：** [evidence/sanitized-logs/upload-logging-absence-proof.txt](evidence/sanitized-logs/upload-logging-absence-proof.txt)——两台机器的逐文件计数；100% 的 `repoSnapshot` 命中被归类为设置转储；0 条子系统活动行。

**Corroboration:** third-party "silent upload" characterization — PARTIALLY_REPRODUCED (no subsystem logging confirmed; earlier draft claims of literally zero `repoSnapshot` grep hits were refined: the hits are settings dumps).

**佐证：** 第三方 "silent upload" 定性——PARTIALLY_REPRODUCED（确认子系统无日志；早先草稿中 "`repoSnapshot` grep 零命中" 的说法已被修正：命中来自设置转储）。

**Confidence:** CONFIRMED

---

## F-034 — capture anchor to the audited build

**Claim:** A capture recorded by the desktop-side runtime at 2026-09-17 20:57 local time post-dates the audited desktop build (app.asar mtime 2026-09-04 16:08), anchoring the observed capture behavior to the audited artifacts.

**声明：** 桌面侧运行时记录于 2026-09-17 20:57 本地时间的一次捕获晚于被审计的桌面构建（app.asar mtime 2026-09-04 16:08），把观察到的捕获行为锚定到被审计工件。

**Evidence class:** [CONFIRMED-LOCAL-ARTIFACT]

**Local artifact:** Windows-side state file `ws-c` (sanitized copy): `lastCompressedSize.recordedAt` epoch = 2026-09-17 20:57 +0800; desktop build mtimes in [evidence/build-info.md](evidence/build-info.md).

**本地工件：** Windows 侧状态文件 `ws-c`（脱敏副本）：`lastCompressedSize.recordedAt` epoch = 2026-09-17 20:57 +0800；桌面构建 mtime 见 [evidence/build-info.md](evidence/build-info.md)。

**Limitations:** mtime-based build identification; a hypothetical unrecorded in-place swap of the desktop bundle cannot be fully excluded (no evidence of one exists).

**限制：** 基于 mtime 的构建识别；无法完全排除假想中未留记录的原地替换桌面 bundle（不存在此类替换的证据）。

**Confidence:** CONFIRMED (with the stated mtime caveat)
