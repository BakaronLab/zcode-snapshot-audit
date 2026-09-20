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

## Version-history questions that cannot be answered locally

- When the snapshot subsystem first appeared (no product git history/changelog on the machine).
- Whether any prior build behaved differently (only the hashed builds above were observed).
- Whether any fix exists or is planned.

See REPORT.md → *Tested Build* and docs/known-unknowns.md.
