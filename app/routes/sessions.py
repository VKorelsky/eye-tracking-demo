from fastapi import APIRouter
from typing import Any, Dict

from app.deps import SessionDep
from app.models import SessionBase

router = APIRouter(tags=["sessions"])


@router.post("/sessions")
async def create_session(db_session: SessionDep, data: SessionBase):
    return "persisting session"


@router.get("/sessions")
async def list_sessions():
    return "list of all the sessions"


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    return "some basic session data"
