"""Expert responsible for generating refusal scripts when Spark checks fail."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class RefusalExpertConfig:
    """Parameters defining how refusal messaging is constructed."""

    tone: str = "warm"
    escalation_channel: str = "spark://ci-ci/refusal"


class RefusalExpert:
    """Produces refusal payloads and hooks for audit logging."""

    def __init__(self, config: RefusalExpertConfig | None = None) -> None:
        self.config = config or RefusalExpertConfig()

    def craft_refusal(self, reason: str, *, include_channel: bool = True) -> Dict[str, str]:
        """Return a refusal response with tone and optional escalation channel."""

        payload = {
            "tone": self.config.tone,
            "reason": reason,
        }
        if include_channel:
            payload["escalation_channel"] = self.config.escalation_channel
        return payload
