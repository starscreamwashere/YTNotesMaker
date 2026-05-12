from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
import datetime

# Change this from a relative to an absolute import
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    sessions = relationship("Session", back_populates="owner")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Session")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="sessions")
    notes = relationship("Note", back_populates="session")
    chats = relationship("ChatHistory", back_populates="session")
    attachments = relationship("Attachment", back_populates="session")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    file_name = Column(String)
    file_url = Column(String) # Will store the S3/GCS bucket URL or local path
    mime_type = Column(String)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("Session", back_populates="attachments")

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)
    video_url = Column(String)
    title = Column(String, nullable=True)
    markdown_notes = Column(Text)
    transcript = Column(Text, nullable=True)
    last_read_position = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    
    session = relationship("Session", back_populates="notes")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    role = Column(String) # 'user' or 'model'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("Session", back_populates="chats")
