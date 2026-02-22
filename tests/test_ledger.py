from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from previz.ledger import CameraState, MotionFrame, MotionLedger, SubjectPose


def make_frame(frame_index: int) -> MotionFrame:
    return MotionFrame(
        frame=frame_index,
        cars={
            "alpha": SubjectPose(x=1.0, y=2.0, yaw=3.0),
        },
        camera=CameraState(pan=0.0, tilt=0.0, zoom=1.0),
    )


def test_duration_seconds_handles_non_zero_start_frame():
    ledger = MotionLedger(
        capsule_id="capsule",
        scene="scene",
        fps=30,
        frames=[make_frame(10), make_frame(40)],
        style_capsules=[],
    )

    assert ledger.duration_seconds() == pytest.approx((40 - 10) / 30)


def test_duration_seconds_empty_ledger_returns_zero():
    ledger = MotionLedger(
        capsule_id="capsule",
        scene="scene",
        fps=30,
        frames=[],
        style_capsules=[],
    )

    assert ledger.duration_seconds() == 0.0
