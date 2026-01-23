import hashlib
import json
from typing import Any, Dict

import yaml


def canonicalize_jcs(data: Dict[str, Any]) -> str:
    """Implements JSON Canonicalization Scheme (RFC 8785) for YAML objects."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def verify_fossil(path_to_yaml: str) -> bool:
    """Verifies the integrity of a fossil artifact against its digest."""
    with open(path_to_yaml, "r", encoding="utf-8") as handle:
        artifact = yaml.safe_load(handle)

    provided_digest = artifact.pop("digest")
    computed_digest = hashlib.sha256(canonicalize_jcs(artifact).encode()).hexdigest()

    return provided_digest == computed_digest


# Kernel usage:
# if verify_fossil("validation/fossils/AgentProposalReceipt.v1.yaml"):
#     engage_replay_court()
