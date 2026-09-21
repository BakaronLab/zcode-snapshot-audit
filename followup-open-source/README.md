# Official-source corroboration — ZCode 3.14.0 published source · 官方开源源码跟进

**EN.** ZCode subsequently published its 3.14.0 source code. This directory is an independent,
source-level corroboration of the earlier binary findings. The official source tree independently
corroborates the removal of the audited client-side repo-snapshot / Repo Wiki implementation, while
**not** establishing exact source identity with the previously frozen shipped binaries.

**中文。** ZCode 后续公开了 3.14.0 源码。本目录针对既有二进制审计结论做源码级交叉验证。官方源码树独立
印证了此前审计到的客户端 repo-snapshot / Repo Wiki 实现已被移除，但**不**据此主张公开源码与此前冻结的
发行二进制具有精确源码同一性。

## The evidence chain this round extends

```
old proprietary build            (hashed earlier builds: desktop 3.11.2, server 3.12.3)
  → 3.14 binary regression       ../followup-3.14/   — audited subsystem absent from 3.14.0 bundles
  → official source corroboration  this directory    — the published source tree agrees
```

The middle link stands on its own: it was established from the frozen shipped bundles, independently
of whether any source was ever published. This round adds the third link.

## Result

**Corroborated at three independent levels, plus a build.**

| Level | Test | Result |
|---|---|---|
| Name | 20 audited symbols | **all 0** — `ABSENT_EXACT_SYMBOL` |
| Structure | 42 removed module names, 4 removed paths, wildcard path sweep | **all absent** — `ABSENT_PATH` |
| Feature cluster | Repo Wiki under every searched name incl. 仓库百科 | **not identified** |
| Structure (calibrated) | bundle module-path comments mapped onto the tree | old bundle → **20 + 22 + 2 recovered**; 3.14 bundle → **0** |
| Behaviour | 5-signal co-occurrence scan over 2,539 source files | **none ≥ 4/5** — `NO_EQUIVALENT_IDENTIFIED` |
| Build | 3.14.0 server bundle built from the tree | **`BUILD_COMPLETED_NONIDENTICAL`**, 100% source-complete, 0 old symbols |

Attribution confirmed, not corrected: the surviving `upload-credential` / `oss.host` / `x-oss-*`
vocabulary resolves in source to the **user-initiated feedback attachment upload** path, exactly as
the binary audit had attributed it.

### Statement this round supports

> The official ZCode 3.14.0 source tree independently corroborates the 3.14 binary regression result:
> the previously audited client-side repo-snapshot and Repo Wiki implementation is not identified in
> the frozen official source tree, while the surviving feedback attachment upload path maps directly
> to the residual upload surface previously attributed in the binary audit.

> ZCode 官方公开的 3.14.0 源码树独立印证了此前的 3.14 二进制回归结论：先前审计到的客户端 repo-snapshot
> 与 Repo Wiki 实现未在固定的官方源码树中识别到；与此同时，源码中仍存在的 feedback 附件上传路径与此前
> 二进制审计中归因的残余上传面直接对应。

## Frozen anchor

| Field | Value |
|---|---|
| Repository | `zai-org/ZCode` |
| HEAD | `872ad960de7ec172591f7e1952f7849229f94521` |
| Tree | `d185a9a893c00d51fc3fe51fe7371b9eea7de143` |
| Commit date | `2026-09-21T05:14:32+08:00` |
| Version / license | `3.14.0` / `Apache-2.0` |

`872ad96` was both the expected anchor at task start and the frozen baseline at freeze time — **no
drift**. Full record with hashes: [`evidence/official-source-anchor.md`](evidence/official-source-anchor.md).

Public history is **two commits**, the first of which is git's empty tree and contains no files: the
public repository history **begins with a source code drop**. It is **not** a complete development
history, and nothing here infers when, by whom or why the subsystem left the product.

## Files

| File | What it contains |
|---|---|
| [`OFFICIAL-SOURCE-STATE.md`](OFFICIAL-SOURCE-STATE.md) | What the published source is at the frozen revision; identity, layout, and the honest disclosure that the tree is not a complete mirror of the shipped build |
| [`SOURCE-CORROBORATION.md`](SOURCE-CORROBORATION.md) | The corroboration itself: exact symbols, module names, paths, Repo Wiki, `zcodeAgentService`, feedback attribution, behavioural scan, structural test |
| [`SOURCE-BINARY-MAPPING.md`](SOURCE-BINARY-MAPPING.md) | Static mapping table (`DIRECT_NAME_MATCH` / `STRUCTURAL_MATCH` / `BEHAVIOR_MATCH` / `NOT_MAPPABLE` / `CONFLICT`), the calibration control, and the **provenance boundary** |
| [`CURRENT-UPLOAD-SURFACES.md`](CURRENT-UPLOAD-SURFACES.md) | Source-backed classification of the upload/network surfaces that **are** present, so "not identified" is never read as "none exists" |
| [`BUILD-CORRESPONDENCE.md`](BUILD-CORRESPONDENCE.md) | The optional isolated build: environment, commands, module-set comparison, unexplained residuals |
| [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) | What this round does **not** answer |
| [`evidence/official-source-anchor.md`](evidence/official-source-anchor.md) | The frozen anchor record and its hashes |
| [`evidence/source-search-matrix.md`](evidence/source-search-matrix.md) | The complete search matrix, every probe, every classification |
| [`scripts/`](scripts/) | Runnable probes: `source-symbol-probe.sh`, `source-binary-map.py`, `behavior-equivalence-scan.py` |

## Evidence classes

This round introduces one new class and keeps it strictly apart from the documentation class:

| Class | Meaning |
|---|---|
| **`[CONFIRMED-OFFICIAL-SOURCE]`** | Read directly from the frozen commit/tree named above. This is the class of all code, path, symbol and module findings here. |
| **`[OFFICIAL-SOURCE-DOCUMENTATION]`** | Vendor-authored descriptive prose — chiefly `NOTICE.md` / `README.md` / `docs`. **Documentation, not runtime proof.** Never used as a substitute for a code finding, and never mixed with the class above. |

The original repository's classes (`[CONFIRMED-CODE]`, `[CONFIRMED-LOCAL-ARTIFACT]`,
`[CONFIRMED-RUNTIME]`, `[INDEPENDENT-CORROBORATION]`, `[INFERRED]`, `[UNKNOWN]`) continue to apply to
the original findings. `[CONFIRMED-RUNTIME]` is **not** claimed for anything in this directory: no
traffic was captured, generated or observed, and no ZCode endpoint was contacted.

## Boundaries — what this round does not say

Stated here as well as in the individual files, because these are the claims most likely to be
over-read:

- **Not** "the official open-sourcing proves there was never a problem." Earlier builds contained the
  audited subsystem; the original findings remain historical findings for those hashed builds.
- **Not** "the official source proves all data has been deleted." Cloud retention, deletion and
  training use are not determinable from a client source tree. Vendor statements on these points are
  **EXTERNAL / VENDOR CLAIMS**, not verified by this audit.
- **Not** "the official source and the shipped binaries are exactly the same source." They are highly
  consistent; they are **NOT PROVEN SOURCE-IDENTICAL**. The shipped desktop payload's build commit
  `a1328db1` is not an object in the official repository.
- **Not** "ZCode now has no upload." Several upload and network surfaces remain and are catalogued in
  [`CURRENT-UPLOAD-SURFACES.md`](CURRENT-UPLOAD-SURFACES.md).
- **Not** "ZCode no longer sends code to any service." Sending code to model providers is the
  by-design premise of the product.
- **Not** proof of non-existence. Name, structure and signal tests are all vocabulary- and
  shape-sensitive; an implementation with disjoint vocabulary and a different shape would evade all
  three. This is **calibrated negative evidence**.
- **Not** a statement about server-side behaviour, which remains **UNKNOWN**.

## Reproducing

```sh
git clone https://github.com/zai-org/ZCode.git
cd ZCode && git checkout 872ad960de7ec172591f7e1952f7849229f94521
bash  <this-dir>/scripts/source-symbol-probe.sh .          # symbol / module / path matrix + controls
python3 <this-dir>/scripts/behavior-equivalence-scan.py packages 3   # 5-signal scan
```

`source-binary-map.py` additionally needs a frozen bundle, which is identified by hash in
[`../followup-3.14/evidence/artifact-hashes-3.14.md`](../followup-3.14/evidence/artifact-hashes-3.14.md);
the bundles themselves are not redistributed here.

No official source code is copied into this repository: only commit/tree hashes, paths, symbol names,
counts, minimal excerpts and structural descriptions.

## Verification of this directory

Both repository scans were run over the whole tree after these files were added and both pass.

The secret scan is self-contained:

```sh
bash scripts/secret-scan.sh                       # → SECRET SCAN: PASS
```

The identity scan requires the withheld values as arguments, and **those values are deliberately not
written down here** — publishing them would defeat the point of withholding them. Supply them from the
local-only index (`.gitignore`d, never tracked) in the documented form:

```sh
python3 scripts/scan-sensitive-paths.py . \
  --identity <each withheld value from the local-only index> \
  --allow-hex-in 'SHA256SUMS,evidence/artifact-hashes.md,evidence/sanitized-code-references.md' \
  --allow-hex-in 'TIMELINE.md,followup-3.14/README.md,followup-3.14/evidence/artifact-hashes-3.14.md,followup-3.14/evidence/open-questions.md' \
  --allow-hex-in 'followup-open-source/BUILD-CORRESPONDENCE.md,followup-open-source/OFFICIAL-SOURCE-STATE.md,followup-open-source/README.md,followup-open-source/SOURCE-BINARY-MAPPING.md,followup-open-source/SOURCE-CORROBORATION.md,followup-open-source/evidence/official-source-anchor.md,followup-open-source/evidence/source-search-matrix.md'
  # → 0 potential violations (exit 0)
```

Notes on the identity scan, recorded so the allow-list is auditable rather than a blanket waiver:

- **The `--identity` arguments are the withheld values themselves**, so this file states only that they
  come from the local-only index. An earlier revision of this section inlined them; that was caught in
  independent review as a publication of the very strings the audit withholds, and removed. Do not
  re-inline them.
- `--allow-hex-in` takes **exact relative file paths**, not directories — a directory name there
  silently does nothing. The files listed above intentionally publish SHA-256/SHA-1 values of **public
  artifacts** — official commit and tree SHAs, the git empty-tree constant, and program-artifact
  hashes. Every 16+-hex string in the files added by this round was checked to be one of those; none is
  a device id, workspace hash, or path-derived value. The scanner's own by-design exemptions already
  cover `*artifact-hashes.md`, `*hashes.md`, `*cryptography-flow.md`, `SHA256SUMS` and
  `PRIVATE_EVIDENCE_INDEX.md`.
- The allow-list entries for `TIMELINE.md` and `followup-3.14/**` were already required **before** this
  round — those files publish program-artifact hashes by design, so the scan instruction recorded in
  `PRIVATE_EVIDENCE_INDEX.md` was already incomplete for them. This round did not widen the policy; it
  only completed the list.

Local working-directory names are **not** published either: this round's clone path is written as
`<clone>/` rather than as a real local directory name, consistent with the repository's existing
withholding convention.

