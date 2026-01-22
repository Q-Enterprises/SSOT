"""Replay-Court reconstruction helpers."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

import yaml


def canonicalize_jcs(data: Dict[str, Any]) -> str:
    """Implement JSON Canonicalization Scheme (RFC 8785) for YAML objects."""

    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def verify_fossil(path_to_yaml: str) -> bool:
    """Verify the integrity of a fossil artifact against its digest."""

    with open(path_to_yaml, "r", encoding="utf-8") as file_handle:
        artifact = yaml.safe_load(file_handle)

    provided_digest = artifact.pop("digest")
    computed_digest = hashlib.sha256(canonicalize_jcs(artifact).encode("utf-8")).hexdigest()

    return provided_digest == computed_digest
