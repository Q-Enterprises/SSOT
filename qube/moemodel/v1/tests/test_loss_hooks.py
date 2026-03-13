"""Tests for MoE loss hooks."""

from __future__ import annotations
import pytest
from qube.moemodel.v1.src.training.loss_hooks import LossMetrics, drift_guard, utilization_penalty, summarize_losses

def test_drift_guard_below_limit() -> None:
    metrics = LossMetrics(utilization=0.5, drift=0.05)
    assert drift_guard(metrics, limit=0.1) == 0.0

def test_drift_guard_at_limit() -> None:
    metrics = LossMetrics(utilization=0.5, drift=0.1)
    assert drift_guard(metrics, limit=0.1) == 0.0

def test_drift_guard_above_limit() -> None:
    metrics = LossMetrics(utilization=0.5, drift=0.15)
    assert drift_guard(metrics, limit=0.1) == pytest.approx(0.05)

def test_drift_guard_custom_limit() -> None:
    metrics = LossMetrics(utilization=0.5, drift=0.25)
    assert drift_guard(metrics, limit=0.2) == pytest.approx(0.05)

def test_utilization_penalty_above_target() -> None:
    metrics = LossMetrics(utilization=0.9, drift=0.05)
    assert utilization_penalty(metrics, target=0.8) == 0.0

def test_utilization_penalty_at_target() -> None:
    metrics = LossMetrics(utilization=0.8, drift=0.05)
    assert utilization_penalty(metrics, target=0.8) == 0.0

def test_utilization_penalty_below_target() -> None:
    metrics = LossMetrics(utilization=0.7, drift=0.05)
    assert utilization_penalty(metrics, target=0.8) == pytest.approx(0.1)

def test_utilization_penalty_custom_target() -> None:
    metrics = LossMetrics(utilization=0.5, drift=0.05)
    assert utilization_penalty(metrics, target=0.6) == pytest.approx(0.1)

def test_summarize_losses() -> None:
    metrics = LossMetrics(utilization=0.7, drift=0.15)
    summary = summarize_losses(metrics)
    assert "utilization_penalty" in summary
    assert "drift_guard" in summary
    assert summary["utilization_penalty"] == pytest.approx(0.1)
    assert summary["drift_guard"] == pytest.approx(0.05)
