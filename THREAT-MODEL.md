# Threat Model

Scope: client-side behavior of the audited ZCode build. This document describes what the observed data flows protect against and what they do not. It makes no claims about server-side behavior or intent.

## Assets leaving the machine (confirmed)

- Workspace file contents (source code and everything else scanned), including the **entire `.git` directory** (regular files; the symlink exclusion applies first): history objects, pack files (any size), reflog (`logs/HEAD`, which contains commit metadata such as author identity), `config` (which can contain remote URLs, potentially with embedded credentials), `index`, `lost-found`, worktree metadata.
- The full text of every user prompt.
- Global agent configuration: `mcp.json`, `hooks.json`, `memory.json`, `instructions.json`, `subagents.json`, `skills.json`, `commands.json`, `plugins.json`, `settings.behavior.json` — redacted only by key-name pattern.
- Attribution metadata (session/query/request ids, capture stage, failure count) and the plaintext snapshot checksum.
- Separate channel: device identifier (`deviceMid` via `X-Device-Mid`) and telemetry endpoints (ARMS RUM, SLS).

## Actors and protections

| Actor | Protected? | Why |
|---|---|---|
| Passive network observer between client and OSS | **Yes** | AES-256-CTR encrypted archive; TLS for control traffic |
| Aliyun OSS / anyone with object access but no key | **Yes** | data key is not stored with the object |
| **The ZCode server** | **No** | it issues the wrapping RSA public key and receives the wrapped data key in the OSS callback — it possesses the decryption capability by design |
| Anyone with access to ZCode server-side storage | **No (capability)** | if the server (or its key holder) decrypts, plaintext is available to that environment |
| Local other-user processes on the same machine | Partially | snapshots transit through user-writable `pending/` directories briefly; post-success they are deleted |

## Consequences of `.git` inclusion (F-007…F-010)

- Secret filtering is **ineffective inside `.git`**: any secret that exists in historical commits (deleted files, old configs), in `.git/config` remote URLs, or in `lost-found` is inside the upload scope whenever a snapshot is captured.
- The reflog exposes project history patterns (branch names, timestamps, author identities inside log entries).
- Size limits do not apply, so full history (potentially gigabytes) is in scope.

## Consequences of key-name-only config redaction (F-013)

- Credentials stored under key names like `LLM_KEY`, `MY_AUTH`, `PROVIDER_CRED`, `MODEL_ACCESS`, or inside nested values (e.g. connection strings, URLs with tokens) are **not** redacted by the audited mechanism. Conversely, `CUSTOM_PROVIDER_CREDENTIAL` is redacted. Whether any concrete credential left the machine depends on the user's own config contents and key names — this audit does not claim any specific key was uploaded.

## What would reduce exposure (see docs/mitigation.md)

- `repoSnapshotIndexingEnabled=false` does **not** stop capture/upload in the audited build (F-022).
- Making the checkpoints state directory non-writable blocks artifact creation on the audited layout (proposed mitigation, not verified — root privileges were unavailable during the audit).
- Avoiding logged-in use of the client for sensitive workspaces avoids the capture path entirely (the sidecar requires a token and server credential).
- The `workspaceIdentity` gate (F-031) suppresses prompt-stage capture for remote sessions, but its practical coverage was not verified — do not rely on it as a control.

## Explicitly out of scope

- Server-side retention, indexing, model-training use, employee access, or any intent attribution.
- Whether any particular snapshot was ever decrypted or read.
- Security of the OSS bucket itself (host not locally observable).
