# Official-source anchor — zai-org/ZCode

This file freezes the identity of the official source tree this follow-up is written against.
Every claim in `../` is traceable to this anchor. Recorded **2026-09-21** (local, +0800).

## Repository identity

| Field | Value |
|---|---|
| Repository | `zai-org/ZCode` (`https://github.com/zai-org/ZCode`) |
| Default branch | `main` |
| Branches present | `main` only (1) |
| Tags | none (0) |
| GitHub Releases | none (0) |
| Repository created (GitHub API) | `2026-09-20T12:01:16Z` |
| Repository description (API) | "Z.ai's coding agent harness. Powerful, intelligent, extensible." |
| Declared license (API) | `Apache-2.0` |

## Frozen revision

| Field | Value |
|---|---|
| **HEAD commit** | `872ad960de7ec172591f7e1952f7849229f94521` |
| **Tree SHA** | `d185a9a893c00d51fc3fe51fe7371b9eea7de143` |
| Author | `wuweiqi <weiqi.wu@aminer.cn>` |
| Committer date | `2026-09-21T05:14:32+08:00` (= `2026-09-20T21:14:32Z`) |
| Commit subject | `feat: open source` |
| Tracked files at HEAD | 6,973 |

For context, the expected anchor at the start of this round was the same commit
(`872ad96`) with the same tree (`d185a9a`). **No drift occurred between task start and freeze.**
`872ad96` therefore remains both the *first-public-source anchor* and this round's *frozen baseline*.

## Public history — what it is, and what it is not

The public history visible at the frozen revision consists of exactly **two commits**:

| # | Commit | Date (+0800) | Author | Subject | Files added |
|---|---|---|---|---|---|
| 1 | `77432b6dbf9f70176ced3f4dcdc25f851c3acb2d` | 2026-09-20 20:06:58 | `zRzRzRzRzRzRzR` | `Initial commit` | 0 |
| 2 | `872ad960de7ec172591f7e1952f7849229f94521` | 2026-09-21 05:14:32 | `wuweiqi` | `feat: open source` | 6,973 |

The first commit's tree is `4b825dc642cb6eb9a060e54bf8d69288fbee4904`, which is git's **empty tree**
(`git mktree </dev/null` returns that exact SHA). It contains zero files. The second commit adds all
6,973 files in a single commit.

**Statement of fact:** the public repository history begins with a source code drop.

**Not claimed.** This history carries no development history, so nothing here shows whether, when,
by whom, or why the audited `repo-snapshot` / `repo-wiki` code entered or left the product, nor any
internal decision process. Those questions remain **UNKNOWN** and are not answered by this anchor.

## Program-identity hashes at HEAD

| File | SHA-256 |
|---|---|
| `package.json` | `fd17e8cdcefd36cf92a83b8e45468c4756a947bd77db4e529d11cf2a62d947ed` |
| `LICENSE` | `606c36baf38b973227273df12a74930e4b4137280eea835c5cd623aa4553c13b` |
| `NOTICE.md` | `cca8e323ad7f3b12167b58fba7d14faf18a2cdc4fa890818058872f6215912bf` |
| `pnpm-lock.yaml` | `a63f2497b6f61711d765be85aa3b6a4b543d792fdcc95a8c0effeaeb3d2292d5` |

`pnpm-lock.yaml` is 650,762 B. `LICENSE` is the Apache License, Version 2.0 text
(`Apache License` / `Version 2.0, January 2004`) with no modification notice.

Root `package.json` declares:

- `name`: `zcode`
- `version`: **`3.14.0`**
- `license`: **`Apache-2.0`**
- `private`: `true`
- `packageManager`: `pnpm@10.33.2`
- `engines.node`: `>=24.0.0`

`NOTICE.md` (27,721 B) is titled `# ZCode 相关功能说明与第三方组件声明`. `README.md` is titled
`# ZCode`; a separate `README.en.md` exists. `THIRD-PARTY-NOTICES.md` (1,975,825 B) carries
third-party license texts.

## Local source archive (LOCAL ONLY — not published)

A deterministic `git archive` of the frozen revision was produced for local reproducibility:

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `zcode-official-source-872ad96.tar` | 77,629,440 | `dabbf832bb0eb96067c68f6b2303914b60fd01996469eb78b51e81fd8674b9cf` |
| `zcode-official-source-872ad96.tar.gz` | 39,758,233 | `92dfe04a8ed1f0b4a1757dd55698305b8e39692f891dc5603e71b162b5f6f8b4` |

The archive is prefixed `zcode-872ad96/`. It is **not** uploaded to this audit repository: shipping
the vendor's full source tree here would duplicate it pointlessly and is explicitly out of scope.
Anyone can regenerate a byte-comparable tar from the public commit:

```sh
git clone https://github.com/zai-org/ZCode.git
cd ZCode && git checkout 872ad960de7ec172591f7e1952f7849229f94521
git archive --format=tar --prefix=zcode-872ad96/ HEAD -o zcode-official-source-872ad96.tar
sha256sum zcode-official-source-872ad96.tar   # expect dabbf832…b9cf
```

## Local checkout used for the search

| Field | Value |
|---|---|
| Path (local, not published) | `<clone>/source` under the round's local working directory |
| Remote | `https://github.com/zai-org/ZCode.git` |
| `git status --porcelain` | empty (clean) at freeze time |

The tree was **not** modified at any point; the optional build (see `../BUILD-CORRESPONDENCE.md`) ran
in a separate copy so this checkout stayed pristine and hashable.

## Evidence class

Everything in this file is `[CONFIRMED-OFFICIAL-SOURCE]`: it is read directly from the frozen
commit/tree named above. Vendor-authored prose inside `NOTICE.md` / `README.md` is reported elsewhere
under `[OFFICIAL-SOURCE-DOCUMENTATION]` and is deliberately not mixed with this class.
