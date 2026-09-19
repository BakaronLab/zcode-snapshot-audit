# Mitigations

Status vocabulary: **VERIFIED** (tested on the audited build during this audit), **PROPOSED** (designed and reasoned but not executed), **FAILED** (tested and ineffective).

## 1. `repoSnapshotIndexingEnabled = false`

**Status: FAILED as an upload mitigation** (tested against the audited code and contradicted by local artifacts).

The Windows-side machine ran with this setting `false` while its state file still records a completed upload (the client's own success marker, F-020); the server bundle contains no code path that conditions capture or upload on the setting (F-022). Setting it to `false` remains reasonable hygiene (the value itself is uploaded either way) but must not be relied upon.

## 2. Making the snapshot state directory non-writable (`chattr +i`)

**Status: PROPOSED** — could not be applied during the audit because the audit session lacked root privileges (`sudo` requires an interactive password that the session must not handle).

On the audited layout, the capture pipeline writes its state and pending artifacts under `~/.zcode/v2/checkpoints/<workspace-id>/`. If that directory tree cannot be created/written, capture fails before any upload is staged. Because upload errors are swallowed silently (F-033/F-004), a blocked capture is expected to produce no user-visible errors.

Verification protocol (canary-based; do not point this at a workspace containing private data):

```bash
# 1. record start time
date -Is | tee /tmp/canary-start.txt

# 2. lock the snapshot state directory (root required)
sudo chattr +i ~/.zcode/v2/checkpoints   # or: sudo chattr -R +i for existing tree

# 3. create a canary repo with a recognizable dummy file
mkdir -p /tmp/zcode-canary && cd /tmp/zcode-canary
git init && echo "canary $(date -Is)" > canary.txt && git add -A && git commit -m canary

# 4. use ZCode normally on the canary workspace (send several prompts)

# 5. search for new snapshot artifacts anywhere
bash scripts/verify-snapshot-disabled.sh   # automates steps 5-6
find ~/.zcode -newer /tmp/canary-start.txt -name 'state.json' -o -newer /tmp/canary-start.txt -name '*.enc'

# 6. restore
sudo chattr -i ~/.zcode/v2/checkpoints
```

`scripts/verify-snapshot-disabled.sh` implements steps 5–6 and reports `MITIGATION VERIFIED` / `NOT VERIFIED` for the machine it runs on.

**Expected side effects on the audited build:** local checkpoint/timeline/rollback functionality and repo-snapshot-related behavior may fail (silently — see F-033). This is not a permanent security guarantee: a future ZCode build may change snapshot paths or transport behavior, and the client may gain a fallback location. Re-verify after every client/server update.

## 3. Avoiding the capture path entirely

**Status: PROPOSED (structural, not executed as a test).** The capture pipeline requires (a) a logged-in token, (b) a server-issued upload credential, and (c) a non-remote workspace (F-031). Not using the logged-in client on sensitive workspaces — or editing outside ZCode — avoids the snapshot path by construction. This is the only mitigation whose effectiveness does not depend on client internals.

## 4. Remote/SSH workspace mode

**Status: PROPOSED — do not rely on it.** The code contains a capture-suppression gate for workspaces that carry a `workspaceIdentity` (remote sessions, F-031), but its practical coverage (WSL targets, SSH targets, task-completion path) was not observed on the audited machine and may change in any build.

## 5. Hygiene for global configs

**Status: PROPOSED.** Because global config files (`mcp.json`, `hooks.json`, memory, instructions, etc.) are packed into every snapshot and redaction is key-name-only (F-012/F-013):

- store credentials in files/locations outside the collected global-config scope (e.g. OS keyring, environment injected by a wrapper, or credential files not listed in `GLOBAL_CONFIG_PATHS`);
- avoid secret-bearing values under key names that do not match `SENSITIVE_KEY_PATTERN`;
- treat anything already present in those files as having left the machine if you used ZCode logged-in on this build.

---

**General caveat:** all mitigations here are client-side observations about one audited build. They are not security guarantees, and none of them says anything about data already captured and uploaded (see F-020: completed uploads predate any mitigation).
