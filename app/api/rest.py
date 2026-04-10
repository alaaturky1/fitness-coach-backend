from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_api_key
from app.core.models import (
    AnalyzeFrameRequest,
    AnalyzeFrameResponse,
    EndSessionRequest,
    SessionSummaryResponse,
    StartSessionRequest,
    StartSessionResponse,
)
from app.storage.inmemory import sessions

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/start-session", response_model=StartSessionResponse)
def start_session(req: StartSessionRequest) -> StartSessionResponse:
    session = sessions.create_session(language=req.language, level=req.level)
    return StartSessionResponse(session_id=session.session_id, ws_url=f"/ws/session/{session.session_id}")


@router.post("/analyze-frame", response_model=AnalyzeFrameResponse)
def analyze_frame(req: AnalyzeFrameRequest) -> AnalyzeFrameResponse:
    session = sessions.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return session.engine.analyze(req.frame)


@router.post("/end-session", response_model=SessionSummaryResponse)
def end_session(req: EndSessionRequest) -> SessionSummaryResponse:
    session = sessions.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    session.ended = True
    return session.engine.summary()


@router.get("/session-summary/{session_id}", response_model=SessionSummaryResponse)
def session_summary(session_id: str) -> SessionSummaryResponse:
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return session.engine.summary()

