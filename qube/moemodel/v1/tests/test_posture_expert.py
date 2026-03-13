"""Tests for PostureExpert functionality."""

from __future__ import annotations

from qube.moemodel.v1.src.experts.posture_expert import PostureExpert, PostureExpertConfig


def test_forward_with_default_config() -> None:
    expert = PostureExpert()
    state = {"other_key": "other_value"}
    result = expert.forward(state)

    assert result["gesture_intent"] == "open"
    assert result["micro_adjustment"] == 0.1
    assert result["other_key"] == "other_value"


def test_forward_with_custom_config() -> None:
    config = PostureExpertConfig(default_posture="closed", micro_adjustment_rate=0.5)
    expert = PostureExpert(config)
    state = {}
    result = expert.forward(state)

    assert result["gesture_intent"] == "closed"
    assert result["micro_adjustment"] == 0.5


def test_forward_preserves_existing_gesture_intent() -> None:
    expert = PostureExpert()
    state = {"gesture_intent": "existing"}
    result = expert.forward(state)

    assert result["gesture_intent"] == "existing"


def test_forward_overwrites_micro_adjustment() -> None:
    expert = PostureExpert()
    state = {"micro_adjustment": 0.99}
    result = expert.forward(state)

    assert result["micro_adjustment"] == 0.1


def test_forward_immutability() -> None:
    expert = PostureExpert()
    state = {"key": "value"}
    expert.forward(state)

    assert state == {"key": "value"}
