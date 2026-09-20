# Control surfaces — why the zeros are meaningful

A delta report that shows "everything went to zero" invites an obvious objection: maybe the
comparison itself is broken — re-bundling, minification, a platform change, or a different packaging
pipeline could make *any* string disappear. This file records the controls that rule that out.

## The controls

| Symbol | OLD server 3.12.3 | NEW server 3.14.0 | OLD desktop 3.11.2 | NEW desktop 3.14.0 | Verdict |
|---|---|---|---|---|---|
| `checkpoint@zcode.local` | 2 | **2** | 2 | **2** | CONTROL_SURVIVES |
| `refs/zcode/checkpoints` | 2 | **2** | 1 | **1** | CONTROL_SURVIVES |
| `sdk.rum.aliyuncs.com` (ARMS RUM) | 0 | 0 | 8 | **8** | CONTROL_SURVIVES (byte-identical) |
| `log.aliyuncs.com` (SLS) | 0 | 0 | 2 | **2** | CONTROL_SURVIVES (byte-identical) |
| `deviceMid` | 54 | 62 | 90 | 116 | CONTROL_SURVIVES (grew) |
| `X-Device-Mid` | 5 | 6 | 6 | 7 | CONTROL_SURVIVES (grew) |
| `multipart/form-data` | 57 | **57** | 155 | 153 | CONTROL_SURVIVES |

### Why these particular ones

- **`checkpoint@zcode.local` / `refs/zcode/checkpoints`** are the local git checkpoint system
  (finding F-023 in the root evidence ledger). It is a *different* client subsystem that happens to
  live near the removed one in the codebase and shares the "workspace state" theme. It survives
  unchanged on both sides — so the disappearance of the snapshot subsystem is not a general
  disappearance of workspace-related client code.
- **`sdk.rum.aliyuncs.com` and `log.aliyuncs.com`** are desktop telemetry endpoints (F-025, F-026).
  They are **byte-identical** across a Linux→Windows payload change. This is the strongest available
  proof that a zero elsewhere is a real zero and not a packaging or minification artifact: the same
  file that lost every snapshot token retained these tokens exactly.
- **`deviceMid` / `X-Device-Mid`** (F-027) are a device identifier and its HTTP header. They
  survive and even grow slightly, which further shows that the delta is selective rather than a
  wholesale string loss.
- **`multipart/form-data`** is generic HTTP form encoding used by several features. Its count is
  essentially stable (57→57 server), so the disappearance of the snapshot's `PostObject` multipart
  upload is specific, not an artifact of form-encoding vocabulary vanishing.

## What the controls establish

1. The comparison is valid: strings that should survive, survive — including across the
   Linux→Windows desktop payload change.
2. The removals are **selective**: the removed cluster is precisely the repo-snapshot / Repo Wiki
   subsystem, not workspace-adjacent or upload-adjacent code in general.
3. The telemetry and local-checkpoint surfaces were **not** touched by this change. They are
   published here only as controls — this follow-up does not extend the telemetry investigation and
   makes no new claim about those endpoints.

## Limits

Controls validate the measurement, not the conclusion's scope. They show that the zeros are real
absences in the examined artifacts; they do not show what the service does — server-side behavior
remains **UNKNOWN** — and they do not exclude an equivalent implementation written with entirely
disjoint vocabulary (addressed separately by the calibrated combination test in
[../SNAPSHOT-HIT-CLASSIFICATION.md](../SNAPSHOT-HIT-CLASSIFICATION.md)).
