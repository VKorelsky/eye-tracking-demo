import datetime
import uuid
from typing import List
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class Session(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_agent: str = Field(max_length=1024)
    sample_rate: float = Field()
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    duration: float = Field()
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
    sample_rate: float
    recorded_at: datetime.datetime | None = None
    duration: float
    samples: List[SampleBase]


class SessionCreateResponse(BaseModel):
    id: uuid.UUID


class SampleRead(SampleBase):
    pass


class SessionRead(BaseModel):
    id: uuid.UUID
    user_agent: str
    duration: float
    sample_rate: float
    created_at: datetime.datetime


class SessionReadWithSamples(SessionRead):
    samples: list[SampleRead] = []
