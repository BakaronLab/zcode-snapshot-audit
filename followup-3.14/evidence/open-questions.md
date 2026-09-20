# Open questions

What this follow-up does **not** resolve. Nothing here is a suspicion of wrongdoing; each item is a
boundary of what static analysis of three artifacts can establish.

## 1. `OPEN-314-001` — component-manifest `sha256` field semantics

**Status: RESOLVED (field semantics identified). Residual sub-question `OPEN-314-001a` remains.**

### The observation

A component manifest next to the installed server component declares a `sha256` that does not match
the installed file:

```
~/.zcode/server/.asset-components/server-bundle.json
  {"id":"server-bundle","sha256":"eab38c60c76674b7b68f496c404992db8cd804e6c298d786fd9e5c49af923d91", …}

actual installed file
  ~/.zcode/server/zcode-server.cjs →
  sha256 99fcad13480b7402843d4d3178bc6bbe01f1a991288a5c582ed3241c9771f003
```

### The discriminator

A second component in the same manifest format declares a **version** that can be checked
independently:

```
glm.json:   {"id":"glm","version":"0.13.3","sha256":"64ac4444fe59cc2b76055848a68890ed7294b5973fa36560f8bc8bcf91be2573", …}
installed:  ~/.zcode/server/agents/glm/.version          → "0.13.3"       ✓ VERSION MATCHES
            ~/.zcode/server/agents/glm/zcode.cjs  (sha256) → 8f5cfccf…11ba05
            ~/.zcode/server/agents/glm/zcode-agent(sha256) → b523635c…521124
            ~/.zcode/server/agents/glm/.version   (sha256) → 6766ecd1…8d4ab7
                                                             ✗ NO FILE matches the declared sha256
```

So for `glm`, the declared **version** matches the installed artifact exactly, while the declared
**sha256** matches no installed file.

### Observed relationship (stated without over-interpretation)

| Sub-question | Finding |
|---|---|
| Is the declared `sha256` the post-extraction installed file? | **NO** — excluded. `glm` demonstrates it cannot be, and `server-bundle` agrees. |
| Is it a compressed view (gzip/xz/zstd/bzip2) of the installed file? | **NO** — tested against the server bundle, no match. |
| Is it the transport / upstream source archive (e.g. the downloaded `.tar.gz` / `.tgz` before extraction)? | **Most consistent with the evidence** — but the upstream object was not available locally, so this is a reasoned inference, not a verified fact. |
| Is the manifest stale (not rewritten on swap)? | **Excluded for the version field** — `glm.json` declares the version actually installed. A stale manifest would show an older version. |
| Does this affect artifact identity for this delta? | **NO** — the examined artifacts were hashed directly from their bytes; no manifest is relied upon for identity. |

**This is a field-semantics question, not an integrity failure, tampering, or a bad download.** The
manifest format's `sha256` field cannot be used as an installed-artifact integrity check.

### Residual: `OPEN-314-001a`

The exact upstream object that the `sha256` field names is **unverified**. Closing it would require
the downloaded component archive, which is not retained locally. Practical consequence for future
audits: **hash the installed files directly** rather than trusting `.asset-components/*.json`.

## 2. Server-side behavior — UNKNOWN

Unchanged from the original audit and **not** narrowed by this follow-up:

- What the ZCode service does with snapshots it received before this update.
- Whether previously uploaded data is retained, processed, used for training, deleted, or anything
  else.
- What the service does with data received from other clients or other builds.

Client-side absence establishes nothing about server-side behavior. This follow-up makes no claim in
either direction.

## 3. Other builds — UNKNOWN

This follow-up examined **three** 3.14.0 artifacts on one machine:

| Examined | Not examined |
|---|---|
| WSL server bundle `zcode-server.cjs` (3.14.0) | Other platforms' desktop bundles (macOS, Linux) |
| WSL server-side second bundle `agents/glm/zcode.cjs` (3.14.0) | Older 3.x builds that may still be in use elsewhere |
| Windows desktop `app.asar` (3.14.0, commit `a1328db1`) | Lazily-downloaded modules not present in the shipped bundles |
| | Non-JavaScript components (native executables were probed for absence of specific strings only) |

**Whether any other client build still contains the uploader is UNKNOWN.** The negative claims in
this directory are scoped to the three artifacts listed in
[artifact-hashes-3.14.md](artifact-hashes-3.14.md) and to their exact hashes.

The second server-side bundle is included explicitly so that the claims cannot be read as "only the
main server bundle was scanned". It returns 0 hits for every repo-snapshot symbol.

## 4. Runtime behavior — not exercised

- No prompt was sent and no behavior was triggered to test the new build.
- No packet capture, no TLS interception, no certificate bypass was performed. Nothing in this
  follow-up observes the wire.
- `~/.zcode/v2/checkpoints` was absent and there were 0 `*.enc` files under `~/.zcode` at
  observation time. This is recorded as **NOT OBSERVED**, not as "proven absent": the directory could
  have been removed by this update, by an earlier cleanup, or never have existed on this profile.
- The local SQLite database size (`~/.zcode/cli/db/db.sqlite`, 21,835,776 B at
  2026-09-20 11:30:21 +0800) is a moving target; it was live and growing during the audit, so the
  figure is timestamped rather than asserted as a stable value.

## 5. Extractor-dependent absolute values

Two absolute figures depend on how module-segment boundaries are attributed, and only their deltas
are load-bearing:

| Quantity | Audit's extractor | Independent review | Re-measurement for publication | Agreed delta |
|---|---|---|---|---|
| `zcodeAgentService.ts` module size | 174,083 → 179,586 B | 174,242 → 179,745 B | 173,993 → 179,496 B | **+5,503 B** |
| Desktop module-comment total | 3634 → 3365 | 3818 → 3549 | 3818 → 3549 | **−269** |

Cite the deltas, not the absolutes.

## 6. Question this follow-up deliberately does not answer

**Why** the subsystem was removed. The delta establishes *what* changed in the client artifacts. It
does not establish the vendor's intent, and no attempt is made to infer it. The official changelog
entry that corresponds to this area is treated as external release context only — it is not used as
evidence for any claim in this directory.
