"""Expert validating CiCi's persona overlay integrity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class OverlayExpertConfig:
    """Controls overlay validation thresholds."""

    persona_layer: str = "CiCi.v2"
    integrity_threshold: float = 0.87


class OverlayExpert:
    """Checks persona overlays against integrity constraints."""

    def __init__(self, config: OverlayExpertConfig | None = None) -> None:
        self.config = config or OverlayExpertConfig()

    def validate(self, overlay_metrics: Dict[str, float]) -> bool:
        """Return True if the overlay integrity meets the configured threshold."""

        integrity = overlay_metrics.get("integrity", 0.0)
        persona = overlay_metrics.get("persona_layer")
        return (
            integrity >= self.config.integrity_threshold
            and persona == self.config.persona_layer
        )
