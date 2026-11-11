# ===== app/db/session.py =====
# Step 2 · Database connection
# What: engine (once, holds the connection pool), SessionLocal, Base, get_db.
# Concepts: engine vs session, one session per request, dependency with yield + finally.
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Engine: created ONCE. Knows the DB URL and keeps a pool of connections.
# check_same_thread=False is needed only for SQLite (FastAPI uses several threads).
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

# Factory that creates a new Session each time we call SessionLocal().
SessionLocal = sessionmaker(bind=engine)


# Parent class for all our models (tables).
class Base(DeclarativeBase):
    pass


# Dependency: gives each request its own session, and always closes it.
def get_db():
    db = SessionLocal()
    try:
        yield db  # the route runs here
    finally:
        db.close()  # runs even if the route raised an error
