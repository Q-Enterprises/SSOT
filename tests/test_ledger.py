from __future__ import annotations
from pathlib import Path
import sys
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from previz.ledger import CameraState, MotionFrame, MotionLedger, SubjectPose

def make_frame(frame_index: int) -> MotionFrame:
    return MotionFrame(
        frame=frame_index,
        cars={"car": make_pose()},
        camera=make_camera(),
    )

def test_duration_seconds_handles_non_zero_start_frame():
    ledger = MotionLedger(
        capsule_id="capsule",
        scene="scene",
        fps=10,
        frames=[
            make_frame(10),
            make_frame(25),
        ],
        style_capsules=[],
    )

    # Expected: (40 - 10) / 30 = 1.0 second
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
