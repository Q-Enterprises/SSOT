"""Posture expert tuned to maintain gesture fidelity during CiCi's replays."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PostureExpertConfig:
    """Configuration controlling the expert's target gestures."""

    default_posture: str = "open"
    micro_adjustment_rate: float = 0.1


class PostureExpert:
    """Simple feed-forward expert that modulates posture vectors."""

    def __init__(self, config: PostureExpertConfig | None = None) -> None:
        self.config = config or PostureExpertConfig()

    def forward(self, posture_state: Dict[str, Any]) -> Dict[str, Any]:
        """Return an adjusted posture state preserving gesture fidelity."""

        adjusted = dict(posture_state)
        adjusted.setdefault("gesture_intent", self.config.default_posture)
        adjusted["micro_adjustment"] = self.config.micro_adjustment_rate
        return adjusted
