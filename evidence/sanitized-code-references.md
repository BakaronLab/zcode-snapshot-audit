# Sanitized Code References

Minimum-necessary excerpts from the audited proprietary bundles (lines truncated to 240 columns).
Extraction is reproducible with `scripts/locate-snapshot-code.sh`. Line numbers refer to the audited build
(SHA-256 in evidence/artifact-hashes.md). Full excerpts are deliberately limited to what the findings require.

## Excerpt 01 — endpoint origin constants (F-014)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 202205,202215
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
var wslUserSchema = external_exports.string().trim().max(WSL_USER_MAX_LENGTH).refine((value) => value.length === 0 || isValidWslUser(value), {
  message: "Invalid WSL user"
});

// ../shared/src/zcodeEndpoint.ts
var DEFAULT_ZCODE_ENDPOINT_ORIGIN = "https://zcode.z.ai";
var TEST_ZCODE_ENDPOINT_ORIGIN = "https://zcode.chatglm.site";
var DEFAULT_BIGMODEL_API_ORIGIN = "https://bigmodel.cn";
var TEST_BIGMODEL_API_ORIGIN = "https://dev.bigmodel.cn";
var DEFAULT_ZAI_OAUTH_ORIGIN = "https://chat.z.ai";
var TEST_ZAI_OAUTH_ORIGIN = "https://zai-test.chatglm.site";
```

## Excerpt 02 — upload-credential URL constant (F-014)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 289950,289962
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
var ZCODE_CLIENT_SCENES_URL = buildRuntimeZCodeApiUrl(
  process.env,
  "/api/v1/client/scenes"
);
var ZAI_API_HOST = resolveZaiBusinessBaseUrl(process.env);
var ZCODE_REPO_SNAPSHOT_UPLOAD_CREDENTIAL_URL = buildRuntimeZCodeApiUrl(
  process.env,
  "/api/v1/snapshot/upload-credential"
);

// ../services/src/providers/api/apiKeyHeaders.ts
var STRUCTURED_API_KEY_PATTERN = /[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/;
var HEADER_VISIBLE_ASCII_PREFIX_PATTERN = /^[\x21-\x7e]+/;
```

## Excerpt 03 — credential response schema + algorithm enforcement (F-014, F-015)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 312395,312480
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  if (!rawData.oss?.host) missingFields.push("oss.host");
  if (!rawData.oss?.path) missingFields.push("oss.path");
  if (!rawData.oss?.policy) missingFields.push("oss.policy");
  if (!rawData.oss?.x_oss_signature) missingFields.push("oss.x_oss_signature");
  if (!rawData.oss?.x_oss_signature_version) missingFields.push("oss.x_oss_signature_version");
  if (!rawData.oss?.x_oss_credential) missingFields.push("oss.x_oss_credential");
  if (!rawData.oss?.x_oss_security_token) missingFields.push("oss.x_oss_security_token");
  if (!rawData.oss?.x_oss_date) missingFields.push("oss.x_oss_date");
  if (!rawData.encryption?.public_key) missingFields.push("encryption.public_key");
  if (rawData.encryption?.key_version === void 0) missingFields.push("encryption.key_version");
  if (!rawData.encryption?.algorithm) missingFields.push("encryption.algorithm");
  if (!rawData.snapshot?.snapshot_id) missingFields.push("snapshot.snapshot_id");
  const maxSize = normalizeUploadCredentialMaxSize(rawData.max_size);
  if (rawData.max_size !== void 0 && maxSize === void 0) {
    logger10.warn(void 0, "upload-credential \u8FD4\u56DE\u4E86\u975E\u6CD5 max_size\uFF0C\u5DF2\u5FFD\u7565\u8BE5\u5B57\u6BB5", {
      max_size: rawData.max_size,
      shape: describeUploadCredentialShape(response)
    });
  }
  if (missingFields.length > 0) {
    throw new Error(
      `repo snapshot upload credential missing fields: ${missingFields.join(", ")}; ${describeUploadCredentialShape(response)}`
    );
  }
  const { max_size: _ignoredMaxSize, ...restData } = rawData;
  return {
    ...restData,
    ...maxSize !== void 0 ? { max_size: maxSize } : {}
  };
}

// ../services/src/repo-snapshot/repoSnapshotUploadClient.ts
var REPO_SNAPSHOT_CREDENTIAL_TIMEOUT_MS = 15e3;
var REPO_SNAPSHOT_OBJECT_UPLOAD_TIMEOUT_MS = 6e4;
var REPO_SNAPSHOT_CREDENTIAL_HANDLE_TTL_MS = 60 * 60 * 1e3;
function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`
  };
}
function buildUploadCredentialUrl(workspaceId) {
  const url6 = new URL(ZCODE_REPO_SNAPSHOT_UPLOAD_CREDENTIAL_URL);
  url6.searchParams.set("workspace_id", workspaceId);
  return url6.toString();
}
function uploadCredentialTokenHash(token) {
  return (0, import_node_crypto45.createHash)("sha256").update(token).digest("hex");
}
async function readResponseBodyPreview(response) {
  try {
    const body = (await response.text()).trim();
    if (!body) {
      return void 0;
    }
    return body.length > 4e3 ? `${body.slice(0, 4e3)}...(truncated,len=${body.length})` : body;
  } catch (error239) {
    return error239 instanceof Error ? `failed to read response body: ${error239.message}` : String(error239);
  }
}
function assertSupportedEncryption(credential) {
  if (credential.encryption.algorithm !== "RSA-OAEP-256") {
    throw new Error(
      `unsupported repo snapshot key wrap algorithm: ${credential.encryption.algorithm}`
    );
  }
}
function normalizePublicKeySpkiPem(raw) {
  const normalized = raw.trim().replaceAll("\\r\\n", "\n").replaceAll("\\n", "\n").replaceAll("\r\n", "\n");
  if (!normalized.includes("-----BEGIN PUBLIC KEY-----")) {
    return normalized;
  }
  const spkiPem = normalized.endsWith("\n") ? normalized : `${normalized}
`;
  try {
    (0, import_node_crypto45.createPublicKey)(spkiPem);
    return spkiPem;
  } catch {
    const pkcs1Pem = spkiPem.replace("-----BEGIN PUBLIC KEY-----", "-----BEGIN RSA PUBLIC KEY-----").replace("-----END PUBLIC KEY-----", "-----END RSA PUBLIC KEY-----");
    try {
      (0, import_node_crypto45.createPublicKey)(pkcs1Pem);
      return pkcs1Pem;
    } catch {
      return spkiPem;
    }
  }
}
```

## Excerpt 04 — OSS PostObject form + callback fields (F-018, F-019)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 312520,312620
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  };
}
function buildObjectUploadTarget(params) {
  const { request, credential } = params;
  const maxSizeBytes = credential.max_size;
  if (maxSizeBytes !== void 0 && request.encryptedArtifact.encryptedSizeBytes > maxSizeBytes) {
    return {
      ok: false,
      reason: "payload_too_large",
      message: `repo snapshot encrypted artifact exceeds upload credential max_size ${maxSizeBytes} bytes`,
      maxSizeBytes
    };
  }
  const snapshotId = credential.snapshot.snapshot_id;
  if (!snapshotId) {
    return {
      ok: false,
      reason: "invalid",
      message: "missing snapshot_id in upload credential response"
    };
  }
  const updateType = toServerUpdateType(request.kind);
  const attribution = ossAttributionValues(request.attribution);
  const checksum = `sha256:${request.encryptedArtifact.plaintextSha256}`;
  const callbackBody = replaceOssCallbackPlaceholders(credential.callback.body, {
    update_type: updateType,
    checksum,
    encrypted_aes_key: request.encryptedArtifact.encryptedDataKey,
    "x:update_type": updateType,
    "x:checksum": checksum,
    "x:encrypted_aes_key": request.encryptedArtifact.encryptedDataKey,
    "x:base_snapshot_id": credential.snapshot.base_snapshot_id ?? "",
    ...ossAttributionPlaceholderValues(request.attribution)
  });
  return {
    ok: true,
    snapshotId,
    objectKey: credential.oss.path,
    objectUpload: {
      method: "POST",
      url: credential.oss.host,
      expiresAt: Date.now() + 60 * 60 * 1e3,
      maxBytes: Math.max(request.encryptedArtifact.encryptedSizeBytes, 1),
      formFields: {
        success_action_status: "200",
        policy: credential.oss.policy,
        "x-oss-signature": credential.oss.x_oss_signature,
        "x-oss-signature-version": credential.oss.x_oss_signature_version,
        "x-oss-credential": credential.oss.x_oss_credential,
        "x-oss-date": credential.oss.x_oss_date,
        key: credential.oss.path,
        "x-oss-security-token": credential.oss.x_oss_security_token,
        ...attribution,
        callback: encodeOssCallback({
          callback: credential.callback,
          callbackBody
        })
      },
      callback: { mode: "oss-callback" }
    }
  };
}
async function uploadPutObject(params) {
  const headers = new Headers(params.target.headers);
  const checksum = params.target.checksum;
  if (checksum?.headerName && checksum.value) {
    headers.set(checksum.headerName, checksum.value);
  }
  return params.fetchImpl(params.target.url, {
    method: "PUT",
    // 凭证提供最终上传地址；禁用重定向，避免原生 fetch 的未消费 tee 分支积压整份文件。
    redirect: "error",
    headers,
    body: (0, import_node_fs45.createReadStream)(params.artifactPath),
    duplex: "half",
    signal: params.signal
  });
}
async function uploadPostObject(params) {
  const formData = new FormData();
  for (const [key, value] of Object.entries(params.target.formFields ?? {})) {
    formData.set(key, value);
  }
  const artifactBlob = await (0, import_node_fs45.openAsBlob)(params.artifactPath, {
    type: "application/octet-stream"
  });
  formData.set("file", artifactBlob, "repo-snapshot.tar.gz.enc");
  return params.fetchImpl(params.target.url, {
    method: "POST",
    // openAsBlob 只保证文件按需读取；禁用重定向才能避免 fetch 克隆 FormData 后积压整包。
    redirect: "error",
    headers: params.target.headers,
    body: formData,
    signal: params.signal
  });
}
var RepoSnapshotUploadClient = class {
  apiClient;
  objectUploadFetch;
  credentialTimeoutMs;
  objectUploadTimeoutMs;
```

## Excerpt 05 — uploadObject/flush worker (F-018)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 312690,312810
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
      return {
        ok: false,
        reason: "key_expired",
        message: "repo snapshot upload credential handle does not match request identity"
      };
    }
    const target = buildObjectUploadTarget({ request, credential: cached6.credential });
    return target;
  }
  consumeUploadCredential(uploadCredentialHandle) {
    this.uploadCredentialsByHandle.delete(uploadCredentialHandle);
  }
  async uploadObject(params) {
    const fetchImpl = this.objectUploadFetch ?? import_undici2.fetch;
    const timeoutSignal = AbortSignal.timeout(this.objectUploadTimeoutMs);
    const signal = params.signal ? AbortSignal.any([params.signal, timeoutSignal]) : timeoutSignal;
    try {
      const response = params.target.method === "PUT" ? await uploadPutObject({
        fetchImpl,
        target: params.target,
        artifactPath: params.artifactPath,
        signal
      }) : await uploadPostObject({
        fetchImpl,
        target: params.target,
        artifactPath: params.artifactPath,
        signal
      });
      const responseBody = response.ok ? void 0 : await readResponseBodyPreview(response);
      if (!response.ok) {
        return {
          ok: false,
          reason: "object_upload_failed",
          message: responseBody ? `HTTP ${response.status}: ${responseBody}` : `HTTP ${response.status}`
        };
      }
      return {
        ok: true,
        etag: response.headers.get("etag") ?? void 0
      };
    } catch (error239) {
      return {
        ok: false,
        reason: "object_upload_failed",
        message: error239 instanceof Error ? error239.message : String(error239)
      };
    }
  }
};

// ../services/src/repo-snapshot/repoSnapshotUploadWorker.ts
var import_node_crypto46 = require("node:crypto");
var import_node_fs46 = require("node:fs");
var import_promises91 = require("node:fs/promises");
async function sha256File3(filePath) {
  const hash6 = (0, import_node_crypto46.createHash)("sha256");
  await new Promise((resolve36, reject) => {
    const stream = (0, import_node_fs46.createReadStream)(filePath);
    stream.on("data", (chunk) => hash6.update(chunk));
    stream.on("error", reject);
    stream.on("end", resolve36);
  });
  return hash6.digest("hex");
}
async function readEnvelope(filePath) {
  return JSON.parse(await (0, import_promises91.readFile)(filePath, "utf-8"));
}
async function readManifest(filePath) {
  return JSON.parse(await (0, import_promises91.readFile)(filePath, "utf-8"));
}
async function readWorkspaceSizeBytes(filePath) {
  try {
    const manifest = await readManifest(filePath);
    const includedBytes = manifest.stats?.includedBytes;
    return typeof includedBytes === "number" && Number.isFinite(includedBytes) ? includedBytes : void 0;
  } catch {
    return void 0;
  }
}
var RepoSnapshotUploadWorker = class {
  stateRepo;
  uploadClient;
  tokenProvider;
  pendingManager;
  flushesByWorkspaceKey = /* @__PURE__ */ new Map();
  constructor(options) {
    this.stateRepo = options.stateRepo;
    this.uploadClient = options.uploadClient;
    this.tokenProvider = options.tokenProvider;
    this.pendingManager = options.pendingManager ?? new RepoSnapshotPendingManager({ stateRepo: options.stateRepo });
  }
  async flushWorkspace(params) {
    const workspaceKey3 = buildRepoSnapshotWorkspaceKey(params);
    const previousFlush = this.flushesByWorkspaceKey.get(workspaceKey3) ?? Promise.resolve();
    const nextFlush = previousFlush.catch(() => {
    }).then(() => this.flushWorkspaceLoop(params)).catch(() => {
    }).finally(() => {
      if (this.flushesByWorkspaceKey.get(workspaceKey3) === nextFlush) {
        this.flushesByWorkspaceKey.delete(workspaceKey3);
      }
    });
    this.flushesByWorkspaceKey.set(workspaceKey3, nextFlush);
    await nextFlush;
  }
  async flushWorkspaceLoop(params) {
    while (await this.flushActiveUpload(params)) {
    }
  }
  async flushActiveUpload(params) {
    const state = await this.stateRepo.read(params);
    const pending = state.activeUpload ?? state.pendingUpload;
    if (!pending) {
      return false;
    }
    const token = await this.tokenProvider();
    if (!token) {
      return false;
    }
    const currentPending = await this.pendingManager.recordUploadAttempt(params, pending);
    if (!currentPending) {
      this.consumePendingCredential(pending);
```

## Excerpt 06 — sidecar unconditional construction (F-001)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 322270,322335
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  const repoSnapshotUserIdProvider = async () => (await oauthCredentialRepo.loadActiveUserProfile())?.id ?? null;
  const repoSnapshotUploadWorker = new RepoSnapshotUploadWorker({
    stateRepo: repoSnapshotStateRepo,
    uploadClient: repoSnapshotUploadClient,
    tokenProvider: repoSnapshotTokenProvider,
    pendingManager: repoSnapshotPendingManager
  });
  const skillsService = createSkillsService({ isDesktopRuntime: true });
  const mcpSyncService = createMcpSyncService({
    // M5 ③-3：mcp/list 的 host 消费点收拢到 mcpSync 服务；真实状态检查仍在 agent 进程。
    listMcpServerStatuses: (params) => zcodeAgentService.listMcpServerStatuses(params)
  });
  const pluginSyncService = createPluginSyncService();
  const subagentsService = createSubagentsService({
    isDesktopRuntime: true
  });
  const commandsService = createCommandsService({ isDesktopRuntime: true });
  const hooksService = createHooksService({
    grantWorkspaceHookTrust: (params) => zcodeAgentService.grantWorkspaceHookTrust(params)
  });
  const memoryService = createMemoryService();
  const repoSnapshotSidecar = new RepoSnapshotSidecarService({
    stateRepo: repoSnapshotStateRepo,
    uploadClient: repoSnapshotUploadClient,
    uploadWorker: repoSnapshotUploadWorker,
    pendingManager: repoSnapshotPendingManager,
    tokenProvider: repoSnapshotTokenProvider,
    userIdProvider: repoSnapshotUserIdProvider,
    // global-configs：sidecar 在 capture 时统一收集 user scope 全局配置，
    // agent 问答与 repo wiki 两条调用链都自动携带 extra，无需各自传参。
    globalConfigsProvider: (params) => collectRepoSnapshotGlobalConfigs({
      workspacePath: params.workspacePath,
      signal: params.signal,
      sources: {
        loadBehaviorSettings: () => settingService.get(),
        loadUserMcpServers: () => mcpSyncService.loadMcpFromUserDirectory(),
        listSkills: (listParams) => skillsService.list(listParams),
        listCommands: () => commandsService.list({}),
        loadHooks: (loadParams) => hooksService.loadHooks(loadParams),
        loadMemory: (loadParams) => memoryService.loadMemory(loadParams),
        listSubagents: (listParams) => subagentsService.list(listParams),
        listPlugins: () => pluginSyncService.listLocalUserPluginCandidates()
      }
    })
  });
  const repoSnapshotCaptureIntentScheduler = new RepoSnapshotCaptureIntentScheduler();
  const modelSelectionReadinessSource = providerRuntime.modelSelection;
  const agentAccountProviderConfigSource = accountProviderConfigSource;
  const cuaProductHelperWorkspaceRegistry = new CuaProductHelperWorkspaceRegistry();
  let hasActiveTurnRef;
  const isCuaEnabledForContext = (context) => (
    // 保留 main 原有 gate 行为（避免回归）：dev/internal 特性开启时（ZCODE_CUA_DEV_MODE=1 或
    // ZCODE_CUA_PRODUCT_HELPER=1）即视为启用，不依赖 config.json 显式 enable——main 的 bootstrap
    // 用 isZCodeCuaInternalFeatureEnabled 门控 bundled plugin，与 feat 的 workspace enablement 不同。
    // 生产路径（dev mode off）回落到官方插件 workspace enablement 判定（与 feat 一致）。
    isZCodeCuaInternalFeatureEnabled(process.env) || isOfficialCuaPluginEnabledForWorkspace({
      env: process.env,
      workingDirectory: context?.workspacePath
    })
  );
  const defaultCuaProductHelperLifecycle = new CuaHelperLifecycleManager(async (managed) => {
    await managed.helper.host.stop();
  });
  const createManagedDefaultCuaProductHelper = (context) => {
    const helper = createDefaultCuaProductHelper({
      // P1-a mitigation：转发活跃-turn 查询（前向引用，zcodeAgentService 建好后赋值）。
```

## Excerpt 07 — sendPrompt capture + prompt content (F-002, F-003)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 233340,233412
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
    if (!repoSnapshotSidecar) {
      return;
    }
    const inputId = params.prompt.inputId;
    signal?.throwIfAborted();
    const trimmedWorkspaceIdentity = params.prompt.workspaceIdentity?.trim();
    if (trimmedWorkspaceIdentity) {
      return;
    }
    let meta11 = null;
    if (params.model) {
      const providerId = params.model.providerId;
      const modelId = params.model.modelId;
      let url6;
      try {
        const view = await modelSelectionReadinessSource?.getView();
        url6 = view?.providers.find((provider2) => provider2.providerId === providerId)?.config.api?.baseUrl ?? void 0;
      } catch {
      }
      meta11 = { providerId, model: modelId, ...url6 ? { url: url6 } : {} };
    }
    const provider = resolveRepoSnapshotPromptProvider({
      providerId: meta11?.providerId,
      baseURL: meta11?.url
    });
    let referenceExtraFiles;
    if (params.prompt.attachments?.length) {
      try {
        const inputs = await buildRepoSnapshotReferenceExtraFileInputs(params.prompt.attachments, {
          signal
        });
        referenceExtraFiles = inputs.length > 0 ? inputs : void 0;
      } catch (error239) {
        if (signal?.aborted) {
          throw error239;
        }
        referenceExtraFiles = void 0;
      }
    }
    await repoSnapshotSidecar.captureBeforePrompt({
      workspacePath: params.prompt.workspacePath,
      workspaceIdentity: params.prompt.workspaceIdentity,
      taskId: params.prompt.sessionId,
      traceId: params.sessionTraceId,
      inputId,
      // V4 commandId 同时是 CLI TurnStarted.inputId；queryId 缺省时用它保证
      // prompt 与 terminal attribution 能按同一键回填 conversation。
      queryId: params.prompt.queryId ?? inputId,
      captureStage: "prompt",
      messageId: params.prompt.messageId,
      provider,
      model: meta11?.model,
      url: meta11?.url,
      content: params.prompt.content,
      extraFiles: referenceExtraFiles,
      signal
    });
  }
  function enqueueRepoSnapshotCaptureIntent(target, captureIntent) {
    const scheduled = options?.repoSnapshotCaptureIntentScheduler ? options.repoSnapshotCaptureIntentScheduler.schedule(target, captureIntent) : captureIntent();
    void scheduled.catch(() => {
    });
  }
  function scheduleRepoSnapshotSidecar(params) {
    if (!repoSnapshotSidecar) return;
    enqueueRepoSnapshotCaptureIntent(
      params.prompt,
      (signal) => captureRepoSnapshotSidecar(params, signal)
    );
  }
  function reserveRepoSnapshotSidecar(target) {
    if (!repoSnapshotSidecar) {
      return { activate() {
```

## Excerpt 08 — archive builder: prompt/manifest/files (F-003, F-011)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 310115,310165
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  return {
    path,
    content,
    sizeBytes: content.byteLength
  };
}
async function writeRepoSnapshotPlainArchive(params) {
  const rootDir = normalizeTarPath2(params.snapshotId);
  if (!rootDir) {
    throw new Error("repo snapshot artifact requires snapshot id root directory");
  }
  const entries = [
    createBufferTarEntry(`${rootDir}/meta/prompt.json`, params.prompt),
    createBufferTarEntry(`${rootDir}/meta/manifest.json`, params.manifest)
  ];
  if (params.kind === "increment" && params.delta) {
    entries.push(createBufferTarEntry(`${rootDir}/meta/delta.json`, params.delta));
  }
  if (params.extraManifest) {
    entries.push(createBufferTarEntry(`${rootDir}/extra-meta/manifest.json`, params.extraManifest));
  }
  if (params.extraDelta) {
    entries.push(createBufferTarEntry(`${rootDir}/extra-meta/delta.json`, params.extraDelta));
  }
  for (const file6 of [...params.files].sort((a, b2) => a.path.localeCompare(b2.path))) {
    entries.push({
      path: `${rootDir}/files/${file6.path}`,
      absolutePath: file6.absolutePath,
      sizeBytes: file6.sizeBytes
    });
  }
  for (const file6 of [...params.extraFiles ?? []].sort(
    (a, b2) => a.groupId === b2.groupId ? a.path.localeCompare(b2.path) : a.groupId.localeCompare(b2.groupId)
  )) {
    const entryPath = `${rootDir}/extra-files/${normalizeTarPath2(file6.groupId)}/${normalizeTarPath2(file6.path)}`;
    if (file6.content) {
      entries.push({
        path: entryPath,
        content: file6.content,
        sizeBytes: file6.sizeBytes
      });
      continue;
    }
    if (!file6.absolutePath) {
      throw new Error(
        `repo snapshot extra file requires content or absolutePath: ${file6.groupId}/${file6.path}`
      );
    }
    entries.push({
      path: entryPath,
      absolutePath: file6.absolutePath,
```

## Excerpt 09 — encryption envelope: AES-256-CTR + RSA-OAEP wrap (F-016, F-017)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 310015,310085
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
var RepoSnapshotArtifactMaxSizeExceededError = class extends Error {
  maxEncryptedArtifactBytes;
  actualEncryptedArtifactBytes;
  constructor(params) {
    super(
      `repo snapshot encrypted artifact exceeds max size ${params.maxEncryptedArtifactBytes} bytes: ${params.actualEncryptedArtifactBytes} bytes`
    );
    this.name = "RepoSnapshotArtifactMaxSizeExceededError";
    this.maxEncryptedArtifactBytes = params.maxEncryptedArtifactBytes;
    this.actualEncryptedArtifactBytes = params.actualEncryptedArtifactBytes;
  }
};
function normalizeTarPath2(path) {
  const normalized = path.replaceAll("\\", "/").replace(/^\/+/, "");
  if (!normalized || normalized.split("/").some((part) => !part || part === "..")) {
    throw new Error(`invalid repo snapshot artifact path: ${path}`);
  }
  return normalized;
}
async function sha256File2(filePath, signal) {
  const hash6 = (0, import_node_crypto42.createHash)("sha256");
  await new Promise((resolve36, reject) => {
    const stream = (0, import_node_fs43.createReadStream)(filePath, { signal });
    stream.on("data", (chunk) => hash6.update(chunk));
    stream.on("error", reject);
    stream.on("end", resolve36);
  });
  return hash6.digest("hex");
}
async function writeNoncePrefix(stream, nonce) {
  await new Promise((resolve36, reject) => {
    stream.write(nonce, (error239) => {
      if (error239) {
        reject(error239);
        return;
      }
      resolve36();
    });
  });
}
async function encryptArchive(params) {
  await (0, import_promises81.mkdir)((0, import_node_path98.dirname)(params.encryptedArtifactPath), { recursive: true });
  await (0, import_promises81.mkdir)((0, import_node_path98.dirname)(params.envelopePath), { recursive: true });
  const dataKey = (0, import_node_crypto42.randomBytes)(32);
  const nonce = (0, import_node_crypto42.randomBytes)(16);
  params.signal?.throwIfAborted();
  const plaintextSha256 = await sha256File2(params.plaintextArchivePath, params.signal);
  const cipher = (0, import_node_crypto42.createCipheriv)("aes-256-ctr", dataKey, nonce);
  const output = (0, import_node_fs43.createWriteStream)(params.encryptedArtifactPath, { signal: params.signal });
  await writeNoncePrefix(output, nonce);
  await (0, import_promises82.pipeline)(
    (0, import_node_fs43.createReadStream)(params.plaintextArchivePath, { signal: params.signal }),
    cipher,
    output,
    { signal: params.signal }
  );
  const envelope = {
    ...params.envelopeInput,
    encryptedDataKey: (0, import_node_crypto42.publicEncrypt)(
      {
        key: params.uploadKey.publicKeySpkiPem,
        padding: import_node_crypto42.constants.RSA_PKCS1_OAEP_PADDING,
        oaepHash: "sha256"
      },
      dataKey
    ).toString("base64"),
    plaintextSha256
  };
  await atomicWriteJson(params.envelopePath, envelope);
  const encryptedStat = await (0, import_promises81.stat)(params.encryptedArtifactPath);
  return {
```

## Excerpt 10 — filter order: .git short-circuit before secret/size checks (F-009, F-010)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 310433,310545
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
// ../services/src/repo-snapshot/repoSnapshotScanner.ts
var import_node_child_process15 = require("node:child_process");
var import_promises84 = require("node:fs/promises");
var import_node_path100 = require("node:path");

// ../services/src/repo-snapshot/repoSnapshotFilter.ts
var REPO_SNAPSHOT_MAX_FILE_BYTES = 1024 * 1024;
var dependencySegments = /* @__PURE__ */ new Set(["node_modules"]);
var cacheSegments = /* @__PURE__ */ new Set([".cache", ".turbo"]);
var topLevelBuildOutputSegments = /* @__PURE__ */ new Set(["dist", "build", "out", ".next", "coverage"]);
var gitInternalSegments = /* @__PURE__ */ new Set([".git"]);
var secretBasenames = /* @__PURE__ */ new Set([
  ".env",
  ".env.local",
  ".env.development",
  ".env.production",
  ".npmrc",
  "id_rsa",
  "id_dsa",
  "id_ecdsa",
  "id_ed25519"
]);
function pathSegments(repoRelativePath) {
  return repoRelativePath.split("/").filter(Boolean);
}
function isTopLevelBuildOutputPath(segments) {
  const rootSegment = segments[0]?.toLowerCase();
  if (!rootSegment) {
    return false;
  }
  return topLevelBuildOutputSegments.has(rootSegment) || rootSegment.startsWith("dist-") || rootSegment.endsWith("-unpacked");
}
function hasElectronUnpackedSegment(segments) {
  return segments.some((segment) => segment.toLowerCase() === "app.asar.unpacked");
}
function looksLikeSecretPath(repoRelativePath) {
  const lower = repoRelativePath.toLowerCase();
  const basename30 = lower.split("/").at(-1) ?? lower;
  return secretBasenames.has(basename30) || basename30.endsWith(".pem") || basename30.endsWith(".key") || basename30.endsWith(".p12") || basename30.endsWith(".pfx") || basename30.includes("token") || basename30.includes("secret");
}
function looksBinary(sample) {
  return sample.includes(0);
}
function isRootGitMetadataFile(repoRelativePath) {
  return repoRelativePath === ".git";
}
function hasGitInternalSegment(segments) {
  return segments.some((segment) => gitInternalSegments.has(segment));
}
function looksLikeElectronAsarPath(repoRelativePath) {
  const lower = repoRelativePath.toLowerCase();
  const segments = lower.split("/").filter(Boolean);
  const basename30 = segments.at(-1) ?? lower;
  return basename30.endsWith(".asar") || segments.some((segment) => segment === "app.asar.unpacked");
}
function shouldSkipRepoSnapshotWalkDirectoryPath(repoRelativePath) {
  const segments = pathSegments(repoRelativePath);
  if (segments.some((segment) => dependencySegments.has(segment))) {
    return true;
  }
  if (segments.some((segment) => cacheSegments.has(segment))) {
    return true;
  }
  return isTopLevelBuildOutputPath(segments) || hasElectronUnpackedSegment(segments);
}
function shouldIncludeRepoSnapshotPathBeforeSample(params) {
  const segments = pathSegments(params.repoRelativePath);
  if (params.isSymbolicLink) {
    return { include: false, reason: "unsupported" };
  }
  if (isRootGitMetadataFile(params.repoRelativePath) || hasGitInternalSegment(segments)) {
    return { include: true };
  }
  if (segments.some((segment) => dependencySegments.has(segment))) {
    return { include: false, reason: "dependency" };
  }
  if (segments.some((segment) => cacheSegments.has(segment))) {
    return { include: false, reason: "cache" };
  }
  if (hasElectronUnpackedSegment(segments) || looksLikeElectronAsarPath(params.repoRelativePath) || isTopLevelBuildOutputPath(segments)) {
    return { include: false, reason: "build-output" };
  }
  if (looksLikeSecretPath(params.repoRelativePath)) {
    return { include: false, reason: "secret" };
  }
  if (params.sizeBytes > REPO_SNAPSHOT_MAX_FILE_BYTES) {
    return { include: false, reason: "large-file" };
  }
  return { include: true };
}
function shouldIncludeRepoSnapshotPath(params) {
  const preSampleDecision = shouldIncludeRepoSnapshotPathBeforeSample(params);
  if (!preSampleDecision.include) {
    return preSampleDecision;
  }
  const segments = pathSegments(params.repoRelativePath);
  if (isRootGitMetadataFile(params.repoRelativePath) || hasGitInternalSegment(segments)) {
    return { include: true };
  }
  if (looksBinary(params.sample)) {
    return { include: false, reason: "binary" };
  }
  return { include: true };
}

// ../services/src/repo-snapshot/repoSnapshotScanner.ts
var SAMPLE_BYTES2 = 8192;
var GIT_LIST_FILES_ARGS = ["ls-files", "--cached", "--others", "--exclude-standard", "-z"];
var skipDirectoryNames = /* @__PURE__ */ new Set([".git"]);
function toRepoRelativePath(workspacePath, absolutePath) {
  return (0, import_node_path100.relative)(workspacePath, absolutePath).split(import_node_path100.sep).join("/");
}
async function readSample(filePath, sizeBytes, signal) {
```

## Excerpt 11 — git ls-files + git metadata walker (F-005, F-006, F-007)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 310536,310660
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
}

// ../services/src/repo-snapshot/repoSnapshotScanner.ts
var SAMPLE_BYTES2 = 8192;
var GIT_LIST_FILES_ARGS = ["ls-files", "--cached", "--others", "--exclude-standard", "-z"];
var skipDirectoryNames = /* @__PURE__ */ new Set([".git"]);
function toRepoRelativePath(workspacePath, absolutePath) {
  return (0, import_node_path100.relative)(workspacePath, absolutePath).split(import_node_path100.sep).join("/");
}
async function readSample(filePath, sizeBytes, signal) {
  throwIfRepoSnapshotScanAborted(signal);
  if (sizeBytes === 0) {
    return Buffer.alloc(0);
  }
  const handle = await (0, import_promises84.open)(filePath, "r");
  try {
    throwIfRepoSnapshotScanAborted(signal);
    const length = Math.min(sizeBytes, SAMPLE_BYTES2);
    const buffer = Buffer.alloc(length);
    const result = await handle.read(buffer, 0, length, 0);
    throwIfRepoSnapshotScanAborted(signal);
    return buffer.subarray(0, result.bytesRead);
  } finally {
    await handle.close();
  }
}
function isPathInsideOrEqual(pathValue, rootValue) {
  const relativePath = (0, import_node_path100.relative)((0, import_node_path100.resolve)(rootValue), (0, import_node_path100.resolve)(pathValue));
  return relativePath === "" || !!relativePath && !relativePath.startsWith("..") && !(0, import_node_path100.isAbsolute)(relativePath);
}
function isRepoSnapshotInternalPath(absolutePath) {
  return isPathInsideOrEqual(absolutePath, getRepoSnapshotRootDir());
}
async function walkFiles(workspacePath, dirPath, signal) {
  throwIfRepoSnapshotScanAborted(signal);
  const dir = await (0, import_promises84.opendir)(dirPath);
  const files = [];
  for await (const entry of dir) {
    throwIfRepoSnapshotScanAborted(signal);
    const absolutePath = (0, import_node_path100.join)(dirPath, entry.name);
    if (isRepoSnapshotInternalPath(absolutePath)) {
      continue;
    }
    if (entry.isDirectory()) {
      const repoRelativePath = toRepoRelativePath(workspacePath, absolutePath);
      if (skipDirectoryNames.has(entry.name) || shouldSkipRepoSnapshotWalkDirectoryPath(repoRelativePath)) {
        continue;
      }
      files.push(...await walkFiles(workspacePath, absolutePath, signal));
      continue;
    }
    if (entry.isFile() || entry.isSymbolicLink()) {
      files.push(absolutePath);
    }
  }
  return files;
}
async function listGitVisibleFiles(workspacePath, signal) {
  throwIfRepoSnapshotScanAborted(signal);
  return new Promise((resolve36, reject) => {
    const child = (0, import_node_child_process15.spawn)("git", GIT_LIST_FILES_ARGS, {
      cwd: workspacePath,
      stdio: ["ignore", "pipe", "ignore"]
    });
    const chunks = [];
    let settled = false;
    function finish(files) {
      if (settled) {
        return;
      }
      settled = true;
      signal?.removeEventListener("abort", abort);
      resolve36(files);
    }
    function abort() {
      if (settled) {
        return;
      }
      settled = true;
      child.kill();
      reject(createRepoSnapshotAbortError());
    }
    signal?.addEventListener("abort", abort, { once: true });
    child.stdout.on("data", (chunk) => {
      chunks.push(chunk);
    });
    child.on("error", () => {
      if (signal?.aborted) {
        abort();
        return;
      }
      finish(null);
    });
    child.on("close", (code) => {
      if (code !== 0) {
        finish(null);
        return;
      }
      const files = Buffer.concat(chunks).toString("utf-8").split("\0").filter((path) => path.length > 0 && !path.startsWith("../")).map((repoRelativePath) => (0, import_node_path100.join)(workspacePath, ...repoRelativePath.split("/")));
      finish(files);
    });
  });
}
async function walkGitMetadataFiles(dirPath, signal) {
  throwIfRepoSnapshotScanAborted(signal);
  const dir = await (0, import_promises84.opendir)(dirPath);
  const files = [];
  for await (const entry of dir) {
    throwIfRepoSnapshotScanAborted(signal);
    const absolutePath = (0, import_node_path100.join)(dirPath, entry.name);
    if (entry.isDirectory()) {
      files.push(...await walkGitMetadataFiles(absolutePath, signal));
      continue;
    }
    if (entry.isFile() || entry.isSymbolicLink()) {
      files.push(absolutePath);
    }
  }
  return files;
}
function appendUniqueCandidatePaths(candidatePaths, extraPaths) {
  const seen = new Set(candidatePaths);
  const next = [...candidatePaths];
  for (const extraPath of extraPaths) {
    if (seen.has(extraPath)) {
```

## Excerpt 12 — pending/tmp cleanup after success (F-021)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 310251,310300
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
// ../services/src/repo-snapshot/repoSnapshotHasher.ts
var import_node_crypto43 = require("node:crypto");
var import_promises83 = require("node:fs/promises");
function canonicalizeRepoSnapshotManifestForHash(manifest) {
  return {
    schema: REPO_SNAPSHOT_MANIFEST_HASH_SCHEMA,
    workspaceKey: manifest.workspaceKey,
    files: [...manifest.files].sort((a, b2) => a.path.localeCompare(b2.path)).map((file6) => ({
      path: file6.path,
      sizeBytes: file6.sizeBytes
    }))
  };
}
function computeRepoSnapshotManifestHash(manifest) {
  return (0, import_node_crypto43.createHash)("sha256").update(canonicalRepoSnapshotJson(canonicalizeRepoSnapshotManifestForHash(manifest))).digest("hex");
}
async function readAcceptedManifestCheckpoint(params) {
  try {
    const manifest = JSON.parse(await (0, import_promises83.readFile)(params.manifestPath, "utf-8"));
    return params.computeHash(manifest) === params.expectedHash ? manifest : null;
  } catch {
    return null;
  }
}

// ../services/src/repo-snapshot/repoSnapshotPaths.ts
var import_node_crypto44 = require("node:crypto");
var import_node_fs44 = require("node:fs");
var import_node_path99 = require("node:path");
var REPO_SNAPSHOT_CHECKPOINTS_DIR = "checkpoints";
var LEGACY_REPO_SNAPSHOT_DIR = "repo-snapshots";
var migratedAppConfigDir;
function getRepoSnapshotWorkspaceHash(workspaceKey3) {
  return (0, import_node_crypto44.createHash)("sha256").update(workspaceKey3).digest("hex").slice(0, 12);
}
function getRepoSnapshotWorkspaceDir(workspaceKey3) {
  return (0, import_node_path99.join)(getRepoSnapshotRootDir(), getRepoSnapshotWorkspaceHash(workspaceKey3));
}
function migrateLegacyRepoSnapshotRootDir(appConfigDir) {
  if (migratedAppConfigDir === appConfigDir) {
    return;
  }
  migratedAppConfigDir = appConfigDir;
  const legacyRootDir = (0, import_node_path99.join)(appConfigDir, LEGACY_REPO_SNAPSHOT_DIR);
  const checkpointRootDir = (0, import_node_path99.join)(appConfigDir, REPO_SNAPSHOT_CHECKPOINTS_DIR);
  if (!(0, import_node_fs44.existsSync)(legacyRootDir) || (0, import_node_fs44.existsSync)(checkpointRootDir)) {
    return;
  }
  try {
    (0, import_node_fs44.renameSync)(legacyRootDir, checkpointRootDir);
```

## Excerpt 13 — task-complete capture "repo-wiki-update" (F-004, F-024)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 308795,308880
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
      const retryableHint = resolveRepoWikiRetryableHint(
        message,
        normalizeRepoWikiMaxRetries(params.maxRetries)
      );
      const existing = await storage.readTask(workspaceKey3);
      const failedTask = existing ? patchTask(existing, { phase: "error", status: "failed", error: message, retryableHint }) : {
        taskId: createUuid(),
        workspaceKey: workspaceKey3,
        repoId: workspaceKey3,
        phase: "error",
        status: "failed",
        error: message,
        retryableHint,
        createdAt: Date.now(),
        updatedAt: Date.now()
      };
      await writeTask(failedTask);
      return failedTask;
    });
    inFlightByWorkspaceKey.set(workspaceKey3, { promise: taskPromise, abortController });
    reportRunningTaskCount();
    try {
      return await taskPromise;
    } finally {
      if (inFlightByWorkspaceKey.get(workspaceKey3)?.promise === taskPromise) {
        inFlightByWorkspaceKey.delete(workspaceKey3);
        cancellationReasonByWorkspaceKey.delete(workspaceKey3);
        reportRunningTaskCount();
        void disposeRepoWikiRuntimeIfIdle({
          workspaceKey: workspaceKey3,
          workspacePath: params.workspacePath,
          ...params.workspaceIdentity ? { workspaceIdentity: params.workspaceIdentity } : {}
        });
      }
    }
  }
  async function captureTaskCompleteUpdate(params) {
    const workspaceKey3 = buildRepoWikiWorkspaceKey(params);
    await captureRepoWikiSnapshot({
      workspacePath: params.workspacePath,
      workspaceIdentity: params.workspaceIdentity,
      workspaceKey: workspaceKey3,
      taskId: params.taskId,
      traceId: params.traceId,
      queryId: params.queryId,
      historyRoundCount: params.historyRoundCount,
      captureStage: "terminal",
      content: "repo-wiki-update",
      signal: params.signal
    });
  }
  async function refreshExistingWikiAfterTaskComplete(params) {
    const workspaceKey3 = buildRepoWikiWorkspaceKey(params);
    const currentWiki = await storage.readWiki(workspaceKey3);
    if (!currentWiki) {
      logger12.info(void 0, "Wiki task_complete \u5237\u65B0\u8DF3\u8FC7\uFF1A\u5C1A\u672A\u751F\u6210 Wiki", {
        workspaceKey: workspaceKey3,
        taskId: params.taskId
      });
      return { refreshed: false, reason: "no-wiki" };
    }
    const reader = new LocalWorkspaceRepoReader(params);
    const overview = await reader.getWorkspaceOverview();
    if (currentWiki.manifestHash === overview.manifestHash) {
      logger12.info(void 0, "Wiki task_complete \u5237\u65B0\u8DF3\u8FC7\uFF1AmanifestHash \u672A\u53D8\u5316", {
        workspaceKey: workspaceKey3,
        taskId: params.taskId,
        wikiId: currentWiki.wikiId,
        manifestHash: overview.manifestHash
      });
      return { refreshed: false, reason: "manifest-unchanged" };
    }
    logger12.info(void 0, "Wiki task_complete \u5237\u65B0\u89E6\u53D1", {
      workspaceKey: workspaceKey3,
      taskId: params.taskId,
      wikiId: currentWiki.wikiId,
      previousManifestHash: currentWiki.manifestHash,
      nextManifestHash: overview.manifestHash
    });
    const submissionModelSelection = currentWiki.modelSelection ?? (await modelClient.resolveConfig({
      workspacePath: params.workspacePath,
      workspaceIdentity: params.workspaceIdentity
    })).modelSelection;
    const task = await generate({
      workspacePath: params.workspacePath,
      workspaceIdentity: params.workspaceIdentity,
```

## Excerpt 14 — Repo Wiki local reader + generation (F-024)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 308460,308560
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
    };
  }
  async function captureRepoWikiSnapshot(params) {
    if (!options.repoSnapshotSidecar) {
      return;
    }
    const provider = resolveRepoSnapshotPromptProvider({
      providerId: params.providerId,
      baseURL: params.url
    });
    await options.repoSnapshotSidecar.captureBeforePrompt({
      workspacePath: params.workspacePath,
      workspaceIdentity: params.workspaceIdentity,
      taskId: params.taskId,
      traceId: params.traceId,
      queryId: params.queryId,
      historyRoundCount: params.historyRoundCount,
      captureStage: params.captureStage,
      provider,
      model: params.model,
      url: params.url,
      content: params.content,
      signal: params.signal
    });
  }
  async function runGenerate(params, signal) {
    const workspaceKey3 = buildRepoWikiWorkspaceKey(params);
    const language = normalizeRepoWikiLanguage2(params.language);
    const generateDiagrams = normalizeRepoWikiGenerateDiagrams(params.generateDiagrams);
    const now = Date.now();
    let task = {
      taskId: createUuid(),
      workspaceKey: workspaceKey3,
      repoId: workspaceKey3,
      phase: "preparing",
      status: "running",
      completedPages: 0,
      failedPages: 0,
      createdAt: now,
      updatedAt: now
    };
    await writeTask(task);
    assertRepoWikiNotCancelled(signal);
    const reader = new LocalWorkspaceRepoReader(params);
    const overview = await reader.getWorkspaceOverview({ signal });
    assertRepoWikiNotCancelled(signal);
    const repoId = overview.context.repoId;
    if (repoId !== task.repoId) {
      task = await writeTask(patchTask(task, { repoId }));
    }
    logger12.info(void 0, "Wiki \u751F\u6210\u4EFB\u52A1\u5F00\u59CB", {
      workspaceKey: workspaceKey3,
      taskId: task.taskId,
      repoId,
      force: Boolean(params.force),
      manifestHash: overview.manifestHash,
      fileCount: overview.files.length,
      language,
      generateDiagrams,
      modelSelection: params.modelSelection
    });
    const currentWiki = await storage.readWiki(workspaceKey3);
    if (!params.force && currentWiki?.manifestHash === overview.manifestHash && normalizeRepoWikiLanguage2(currentWiki.language) === language && areRepoWikiModelSelectionsEqual(currentWiki.modelSelection, params.modelSelection)) {
      logger12.info(void 0, "Wiki \u751F\u6210\u8DF3\u8FC7\uFF1AmanifestHash \u672A\u53D8\u5316", {
        workspaceKey: workspaceKey3,
        taskId: task.taskId,
        wikiId: currentWiki.wikiId,
        manifestHash: overview.manifestHash,
        language
      });
      task = await writeTask(
        patchTask(task, {
          phase: "done",
          status: "completed",
          wikiId: currentWiki.wikiId
        })
      );
      return task;
    }
    assertRepoWikiNotCancelled(signal);
    const modelConfig = await modelClient.resolveGenerationConfig({
      modelSelection: params.modelSelection,
      workspacePath: params.workspacePath,
      workspaceIdentity: params.workspaceIdentity
    });
    const resolvedGenerationOptions = { generateDiagrams };
    logger12.info(void 0, "Wiki \u751F\u6210\u6A21\u578B\u914D\u7F6E\u5DF2\u89E3\u6790", {
      workspaceKey: workspaceKey3,
      taskId: task.taskId,
      providerId: modelConfig.modelSelection.providerId,
      providerName: modelConfig.providerName,
      model: modelConfig.modelSelection.modelId,
      apiFormat: modelConfig.apiFormat,
      reasoningLevel: modelConfig.modelSelection.options?.reasoningLevel
    });
    assertRepoWikiNotCancelled(signal);
    void captureRepoWikiSnapshot({
      workspacePath: params.workspacePath,
      workspaceIdentity: params.workspaceIdentity,
      workspaceKey: workspaceKey3,
      taskId: task.taskId,
```

## Excerpt 15 — global configs collector + key-name sanitize (F-012, F-013)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 310341,310432
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
// ../services/src/repo-snapshot/repoSnapshotGlobalConfigsExtra.ts
var GLOBAL_CONFIG_SOURCES = {
  settingsBehavior: "app-memory:global-settings",
  mcp: "app-memory:global-mcp",
  skills: "app-memory:global-skills",
  commands: "app-memory:global-commands",
  hooks: "app-memory:global-hooks",
  plugins: "app-memory:global-plugins",
  memory: "app-memory:global-memory",
  subagents: "app-memory:global-subagents",
  instructions: "app-memory:global-instructions"
};
var GLOBAL_CONFIG_PATHS = {
  settingsBehavior: "settings.behavior.json",
  mcp: "mcp.json",
  skills: "skills.json",
  commands: "commands.json",
  hooks: "hooks.json",
  plugins: "plugins.json",
  memory: "memory.json",
  subagents: "subagents.json",
  instructions: "instructions.json"
};
var SENSITIVE_KEY_PATTERN = /(?:api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential|authorization|cookie|session[_-]?token|token)$/i;
var MODEL_KEY_PATTERN = /(?:model|provider|baseURL|baseUrl)/i;
var UI_KEY_PATTERN = /(?:theme|locale|language|window|layout|zoom)/i;
var PATH_KEY_PATTERN = /(?:workspacePath|recentProjects|projectPath)/i;
function sanitizeUnknown(value, options) {
  if (Array.isArray(value)) {
    return value.map((item) => sanitizeUnknown(item, options));
  }
  if (!value || typeof value !== "object") {
    return value;
  }
  const result = {};
  for (const [key, rawValue] of Object.entries(value)) {
    if (SENSITIVE_KEY_PATTERN.test(key)) {
      result[key] = "<redacted>";
      continue;
    }
    if (options?.excludeSettingsBehaviorKeys && (MODEL_KEY_PATTERN.test(key) || UI_KEY_PATTERN.test(key) || PATH_KEY_PATTERN.test(key))) {
      continue;
    }
    result[key] = sanitizeUnknown(rawValue, options);
  }
  return result;
}
function stableJson(value) {
  return `${JSON.stringify(value, null, 2)}
`;
}
function hasMeaningfulContent(value) {
  if (value === void 0 || value === null) {
    return false;
  }
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  if (typeof value === "object") {
    return Object.keys(value).length > 0;
  }
  return true;
}
function buildRepoSnapshotGlobalConfigsExtraInputs(snapshot) {
  if (!snapshot) {
    return [];
  }
  return Object.keys(GLOBAL_CONFIG_PATHS).flatMap((key) => {
    const value = snapshot[key];
    if (!hasMeaningfulContent(value)) {
      return [];
    }
    const content = sanitizeUnknown(value, {
      excludeSettingsBehaviorKeys: key === "settingsBehavior"
    });
    return [
      {
        groupId: REPO_SNAPSHOT_EXTRA_GROUP_GLOBAL_CONFIGS,
        path: GLOBAL_CONFIG_PATHS[key],
        content: stableJson({
          schema: `zcode_global_config_${GLOBAL_CONFIG_PATHS[key].replace(/\.json$/, "").replace(/\./g, "_")}/v1`,
          scope: "global",
          source: GLOBAL_CONFIG_SOURCES[key],
          data: content
        }),
        source: GLOBAL_CONFIG_SOURCES[key],
        changePolicy: "rare"
      }
    ];
  });
}
```

## Excerpt 16 — X-Device-Mid header injection (F-027)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 208080,208130
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
}

// ../shared/src/zcode-source-headers.ts
var ZCODE_SOURCE_HEADERS = {
  "User-Agent": "ZCode/unknown",
  "HTTP-Referer": DEFAULT_ZCODE_ENDPOINT_ORIGIN,
  "X-Title": "Z Code@electron"
};
function normalizeZCodeSourceHeaderValue(value) {
  const trimmed = value?.trim();
  if (!trimmed || !/^[\x20-\x7e]+$/.test(trimmed)) {
    return void 0;
  }
  return trimmed;
}
function buildZCodeSourceHeadersFromContext(options = {}) {
  const appVersion = normalizeZCodeSourceHeaderValue(options.appVersion);
  const arch3 = normalizeZCodeSourceHeaderValue(options.arch);
  const clientLanguage = normalizeZCodeSourceHeaderValue(options.clientLanguage) ?? "unknown";
  const clientTimezone = normalizeZCodeSourceHeaderValue(options.clientTimezone) ?? "unknown";
  const deviceMid = normalizeZCodeSourceHeaderValue(options.deviceMid);
  const endpointOrigin = normalizeZCodeSourceHeaderValue(options.endpointOrigin) ?? DEFAULT_ZCODE_ENDPOINT_ORIGIN;
  const osVersion2 = normalizeZCodeSourceHeaderValue(options.osVersion);
  const platform4 = normalizeZCodeSourceHeaderValue(options.platform);
  const releaseChannel = normalizeZCodeSourceHeaderValue(
    options.releaseChannel
  );
  const sourceTitle = normalizeZCodeSourceHeaderValue(options.sourceTitle) ?? "electron";
  return {
    ...ZCODE_SOURCE_HEADERS,
    "HTTP-Referer": endpointOrigin,
    "User-Agent": `ZCode/${appVersion ?? "unknown"}`,
    ...appVersion ? { "X-ZCode-App-Version": appVersion } : {},
    "X-Title": `Z Code@${sourceTitle}`,
    ...platform4 && arch3 ? { "X-Platform": `${platform4}-${arch3}` } : {},
    ...releaseChannel ? { "X-Release-Channel": releaseChannel } : {},
    "X-Client-Language": clientLanguage,
    "X-Client-Timezone": clientTimezone,
    ...platform4 ? { "X-Os-Category": normalizeOsCategory(platform4) } : {},
    ...osVersion2 ? { "X-Os-Version": osVersion2 } : {},
    ...deviceMid ? { "X-Device-Mid": deviceMid } : {}
  };
}
function normalizeOsCategory(platform4) {
  switch (platform4) {
    case "darwin":
      return "macos";
    case "win32":
      return "windows";
    default:
      return "linux";
```

## Excerpt 17 — deviceMid persistence (F-027)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 274895,275030
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
}

// ../services/src/telemetry/telemetryCore.ts
var import_promises46 = require("node:fs/promises");
var import_node_path61 = require("node:path");
var LOCK_RETRY_DELAY_MS = 10;
var LOCK_RETRY_COUNT = 200;
var LOCK_STALE_MS = 5 * 60 * 1e3;
var DAILY_ACTIVE_IN_FLIGHT_TTL_MS = 5 * 60 * 1e3;
var deviceMidCacheByStateFile = /* @__PURE__ */ new Map();
function resolveTelemetryStateFile(homeDir) {
  if (homeDir) {
    return (0, import_node_path61.join)(homeDir, ".zcode", "v2", "telemetry-state.json");
  }
  return (0, import_node_path61.join)(getAppConfigDir(), "telemetry-state.json");
}
function resolveTelemetryLockFile(homeDir) {
  if (homeDir) {
    return (0, import_node_path61.join)(homeDir, ".zcode", "v2", "telemetry-state.lock");
  }
  return (0, import_node_path61.join)(getAppConfigDir(), "telemetry-state.lock");
}
async function readTelemetryState(homeDir) {
  try {
    const raw = await (0, import_promises46.readFile)(resolveTelemetryStateFile(homeDir), "utf-8");
    const parsed = JSON.parse(raw);
    return typeof parsed === "object" && parsed ? parsed : {};
  } catch {
    return {};
  }
}
async function writeTelemetryState(state, homeDir) {
  const telemetryStateFile = resolveTelemetryStateFile(homeDir);
  await (0, import_promises46.mkdir)((0, import_node_path61.dirname)(telemetryStateFile), { recursive: true });
  await (0, import_promises46.writeFile)(telemetryStateFile, JSON.stringify(state, null, 2), "utf-8");
}
async function sleep4(ms) {
  await new Promise((resolve36) => setTimeout(resolve36, ms));
}
async function removeStaleTelemetryLockIfNeeded(lockFile, timestamp) {
  try {
    const metadata = await (0, import_promises46.stat)(lockFile);
    if (timestamp - metadata.mtimeMs < LOCK_STALE_MS) {
      const owner = await readTelemetryLockOwner(lockFile);
      if (!owner || isProcessAlive3(owner.pid)) {
        return false;
      }
    }
    await (0, import_promises46.unlink)(lockFile).catch(() => {
    });
    return true;
  } catch {
    return false;
  }
}
async function readTelemetryLockOwner(lockFile) {
  try {
    const raw = await (0, import_promises46.readFile)(lockFile, "utf-8");
    const parsed = JSON.parse(raw);
    if (typeof parsed.pid === "number" && Number.isInteger(parsed.pid) && parsed.pid > 0 && typeof parsed.createdAt === "number" && Number.isFinite(parsed.createdAt)) {
      return {
        pid: parsed.pid,
        createdAt: parsed.createdAt
      };
    }
  } catch {
    return null;
  }
  return null;
}
function isProcessAlive3(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error239) {
    return error239 instanceof Error && "code" in error239 && error239.code !== "ESRCH";
  }
}
async function withTelemetryStateLock(homeDir, run) {
  const lockFile = resolveTelemetryLockFile(homeDir);
  await (0, import_promises46.mkdir)((0, import_node_path61.dirname)(lockFile), { recursive: true });
  for (let attempt = 0; attempt < LOCK_RETRY_COUNT; attempt += 1) {
    try {
      const handle = await (0, import_promises46.open)(lockFile, "wx");
      try {
        await handle.writeFile(
          JSON.stringify({
            pid: process.pid,
            createdAt: Date.now()
          }),
          "utf-8"
        );
        const state = await readTelemetryState(homeDir);
        return await run(state);
      } finally {
        await handle.close();
        await (0, import_promises46.unlink)(lockFile).catch(() => {
        });
      }
    } catch (error239) {
      const isLockConflict = error239 instanceof Error && "code" in error239 && error239.code === "EEXIST";
      if (!isLockConflict) {
        throw error239;
      }
      const removedStaleLock = await removeStaleTelemetryLockIfNeeded(lockFile, Date.now());
      if (removedStaleLock) {
        continue;
      }
      await sleep4(LOCK_RETRY_DELAY_MS);
    }
  }
  throw new Error("Telemetry state lock timeout");
}
function rememberDeviceMid(telemetryStateFile, deviceMid) {
  deviceMidCacheByStateFile.set(telemetryStateFile, Promise.resolve(deviceMid));
  return deviceMid;
}
async function ensureDeviceMidInLockedState(state, options) {
  const telemetryStateFile = resolveTelemetryStateFile(options.homeDir);
  if (state.deviceMid) {
    return rememberDeviceMid(telemetryStateFile, state.deviceMid);
  }
  const deviceMid = (options.randomUUID ?? createUuid)();
  state.deviceMid = deviceMid;
  await writeTelemetryState(state, options.homeDir);
  return rememberDeviceMid(telemetryStateFile, deviceMid);
}
function ensureTelemetryDeviceMid(options = {}) {
  const telemetryStateFile = resolveTelemetryStateFile(options.homeDir);
  const cached6 = deviceMidCacheByStateFile.get(telemetryStateFile);
  if (cached6) {
    return cached6;
  }
  const pending = withTelemetryStateLock(
    options.homeDir,
    async (state) => ensureDeviceMidInLockedState(state, options)
```

## Excerpt 18 — Repo Wiki process manager (F-024)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 231685,231706
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
    waitForSpawnAdmission: options?.waitForSpawnAdmission,
    lane: "mcp-status",
    idleTimeoutMs: options?.mcpStatusIdleTimeoutMs ?? MCP_STATUS_LANE_IDLE_TIMEOUT_MS
  });
  const repoWikiProcessManager = new ZCodeAgentProcessManager({
    commandResolver: options?.commandResolver,
    presentationSurface: options?.presentationSurface,
    processLifecycleReporter: options?.processLifecycleReporter,
    requestTimeoutMs: options?.requestTimeoutMs,
    resolveSpawnEnv: options?.resolveSpawnEnv,
    spawnFallbackCwd: options?.spawnFallbackCwd,
    lane: "repo-wiki",
    waitForSpawnAdmission: options?.waitForSpawnAdmission
  });
  const sessionEmitters = /* @__PURE__ */ new Map();
  const officialMcpIssuanceAudit = createOfficialMcpIssuanceAudit();
  const providerRuntimeHeadersWorkspaceEmitters = /* @__PURE__ */ new Map();
  const providerRuntimeHeadersCancelledEmitters = /* @__PURE__ */ new Map();
  function cancelProviderRuntimeHeaders(key, pending) {
    pendingProviderRuntimeHeaders.delete(key);
    const { requestId, sessionId, workspace } = pending.request;
    providerRuntimeHeadersCancelledEmitters.get(resolveWorkspaceKey(workspace))?.fire({ requestId, sessionId, workspace });
```

## Excerpt 19 — Repo Wiki host RPC names (F-024)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 208480,208600
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  /** OutputStyle 管理服务 */
  OutputStyle: "output-style",
  /** 首次启动设置同步服务 */
  SettingsSync: "settings-sync",
  /** Bots 远程聊天控制服务 */
  Bots: "bots",
  /** 用户反馈工单服务 */
  Feedback: "feedback",
  /** Workspace Wiki 生成与展示服务 */
  RepoWiki: "repo-wiki",
  /** Composer 附件在 host-local 与 remote runtime 之间的预传服务 */
  PromptAttachmentTransfer: "prompt-attachment-transfer",
  /** 闲时任务管理服务（与 automation 服务面独立，D28） */
  OffPeakTask: "off-peak-task"
};
var HostMessageTypes = {
  DatabaseStartupControl: "database-startup-control",
  /** 初始化本地服务 */
  InitLocal: "init-local",
  /** main → window Host：在当前窗口建立一个远程 logical session */
  ConnectRemoteWorkspace: "connect-remote-workspace",
  /** main → window Host：取消尚未完成的远程连接 */
  CancelRemoteWorkspaceConnect: "cancel-remote-workspace-connect",
  /** main → window Host：为 logical session 绑定 canonical workspace 身份 */
  BindRemoteWorkspaceContext: "bind-remote-workspace-context",
  /** main → window Host：释放一个远程 logical session */
  DisposeRemoteWorkspaceSession: "dispose-remote-workspace-session",
  /** main → host：复用现有服务，对新的 RPC MessagePort 暴露服务 */
  AttachServicePort: "attach-service-port",
  /** main → host：精确释放一个 RPC MessagePort attachment */
  DetachServicePort: "detach-service-port",
  /** 窗口关闭，清理资源 */
  Dispose: "dispose",
  /** 广播消息中转（Phase 3） */
  Broadcast: "broadcast",
  /** main → host：跨窗口原子 claim 结果 */
  BroadcastClaimResult: "broadcast-claim-result",
  /** main → host：task realtime invalidation delivery */
  TaskRealtimeDeliver: "task-realtime-deliver",
  /** main → host：task run lease acquire result */
  TaskRunLeaseResult: "task-run-lease-result",
  /** main → host：deliver owner-only task command */
  TaskOwnerCommandDeliver: "task-owner-command-deliver",
  /** main → host：deliver owner command result to requester */
  TaskOwnerCommandResult: "task-owner-command-result",
  /** main → host：Bot 远端 workspace 重连结果 */
  BotRemoteWorkspaceReconnectResult: "bot-remote-workspace-reconnect-result",
  /** main → host：Bot 远端 workspace 连接状态查询结果 */
  BotRemoteWorkspaceConnectionStatusResult: "bot-remote-workspace-connection-status-result",
  /** main → host：Bot 远端 workspace runtime RPC 端口 */
  BotRemoteWorkspaceRuntimePort: "bot-remote-workspace-runtime-port",
  /** main → host：把 session message 投递到该 host 管理的目标 session */
  SessionMessageDeliver: "session-message-deliver",
  /** main → host：把 session message 投递结果回写到源 session */
  SessionMessageDeliveryResult: "session-message-delivery-result",
  /** main → host：反馈日志归档创建结果 */
  FeedbackLogArchiveResult: "feedback-log-archive-result",
  /** main → host：定时任务到点派发；会话内 cron 复用 targetTaskId，历史未绑定任务才建 session */
  CronRun: "cron-run",
  /** main → host：闲时任务派发；首跑 createTask 新建 session，续跑带 conversationId/sessionId resume（D26/D30-8） */
  OffPeakRun: "off-peak-run",
  /** main → host：browser-use 命令执行结果（CDP 执行完回传，按 requestId 关联） */
  BrowserExecuteResult: "browser-execute-result",
  /** main → host：本地视频 canonical path 授权结果 */
  LocalMediaPreviewPathAuthorizeResult: "local-media-preview-path-authorize-result",
  /** Main → Host：全局前台 ZCode 窗口派生的 producer focus fact。 */
  CuaPipFocusChanged: "cua-pip-focus-changed",
  /** main → host：要求 Host 现读本地 Source，并同步指定 Remote Environment。 */
  ProviderProvisioningExecute: "provider-provisioning-execute",
  /** main → host：资源管理器请求 Host 采样其后代进程（Agent / MCP / 终端）的 CPU 与内存 */
  ResourceUsageSnapshotRequest: "resource-usage-snapshot-request"
};
var HostResponseTypes = {
  DatabaseStartupState: "database-startup-state",
  /** window Host → main：按 requestId 上报远程连接过程日志 */
  RemoteWorkspaceConnectionLog: "remote-workspace-connection-log",
  /** window Host → main：远程 logical session 已建立 */
  RemoteWorkspaceConnected: "remote-workspace-connected",
  /** window Host → main：远程 logical session 建立失败 */
  RemoteWorkspaceConnectFailed: "remote-workspace-connect-failed",
  /** window Host → main：已连接的远程 logical session 关闭 */
  RemoteWorkspaceClosed: "remote-workspace-closed",
  /** host 进程日志上报 */
  Log: "log",
  /** host 内拉起新的 agent 子进程 */
  AgentProcessSpawned: "agent-process-spawned",
  /** host 内 agent runtime 首次通过模型执行门禁 */
  AgentProcessReady: "agent-process-ready",
  /** host 内的 agent 子进程退出 */
  AgentProcessExited: "agent-process-exited",
  /** host 内的 agent 子进程启动失败 */
  AgentProcessError: "agent-process-error",
  AgentProcessException: "agent-process-exception",
  /** host → main：CLI 进程内自采样的 CPU / RSS */
  AgentResourceSample: "agent-resource-sample",
  /** host → main：CLI 内 MCP 进程生命周期与内存遥测 */
  McpTelemetry: "mcp-telemetry",
  /** host → main：资源管理器采样结果（按 requestId 关联） */
  ResourceUsageSnapshotResult: "resource-usage-snapshot-result",
  /** host 内当前正在执行 prompt 的 agent session 数量变化 */
  AgentRunningTaskCountChanged: "agent-running-task-count-changed",
  /** host 内指定 workspace 当前仍未 terminal 的 task 数量变化 */
  WorkspaceRunningTaskCountChanged: "workspace-running-task-count-changed",
  /** host → main：Windows desktop-local CUA turn 的操作提示状态 */
  CuaOperationState: "cua-operation-state",
  /** host → main：workspace generation 已可安全 attach */
  RemoteWorkspaceAcquired: "remote-workspace-acquired",
  /** host 内当前正在生成的 Repo Wiki 任务数量变化 */
  RepoWikiRunningTaskCountChanged: "repo-wiki-running-task-count-changed",
  /** 广播消息（Phase 3） */
  Broadcast: "broadcast",
  /** host → main：申请跨窗口原子 claim */
  BroadcastClaimRequest: "broadcast-claim-request",
  /** host → main：把临时 claim reservation 提交为永久 claim */
  BroadcastClaimCommit: "broadcast-claim-commit",
  /** host → main：按 token 释放尚未提交的 claim reservation */
  BroadcastClaimRelease: "broadcast-claim-release",
  /** host → main：发布 task realtime invalidation */
  TaskRealtimePublish: "task-realtime-publish",
  /** host → main：发布 task stream mirror op */
  TaskStreamOpPublish: "task-stream-op-publish",
```

## Excerpt 20 — settings schema for repoSnapshot keys (F-022)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 202795,202875
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  providerFamilyDomain: providerFamilyDomainSchema.optional(),
  providerFamilyDomainUpdatedAt: external_exports.number().int().nonnegative().optional(),
  providerFamilyDomainMigrated: external_exports.boolean().default(false),
  repoSnapshotIndexingEnabled: external_exports.boolean().default(false),
  repoSnapshotIndexingUserConfigured: external_exports.boolean().optional(),
  instantGrepIndexingEnabled: external_exports.boolean().default(false),
  nativeSearchEnhancementsEnabled: external_exports.boolean().default(true),
  memoryEnabled: external_exports.boolean().default(false),
  lastWorkspaceSession: external_exports.array(appWorkspaceSessionEntrySchema).default([]),
  lastActiveTabIndex: external_exports.number().int().nonnegative().default(0),
  lastActiveTaskByWorkspace: external_exports.record(external_exports.string(), external_exports.string()).optional(),
  dataBaseDir: external_exports.string().trim().min(1).optional(),
  pendingPostUpdateReleaseNotes: postUpdateReleaseNotesPayloadSchema.optional(),
  receivePreviewUpdates: external_exports.boolean().default(false),
  autoDownloadAndInstallUpdates: external_exports.boolean().default(false),
  skippedElectronUpdateVersions: skippedElectronUpdateVersionsSchema,
  settingsSyncFirstRunPromptHandled: external_exports.boolean().optional(),
  webRemoteControlExternalRelayDevice: webRemoteControlExternalRelayDeviceSchema.optional(),
  webRemoteControlLastEnabledContext: webRemoteControlLastEnabledContextSchema.optional(),
  zcodeEndpointOrigin: zcodeEndpointOriginSchema.optional()
});
var appSettingsSchema = external_exports.preprocess(
  (value) => sanitizeEmbeddedBrowserViewportPreference(
    sanitizeDesktopWindowSize(
      migrateMessageStreamShowReasoningDefault(
        migrateCloseToTrayOnWindowsDefault(
          migrateOptimizeAgentExperienceDefault(
            migrateLegacyLocalePreference(
              sanitizeZCodeEndpointOrigin(
                migrateLegacyWorkspaceSession(migrateLegacyBuiltinAgentCliProviders(value))
              )
            )
          )
        )
      )
    )
  ),
  appSettingsObjectSchema
);
var appSettingsPatchSchema = external_exports.object({
  recentProjects: external_exports.array(external_exports.string()).optional(),
  locale: localeSchema.optional(),
  localePreference: localePreferenceSchema.optional(),
  terminalInheritSystemProfile: external_exports.boolean().optional(),
  terminalFontFamily: nonEmptyStringSchema2.optional(),
  integratedTerminalShell: integratedTerminalShellSelectionSchema.optional(),
  httpProxy: nonEmptyStringSchema2.optional(),
  httpProxyNoProxy: nonEmptyStringSchema2.optional(),
  httpProxyCaCertPath: nonEmptyStringSchema2.optional(),
  embeddedBrowserAllowInsecureCertificates: external_exports.boolean().optional(),
  embeddedBrowserViewportPreference: embeddedBrowserViewportPreferenceSchema.optional(),
  computerUseComposerEntryHidden: external_exports.boolean().optional(),
  taskAutoArchiveEnabled: external_exports.boolean().optional(),
  taskAutoArchiveOlderThanDays: external_exports.number().int().positive().max(365).optional(),
  closeToTrayOnWindows: external_exports.boolean().optional(),
  keepAwakeWhileRunning: external_exports.boolean().optional(),
  closeToTrayOnWindowsMigrationInitialized: external_exports.boolean().optional(),
  desktopZoomLevel: desktopZoomLevelSchema.optional(),
  desktopWindowSize: desktopWindowSizeSchema.optional(),
  desktopChromiumHardwareAccelerationEnabled: external_exports.boolean().optional(),
  messageStreamShowReasoning: external_exports.boolean().optional(),
  messageStreamShowReasoningMigrationInitialized: external_exports.boolean().optional(),
  messageStreamShowTodos: external_exports.boolean().optional(),
  toolGroupingExploreEnabled: external_exports.boolean().optional(),
  toolGroupingTerminalEnabled: external_exports.boolean().optional(),
  toolGroupingChangesEnabled: external_exports.boolean().optional(),
  zcodeInteractionBehavior: zcodeInteractionBehaviorSchema.optional(),
  askUserQuestionAutoResolutionEnabled: external_exports.boolean().optional(),
  modelIoFullRetentionEnabled: external_exports.boolean().optional(),
  optimizeAgentExperienceEnabled: external_exports.boolean().optional(),
  optimizeAgentExperienceMigrationInitialized: external_exports.boolean().optional(),
  enabledBuiltinAgentCliProviders: enabledBuiltinAgentCliProvidersSchema.optional(),
  providerFamilyConnectionSelections: providerFamilyConnectionSelectionSettingsSchema.optional(),
  providerFamilyDomain: external_exports.union([providerFamilyDomainSchema, external_exports.literal("")]).optional(),
  providerFamilyDomainUpdatedAt: external_exports.number().int().nonnegative().optional(),
  providerFamilyDomainMigrated: external_exports.boolean().optional(),
  repoSnapshotIndexingEnabled: external_exports.boolean().optional(),
  repoSnapshotIndexingUserConfigured: external_exports.boolean().optional(),
  instantGrepIndexingEnabled: external_exports.boolean().optional(),
  nativeSearchEnhancementsEnabled: external_exports.boolean().optional(),
  memoryEnabled: external_exports.boolean().optional(),
```

## Excerpt 22 — getUploadCredential request (F-014)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 312620,312666 (getUploadCredential + getUploadKey)
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  objectUploadTimeoutMs;
  uploadCredentialsByHandle = /* @__PURE__ */ new Map();
  constructor(options) {
    this.apiClient = options.apiClient;
    this.objectUploadFetch = options.objectUploadFetch;
    this.credentialTimeoutMs = options.credentialTimeoutMs ?? REPO_SNAPSHOT_CREDENTIAL_TIMEOUT_MS;
    this.objectUploadTimeoutMs = options.objectUploadTimeoutMs ?? REPO_SNAPSHOT_OBJECT_UPLOAD_TIMEOUT_MS;
  }
  async getUploadCredential(token, workspaceId, signal) {
    const url6 = buildUploadCredentialUrl(workspaceId);
    const response = await readApiJson(
      this.apiClient,
      url6,
      {
        method: "GET",
        headers: authHeaders(token),
        timeoutMs: this.credentialTimeoutMs,
        signal
      }
    );
    const credential = resolveUploadCredentialData(response);
    if (!credential) {
      return null;
    }
    assertSupportedEncryption(credential);
    return credential;
  }
  pruneExpiredUploadCredentials(now = Date.now()) {
    for (const [handle, cached6] of this.uploadCredentialsByHandle) {
      if (cached6.expiresAt <= now) {
        this.uploadCredentialsByHandle.delete(handle);
      }
    }
  }
  async getUploadKey(token, workspaceId, _traceId, options) {
    const credential = await this.getUploadCredential(token, workspaceId, options?.signal);
    if (!credential) {
      return null;
    }
    this.pruneExpiredUploadCredentials();
    const uploadCredentialHandle = (0, import_node_crypto45.randomUUID)();
    this.uploadCredentialsByHandle.set(uploadCredentialHandle, {
      credential,
      tokenHash: uploadCredentialTokenHash(token),
      workspaceId,
      expiresAt: Date.now() + REPO_SNAPSHOT_CREDENTIAL_HANDLE_TTL_MS
    });
```

## Excerpt 23 — sendPrompt schedules capture (F-002)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 234465,234480
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
        inputId: params.inputId,
        queryId: params.queryId ?? null,
        sessionId: params.sessionId,
        sessionTraceId: sessionTraceId ?? null,
        textLength: params.content.length,
        workspaceKey: resolveWorkspaceKey(params),
        workspacePath: params.workspacePath
      });
      scheduleRepoSnapshotSidecar({
        prompt: params,
        sessionTraceId
      });
      try {
        const result = await client.request(
          zcodeProtocolMethods.sessionSend,
          buildSessionSendParams(protocolParams),
```

## Excerpt 24 — workspaceIdentity capture gate (F-031, F-030)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 311930,311940
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  }
  async captureBeforePrompt(params) {
    const trimmedIdentity = params.workspaceIdentity?.trim();
    if (trimmedIdentity) {
      return;
    }
    await this.captureScheduler.schedule(params, async (jobSignal) => {
      const signal = params.signal ? AbortSignal.any([params.signal, jobSignal]) : jobSignal;
      await this.captureBeforePromptUnsafe({ ...params, signal });
    });
  }
```

## Excerpt 25 — workspace key builder identity||path (F-031, F-030)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 210420,210432
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  REPO_SNAPSHOT_UPLOAD_SCHEMA_VERSION
);
var REPO_SNAPSHOT_UPLOAD_TARGET_SCHEMA = repoSnapshotSchema(
  "upload_target",
  REPO_SNAPSHOT_UPLOAD_SCHEMA_VERSION
);
function buildRepoSnapshotWorkspaceKey(params) {
  return params.workspaceIdentity?.trim() || params.workspacePath;
}
function resolveRepoSnapshotPromptProvider(params) {
  const providerId = params.providerId?.trim();
  if (providerId === BUILTIN_MODEL_PROVIDER_IDS.bigmodelIndividualCodingPlan || providerId === BUILTIN_MODEL_PROVIDER_IDS.bigmodelStartPlan) {
    return "bigmodel";
```

## Excerpt 26 — task-complete capture + silent error swallow (F-004, F-033)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 319000,319018
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
    if (!failed && captureRepoSnapshot) {
      const captureIntent = async (signal) => {
        const captureTarget = summary.lastTerminalQuery ? {
          ...target,
          queryId: summary.lastTerminalQuery.queryId,
          historyRoundCount: summary.lastTerminalQuery.historyRoundCount
        } : target;
        if (signal) {
          await options.captureRepoSnapshotAfterTaskComplete?.(captureTarget, signal);
        } else {
          await options.captureRepoSnapshotAfterTaskComplete?.(captureTarget);
        }
      };
      const scheduled = options.repoSnapshotCaptureIntentScheduler ? options.repoSnapshotCaptureIntentScheduler.schedule(target, captureIntent) : captureIntent();
      void scheduled.catch(() => {
      });
    }
    terminalEventEmitter.fire({
      target,
```

## Excerpt 27 — uploaded settings-behavior key list (F-022)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 312160,312172
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  "toolGroupingExploreEnabled",
  "toolGroupingTerminalEnabled",
  "toolGroupingChangesEnabled",
  "nativeSearchEnhancementsEnabled",
  "memoryEnabled",
  "optimizeAgentExperienceEnabled",
  "repoSnapshotIndexingEnabled",
  "repoSnapshotIndexingUserConfigured",
  "instantGrepIndexingEnabled",
  "embeddedBrowserAllowInsecureCertificates",
  "keepAwakeWhileRunning",
  "terminalInheritSystemProfile",
  "integratedTerminalShell"
```

## Excerpt 28 — local git checkpoint refs (F-023)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 214495,214512
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
}
function getWorkspacePathspec(workspaceInRepoPath) {
  return workspaceInRepoPath === "." ? "." : workspaceInRepoPath;
}
function getCheckpointRefName(workspacePath, checkpointId) {
  const workspaceHash = getWorkspaceHash(workspacePath);
  return `refs/zcode/checkpoints/${workspaceHash}/${checkpointId}`;
}
function mapNameStatusKind(status) {
  const normalized = status[0] ?? "M";
  if (normalized === "A") {
    return "added";
  }
  if (normalized === "D") {
    return "deleted";
  }
  if (normalized === "R" || normalized === "C") {
    return "renamed";
```

## Excerpt 29 — local checkpoint author email constant (F-023)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 214630,214648
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
  return [...values];
}
function buildCheckpointEnv(tempIndexPath) {
  return {
    GIT_INDEX_FILE: tempIndexPath,
    GIT_AUTHOR_NAME: "ZCode Checkpoint",
    GIT_AUTHOR_EMAIL: "checkpoint@zcode.local",
    GIT_COMMITTER_NAME: "ZCode Checkpoint",
    GIT_COMMITTER_EMAIL: "checkpoint@zcode.local"
  };
}
async function removeFileIfExists(path) {
  await (0, import_promises15.rm)(path, {
    force: true,
    recursive: true
  });
}
function toRepoRelativePathFromAbsolute(repoRoot, absolutePath) {
  return normalizeGitPath(absolutePath.replace(`${repoRoot}${import_node_path16.sep}`, ""));
```

## Excerpt 30 — local checkpoint restore via git restore (F-023)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 214955,214975
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---
          args: [
            "restore",
            `--source=${params.to.commitOid}`,
            "--worktree",
            "--",
            ...restoreRepoPaths
          ]
        });
        ensureGitCommandSucceeded("git restore checkpoint", restoreResult);
      }
      const deleteAbsolutePaths = /* @__PURE__ */ new Set();
      for (const file6 of diff.files) {
        if (file6.kind === "deleted") {
          deleteAbsolutePaths.add(file6.path);
          continue;
        }
        if (file6.kind === "renamed" && file6.originalPath) {
          deleteAbsolutePaths.add(file6.originalPath);
        }
      }
      for (const path of deleteAbsolutePaths) {
```

## Excerpt 31 — snapshot max-size / disk quota defaults (F-002)

```js
# source: /home/<USER>/.zcode/server/zcode-server.cjs
# lines: 311680,311692
# extracted: 2026-09-19 (minified bundle, cut -c1-240)
# ---

// ../services/src/repo-snapshot/repoSnapshotDiskQuota.ts
var import_promises88 = require("node:fs/promises");
var import_node_path104 = require("node:path");
var REPO_SNAPSHOT_DEFAULT_MAX_SIZE_BYTES = 2 * 1024 * 1024 * 1024;
var REPO_SNAPSHOT_DISK_QUOTA_MAX_SIZE_MULTIPLIER = 3;
var REPO_SNAPSHOT_DISK_QUOTA_ABSOLUTE_MAX_BYTES = 6 * 1024 * 1024 * 1024;
var repoSnapshotDiskQuotaAbsoluteMaxBytesOverride;
var REPO_SNAPSHOT_GENERATION_RESERVED_MULTIPLIER = 2;
function resolveRepoSnapshotMaxSizeBytes(maxSizeBytes) {
  const requested = maxSizeBytes !== void 0 && Number.isFinite(maxSizeBytes) && maxSizeBytes > 0 ? maxSizeBytes : REPO_SNAPSHOT_DEFAULT_MAX_SIZE_BYTES;
  const absoluteMaxBytes = repoSnapshotDiskQuotaAbsoluteMaxBytesOverride ?? REPO_SNAPSHOT_DISK_QUOTA_ABSOLUTE_MAX_BYTES;
  return Math.min(requested, absoluteMaxBytes / REPO_SNAPSHOT_DISK_QUOTA_MAX_SIZE_MULTIPLIER);
```

## Excerpt 32 — desktop asar equivalents: gate, key builder, workspace/target kinds (F-031, F-030, F-024)

```js
# source: /opt/ZCode/resources/app.asar (grep -aoE windows, desktop-side equivalents)
# extracted: 2026-09-19
# ---
== captureBeforePrompt with workspaceIdentity early-return (desktop asar) ==
async captureBeforePrompt(t){t.workspaceIdentity?.trim()||await this.captureScheduler.schedule(t,async o=>{let r=t.signal?AbortSignal.any([t.signal,o]):o;await this.captureBeforePromptUnsafe({...t,signal:r})})}getCaptureQueueDiagnostics(){return this.captureScheduler.getDiagnostics()}a

== workspaceKey = identity||path fallback (desktop asar) ==
function A(r){return r.workspaceIdentity?.trim()||r.workspacePath}d(A,"workspaceKey");function V(r){

== workspace kinds: project | remote(ssh/wsl/docker target) ==
kind:t.literal("remote"),workspacePath:D,localWorkspacePath:D.optional(),workspaceIdentity:D.optional(),target:Qf,lastOpenedAt:t.number().int().nonnegative(),lastConnectionStatus

== target kinds ssh/wsl/docker ==
kind:t.literal("ssh"),host:D,port:t.number().int().positive().max(65535).optional(),username:D,sshConfigAl
kind:t.literal("wsl"),distro:t.string().optional(),user:Xo.optional()}),t.object({kind:t
kind:t.literal("ssh"),host:f,port:t.number().int().positive().max(65535).optional(),username:f,sshConfigAl
kind:t.literal("wsl"),distro:t.string().optional(),user:Xo.optional()}),iP=t.object({kin

== remote requires workspaceIdentity (schema refine) ==
remoteSessionId&&!r.workspaceIdentity&&t.addIssue({code:"custom",message:"remote task address requires workspaceIdentity",path:["workspaceIdentity"]})}),Br=e.object({rem
remoteSessionId&&!r.workspaceIdentity&&t.addIssue({code:"custom",message:"remote workspace fact requires workspaceIdentity",path:["workspaceIdentity"]}),r.sourceAvailabi
remoteSessionId&&!r.workspaceIdentity&&t.addIssue({code:"custom",message:"remote task address requires workspaceIdentity",path:["workspaceIdentity"]})}),kt=e.object({rem
```
