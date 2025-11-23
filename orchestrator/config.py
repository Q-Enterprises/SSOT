"""Orchestrator capsule configuration and validation helpers."""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from pydantic import BaseModel, Field


class RouterSpec(BaseModel):
    """Definition for the routing avatar that governs flow order."""

    avatar: str
    checkpoint_ref: str
    policies: List[str] = Field(default_factory=list)


class StabilizerSpec(BaseModel):
    """Payload register for the stabilizer avatar (CiCi)."""

    avatar: str
    payload_register: Dict[str, str] = Field(default_factory=dict)


class OrchestratorCapsule(BaseModel):
    """Pydantic capsule describing the orchestrator runtime."""

    capsule_id: str
    router: RouterSpec
    stabilizer: StabilizerSpec
    flow_order: List[str]

    def validate_sequence(self, sequence: Sequence[str]) -> "FlowCheckResult":
        """Validate a requested sequence against the canonical flow order."""

        normalized = [step.strip() for step in sequence if step]
        missing = [step for step in self.flow_order if step not in normalized]
        extras = [step for step in normalized if step not in self.flow_order]
        aligned = [step for step in normalized if step in self.flow_order]
        in_order = aligned == self.flow_order[: len(aligned)]
        next_expected = None
        if not missing and len(aligned) < len(self.flow_order):
            next_expected = self.flow_order[len(aligned)]
        valid = not missing and not extras and in_order
        return FlowCheckResult(
            valid=valid,
            missing=missing,
            extras=extras,
            in_order=in_order,
            normalized=aligned,
            next_expected=next_expected,
        )


class FlowSubmission(BaseModel):
    """Payload submitted for flow validation."""

    sequence: List[str]


@dataclass
class FlowCheckResult:
    """Result of validating a stage sequence against the capsule."""

    valid: bool
    missing: List[str]
    extras: List[str]
    in_order: bool
    normalized: List[str]
    next_expected: Optional[str]

    def dict(self) -> Dict[str, object]:
        return {
            "valid": self.valid,
            "missing": self.missing,
            "extras": self.extras,
            "in_order": self.in_order,
            "normalized": self.normalized,
            "next_expected": self.next_expected,
        }


def _data_root() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _capsule_path() -> Path:
    return _data_root() / "orchestrator_capsule.json"


@lru_cache()
def load_capsule() -> OrchestratorCapsule:
    path = _capsule_path()
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return OrchestratorCapsule.parse_obj(payload)


CAPSULE = load_capsule()

__all__ = [
    "CAPSULE",
    "FlowCheckResult",
    "FlowSubmission",
    "OrchestratorCapsule",
    "RouterSpec",
    "StabilizerSpec",
    "load_capsule",
]
