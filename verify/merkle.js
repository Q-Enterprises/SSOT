import { createHash } from 'crypto';

function stripPrefix(value) {
  return value.replace(/^sha256:/, '');
}

export function sha256Hex(input) {
  const buffer = input instanceof Uint8Array || Buffer.isBuffer(input) ? input : Buffer.from(input, 'hex');
  return createHash('sha256').update(buffer).digest('hex');
}

export function computeRoot(leafPrefixed, siblingPrefixed, pathPrefixed) {
  let current = Buffer.from(stripPrefix(leafPrefixed), 'hex');
  const sibling = Buffer.from(stripPrefix(siblingPrefixed), 'hex');
  const pair = Buffer.compare(current, sibling) <= 0 ? Buffer.concat([current, sibling]) : Buffer.concat([sibling, current]);
  current = Buffer.from(sha256Hex(pair), 'hex');

  for (const node of pathPrefixed) {
    const sib = Buffer.from(stripPrefix(node), 'hex');
    const [a, b] = Buffer.compare(current, sib) <= 0 ? [current, sib] : [sib, current];
    current = Buffer.from(sha256Hex(Buffer.concat([a, b])), 'hex');
  }

  return `sha256:${current.toString('hex')}`;
}
