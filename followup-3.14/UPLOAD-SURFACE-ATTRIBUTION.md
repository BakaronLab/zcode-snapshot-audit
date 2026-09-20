# Upload-surface attribution — what the residual OSS/upload vocabulary belongs to

**Question:** the new build still contains `upload-credential`, `oss.host`, `x-oss-*` and
`success_action_status`. Do these belong to the audited repo-snapshot pipeline, or to something else?

**Answer: something else.** Every surviving occurrence is attributable to `services/src/feedback/*`
— user-initiated **feedback attachment** upload — plus generic HTTP form code. The repo-snapshot
credential endpoint constant and its endpoint string are gone.

## Full attribution in the new server bundle

| Token | NEW hits | Owner module | Context |
|---|---|---|---|
| `upload-credential` | 2 | `services/src/feedback/feedbackHttpClient.ts` | `POST /feedback/attachment/upload-credential` (request builder + response summarizer) |
| `oss.host` | 1 | `services/src/feedback/feedbackHttpClient.ts` | `new URL(credential.oss.host)`, then an HTTP request |
| `x-oss-security-token` | 1 | `services/src/feedback/feedbackHttpClient.ts` | form field `credential.oss.x_oss_security_token` |
| `x-oss-*` (all) | 5 | `services/src/feedback/feedbackHttpClient.ts` | `x-oss-signature-version`, `x-oss-credential`, `x-oss-security-token`, `x-oss-date` |
| `success_action_status` | 1 | `services/src/feedback/feedbackHttpClient.ts` | OSS PostObject form field |
| `security-token` | 1 | `services/src/feedback/feedbackHttpClient.ts` | as above |
| `PostObject` | **0** | — | the audited `buildObjectUploadTarget` / `uploadPostObject` symbols are gone |
| `repo-snapshot.tar.gz.enc` | **0** | — | audited multipart filename gone |
| `encrypted_aes_key` | **0** | — | audited callback field gone |
| `/api/v1/snapshot/upload-credential` | **0** | — | audited endpoint string gone |

## Call chain: what the residual actually does

```
user submits feedback
  → feedbackService
    → feedbackHttpClient.request("/feedback/attachment/upload-credential", {method:"POST"})
      ← credential { oss: { host, x_oss_credential, x_oss_security_token, x_oss_date, signature, policy } }
    → uploads the user's attachment file to credential.oss.host
      with OSS PostObject form fields (x-oss-*, policy, signature, success_action_status)
```

## USER-INITIATED FEEDBACK ATTACHMENT vs OLD AUTOMATIC REPO SNAPSHOT

| Property | Audited repo-snapshot pipeline (removed) | 3.14.0 feedback pipeline (present) |
|---|---|---|
| Trigger | **automatic**, every capture-eligible prompt + task completion | **user explicitly submits feedback** |
| Payload | workspace file tree + `.git/**` + nine global config groups + prompt text | **the attachment file the user selected** |
| Archive | `tar` + gzip, `files/**`, `meta/prompt.json`, `meta/manifest.json`, `extra-files/**` | none |
| Manifest | `meta/manifest.json` with per-file entries, delta vs base | none |
| Encryption | AES-256-CTR + RSA-OAEP-SHA256 wrapped data key | none of these symbols present |
| Size limit | `REPO_SNAPSHOT_MAX_FILE_BYTES` (1 MB, bypassed for `.git`) | `FEEDBACK_MAX_ATTACHMENT_BYTES = 100 * 1024 * 1024` |
| Local staging | `~/.zcode/v2/checkpoints/.../pending/*.tar.gz.enc` | feedback temp dir under the feedback root |
| Endpoint path | `/api/v1/snapshot/upload-credential` | `/feedback/attachment/upload-credential` |

These are different subsystems with different triggers and different payloads. The feedback path
cannot carry a workspace snapshot: it uploads one user-selected file and performs no workspace
enumeration, no archiving and no manifest construction.

## Old-side split (why the count drops 5 → 2 rather than to 0)

| OLD hit | Module | Status in 3.14.0 |
|---|---|---|
| 1 | `services/src/providers/api/apiEndpoints.ts` — snapshot credential URL constant | **REMOVED** |
| 1 | `services/src/repo-snapshot/repoSnapshotUploadCredentialDiagnostics.ts` | **REMOVED** (module gone) |
| 2 | `services/src/feedback/feedbackHttpClient.ts` | survives |
| 1 | `services/src/feedback/compactLogArchive.ts` | survives |

## Desktop side

NEW desktop `upload-credential` = 3, `oss.host` = 1, `x-oss-*` = 5 — the same feedback footprint
(the desktop bundles the same services layer). No `repo-snapshot.tar.gz.enc`, no `PostObject`, no
`encrypted_aes_key`, and no `/api/v1/snapshot/upload-credential` on either side.

## A second surviving upload path, named explicitly

Conversation sharing is a second user-initiated upload path that survives and must not be mistaken
for a successor to the removed subsystem:

- `services/src/conversation-share/*`, `POST /shares/preparations/{id}/artifacts`, multipart form
  with file bytes;
- it reads workspace-contained files through a realpath-checked artifact source;
- its only directory reads target a `.zcode-share` subdirectory of the workspace — it is **not** a
  repository walk;
- it is **semantically unchanged** old→new: per-module rename-invariant string sets are equal and
  the key identifiers are stable (`/shares/preparations` 3→3, `conversationShareArtifactSource` 2→2,
  `isInsideWorkspace` 5→5, `conversationShareHttpClient` 1→1, `conversationShare` 90→90,
  `uploadArtifact` 2→2), and it is present in the old bundle that the published findings describe.

Neither surviving upload path is new, and neither is a rewrite of the removed subsystem.

## Conclusion

The residual upload/OSS surface in 3.14.0 is **feedback attachment upload** (and separately
conversation-share artifact upload), user-initiated features distinct from the audited subsystem in
trigger, payload, staging and cryptography. **The audited repo-snapshot upload pipeline
(`buildObjectUploadTarget`, `uploadPostObject`, `uploadPutObject`, its multipart filename and its
callback fields) is not present.**

**Stated plainly, to avoid the overclaim:** OSS upload has **not** been completely removed from
ZCode. It survives for user-initiated features. What is absent is the audited **automatic
repo-snapshot** upload path.

**Limitation.** This is a static attribution. It does not establish what the feedback or
conversation-share features send beyond their declared payloads, nor any server-side handling —
server-side behavior remains **UNKNOWN**. It also does not prove the audited endpoint is unreachable
from some other client version.
