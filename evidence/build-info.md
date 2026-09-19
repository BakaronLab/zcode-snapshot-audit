# Build Info

## Desktop application (Electron)

- Install layout: `/opt/ZCode/` (Linux/WSL install observed); the Windows side runs the same application from the Windows filesystem.
- `app.asar`: 307,138,103 B, mtime 2026-09-04 16:08:01 +0800.
- Electron executable: 206,036,184 B, mtime 2026-09-04 16:06:22 +0800.
- Installer metadata (NSIS resources on the Windows side) reports product version strings 1.0.0.0 / 6.0.0.0 (installer metadata, not a build id).
- `app-update.yml` pointed at `http://localhost:8081` — an internal/intranet distribution endpoint; no public update channel was identifiable from the client.
- The desktop bundle contains the same repo-snapshot capture logic as the server bundle (excerpt 32) and the telemetry endpoints (evidence/telemetry-map.md).

## Server bundle (WSL side)

- `~/.zcode/server/zcode-server.cjs`: 13,409,418 B, mtime 2026-09-17 20:49 +0800 — auto-updates **independently** of the desktop app.
- A separate Windows-side `~/.zcode/server/` bundle was not present; on Windows the desktop-embedded runtime performs the equivalent role (host processes visible in logs).
- The bundle embeds original module-path comments (e.g. `// ../services/src/repo-snapshot/repoSnapshotScanner.ts`), identifying the subsystem layout: scanner, hasher, pending manager, upload client/worker, global-configs extra, disk quota.

## Local artifact layout (both machines)

```
~/.zcode/v2/checkpoints/<workspace-id>/   workspace-id = first 12 hex of sha256(workspacePath)
    state.json                            lastAcceptedManifestHash, lastCompressedSize, failureCount
    manifests/<sha256>.json               {schema, workspaceKey, createdAt, files:[{path,sizeBytes}]}
    extra-manifests/<sha256>.json         global-config group listing
~/.zcode/v2/setting.json                  repoSnapshotIndexingEnabled / …UserConfigured
~/.zcode/v2/telemetry-state.json          deviceMid
~/.zcode/v2/logs/YYYY-MM-DD.log           application logs
~/.zcode/cli/db/db.sqlite                 local CLI session store (~700 MB)
```

The workspace-id derivation was verified: `sha256(workspacePath)[:12]` matches every observed directory name, which also proves the workspace key at capture time was the raw path (`workspaceIdentity` empty, F-030).

## Windows-side data-size telemetry file

`AppData/Roaming/ZCode/zcode-data-size-telemetry.json` contains only a `lastReportedAt` timestamp (sanitized copy: evidence/sanitized-logs/zcode-data-size-telemetry.json). What it reports, and to where, is UNKNOWN.
