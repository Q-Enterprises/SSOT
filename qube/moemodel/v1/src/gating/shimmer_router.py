"""Shimmer-aware token router for the Spark Test gating process."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass
class RouteDecision:
    """Represents a routing outcome for a token batch."""

    expert_index: int
    confidence: float


class ShimmerRouter:
    """Dispatches tokens to experts based on Spark resonance scores."""

    def __init__(self, thresholds: Sequence[float]) -> None:
        if not thresholds:
            raise ValueError("At least one threshold is required for routing.")
        self.thresholds: List[float] = list(thresholds)

    def route(self, resonance_scores: Iterable[float]) -> List[RouteDecision]:
        """Map resonance scores to expert indices using the configured thresholds."""

        decisions: List[RouteDecision] = []
        for score in resonance_scores:
            expert = self._select_expert(score)
            decisions.append(RouteDecision(expert_index=expert, confidence=score))
        return decisions

    def _select_expert(self, score: float) -> int:
        for index, threshold in enumerate(self.thresholds):
            if score <= threshold:
                return index
        return len(self.thresholds)
