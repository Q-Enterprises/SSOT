#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 5 ]]; then
  echo "Usage: $0 <attestation.json> <anchor.json> <replay_binding.json> <council_roster.json> <manifest.json>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ATT_FILE="$1"
ANCHOR_FILE="$2"
BINDING_FILE="$3"
ROSTER_FILE="$4"
MANIFEST_FILE="$5"

node "$SCRIPT_DIR/verify.js" "$ATT_FILE" "$ANCHOR_FILE" "$BINDING_FILE" "$ROSTER_FILE" "$MANIFEST_FILE"

EVENT_URL="${EVENT_URL:-https://events.example/attest.broadcast.v1}"
EXTRA_ARGS=()
if [[ -n "${EVENT_HEADERS:-}" ]]; then
  IFS=';' read -ra HEADERS <<< "$EVENT_HEADERS"
  for header in "${HEADERS[@]}"; do
    EXTRA_ARGS+=("-H" "$header")
  done
fi

curl -fsS -X POST "$EVENT_URL" \
  -H "Content-Type: application/json" \
  "${EXTRA_ARGS[@]}" \
  --data-binary "@$ANCHOR_FILE"

echo "✅ Broadcasted Merkle root"
