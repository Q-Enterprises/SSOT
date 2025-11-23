"""Schemas and helpers used by FastAPI endpoints for validation."""
from typing import Any, Dict, Type

from pydantic import BaseModel, ValidationError


class Credential(BaseModel):
    """Schema describing a credential submission."""

    user: str
    credential: str


class OverrideRequest(BaseModel):
    """Schema describing an override request payload."""

    requestor: str
    action: str
    target: str


def validate_payload(schema: Type[BaseModel], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate payloads against the provided Pydantic schema."""

    try:
        validated = schema(**payload)
        return {"valid": True, "data": validated.dict()}
    except ValidationError as exc:
        return {"valid": False, "errors": exc.errors()}
