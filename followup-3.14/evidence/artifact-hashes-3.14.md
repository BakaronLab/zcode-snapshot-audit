# Artifact hashes — ZCode 3.14.0

SHA-256 and SHA-512 of the audited **program artifacts**. These identify a build, not a user, and are
safe to publish. They are the anchors for every claim in this follow-up: if your installed files hash
to these values, the counts and module sets in this directory apply to your build.

## 3.14.0 artifacts (the right-hand side of the delta)

| Artifact | Size (B) | mtime (+0800) | SHA-256 | SHA-512 |
|---|---|---|---|---|
| Server bundle `zcode-server.cjs` (WSL) | 11,527,731 | 2026-09-20 11:03:00 | `99fcad13480b7402843d4d3178bc6bbe01f1a991288a5c582ed3241c9771f003` | `1832fae719f7220c46c0a555c310f0ab740b017dd82bd01ed742f055cf803cd1b94a6c863889f02d5f0b6f12d4017bd2bfa436de3cd3bc353b315293d5bd8910` |
| Server-side second bundle `agents/glm/zcode.cjs` (WSL) | 14,796,490 | 2026-09-20 11:03:06 | `8f5cfccf2a899b92e57bc2a5760b949c1a928f739652fffc9e6d07c24f11ba05` | `a52eff27f6f8585a0a2ca8b0710a03e02da127662774d8e78e79e65480ea00fc66e037aa1925f99638aa8ae202b5b7afe653e091f61fe42fa0987474ecf3b117` |
| Desktop `app.asar` (Windows) | 326,893,098 | 2026-09-19 10:13:12 | `8604b5f47b0f4bf9e900901d8c60a0dcf6406b89879da872640ae27026b628cb` | `444689d7bfe1b3fb07eb7742dafa1bf7f90e9cf5f177c8523ee7f3c726e988f31d1ec7fbc1ee9bfc4ee21f92d57a046f37f42bfe59ad10740f2d92e7009aa4b1` |

Where each value comes from:

- **Server bundle** — copied from the live WSL server path `~/.zcode/server/zcode-server.cjs` with
  metadata preserved, before analysis. It self-declares `ZCODE_VERSION = "3.14.0"` (bundle
  `shared/src/version.ts`). `node --check` on the frozen copy returns PARSE OK.
- **Second server-side bundle** — copied the same way from
  `~/.zcode/server/agents/glm/zcode.cjs`. It was replaced by the same 3.14.0 update, six seconds
  after the main bundle. It carries no version string of its own, so its 3.14.0 identification rests
  on that copy provenance rather than on self-declaration. It is included because a first draft of
  the audit wrongly asserted that no second bundle existed; **0 hits for every repo-snapshot symbol**
  were found in it.
- **Desktop `app.asar`** — read (not modified) from the installed Windows application's
  `resources/app.asar`. Version identity is read from the ASAR's own `package.json`
  (`@zcode/desktop`, version `3.14.0`) and `out/metadata/build-meta.json`
  (`appVersion: 3.14.0`, commit `a1328db1`, build time `2026-09-19T01:46:14.799Z`) — not inferred
  from a filename. The file is read-only on disk.

For reference, the installer that produced the Windows side hashes to
`74aaf7deef9b805b993aeaf2133e70eef74816888b326fc8b4a36c90c4ed15ee` (178,435,968 B). It was hashed
in place on the Windows side during the audit and is **not** part of the frozen artifact set, so this
value cannot be recomputed from the artifacts published here. Its own updater metadata records a
base64 SHA-512 that decodes to the value computed from the file, i.e. the file on disk is what the
updater believes it downloaded.

## Earlier-build reference hashes (the left-hand side)

These are the old-side values, already published in [evidence/artifact-hashes.md](../../evidence/artifact-hashes.md).
They are repeated here only so the delta can be read in one place.

| Artifact | Size (B) | SHA-256 |
|---|---|---|
| Desktop `app.asar` (Linux, 3.11.2) | 307,138,103 | `e260f7537c7e173b21cbb54b42800ca320da14d8f2244b297b71b2a3a2d90081` |
| Server bundle `zcode-server.cjs` (WSL, self-declared **3.12.3**) | 13,409,418 | `e4150318eac90ad5e74ce99a7d8f891c598a4057c0e061570702e4f778c6183c` |

**Version relationship:** desktop `3.11.2 → 3.14.0`; server `3.12.3 → 3.14.0`. The two components
version independently and were never on the same version — do not read the delta as
"3.11.2 → 3.14 server".

## Verify on your own machine

```sh
sha256sum ~/.zcode/server/zcode-server.cjs
sha256sum ~/.zcode/server/agents/glm/zcode.cjs
sha256sum "<ZCode install dir>/resources/app.asar"      # e.g. under Program Files on Windows
```

If the server bundle hash does not match, this follow-up describes a different build than the one
installed on your machine — re-run the probes rather than assuming the results carry over.

## What is deliberately not published

No bundle, no installer, no extracted bundle, no `.asar` payload, no database, no log, no prompt, no
configuration content. Only hashes of program artifacts plus the counts, module names, symbol names
and minimum-necessary excerpts that appear in the documents of this directory.
