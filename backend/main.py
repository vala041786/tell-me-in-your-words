from fastapi import FastAPI, HTTPException

from backend.container import get_orchestrator
from backend.models import (
    ExplainRequest,
    ExplainResponse,
    RecoverRequest,
    RecoverResponse,
    SessionNextRequest,
    SessionNextResponse,
)
from backend.orchestrator import SessionEvent, SessionState

app = FastAPI(title="Tell Me In Your Words API", version="0.2.0")
_sessions: dict[str, SessionState] = {}


def _get_session(session_id: str) -> SessionState:
    if session_id not in _sessions:
        _sessions[session_id] = SessionState(session_id=session_id)
    return _sessions[session_id]


@app.get("/")
def root():
    return {"name": "Tell Me In Your Words", "tagline": "You don't need the right words."}


@app.post("/session/next", response_model=SessionNextResponse)
def session_next(request: SessionNextRequest):
    orchestrator = get_orchestrator()
    state = _get_session(request.session_id)
    try:
        event = SessionEvent(request.event)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown event: {request.event}") from exc

    updated = orchestrator.handle(state, event, request.payload)
    _sessions[request.session_id] = updated
    return SessionNextResponse(
        session=updated.model_dump(mode="json"),
        next_actions=orchestrator.next_actions(updated),
    )


@app.post("/recover", response_model=RecoverResponse)
def recover(request: RecoverRequest):
    orchestrator = get_orchestrator()
    state = orchestrator.handle(
        SessionState(session_id="recover"),
        SessionEvent.SUBMIT_QUERY,
        {"query": request.text},
    )
    return RecoverResponse(
        original_text=request.text,
        suggestions=state.suggestions,
        message=state.message,
    )


@app.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest):
    orchestrator = get_orchestrator()
    state = orchestrator.handle(
        SessionState(session_id="explain"),
        SessionEvent.CONFIRM_TERM,
        {"term": request.term},
    )
    if not state.explain_view:
        raise HTTPException(status_code=404, detail="Term not found")

    view = state.explain_view
    return ExplainResponse(
        term=view.term,
        domain=view.domain,
        explanation=view.explanation,
        source_name=view.source_name,
        source_url=view.source_url,
        followups=view.followups,
        expert_context=view.expert_context,
        safety_note=view.safety_note,
    )
