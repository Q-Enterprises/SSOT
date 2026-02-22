import sys
from pathlib import Path
from typing import Dict, Any, List
import pytest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pydantic
from pydantic import BaseModel, ValidationError
from codex_validator import validate_payload

class MockSchema(BaseModel):
    name: str
    age: int

class NestedModel(BaseModel):
    field: str

class ComplexSchema(BaseModel):
    nested: NestedModel

def test_validate_payload_valid():
    payload = {"name": "Alice", "age": 30}
    result = validate_payload(MockSchema, payload)
    assert result["valid"] is True
    assert result["data"] == payload

def test_validate_payload_invalid_missing_field():
    payload = {"name": "Alice"}
    result = validate_payload(MockSchema, payload)
    assert result["valid"] is False
    assert "errors" in result
    errors = result["errors"]
    assert isinstance(errors, list)
    assert len(errors) > 0
    assert "msg" in errors[0]
    # Verify error message content
    assert "Missing fields" in errors[0]["msg"]
    assert "age" in errors[0]["msg"]

def test_validate_payload_nested_valid():
    payload = {"nested": {"field": "value"}}
    result = validate_payload(ComplexSchema, payload)
    assert result["valid"] is True
    assert result["data"]["nested"].field == "value"

def test_validate_payload_nested_invalid():
    payload = {"nested": {}} # missing field in nested model
    # The shim's _coerce_value creates the nested model.
    # If creation fails, it raises ValidationError.
    # codex_validator catches it.

    result = validate_payload(ComplexSchema, payload)
    assert result["valid"] is False
    assert "errors" in result
    assert "Missing fields" in result["errors"][0]["msg"]

def test_validate_payload_extra_fields():
    # Shim behavior on extra fields: it ignores them?
    # Shim __init__:
    # annotations = ...
    # initial_data = dict(data)
    # missing = ...
    # for field, value in initial_data.items():
    #    expected = annotations.get(field)
    #    setattr(self, field, self._coerce_value(expected, value))

    # It sets attributes for all keys in input data, even if not in annotations.
    # But .dict() only returns keys in annotations.

    payload = {"name": "Alice", "age": 30, "extra": "field"}
    result = validate_payload(MockSchema, payload)
    assert result["valid"] is True
    # Verify extra field is NOT in the output data (sanitization)
    assert "extra" not in result["data"]
