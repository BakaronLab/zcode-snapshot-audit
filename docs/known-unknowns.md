# Known Unknowns

Things this audit could **not** determine from local evidence. Each is a statement of absence of evidence, not evidence of absence.

1. **Actual OSS object host/bucket.** Delivered at runtime in the upload credential; no network capture was performed, and no static host exists in the artifacts. Which bucket receives snapshots, and under which account, is UNKNOWN.
2. **Server-side handling of uploaded snapshots.** Storage layout, indexing, retention, access control, internal use — all UNKNOWN. The envelope design gives the server the *capability* to decrypt (F-017/F-019); whether and how it exercises it is UNKNOWN.
3. **Whether any concrete secret ever left the machine.** The filter-bypass and key-name-only redaction mechanisms are confirmed (F-009/F-010/F-013); whether any specific credential or secret was actually uploaded depends on private content and is UNKNOWN.
4. **RUM/SLS payload composition.** Endpoints and the `X-Device-Mid` header are confirmed; what the RUM SDK actually reports per event is UNKNOWN (not reconstructed from the minified SDK).
5. **Practical remote-session capture behavior.** The `workspaceIdentity` gate exists in code (F-031), but no remote-session workspace existed on the audited machine; whether current builds suppress capture for SSH/WSL-remote sessions in practice is UNKNOWN.
6. **First-introduced version and later-build status.** At the time of the original audit, no product changelog or source history was available locally, so when this behavior was introduced and whether a later build would change it were UNKNOWN. The subsequent ZCode 3.14.0 follow-up found the audited client-side repo-snapshot / Repo Wiki subsystem removed in the exact 3.14.0 artifacts examined there. The first-introduced version, vendor intent, and server-side handling remain UNKNOWN.
7. **Desktop-side consumption of `repoSnapshotIndexingEnabled`.** In the audited bundles, 13 asar occurrences are schema/normalization/key-list contexts and no gating predicate was identified; whether some desktop-side code path consumes the setting in a way that affects behavior is UNKNOWN (none was found).
8. **`zcode-data-size-telemetry.json` uploader.** The file exists locally with a `lastReportedAt` timestamp; what reports it and where is UNKNOWN.
9. **Non-git workspaces.** Enumeration starts from `git ls-files` (F-005); how the scanner treats non-git directories end-to-end was not exercised at runtime (no artifacts exist for one).
10. **Cross-platform parity.** Only the WSL server bundle and desktop bundles on one machine were audited; a native macOS/Linux desktop build may differ.
