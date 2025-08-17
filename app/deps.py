from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session

from .db import db_engine


def get_db() -> Generator[Session, None, None]:
    with Session(db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
