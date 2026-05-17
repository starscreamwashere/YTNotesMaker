import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Load from environment variable (ensure DATABASE_URL is set in .env)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # Optional: help user identify the issue locally
    print("WARNING: DATABASE_URL not found in environment. Defaulting to local postgres for development.")
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres@localhost:5432/YtNotes"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
