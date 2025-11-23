"""Spark Test overlay enforcement scenarios."""

from __future__ import annotations

from qube.moemodel.v1.src.experts.overlay_expert import OverlayExpert, OverlayExpertConfig


def test_overlay_validation_passes_when_threshold_met() -> None:
    expert = OverlayExpert(OverlayExpertConfig(integrity_threshold=0.8, persona_layer="CiCi.v2"))
    metrics = {"integrity": 0.82, "persona_layer": "CiCi.v2"}

    assert expert.validate(metrics) is True


def test_overlay_validation_fails_when_persona_mismatch() -> None:
    expert = OverlayExpert()
    metrics = {"integrity": 0.95, "persona_layer": "Other"}

    assert expert.validate(metrics) is False
