# Artifact Hashes

SHA-256 of the audited **program artifacts** (safe to publish — they identify the build, not the user).

| Artifact | Size (B) | mtime (+0800) | SHA-256 |
|---|---|---|---|
| Desktop app bundle `app.asar` | 307,138,103 | 2026-09-04 16:08:01 | `e260f7537c7e173b21cbb54b42800ca320da14d8f2244b297b71b2a3a2d90081` |
| Desktop Electron executable `zcode` | 206,036,184 | 2026-09-04 16:06:22 | `7f7881d04a9119cd865abe9e45d3cce510eab82a40cab823d7b243f7daf0b03b` |
| WSL server bundle `zcode-server.cjs` | 13,409,418 | 2026-09-17 20:49 | `e4150318eac90ad5e74ce99a7d8f891c598a4057c0e061570702e4f778c6183c` |

Recompute on your machine with `bash scripts/hash-zcode-artifacts.sh` — if your `zcode-server.cjs` hash matches, every line-number citation in this repository applies verbatim to your installation.

Not published: SHA-256 of the raw private artifacts (checkpoint state/manifests, logs, DB). Their hashes are recorded in a local-only index because the artifacts themselves contain private paths; hashes of private content are not needed by third parties to verify any published claim (all published claims are verifiable against *your own* installation or against the sanitized derivatives' structure).
