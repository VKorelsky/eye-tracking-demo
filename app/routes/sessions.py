from fastapi import APIRouter, HTTPException, Header, Response
from typing import Annotated, Any
import uuid
import datetime

from app.deps import SessionDep
from app.models import Session, Sample, SessionCreate

router = APIRouter(tags=["sessions"])


@router.post("/sessions", status_code=201)
async def create_session(
    db_session: SessionDep, data: SessionCreate, user_agent: Annotated[str | None, Header()]
) -> dict[str, Any]:
    try:
        created_at = data.recorded_at or datetime.datetime.now(datetime.timezone.utc)

        session_id = uuid.uuid4()
        device_info = "Unknown" if user_agent is None else user_agent

        session = Session(
            id=session_id,
            user_agent=device_info,
            accuracy=data.accuracy,
            sample_rate=data.sample_rate,
            created_at=created_at,
        )
        db_session.add(session)

        samples = [
            Sample(
                session_id=session.id,
                timestamp=s.timestamp,
                pos=s.pos,
            )
            for s in data.samples
        ]

        db_session.add_all(samples)
        db_session.commit()
        
        return Response(status_code=201)
    except Exception as e:
        db_session.rollback()
        print(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session")


@router.get("/sessions")
async def list_sessions():
    return "list of all the sessions"


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    return "some basic session data"
