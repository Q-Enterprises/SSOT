"""Screenplay capsule loader for sovereign cinematic relays."""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class RelayLink(BaseModel):
    """Reference to a capsule or policy activated during a beat."""

    stage: str
    capsule: str
    description: Optional[str] = None


class SceneBeat(BaseModel):
    """One narrative beat that coordinates a relay stage."""

    beat_id: str
    title: str
    description: str
    relay_stage: str
    ssot_refs: List[str] = Field(default_factory=list)
    orchestrator_refs: List[str] = Field(default_factory=list)
    previz_refs: List[str] = Field(default_factory=list)
    clip_refs: List[str] = Field(default_factory=list)


class Scene(BaseModel):
    """A screenplay scene containing beats."""

    scene_id: str
    title: str
    runtime_seconds: int
    summary: str
    environment: str
    beats: List[SceneBeat] = Field(default_factory=list)

    @validator("beats")
    def ensure_beats_sorted(cls, value: List[SceneBeat]) -> List[SceneBeat]:
        return sorted(value, key=lambda beat: beat.beat_id)

    def relay_stage_sequence(self) -> List[str]:
        order: List[str] = []
        for beat in self.beats:
            stage = beat.relay_stage
            if stage not in order:
                order.append(stage)
        return order

    def execution_branch(self) -> Dict[str, object]:
        return {
            "scene_id": self.scene_id,
            "title": self.title,
            "runtime_seconds": self.runtime_seconds,
            "environment": self.environment,
            "relay_stages": self.relay_stage_sequence(),
            "beats": [
                {
                    "beat_id": beat.beat_id,
                    "title": beat.title,
                    "relay_stage": beat.relay_stage,
                    "description": beat.description,
                    "ssot_refs": beat.ssot_refs,
                    "orchestrator_refs": beat.orchestrator_refs,
                    "previz_refs": beat.previz_refs,
                    "clip_refs": beat.clip_refs,
                }
                for beat in self.beats
            ],
        }


class ScreenplayAct(BaseModel):
    """One act in the screenplay."""

    act_id: str
    title: str
    purpose: str
    scenes: List[Scene] = Field(default_factory=list)

    @validator("scenes")
    def ensure_scenes_sorted(cls, value: List[Scene]) -> List[Scene]:
        return sorted(value, key=lambda scene: scene.scene_id)

    def execution_branch(self) -> Dict[str, object]:
        return {
            "act_id": self.act_id,
            "title": self.title,
            "purpose": self.purpose,
            "scenes": [scene.execution_branch() for scene in self.scenes],
        }


class ClipPlan(BaseModel):
    """High-level clip production plan metadata."""

    target_clips: int
    duration_seconds: int
    cadence_fps: int
    style_capsules: List[str] = Field(default_factory=list)


class RelayAlignment(BaseModel):
    """Describes how the screenplay links to other capsules."""

    ssot_capsule: str
    orchestrator_capsule: str
    previz_library: List[str] = Field(default_factory=list)
    clip_plan: ClipPlan


class ScreenplayCapsule(BaseModel):
    """Full screenplay capsule payload."""

    capsule_id: str
    title: str
    logline: str
    duration_minutes: int
    themes: List[str] = Field(default_factory=list)
    acts: List[ScreenplayAct] = Field(default_factory=list)
    relay_alignment: RelayAlignment
    council_directive: str

    @validator("acts")
    def ensure_acts_sorted(cls, value: List[ScreenplayAct]) -> List[ScreenplayAct]:
        return sorted(value, key=lambda act: act.act_id)

    def summary(self) -> Dict[str, object]:
        total_runtime = sum(scene.runtime_seconds for act in self.acts for scene in act.scenes)
        return {
            "capsule_id": self.capsule_id,
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "scenes": sum(len(act.scenes) for act in self.acts),
            "runtime_seconds": total_runtime,
            "themes": self.themes,
        }

    def execution_tree(self) -> List[Dict[str, object]]:
        return [act.execution_branch() for act in self.acts]


@dataclass
class ActSummary:
    """Lightweight descriptor for listing screenplay capsules."""

    capsule_id: str
    path: Path
    metadata: Dict[str, object]


class ScreenplayLibrary:
    """Discovers screenplay capsules stored on disk."""

    def __init__(self, root: Path):
        self._root = root
        self._cache: Dict[str, ScreenplayCapsule] = {}
        self._index: Dict[str, Path] = {}
        self._load_index()

    def _load_index(self) -> None:
        for path in sorted(self._root.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            capsule = ScreenplayCapsule.parse_obj(payload)
            self._cache[capsule.capsule_id] = capsule
            self._index[capsule.capsule_id] = path

    def list_capsules(self) -> List[ActSummary]:
        summaries: List[ActSummary] = []
        for capsule_id, path in self._index.items():
            capsule = self._cache[capsule_id]
            summaries.append(ActSummary(capsule_id=capsule_id, path=path, metadata=capsule.summary()))
        return summaries

    def get_capsule(self, capsule_id: str) -> ScreenplayCapsule:
        if capsule_id not in self._cache:
            raise KeyError(f"screenplay capsule '{capsule_id}' not found")
        return self._cache[capsule_id]


@lru_cache()
def load_library() -> ScreenplayLibrary:
    root = Path(__file__).resolve().parents[1] / "data" / "scripts"
    return ScreenplayLibrary(root)


LIBRARY = load_library()

__all__ = [
    "RelayLink",
    "SceneBeat",
    "Scene",
    "ScreenplayAct",
    "ClipPlan",
    "RelayAlignment",
    "ScreenplayCapsule",
    "ActSummary",
    "ScreenplayLibrary",
    "LIBRARY",
    "load_library",
]
