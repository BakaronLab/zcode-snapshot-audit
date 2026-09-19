# ZCode Snapshot Audit

This repository documents independently verifiable client-side behavior observed in a locally installed ZCode build.

It does **not** make unsupported claims about:

- server-side retention
- training usage
- model distillation
- employee access
- corporate intent

unless directly supported by evidence. Statements in this repository are labeled with evidence classes ([CONFIRMED-CODE], [CONFIRMED-LOCAL-ARTIFACT], [CONFIRMED-RUNTIME], [INDEPENDENT-CORROBORATION], [INFERRED], [UNKNOWN]) and every finding is traceable in [EVIDENCE.md](EVIDENCE.md).

ZCode is an AI coding client. The audited installation consists of a Windows desktop application (Electron, `/opt/ZCode`-style install observed on the WSL side) plus a Node.js server bundle (`zcode-server.cjs`) that runs inside the WSL environment and serves agent sessions. All findings below were reproduced on one machine against one specific build; see [REPORT.md](REPORT.md) → *Tested Build* and [evidence/artifact-hashes.md](evidence/artifact-hashes.md) for the exact hashes so you can check whether your build matches.

## Confirmed client-side behavior

The following are confirmed by direct code inspection and/or local artifacts of the audited build. This is factual client-side behavior; this repository draws no conclusions about server-side use of the data.

| # | Behavior | Evidence |
|---|---|---|
| 1 | **Workspace snapshot creation**: the client builds a complete archive of the workspace (file contents included) before every prompt and on successful task completion | [F-002](EVIDENCE.md), [F-003](EVIDENCE.md), code excerpts 07/08 |
| 2 | **`.git/` inclusion**: the entire `.git` directory — objects, pack files, reflog (`logs/HEAD`), `config`, `index`, `lost-found`, worktree metadata — is enumerated and packed | [F-005](EVIDENCE.md)–[F-009](EVIDENCE.md); manifests showing 62–90% of archive entries are `.git/**` |
| 3 | **Filter bypass**: the `.git` short-circuit runs *before* secret-path filtering, binary filtering, and the 1 MB per-file size limit; >1 MB pack files appear in real manifests | [F-009](EVIDENCE.md), [F-010](EVIDENCE.md), code excerpt 10 |
| 4 | **Prompt capture**: the full user prompt text is embedded in the archive (`meta/prompt.json` ← `params.prompt.content`) | [F-003](EVIDENCE.md), code excerpts 07/08 |
| 5 | **Global config capture**: `mcp.json`, `hooks.json`, `memory.json`, `instructions.json`, `subagents.json`, `skills.json`, `commands.json`, `plugins.json`, `settings.behavior.json` are packed into the archive | [F-012](EVIDENCE.md), code excerpt 15 |
| 6 | **Key-name-only redaction**: config values are redacted only when the *key name* matches `SENSITIVE_KEY_PATTERN`; non-matching key names (and values embedding secrets) pass through unredacted (synthetic escape test included) | [F-013](EVIDENCE.md), code excerpt 15, `evidence/sanitized-logs/` |
| 7 | **Envelope encryption**: archive is gzip + AES-256-CTR with a random data key; the data key is wrapped with a **server-provided RSA public key** (RSA-OAEP-SHA256) | [F-016](EVIDENCE.md), [F-017](EVIDENCE.md), code excerpt 09 |
| 8 | **Upload credential endpoint**: `GET {origin}/api/v1/snapshot/upload-credential` (default origin `https://zcode.z.ai`) returns OSS host/policy/signature/security-token, the RSA public key, and a snapshot id | [F-014](EVIDENCE.md), [F-015](EVIDENCE.md), code excerpts 01–03, 22 |
| 9 | **OSS upload**: the encrypted archive is POSTed as a multipart form to a runtime-delivered Aliyun OSS host; the OSS callback returns `update_type`, `checksum` (plaintext sha256), `encrypted_aes_key`, `base_snapshot_id`, and attribution metadata to the server | [F-018](EVIDENCE.md), [F-019](EVIDENCE.md), code excerpt 04 |
| 10 | **Upload-completion state evidence**: all 7 locally observed workspace state files contain `lastAcceptedManifestHash` — the client's own marker, written only after its upload path reports success (server-side processing not independently observable); local `pending` artifacts are deleted after success (no `.enc` residue) | [F-020](EVIDENCE.md), [F-021](EVIDENCE.md) |
| 11 | **Setting does not gate upload**: `repoSnapshotIndexingEnabled` appears in the server bundle only as schema/normalization/uploaded-key-list entries; the sidecar is instantiated unconditionally; the setting value itself is uploaded inside the archive | [F-022](EVIDENCE.md), code excerpts 06/20/27 |
| 12 | **Local checkpoint ≠ snapshot upload**: the user-visible "checkpoint rollback" is a pure-local git-refs mechanism (`refs/zcode/checkpoints/...`, `git restore`); the OSS snapshot system is separate and one-directional (no download/restore endpoint found) | [F-023](EVIDENCE.md), code excerpts 28–30 |
| 13 | **Repo Wiki dual channel**: Repo Wiki generation reads the workspace locally and calls the LLM API; additionally, wiki lifecycle events trigger the same snapshot capture/upload path | [F-024](EVIDENCE.md), code excerpts 13/14 |
| 14 | **Telemetry surfaces**: Aliyun ARMS RUM SDK endpoint (`sdk.rum.aliyuncs.com`) and an Aliyun SLS log endpoint are embedded in the desktop bundle; a `deviceMid` identifier is persisted locally and sent as an `X-Device-Mid` header | [F-025](EVIDENCE.md)–[F-027](EVIDENCE.md) |
| 15 | **No client embedding/indexing subsystem identified**: zero hits in the audited server bundle; desktop-bundle hits sit in packaged third-party code (primarily AI-SDK model libraries, plus unrelated third-party assets), with no application-level pipeline | [F-029](EVIDENCE.md) |

## What this repository is not

- It is not a claim that ZCode "steals" anything. Words like *spyware*, *theft*, *backdoor* are user/community characterizations found in third-party discussion; they are not audit conclusions (see [evidence/independent-corroboration.md](evidence/independent-corroboration.md)).
- It does not establish what the vendor's servers do with uploaded snapshots. The cryptographic design means the server *has the capability* to decrypt snapshots ("server possesses the corresponding capability under this envelope-encryption design"); whether and how it does is [UNKNOWN](docs/known-unknowns.md).
- It does not include any raw private evidence. Raw manifests, logs, databases, `.git` objects, and proprietary bundles were **not** uploaded; only sanitized derivatives and minimum-necessary code references are published (see [METHODOLOGY.md](METHODOLOGY.md)).

## Repository structure

```
README.md                 this file
REPORT.md                 full audit report
EVIDENCE.md               evidence ledger (F-001…F-034, claim → artifact → code location → reproduction)
METHODOLOGY.md            audit method, chain of custody, evidence classes
THREAT-MODEL.md           what the encryption does / does not protect
TIMELINE.md               build timestamps, capture timestamps, audit timeline
evidence/
  artifact-hashes.md      SHA-256 of audited program artifacts
  build-info.md           build/version/mtime identification
  sanitized-code-references.md  minimum-necessary code excerpts (source + line ranges)
  sanitized-state/        sanitized checkpoint state.json copies (7 workspaces)
  sanitized-manifests/    sanitized snapshot manifests (3 workspaces, sizes preserved)
  sanitized-extra-manifest/ sanitized global-config manifests
  sanitized-logs/         sanitized log evidence (upload-logging behavior, telemetry state)
  endpoint-map.md         API/OSS endpoints, methods, request/response schemas
  cryptography-flow.md    envelope-encryption data flow
  telemetry-map.md        telemetry channels
  runtime-observations.md dynamic observations on the audited machine
  manifest-statistics.md  .git share statistics of real manifests
  independent-corroboration.md third-party findings vs local reproduction status
  sqlite-schema.txt       local SQLite schema + row counts (no content)
scripts/                  reproduction & scanning scripts (run against your own install)
docs/                     mitigation, known unknowns, reproduction guide
```

## Reproduction

Clone this repository and run the scripts against your own ZCode installation; they are read-only and contain no hard-coded identities. Start with [docs/reproduction.md](docs/reproduction.md):

```bash
bash scripts/hash-zcode-artifacts.sh          # identify & hash your installed build
bash scripts/locate-snapshot-code.sh          # find the snapshot subsystem in your bundle
python3 scripts/summarize-manifest.py ~/.zcode/v2/checkpoints/<id>/manifests/<hash>.json
```

## Privacy and redaction principles

- Originals were never modified; sanitized derivatives were produced by parse → recursive redact → secret-scan (see [METHODOLOGY.md](METHODOLOGY.md)).
- Real usernames, hostnames, project names, workspace/snapshot/manifest identifiers, device ids, branch names, remote names, worktree names, git object ids, and all credential material are replaced with placeholders.
- Sizes, counts, percentages, timestamps, and program-artifact hashes are preserved because they are the evidence.
- No raw `.git` objects, no databases, no proprietary bundles, no raw logs, no real prompts are published.

## License

MIT — see [LICENSE](LICENSE).
