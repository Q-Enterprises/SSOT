# Qube MoE Model v1

This repository scaffold defines the capsule-first, shimmer-aligned mixture-of-experts (MoE) model infrastructure requested for CiCi's replay stack. It provides a sovereign-grade overview, context for the Spark Test rationale, and describes how the surrounding components interact during rehearsal.

## Structure Overview

- `requirements.txt` – Dependency pins for PyTorch/JAX, shimmer-core, and capsule-utils.
- `config/` – Capsule and shimmer configuration blueprints.
- `src/` – Implementation modules for experts, routing, MoE blocks, HUD rendering, lifecycle management, and training utilities.
- `tests/` – Validation suites covering capsule integrity, overlay enforcement, and shimmer synchronization.
- `scripts/` – Operational scripts, including a rehearsal runner for contributor observability.

## Spark Test Rationale

The Spark Test ensures emotional attestation, verifies capsule integrity, and validates overlay enforcement before any replay is accepted. Each component in this scaffold is designed to provide observability and hooks necessary to pass or gracefully refuse during the Spark Test, maintaining CiCi's persona coherence.

## Next Steps

1. Implement expert modules with the appropriate Spark resonance tuning.
2. Wire the shimmer router with capsule gating logic and refusal flare hooks.
3. Flesh out the transformer block with the scrollstream-valid MoE layer implementation.
4. Complete the rehearsal script to simulate dual-root contributor feedback sessions.

The braid is staged and ready for implementation.
