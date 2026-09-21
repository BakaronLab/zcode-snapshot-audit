# Timeline

All times local (+0800). Workspace identities anonymized (ws-a…ws-g ↔ project-a…project-g mapping is local-only).

## Build timeline

| Date | Event | Evidence |
|---|---|---|
| 2026-09-04 16:06 | Desktop Electron executable built/installed (mtime) | evidence/build-info.md |
| 2026-09-04 16:08 | `app.asar` mtime (desktop build) | evidence/build-info.md |
| 2026-09-17 20:49 | WSL server bundle `zcode-server.cjs` mtime (independent auto-update, 13,409,418 B) | evidence/build-info.md |

## Observed capture/upload timeline (from local state artifacts)

| Timestamp | Workspace | Notes |
|---|---|---|
| 2026-09-08 06:12 | ws-g | last compressed size recorded; upload-success marker present |
| 2026-09-08 14:12 | ws-b | upload-success marker present; 3 extra-manifests retained |
| 2026-09-10 12:52 | ws-f | upload-success marker present |
| 2026-09-10 16:41 | ws-d | upload-success marker present |
| 2026-09-10 16:55 | ws-e | upload-success marker present |
| 2026-09-11 15:37 | ws-a | upload-success marker present; largest observed manifest (5,067 files, 82.7% `.git/**`) |
| 2026-09-17 20:57 | ws-c (Windows side) | **post-dates the audited desktop build (2026-09-04)** and anchors the observed capture behavior to the audited artifacts (F-034) |

All 7 state files contain the client-recorded upload-success marker `lastAcceptedManifestHash` (F-020). `failureCount` values 1–3 indicate retry activity (F-021).

## Audit timeline

| Date | Event |
|---|---|
| 2026-09-19 by 03:10 | WSL `setting.json` last written; `repoSnapshotIndexingEnabled: true` (state at audit time) |
| 2026-09-19 morning | Owner discovers the behavior (third-party report), sets Windows-side `repoSnapshotIndexingEnabled: false` (settings file mtime 12:25 observed) |
| 2026-09-19 ~12:30 | Audit session 1: static analysis + artifact fixation (read-only); no mitigation applied; no push performed by the audit session |
| 2026-09-19 12:36+ | Audit session 2 (this repository): build-consistency check (hashes unchanged), gap verification (remote/WSL gating, redaction escape test, SQLite counts), sanitization, publication pipeline. **No new checkpoint artifacts were created during either audit session** (F-032) |

## Official-source timeline

| Date | Event | Reference |
|---|---|---|
| 2026-09-20 20:06:58 (+0800) | Official repository `zai-org/ZCode` created; public history opens with `77432b6d` `Initial commit`, whose tree is git's empty tree and which contains **0 files** | [evidence/official-source-anchor.md](followup-open-source/evidence/official-source-anchor.md) |
| 2026-09-21 05:14:32 (+0800) | `872ad960de7ec172591f7e1952f7849229f94521` `feat: open source` — 6,973 files added in a single commit. Public history therefore **begins with a source code drop** | [evidence/official-source-anchor.md](followup-open-source/evidence/official-source-anchor.md) |
| 2026-09-21 | Official ZCode source publication observed; frozen as this round's baseline (tree `d185a9a893c00d51fc3fe51fe7371b9eea7de143`, `package.json` version `3.14.0`, license `Apache-2.0`). No drift from the expected `872ad96` anchor | [followup-open-source/](followup-open-source/README.md) |
| 2026-09-21 | Source-level corroboration of the 3.14 binary regression published: audited repo-snapshot / Repo Wiki implementation not identified in the frozen source tree; feedback attachment upload confirmed as the residual upload surface's owner | [followup-open-source/SOURCE-CORROBORATION.md](followup-open-source/SOURCE-CORROBORATION.md) |

The public history carries no development history, so it does **not** answer the version-history
questions below — in particular it does not show when the audited subsystem entered or left the
product. The frozen shipped-build commit recorded by the 3.14 desktop payload, `a1328db1`, is not an
object in the official repository, so exact source identity is **not** established
([followup-open-source/SOURCE-BINARY-MAPPING.md](followup-open-source/SOURCE-BINARY-MAPPING.md)).

## Version-history questions that cannot be answered locally

- When the snapshot subsystem first appeared (no product git history/changelog on the machine).
- Whether any prior build behaved differently (only the hashed builds above were observed).
- Whether any fix exists or is planned.

See REPORT.md → *Tested Build* and docs/known-unknowns.md.
