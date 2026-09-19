# Methodology

## Goal and stance

This is a forensic, reproducibility-first audit of client-side data flow in a locally installed ZCode build. Facts are separated from inference by explicit evidence classes; where a statement cannot be supported by local evidence it is marked UNKNOWN. Vendor documentation, UI copy, and marketing text were **not** used as technical evidence.

## Evidence sources

| Source | Used for |
|---|---|
| WSL server bundle `~/.zcode/server/zcode-server.cjs` (13.4 MB minified Node bundle) | snapshot subsystem logic, endpoints, encryption, filters |
| Desktop bundle `/opt/ZCode/resources/app.asar` (307 MB) | desktop-side equivalents, telemetry endpoints, remote-workspace schemas |
| `~/.zcode/v2/checkpoints/**` (state.json, manifests, extra-manifests, both machines) | capture/upload-completion evidence, archive contents, statistics |
| `~/.zcode/v2/setting.json` (both machines), `telemetry-state.json` | gate/setting analysis, device identifier |
| `~/.zcode/v2/logs/*.log` (both machines) | logging behavior |
| `~/.zcode/cli/db/db.sqlite` (read-only, `mode=ro&immutable=1`) | local session storage schema/counts |
| Live runtime observation | build consistency, audit-session isolation |

## Chain of custody

1. Raw originals were **never modified**. All inspection was read-only.
2. Program artifacts were hashed with SHA-256 before any analysis (evidence/artifact-hashes.md).
3. Sanitized derivatives were produced by: parse → recursive redact → verify → publish. The sanitizer replaces: usernames (`/home/<USER>/`, `C:\Users\<USER>\`, `X:\workspace\`), real project names (`project-a`…`project-g`), workspace ids (`ws-a`…`ws-g`), manifest hashes (`<MANIFEST_HASH>`), device ids (`<DEVICE_ID>`), git branch/remote/worktree names, pack/object ids, and per-config content hashes.
4. An automated assertion scans every published file for the withheld identity strings and for any 16+ hex-digit residue inside sanitized derivatives; the publication scan is `scripts/secret-scan.sh` + `scripts/scan-sensitive-paths.py`.

## Evidence classes

- **[CONFIRMED-CODE]** — line-numbered excerpt from the audited bundle. Excerpts are truncated to 240 columns (minified bundle lines are extremely long); line ranges are verifiable with the reproduction commands.
- **[CONFIRMED-LOCAL-ARTIFACT]** — local artifact produced by the audited build (state, manifest, log, DB schema, config). Published only as sanitized derivatives.
- **[CONFIRMED-RUNTIME]** — observed behavior of the running system on the audited machine during the audit window.
- **[INDEPENDENT-CORROBORATION]** — third-party report consistent with local evidence; never a substitute for it.
- **[INFERRED]** — strong structural support without direct runtime/server proof.
- **[UNKNOWN]** — not determinable from local evidence.

## Code excerpt provenance

Every excerpt records: source artifact, line range, extraction date, and the finding(s) it supports (evidence/sanitized-code-references.md). Only minimum-necessary excerpts are published; the bundles are not redistributed.

## Limitations

- **No network capture.** "Upload reaches OSS" is established by code path + the client's own upload-success state artifacts, not by packet capture. The actual OSS host is runtime-delivered and was not observed.
- **Server side is a black box.** Nothing here establishes server-side storage, indexing, retention, ACLs, or use.
- **Single machine, single build.** Findings apply to the hashed build; other builds may differ (the server bundle auto-updates independently).
- **Minified code.** Symbol names in the bundles are compiler outputs; original module names come from embedded source-path comments (`// ../services/src/repo-snapshot/...`).
- **mtime-based build anchoring** has the residual caveat noted in F-034.

## Tooling

bash, grep, sed, python3 (standard library only), sqlite3 (read-only), sha256sum, strings. No proprietary tooling; no network access required.
