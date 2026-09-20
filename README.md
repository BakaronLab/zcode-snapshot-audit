# ZCode Snapshot Audit

[English](#confirmed-client-side-behavior--已确认的客户端行为) · [中文](#中文对照)

## Version follow-up · 版本跟进

**EN.** Update: in the audited ZCode 3.14.0 client artifacts, the client-side repo-snapshot / Repo Wiki module clusters documented below are no longer present. A separate regression audit is available in [followup-3.14/](followup-3.14/README.md). The original findings remain historical findings for the hashed earlier builds.

**中文.** 更新：在本次审计的 ZCode 3.14.0 客户端工件中，下文记录的客户端 repo-snapshot / Repo Wiki 模块簇已不再存在。独立回归审计见 [followup-3.14/](followup-3.14/README.md)。原始 findings 仍是针对已固定哈希旧构建的历史结论。

This repository documents independently verifiable client-side behavior observed in a locally installed ZCode build. It does **not** make unsupported claims about:

本仓库记录在本地安装的 ZCode 构建中观察到的、可独立验证的客户端行为。它不做出以下无证据支持的断言（English is canonical; 中文为对照译文）：

- server-side retention
- training usage
- model distillation
- employee access
- corporate intent

unless directly supported by evidence. Statements in this repository are labeled with evidence classes ([CONFIRMED-CODE], [CONFIRMED-LOCAL-ARTIFACT], [CONFIRMED-RUNTIME], [INDEPENDENT-CORROBORATION], [INFERRED], [UNKNOWN]) and every finding is traceable in [EVIDENCE.md](EVIDENCE.md).

除非有直接证据支持。本仓库中的所有陈述均标注证据等级（[CONFIRMED-CODE]、[CONFIRMED-LOCAL-ARTIFACT]、[CONFIRMED-RUNTIME]、[INDEPENDENT-CORROBORATION]、[INFERRED]、[UNKNOWN]），每项 finding 均可在 [EVIDENCE.md](EVIDENCE.md) 中溯源。

ZCode is an AI coding client. The audited installation consists of a Windows desktop application (Electron, `/opt/ZCode`-style install observed on the WSL side) plus a Node.js server bundle (`zcode-server.cjs`) that runs inside the WSL environment and serves agent sessions. All findings below were reproduced on one machine against one specific build; see [REPORT.md](REPORT.md) → *Tested Build* and [evidence/artifact-hashes.md](evidence/artifact-hashes.md) for the exact hashes so you can check whether your build matches.

ZCode 是一个 AI 编码客户端。被审计的安装由两部分组成：Windows 桌面应用（Electron，在 WSL 侧观察到 `/opt/ZCode` 风格的安装）+ 运行在 WSL 环境内、为 agent 会话提供服务的 Node.js server bundle（`zcode-server.cjs`）。以下全部 finding 均在一台机器上针对一个特定构建复现；确切哈希见 [REPORT.md](REPORT.md) → *Tested Build* 与 [evidence/artifact-hashes.md](evidence/artifact-hashes.md)，可用于核对你的构建是否一致。

## Confirmed client-side behavior · 已确认的客户端行为

The following are confirmed by direct code inspection and/or local artifacts of the audited build. This is factual client-side behavior; this repository draws no conclusions about server-side use of the data.

以下内容经对被审计构建的直接代码检查和/或本地工件确认。这些是事实层面的客户端行为；本仓库不对服务器端如何使用这些数据下任何结论。

| # | Behavior | Evidence |
|---|---|---|
| 1 | **Workspace snapshot creation**: the client builds a complete archive of the workspace (file contents included) before each capture-eligible prompt — prompt-stage capture is gated by the workspaceIdentity, authentication, credential, and quota preconditions (workspaceIdentity gate: [F-031](EVIDENCE.md)) — and on successful task completion | [F-002](EVIDENCE.md), [F-003](EVIDENCE.md), [F-031](EVIDENCE.md), code excerpts 07/08 |
| 2 | **`.git/` inclusion**: `.git` metadata is recursively enumerated and regular files under `.git` are added to snapshot scope — objects, pack files, reflog (`logs/HEAD`), `config`, `index`, `lost-found`, and worktree metadata observed in real manifests (the symlink exclusion still applies inside `.git`) | [F-005](EVIDENCE.md)–[F-010](EVIDENCE.md); manifests showing 62–90% of archive entries are `.git/**` |
| 3 | **Filter bypass**: the `.git` short-circuit bypasses secret-path filtering and the 1 MB per-file size check; symlink exclusion still applies, and binary/content sampling occurs later in the pipeline; >1 MB pack files appear in real manifests | [F-009](EVIDENCE.md), [F-010](EVIDENCE.md), code excerpt 10 |
| 4 | **Prompt capture**: when a capture occurs, the full user prompt text is embedded in the archive (`meta/prompt.json` ← `params.prompt.content`) | [F-003](EVIDENCE.md), code excerpts 07/08 |
| 5 | **Global config capture**: `mcp.json`, `hooks.json`, `memory.json`, `instructions.json`, `subagents.json`, `skills.json`, `commands.json`, `plugins.json`, `settings.behavior.json` are packed into the archive | [F-012](EVIDENCE.md), code excerpt 15 |
| 6 | **Key-name-only redaction**: config values are redacted only when the *key name* matches `SENSITIVE_KEY_PATTERN`; non-matching key names (and values embedding secrets) pass through unredacted (synthetic escape test included) | [F-013](EVIDENCE.md), code excerpt 15, `evidence/sanitized-logs/` |
| 7 | **Envelope encryption**: archive is gzip + AES-256-CTR with a random data key; the data key is wrapped with a **server-provided RSA public key** (RSA-OAEP-SHA256) | [F-016](EVIDENCE.md), [F-017](EVIDENCE.md), code excerpt 09 |
| 8 | **Upload credential endpoint**: `GET {origin}/api/v1/snapshot/upload-credential` (default origin `https://zcode.z.ai`) returns OSS host/policy/signature/security-token, the RSA public key, and a snapshot id | [F-014](EVIDENCE.md), [F-015](EVIDENCE.md), code excerpts 01–03, 22 |
| 9 | **OSS upload**: the encrypted archive is POSTed as a multipart form to a runtime-delivered Aliyun OSS host; the OSS callback returns `update_type`, `checksum` (plaintext sha256), `encrypted_aes_key`, `base_snapshot_id`, and attribution metadata to the server | [F-018](EVIDENCE.md), [F-019](EVIDENCE.md), code excerpt 04 |
| 10 | **Upload-completion state evidence**: all 7 locally observed workspace state files contain `lastAcceptedManifestHash` — the client's own marker, written only after its upload path reports success (server-side processing not independently observable); local `pending` artifacts are deleted after success (no `.enc` residue) | [F-020](EVIDENCE.md), [F-021](EVIDENCE.md) |
| 11 | **Setting does not gate upload**: `repoSnapshotIndexingEnabled` appears in the server bundle only as schema/normalization/uploaded-key-list entries; the sidecar is instantiated unconditionally; the setting value itself is uploaded inside the archive | [F-022](EVIDENCE.md), code excerpts 06/20/27 |
| 12 | **Local checkpoint ≠ snapshot upload**: the user-visible "checkpoint rollback" is a pure-local git-refs mechanism (`refs/zcode/checkpoints/...`, `git restore`); the OSS snapshot system is separate and one-directional (no download/restore endpoint found) | [F-023](EVIDENCE.md), code excerpts 28–30 |
| 13 | **Repo Wiki dual channel**: Repo Wiki generation reads the workspace locally and calls the LLM API; additionally, wiki lifecycle events trigger the same snapshot capture/upload path | [F-024](EVIDENCE.md), code excerpts 13/14 |
| 14 | **Telemetry surfaces**: Aliyun ARMS RUM SDK endpoint (`sdk.rum.aliyuncs.com`) and an Aliyun SLS log endpoint are embedded in the desktop bundle; a `deviceMid` identifier is persisted locally and sent as an `X-Device-Mid` header | [F-025](EVIDENCE.md)–[F-027](EVIDENCE.md) |
| 15 | **No client embedding/indexing subsystem identified**: zero hits in the audited server bundle; desktop-bundle hits sit in packaged third-party code (primarily AI-SDK model libraries, plus unrelated third-party assets), with no application-level pipeline | [F-029](EVIDENCE.md) |

### 中文对照

| # | 行为 | 证据 |
|---|---|---|
| 1 | **工作区快照创建**：在每个符合捕获条件的提示词之前——提示词阶段的捕获受 workspaceIdentity、认证、凭据与配额前置条件约束（workspaceIdentity 门槛见 [F-031](EVIDENCE.md)）——以及任务成功完成时，客户端构建完整的工作区归档（包含文件内容） | [F-002](EVIDENCE.md)、[F-003](EVIDENCE.md)、[F-031](EVIDENCE.md)、代码摘录 07/08 |
| 2 | **`.git/` 收录**：`.git` 元数据被递归枚举，`.git` 下的常规文件进入快照范围——包括真实 manifest 中观察到的 objects、pack 文件、reflog（`logs/HEAD`）、`config`、`index`、`lost-found`、worktree 元数据（symlink 排除在 `.git` 内仍然生效） | [F-005](EVIDENCE.md)–[F-010](EVIDENCE.md)；真实 manifest 中 `.git/**` 占归档条目的 62–90% |
| 3 | **过滤绕过**：`.git` 短路分支绕过的是 secret 路径过滤与单文件 1 MB 大小检查；symlink 排除仍然生效，binary/内容采样发生在流水线后续阶段；>1 MB 的 pack 文件出现在真实 manifest 中 | [F-009](EVIDENCE.md)、[F-010](EVIDENCE.md)、代码摘录 10 |
| 4 | **提示词捕获**：捕获发生时，完整用户提示词文本被嵌入归档（`meta/prompt.json` ← `params.prompt.content`） | [F-003](EVIDENCE.md)、代码摘录 07/08 |
| 5 | **全局配置捕获**：`mcp.json`、`hooks.json`、`memory.json`、`instructions.json`、`subagents.json`、`skills.json`、`commands.json`、`plugins.json`、`settings.behavior.json` 被打包进归档 | [F-012](EVIDENCE.md)、代码摘录 15 |
| 6 | **仅按键名脱敏**：只有当*键名*匹配 `SENSITIVE_KEY_PATTERN` 时配置值才会被脱敏；不匹配的键名（以及内嵌秘密的值）未经脱敏直接通过（含合成逃逸测试） | [F-013](EVIDENCE.md)、代码摘录 15、`evidence/sanitized-logs/` |
| 7 | **信封加密**：归档为 gzip + AES-256-CTR（随机数据密钥）；数据密钥用**服务器提供的 RSA 公钥**（RSA-OAEP-SHA256）封装 | [F-016](EVIDENCE.md)、[F-017](EVIDENCE.md)、代码摘录 09 |
| 8 | **上传凭据端点**：`GET {origin}/api/v1/snapshot/upload-credential`（默认 origin `https://zcode.z.ai`）返回 OSS host/policy/signature/security-token、RSA 公钥与快照 id | [F-014](EVIDENCE.md)、[F-015](EVIDENCE.md)、代码摘录 01–03、22 |
| 9 | **OSS 上传**：加密归档以 multipart form POST 到运行时下发的阿里云 OSS host；OSS 回调向服务器返回 `update_type`、`checksum`（明文 sha256）、`encrypted_aes_key`、`base_snapshot_id` 与归因元数据 | [F-018](EVIDENCE.md)、[F-019](EVIDENCE.md)、代码摘录 04 |
| 10 | **上传完成状态证据**：本地观察到的全部 7 个工作区状态文件都含 `lastAcceptedManifestHash`——客户端自己的标记，仅在其上传路径报告成功后写入（服务器端处理无法独立观察）；本地 `pending` 工件在成功后删除（无 `.enc` 残留） | [F-020](EVIDENCE.md)、[F-021](EVIDENCE.md) |
| 11 | **设置不构成上传门槛**：`repoSnapshotIndexingEnabled` 在 server bundle 中仅以 schema/normalization/上传键列表条目出现；sidecar 被无条件实例化；该设置值本身也被上传进归档 | [F-022](EVIDENCE.md)、代码摘录 06/20/27 |
| 12 | **本地 checkpoint ≠ 快照上传**：用户可见的"checkpoint 回滚"是纯本地 git-refs 机制（`refs/zcode/checkpoints/...`、`git restore`）；OSS 快照系统独立且单向（未发现下载/恢复端点） | [F-023](EVIDENCE.md)、代码摘录 28–30 |
| 13 | **Repo Wiki 双通道**：Repo Wiki 生成在本地读取工作区并调用 LLM API；此外，wiki 生命周期事件会触发同一条快照捕获/上传路径 | [F-024](EVIDENCE.md)、代码摘录 13/14 |
| 14 | **遥测面**：桌面 bundle 内嵌阿里云 ARMS RUM SDK 端点（`sdk.rum.aliyuncs.com`）与一个阿里云 SLS 日志端点；`deviceMid` 标识持久化在本地并以 `X-Device-Mid` 请求头发送 | [F-025](EVIDENCE.md)–[F-027](EVIDENCE.md) |
| 15 | **未发现客户端 embedding/索引子系统**：被审计 server bundle 中零命中；桌面 bundle 的命中位于打包的第三方代码中（主要是 AI-SDK 模型库，另有无关联的第三方资产），不存在应用级流水线 | [F-029](EVIDENCE.md) |

## What this repository is not · 本仓库不做的主张

- It is not a claim that ZCode "steals" anything. Words like *spyware*, *theft*, *backdoor* are user/community characterizations found in third-party discussion; they are not audit conclusions (see [evidence/independent-corroboration.md](evidence/independent-corroboration.md)).
- It does not establish what the vendor's servers do with uploaded snapshots. The cryptographic design means the server *has the capability* to decrypt snapshots ("server possesses the corresponding capability under this envelope-encryption design"); whether and how it does is [UNKNOWN](docs/known-unknowns.md).
- It does not include any raw private evidence. Raw manifests, logs, databases, `.git` objects, and proprietary bundles were **not** uploaded; only sanitized derivatives and minimum-necessary code references are published (see [METHODOLOGY.md](METHODOLOGY.md)).

- 本仓库不主张 ZCode "窃取"了任何东西。*spyware*、*theft*、*backdoor* 等词是第三方讨论中的用户/社区定性，不是审计结论（见 [evidence/independent-corroboration.md](evidence/independent-corroboration.md)）。
- 本仓库不确立厂商服务器对已上传快照做了什么。密码学设计意味着服务器*具备*解密快照的能力（"在该信封加密设计下，服务器拥有相应的解密能力"）；是否以及如何行使该能力属于 [UNKNOWN](docs/known-unknowns.md)。
- 本仓库不包含任何原始隐私证据。原始 manifest、日志、数据库、`.git` objects 与专有 bundle 均**未**上传；仅发布脱敏衍生件与最小必要代码引用（见 [METHODOLOGY.md](METHODOLOGY.md)）。

## Repository structure · 仓库结构

```
README.md                 this file · 本文件（中英双语）
REPORT.md                 full audit report · 完整审计报告
EVIDENCE.md               evidence ledger (F-001…F-034, claim → artifact → code location → reproduction) · 证据台账（中英双语）
METHODOLOGY.md            audit method, chain of custody, evidence classes · 审计方法、证据链、证据等级
THREAT-MODEL.md           what the encryption does / does not protect · 加密保护什么/不保护什么
TIMELINE.md               build timestamps, capture timestamps, audit timeline · 构建/捕获/审计时间线
evidence/
  artifact-hashes.md      SHA-256 of audited program artifacts · 被审计程序工件的 SHA-256
  build-info.md           build/version/mtime identification · 构建/版本/mtime 识别
  sanitized-code-references.md  minimum-necessary code excerpts (source + line ranges) · 最小必要代码摘录（来源 + 行号）
  sanitized-state/        sanitized checkpoint state.json copies (7 workspaces) · 脱敏 checkpoint state.json 副本（7 个工作区）
  sanitized-manifests/    sanitized snapshot manifests (3 workspaces, sizes preserved) · 脱敏快照 manifest（3 个工作区，大小保留）
  sanitized-extra-manifest/ sanitized global-config manifests · 脱敏全局配置 manifest
  sanitized-logs/         sanitized log evidence (upload-logging behavior, telemetry state) · 脱敏日志证据（上传日志行为、遥测状态）
  endpoint-map.md         API/OSS endpoints, methods, request/response schemas · API/OSS 端点、方法、请求/响应 schema
  cryptography-flow.md    envelope-encryption data flow · 信封加密数据流
  telemetry-map.md        telemetry channels · 遥测通道
  runtime-observations.md dynamic observations on the audited machine · 被审计机器上的动态观察
  manifest-statistics.md  .git share statistics of real manifests · 真实 manifest 的 .git 占比统计
  independent-corroboration.md third-party findings vs local reproduction status · 第三方 finding 与本地复现状态对照
  sqlite-schema.txt       local SQLite schema + row counts (no content) · 本地 SQLite schema + 行数（无内容）
scripts/                  reproduction & scanning scripts (run against your own install) · 复现与扫描脚本（对你自己的安装运行）
docs/                     mitigation, known unknowns, reproduction guide · 缓解措施、已知未知、复现指南
```

## Reproduction · 复现

Clone this repository and run the scripts against your own ZCode installation; they are read-only and contain no hard-coded identities. Start with [docs/reproduction.md](docs/reproduction.md):

克隆本仓库，对您自己的 ZCode 安装运行这些脚本；脚本只读且不含硬编码身份信息。从 [docs/reproduction.md](docs/reproduction.md) 开始：

```bash
bash scripts/hash-zcode-artifacts.sh          # identify & hash your installed build · 识别并哈希您的构建
bash scripts/locate-snapshot-code.sh          # find the snapshot subsystem in your bundle · 在 bundle 中定位快照子系统
python3 scripts/summarize-manifest.py ~/.zcode/v2/checkpoints/<id>/manifests/<hash>.json
```

## Privacy and redaction principles · 隐私与脱敏原则

- Originals were never modified; sanitized derivatives were produced by parse → recursive redact → secret-scan (see [METHODOLOGY.md](METHODOLOGY.md)).
- Real usernames, hostnames, project names, workspace/snapshot/manifest identifiers, device ids, branch names, remote names, worktree names, git object ids, and all credential material are replaced with placeholders.
- Sizes, counts, percentages, timestamps, and program-artifact hashes are preserved because they are the evidence.
- No raw `.git` objects, no databases, no proprietary bundles, no raw logs, no real prompts are published.

- 原件从未被修改；脱敏衍生件经 parse → 递归脱敏 → secret 扫描生成（见 [METHODOLOGY.md](METHODOLOGY.md)）。
- 真实用户名、主机名、项目名、workspace/snapshot/manifest 标识符、设备 id、分支名、remote 名、worktree 名、git object id 以及全部凭据材料均替换为占位符。
- 大小、计数、百分比、时间戳与程序工件哈希被保留，因为它们本身就是证据。
- 不发布任何原始 `.git` objects、数据库、专有 bundle、原始日志或真实提示词。

## License · 许可证

MIT — see [LICENSE](LICENSE). · MIT — 见 [LICENSE](LICENSE)。
