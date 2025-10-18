"""Data model for the anomaly trace capsule protocol."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from importlib import resources
from typing import Any, Dict


@dataclass(frozen=True)
class Trigger:
    """Capture the conditions that spark the anomaly trace."""

    source: str
    condition: str
    sector: str
    severity: str


@dataclass(frozen=True)
class FallbackArc:
    """Describe the fallback arc that stabilizes the rupture."""

    color: str
    structure: str
    stabilization: str
    rhythm: str


@dataclass(frozen=True)
class RecoveryGlyph:
    """Information about the glyph embedded during recovery."""

    status: str
    location: str
    annotation: str
    alertFlag: bool


@dataclass(frozen=True)
class Response:
    """The full response ritual triggered after detection."""

    fallbackArc: FallbackArc
    recoveryGlyph: RecoveryGlyph


@dataclass(frozen=True)
class EmissionArc:
    """Visual grammar describing the emission arc."""

    tone: str
    gesture: str
    shimmer: str
    trail: str


@dataclass(frozen=True)
class TransitNode:
    """Visual grammar describing the transit node behavior."""

    collision: str
    reaction: str
    reroute: str


@dataclass(frozen=True)
class VisualGrammar:
    """Visual grammar for rendering the anomaly trace."""

    emissionArc: EmissionArc
    transitNode: TransitNode


@dataclass(frozen=True)
class Attestation:
    """Attestation guarantees for the anomaly trace capsule."""

    emotionallyLayered: bool
    sceneAware: bool
    replayReady: bool
    contributorTrainable: bool


@dataclass(frozen=True)
class AnomalyTraceProtocol:
    """Full anomaly trace capsule definition."""

    capsuleId: str
    title: str
    description: str
    trigger: Trigger
    response: Response
    visualGrammar: VisualGrammar
    attestation: Attestation
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """Render the protocol as a serializable dictionary."""

        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        """Render the protocol as a JSON string."""

        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


DEFAULT_PROTOCOL = AnomalyTraceProtocol(
    capsuleId="capsule.anomaly.trace.v1",
    title="Anomaly Trace Protocol",
    description=(
        "Encodes rupture-grade emissions into scrollstream-valid artifacts for replay, "
        "contributor training, and forensic lineage mapping."
    ),
    trigger=Trigger(
        source="HUD emission",
        condition="glyph integrity breach",
        sector="braid sector 3",
        severity="high",
    ),
    response=Response(
        fallbackArc=FallbackArc(
            color="amber",
            structure="braided",
            stabilization="glitch-corrected",
            rhythm="triple-beat",
        ),
        recoveryGlyph=RecoveryGlyph(
            status="embedded",
            location="scrollstream rail",
            annotation="rupture trace",
            alertFlag=True,
        ),
    ),
    visualGrammar=VisualGrammar(
        emissionArc=EmissionArc(
            tone="Shout",
            gesture="Signal_Broadcast",
            shimmer="high-frequency crackle",
            trail="glyph fragments",
        ),
        transitNode=TransitNode(
            collision="glyph firewall",
            reaction="tri-glyph bloom",
            reroute="anomaly trace channel",
        ),
    ),
    attestation=Attestation(
        emotionallyLayered=True,
        sceneAware=True,
        replayReady=True,
        contributorTrainable=True,
    ),
    status="fossilized",
)


def default_protocol() -> AnomalyTraceProtocol:
    """Return the default anomaly trace protocol definition."""

    return DEFAULT_PROTOCOL


def default_protocol_dict() -> Dict[str, Any]:
    """Return the protocol definition as a dictionary."""

    return DEFAULT_PROTOCOL.to_dict()


def default_protocol_json(*, indent: int = 2) -> str:
    """Return the protocol definition serialized as JSON."""

    return DEFAULT_PROTOCOL.to_json(indent=indent)


def load_protocol_resource() -> Dict[str, Any]:
    """Load the fossilized protocol JSON resource bundled with the capsule."""

    with resources.files(__package__).joinpath("protocol.json").open("r", encoding="utf-8") as fp:
        return json.load(fp)
