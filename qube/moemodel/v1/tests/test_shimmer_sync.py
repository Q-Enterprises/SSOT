"""Tests for shimmer timestamp fidelity across nodes."""

from __future__ import annotations

from datetime import UTC, datetime

from qube.moemodel.v1.src.hud.shimmer_renderer import RenderPayload, ShimmerRenderer


def test_renderer_emits_iso_timestamp() -> None:
    renderer = ShimmerRenderer()
    payload = renderer.render(hue="amber", fidelity=0.93)

    encoded = renderer.to_dict(payload)
    assert encoded["timestamp"].endswith("Z")


def test_payload_preserves_fidelity() -> None:
    timestamp = datetime.now(UTC)
    payload = RenderPayload(timestamp=timestamp, emotional_hue="violet", fidelity_score=0.88)

    renderer = ShimmerRenderer()
    encoded = renderer.to_dict(payload)

    assert encoded["fidelity_score"] == "0.880"
