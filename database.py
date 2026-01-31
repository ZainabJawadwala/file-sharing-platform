import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read DB URL from environment for Postgres in production; fallback to SQLite for local dev.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./fileshare.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite:"):
	connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
