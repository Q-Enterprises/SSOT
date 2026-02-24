# TriAxisKernel Hashing & Determinism Transcript Ritual

## Proceed: Compute & Emit Hashes

This document provides the canonical hashing ritual for TriAxisKernel artifacts and
DeterminismTranscript objects. All digests are SHA-256 over JSON Canonicalization Scheme
(JCS) bytes, with the required exclusions and insertion points described below.

## 1. Canonicalization Rules (must be followed exactly)

- **Canonical form:** JSON Canonicalization Scheme (JCS).
- **Whitespace:** none; use JCS byte ordering.
- **Field ordering:** JCS canonical ordering (lexicographic by Unicode code points).
- **Number formatting:** use plain JSON numbers (no trailing zeros beyond necessary).
- **Timestamps:** ISO-8601 UTC strings unchanged.
- **Excluded fields when hashing transcripts:** when computing `transcript_digest`, exclude
  `attestation.signature` and `transcript_digest` itself.

## 2. Hash Scopes and What to Compute

Compute these digests over the **JCS bytes** of each named scope:

- **ShapeProgram.v1 digest**
  - Scope name: `ShapeProgram.v1`
  - Input: JCS(ShapeProgram object)
  - Output field: `sha256:<hex64>` → insert into
    `TriAxisKernel.components[ShapeProgram].integrity.digest`

- **AgentPlane.v1 digest**
  - Scope name: `AgentPlane.v1`
  - Input: JCS(AgentPlane object)
  - Output field: `sha256:<hex64>` → insert into
    `TriAxisKernel.components[AgentPlane].integrity.digest`

- **Initial state hash**
  - Scope name: `InitialState`
  - Input: JCS(initial_state object from AgentPlane)
  - Output field: `ReplayCourt.initial_state_hash`

- **Control sequence hash**
  - Scope name: `ControlSequence`
  - Input: JCS(control_sequence array from AgentPlane.proposal)
  - Output field: `ReplayCourt.control_sequence_hash`

- **Per-tick state hashes** (for transcript)
  - Scope name: `StateSnapshot_i` for each tick `i`
  - Input: JCS(state_snapshot_i)
  - Output: `state_hashes[i]` in DeterminismTranscript.v1

- **Merkle root**
  - Build binary Merkle tree over `state_hashes[]` (use raw 32-byte binary values in
    canonical order), compute SHA-256 root, encode as `sha256:<hex64>`.

- **Full transcript digest**
  - Scope name: `DeterminismTranscript`
  - Input: JCS(full transcript object) **excluding** `transcript_digest` and
    `attestation.signature`
  - Output field: `transcript_digest`

- **TriAxisKernel full artifact digest**
  - Scope name: `TriAxisKernel.FULL_ARTIFACT`
  - Input: JCS(full TriAxisKernel envelope after inserting component digests and the
    transcript hash)
  - Output field: `TriAxisKernel.integrity.digest`

## 3. Deterministic Command Recipe (example)

Use a JCS tool (or library) to canonicalize, then compute SHA-256.
Replace `jcs` with your canonicalizer.

```bash
# 1. Canonicalize ShapeProgram
cat shapeprogram.json | jcs > shapeprogram.jcs
sha256sum shapeprogram.jcs | awk '{print $1}'  # yields hex64

# 2. Canonicalize AgentPlane
cat agentplane.json | jcs > agentplane.jcs
sha256sum agentplane.jcs | awk '{print $1}'

# 3. Canonicalize initial state and control sequence
cat initial_state.json | jcs > initial_state.jcs
sha256sum initial_state.jcs | awk '{print $1}'

cat control_sequence.json | jcs > control_sequence.jcs
sha256sum control_sequence.jcs | awk '{print $1}'

# 4. Per-tick snapshots
for i in $(seq 0 $((TICKS-1))); do
  cat state_snapshot_$i.json | jcs > state_$i.jcs
  sha256sum state_$i.jcs | awk '{print $1}' >> state_hashes.txt
done

# 5. Build Merkle root (example Python snippet)
python3 - <<'PY'
import hashlib

with open('state_hashes.txt') as f:
    leaves = [bytes.fromhex(line.strip()) for line in f]

def merkle_root(leaves):
    if len(leaves) == 1:
        return leaves[0]
    while len(leaves) > 1:
        if len(leaves) % 2:
            leaves.append(leaves[-1])
        leaves = [
            hashlib.sha256(a + b).digest()
            for a, b in zip(leaves[0::2], leaves[1::2])
        ]
    return leaves[0]

root = merkle_root(leaves)
print(root.hex())
PY

# 6. Assemble transcript.json (exclude transcript_digest and signature), canonicalize, hash
cat transcript_partial.json | jcs > transcript_partial.jcs
sha256sum transcript_partial.jcs | awk '{print $1}'
```

## 4. Insertion Points and Finalization Ritual

1. Compute component digests and insert them into the TriAxisKernel envelope at the
   `__COMPUTE_OVER_*__` placeholders.
2. Compute per-tick `state_hashes[]` and `merkle_root`; insert into
   DeterminismTranscript.v1.
3. Canonicalize the transcript (without signature), compute `transcript_digest`, insert it.
4. Produce attestation signature over `transcript_digest` using authorized signer; insert
   into `attestation.signature`.
5. Canonicalize the full TriAxisKernel envelope (now containing all component digests and
   the transcript digest), compute `TriAxisKernel.integrity.digest`.
6. Store the finalized artifact and transcript in Golden S3 with indexing keys:
   `(kernel_version.binary_digest, seed_domain.seed_value, input_capsule_ref.digest,
   transcript_digest)`.

## 5. Final Envelope Template (placeholders replaced by computed tokens)

Replace `<hex>` markers with computed hex64 values prefixed by `sha256:`.

```json
{
  "artifact_id": "TriAxisKernel_Worldline_0001",
  "schema_version": "TriAxisKernel.v1",
  "integrity": {
    "hash_algorithm": "SHA-256",
    "scope": "FULL_ARTIFACT",
    "digest": "sha256:<TRIAXIS_FULL_DIGEST_HEX>"
  },
  "components": [
    {
      "scope": "ShapeProgram.v1",
      "digest": "sha256:<SHAPEPROGRAM_HEX>"
    },
    {
      "scope": "AgentPlane.v1",
      "digest": "sha256:<AGENTPLANE_HEX>"
    },
    {
      "scope": "ReplayCourt.v1",
      "initial_state_hash": "sha256:<INITIAL_STATE_HEX>",
      "control_sequence_hash": "sha256:<CONTROL_SEQUENCE_HEX>",
      "transcript_digest": "sha256:<TRANSCRIPT_DIGEST_HEX>"
    }
  ]
}
```

## 6. Validation Checklist (performed before signing)

- Validate hash scopes, canonicalization rules, and exact insertion points.
- Generate `state_hashes[]` and the Merkle root from snapshot digests.
- Confirm `transcript_digest` excludes `attestation.signature` and itself.
- Confirm final `TriAxisKernel.integrity.digest` includes all inserted digests.
- Archive the finalized artifact and transcript under Golden S3 indexing keys.
