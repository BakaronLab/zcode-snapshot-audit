# Runtime Observations

Dynamic observations made on the audited machine during the audit window (2026-09-19). All times +0800. [CONFIRMED-RUNTIME] unless noted.

## Build consistency at audit time

- `zcode-server.cjs` (WSL): mtime 2026-09-17 20:49, SHA-256 `e4150318…` — unchanged since the build identification, so all line-number citations remained valid throughout the audit.
- `app.asar`: mtime 2026-09-04 16:08, SHA-256 `e260f753…` — unchanged.

## Capture activity around the audit

- No files in either machine's `~/.zcode/v2/checkpoints/` were created or modified after the audit start; no state exists for the audit workspace itself.
- The WSL server bundle has not run since 2026-09-17 20:47 (its per-day log ends there; no 2026-09-18/19 WSL server logs exist). Audit sessions ran through the CLI runtime, not the server bundle.
- The Windows-side desktop application was running during the audit (logs written through 2026-09-19 12:44).
- The latest observed capture in any state file is the Windows-side 2026-09-17 20:57 record (F-034).

## CLI runtime isolation

- `/opt/ZCode/zcode` (invoked as `zcode`): `strings` search finds **0** occurrences of `upload-credential` and RepoSnapshot uploader symbols; CLI application logs for 2026-09-19 contain **0** repoSnapshot capture references; no checkpoints directory exists under the CLI data root (F-032).

## Settings state during audit

| Machine | `repoSnapshotIndexingEnabled` | `…UserConfigured` | settings mtime |
|---|---|---|---|
| WSL | `true` | `true` | 2026-09-19 03:10 |
| Windows | `false` | `true` | 2026-09-19 12:25 |

(sanitized copy: [sanitized-logs/settings-extract.txt](sanitized-logs/settings-extract.txt)). Per F-022, neither value gates capture/upload in the audited server code.

## Log surface checks

- Per-file grep across all WSL (7 files) and Windows (13 files) application logs: **0** lines from the snapshot subsystem (capture/upload/credential). All `repoSnapshot` hits are full-settings JSON dumps written by `settingService` (F-033). Output: [sanitized-logs/upload-logging-absence-proof.txt](sanitized-logs/upload-logging-absence-proof.txt).
- `grep -i snapshot` alone is misleading: it matches unrelated identifiers such as `usage-stats.getEntitlementSnapshot` and a `snapshot: {` dump key.

## Checkpoint directory census

| Machine | state.json | manifests + extra-manifests | `.enc`/tar/tmp residue |
|---|---|---|---|
| WSL | 6 | 28 | 0 |
| Windows | 1 | 3 | 0 |

Consistent with post-success cleanup (F-021) and with failures being retried until the upload succeeded (7/7 states carry the client-recorded upload-success marker `lastAcceptedManifestHash`).

## Local SQLite (read-only inspection)

`~/.zcode/cli/db/db.sqlite` (~700 MB): 24 tables; message 24,286 rows; part 104,288; tool_usage 29,992; model_usage 21,533; session 559. Schema: [../sqlite-schema.txt](../evidence/sqlite-schema.txt). Opened with `mode=ro&immutable=1`; original untouched.
