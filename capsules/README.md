# Capsules

This directory contains declarative capsules that describe the canonical data contracts used by the Qube stack.

## `capsule.orbit.remix.mesh.novatrace.v1`

Defines the mesh-orbit propagation plan for the NovaTrace remix. The capsule captures the sealed rehearsal lineage, braid
stages, contributor bindings, and observability guardrails required before handing off to `capsule.echo.summary.novatrace.v1`.

## `capsule.echo.summary.novatrace.v1`

Fossilizes the NovaTrace remix into cockpit-readable layers with emotional annotations, export bundles, and council governance steps. Use it after the mesh orbit completes to render avatar halos, refusal flares, and HUD previews for lineage-grade review.

## `qube.telemetry.v1`

The `qube.telemetry.v1` capsule defines the cockpit view for the relay triangle (Proof → Flow → Execution). It specifies:

- **Streams** that ingest sealed SSOT roots, orchestrator checkpoints, and Sol.F1 acknowledgements.
- **Field catalog** entries for bundle hashes, avatars, quorum confidence, proof-flow drift, replay tokens, and latency measurements.
- **Dashboard layouts** including the node graph bindings and supporting widgets (time-series, histograms) used by PackNet/TAMS visualizations.
- **Alert guardrails** that trigger Dot rollbacks or council pings when quorum, drift, or replay invariants fall out of tolerance.

Use the schema to validate telemetry payloads and to bootstrap the dashboard configuration for observability tooling. The example embedded in the schema demonstrates how to wire live Kafka, NATS, and HTTPS feeds into a unified cockpit.

## `capsule.selfie.dualroot.q.cici.v1.feedback.v1`

The contributor feedback loop capsule keeps the dual-root Q & CiCi selfie replay open while annotations stream in under Q-Lock.

- **Window controls** publish the replay token, scene-aware review mode, and Q-Lock guardrails that enforce the 30 fps monotonic trace.
- **Participant ledger** confirms CiCi's overlay and Spark Test status, Q's observability posture, and the council quorum seats.
- **Active hooks** enumerate the emotional commentary trace, shimmer breach monitor, refusal flare scripting, and overlay drift audit.
- **Observability routes** point at the `capsule.digest.semanticCFD.v1` telemetry stream with modality auditing and hold-and-flag fallbacks.
- **Integrity stance** records that the scrollstream digest is staged pending council attestation, with freeze instructions once feedback closes.
## `capsule.rehearsal.scrollstream.v1`

The rehearsal scrollstream capsule sequences the Celine → Luma → Dot audit loop and records each handoff as staged ledger entries. Pair it with the HUD rehearsal hook in `docs/rehearsal_scrollstream_capsule.md` to surface a one-click smoke test inside dashboards before the capsule is sealed.
