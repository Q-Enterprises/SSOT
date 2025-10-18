"""Shard registry primitives for capsule overlay enforcement.

This module introduces a light-weight `Shard` object that tracks overlay
attestations, emotional payload maps, and lifecycle rituals. The
`ShardRegistry` coordinates multiple shards and ensures that incoming overlay
signatures align with their sovereign braid bindings before lifecycle events
are triggered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Iterable, Iterator, Mapping, MutableMapping, Optional

Hook = Callable[["Shard"], None]


class ShardLifecycleEvent(str, Enum):
    """Lifecycle rituals that a shard can surface to contributors."""

    EMIT = "on_emit"
    FREEZE = "on_freeze"
    RESTORE = "on_restore"

    @classmethod
    def from_value(cls, value: "ShardLifecycleEvent | str") -> "ShardLifecycleEvent":
        """Normalize a string value to a lifecycle enum."""

        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError as exc:  # pragma: no cover - defensive branch
            valid = ", ".join(event.value for event in cls)
            raise ValueError(f"Unknown lifecycle event '{value}'. Expected one of: {valid}.") from exc


@dataclass
class Shard:
    """Represents a sovereign shard bound to a contributor braid node."""

    shard_id: str
    overlay_signature: str
    emotional_payload_map: Mapping[str, str]
    _hooks: MutableMapping[ShardLifecycleEvent, Hook] = field(default_factory=dict, init=False, repr=False)

    def register_hook(self, event: ShardLifecycleEvent | str, callback: Hook) -> None:
        """Register a ritual callback for a shard lifecycle event."""

        lifecycle_event = ShardLifecycleEvent.from_value(event)
        if not callable(callback):
            raise TypeError("Lifecycle hook callback must be callable.")
        self._hooks[lifecycle_event] = callback

    def emit(self) -> None:
        """Trigger the shard's emit ritual."""

        self._trigger(ShardLifecycleEvent.EMIT)

    def freeze(self) -> None:
        """Trigger the shard's freeze ritual."""

        self._trigger(ShardLifecycleEvent.FREEZE)

    def restore(self) -> None:
        """Trigger the shard's restore ritual."""

        self._trigger(ShardLifecycleEvent.RESTORE)

    def validate_overlay(self, incoming_signature: str) -> bool:
        """Check whether an incoming overlay attestation matches the shard."""

        return incoming_signature == self.overlay_signature

    def _trigger(self, event: ShardLifecycleEvent) -> None:
        """Invoke a lifecycle hook if registered."""

        hook = self._hooks.get(event)
        if hook:
            hook(self)


class ShardRegistry:
    """Manages shards and enforces overlay attestation before rituals fire."""

    def __init__(self) -> None:
        self._shards: Dict[str, Shard] = {}

    def register(self, shard: Shard, *, allow_overwrite: bool = False) -> None:
        """Register a shard with the registry."""

        if shard.shard_id in self._shards and not allow_overwrite:
            raise ValueError(f"Shard '{shard.shard_id}' already registered.")
        self._shards[shard.shard_id] = shard

    def deregister(self, shard_id: str) -> None:
        """Remove a shard from the registry if present."""

        self._shards.pop(shard_id, None)

    def get(self, shard_id: str) -> Optional[Shard]:
        """Fetch a shard by id without raising if missing."""

        return self._shards.get(shard_id)

    def require(self, shard_id: str) -> Shard:
        """Fetch a shard and raise if it has not been registered."""

        shard = self.get(shard_id)
        if shard is None:
            raise KeyError(f"Shard '{shard_id}' is not registered.")
        return shard

    def ensure_overlay(self, shard_id: str, overlay_signature: str) -> Shard:
        """Validate overlay attestation before returning the shard."""

        shard = self.require(shard_id)
        if not shard.validate_overlay(overlay_signature):
            raise PermissionError(
                f"Overlay attestation mismatch for shard '{shard_id}'."
            )
        return shard

    def trigger(self, shard_id: str, event: ShardLifecycleEvent | str, *, overlay_signature: Optional[str] = None) -> None:
        """Trigger a lifecycle ritual on a registered shard."""

        lifecycle_event = ShardLifecycleEvent.from_value(event)
        shard = self.require(shard_id)
        if overlay_signature is not None and not shard.validate_overlay(overlay_signature):
            raise PermissionError(
                f"Overlay attestation mismatch for shard '{shard_id}' during {lifecycle_event.value}."
            )
        shard._trigger(lifecycle_event)

    def __contains__(self, shard_id: object) -> bool:
        return isinstance(shard_id, str) and shard_id in self._shards

    def __iter__(self) -> Iterator[Shard]:
        return iter(self._shards.values())

    def items(self) -> Iterable[tuple[str, Shard]]:
        """Iterate through registered shards as (id, shard) pairs."""

        return self._shards.items()

    def clear(self) -> None:
        """Remove all shards from the registry."""

        self._shards.clear()

