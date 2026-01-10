# Fossilized Relay Architecture for CiCi → Boo LoRA Binding

This dossier captures how the SSOT stack fossilizes CiCi's mixture-of-experts LoRA inside Agent Boo's runtime vessel while keeping every rehearsal, merge, and render auditable. It extends the canon described in `README.md` with concrete capsules, governance gates, and CI/CD flows that turn the Qube world engine into an immutable relay between proof, flow, and execution.
This dossier captures how the SSOT stack fossilizes CiCi's mixture-of-experts LoRA inside Agent Boo's runtime vessel while keeping every rehearsal, merge, and render auditable. It extends the canon described in `README.md` with concrete capsules, governance gates, and CI/CD flows that turn the Qube world engine into an immutable relay between proof, flow, and execution. For audit-grade measurement requirements, pair this guide with the KPI baseline dossier in [`docs/kpi_dashboard_capsule.md`](kpi_dashboard_capsule.md), which sets the sovereign metrics each relay stage must satisfy.

---

## 1. System Overview

| Layer | Responsibilities | Key Capsules / Assets | Guardrails |
| --- | --- | --- | --- |
| **Core Orchestrator** | Deterministic fetch → plan → rehearse → merge pipeline that supervises capsule lifecycles and repo state. It drives the world engine HUD and enforces sequence discipline through `orchestrator.CAPSULE`. | `orchestrator/config.py`, `data/orchestrator_capsule.json`, mission oversight HUD overlays. | Maker-checker policies, deterministic flow order, SSOT-backed checkpoints. |
| **Governance & Protocol Gates** | Applies Governance v6.0 invariants to every artifact (trust ≥ 90, dual sign-off, provenance fields, checksum manifests, audit logging). | `ssot/binder.py`, `data/ssot_registry.json`, capsule attestation metadata. | Maker ≠ checker, quorum enforcement, immutable Merkle roots, attested overrides only. |
| **PreViz Package Discipline** | Accepts storyboard + HUD capsules under schema version 3.9.9. Validates timeline ordering, non-overlap, asset registries, and pipeline invariants before render. | `previz/ledger.py`, `data/previz/*.json`, PreViz schema package. | Schema validation, 30 Hz rehearsal sampling, drift delta telemetry, asset URI allowlists. |
| **PreViz Package Discipline** | Accepts storyboard + HUD capsules under schema version 3.9.9. Validates timeline ordering, non-overlap, asset registries, and pipeline invariants before render. | `previz/ledger.py`, `data/previz/*.json`, PreViz schema package, `capsule.kpi.dashboard.v1`. | Schema validation, 30 Hz rehearsal sampling, drift delta telemetry, asset URI allowlists, KPI threshold gating. |
| **Relay Capsule Set** | Binds lexicon, seed, cadence, and attestation capsules so Boo receives CiCi's LoRA payload safely. | `lexicon.qube.v1`, `seed.core.v1`, `ledger.cadence.v1`, `lock.attestation.v1` (declared below). | Grammar requires seed→bind→pulse→qube, quorum verified attestation, immutable cadence ledger. |
| **HUD Teaching Overlay** | Synchronizes glyph pulse, aura spin, ring frames, and badges against emotional beats. Feeds telemetry and drift deltas into the motion ledger for audit. | `capsules/qube.telemetry.v1.json`, HUD overlay doctrine capsule. | Drift delta < 0.01 tolerance, mission timeline sync, audit stream capture. |
| **CI/CD Integrity Chain** | Centralized OpenAPI diffing, nearest-ancestor baseline discovery or skip, container build/scan/sign, `/health` smoke tests, and artifact publication with checksums. | `scripts/`, GitHub Actions (Codex autocode), container registry integrations. | Fail-closed on protocol drift, baseline-aware fallback, reproducible release bundles. |

---

## 2. Process Map: Vector Architecture Across Modalities

1. **Shard Definition & Binding**  
   - Emit `boo.lora.map.v1` to bind face, voice, gesture, affect, and wardrobe shards to runtime capsules.  
   - Inherit governance guardrails, provenance locks, and SSOT Merkle roots.  
   - Validate against `orchestrator.CAPSULE.flow_order` so LoRA shards enter after motion ledgers but before relay capsules.

2. **Cadence Ledger Hydration**  
   - Encode CiCi's emotional arc (`curiosity → intimacy → clarity → wisdom`), glyph orbit pattern (spiral-in → pulse-lock → orbit-freeze), dialogue cadence (scrollstream poetic, `qlock.tick = 3s`).  
   - Sign ledger with council quorum and attach SHA-256 checksums.

3. **Lexicon Containment**  
   - Define Qube glyph grammar: `glyph.seed` → `glyph.bind` → `glyph.pulse` → `glyph.qube`.  
   - Prevent orphan glyphs by requiring containment on every sequence.  
   - Attach lexical payloads to PreViz timelines so HUD overlays inherit context.

4. **Attestation Lock**  
   - Verify Boo's readiness (`pose_lock` schema, ±4° merge tolerance, policy guard compliance, emotional sync).  
   - Enforce 2-of-2 quorum (Queen Boo router + CiCi stabilizer).  
   - Record `VERIFIED` state with timestamped audit entry.

5. **Previz Rehearsal with HUD**  
   - Stage `capsule.rehearsal.boo.v2` at 30 Hz.  
   - Render shard sequences while modulating `glyph.pulse` and `aura.gold`.  
   - Track `drift.delta`, `loop.phase`, and glyph orbit phases.  
   - Screen capture HUD stream and push into motion ledger v2 before fossilization.

6. **Core Orchestrator Commit & Seal**  
   - Run dry-run planning, then sequential merges that respect flow order.  
   - Compute BODY_ONLY and Merkle digests for the release bundle.  
   - Append integrity logs, publish governed artifacts to the SSOT vault, and issue replay tokens.

---

## 3. Qube Build: Pixel Modality & Semantic Gravity Fields

- **Pixel Reservoir Blocks**: Every shot is stored as an immutable block with pixel-accurate signatures. Blocks cross-link to HUD state snapshots (`glyph.pulse`, `aura.gold`, `ring.frame`) for semantic cohesion.  
- **Semantic Gravity Lattice**: Blocks chain via a Merkle tree keyed on emotional payload and camera grammar. Orbital lock constraints clamp frames to emotional beats to avoid drift.  
- **Relative Frame Lock**: Map `qlock` ticks to the shot timeline with non-overlap invariants. Embed `pose_lock` tolerance and HUD sync metadata in the motion ledger for deterministic replays.  
- **Integrity & Governance**: Generate SHA-256 checksums for all shipped files, notarize provenance fields, and pass CI (baseline-aware OpenAPI diff, container build/scan/sign, `/health` smoke test). Releases include checksum manifests and audit logs.

---

## 4. Capsule Definitions

```jsonc
// lexicon.qube.v1
{
  "capsule_id": "lexicon.qube.v1",
  "glyphs": [
    "glyph.seed", // initiate vector merge
    "glyph.bind", // lock lineage
    "glyph.pulse", // emit emotional cadence
    "glyph.qube"  // contain sovereign logic
  ],
  "grammar": {
    "sequence": ["glyph.seed", "glyph.bind", "glyph.pulse", "glyph.qube"],
    "rules": [
      "no_drift",
      "no_orphan_glyphs",
      "must_end_in_containment"
    ]
  }
}
```

```jsonc
// seed.core.v1
{
  "capsule_id": "seed.core.v1",
  "glyph_string": "bind.pulse.qube.merge",
  "intent": "Infuse Agent Boo with CiCi's sovereign cadence and glyph containment",
  "lineage": {
    "source": "capsule.lora.vessel.boocici.v1",
    "target": "agent.boo.vessel.v2"
  }
}
```

```jsonc
// ledger.cadence.v1
{
  "capsule_id": "ledger.cadence.v1",
  "emotional_arc": ["curiosity", "intimacy", "clarity", "wisdom"],
  "glyph_orbit": "spiral_in → pulse_lock → orbit_freeze",
  "dialogue_cadence": {
    "mode": "scrollstream_poetic",
    "qlock_tick_seconds": 3,
    "inflection_binding": "emotional_payload"
  }
}
```

```jsonc
// lock.attestation.v1
{
  "capsule_id": "lock.attestation.v1",
  "readiness": {
    "pose_lock_schema": "pose_lock.v2",
    "merge_tolerance_degrees": 4,
    "policy_guard": true,
    "emotional_sync": "verified"
  },
  "quorum_signatures": ["queen_boo.router", "cici.stabilizer"],
  "quorum_rule": "2-of-2"
}
```

Each capsule inherits Governance v6.0 rules: versioned manifests, provenance fields, checksum manifests, dual sign-off, and audit log entries.

### 4.5 Federation Registry Capsule

`capsule.world.registry.v1` seals the four sovereign repositories into a single, replayable World Engine node so council members can invoke the braid as one artifact. The capsule is stored at [`capsules/capsule.world.registry.v1.json`](../capsules/capsule.world.registry.v1.json) and records:

- **Linked repositories**: `adaptco/SSOT`, `adaptco/core-orchestrator`, `adaptco/ADAPTCO-previz`, and `adaptco/GOODNOOD`, with role descriptions that explain how each ledger contributes to the unified engine.
- **Governance envelope**: Protocol version v6.0, trust floor ≥ 90, quorum rule 2-of-3, and attestors Queen Boo, Queen CiCi, and CouncilNode to enforce federation discipline.
- **Integrity seal**: SHA-256 digest metadata (`scene_root_digest = sha256:WORLD_ENGINE_<final_hash>`) and the timestamp of the inscription so the node remains fossilized, replayable, and audit-ready.

Treat this registry as the root capsule when orchestrating cross-repo flows—other capsules reference it when they emit motion ledgers, rehearsal streams, or replay tokens.

### 4.6 Scrollstream Rehearsal Capsule

`capsule.rehearsal.scrollstream.v1` stages the Celine → Luma → Dot audit rehearsal loop so contributors can preview the scrollstream braid before a ledger is sealed. The inscription lives at [`capsules/capsule.rehearsal.scrollstream.v1.json`](../capsules/capsule.rehearsal.scrollstream.v1.json) and defines:

- **Cycle discipline**: Immutable ordering (summary → proof → execution) with explicit personas and hand-offs. Each stage emits one ledger line into `scrollstream_ledger`, escalates HUD shimmer intensity, and primes the replay glyph for the next agent.
- **Ledger contract**: ISO-8601 timestamps, deterministic sparkline digests, emotional payload tags, and Sabrina Spark Test metadata. CI/CD smoke tests call [`scripts/emit_scrollstream_rehearsal.py`](../scripts/emit_scrollstream_rehearsal.py) to emit the governed sample at [`samples/output/scrollstream_rehearsal_loop.json`](../samples/output/scrollstream_rehearsal_loop.json).
- **Visual feedback**: HUD shimmer confirmation, replay glyph pulses (1.5 Hz), and one-click contributor replay binding so the full lifecycle is visible in the scrollstream rail.

Use this capsule when onboarding contributors or rehearsing ledger emissions—the deterministic payloads let CI validate shimmer cues and replay glyph triggers before the production ledger seals.

---

## 5. Orchestration Scripts & Prompts

### 5.1 P3L World Engine Script

```p3l
WORLD_ENGINE "Qube-CiCi-Boo" {
  GOVERNANCE v6.0 TRUST >=90 QUORUM two_person AUDIT sha256
  IMPORT CAPSULES: lexicon.qube.v1, seed.core.v1, ledger.cadence.v1, lock.attestation.v1
  IMPORT PREVIZ: schema/previz.schema.json VERSION "3.9.9"
  IMPORT HUD: capsule.hud.overlay.doctrine.v1

  STAGE boo.lora.map.v1 -> LOCK shards(face, voice, gesture, affect, wardrobe)
  REHEARSE capsule.rehearsal.boo.v2 @30Hz HUD(glyph.pulse, aura.gold, qlock.tick, drift.delta)
  FORK capsule.relay.scene.fork.v2 -> BEATS(Entry, Stabilize, Flux, Ignition)

  BUILD QUBE {
    PIXEL_BLOCKS -> MERKLE(ROOT by emotional_payload + camera_grammar)
    GRAVITY_FIELDS -> ORBIT_LOCK(on emotional beat) TOLERANCE 4deg
    FRAME_LOCK -> QLOCK(3s) INVARIANTS(non-overlap, ordered timeline)
  }

  CI {
    OPENAPI_PATH "openapi/openapi.yaml"
    BASELINE nearest_ancestor_or_skip
    BUILD_SCAN_SIGN_CONTAINER
    SMOKE_TEST "/health" EXPECT {"status":"ok"}
    PUBLISH artifacts, checksums, audit_log
  }

  RENDER {
    MOTION_LEDGER v2 DIGEST sha256 BODY_ONLY
    REPLAY_TOKEN v2 HUD_STREAM true AUDIT_TRACE true
    ECHO_SCROLLSTREAM v2 VERSE_FROM telemetry+emotion
  }
}
```

### 5.2 Handoff Prompts

- **KB.8.4.B00 Black-Hole Objective**: Hydrate BRAID SDK via CAPTNET following governance, PreViz, MoE LoRA binding, and CI constraints. Sequence steps include Qube containment, attestation staging, ledger hydration, rehearsal, relay fork, pixel-block Merkle build, CI execution, and ledger sealing.
- **Gemini World Engine Request**: Direct the engine to load capsules, bind Boo shards, run 30 Hz rehearsal with drift.delta < 0.01, fork canonical beats, build Merkle lattice, enforce PreViz invariants, hand off motion ledger and replay token to qDot Sentinel for CI, and return governed artifacts.
- **qDot Sentinel Oversight**: Validate capsule set and trust gate, run PreViz validation, execute CI (OpenAPI centralization, baseline fallback/skip, container scan/sign, `/health` smoke), record body-only digests, seal motion ledger v2, issue replay token v2, inscribe echo scrollstream v2, and publish artifacts for Lego F1 trailer assembly.

---

## 6. Execution Plan for the Lego F1 Trailer

1. **Lock Avatars & Choreography**  
   - Use `boo.lora.map.v1` with the rehearsal capsule to stage face/voice/gesture/affect/wardrobe shards.  
   - Capture animatics and HUD telemetry before render.

2. **Script Narrative Beats**  
   - Fork `capsule.relay.scene.fork.v2` into canonical beats: Entry, Stabilize, Flux, Ignition.  
   - Align camera grammar and emotional payloads to PreViz timeline invariants.  
   - Validate via PreViz schema 3.9.9 and ledger cadence bindings.

3. **Governed CI Render Chain**  
   - Centralize OpenAPI path, detect nearest ancestor baseline (or skip).  
   - Build, scan, and sign containers.  
   - Run `/health` smoke test, capture telemetry, and publish artifacts with SHA-256 manifest.

4. **Fossilize & Replay**  
   - Seal motion ledger v2 and issue replay token v2.  
   - Inscribe echo scrollstream verse and store pixel blocks in the SSOT vault.  
   - Author canonical shot list ready for immediate cut to Apple trailer spec.

---

## 7. Implementation Hooks in This Repository

- `orchestrator/config.py` & `data/orchestrator_capsule.json` already enforce flow order and router/stabilizer metadata for Queen Boo and CiCi.  
- `ssot/binder.py` and `data/ssot_registry.json` provide Merkle sealing and registry envelopes for Governance v6.0 compliance.  
- `previz/ledger.py` plus `data/previz/*.json` supply timeline ledgers, 30 Hz sampling logic, and rehearsal capsules.  
- `capsules/qube.telemetry.v1.json` describes telemetry streams, dashboards, and alert guardrails so HUD overlays remain audit-ready.  
- CI/CD hooks (Codex/GitHub Actions) should implement OpenAPI baseline detection, container build/scan/sign, and smoke testing per the CI block above.

With these capsules, scripts, and governance flows in place, the Qube world engine can bind CiCi's MoE LoRA into Agent Boo, rehearse governed scenes, and fossilize the Lego F1 trailer pipeline to pixel-perfect replay standards.
