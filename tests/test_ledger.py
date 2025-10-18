from __future__ import annotations

from pathlib import Path
import sys
import types
from typing import Any, Callable, Dict, Iterable, List, get_args, get_origin, get_type_hints

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.append(str(_PROJECT_ROOT))
from pathlib import Path
import sys
import types
from typing import Any, Callable, Dict, List, Tuple, get_args, get_origin, get_type_hints

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))


def _install_pydantic_stub() -> None:
    if "pydantic" in sys.modules:
        return

    module = types.ModuleType("pydantic")

    class _DefaultFactory:
        def __init__(self, factory: Callable[[], Any]):
            self.factory = factory

    def Field(*, default_factory: Callable[[], Any] | None = None, **_: Any) -> Any:
        if default_factory is None:
            raise TypeError("default_factory is required in this test stub")
        return _DefaultFactory(default_factory)

    def validator(*fields: str, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            func._validator_fields = fields  # type: ignore[attr-defined]
            return func

        return decorator

    class BaseModel:
        __validators__: Dict[str, Iterable[Callable[[type, Any], Any]]] = {}
        _default_factories: Dict[str, Callable[[], Any]] = {}

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            cls._default_factories = {}
            cls.__validators__ = {}

            for name, value in cls.__dict__.items():
                if isinstance(value, _DefaultFactory):
                    cls._default_factories[name] = value.factory

            for attr in cls.__dict__.values():
                fields = getattr(attr, "_validator_fields", ())
                for field in fields:
                    cls.__validators__.setdefault(field, []).append(attr)

        def __init__(self, **data: Any) -> None:
            annotations = get_type_hints(self.__class__)

            for name, factory in self.__class__._default_factories.items():
                if name not in data:
                    data[name] = factory()

            for name in annotations:
                if name in data:
                    value = self._convert_value(annotations[name], data[name])
                else:
                    value = getattr(self.__class__, name, None)
                setattr(self, name, value)

            for field, validators in self.__class__.__validators__.items():
                value = getattr(self, field)
                for validator_fn in validators:
                    value = validator_fn(self.__class__, value)
                setattr(self, field, value)

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "BaseModel":
            return cls(**obj)
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
            raise ValueError("default_factory is required in this test stub")
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
