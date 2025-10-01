from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base  # Import Base from base.py

DATABASE_URL = "sqlite:///./test.db"  # Example database URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_DB():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()