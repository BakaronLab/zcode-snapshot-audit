# Independent Corroboration

Third-party material is used **only** to check whether independent observers reached conclusions consistent with the local evidence. It is never a substitute for local evidence, and no claim from this table should be repeated without its reproduction status.

Primary external source: blog analysis "扒一扒 ZCode 静默上传全量 Git 历史的骚操作" — <https://blog.ferstar.org/posts/zcode-silent-workspace-snapshot-upload/> (independent technical write-up of the same client behavior). Additional corroboration exists in public issue reports on community forums; those are treated as low-weight signals and are not cited as core evidence.

| # | Third-party finding | Local status | Local evidence |
|---|---|---|---|
| 1 | A snapshot of the workspace is silently uploaded before each prompt | **REPRODUCED** (code-level trigger) | F-002 (code; capture itself is additionally gated by F-031 preconditions), F-020 (accepted-state artifacts) |
| 2 | Upload content includes file contents and full `.git` history (objects/pack) | **REPRODUCED** | F-003, F-008 (manifests: 61.8–89.5% `.git/**`) |
| 3 | Large pack files exceed the nominal 1 MB file limit | **REPRODUCED** | F-009 (4.5 MB / 2.5 MB packs in real manifests) |
| 4 | The `repoSnapshotIndexingEnabled` switch does not stop capture/upload | **REPRODUCED** | F-022 (all 4 occurrences non-gating; sidecar unconditional) |
| 5 | Encryption is enveloped with a server-delivered RSA public key; server can decrypt | **REPRODUCED** (capability claim) | F-015/F-017/F-019 (code); capability-only phrasing maintained |
| 6 | Failed uploads leave `.tar.gz.enc` pending artifacts that retry | **PARTIALLY_REPRODUCED** | code path confirmed (excerpt 12); no failed-upload residue existed locally to observe |
| 7 | Upload activity is invisible in local logs / silent | **PARTIALLY_REPRODUCED** | subsystem emits no log lines (confirmed), but the word `repoSnapshot` does appear inside settings dumps — refined, not contradicted (F-033) |
| 8 | Server-side storage/usage of snapshots (indexing, training claims) | **NOT_TESTED** | out of scope for local evidence; no claims made |
| 9 | Conflation of "checkpoint" UI feature with the snapshot upload system | **NOT_REPRODUCED** | two distinct systems locally (F-023): rollback is a local git-refs mechanism |
| 10 | Specific OSS bucket host names | **NOT_TESTED** | host is runtime-delivered; not locally observable |

## Community characterization note

Community discussions characterize this behavior with terms such as "spyware" or "silent upload". This repository treats those as **user/community characterizations**, not audit conclusions. The audit documents the client-side mechanism, its defaults, and its lack of a local opt-out; readers draw their own conclusions.
