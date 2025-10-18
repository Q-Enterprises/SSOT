# Capsules

This directory contains declarative capsules that describe the canonical data contracts used by the Qube stack.

## `qube.telemetry.v1`

The `qube.telemetry.v1` capsule defines the cockpit view for the relay triangle (Proof → Flow → Execution). It specifies:

- **Streams** that ingest sealed SSOT roots, orchestrator checkpoints, and Sol.F1 acknowledgements.
- **Field catalog** entries for bundle hashes, avatars, quorum confidence, proof-flow drift, replay tokens, and latency measurements.
- **Dashboard layouts** including the node graph bindings and supporting widgets (time-series, histograms) used by PackNet/TAMS visualizations.
- **Alert guardrails** that trigger Dot rollbacks or council pings when quorum, drift, or replay invariants fall out of tolerance.

Use the schema to validate telemetry payloads and to bootstrap the dashboard configuration for observability tooling. The example embedded in the schema demonstrates how to wire live Kafka, NATS, and HTTPS feeds into a unified cockpit.

## `capsule.patentDraft.qube.v1`

The council draft capsule locks the patent braid for QUBE artifacts before they are sealed and exported. It captures:

- **Packaging map** that threads inputs through qLock/LiD, SR Gate, MoE, BLQB9X, and the R0P3 emission, including status for gates G01–G04 and the SEAL trigger.
- **Integrity envelope** with deterministic A/B hashes, merkle root, quorum requirement, and the QONLEDGE ledger append target.
- **Threat surface** mitigations covering SR Gate route signing, MoE drift telemetry, LiD replay protection, and ledger notarization.
- **Orchestrator alignment** describing the make-run cadence and the REST hooks (runs, artifacts, seal, DAO export) required for council receipts.

Use this capsule to stage the patent draft prior to sealing and to drive the audit checklist for council review.

