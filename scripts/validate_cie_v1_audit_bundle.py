#!/usr/bin/env python3
"""Validate CIE-V1 audit bundles with neutral-only corridor invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple


@dataclass(frozen=True)
class ValidationError:
    message: str
    line_number: Optional[int] = None


def load_json_lines(path: Path) -> Iterable[Tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number} invalid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_number} expected object payload")
            yield line_number, payload


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_field(payload: dict[str, Any], field: str) -> Optional[Any]:
    if field in payload:
        return payload[field]
    metadata = payload.get("metadata")
    if isinstance(metadata, dict) and field in metadata:
        return metadata[field]
    return None


def validate_payload_record(
    payload: dict[str, Any],
    line_number: int,
    receipt_index: set[tuple[str, str]],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    run_id = read_field(payload, "run_id")
    council_attestation_id = read_field(payload, "council_attestation_id")
    sha256_payload = payload.get("sha256_payload")

    if not run_id:
        errors.append(
            ValidationError(
                "missing run_id (expected top-level or metadata.run_id)", line_number
            )
        )
    if not council_attestation_id:
        errors.append(
            ValidationError(
                "missing council_attestation_id (expected top-level or metadata.council_attestation_id)",
                line_number,
            )
        )
    if not sha256_payload:
        errors.append(ValidationError("missing sha256_payload", line_number))

    if errors:
        return errors

    payload_copy = dict(payload)
    payload_copy.pop("sha256_payload", None)
    calculated = sha256_hex(canonical_json(payload_copy))
    if calculated != sha256_payload:
        errors.append(
            ValidationError(
                f"sha256_payload mismatch (expected {sha256_payload}, calculated {calculated})",
                line_number,
            )
        )

    if (run_id, council_attestation_id) not in receipt_index:
        errors.append(
            ValidationError(
                "council attestation not found in receipts for run_id binding",
                line_number,
            )
        )

    return errors


def build_receipt_index(path: Path) -> tuple[set[tuple[str, str]], list[ValidationError]]:
    index: set[tuple[str, str]] = set()
    errors: list[ValidationError] = []
    for line_number, receipt in load_json_lines(path):
        run_id = read_field(receipt, "run_id")
        council_attestation_id = read_field(receipt, "council_attestation_id")
        if not run_id or not council_attestation_id:
            errors.append(
                ValidationError(
                    "receipt missing run_id or council_attestation_id",
                    line_number,
                )
            )
            continue
        index.add((str(run_id), str(council_attestation_id)))
    return index, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate CIE-V1 audit bundle payloads against neutrality receipts."
    )
    parser.add_argument(
        "--payloads",
        required=True,
        type=Path,
        help="Path to payload NDJSON file (cie_v1 audit bundle).",
    )
    parser.add_argument(
        "--receipts",
        required=True,
        type=Path,
        help="Path to neutrality receipts JSONL file.",
    )
    args = parser.parse_args()

    receipt_index, receipt_errors = build_receipt_index(args.receipts)

    all_errors = receipt_errors
    for line_number, payload in load_json_lines(args.payloads):
        all_errors.extend(
            validate_payload_record(payload, line_number, receipt_index)
        )

    if all_errors:
        for error in all_errors:
            if error.line_number is None:
                location = ""
            else:
                location = f"line {error.line_number}: "
            print(f"{location}{error.message}", file=sys.stderr)
        return 1

    print("CIE-V1 audit bundle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
