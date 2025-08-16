from fastapi import APIRouter
from typing import Any, Dict

router = APIRouter(tags=["sessions"])

@router.post("/sessions")
async def create_session(session_data: Dict[str, Any]):
    return "session created"


@router.get("/sessions")
async def list_sessions():
    return "list of all the sessions"


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    return "some basic session data"
