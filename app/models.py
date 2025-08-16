import datetime
import uuid
from sqlmodel import Field, Relationship, SQLModel, String

class SessionBase(SQLModel):
    user_agent: str = Field(max_length=1024)
    accuracy: int = Field(ge=0, le=100)
    sample_rate: int = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Session(SessionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    samples: list["Sample"] = Relationship(back_populates="session")

class SampleBase(SQLModel):
    timestamp: datetime = Field()
    pos: float = Field()

class Sample(SampleBase, table=True):
    session_id: uuid.UUID = Field(foreign_key="session.id", primary_key=True) 
    timestamp: datetime = Field(primary_key=True) # redefine timestamp to highlight it being part of the primary key
    session: Session = Relationship(back_populates="samples")