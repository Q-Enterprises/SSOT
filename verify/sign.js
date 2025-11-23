import {
  createPrivateKey,
  createPublicKey,
  sign as nodeSign,
  verify as nodeVerify,
  createHash
} from 'crypto';

const ED25519_PKCS8_PREFIX = Buffer.from('302e020100300506032b657004220420', 'hex');
const ED25519_SPKI_PREFIX = Buffer.from('302a300506032b6570032100', 'hex');

export function decodeBase64Prefixed(value) {
  return Buffer.from(value.replace(/^base64:/, ''), 'base64');
}

export function encodeBase64Prefixed(buffer) {
  const input = buffer instanceof Uint8Array ? Buffer.from(buffer) : buffer;
  return `base64:${input.toString('base64')}`;
}

function toPrivateKeyObject(raw) {
  const buffer = raw instanceof Uint8Array ? Buffer.from(raw) : raw;
  if (buffer.length !== 64) {
    throw new Error('Ed25519 private key must be 64 bytes (seed + public key)');
  }
  const seed = buffer.subarray(0, 32);
  const pkcs8 = Buffer.concat([ED25519_PKCS8_PREFIX, seed]);
  return createPrivateKey({ key: pkcs8, format: 'der', type: 'pkcs8' });
}

function toPublicKeyObject(raw) {
  const buffer = raw instanceof Uint8Array ? Buffer.from(raw) : raw;
  if (buffer.length !== 32) {
    throw new Error('Ed25519 public key must be 32 bytes');
  }
  const spki = Buffer.concat([ED25519_SPKI_PREFIX, buffer]);
  return createPublicKey({ key: spki, format: 'der', type: 'spki' });
}

export function privateKeyFromBase64(base64Raw) {
  const raw = decodeBase64Prefixed(base64Raw);
  return { keyObject: toPrivateKeyObject(raw), raw };
}

export function publicKeyFromBase64(base64Raw) {
  const raw = decodeBase64Prefixed(base64Raw);
  return { keyObject: toPublicKeyObject(raw), raw };
}

function resolvePrivateKey(secretKey) {
  if (typeof secretKey === 'string') {
    return privateKeyFromBase64(secretKey);
  }
  if (secretKey?.keyObject) {
    return secretKey;
  }
  if (secretKey instanceof Uint8Array || Buffer.isBuffer(secretKey)) {
    return { keyObject: toPrivateKeyObject(secretKey), raw: Buffer.from(secretKey) };
  }
  return { keyObject: secretKey, raw: undefined };
}

function resolvePublicKey(publicKey) {
  if (typeof publicKey === 'string') {
    return publicKeyFromBase64(publicKey);
  }
  if (publicKey?.keyObject) {
    return publicKey;
  }
  if (publicKey instanceof Uint8Array || Buffer.isBuffer(publicKey)) {
    return { keyObject: toPublicKeyObject(publicKey), raw: Buffer.from(publicKey) };
  }
  return { keyObject: publicKey, raw: undefined };
}

export function signEd25519(preimage, secretKey) {
  const message = Buffer.from(preimage, 'utf8');
  const { keyObject } = resolvePrivateKey(secretKey);
  const sig = nodeSign(null, message, keyObject);
  return encodeBase64Prefixed(sig);
}

export function verifyEd25519(preimage, signatureB64, publicKey) {
  const message = Buffer.from(preimage, 'utf8');
  const sigBytes = decodeBase64Prefixed(signatureB64);
  const { keyObject } = resolvePublicKey(publicKey);
  return nodeVerify(null, message, keyObject, sigBytes);
}

export function fingerprintFromPublicKey(publicKey) {
  const { raw, keyObject } = resolvePublicKey(publicKey);
  const material = raw ?? keyObject.export({ format: 'der', type: 'spki' }).slice(-32);
  return `ed25519:${createHash('sha256').update(material).digest('hex')}`;
}
