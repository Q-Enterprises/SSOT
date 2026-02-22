from pathlib import Path
import sys
import pytest

# Ensure imports work
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from previz.ledger import CameraState, MotionFrame, MotionLedger, SubjectPose

def make_pose() -> SubjectPose:
    return SubjectPose(x=0.0, y=0.0, yaw=0.0)

def make_camera() -> CameraState:
    return CameraState(pan=0.0, tilt=0.0, zoom=1.0)

def make_frame(frame_index: int) -> MotionFrame:
    return MotionFrame(
        frame=frame_index,
        cars={"car": make_pose()},
        camera=make_camera(),
    )

def test_duration_seconds_accounts_for_non_zero_start():
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

    assert ledger.duration_seconds() == pytest.approx((25 - 10) / 10)

def test_duration_seconds_empty_ledger_returns_zero():
    ledger = MotionLedger(
        capsule_id="capsule",
        scene="scene",
        fps=30,
        frames=[],
        style_capsules=[],
    )

    assert ledger.duration_seconds() == 0.0
