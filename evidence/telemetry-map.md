# Telemetry Map

Telemetry surfaces observed in the audited build, independent of the repo-snapshot system. Evidence: binary grep of `app.asar` + server bundle excerpts 16/17 ([CONFIRMED-CODE]); reproduced with `scripts/inspect-upload-endpoints.py --telemetry`.

## Confirmed surfaces

| Surface | Endpoint | Mechanism | Payload knowledge |
|---|---|---|---|
| Aliyun ARMS RUM (Real User Monitoring) | `https://sdk.rum.aliyuncs.com` | embedded RUM SDK in the desktop bundle; events gzipped locally (pako) before send | endpoint [CONFIRMED]; event field detail [UNKNOWN] |
| Aliyun SLS (log service) | `proj-xtrace-<project-id>-cn-beijing.cn-beijing.log.aliyuncs.com` | embedded endpoint constant in the desktop bundle | endpoint [CONFIRMED]; shipped content [UNKNOWN] |
| Device identifier | request header `X-Device-Mid` | `deviceMid` UUID persisted in `~/.zcode/v2/telemetry-state.json`, injected into API requests (server.cjs ~208120) | header + persistence [CONFIRMED]; sanitized artifact copy published |

## Local device identifier artifact

`~/.zcode/v2/telemetry-state.json` (sanitized copy: [sanitized-logs/telemetry-state.json](sanitized-logs/telemetry-state.json)):

```json
{ "deviceMid": "<DEVICE_ID>", "lastDailyActiveDate": "2026-09-17" }
```

## Secondary local-log observation (not a network surface)

`settingService` writes full settings JSON dumps into plaintext local log files; the dumps contain `deviceSid`, `workspacePath`, `workspacePurpose` values (evidence/sanitized-logs/upload-logging-absence-proof.txt). No key/token/secret-shaped fields were observed in sampled dumps. This is a local log-hygiene surface only.

## Explicit non-claims

- No claim is made that RUM uploads source code or workspace content — the payload composition was not reconstructed.
- No claim about the SLS endpoint's runtime content.
- The snapshot upload system is documented separately (REPORT.md → OSS Upload) and does not use these telemetry hosts.
