# OFFICIAL-SOURCE-STATE — what ZCode's published source is, at the frozen revision

This file records the state of the official public source repository as observed for this round, and
nothing else. The frozen anchor and its hashes are in
[`evidence/official-source-anchor.md`](evidence/official-source-anchor.md); this file is the readable
summary.

## Identity

| Field | Value |
|---|---|
| Repository | `zai-org/ZCode` |
| Default branch | `main` |
| **Frozen HEAD** | `872ad960de7ec172591f7e1952f7849229f94521` |
| **Frozen tree** | `d185a9a893c00d51fc3fe51fe7371b9eea7de143` |
| Commit timestamp | `2026-09-21T05:14:32+08:00` (= `2026-09-20T21:14:32Z`) |
| Commit subject | `feat: open source` |
| Root `package.json` name / version / license | `zcode` / **`3.14.0`** / **`Apache-2.0`** |
| `LICENSE` | Apache License, Version 2.0 (unmodified text) |
| `NOTICE.md` | present, 27,721 B, `# ZCode 相关功能说明与第三方组件声明` |
| `THIRD-PARTY-NOTICES.md` | present, 1,975,825 B |
| Tracked files at HEAD | 6,973 |
| Branches / tags / releases | 1 / 0 / 0 |

Drift check: the expected anchor at task start was also `872ad96` with tree `d185a9a`. **No drift
occurred before or during the freeze.** `872ad96` is therefore both the first-public-source anchor and
this round's frozen baseline; there is no `AUDIT_START_HEAD` ≠ `AUDIT_END_HEAD` split to report.

## Public history

Two commits:

| Commit | Date (+0800) | Author | Subject | Files |
|---|---|---|---|---|
| `77432b6dbf9f70176ced3f4dcdc25f851c3acb2d` | 2026-09-20 20:06:58 | `zRzRzRzRzRzRzR` | `Initial commit` | 0 |
| `872ad960de7ec172591f7e1952f7849229f94521` | 2026-09-21 05:14:32 | `wuweiqi` | `feat: open source` | 6,973 |

The first commit's tree is `4b825dc642cb6eb9a060e54bf8d69288fbee4904` — git's **empty tree** — and it
contains zero files. The second commit adds all 6,973 tracked files at once.

**The public repository history begins with a source code drop.**

**Explicitly not claimed.** This is not a complete development history. Nothing in this history shows
when the audited `repo-snapshot` / Repo Wiki subsystem entered or left the product, who added or
removed it, or what internal decisions were involved. Those remain **UNKNOWN**. This audit does not
infer them from the two-commit history, and no statement in this directory should be read as doing so.

## Layout at the frozen revision

Top level: `apps/` (`zcode-cli`), `packages/` (`client`, `desktop`, `formal-proof`,
`model-option-map`, `provider`, `provider-node`, `rpc`, `server`, `services`, `shared`, `ui`, `web`,
`zcode-cua`, `zcode-server-cli`), `config/`, `harness/`, `patches/`, `public/`, `scripts/`,
`third-party/`, plus `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `THIRD-PARTY-NOTICES.md`, `DESIGN.md`,
`AGENTS.md`, `CONTEXT.md`, `README.md`, `README.en.md`, `mise.toml`, `architecture-policy.yaml`.

`packages/services/src/` holds 47 subsystem directories. **`repo-snapshot` and `repo-wiki` are not
among them.** So are `bots`, `cloud-content`, `marketing-touch` and `output-style` — see below.

## Honest disclosure: the tree is not a complete mirror of the shipped build

Because it bears directly on how the corroboration must be phrased, this is stated here rather than
buried: **42 workspace modules present in the shipped 3.14.0 server bundle have no counterpart in the
published tree** — `services/src/bots/**` (26), `services/src/cloud-content/**` (3),
`services/src/marketing-touch/**` (3), `services/src/output-style/**` (2),
`services/src/session/sessionModeOptions.ts` (1), and seven `shared/src/*.ts` files.

None of the 42 is a repo-snapshot or Repo Wiki module. They are unrelated feature clusters. The
vendor's own `NOTICE.md` §四 states that the repository does not promise to provide all functions of
the official product and that the actually released source code and build artifacts govern
(`[OFFICIAL-SOURCE-DOCUMENTATION]`).

Two consequences, both recorded rather than smoothed over:

1. **"Absent from the published tree" is weaker on its own than it would be for a complete drop** —
   a subsystem could in principle be unpublished rather than removed.
2. **That gap does not carry the conclusion here**, because the conclusion rests primarily on the
   shipped 3.14.0 *bundles*, which are independent of the source publication and which contain zero
   repo-snapshot modules and zero old symbols. The tree *agrees* with them; it is not the only
   witness. Structural details and the calibration control:
   [SOURCE-BINARY-MAPPING.md](SOURCE-BINARY-MAPPING.md).

## What the published source is useful for in this round

1. **Exact-symbol and exact-path confirmation** — 20 symbols, 42 module names, 4 paths, all absent
   ([SOURCE-CORROBORATION.md](SOURCE-CORROBORATION.md) §1–§2).
2. **Feature-cluster confirmation** — no Repo Wiki cluster under any searched name, including 仓库百科
   (§3).
3. **Surviving-host confirmation** — `zcodeAgentService.ts` and the desktop host module exist with
   none of the audited hook symbols (§4).
4. **Attribution confirmation** — the residual OSS/upload vocabulary resolves to the feedback
   attachment path, exactly as the binary audit attributed it (§5).
5. **A structural test with a positive control** — the same module-set method recovers the subsystem
   from the old bundle and finds nothing in the new one (§7).
6. **A build** — the tree builds a 3.14.0 server bundle with 100% source-complete module set and the
   same zero profile for all 22 old symbols ([BUILD-CORRESPONDENCE.md](BUILD-CORRESPONDENCE.md)).

## Evidence class

`[CONFIRMED-OFFICIAL-SOURCE]` for repository identity, revision, history, layout, hashes and file
counts. Vendor-authored prose (`NOTICE.md`, `README.md`, docs) is `[OFFICIAL-SOURCE-DOCUMENTATION]`
and is not treated as runtime proof.
