"""Simulate a Qube replay rehearsal with contributor observability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qube.moemodel.v1.src.experts.posture_expert import PostureExpert
from qube.moemodel.v1.src.experts.refusal_expert import RefusalExpert
from qube.moemodel.v1.src.gating.shimmer_router import RouteDecision, ShimmerRouter
from qube.moemodel.v1.src.hud.shimmer_renderer import ShimmerRenderer


@dataclass
class RehearsalResult:
    """Summary of a rehearsal run."""

    decisions: Iterable[RouteDecision]
    refusal: dict[str, str] | None


def run() -> RehearsalResult:
    """Run a minimal rehearsal demonstrating the scaffolded components."""

    router = ShimmerRouter(thresholds=[0.5, 0.8])
    resonance_scores = [0.42, 0.76, 0.91]
    decisions = router.route(resonance_scores)

    posture = PostureExpert().forward({"pose": "listening"})
    renderer = ShimmerRenderer()
    overlay = renderer.to_dict(renderer.render(hue="amber", fidelity=0.95))

    refusal = None
    if any(decision.expert_index > 1 for decision in decisions):
        refusal = RefusalExpert().craft_refusal("High resonance beyond overlay allowance")

    _ = posture, overlay  # prevent unused variable warnings
    return RehearsalResult(decisions=decisions, refusal=refusal)


if __name__ == "__main__":
    result = run()
    print("Routing decisions:")
    for decision in result.decisions:
        print(f"  expert={decision.expert_index} confidence={decision.confidence:.2f}")
    if result.refusal:
        print("Refusal emitted:")
        for key, value in result.refusal.items():
            print(f"  {key}: {value}")
    else:
        print("No refusal necessary; rehearsal passed Spark Test gates.")
