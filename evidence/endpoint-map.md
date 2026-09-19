# Endpoint Map

All endpoints below are from static analysis of the audited bundles ([CONFIRMED-CODE]). No credentials, policies, signatures, or tokens are reproduced here.

## ZCode API (snapshot subsystem)

| Property | Value |
|---|---|
| Default origin | `https://zcode.z.ai` (production), `https://zcode.chatglm.site` (test) — server.cjs ~202210-202211 |
| Origin override | environment variables (`ZCODE_BASE_URL`, `ZCODE_PRODUCTION_BASE_URL`, `ZCODE_TEST_BASE_URL`, `ZCODE_ENDPOINT_ORIGIN`) and settings |
| Endpoint | `GET {origin}/api/v1/snapshot/upload-credential?workspace_id=<id>` |
| Auth | `Authorization: Bearer <token>` (OAuth/JWT held by the client) |
| Called by | `getUploadCredential` (excerpt 22), invoked from the capture pipeline (excerpt 24 flow) |
| Only snapshot path | `/api/v1/snapshot/upload-credential` is the **only** `/api/v1/snapshot/*` path in the bundle — no download/restore endpoint exists |

### Credential response (enforced fields, excerpt 03)

```
oss.host                      object-storage host (runtime-delivered)
oss.path                      object key
oss.policy / x_oss_signature / x_oss_signature_version /
x_oss_credential / x_oss_date / x_oss_security_token     OSS PostObject policy fields
encryption.public_key         RSA public key (SPKI PEM) for key wrapping
encryption.key_version
encryption.algorithm          enforced === "RSA-OAEP-256"  (~312454)
snapshot.snapshot_id          server-assigned snapshot id
max_size                      optional per-snapshot cap (client default 2 GB, excerpt 31)
callback                      optional callback descriptor
```

## Object storage upload (Aliyun OSS PostObject)

| Property | Value |
|---|---|
| URL | `POST {credential.oss.host}` — host known only at runtime from the credential response |
| Form encoding | multipart/form-data |
| File field | `repo-snapshot.tar.gz.enc` (excerpt 04) |
| Other fields | `success_action_status`, `policy`, `x-oss-signature`, `x-oss-signature-version`, `x-oss-credential`, `x-oss-date`, `key` (= `oss.path`), `x-oss-security-token`, `attribution`, `callback` |
| Alternative | `uploadPutObject` PUT channel exists (~312587); main path is the form POST |
| Callback fields (client fills) | `update_type` (full/incremental), `checksum` = `sha256:<plaintext snapshot hash>`, `encrypted_aes_key` (= wrapped data key), `x:base_snapshot_id`, attribution (`sessionId`, `queryId`, `requestId`, `failureCount`, `captureStage`) |

## Other client endpoints (context, non-snapshot)

- LLM inference traffic goes to the configured model provider endpoints (e.g. `api.z.ai` / `open.bigmodel.cn` / `chat.z.ai` families) — ordinary assistant traffic: prompts and tool-read file contents as context.
- Telemetry: Aliyun ARMS RUM `https://sdk.rum.aliyuncs.com`; Aliyun SLS log endpoint `proj-xtrace-…cn-beijing.log.aliyuncs.com` (evidence/telemetry-map.md).
- WebSocket endpoints (`wss://`): **0 hits** in the server bundle.

## Absence findings

- `restore|download` combined with snapshot: 0 hits in both bundles (one-directional collection).
- The upload activity produces **no log lines** (F-033).
