"""Loss hooks for expert utilization and drift prevention."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class LossMetrics:
    """Tracks training metrics for MoE experts."""

    utilization: float
    drift: float


def utilization_penalty(metrics: LossMetrics, target: float = 0.8) -> float:
    """Encourage balanced expert utilization."""

    return max(0.0, target - metrics.utilization)


def drift_guard(metrics: LossMetrics, limit: float = 0.1) -> float:
    """Penalize overlay drift beyond the allowed limit."""

    return max(0.0, metrics.drift - limit)


def summarize_losses(metrics: LossMetrics) -> Dict[str, float]:
    """Summarize loss contributions for logging."""

    return {
        "utilization_penalty": utilization_penalty(metrics),
        "drift_guard": drift_guard(metrics),
    }
