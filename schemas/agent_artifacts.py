from typing import Any, Dict
from pydantic import BaseModel

class MCPArtifact(BaseModel):
    artifact_id: str
    type: str
    content: str
    metadata: Dict[str, Any]
