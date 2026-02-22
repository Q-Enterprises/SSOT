from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, get_args, get_origin, get_type_hints

import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _install_pydantic_stub() -> None:
    """Mock Pydantic for environments where it is not installed."""
    if "pydantic" in sys.modules:
        return

    module = types.ModuleType("pydantic")

    class _DefaultFactory:
        def __init__(self, factory: Callable[[], Any]):
            self.factory = factory

    class BaseModel:
        __validators__: Dict[str, List[Callable[[type, Any], Any]]] = {}

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            validators: Dict[str, List[Callable[[type, Any], Any]]] = {}
            for attr in cls.__dict__.values():
                config: Tuple[Tuple[str, ...], Dict[str, Any]] | None = getattr(
                    attr, "_validator_config", None
                )
                if not config:
                    continue
                fields, _ = config
                for field in fields:
                    validators.setdefault(field, []).append(attr)
            cls.__validators__ = validators

        def __init__(self, **data: Any) -> None:
            annotations: Dict[str, Any] = get_type_hints(self.__class__)
            values: Dict[str, Any] = {}
            for name, annotation in annotations.items():
                if name in data:
                    value = self._convert_value(annotation, data[name])
                else:
                    default = getattr(self.__class__, name, None)
                    if isinstance(default, _DefaultFactory):
                        value = default.factory()
                    else:
                        value = default
                values[name] = value

            for field, validators in getattr(self.__class__, "__validators__", {}).items():
                if field in values:
                    value = values[field]
                    for validator_fn in validators:
                        value = validator_fn(self.__class__, value)
                    values[field] = value

            for key, value in values.items():
                setattr(self, key, value)

        @classmethod
        def _convert_value(cls, annotation: Any, value: Any) -> Any:
            origin = get_origin(annotation)
            if origin is None:
                if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                    if isinstance(value, annotation):
                        return value
                    if isinstance(value, dict):
                        return annotation(**value)
                return value

            args = get_args(annotation)
            if origin in (list, List):
                (item_type,) = args
                return [cls._convert_value(item_type, item) for item in value]
            if origin in (dict, Dict):
                key_type, val_type = args
                return {
                    cls._convert_value(key_type, key): cls._convert_value(val_type, item)
                    for key, item in value.items()
                }
            return value

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "BaseModel":
            return cls(**obj)

    def Field(*, default_factory: Callable[[], Any] | None = None, **_: Any) -> Any:
        if default_factory is None:
            return None
        return _DefaultFactory(default_factory)

    def validator(*fields: str, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            func._validator_config = (fields, {})  # type: ignore[attr-defined]
            return func

        return decorator

    module.BaseModel = BaseModel
    module.Field = Field
    module.validator = validator
    sys.modules["pydantic"] = module


_install_pydantic_stub()

from previz.ledger import CameraState, MotionFrame, MotionLedger, SubjectPose


def make_pose() -> SubjectPose:
    return SubjectPose(x=0.0, y=0.0, yaw=0.0)


def make_camera() -> CameraState:
    return CameraState(pan=0.0, tilt=0.0, zoom=1.0)


def test_duration_seconds_handles_non_zero_start_frame():
    ledger = MotionLedger(
        capsule_id="capsule",
        scene="scene",
        fps=30,
        frames=[
            MotionFrame(frame=10, cars={"alpha": make_pose()}, camera=make_camera()),
            MotionFrame(frame=40, cars={"alpha": make_pose()}, camera=make_camera()),
        ],
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


def test_duration_seconds_accounts_for_non_zero_start():
    ledger = MotionLedger(
        capsule_id="capsule",
        scene="scene",
        fps=10,
        frames=[
            MotionFrame(frame=10, cars={"car": make_pose()}, camera=make_camera()),
            MotionFrame(frame=25, cars={"car": make_pose()}, camera=make_camera()),
        ],
        style_capsules=[],
    )

    assert ledger.duration_seconds() == pytest.approx((25 - 10) / 10)
