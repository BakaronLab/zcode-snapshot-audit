# ZCode 3.14.0 — Regression Follow-up · 3.14.0 回归跟进

[English](#english) · [中文](#中文)

This directory is an **independent follow-up** to the audit published in the repository root. It
asks one question of a newer build: *do the client-side behaviors documented in
[EVIDENCE.md](../EVIDENCE.md) (F-001 … F-034) still exist in ZCode 3.14.0?*

It is not a replacement for the original findings, and it does not revise them. The root
findings remain **historical findings for the hashed earlier builds they cite**.

本目录是仓库根目录所发布审计的**独立跟进**。它只针对一个更新的构建问一个问题：*[EVIDENCE.md](../EVIDENCE.md)
中记录的客户端行为（F-001 … F-034）在 ZCode 3.14.0 中是否仍然存在？* 它不是原始 findings 的替代，也不修改它们。
根目录的 findings 仍然是**针对其所引用的、已固定哈希的旧构建的历史结论**。

## Canonical statement · 规范表述

> **EN.** ZCode 3.14.0 removes the client-side repo-snapshot and Repo Wiki module clusters
> observed in the previously audited builds. No equivalent repo/workspace snapshot upload
> implementation was identified in the audited 3.14.0 client artifacts. This follow-up does not
> alter the historical findings for the hashed earlier artifacts.

> **中文.** ZCode 3.14.0 中，先前审计构建所观察到的客户端 repo-snapshot 与 Repo Wiki 模块簇已被移除。
> 在本次审计的 3.14.0 客户端工件中，未识别到等价的 repo/workspace snapshot 上传实现。本跟进不改变针对
> 已固定哈希旧构建的历史结论。

## Version relationship · 版本关系

The two audited components version **independently** and were *never* on the same version. Stating
this correctly matters: each component is compared against its own predecessor — desktop
3.11.2 → 3.14.0, server 3.12.3 → 3.14.0 — and never the desktop version against the server bundle.

被审计的两个组件**独立**升级，且从来不在同一版本上。这里必须写准确：每个组件都与自己的前代比较——桌面
3.11.2 → 3.14.0、服务器 3.12.3 → 3.14.0——而不是把桌面版本与服务器 bundle 混为一谈。

```
desktop   3.11.2 (Linux, audited)   →   3.14.0 (Windows, audited here)
server    3.12.3 (WSL,   audited)   →   3.14.0 (WSL,     audited here)
```

| Side | Old (this repo's original audit) | New (this follow-up) |
|---|---|---|
| Desktop | 3.11.2, Linux, `app.asar` 307,138,103 B | **3.14.0**, Windows, `app.asar` 326,893,098 B, build commit `a1328db1` |
| Server | **3.12.3**, WSL `zcode-server.cjs` 13,409,418 B | **3.14.0**, WSL `zcode-server.cjs` 11,527,731 B |
| Server (second bundle) | not separately examined | **3.14.0**, WSL `agents/glm/zcode.cjs` 14,796,490 B |

The old server bundle self-declares `ZCODE_VERSION = "3.12.3"`; the old desktop was 3.11.2. That is
an artifact of independent update channels, not an error in the published audit. The old artifact
hashes cited here are the ones already published in
[evidence/artifact-hashes.md](../evidence/artifact-hashes.md) and reproduced from the frozen copies.

## Headline result · 主要结果

In the audited 3.14.0 client artifacts:

1. **The repo-snapshot module cluster is removed.** `services/src/repo-snapshot/*` — 20 modules —
   and both `shared/src` contract modules do not exist. → [MODULE-CLUSTER-DIFF.md](MODULE-CLUSTER-DIFF.md)
2. **The Repo Wiki feature is removed**, not merely its upload trigger: the whole
   `services/src/repo-wiki/*` cluster — 22 modules, including the local generation half.
   → [MODULE-CLUSTER-DIFF.md](MODULE-CLUSTER-DIFF.md)
3. **The prompt-stage hook is gone from a module that still exists.** `zcodeAgentService.ts`
   survives (and grew by +5,503 B), but every capture-related symbol is absent from it.
   → [DELTA.md](DELTA.md)
4. **All 20 required symbol probes read zero across the audited 3.14.0 artifacts**, while the
   control surfaces survive byte-identically. → [SYMBOL-DIFF.md](SYMBOL-DIFF.md)
5. **A calibrated five-signal combination test isolates the old subsystem and returns nothing on
   3.14.0.** → [SNAPSHOT-HIT-CLASSIFICATION.md](SNAPSHOT-HIT-CLASSIFICATION.md)
6. **The residual OSS/upload surface is a different, user-initiated feature** (feedback
   attachments), not a successor to the removed subsystem.
   → [UPLOAD-SURFACE-ATTRIBUTION.md](UPLOAD-SURFACE-ATTRIBUTION.md)

### Four key questions · 四个关键问题

| # | Question | Answer |
|---|---|---|
| Q1 | Do ordinary agent prompts still enter a repo/workspace snapshot upload path? | **NO** — the hook was removed from a surviving host module; no successor hook was identified |
| Q2 | Does Repo Wiki still trigger that path? | **NO** — the entire Repo Wiki feature is absent, not just its trigger |
| Q3 | Does the old repo-snapshot subsystem still exist in 3.14.0? | **NO_EQUIVALENT_FOUND** — no equivalent was identified under any name |
| Q4 | If a repo capture existed, would `.git` regular files still enter scope? | **NO_REPO_CAPTURE_SUBSYSTEM_FOUND** — deliberately *not* phrased as ".git exclusion was fixed" |

## Audited 3.14.0 artifacts · 被审计的 3.14.0 工件

| Artifact | Size (B) | SHA-256 |
|---|---|---|
| Server bundle `zcode-server.cjs` (WSL, 3.14.0) | 11,527,731 | `99fcad13480b7402843d4d3178bc6bbe01f1a991288a5c582ed3241c9771f003` |
| Server-side second bundle `agents/glm/zcode.cjs` (WSL, 3.14.0) | 14,796,490 | `8f5cfccf2a899b92e57bc2a5760b949c1a928f739652fffc9e6d07c24f11ba05` |
| Desktop `app.asar` (Windows, 3.14.0, commit `a1328db1`) | 326,893,098 | `8604b5f47b0f4bf9e900901d8c60a0dcf6406b89879da872640ae27026b628cb` |

Sizes, SHA-256 and SHA-512, provenance and the old-side reference hashes: →
[evidence/artifact-hashes-3.14.md](evidence/artifact-hashes-3.14.md).

**The second server-side bundle is disclosed on purpose.** A first draft of this audit asserted
there was no second bundle where a subsystem could be hiding; an independent review found that to
be false. `~/.zcode/server/agents/glm/zcode.cjs` is a second server-side JavaScript bundle,
replaced by the same 3.14.0 update. It was frozen and probed: **0 hits for every repo-snapshot
symbol**. All negative claims here are scoped to the three examined artifacts.

**第二个服务端 bundle 是刻意披露的。**本审计初稿曾断言"不存在第二个可隐藏子系统的 bundle"，独立评审认定该断言为假。
`~/.zcode/server/agents/glm/zcode.cjs` 是第二个服务端 JavaScript bundle，由同一次 3.14.0 更新替换。它已被冻结并探测：
**所有 repo-snapshot 符号均为 0 次命中**。本文所有否定性结论均以这三个被检查工件为界。

## What this follow-up does NOT claim · 本跟进不主张什么

- It does **not** claim ZCode stopped uploading repositories, or that it will not upload code in
  future.
- It does **not** claim the service deleted any historical data, stopped collecting data, or that
  previously uploaded data was deleted.
- It does **not** claim 3.14.0 is "completely safe", or that all upload functionality was removed.
  **Other upload paths still exist** — in particular user-initiated feedback attachment upload, and
  conversation-share artifact upload (both present before this update and unchanged).
- It does **not** infer server-side behavior from client-side absence. **Server-side handling of
  previously uploaded snapshots is UNKNOWN, and was UNKNOWN before.**
- It does **not** claim the `.git` handling was repaired.

The supported statement is narrower: *the audited client-side repo-snapshot implementation was not
identified in 3.14.0.*

## Method in one paragraph

Each 3.14.0 artifact was frozen and hashed before analysis. The delta rests on four independent
lines of evidence: (1) a whole-module-set diff using the bundles' own retained esbuild module-path
comments, (2) required symbol probes measured as raw byte occurrences on all four artifacts with
validated controls, (3) a **calibrated combination test** that scores each module on five behavioral
signals (archive, upload, manifest, workspace enumeration, prompt trigger), validated by checking
that it isolates the known old subsystem, and (4) per-module attribution of every surviving
`snapshot` occurrence. Full method and limitations: [DELTA.md](DELTA.md).

## Verification · 如何验证

Everything published here is recomputable from artifact hashes and from your own installation. The
scripts in [`scripts/`](scripts/) take file paths as arguments and contain no hard-coded local paths.

```sh
# 1. Identify your build (hashes above; see also ../scripts/hash-zcode-artifacts.sh)
sha256sum ~/.zcode/server/zcode-server.cjs

# 2. Which whole module clusters disappeared?
python3 followup-3.14/scripts/module-diff.py <old/zcode-server.cjs> <new/zcode-server.cjs>

# 3. Attribute every surviving `snapshot` occurrence to its owning module
python3 followup-3.14/scripts/snapshot-hit-classify.py <new/zcode-server.cjs> snapshot

# 4. The calibrated five-signal combination test
python3 followup-3.14/scripts/combination-test.py <old/zcode-server.cjs>
python3 followup-3.14/scripts/combination-test.py <new/zcode-server.cjs>
```

Direct probes (any grep works; counts below are case-sensitive raw byte occurrences):

```sh
grep -ao "captureBeforePrompt" zcode-server.cjs | wc -l     # 3.12.3: 5   →  3.14.0: 0
grep -ao "repoSnapshot"        zcode-server.cjs | wc -l     # 3.12.3: 92  →  3.14.0: 0
grep -ao "checkpoint@zcode.local" zcode-server.cjs | wc -l  # 3.12.3: 2   →  3.14.0: 2  (control)
```

## Contents · 目录

| File | What it contains |
|---|---|
| [DELTA.md](DELTA.md) | The delta narrative, the four key questions, the official-fix classification (CASE B), controls, limitations |
| [REGRESSION-MATRIX.md](REGRESSION-MATRIX.md) | All 34 findings F-001 … F-034 mapped to a new status, with per-row evidence |
| [MODULE-CLUSTER-DIFF.md](MODULE-CLUSTER-DIFF.md) | Module-set diff: what was removed, what was added |
| [SYMBOL-DIFF.md](SYMBOL-DIFF.md) | Required probes, controls, reduced-count survivors, and their attribution |
| [SNAPSHOT-HIT-CLASSIFICATION.md](SNAPSHOT-HIT-CLASSIFICATION.md) | All 775 surviving `snapshot` occurrences classified; the calibrated combination test |
| [UPLOAD-SURFACE-ATTRIBUTION.md](UPLOAD-SURFACE-ATTRIBUTION.md) | Residual `upload-credential` / OSS surface attributed to feedback, not to a snapshot successor |
| [evidence/artifact-hashes-3.14.md](evidence/artifact-hashes-3.14.md) | Hashes, sizes, provenance, and how to reproduce them |
| [evidence/control-surfaces.md](evidence/control-surfaces.md) | The controls that make the zeros meaningful |
| [evidence/open-questions.md](evidence/open-questions.md) | What remains unresolved, including `OPEN-314-001a` and all server-side questions |

## Review history · 评审历史

This follow-up was published only after an internal sanity pass and an independent adversarial
review of the delta reports, which returned a **BLOCK** on supporting inconsistencies and later, on
mechanically verifiable defects. All blocking items were corrected (module counts, symbol counts,
disclosure of a second server bundle, disclosure of desktop-side residuals, counting conventions,
and two published cell counts), and the final review verdict was **ACCEPT**, with the reviewer
independently re-measuring every numeric cell of the published symbol table (61 rows × 4 artifact
columns = 244 cells). The reviewer found no equivalent capture/upload subsystem in 3.14.0 at any
point across its passes.

本跟进仅在内审与独立对抗性评审之后发布。评审先就支撑性陈述不一致给出 **BLOCK**，随后又指出若干可机械验证的缺陷；
所有阻塞项均已修正（模块计数、符号计数、第二个服务端 bundle 的披露、桌面侧残留的披露、计数口径，以及两处公开的单元计数），
最终评审结论为 **ACCEPT**，评审者独立复测了公开符号表的每一个数值单元（61 行 × 4 个工件列 = 244 个单元）。
评审在任何一轮中均未在 3.14.0 中发现等价的捕获/上传子系统。

## Limitations · 局限

1. **Static analysis only.** No packet capture, no TLS interception, no certificate bypass. Nothing
   here observes the wire.
2. **Server-side behavior is UNKNOWN** and was UNKNOWN before. Client-side absence says nothing
   about what the service retains or processes.
3. **Desktop structural evidence is weaker than server evidence.** The desktop `app.asar` does not
   retain application source paths for its own code, so desktop conclusions are symbol-level with
   control validation, not module-cluster-level.
4. **Cross-platform comparison.** The old desktop payload is Linux, the new one Windows. The
   JavaScript payload is comparable; native executables (ELF vs PE) are not, and none of the claims
   here depend on a native-code delta.
5. **Runtime not exercised.** No prompt was sent and no behavior was triggered to test the new
   build. No claim is made that 3.14.0 "never uploads" anything.

A change to this conclusion would require a functional equivalent written with entirely disjoint
vocabulary *and* structured so that the five signals never co-occur in a single module, or a
client-side capture component in an artifact outside the three examined here (for example a
lazily-downloaded module, or a different platform's bundle). See [DELTA.md](DELTA.md)
§"What would change this conclusion".

## Licensing and provenance · 许可与来源

Same as the repository root: MIT ([LICENSE](../LICENSE)). No proprietary bundle, installer, or
extracted bundle is published in this directory — only artifact hashes, module names, symbol names,
counts, call-graph descriptions, and minimum-necessary excerpts.
