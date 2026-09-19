# Manifest statistics (sanitized derivative of local snapshot manifests)

Generated from `evidence/sanitized-manifests/*.json` (sizes preserved, paths anonymized).
These manifests are the local copies ZCode wrote under `~/.zcode/v2/checkpoints/<workspace-id>/manifests/`;
the same `meta/manifest.json` is embedded in the encrypted upload (see EVIDENCE.md F-011).

| workspace | files | .git/** entries | .git share (count) | .git bytes | .git byte share | .git/objects/** | pack files | .git/logs/** | .git/config | .git/index | lost-found |
|---|---|---|---|---|---|---|---|---|---|---|---|
| project-a | 5067 | 4190 | 82.7% | 36,334,898 B | 70.2% | 3927 | 1 | 51 | True | True | 67 |
| project-b | 621 | 556 | 89.5% | 1,029,260 B | 62.0% | 427 | 0 | 19 | True | True | 4 |
| project-c | 306 | 189 | 61.8% | 13,328,341 B | 88.3% | 161 | 2 | 3 | True | True | 0 |

Largest .git entries per manifest (paths anonymized, sizes real):

**project-a**

- `.git/objects/pack/pack-<REDACTED>.pack` — 4,540,393 bytes
- `.git/objects/pack/pack-<REDACTED>.idx` — 163,640 bytes
- `.git/logs/HEAD` — 145,943 bytes

**project-b**

- `.git/objects/73/<REDACTED>` — 31,370 bytes
- `.git/objects/2f/<REDACTED>` — 31,319 bytes
- `.git/objects/45/<REDACTED>` — 31,305 bytes

**project-c**

- `.git/objects/pack/pack-<REDACTED>.pack` — 2,523,192 bytes
- `.git/objects/7c/<REDACTED>` — 1,087,943 bytes
- `.git/objects/ba/<REDACTED>` — 1,087,853 bytes

Notes:

- `project-a` contains a 4,540,393-byte `.pack` file and `project-c` a 2,523,192-byte `.pack` plus two ~1.09 MB loose objects. The scanner's stated per-file limit is `REPO_SNAPSHOT_MAX_FILE_BYTES = 1,024,000/1,048,576` bytes (1 MB); these entries prove the limit is not applied to `.git/**` (EVIDENCE.md F-009).
- `.git/logs/HEAD` (the reflog, 145,943 bytes in project-a) is a manifest entry, so commit-history metadata enters the upload scope (EVIDENCE.md F-008).
- `anon/NNNN.<ext>` entries are workspace files outside `.git/` whose real names were redacted for publication; their sizes are preserved.
