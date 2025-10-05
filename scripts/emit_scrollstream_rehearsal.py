"""Emit a deterministic rehearsal ledger for capsule.rehearsal.scrollstream.v1.

This script simulates the Celine → Luma → Dot audit loop described in the
scrollstream rehearsal capsule. It writes an append-only ledger payload that
captures the audit summary, proof, and execution stages along with HUD shimmer
and replay glyph metadata. The output is deterministic so the artifact can be
used in CI smoke tests and documentation samples.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

CAPSULE_ID = "capsule.rehearsal.scrollstream.v1"
TRAINING_SEED = f"{CAPSULE_ID}::training-seed::v1"

CYCLE: List[Dict[str, str]] = [
    {
        "stage": "audit.summary",
        "agent": "celine_architect",
        "persona": "Celine/Architect",
        "focus": "Architectural braid synopsis",
        "emotional_payload": "anticipation",
        "hud_channel": "glyph.pulse",
    },
    {
        "stage": "audit.proof",
        "agent": "luma_sentinel",
        "persona": "Luma/Sentinel",
        "focus": "Proof bundle verification",
        "emotional_payload": "resolve",
        "hud_channel": "aura.gold",
    },
    {
        "stage": "audit.execution",
        "agent": "dot_guardian",
        "persona": "Dot/Guardian",
        "focus": "Execution checkpoint replay",
        "emotional_payload": "assurance",
        "hud_channel": "qlock.tick",
    },
]


def _isoformat(ts: datetime) -> str:
    """Return an ISO-8601 timestamp with trailing 'Z'."""

    return ts.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="milliseconds") + "Z"


def _stage_digest(stage: Dict[str, str], sequence: int) -> str:
    """Generate a deterministic digest for a stage emission."""

    payload = "::".join(
        [
            CAPSULE_ID,
            stage["stage"],
            stage["agent"],
            stage["focus"],
            str(sequence),
            TRAINING_SEED,
        ]
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_ledger(start: Optional[datetime] = None, cadence_seconds: int = 42) -> Dict[str, object]:
    """Build the deterministic rehearsal ledger payload."""

    if start is None:
        start = datetime(2025, 9, 27, 12, 0, 0, tzinfo=timezone.utc)

    entries: List[Dict[str, object]] = []
    for idx, stage in enumerate(CYCLE, start=1):
        timestamp = start + timedelta(seconds=cadence_seconds * (idx - 1))
        digest = _stage_digest(stage, idx)
        entries.append(
            {
                "sequence": idx,
                "timestamp": _isoformat(timestamp),
                "stage": stage["stage"],
                "agent": stage["agent"],
                "persona": stage["persona"],
                "capsule_id": CAPSULE_ID,
                "hud_shimmer": {
                    "channel": stage["hud_channel"],
                    "intensity": round(0.72 + 0.08 * idx, 2),
                    "duration_ms": 1800,
                },
                "output": {
                    "focus": stage["focus"],
                    "emotional_payload": stage["emotional_payload"],
                    "sparkline": digest[:16],
                    "body_digest": f"sha256:{digest}",
                },
            }
        )

    payload: Dict[str, object] = {
        "capsule_id": CAPSULE_ID,
        "braid_id": "scrollstream.demo.001",
        "training_seed": TRAINING_SEED,
        "cycle": [item["stage"] for item in CYCLE],
        "ledger": entries,
        "replay_glyph": {
            "icon": "braid.pulse",
            "pulse_rate_hz": 1.5,
            "spark_test": {
                "name": "Sabrina Spark Test",
                "status": "pass",
                "applied_at": _isoformat(start + timedelta(seconds=cadence_seconds * len(CYCLE))),
            },
        },
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o", type=Path, help="Path to write the ledger JSON payload")
    args = parser.parse_args()

    payload = build_ledger()
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
