"""Capsule shard registry module exposing shard primitives."""

from .registry import Shard, ShardRegistry, ShardLifecycleEvent

__all__ = ["Shard", "ShardRegistry", "ShardLifecycleEvent"]
