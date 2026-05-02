from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class NoteCreate(BaseModel):
    video_url: str
    session_id: int

class NoteResponse(BaseModel):
    id: int
    video_id: str
    video_url: str
    title: Optional[str]
    markdown_notes: str
    created_at: datetime
    session_id: int

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatCreate(BaseModel):
    session_id: int
    message: str

class ChatResponse(ChatMessage):
    id: int
    session_id: int
    created_at: datetime
    class Config:
        orm_mode = True

class SessionBase(BaseModel):
    title: Optional[str] = "New Session"

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    user_id: int
    created_at: datetime
    notes: List[NoteResponse] = []
    chats: List[ChatResponse] = []

    class Config:
        orm_mode = True
