import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { canon, sha256Prefixed, hashObject } from './canon.js';
import { computeRoot } from './merkle.js';
import { fingerprintFromPublicKey, publicKeyFromBase64, verifyEd25519 } from './sign.js';
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

function usage() {
  console.error('Usage: node verify/verify.js [--now <iso8601>] <attestation> <anchor> <replay_binding> <council_roster> <manifest>');
  process.exit(1);
}

function withinWindow(ts, windowSec, nowISO) {
  const base = Date.parse(ts);
  const reference = Date.parse(nowISO);
  if (Number.isNaN(base) || Number.isNaN(reference)) {
    return false;
  }
  return Math.abs(reference - base) <= windowSec * 1000;
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

function mapRoster(roster) {
  ensure(Array.isArray(roster.keys), 'council_roster.keys must be an array');
  const map = new Map();
  for (const entry of roster.keys) {
    ensure(entry.node_id && entry.ed25519_pk, 'roster entry missing node_id or ed25519_pk');
    const pkObject = publicKeyFromBase64(entry.ed25519_pk);
    ensure(pkObject.raw.length === 32, `roster key for ${entry.node_id} must be 32 bytes`);
    const fingerprint = fingerprintFromPublicKey(pkObject);
    ensure(
      !entry.key_fingerprint || entry.key_fingerprint === fingerprint,
      `fingerprint mismatch for ${entry.node_id}`
    );
    map.set(entry.node_id, { ...entry, publicKey: pkObject, fingerprint });
  }
  return map;
}

function isSortedByNodeId(signers) {
  for (let i = 1; i < signers.length; i += 1) {
    if (signers[i - 1].node_id.localeCompare(signers[i].node_id) > 0) {
      return false;
    }
  }
  return true;
}

function parseArgs() {
  const args = process.argv.slice(2);
  let nowOverride;
  if (args[0] === '--now') {
    ensure(args.length >= 2, '--now flag requires an ISO timestamp');
    nowOverride = args[1];
    args.splice(0, 2);
  }
  if (args.length !== 5) {
    usage();
  }
  return { nowOverride, paths: args };
}

try {
  const { nowOverride, paths } = parseArgs();
  const [attestationPath, anchorPath, bindingPath, rosterPath, manifestPath] = paths;

  const attestationSchema = loadSchema('attestation.schema.json');
  const anchorSchema = loadSchema('anchor.schema.json');
  const bindingSchema = loadSchema('replay_binding.schema.json');

  const frame = readJson(attestationPath);
  const anchor = readJson(anchorPath);
  const binding = readJson(bindingPath);
  const roster = readJson(rosterPath);
  const manifest = readJson(manifestPath);

  ensureSchema(attestationSchema, frame, 'Attestation');
  ensureSchema(anchorSchema, anchor, 'Anchor');
  ensureSchema(bindingSchema, binding, 'Replay binding');

  ensure(frame.quorum.required <= frame.quorum.total, 'quorum.required cannot exceed quorum.total');
  ensure(frame.signers.length === frame.quorum.total, 'signer list must equal quorum.total');
  ensure(isSortedByNodeId(frame.signers), 'signers must be sorted lexicographically by node_id');

  const manifestHash = sha256Prefixed(canon(manifest));
  ensure(frame.manifest_hash === manifestHash, 'manifest_hash mismatch between frame and manifest');

  const rosterMap = mapRoster(roster);

  let validSignatures = 0;
  for (const signer of frame.signers) {
    const rosterEntry = rosterMap.get(signer.node_id);
    ensure(rosterEntry, `missing roster entry for signer ${signer.node_id}`);
    ensure(signer.key_fingerprint === rosterEntry.fingerprint, `fingerprint mismatch for signer ${signer.node_id}`);

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

    if (verifyEd25519(preimage, signer.signature, rosterEntry.publicKey)) {
      validSignatures += 1;
    } else {
      throw new Error(`invalid signature for signer ${signer.node_id}`);
    }
  }

  ensure(validSignatures >= frame.quorum.required, `quorum not met: ${validSignatures}/${frame.quorum.required}`);

  const attesterEntry = rosterMap.get('Scrollsmith');
  ensure(attesterEntry, 'Missing Scrollsmith key in roster');
  ensure(frame.attester.key_fingerprint === attesterEntry.fingerprint, 'attester fingerprint mismatch');

  const sortedSigners = [...frame.signers].sort((a, b) => a.node_id.localeCompare(b.node_id));
  const counterPreimage = canon({
    manifest_hash: frame.manifest_hash,
    quorum: frame.quorum,
    signers: sortedSigners.map(({ node_id, key_fingerprint, signature }) => ({
      node_id,
      key_fingerprint,
      signature
    })),
    attester_key: frame.attester.key_fingerprint
  });

  ensure(
    verifyEd25519(counterPreimage, frame.attester.counter_signature, attesterEntry.publicKey),
    'counter-signature invalid'
  );

  const frameHash = hashObject(frame);
  ensure(anchor.leaf === frame.manifest_hash, 'anchor leaf must equal manifest hash');
  ensure(anchor.sibling === frameHash, 'anchor sibling must equal attestation hash');
  ensure(anchor.timestamp === frame.anti_replay.timestamp, 'anchor timestamp must match attestation anti_replay timestamp');

  const computedRoot = computeRoot(anchor.leaf, anchor.sibling, anchor.path);
  ensure(anchor.root === computedRoot, 'computed Merkle root does not match anchor root');

  ensure(binding.manifest_hash === frame.manifest_hash, 'replay binding manifest hash mismatch');
  ensure(binding.attestation_hash === frameHash, 'replay binding attestation hash mismatch');
  ensure(binding.nonce === frame.anti_replay.nonce, 'replay binding nonce mismatch');
  ensure(binding.timestamp === frame.anti_replay.timestamp, 'replay binding timestamp mismatch');
  ensure(binding.replay_window_s === frame.anti_replay.replay_window_s, 'replay window mismatch');
  ensure(binding.auth_scope === frame.bindings.auth_scope, 'auth scope mismatch');

  const parentExpectation = 'capsule.avatar.ceciliaQ.royal_flush.v1';
  ensure(
    typeof frame.bindings.parent === 'string' && frame.bindings.parent.includes(parentExpectation),
    `parent lineage mismatch, expected to include ${parentExpectation}`
  );

  const nowISO = nowOverride || new Date().toISOString();
  ensure(
    withinWindow(frame.anti_replay.timestamp, frame.anti_replay.replay_window_s, nowISO),
    'attestation timestamp outside allowed replay window'
  );

  ensure(anchor.clock_source === 'scrollstream', 'anchor clock source mismatch');
  ensure(binding.clock_source === 'scrollstream', 'binding clock source mismatch');

  console.log('✅ Verification passed');
} catch (error) {
  console.error(`❌ Verification failed: ${error.message}`);
  process.exit(1);
}
