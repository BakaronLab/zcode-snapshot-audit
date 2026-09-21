# CURRENT-UPLOAD-SURFACES — source-backed current-state classification

**Purpose.** State plainly what network/upload surfaces the frozen official source tree *does* have,
so that "the audited automatic repo-snapshot is not identified" is never misread as "ZCode now has no
upload".

**Two-line summary.**

- **OLD AUTOMATIC REPO SNAPSHOT: not identified.** In the frozen official source tree, no client-side
  automatic workspace-capture → archive → upload implementation is identified, and none of the
  audited symbols, module names or paths is present
  ([SOURCE-CORROBORATION.md](SOURCE-CORROBORATION.md)).
- **OTHER EXPLICIT/NORMAL NETWORK OR UPLOAD SURFACES: still present.** Several are, several are
  user-initiated, and several transmit code, conversation content or files by design. They are
  catalogued below and are not successors to the removed subsystem.

## Evidence classes used here — deliberately kept apart

- **[CONFIRMED-OFFICIAL-SOURCE]** — read directly from `872ad96` / tree `d185a9a`.
- **[OFFICIAL-SOURCE-DOCUMENTATION]** — vendor-authored descriptive prose, chiefly `NOTICE.md`
  §二 "上传接口、对外请求与业务用途" (27,721 B, 70 lines). It is a *description written by the vendor*
  of its own software. **It is documentation, not runtime proof**, and is labelled as such throughout.
  Where a row below rests on `NOTICE.md` alone, that is stated.

Nothing in this file is `[CONFIRMED-RUNTIME]`. No traffic was captured, generated or observed in this
round; the audit made no network calls to ZCode endpoints.

## A. Model and auxiliary model requests — [CONFIRMED-OFFICIAL-SOURCE] + [OFFICIAL-SOURCE-DOCUMENTATION]

Prompts, conversation history, code, diffs, tool results and attachments are sent to the configured
model providers; the vendor documents that some auxiliary calls fire automatically with a task
(compaction, titles, memory, history extraction, AI commit messages, connectivity checks), and that
requests may carry auth material, client environment, and session/request/trace identifiers.
`[OFFICIAL-SOURCE-DOCUMENTATION]` (NOTICE.md §二 row 1).

This is the largest by-design path by which code leaves the machine, and it is the ordinary premise of
an AI coding client. It is not the audited subsystem: the audited finding was an *archive of the
repository, including `.git` metadata, built by the client and uploaded to object storage*, which is a
different mechanism with a different payload and a different destination. The binary audit's F-014/
F-018 findings concerned that archive, not model requests.

Also documented for the same section: an official Anthropic-compatible **model gateway forwarding**
path that re-issues matching requests to a ZCode gateway, preserving method, body, query and headers
including auth; the vendor states this forwarding has no per-request user confirmation and that
gateway-internal handling is outside what its source review covers. `[OFFICIAL-SOURCE-DOCUMENTATION]`
(NOTICE.md §二 row 4).

## B. Conversation sharing — [CONFIRMED-OFFICIAL-SOURCE]

`packages/services/src/conversation-share/` (8 modules, present at HEAD). Source-visible endpoints in
`conversationShareHttpClient.ts`: `/shares/preparations`, `/shares/preparations/{id}/artifacts`,
`/shares/preparations/{id}/confirm`. It reads workspace-contained files through a realpath-checked
artifact source and its directory reads target a `.zcode-share` subdirectory of the workspace.

This is **not** a repository walk: no enumeration, no archive, no manifest, no `.git` collection. It is
user-initiated sharing of selected conversation rows and materialisable attachments. The vendor
documents the disclosure-confirmation ordering (capability query → confirmation timestamp check →
preparation → attachment upload → publish confirmation) and notes that attachments can be sent before
final publication succeeds, and that browsing/importing is not gated on the publish checkbox.
`[OFFICIAL-SOURCE-DOCUMENTATION]` (NOTICE.md §二 row 11).

The binary audit already established this path is semantically unchanged old→new and is **not** a
rewrite of the removed subsystem (`../followup-3.14/UPLOAD-SURFACE-ATTRIBUTION.md`).

## C. Feedback attachments — [CONFIRMED-OFFICIAL-SOURCE]

The residual OSS/upload vocabulary in 3.14.0 belongs here, and the source confirms it
([SOURCE-CORROBORATION.md](SOURCE-CORROBORATION.md) §5): a user submitting feedback → the client
requests an upload credential at `POST /feedback/attachment/upload-credential` → OSS PostObject form
fields → a single caller-supplied file is uploaded to the returned object-storage host. Attachment
kinds are `"log" | "image" | "other"`. The optional log attachment is a bounded ZIP of the
application config directory's `logs` subdirectory (not a workspace), with text passed through
`redactFeedbackText`.

The vendor describes the same flow, including that the log option is off by default, that when ticked
it selects diagnostic files by local mtime and archive rules and processes full file text, and that
text handling does not guarantee screenshots or arbitrary files are redacted.
`[OFFICIAL-SOURCE-DOCUMENTATION]` (NOTICE.md §二 row 13).

## D. Normal file and media handling — [CONFIRMED-OFFICIAL-SOURCE]

- **Prompt attachments** — `packages/services/src/prompt-attachment-transfer/` transfers
  user-attached files to the **execution host** (local host returns a zero-copy path; a remote host
  wrapper stages cross-machine). Direction and destination are the execution environment, not a
  vendor cloud collector. The vendor states the receiver of chunked upload or remote pre-transfer is
  the execution host, that transfer may begin before the send button is pressed, and that this
  cross-environment handling is not publication. `[OFFICIAL-SOURCE-DOCUMENTATION]` (NOTICE.md §二 row 10).
- **Remote media preview** — `packages/desktop/src/host/remoteMediaPreviewProxy*.ts` reads media back
  from that host.
- **Browser-recording artifact materialisation** — `packages/desktop/src/host/browserRecordingArtifactMaterializer.ts`
  takes the short-lived WebM the main process returns and writes it to the workspace, with a
  containment check (`recording outputPath must stay inside the workspace`) and a `.webm` extension
  check; for a remote target it reuses the existing `backend.upload` rather than a Desktop temp path.
  Same class as the bullets above — destination is the execution host, and the payload is a recording
  of the browser session the user chose to record. Listed explicitly because this file's purpose is to
  state what surfaces *are* present, not only the ones that scored highest in a scan.
- **Provider/builtin asset download** — `packages/provider-node/src/zcode-builtin-*.ts` (download
  direction) and the `cloud-content` subsystem, which is **download**-oriented
  (`../followup-3.14/MODULE-CLUSTER-DIFF.md` read its `download(bundle)` / `trustedUrl()` /
  `bundle_download` symbols; note `cloud-content` is in the shipped bundle but **not** in the
  published tree).

## E. Remote deployment, update and installation — [CONFIRMED-OFFICIAL-SOURCE]

`packages/server/src/remote/` — `remoteAssetInstaller.ts` (stages `<componentId>-<ts>-<uuid>.tar.gz`
locally; mode `"local-download-upload"`), `zcodeAgentDevDeploy.ts`
(`uploadDevelopmentOfficialPluginPackage`), `deploy.ts`, `remoteAssetDeployDecision.ts`. Payloads are
**product/plugin assets deployed to a target environment**, not workspace content; the tar.gz files
are the vendor's own component and plugin packages. This is why these modules scored 3/5 on the
behavioural scan and were then read and attributed.

The vendor documents installation, plugin acquisition, remote deployment and update as accessing
repositories, package services, marketplaces, CDNs or update servers, and states that remote
deployment may upload or copy already-local or downloaded components to a target environment.
`[OFFICIAL-SOURCE-DOCUMENTATION]` (NOTICE.md §二 row 14).

## F. Plugins, MCP, hooks and tool network actions — [CONFIRMED-OFFICIAL-SOURCE] + [OFFICIAL-SOURCE-DOCUMENTATION]

`packages/services/src/{mcp-sync,official-mcp,plugin-sync,plugins,hooks,skills,subagents,skill-sync,settings-sync,remote-sync}/`
and `apps/zcode-cli/packages/{core/src/hooks,adapters/src/mcp}/`. Tools, hooks, plugins, MCP servers
and workflows can read task data, upload files or generated artifacts to the services they are
configured with, and change external state. Lifecycle hooks can trigger commands or processes; hook
input may include prompts, working paths, tool arguments, tool results and replies.
`[OFFICIAL-SOURCE-DOCUMENTATION]` (NOTICE.md §一 and §二 rows 6, 14).

These are third-party- or user-configured destinations whose behaviour is not the client's. They are
listed so they are not mistaken for a vendor capture path — and equally so that "no repo snapshot
identified" is not read as "nothing can leave the machine".

## G. Accounts, entitlements, telemetry and update metadata — [CONFIRMED-OFFICIAL-SOURCE]

- **Device identity** — `packages/services/src/device/deviceMid.ts`; sent as an `X-Device-Mid` header
  (`packages/desktop/src/main/manifestUpdateProvider.ts:222`). The source comment describes it as a
  cross-surface device identity read by the billing header, feedback and onboarding. This corroborates
  the original audit's F-025–F-027 attribution of `deviceMid` / `X-Device-Mid`.
- **ARMS RUM telemetry** — `packages/desktop/src/main/appARMSBootstrap.ts` imports
  `@arms/rum-electron`, gated on `ZCODE_TELEMETRY_ENABLED && ZCODE_ARMS_RUM_ENDPOINT`
  (`packages/shared/src/env.ts:57`). `armsUserIdentity.ts` writes `deviceMid` into the RUM
  `user.name`. The literal `sdk.rum.aliyuncs.com` string observed in the desktop payload lives inside
  the third-party `@arms/rum-electron` package, which is not tracked in the tree — which is why the
  tree has no such literal. `aliyuncs.com` appears in the tree only as model provider base URLs
  (`config/provider/zcode-builtin.json`: `dashscope.aliyuncs.com`).
- **Account, plan, order and quota calls** — `packages/services/src/{credential,oauth,usage-stats,coding-plan-subscription,official-mcp}/`.
  `[OFFICIAL-SOURCE-DOCUMENTATION]` (NOTICE.md §二 rows 2–3).

## What is *not* catalogued here, and why

- **Server-side handling of anything sent.** Not observable from a client source tree. **UNKNOWN.**
- **Whether any given feature's declared payload matches its actual payload at runtime.** Source
  reading establishes declared behaviour; it does not establish runtime behaviour.
- **Cloud retention, deletion, or training use.** Not part of this source audit. Where the vendor
  makes such statements, they are **EXTERNAL / VENDOR CLAIMS** and are **not independently verified by
  this source audit**. They are not recorded as confirmed findings here.
- **Earlier builds.** This file describes the frozen 3.14.0-era tree. The original repository's
  findings remain historical findings for the earlier hashed builds.

## Conclusion

The frozen official source tree contains a number of explicit or ordinary network and upload
surfaces — model requests, conversation sharing, feedback attachments, prompt-attachment transfer,
remote deployment, plugin/MCP/hook network actions, accounts and telemetry. **None is the audited
automatic repository-snapshot pipeline**, and none carries that pipeline's signature: an automatic
pre-prompt and task-completion trigger, a recursive workspace and `.git`-metadata enumeration, tar+gzip
archive construction, a manifest with delta tracking, envelope encryption with a server-supplied RSA
key, and upload to object storage via a `/api/v1/snapshot/upload-credential`-style credential.

**Stated plainly, to avoid the overclaim:** the audited automatic repo-snapshot is not identified in
the frozen source tree. That is not a statement that ZCode never sends anything, and it is not a
statement that code no longer reaches any service — §A is a by-design path that sends code to model
providers.
