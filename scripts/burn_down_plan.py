"""Utility for generating the burn-down plan for the remaining GitHub work.

The script prints the workstream table and daily target table in Markdown by
default, but it can also emit JSON suitable for dashboards. Dates are computed
from a user-provided start date so the plan can be aligned with any kickoff.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, List, Sequence

TOTAL_POINTS = 28


@dataclass(frozen=True)
class Workstream:
    """Represents one workstream within the burn-down plan."""

    name: str
    subtasks: str
    estimate_points: int
    dependencies: str
    owner: str


@dataclass(frozen=True)
class DailyTarget:
    """Daily burn-down target with date and focus summary."""

    day_offset: int
    target_remaining_points: int
    focus: str

    def dated(self, kickoff: date) -> "DatedDailyTarget":
        """Return a :class:`DatedDailyTarget` using the provided kickoff date."""

        return DatedDailyTarget(
            day=self.day_offset,
            calendar_date=kickoff + timedelta(days=self.day_offset),
            target_remaining_points=self.target_remaining_points,
            focus=self.focus,
        )


@dataclass(frozen=True)
class DatedDailyTarget:
    """Daily target with concrete calendar date."""

    day: int
    calendar_date: date
    target_remaining_points: int
    focus: str

    def to_serializable(self) -> dict:
        """Return a JSON-serializable representation."""

        payload = asdict(self)
        payload["calendar_date"] = self.calendar_date.isoformat()
        return payload


WORKSTREAMS: Sequence[Workstream] = (
    Workstream(
        name="Final CI/CD Pipeline Hooks",
        subtasks="Post-merge SOL replay trigger; Fail-closed governance gate",
        estimate_points=5,
        dependencies="Governance scripts updated",
        owner="DevOps",
    ),
    Workstream(
        name="HUD Front-End Polish",
        subtasks="Responsive layout; Queen Boo descent glyph overlays",
        estimate_points=8,
        dependencies="HUD API contract live",
        owner="Front-End",
    ),
    Workstream(
        name="Telemetry Contract Enforcement",
        subtasks="KPI unit tests; Breach alert triggers",
        estimate_points=5,
        dependencies="KPI bindings complete",
        owner="Backend",
    ),
    Workstream(
        name="Capsule Emission CLI",
        subtasks="Emit/freeze/push flow; Digest verification",
        estimate_points=7,
        dependencies="CouncilLedger sandbox access",
        owner="Tools",
    ),
    Workstream(
        name="Documentation",
        subtasks="README refresh; Agent Boo onboarding guide",
        estimate_points=3,
        dependencies="Features finalized",
        owner="Docs",
    ),
)

DAILY_TARGETS: Sequence[DailyTarget] = (
    DailyTarget(day_offset=0, target_remaining_points=28, focus="Baseline scope & owners"),
    DailyTarget(day_offset=1, target_remaining_points=22, focus="CI/CD hooks; HUD layout"),
    DailyTarget(day_offset=2, target_remaining_points=17, focus="Responsive HUD; telemetry tests"),
    DailyTarget(day_offset=3, target_remaining_points=11, focus="Telemetry alerts; Capsule CLI core"),
    DailyTarget(day_offset=4, target_remaining_points=6, focus="Capsule CLI finalize; docs kickoff"),
    DailyTarget(day_offset=5, target_remaining_points=0, focus="Docs wrap; regression pass"),
)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        default=date.today(),
        help=(
            "Kickoff date in YYYY-MM-DD format. Defaults to today so the plan "
            "can be generated quickly for ad-hoc updates."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Select output format. Markdown prints human-readable tables.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the generated plan. Format follows --format.",
    )
    return parser.parse_args(argv)


def build_dated_targets(kickoff: date) -> List[DatedDailyTarget]:
    return [target.dated(kickoff) for target in DAILY_TARGETS]


def render_markdown(kickoff: date) -> str:
    workstream_rows = "\n".join(
        f"| {ws.name} | {ws.subtasks} | {ws.estimate_points} | {ws.dependencies} | {ws.owner} |"
        for ws in WORKSTREAMS
    )
    workstream_table = (
        "## Workstreams\n"
        "| Workstream | Subtasks | Estimate (pts) | Dependencies | Owner |\n"
        "|---|---|---:|---|---|\n"
        f"{workstream_rows}\n\n"
        f"**Total planned points:** {TOTAL_POINTS}\n"
    )

    dated_targets = build_dated_targets(kickoff)
    target_rows = "\n".join(
        f"| Day {target.day} | {target.calendar_date.isoformat()} | {target.target_remaining_points} | {target.focus} |"
        for target in dated_targets
    )
    target_table = (
        "## Daily Burn-Down Targets\n"
        "| Day | Date | Target Remaining Points | Focus |\n"
        "|---|---|---:|---|\n"
        f"{target_rows}"
    )
    return f"{workstream_table}\n{target_table}\n"


def render_json(kickoff: date) -> str:
    payload = {
        "total_points": TOTAL_POINTS,
        "workstreams": [asdict(ws) for ws in WORKSTREAMS],
        "daily_targets": [target.to_serializable() for target in build_dated_targets(kickoff)],
    }
    return json.dumps(payload, indent=2)


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    kickoff = args.start_date

    if args.format == "markdown":
        output = render_markdown(kickoff)
    else:
        output = render_json(kickoff)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
