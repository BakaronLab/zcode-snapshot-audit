# Reproduction Guide

All scripts are **read-only** against the ZCode installation, use only bash/grep/python3/sqlite3/openssl, and contain no hard-coded identities. Paths are auto-detected with environment-variable overrides.

Default locations checked by the scripts:

| Env override | Default |
|---|---|
| `ZCODE_HOME` | `~/.zcode` |
| `ZCODE_SERVER_BUNDLE` | `$ZCODE_HOME/server/zcode-server.cjs` |
| `ZCODE_ASAR` | `/opt/ZCode/resources/app.asar` |
| `ZCODE_CHECKPOINTS` | `$ZCODE_HOME/v2/checkpoints` |
| `ZCODE_WIN_CHECKPOINTS` | `/mnt/c/Users/<you>/.zcode/v2/checkpoints` (WSL) — pass explicitly |

## Step 0 — identify your build

```bash
bash scripts/hash-zcode-artifacts.sh
```

Prints size/mtime/SHA-256 of the server bundle and (if present) the desktop asar. Compare against [evidence/artifact-hashes.md](../evidence/artifact-hashes.md): a matching `zcode-server.cjs` hash means every line-number citation applies verbatim to your install.

## Step 1 — locate the snapshot subsystem in your bundle

```bash
bash scripts/locate-snapshot-code.sh                # all key symbols + line numbers
bash scripts/locate-snapshot-code.sh --embedding-check
bash scripts/locate-snapshot-code.sh --wsl-gate-check
```

Expected on a matching build: `RepoSnapshotSidecarService`, `captureBeforePrompt`, `captureRepoWikiSnapshot`, `repo-wiki-update`, `upload-credential`, `walkGitMetadataFiles`, and exactly 4 `repoSnapshotIndexingEnabled` occurrences (schema / optional / normalization / uploaded-key list — no gate). The `workspaceIdentity` early-return in `captureBeforePrompt` is the F-031 gate.

## Step 2 — inspect your local checkpoint artifacts

```bash
python3 scripts/inspect-checkpoints.py ~/.zcode/v2/checkpoints
python3 scripts/inspect-checkpoints.py ~/.zcode/v2/checkpoints --sqlite   # row counts, read-only
```

Prints, per workspace: presence of `lastAcceptedManifestHash` (the client's upload-success marker), `failureCount`, encrypted vs plaintext sizes, capture timestamps. Then look at a manifest:

```bash
python3 scripts/summarize-manifest.py ~/.zcode/v2/checkpoints/<id>/manifests/<hash>.json
python3 scripts/inspect-git-inclusion.py ~/.zcode/v2/checkpoints/<id>/manifests/<hash>.json
```

`summarize-manifest.py` prints total/`.git` counts and byte shares; `inspect-git-inclusion.py` lists `.git/objects`, `logs`, `config`, pack sizes and any >1 MB entries (the F-009 bypass).

## Step 3 — global config groups and redaction

```bash
python3 scripts/inspect-extra-manifest.py ~/.zcode/v2/checkpoints/<id>/extra-manifests/<hash>.json
python3 scripts/scan-sensitive-paths.py --selftest        # SENSITIVE_KEY_PATTERN escape test (synthetic keys only)
```

## Step 4 — endpoints and telemetry

```bash
python3 scripts/inspect-upload-endpoints.py               # needs ZCODE_SERVER_BUNDLE
python3 scripts/inspect-upload-endpoints.py --telemetry   # needs ZCODE_ASAR (binary grep)
```

## Step 5 — verify your own logging surface

```bash
for f in ~/.zcode/v2/logs/*.log; do printf '%s : %s\n' "$f" "$(grep -c 'repoSnapshot' "$f")"; done
# then classify the hits — expect only '[settingService] writing settings' dump lines (F-033)
```

## Step 6 — mitigation check (optional; root needed for chattr)

See [mitigation.md](mitigation.md). `bash scripts/verify-snapshot-disabled.sh` automates the artifact-search half of the canary protocol.

## Sanitizing your own copies (if you publish your own audit)

`scripts/sanitize-json.py` / `scripts/sanitize-jsonl.py` implement the same recursive redaction used for this repository (paths, ids, hashes, device ids) and `scripts/secret-scan.sh` / `scripts/scan-sensitive-paths.py` perform the pre-publication scans. Always re-scan after sanitizing; never upload raw artifacts.

## Interpreting results

- If your build hash **matches** ours and your artifacts show the same structures, the findings reproduce on your machine.
- If your build hash **differs** (the server bundle auto-updates), re-run `locate-snapshot-code.sh`: symbol presence and the `captureBeforePrompt` gate are the load-bearing checks; line numbers will shift.
- Absence of `lastAcceptedManifestHash` in your state files means no completed upload (yet) on your machine — the code path, not the artifact, remains the primary evidence.
