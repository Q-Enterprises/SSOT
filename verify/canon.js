import { createHash } from 'crypto';

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function canonicalize(value) {
  if (value === null) {
    return 'null';
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) {
      throw new TypeError('Non-finite numbers are not permitted in canonical JSON');
    }
    return Number(value).toString();
  }
  if (typeof value === 'string') {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    const items = value.map((item) => canonicalize(item));
    return `[${items.join(',')}]`;
  }
  if (isObject(value)) {
    const keys = Object.keys(value).sort();
    const props = keys.map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`);
    return `{${props.join(',')}}`;
  }
  throw new TypeError(`Unsupported data type in canonicalization: ${typeof value}`);
}

export function canon(obj) {
  return canonicalize(obj);
}

export function sha256Prefixed(canonicalJson) {
  const hash = createHash('sha256').update(canonicalJson, 'utf8').digest('hex');
  return `sha256:${hash}`;
}

export function hashObject(obj) {
  return sha256Prefixed(canon(obj));
}
