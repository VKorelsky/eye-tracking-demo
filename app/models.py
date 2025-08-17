import datetime
import uuid
from typing import List
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class Session(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_agent: str = Field(max_length=1024)
    accuracy: int = Field(ge=0, le=100)
    sample_rate: int = Field()
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    samples: list["Sample"] = Relationship(back_populates="session")


class SampleBase(SQLModel):
    timestamp: datetime.datetime = Field()
    pos: float = Field()


class Sample(SampleBase, table=True):
    session_id: uuid.UUID = Field(foreign_key="session.id", primary_key=True)
    timestamp: datetime.datetime = Field(primary_key=True)
    session: "Session" = Relationship(back_populates="samples")


# request/response schemas
class SessionCreate(BaseModel):
    accuracy: int = Field(ge=0, le=100)
    sample_rate: int = Field()
    recorded_at: datetime.datetime | None = None
    samples: List[SampleBase]


class SessionCreateResponse(BaseModel):
    id: uuid.UUID


class SessionRead(BaseModel):
    id: uuid.UUID
    user_agent: str
    accuracy: int
    sample_rate: int
    created_at: datetime.datetime
