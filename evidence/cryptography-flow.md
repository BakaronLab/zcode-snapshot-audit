# Cryptography Flow

All statements [CONFIRMED-CODE] against the audited build (excerpt 09, excerpt 03, excerpt 04) unless noted.

## Envelope-encryption design

```
plaintext snapshot (tar.gz)
   │
   │  dataKey = randomBytes(32)            ← generated client-side
   │  nonce   = randomBytes(16)            ← prepended to ciphertext
   ▼
AES-256-CTR(dataKey, nonce) ──────────► ciphertext  (uploaded object)
   │
   │  wrappedKey = publicEncrypt(
   │      key:      credential.encryption.public_key,   ← delivered by ZCode server
   │      padding:  RSA_PKCS1_OAEP_PADDING,
   │      oaepHash: "sha256" }, dataKey)
   ▼
wrappedKey (base64) ── OSS callback form field "x:encrypted_aes_key" ──► ZCode server
```

Envelope metadata declares `contentAlgorithm: "aes-256-ctr"`, `keyWrapAlgorithm: "rsa-oaep-sha256"`. The credential validation enforces `encryption.algorithm === "RSA-OAEP-256"`.

## What this design does and does not provide

- **Provides:** confidentiality of the archive against parties who can observe or obtain the uploaded object but not the wrapped key — e.g. passive network observers, storage-side access without the callback payload.
- **Does not provide:** confidentiality of the archive **from the ZCode server**. The server (a) generates and delivers the RSA key pair used for wrapping, and (b) receives the wrapped data key through the OSS callback. It therefore **possesses the corresponding capability to decrypt every snapshot** under this design.
- This statement is about cryptographic capability. Whether the server actually decrypts any snapshot, and what it does with plaintext afterwards, is UNKNOWN — this repository makes no claim about that.

## Additional protocol observations

- The OSS callback also carries `checksum = "sha256:" + <sha256 of the plaintext snapshot>` — a plaintext-content fingerprint in addition to the encrypted object.
- `base_snapshot_id` links incremental snapshots to a server-side base, enabling server-side delta reconstruction of full workspace trees.
- `meta/manifest.json` (full path + size listing) is inside the encrypted archive; the callback's attribution fields (session/query/request ids) are separate metadata.
