# BUILD-CORRESPONDENCE — optional reproducible build of the 3.14.0 server bundle

**Classification: `BUILD_COMPLETED_NONIDENTICAL`.**

A server bundle was built from the frozen official source commit and **not** byte-identical to the
shipped artifact. No lockfile, manifest or source file was modified to obtain it. The frozen source
checkout stayed pristine throughout (the build ran in a separate copy).

This file is what the requested `BUILD-CORRESPONDENCE.md` describes: what was built, under what
environment, and how far the built artifact matches the shipped one and the source tree.

## Why it was attempted

Static mapping (see [SOURCE-BINARY-MAPPING.md](SOURCE-BINARY-MAPPING.md)) establishes module-name
correspondence. A build adds a second, independent check: if the frozen source can produce a bundle
whose module set is source-complete and whose old-symbol profile matches the shipped bundle, then the
source and the shipped artifact are structurally consistent — without claiming they are the same
commit.

## Environment (recorded)

| Field | Value |
|---|---|
| Date | 2026-09-21 14:08 +0800 |
| Platform | `Linux 6.18.33.2-microsoft-standard-WSL2 x86_64 GNU/Linux` |
| Node | `v24.19.0` (checkout's `.nvmrc` = `24`; root `engines.node` = `>=24.0.0`) |
| npm | `11.17.0` |
| pnpm | `10.33.2` via `npx --yes pnpm@10.33.2` (matches root `packageManager`; **no global install**) |
| Lockfile | used as-is, `--frozen-lockfile` |
| `pnpm-lock.yaml` SHA-256 | `a63f2497b6f61711d765be85aa3b6a4b543d792fdcc95a8c0effeaeb3d2292d5` (650,762 B, unmodified) |
| Source under test | `872ad960de7ec172591f7e1952f7849229f94521` |
| CPUs / RAM / free disk | 16 / 15 GB / ~748 GB |
| Isolation | no container runtime available (no `docker`, no `podman`); build ran in a **copy** at `<clone>/build/source` (see `ENV.txt`), never in the frozen checkout |

Commands, in order:

```sh
cp -a source/. build/source/
cd build/source
npx --yes pnpm@10.33.2 install --ignore-scripts --frozen-lockfile   # exit 0, 1713 pkgs, 2m 8s
npx --yes pnpm@10.33.2 --filter "@zcode/server..." build            # exit 0
```

`--ignore-scripts` was used deliberately: the root `prepare` script runs `husky`, which would rewrite
git hook configuration in the build copy. Skipping lifecycle scripts keeps the build from touching
anything outside `node_modules`. It did not affect the result — the produced bundle passes
`node --check`.

Build entry points (read from the repo, not chosen by this audit):
`packages/server/package.json` → `build` = `tsup && pnpm run build:remote`; `build-remote.ts` uses
`entryPoints: ["src/entry-stdio.ts"]` → `outfile: "dist/remote/zcode-server.cjs"`. That is the same
artifact name and entry the shipped file carries, so the comparison below is like-for-like at the
entry level.

## Built artifact

| Artifact | Bytes | SHA-256 | Notes |
|---|---|---|---|
| Built `dist/remote/zcode-server.cjs` | 5,757,271 | `0ad8f300011bf90baa741bf42364efeeae00a0ab8c0c7dcba4da99c9e6ab03fa` | `node --check` → parse OK; self-declares `"3.14.0"` |
| Shipped `zcode-server.cjs` (frozen 3.14.0) | 11,527,731 | `99fcad13480b7402843d4d3178bc6bbe01f1a991288a5c582ed3241c9771f003` | from `../followup-3.14/evidence/artifact-hashes-3.14.md` |

**The two are not byte-identical, and are not expected to be.** Reproducible-build equality would
require pinned toolchain, dependency and environment determinism that the project does not claim and
this audit cannot verify.

## What was compared

Module-path comments (the same esbuild `// ../<path>` convention used throughout this audit) were
extracted from the built bundle and compared with (a) the shipped bundle and (b) the official source
tree. Reproduce with [`scripts/source-binary-map.py`](scripts/source-binary-map.py).

### Built bundle vs official source tree

| Metric | Value |
|---|---|
| Module comments | 789 |
| Third-party | 323 |
| Workspace | 466 |
| `DIRECT_NAME_MATCH` | **466 (100.0%)** |
| `MISSING_IN_SOURCE` | **0** |

This is the expected result and serves as the build's own control: a bundle built from a tree has
every one of its application modules in that tree.

### Built bundle vs shipped 3.14.0 bundle

| Metric | Built | Shipped | Common |
|---|---|---|---|
| Module comments (total) | 789 | 1,012 | 779 |
| Workspace modules | 466 | 506 | 456 |
| Third-party modules | 323 | 506 | 323 |

**Workspace modules present in the built bundle but not the shipped one: 10.** All 10 are present in
the official source tree — they are packaging-layout differences, not behaviour differences. In this
build `@zcode/zcode-cua` resolved to the workspace package `packages/zcode-cua/*.js`, while the
shipped bundle carries the published-package layout `node_modules/@zcode/zcode-cua/dist/broker/*.js`.
The other three (`services/src/cua-permission-broker/index.ts`, `services/src/device/deviceMid.ts`,
`shared/src/endpointHostname.ts`) are modules this build's closure reached and the shipped build
reached through a different path.

**Workspace modules present in the shipped bundle but not the built one: 50.** These split cleanly:

| Group | Count | In the official source tree? |
|---|---|---|
| `services/src/bots/**` | 26 | **No** |
| `services/src/cloud-content/**` | 3 | **No** |
| `services/src/marketing-touch/**` | 3 | **No** |
| `services/src/output-style/**` | 2 | **No** |
| `services/src/session/sessionModeOptions.ts` | 1 | **No** |
| `shared/src/{bots,cloudContent,coding-plan-signature-feature,marketingTouch,opencode-model-id,rewardsEmbedded,web-remote-control-rpc-transport}.ts` | 7 | **No** |
| `rpc/src/channelClient.ts`, `session/taskChangeSummary.ts`, `shared/src/{assistant-message-parts,assistant-presentation,lineChangeStat,permission-request-preview,telemetry,tool-call-summary}.ts` | 8 | **Yes** — not reached by this build's entry closure |

35 of the 50 are the feature clusters the official tree does not publish; the remaining 8 are in the
tree but outside this build's import closure (a plausible cascade, since several are consumed by the
unpublished clusters — not investigated to conclusion and not load-bearing here).

**Third-party modules: built 323 vs shipped 506 (323 common).** The shipped bundle inlines ~183 more
third-party modules than this build produced. The cause was not investigated to conclusion; the
shipped artifact is produced by the vendor's release pipeline, whose dependency resolution and
bundling flags this audit does not reproduce. Recorded as an unexplained residual, not glossed over.

### Old-symbol profile of the built bundle

All 22 old repo-snapshot / Repo Wiki symbols probed in the binary audit return **0** in the built
bundle (`RepoSnapshotSidecarService`, `repoSnapshot`, `RepoSnapshot`, `captureBeforePrompt`,
`scheduleRepoSnapshotSidecar`, `captureRepoWikiSnapshot`, `repo-wiki-update`, `walkGitMetadataFiles`,
`appendRootGitMetadataPaths`, `shouldIncludeRepoSnapshotPathBeforeSample`,
`writeRepoSnapshotPlainArchive`, `buildRepoSnapshotGlobalConfigsExtraInputs`,
`repoSnapshotIndexingEnabled`, `lastAcceptedManifestHash`, `markAcceptedManifest`,
`repo-snapshot.tar.gz.enc`, `encrypted_aes_key`, `base_snapshot_id`,
`/api/v1/snapshot/upload-credential`, `repo-snapshot`, `repo-wiki`, `RepoWiki`).

This agrees with the shipped bundle (also 0 for all 22) and with the source tree. **The built
artifact independently reproduces the audited absence.**

## Verdict

`BUILD_COMPLETED_NONIDENTICAL`, with a source-complete module set and a matching old-symbol profile.

What this supports: the frozen official source can produce a 3.14.0 server bundle, that bundle's
application modules are 100% drawn from the frozen tree, and it contains none of the audited
subsystem — the same negative profile as the shipped artifact.

What this does **not** support: that the built bundle is the shipped bundle, that the shipped bundle
was built from `872ad96`, or any claim about `a1328db1`. Reproducing a *non-identical* bundle from a
tree is consistent with that tree being the shipped source; it is not proof of it. See
[SOURCE-BINARY-MAPPING.md](SOURCE-BINARY-MAPPING.md) §"Provenance boundary".

**Limitation.** A build proves the tree *compiles into* a consistent bundle. It cannot establish that
the vendor's released binaries came from this tree, and it does not observe runtime or network
behaviour.
