"""Lightweight compatibility shim for the parts of Pydantic used in tests.

This module intentionally implements only a very small subset of the real
Pydantic API so that the repository's unit tests can run in environments where
installing external dependencies is not possible.  The goal is to provide the
behaviour relied upon by the project (basic model construction, default
handling, the ``Field`` helper, validators, and ``parse_obj``) without pulling
in the full dependency tree.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, get_args, get_origin, get_type_hints

__all__ = [
    "BaseModel",
    "Field",
    "ValidationError",
    "validator",
]


class ValidationError(ValueError):
    """Exception raised when provided data cannot initialise a model."""


@dataclass
class _FieldInfo:
    default: Any = None
    default_factory: Optional[Callable[[], Any]] = None


def Field(*, default: Any = None, default_factory: Optional[Callable[[], Any]] = None) -> _FieldInfo:
    """Return field metadata used during ``BaseModel`` initialisation."""

    return _FieldInfo(default=default, default_factory=default_factory)


def validator(*field_names: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register a simple validator for one or more fields on a ``BaseModel`` subclass."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "_validator_fields", field_names)
        return func

    return decorator


class _ModelMeta(type):
    def __new__(mcls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> "_ModelMeta":
        validators: Dict[str, List[Callable[..., Any]]] = {}
        field_defaults: Dict[str, _FieldInfo] = {}

        for base in bases:
            validators.update(getattr(base, "__validators__", {}))
            field_defaults.update(getattr(base, "__field_defaults__", {}))

        for attr, value in namespace.items():
            if isinstance(value, _FieldInfo):
                field_defaults[attr] = value
            elif callable(value) and hasattr(value, "_validator_fields"):
                for field in getattr(value, "_validator_fields"):
                    validators.setdefault(field, []).append(value)

        namespace["__validators__"] = validators
        namespace["__field_defaults__"] = field_defaults
        return super().__new__(mcls, name, bases, namespace)


class BaseModel(metaclass=_ModelMeta):
    """A tiny subset of ``pydantic.BaseModel`` for internal use."""

    __validators__: Dict[str, List[Callable[..., Any]]]
    __field_defaults__: Dict[str, _FieldInfo]

    def __init__(self, **data: Any) -> None:
        annotations: Dict[str, Any] = {
            key: value
            for key, value in get_type_hints(self.__class__).items()
            if not key.startswith("_")
        }
        initial_data = dict(data)

        for field, info in self.__field_defaults__.items():
            if field not in initial_data:
                if info.default_factory is not None:
                    initial_data[field] = info.default_factory()
                else:
                    initial_data[field] = info.default

        missing = [field for field in annotations if field not in initial_data]
        if missing:
            raise ValidationError(f"Missing fields for {self.__class__.__name__}: {missing}")

        for field, value in initial_data.items():
            expected = annotations.get(field)
            setattr(self, field, self._coerce_value(expected, value))

        for field, validators in self.__validators__.items():
            if field in annotations:
                value = getattr(self, field, None)
                for fn in validators:
                    value = fn(self.__class__, value)
                setattr(self, field, value)

    def dict(self) -> Dict[str, Any]:
        annotations = {
            key: value
            for key, value in get_type_hints(self.__class__).items()
            if not key.startswith("_")
        }
        return {key: getattr(self, key) for key in annotations}

    @classmethod
    def parse_obj(cls, obj: Any) -> "BaseModel":
        if not isinstance(obj, dict):
            raise ValidationError(f"Object of type {type(obj).__name__} is not a dict")
        return cls(**obj)

    @classmethod
    def _coerce_value(cls, expected_type: Any, value: Any) -> Any:
        if expected_type is None:
            return value

        origin = get_origin(expected_type)
        if origin in (list, List):
            if value is None:
                return None
            (item_type,) = get_args(expected_type) or (Any,)
            return [cls._coerce_value(item_type, item) for item in value]
        if origin in (dict, Dict):
            if value is None:
                return None
            key_type, value_type = get_args(expected_type) or (Any, Any)
            return {
                cls._coerce_value(key_type, key): cls._coerce_value(value_type, item)
                for key, item in value.items()
            }

        if origin is Union:
            args = [arg for arg in get_args(expected_type) if arg is not type(None)]  # noqa: E721
            if not args or value is None:
                return value
            return cls._coerce_value(args[0], value)

        if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
            if isinstance(value, expected_type):
                return value
            if isinstance(value, dict):
                return expected_type(**value)

        return value

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        annotations = {
            key: value
            for key, value in get_type_hints(self.__class__).items()
            if not key.startswith("_")
        }
        fields = ", ".join(f"{k}={getattr(self, k)!r}" for k in annotations)
        return f"{self.__class__.__name__}({fields})"
