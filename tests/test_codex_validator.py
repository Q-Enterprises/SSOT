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
    # Pydantic V2 error message is "Field required"
    msg = errors[0]["msg"]
    assert "Field required" in msg or "Missing fields" in msg

def test_validate_payload_nested_valid():
    payload = {"nested": {"field": "value"}}
    result = validate_payload(ComplexSchema, payload)
    assert result["valid"] is True
    # In Pydantic V2, model_dump returns dicts recursively
    assert result["data"]["nested"]["field"] == "value"

def test_validate_payload_nested_invalid():
    payload = {"nested": {}} # missing field in nested model
    result = validate_payload(ComplexSchema, payload)
    assert result["valid"] is False
    assert "errors" in result
    msg = result["errors"][0]["msg"]
    assert "Field required" in msg or "Missing fields" in msg

def test_validate_payload_extra_fields():
    payload = {"name": "Alice", "age": 30, "extra": "field"}
    result = validate_payload(MockSchema, payload)
    assert result["valid"] is True
    # Verify extra field is NOT in the output data (sanitization)
    # Pydantic V2 ignores extra fields by default
    assert "extra" not in result["data"]
