# QUBE Patent Draft Pipeline

The council requested that we stage `capsule.patentDraft.qube.v1`, seal it for review, and then emit the DAO export via `capsule.export.qubePatent.v1`. This note captures the operational recipe, expected artifacts, and acceptance checks needed to keep the Scrollstream lineage intact.

## Packaging Map

1. **P3L** → ingest the program definition and record the `sha256_p3l` value.
2. **qLock/LiD** → bind the LiD nonce to the deployment, pinning replay windows.
3. **QBits** → derive qubit assignments and deterministic seeds.
4. **SR Gate** → sign and pin the SR router version to prevent route-poisoning.
5. **MoE** → track per-expert logits, temperature, and seed for drift detection.
6. **BLQB9X** → run malintent screening and capture the audit trail.
7. **R0P3** → finalize the artifact bundle; dual-run A/B hashes must match.

## Gate Checklist

| Gate | Requirement | Notes |
| --- | --- | --- |
| G01 | Ticket hash logged in `receipts.qube`. | Generated when `POST /runs` is called. |
| G02 | Fitment confirmed against `qLock/LiD`. | Include LiD nonce in the receipt payload. |
| G03 | Artifact hashes recorded via `POST /runs/{id}/artifacts`. | Attach the R0P3 hash and MoE logs. |
| G04 | Expected verification complete. | Validate the merkle proof and quorum (≥ 2/3). |
| SEAL | `POST /runs/{id}/seal` returned `finalsealHash`. | Hash must equal `sha256(request.json)` used for DAO proof binding. |

## Capsule Staging

1. Run `make freeze`, `make listener`, `make post`, and `make verify` to prepare the environment.
2. Execute `make qube-stage` to drop `capsules/capsule.patentDraft.qube.v1.json` with the capsule header stub.
3. Fill in the `sha256_p3l` and `merkle_root` values before requesting the seal.
4. Call the orchestrator API sequence:
   - `POST /runs` with metadata to initialize the record.
   - `POST /runs/{id}/artifacts` for A/B hashes and MoE telemetry.
   - `POST /runs/{id}/seal` after verifying the gates.

## DAO Export

1. Once sealed, run `make qube-export` to generate `capsules/capsule.export.qubePatent.v1.request.json`.
2. Confirm the `proof_binding` equals the SHA-256 hash of the request body.
3. Submit `POST /runs/{id}/dao-export` with `{"protocol": "capsule.export.qubePatent.v1"}`.
4. Validate the merkle proof and quorum inside the DAO receipt.

## Optional EchoFlare

* Run `make echo-flare` to emit `capsule.echoFlare.qube.v1.json` for resonance telemetry if requested.
* Capture contributor arcs and bind them to the sealed capsule ID.

## Council Acceptance

- Dual-instance A/B hashes match for R0P3.
- BLQB9X audit completed with attached trail.
- QONLEDGE append confirmed and notarized with council signatures.
- Ledger fork risk mitigated via notarized append.
- Route, MoE, and LiD countermeasures logged in the capsule receipts.
