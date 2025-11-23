"""Capsule lifecycle manager handling freeze, braid bind, and feedback loops."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class CapsuleHook:
    """A lifecycle hook triggered at key capsule stages."""

    name: str
    callback: Callable[[], None]


@dataclass
class CapsuleManager:
    """Coordinates capsule lifecycle events for CiCi's replay stack."""

    hooks: List[CapsuleHook] = field(default_factory=list)
    frozen: bool = False

    def register_hook(self, hook: CapsuleHook) -> None:
        self.hooks.append(hook)

    def freeze(self) -> None:
        self.frozen = True
        self._emit("freeze")

    def braid_bind(self) -> None:
        if not self.frozen:
            raise RuntimeError("Capsule must be frozen before braid binding.")
        self._emit("braid_bind")

    def feedback_loop(self) -> None:
        self._emit("feedback_loop")

    def _emit(self, event: str) -> None:
        for hook in self.hooks:
            if hook.name == event:
                hook.callback()
