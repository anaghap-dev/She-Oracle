import os
import json
import asyncio
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Validate API key early
if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY not set in orchestrator/.env")

from agents.planner import run_plan
from agents import memory as mem_agent
from agents.memory import get_artifacts
from rag.chroma_store import collection_count
from tools.threat_analyzer import analyze_threat as _analyze_threat
from tools.document_generator import generate_documents as _generate_documents
from tools.cab_risk_scorer import score_cab_risk as _score_cab_risk
from tools.cab_safety_advisor import generate_cab_safety_response as _generate_cab_safety_response
from gemini_client import gemini_status


def _auto_seed():
    """Seed ChromaDB on startup if empty — needed on Render (no persistent disk, no shell)."""
    try:
        count = collection_count()
        if count > 0:
            print(f"SHE-ORACLE Orchestrator started. ChromaDB has {count} knowledge chunks.")
            return
        print("ChromaDB is empty — auto-seeding knowledge base...")
        # Import here to avoid circular imports at module level
        from rag.seed_knowledge import seed
        seed()
        print(f"Auto-seed complete. ChromaDB now has {collection_count()} chunks.")
    except Exception as e:
        print(f"WARNING: Auto-seed failed: {e}. RAG will be unavailable.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fire seed in background — do NOT await it.
    # Render detects the port only after startup completes; awaiting a slow
    # seed (30s+) causes Render to kill the process before the port is open.
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _auto_seed)
    yield


app = FastAPI(
    title="SHE-ORACLE Orchestrator",
    description="Autonomous multi-agent AI for women empowerment",
    version="1.0.0",
    lifespan=lifespan,
)

_allowed_origins = [
    "http://localhost:3001",
    "http://localhost:5173",
]
# Allow production backend URL set via env var (e.g. https://she-oracle-backend.up.railway.app)
if os.getenv("BACKEND_URL"):
    _allowed_origins.append(os.getenv("BACKEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ────────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    goal: str
    domain: str = "general"
    session_id: str = ""
    extra_context: dict = {}


class ProfileUpdateRequest(BaseModel):
    session_id: str
    profile_data: dict


class StepCompleteRequest(BaseModel):
    session_id: str
    step: str


class ThreatAnalysisRequest(BaseModel):
    evidence_text: str
    context: str = ""


class DocumentGenerationRequest(BaseModel):
    victim_name: str
    incident_description: str
    evidence_summary: str
    threat_analysis: dict
    contact_info: str = ""


class ArtifactDownloadRequest(BaseModel):
    artifact_id: str
    session_id: str
    filename: str = ""


class CabSafetyRequest(BaseModel):
    driver_name: str = ""
    vehicle_plate: str = ""
    pickup: str = ""
    destination: str = ""
    time_of_day: str = "day"      # day | evening | night | late_night
    area_type: str = "urban"      # urban | suburban | rural | highway
    behaviour_flags: list = []


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    ai = gemini_status()
    return {
        "status": "ok",
        "knowledge_chunks": collection_count(),
        "ai": {
            "healthy": ai["healthy"],
            "last_failure": ai["last_failure"],
            "fallback_mode": not ai["healthy"],
        },
    }


@app.post("/run")
async def run_agent(request: RunRequest):
    """
    Non-streaming endpoint — runs full agent loop and returns complete plan.
    Used by Node.js backend for simple requests.
    """
    if not request.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")

    session_id = request.session_id or str(uuid.uuid4())
    events = []

    async for event in run_plan(
        goal=request.goal,
        domain=request.domain,
        session_id=session_id,
        extra_context=request.extra_context,
    ):
        events.append(event)

    plan_event = next((e for e in reversed(events) if e.get("type") == "result"), None)
    error_event = next((e for e in reversed(events) if e.get("type") == "error"), None)

    if plan_event:
        return {
            "session_id": session_id,
            "plan": plan_event["plan"],
            "events": events,
        }
    elif error_event:
        raise HTTPException(status_code=500, detail=error_event.get("content", "Agent error"))
    else:
        raise HTTPException(status_code=500, detail="No plan generated.")


@app.post("/stream")
async def stream_agent(request: RunRequest):
    """
    SSE streaming endpoint — yields agent events in real-time.
    """
    if not request.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")

    session_id = request.session_id or str(uuid.uuid4())

    async def event_generator():
        # Send session_id first
        yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"
        await asyncio.sleep(0)

        try:
            async for event in run_plan(
                goal=request.goal,
                domain=request.domain,
                session_id=session_id,
                extra_context=request.extra_context,
            ):
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0)
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session memory."""
    memory = mem_agent.load(session_id)
    return memory


@app.post("/session/profile")
async def update_profile(request: ProfileUpdateRequest):
    """Update user profile in memory."""
    memory = mem_agent.update_profile(request.session_id, request.profile_data)
    return {"status": "ok", "profile": memory.get("user_profile", {})}


@app.post("/session/step-complete")
async def complete_step(request: StepCompleteRequest):
    """Mark a step as completed."""
    mem_agent.add_completed_step(request.session_id, request.step)
    return {"status": "ok"}


@app.get("/kb/status")
async def kb_status():
    """Knowledge base status."""
    return {
        "total_chunks": collection_count(),
        "status": "ready" if collection_count() > 0 else "empty — run seed_knowledge.py",
    }


# ── Protection Intelligence Layer ─────────────────────────────────────────────

@app.post("/analyze-threat")
async def analyze_threat_endpoint(request: ThreatAnalysisRequest):
    """
    Analyze digital harassment evidence for threat classification,
    severity scoring, legal mapping, and escalation guidance.
    """
    if not request.evidence_text.strip():
        raise HTTPException(status_code=400, detail="Evidence text cannot be empty.")

    try:
        result = _analyze_threat(
            evidence_text=request.evidence_text,
            context=request.context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat analysis error: {str(e)}")


@app.post("/generate-documents")
async def generate_documents_endpoint(request: DocumentGenerationRequest):
    """
    Generate formal legal documents for a digital harassment case:
    FIR draft, complaint letter, takedown request, legal notice.
    """
    if not request.incident_description.strip():
        raise HTTPException(status_code=400, detail="Incident description cannot be empty.")

    try:
        result = _generate_documents(
            victim_name=request.victim_name or "Complainant",
            incident_description=request.incident_description,
            evidence_summary=request.evidence_summary,
            threat_analysis=request.threat_analysis,
            contact_info=request.contact_info,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation error: {str(e)}")


# ── Cab Safety Intelligence ────────────────────────────────────────────────────

@app.post("/cab-safety/assess")
async def cab_safety_assess(request: CabSafetyRequest):
    """
    Deterministic risk scoring + LLM-generated safety response for cab rides.
    Returns structured risk object, emergency message, safety card,
    escalation steps, complaint draft, and helplines.
    """
    try:
        risk = _score_cab_risk(
            driver_name=request.driver_name,
            vehicle_plate=request.vehicle_plate,
            time_of_day=request.time_of_day,
            area_type=request.area_type,
            behaviour_flags=request.behaviour_flags,
        )
        advice = _generate_cab_safety_response(
            risk_result=risk,
            driver_name=request.driver_name,
            vehicle_plate=request.vehicle_plate,
            pickup=request.pickup,
            destination=request.destination,
            time_of_day=request.time_of_day,
            area_type=request.area_type,
            behaviour_flags=request.behaviour_flags,
        )
        return {"risk": risk, "advice": advice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cab safety assessment error: {str(e)}")


# ── Artifact Retrieval & Download ──────────────────────────────────────────────

@app.get("/artifacts/{session_id}")
async def get_session_artifacts(session_id: str):
    """Retrieve all artifacts for a session."""
    artifacts = get_artifacts(session_id)
    return {"session_id": session_id, "artifacts": artifacts, "count": len(artifacts)}


@app.post("/download-artifact")
async def download_artifact(request: ArtifactDownloadRequest):
    """Return a specific artifact as a downloadable file."""
    artifacts = get_artifacts(request.session_id)
    artifact = next((a for a in artifacts if a.get("id") == request.artifact_id), None)

    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found in session.")

    content = artifact.get("content", "")
    fmt = artifact.get("format", "text")
    content_type = "text/markdown" if fmt == "markdown" else "text/plain"
    filename = request.filename or f"{artifact.get('type', 'document')}_{request.artifact_id[:8]}.md"

    return Response(
        content=content.encode("utf-8"),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
