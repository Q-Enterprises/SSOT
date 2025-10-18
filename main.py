import json
import json
from pathlib import Path
from time import time

from fastapi import FastAPI, HTTPException, Request
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pathlib import Path
from time import time
from ipaddress import ip_address, ip_network
import json
from ipaddress import ip_address, ip_network

from codex_validator import Credential, OverrideRequest, validate_payload
from orchestrator.config import CAPSULE as ORCHESTRATOR_CAPSULE, FlowSubmission
from previz.ledger import LIBRARY
from previz.world_engine import WorldEngine
from screenplay import LIBRARY as SCREENPLAY_LIBRARY
from ssot.binder import binder

app = FastAPI()

WORLD_ENGINE = WorldEngine()

# Network block list enforcing council security guidance.
_BLOCKED_NETWORKS = tuple(
    ip_network(value)
    for value in (
        "3.134.238.10/32",
        "3.129.111.220/32",
        "52.15.118.168/32",
        "74.220.50.0/24",
        "74.220.58.0/24",
    )
)

_BLOCKED_NETWORKS = [
    ip_network("3.134.238.10/32"),
    ip_network("3.129.111.220/32"),
    ip_network("52.15.118.168/32"),
    ip_network("74.220.50.0/24"),
    ip_network("74.220.58.0/24"),
]


@app.middleware("http")
async def blocklisted_ip_guard(request: Request, call_next):
    """Reject requests originating from blocklisted IP ranges."""

    client_host = request.client.host if request.client else None
    if client_host:
        try:
            client_ip = ip_address(client_host)
        except ValueError:
            client_ip = None
        if client_ip:
            for network in _BLOCKED_NETWORKS:
                if client_ip in network:
                    return JSONResponse(
                        {"detail": "Access denied from blocked network"},
                        status_code=403,
                    )
    return await call_next(request)

# Load the avatar registry into memory at startup. This registry is
# treated as read-only and anchors avatar logic to the DimIndex scroll.
_registry_path = Path(__file__).resolve().parent / "avatar_registry.json"
try:
    with _registry_path.open("r", encoding="utf-8") as _f:
        AVATAR_REGISTRY = json.load(_f)
except FileNotFoundError:
    # Fallback to empty registry if file is missing
    AVATAR_REGISTRY = {}

@app.get("/health")
def health_check():
    """Return a simple JSON status to indicate service liveness."""
    return {"status": "alive"}


@app.middleware("http")
async def enforce_blocklist(request: Request, call_next):
    """Deny access to requests originating from blocked networks."""

    client = request.client
    if client and client.host:
        try:
            client_ip = ip_address(client.host)
        except ValueError:
            client_ip = None
        if client_ip and any(client_ip in network for network in _BLOCKED_NETWORKS):
            raise HTTPException(status_code=403, detail="request blocked")
    response = await call_next(request)
    return response


@app.get("/healthz")
def readiness_check():
    """Expose readiness details compatible with container probes."""
    return {"ok": True, "ts": int(time() * 1000)}


@app.get("/avatars")
def avatar_registry():
    """Expose the avatar registry to downstream orchestrators."""

    return AVATAR_REGISTRY

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhook events.

    Echo back whether a payload was received and return the action
    field if present. In a production environment you would validate
    the request signature using a shared secret or token on the event.
    """
    payload = await request.json()
    return {"received": True, "event": payload.get("action", "unknown")}

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


@app.get("/ssot/registry")
def ssot_registry():
    """Return the SSOT binder with Merkle metadata."""

    return binder.as_dict()


@app.post("/ssot/registry/validate")
async def ssot_registry_validate(request: Request):
    """Validate a prospective SSOT entry and preview the Merkle root."""

    payload = await request.json()
    return binder.validate_candidate(payload)


@app.get("/orchestrator/capsule")
def orchestrator_capsule():
    """Return the orchestrator capsule specification."""

    return ORCHESTRATOR_CAPSULE.dict()


@app.post("/orchestrator/route")
async def orchestrator_route(request: Request):
    """Validate a routing sequence against the orchestrator flow order."""

    payload = await request.json()
    result = validate_payload(FlowSubmission, payload)
    if not result.get("valid"):
        return result
    submission = FlowSubmission(**result["data"])
    flow_result = ORCHESTRATOR_CAPSULE.validate_sequence(submission.sequence)
    result["flow"] = flow_result.dict()
    return result


@app.get("/screenplay/capsules")
def screenplay_capsules():
    """List screenplay capsules anchoring sovereign relays."""

    capsules = []
    for summary in SCREENPLAY_LIBRARY.list_capsules():
        capsules.append({
            "capsule_id": summary.capsule_id,
            "metadata": summary.metadata,
        })
    return {"capsules": capsules, "count": len(capsules)}


@app.get("/screenplay/capsules/{capsule_id}")
def screenplay_capsule(capsule_id: str):
    """Return a screenplay capsule payload by id."""

    try:
        capsule = SCREENPLAY_LIBRARY.get_capsule(capsule_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    payload = capsule.dict()
    payload["execution_tree"] = capsule.execution_tree()
    return payload


@app.get("/previz/ledgers")
def previz_ledgers():
    """List available PreViz ledgers with summary metadata."""

    ledgers = []
    for summary in LIBRARY.list_summaries():
        ledgers.append({
            "scene": summary.scene,
            "metadata": summary.metadata,
        })
    return {"ledgers": ledgers, "count": len(ledgers)}


@app.get("/previz/ledgers/{scene}")
def previz_ledger(scene: str):
    """Return the full ledger payload for a given scene."""

    try:
        ledger = LIBRARY.get_ledger(scene)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ledger.dict()


@app.post("/previz/render")
async def previz_render(request: Request):
    """Route media requests through the WorldEngine simulation."""

    payload = await request.json()
    media_type = payload.get("media_type", "video")
    prompt = payload.get("prompt")
    return WORLD_ENGINE.request_media(media_type, prompt)
