#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <merkle-root> [capsule-id]" >&2
  exit 1
fi

MERKLE_ROOT="$1"
CAPSULE_ID="${2:-capsule.council.boo.agency.v7}"
OUT_DIR="${OUT_DIR:-ops/out}"
LEDGER_FILE="$OUT_DIR/merkle_seals.log"
mkdir -p "$OUT_DIR"

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat >> "$LEDGER_FILE" <<JSON
{"ts":"$TS","capsule":"$CAPSULE_ID","merkle_root":"$MERKLE_ROOT"}
JSON

echo "sealed $CAPSULE_ID @ $MERKLE_ROOT"
