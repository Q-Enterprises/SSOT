"""HUD renderer providing shimmer timestamp overlays."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Dict


@dataclass
class RenderPayload:
    """Structure describing shimmer render components."""

    timestamp: datetime
    emotional_hue: str
    fidelity_score: float


class ShimmerRenderer:
    """Produces HUD overlays capturing shimmer state for replays."""

    def render(self, hue: str, fidelity: float) -> RenderPayload:
        """Create a render payload with current timestamp and emotional hue."""

        now = datetime.now(UTC)
        return RenderPayload(timestamp=now, emotional_hue=hue, fidelity_score=fidelity)

    def to_dict(self, payload: RenderPayload) -> Dict[str, str]:
        """Convert the payload to a serializable dictionary."""

        timestamp = payload.timestamp.isoformat().replace("+00:00", "Z")
        return {
            "timestamp": timestamp,
            "emotional_hue": payload.emotional_hue,
            "fidelity_score": f"{payload.fidelity_score:.3f}",
        }
