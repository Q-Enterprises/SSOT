import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { randomBytes } from 'crypto';
import { spawnSync } from 'child_process';
import { canon, sha256Prefixed, hashObject } from './canon.js';
import { computeRoot } from './merkle.js';
import {
  fingerprintFromPublicKey,
  privateKeyFromBase64,
  publicKeyFromBase64,
  signEd25519
} from './sign.js';
import { validateWithSchema } from './schema-validator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function loadSchema(name) {
  const schemaPath = path.join(__dirname, 'schemas', name);
  return readJson(schemaPath);
}

function ensure(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function ensureSchema(schema, data, label) {
  const errors = validateWithSchema(schema, data);
  if (errors.length > 0) {
    const details = errors.map((e) => `  - ${e}`).join('\n');
    throw new Error(`${label} failed schema validation:\n${details}`);
  }
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i];
    const value = args[i + 1];
    if (!key || !key.startsWith('--') || value === undefined) {
      throw new Error('Invalid arguments. Expected --key value pairs.');
    }
    options[key.substring(2)] = value;
  }
  const required = [
    'manifest',
    'attestation-template',
    'anchor-template',
    'replay-template',
    'signers',
    'roster',
    'output'
  ];
  for (const key of required) {
    ensure(options[key], `Missing required argument --${key}`);
  }
  return options;
}

function buildRosterMap(roster) {
  ensure(Array.isArray(roster.keys), 'roster.keys must be an array');
  const map = new Map();
  for (const entry of roster.keys) {
    ensure(entry.node_id && entry.ed25519_pk, 'roster entry missing node_id or ed25519_pk');
    const pk = publicKeyFromBase64(entry.ed25519_pk);
    ensure(pk.raw.length === 32, `Roster key for ${entry.node_id} must be 32 bytes`);
    const fingerprint = fingerprintFromPublicKey(pk);
    if (entry.key_fingerprint && entry.key_fingerprint !== fingerprint) {
      throw new Error(`Roster fingerprint mismatch for ${entry.node_id}`);
    }
    map.set(entry.node_id, { ...entry, publicKey: pk, fingerprint });
  }
  return map;
}

try {
  const options = parseArgs();
  const manifest = readJson(options.manifest);
  const frame = readJson(options['attestation-template']);
  const anchor = readJson(options['anchor-template']);
  const binding = readJson(options['replay-template']);
  const signersConfig = readJson(options.signers);
  const roster = readJson(options.roster);

  const attestationSchema = loadSchema('attestation.schema.json');
  const anchorSchema = loadSchema('anchor.schema.json');
  const bindingSchema = loadSchema('replay_binding.schema.json');

  const manifestHash = sha256Prefixed(canon(manifest));
  const nonce = randomBytes(18).toString('base64');
  const timestamp = new Date().toISOString();

  frame.manifest_hash = manifestHash;
  frame.anti_replay.nonce = nonce;
  frame.anti_replay.timestamp = timestamp;
  frame.status = 'SEALED';

  ensure(frame.quorum.required <= frame.quorum.total, 'quorum.required cannot exceed quorum.total');

  const rosterMap = buildRosterMap(roster);
  const signerSecretMap = new Map();
  for (const signer of signersConfig.signers || []) {
    ensure(signer.node_id && signer.secret_key && signer.public_key, 'signer config must include node_id, secret_key, public_key');
    const pk = publicKeyFromBase64(signer.public_key);
    ensure(pk.raw.length === 32, `Signer config public key for ${signer.node_id} must be 32 bytes`);
    const fingerprint = fingerprintFromPublicKey(pk);
    ensure(fingerprint === signer.key_fingerprint, `signer config fingerprint mismatch for ${signer.node_id}`);
    signerSecretMap.set(signer.node_id, {
      ...signer,
      publicKey: pk,
      fingerprint,
      privateKey: privateKeyFromBase64(signer.secret_key)
    });
  }

  for (const [nodeId, config] of signerSecretMap.entries()) {
    ensure(config.privateKey.raw.length === 64, `signing key for ${nodeId} must be 64 bytes (seed + public key)`);
  }

  const attesterConfig = signersConfig.attester;
  ensure(attesterConfig, 'attester configuration missing');
  const attesterPublicKey = publicKeyFromBase64(attesterConfig.public_key);
  ensure(attesterPublicKey.raw.length === 32, 'Attester public key must be 32 bytes');
  const attesterFingerprint = fingerprintFromPublicKey(attesterPublicKey);
  ensure(attesterFingerprint === attesterConfig.key_fingerprint, 'attester fingerprint mismatch in configuration');

  const attesterPrivateKey = privateKeyFromBase64(attesterConfig.secret_key);
  ensure(attesterPrivateKey.raw.length === 64, 'Attester secret key must be 64 bytes (seed + public key)');
  const rosterAttester = rosterMap.get(attesterConfig.node_id);
  ensure(rosterAttester, `Roster is missing attester ${attesterConfig.node_id}`);
  ensure(rosterAttester.fingerprint === attesterFingerprint, 'Attester fingerprint mismatch with roster');

  const sortedSigners = [...frame.signers].sort((a, b) => a.node_id.localeCompare(b.node_id));
  ensure(sortedSigners.length === frame.quorum.total, 'signer list must equal quorum.total');

  const signedSigners = sortedSigners.map((signer) => {
    const config = signerSecretMap.get(signer.node_id);
    ensure(config, `Missing signing key for ${signer.node_id}`);
    const rosterEntry = rosterMap.get(signer.node_id);
    ensure(rosterEntry, `Roster missing ${signer.node_id}`);
    ensure(rosterEntry.fingerprint === signer.key_fingerprint, `Template fingerprint mismatch for ${signer.node_id}`);
    ensure(config.fingerprint === signer.key_fingerprint, `Configuration fingerprint mismatch for ${signer.node_id}`);

    const preimage = canon({
      frame_id: frame.frame_id,
      capsule_id: frame.capsule_id,
      manifest_hash: frame.manifest_hash,
      quorum: frame.quorum,
      bindings: frame.bindings,
      anti_replay: frame.anti_replay,
      signer_context: {
        node_id: signer.node_id,
        key_fingerprint: signer.key_fingerprint
      }
    });

    const signature = signEd25519(preimage, config.privateKey);
    return {
      node_id: signer.node_id,
      key_fingerprint: signer.key_fingerprint,
      signature
    };
  });

  frame.signers = signedSigners;

  const counterPreimage = canon({
    manifest_hash: frame.manifest_hash,
    quorum: frame.quorum,
    signers: frame.signers.map(({ node_id, key_fingerprint, signature }) => ({
      node_id,
      key_fingerprint,
      signature
    })),
    attester_key: attesterConfig.key_fingerprint
  });

  frame.attester = {
    role: frame.attester.role,
    key_fingerprint: attesterConfig.key_fingerprint,
    counter_signature: signEd25519(counterPreimage, attesterPrivateKey)
  };

  const frameHash = hashObject(frame);

  anchor.leaf = manifestHash;
  anchor.sibling = frameHash;
  anchor.timestamp = timestamp;
  anchor.path = Array.isArray(anchor.path) ? anchor.path : [];
  anchor.root = computeRoot(anchor.leaf, anchor.sibling, anchor.path);

  binding.manifest_hash = manifestHash;
  binding.attestation_hash = frameHash;
  binding.timestamp = timestamp;
  binding.nonce = nonce;
  binding.replay_window_s = frame.anti_replay.replay_window_s;

  ensureSchema(attestationSchema, frame, 'Sealed attestation');
  ensureSchema(anchorSchema, anchor, 'Merkle anchor');
  ensureSchema(bindingSchema, binding, 'Replay binding');

  const outputDir = path.resolve(options.output);
  fs.mkdirSync(outputDir, { recursive: true });

  const attestationOut = path.join(outputDir, 'attestation.json');
  const anchorOut = path.join(outputDir, 'anchor.json');
  const bindingOut = path.join(outputDir, 'replay_binding.json');

  fs.writeFileSync(attestationOut, `${JSON.stringify(frame, null, 2)}\n`);
  fs.writeFileSync(anchorOut, `${JSON.stringify(anchor, null, 2)}\n`);
  fs.writeFileSync(bindingOut, `${JSON.stringify(binding, null, 2)}\n`);

  const verifyArgs = [
    path.join(__dirname, 'verify.js'),
    attestationOut,
    anchorOut,
    bindingOut,
    path.resolve(options.roster),
    path.resolve(options.manifest)
  ];
  const verifyResult = spawnSync('node', verifyArgs, { stdio: 'inherit' });
  if (verifyResult.status !== 0) {
    throw new Error('Verification failed after sealing');
  }

  console.log('✅ Attestation sealed and verified');
} catch (error) {
  console.error(`❌ Failed to seal attestation: ${error.message}`);
  process.exit(1);
}
