import os
from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

db_url = "postgresql://{user}:{password}@{host}/{db}".format(
    user=os.getenv("DB_USER", ""),
    password=os.getenv("DB_PASS", ""),
    host=os.getenv("DB_HOST", ""),
    db=os.getenv("DB_NAME", ""),
)

db_engine = create_engine(str(db_url))
