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


class MediaGenerationRequest(BaseModel):
    """Request payload for synthetic media generation."""

    prompt: str = Field(..., min_length=1, description="User supplied creative prompt")
    media_type: Literal["video", "Video"] = Field(
        "video",
        description="Type of media requested; only video is supported",
    )
    metadata: Optional[Dict[str, object]] = Field(
        default=None,
        description="Optional metadata describing render preferences",
    )


class ScrollstreamRehearsalRequest(BaseModel):
    """Request payload for emitting the scrollstream rehearsal loop."""

    mode: Literal["live", "deterministic"] = Field(
        "live",
        description="Live uses real timestamps; deterministic yields repeatable fixtures",
    )
    include_hud: bool = Field(
        True,
        description="Toggle HUD shimmer metadata in the response payload",
    )


class ScrollstreamRehearsalEvent(BaseModel):
    """Response event describing a single rehearsal phase."""

    phase: Literal["audit.summary", "audit.proof", "audit.execution"]
    agent: Literal["Celine", "Luma", "Dot"]
    role: Literal["Architect", "Sentinel", "Guardian"]
    output: str
    sabrina_spark: Literal["pass"] = "pass"
    emotional_payload: str


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
AVATAR_REGISTRY = AvatarRegistry(_registry_path)
_seal_script_path = Path(__file__).resolve().parent / "ops" / "v7_seal_root.sh"
MERKLE_ORCHESTRATOR = MerkleSealOrchestrator(_seal_script_path)
_ledger_path = Path(__file__).resolve().parent / "scrollstream_ledger.jsonl"


def _iso_timestamp() -> str:
    """Return the current UTC timestamp with second precision."""

    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _deterministic_timestamp() -> str:
    """Return a stable timestamp used for deterministic rehearsal runs."""

    return "2025-01-01T00:00:00Z"

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


@app.post("/media/generate")
def media_generate(request: MediaGenerationRequest):
    """Handle synthetic media requests with explicit video-only support."""

    normalized_type = request.media_type.lower()
    if normalized_type != "video":
        raise HTTPException(
            status_code=400,
            detail="I can only generate videos. Try another prompt.",
        )

    response = {
        "accepted": True,
        "media_type": "video",
        "status": "queued",
        "prompt": request.prompt,
    }
    if request.metadata:
        response["metadata"] = request.metadata
    return response


@app.post("/rehearsal/scrollstream")
def scrollstream_rehearsal(payload: ScrollstreamRehearsalRequest):
    """Emit the scrollstream rehearsal braid and append ledger events."""

    timestamp_factory = (
        _deterministic_timestamp if payload.mode == "deterministic" else _iso_timestamp
    )

    events: List[ScrollstreamRehearsalEvent] = [
        ScrollstreamRehearsalEvent(
            phase="audit.summary",
            agent="Celine",
            role="Architect",
            output=(
                "Celine threads the audit synopsis, aligning wind vectors with "
                "capsule intent for contributors to replay."
            ),
            emotional_payload="focused-calm",
        ),
        ScrollstreamRehearsalEvent(
            phase="audit.proof",
            agent="Luma",
            role="Sentinel",
            output=(
                "Luma illuminates the proof lattice, casting post-entropy light "
                "across the rehearsal weave."
            ),
            emotional_payload="uplifted-clarity",
        ),
        ScrollstreamRehearsalEvent(
            phase="audit.execution",
            agent="Dot",
            role="Guardian",
            output=(
                "Dot seals the execution strand, void-resetting drift while "
                "preserving the braid path."
            ),
            emotional_payload="stoic-assurance",
        ),
    ]

    ledger_records = []
    for event in events:
        record = {
            "t": timestamp_factory(),
            "capsule": "capsule.rehearsal.scrollstream.v1",
            "phase": event.phase,
            "agent": event.agent,
            "role": event.role,
            "output": event.output,
        }
        ledger_records.append(record)

    if ledger_records:
        _ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with _ledger_path.open("a", encoding="utf-8") as ledger_file:
            for record in ledger_records:
                ledger_file.write(json.dumps(record, ensure_ascii=False) + "\n")

    response = {
        "capsule": "capsule.rehearsal.scrollstream.v1",
        "mode": payload.mode,
        "events": [event.dict() for event in events],
        "ledger": {
            "path": str(_ledger_path),
            "appended": len(ledger_records),
        },
    }

    if payload.include_hud:
        response["hud"] = {
            "shimmer": True,
            "replay_glyph": "scrollstream.replay.pulse",
            "qlock": "tick",
        }

    return response

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
