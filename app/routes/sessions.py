from fastapi import APIRouter, HTTPException, Header, Query
from typing import Annotated
import uuid
import datetime

from sqlmodel import select

from app.deps import DBSessionDep
from app.models import Session, Sample, SessionCreate, SessionCreateResponse, SessionRead, SessionReadWithSamples

router = APIRouter(tags=["sessions"])


@router.post("/sessions", status_code=201, response_model=SessionCreateResponse)
async def create_session(db_session: DBSessionDep, data: SessionCreate, user_agent: Annotated[str | None, Header()]):
    try:
        created_at = data.recorded_at or datetime.datetime.now(datetime.timezone.utc)

        session_id = uuid.uuid4()
        device_info = "Unknown" if user_agent is None else user_agent
        session_duration = round(data.duration, 3)

        session = Session(
            id=session_id,
            user_agent=device_info,
            sample_rate=data.sample_rate,
            duration=session_duration,
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

        return SessionCreateResponse(id=session.id)
    except Exception as e:
        db_session.rollback()
        print(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session")


@router.get("/sessions", response_model=list[SessionRead])
async def list_sessions(db_session: DBSessionDep, offset: int = 0, limit: Annotated[int, Query(le=150)] = 150):
    sessions = db_session.exec(select(Session).order_by(Session.created_at.desc()).offset(offset).limit(limit)).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionReadWithSamples)
async def get_session(db_session: DBSessionDep, session_id: uuid.UUID):
    statement = select(Session).where(Session.id == session_id).join(Session.samples).order_by(Sample.timestamp.asc())

    session = db_session.exec(statement).first()

    if not session:
        raise HTTPException(status_code=404, detail="No session found")

    return session
