import json
import logging
import os
import subprocess
from copy import deepcopy
from pathlib import Path
from time import time
from typing import Dict, Iterable, List, Optional, Sequence

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from codex_validator import Credential, OverrideRequest, validate_payload

logger = logging.getLogger(__name__)


class AvatarRegistry:
    """In-memory representation of the avatar dossier registry.

    The registry is loaded once at application startup and exposes
    convenience helpers so route handlers can provide rich responses
    without repeating parsing logic.
    """

    def __init__(self, registry_path: Path) -> None:
        self._path = registry_path
        data = self._load()
        self._mesh: Dict[str, object] = data.get("mesh", {})
        self._avatars: List[Dict[str, object]] = data.get("avatars", [])
        self._index = self._build_index(self._avatars)
        self._available_names = tuple(
            avatar["name"]
            for avatar in self._avatars
            if isinstance(avatar.get("name"), str)
        )

    def _load(self) -> Dict[str, object]:
        """Load registry data from disk, handling common failure cases."""

        if not self._path.exists():
            logger.warning("Avatar registry file is missing at %s", self._path)
            return {"mesh": {}, "avatars": []}

        try:
            with self._path.open("r", encoding="utf-8") as registry_file:
                return json.load(registry_file)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            logger.error("Failed to parse avatar registry: %s", exc)
        except OSError as exc:  # pragma: no cover - unexpected I/O error
            logger.error("Unable to read avatar registry: %s", exc)
        return {"mesh": {}, "avatars": []}

    @staticmethod
    def _build_index(avatars: Iterable[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
        """Normalize names for quick lookups."""

        index: Dict[str, Dict[str, object]] = {}
        for avatar in avatars:
            name = avatar.get("name")
            if not isinstance(name, str):
                continue
            normalized = name.strip().lower()
            if normalized:
                index[normalized] = avatar
        return index

    def mesh(self) -> Dict[str, object]:
        """Return mesh metadata describing the Agent Mesh context."""

        return deepcopy(self._mesh)

    def list(self, element: Optional[str] = None) -> List[Dict[str, object]]:
        """Return avatars, optionally filtered by elemental alignment."""

        if element is None:
            return [deepcopy(avatar) for avatar in self._avatars]

        normalized = element.strip().lower()
        filtered: List[Dict[str, object]] = []
        for avatar in self._avatars:
            alignment = avatar.get("elemental_alignment")
            if isinstance(alignment, str) and alignment.strip().lower() == normalized:
                filtered.append(deepcopy(avatar))
        return filtered

    def get(self, name: str) -> Optional[Dict[str, object]]:
        """Return a single avatar dossier by normalized name."""

        if not name:
            return None
        avatar = self._index.get(name.strip().lower())
        return deepcopy(avatar) if avatar else None

    def available_names(self) -> Sequence[str]:
        """Return the list of canonical avatar names."""

        return self._available_names

    def elemental_alignments(self) -> List[str]:
        """Return the unique elemental alignments present in the registry."""

        seen = {
            alignment.strip()
            for alignment in (
                avatar.get("elemental_alignment") for avatar in self._avatars
            )
            if isinstance(alignment, str) and alignment.strip()
        }
        return sorted(seen, key=str.lower)

    def capsule_domains(self) -> List[str]:
        """Return unique capsule domains for quick cross-referencing."""

        domains = {
            domain.strip()
            for domain in (avatar.get("capsule_domain") for avatar in self._avatars)
            if isinstance(domain, str) and domain.strip()
        }
        return sorted(domains)


class MerkleSealOrchestrator:
    """Automate Merkle sealing by invoking the Boo council helper script."""

    def __init__(self, script_path: Path) -> None:
        self._script_path = script_path

    def _ensure_available(self) -> None:
        if not self._script_path.exists():
            raise FileNotFoundError(f"Seal helper missing at {self._script_path}")
        if not os.access(self._script_path, os.X_OK):
            raise PermissionError(f"Seal helper is not executable: {self._script_path}")

    def seal(
        self,
        merkle_root: str,
        capsule_id: str,
        metadata: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        """Invoke the helper script and return execution metadata."""

        self._ensure_available()
        command = [str(self._script_path), merkle_root, capsule_id]
        env = os.environ.copy()
        if metadata:
            env["MERKLE_METADATA"] = json.dumps(metadata)

        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Seal helper failed",
                {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )

        return {
            "capsule": capsule_id,
            "merkle_root": merkle_root,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "script": str(self._script_path),
        }


class MerkleSealRequest(BaseModel):
    """Request payload for triggering a Merkle seal."""

    merkle_root: str = Field(
        ...,
        min_length=1,
        description="Newly computed Merkle root digest",
    )
    capsule_id: str = Field(
        "capsule.council.boo.agency.v7",
        min_length=1,
        description="Capsule identifier to bind the seal to",
    )
    metadata: Optional[Dict[str, object]] = Field(
        default=None,
        description="Optional metadata passed to the seal helper via MERKLE_METADATA",
    )


app = FastAPI()

# Load the avatar registry into memory at startup. This registry is
# treated as read-only and anchors avatar logic to the DimIndex scroll.
_registry_path = Path(__file__).resolve().parent / "avatar_registry.json"
AVATAR_REGISTRY = AvatarRegistry(_registry_path)
_seal_script_path = Path(__file__).resolve().parent / "ops" / "v7_seal_root.sh"
MERKLE_ORCHESTRATOR = MerkleSealOrchestrator(_seal_script_path)

@app.get("/health")
def health_check():
    """Return a simple JSON status to indicate service liveness."""
    return {"status": "alive"}


@app.get("/healthz")
def readiness_check():
    """Expose readiness details compatible with container probes."""
    return {"ok": True, "ts": int(time() * 1000)}


@app.get("/avatars")
def list_avatars(element: Optional[str] = Query(None, description="Filter by elemental alignment")):
    """Return the full avatar dossier as loaded from the registry."""

    avatars = AVATAR_REGISTRY.list(element)
    return {
        "count": len(avatars),
        "filter": {"element": element} if element else None,
        "mesh": AVATAR_REGISTRY.mesh(),
        "elemental_alignments": AVATAR_REGISTRY.elemental_alignments(),
        "capsule_domains": AVATAR_REGISTRY.capsule_domains(),
        "avatars": avatars,
    }


@app.get("/avatars/{avatar_name}")
def fetch_avatar(avatar_name: str):
    """Fetch a single avatar dossier by name.

    Names are normalized to lowercase, so callers may provide any
    casing. If the avatar is not found, return a 404 error to signal
    that the registry lacks the requested record.
    """

    normalized = avatar_name.strip().lower()
    if not normalized:
        raise HTTPException(status_code=400, detail="Avatar name is required")

    avatar = AVATAR_REGISTRY.get(normalized)
    if avatar is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Avatar not found",
                "available": list(AVATAR_REGISTRY.available_names()),
            },
        )
    return avatar


@app.get("/mesh")
def mesh_overview():
    """Expose high-level metadata about the Agent Mesh."""

    mesh = AVATAR_REGISTRY.mesh()
    return {
        "name": mesh.get("name", "Agent Mesh"),
        "description": mesh.get("description"),
        "elemental_alignments": mesh.get("elemental_alignments", {}),
    }

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhook events.

    Echo back whether a payload was received and return the action
    field if present. In a production environment you would validate
    the request signature using a shared secret or token on the event.
    """
    payload = await request.json()
    return {"received": True, "event": payload.get("action", "unknown")}


@app.post("/merkle/seal")
def merkle_seal(payload: MerkleSealRequest):
    """Trigger the Boo council seal helper via the Merkle orchestrator."""

    try:
        result = MERKLE_ORCHESTRATOR.seal(
            payload.merkle_root,
            payload.capsule_id,
            payload.metadata,
        )
    except (FileNotFoundError, PermissionError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RuntimeError as exc:
        _, details = exc.args
        raise HTTPException(status_code=502, detail=details) from exc

    return {
        "orchestrated": True,
        "result": result,
    }

@app.post("/qbot/credentials")
async def credential_checker(request: Request):
    """Validate and process credential payloads.

    Uses the Credential schema defined in `codex_validator` to enforce
    that incoming data includes the expected fields. If the data is
    valid, return the validated data; otherwise return validation
    errors. This helps fossilize credential flows as audit-grade
    artifacts.
    """
    data = await request.json()
    return validate_payload(Credential, data)

@app.post("/qbot/override")
async def override_simulator(request: Request):
    """Validate and simulate override requests.

    This endpoint uses the OverrideRequest schema to enforce that
    incoming override requests contain the required fields. If the
    payload is valid, augment the response with override response fields
    metadata and echo back the original request. Otherwise, return
    validation errors.
    """
    data = await request.json()
    result = validate_payload(OverrideRequest, data)
    if result.get("valid"):
        # Augment successful validation with override response fields
        result.update({
            "override": "accepted",
            "reason": "proof-mode",
            "request": data,
        })
    return result

@app.post("/qbot/onboard")
async def onboard_agent(request: Request):
    """Simulate the credential onboarding ritual.

    Generates a badge for the given user and returns onboarding
    confirmation. In a real-world scenario, this would issue a badge
    through a credentialing service and persist the onboarding record.
    """
    data = await request.json()
    user = data.get("user", "unknown")
    badge = f"{user}-badge-v1"
    return {
        "onboarded": True,
        "badge": badge,
        "status": "credentialed"
    }
