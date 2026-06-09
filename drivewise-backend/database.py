from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./drivewise.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    language_code = Column(String, nullable=False)
    total = Column(Integer, nullable=False)
    correct = Column(Integer, nullable=False)
    score_pct = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    duration_seconds = Column(Integer, default=0)
    review = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
