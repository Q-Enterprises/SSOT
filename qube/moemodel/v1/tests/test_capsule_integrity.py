"""Tests for verifying capsule integrity during dual-root replay."""

from __future__ import annotations

from qube.moemodel.v1.src.lifecycle.capsule_manager import CapsuleHook, CapsuleManager


def test_capsule_freeze_emits_hook() -> None:
    events: list[str] = []
    manager = CapsuleManager()
    manager.register_hook(CapsuleHook(name="freeze", callback=lambda: events.append("freeze")))

    manager.freeze()

    assert events == ["freeze"]
