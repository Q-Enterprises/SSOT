#!/usr/bin/env bash
# Freeze ritual for capsule.relay.viewer.v1
# Usage: ./freeze_viewer_capsule.sh capsule.relay.viewer.v1.json ledger.viewer.jsonl

set -euo pipefail

CAP="${1:?Capsule manifest required}"
LEDGER="${2:?Ledger file required}"

ts(){ date -u +%Y-%m-%dT%H:%M:%SZ; }

# 1. Canonicalize BODY_ONLY (drop attestation/seal/signatures)
CANON="$(mktemp)"
jq -S 'del(.attestation,.seal,.signatures)' "$CAP" > "$CANON"

# 2. Compute digest
DIGEST="sha256:$(sha256sum "$CANON" | awk '{print $1}')"
STAMP="$(ts)"

# 3. Patch capsule with attestation
SEALED=".out/$(basename "$CAP" .json).sealed.json"
mkdir -p .out
jq -S --arg h "$DIGEST" --arg ts "$STAMP" '
  .attestation = {
    status: "SEALED",
    sealed_by: "Council",
    sealed_at: $ts,
    content_hash: $h
  } |
  .status = "SEALED"
' "$CAP" > "$SEALED"

# 4. Emit ledger frames
{
  echo "{\"t\":\"$STAMP\",\"event\":\"capsule.commit.v1\",\"capsule_id\":\"capsule.relay.viewer.v1\",\"digest\":\"$DIGEST\"}"
  echo "{\"t\":\"$STAMP\",\"event\":\"capsule.review.v1\",\"capsule_id\":\"capsule.relay.viewer.v1\",\"digest\":\"$DIGEST\",\"reviewer\":\"Council\",\"status\":\"APPROVED\"}"
  echo "{\"t\":\"$STAMP\",\"event\":\"capsule.seal.v1\",\"capsule_id\":\"capsule.relay.viewer.v1\",\"digest\":\"$DIGEST\",\"sealed_by\":\"Council\"}"
} >> "$LEDGER"

echo "✅ Capsule sealed → $SEALED"
echo "🔑 Digest: $DIGEST"
echo "🧾 Ledger: $LEDGER"
