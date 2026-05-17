from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import models
import schemas
import auth
import database
from app import get_video_id, get_video_details, extract_chapters_from_text, get_chapters_from_comments, get_transcript, generate_notes
from jose import JWTError, jwt
import google.generativeai as genai

# Configure genai with API Key if available
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Warning in prod: dropping all is destructive
# For dev we create_all, but we need to run external python script to reset db:
# We'll just rely on create_all, user should recreate their local db

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="YT Note Maker API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/api/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Sessions API ---

@app.post("/api/sessions/", response_model=schemas.SessionResponse)
def create_session(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    new_session = models.Session(user_id=current_user.id, title="New Session")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@app.get("/api/sessions/", response_model=list[schemas.SessionResponse])
def get_sessions(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Session).filter(models.Session.user_id == current_user.id).order_by(models.Session.created_at.desc()).all()

@app.get("/api/sessions/{session_id}", response_model=schemas.SessionResponse)
def get_session(session_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    session_obj = db.query(models.Session).filter(models.Session.id == session_id, models.Session.user_id == current_user.id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_obj


# --- Notes API ---

@app.post("/api/notes/generate", response_model=schemas.NoteResponse)
def create_note(request: schemas.NoteCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    session_obj = db.query(models.Session).filter(models.Session.id == request.session_id, models.Session.user_id == current_user.id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        video_id = get_video_id(request.video_url)
        snippet = get_video_details(video_id)
        description = snippet.get('description', '')
        title = snippet.get('title', '')
        
        # If the session title is still the default
        if session_obj.title == "New Session" and title:
            session_obj.title = title
            db.commit()
            
        chapters = extract_chapters_from_text(description)
        if not chapters:
            chapters = get_chapters_from_comments(video_id)
            
        transcript = get_transcript(video_id)
        markdown_notes = generate_notes(transcript, chapters)
        
        new_note = models.Note(
            video_id=video_id,
            video_url=request.video_url,
            title=title,
            markdown_notes=markdown_notes,
            transcript=transcript,
            session_id=session_obj.id
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return new_note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes/", response_model=list[schemas.NoteResponse])
def get_notes(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    sessions = db.query(models.Session).filter(models.Session.user_id == current_user.id).all()
    session_ids = [s.id for s in sessions]
    return db.query(models.Note).filter(models.Note.session_id.in_(session_ids)).order_by(models.Note.created_at.desc()).all()

@app.patch("/api/notes/{note_id}/bookmark", response_model=schemas.NoteResponse)
def update_bookmark(note_id: int, position: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Verify the session belongs to the user
    session_obj = db.query(models.Session).filter(models.Session.id == note.session_id, models.Session.user_id == current_user.id).first()
    if not session_obj:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    note.last_read_position = position
    db.commit()
    db.refresh(note)
    return note

@app.delete("/api/notes/{note_id}/bookmark", response_model=schemas.NoteResponse)
def delete_bookmark(note_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    session_obj = db.query(models.Session).filter(models.Session.id == note.session_id, models.Session.user_id == current_user.id).first()
    if not session_obj:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    note.last_read_position = 0
    db.commit()
    db.refresh(note)
    return note


# --- Chat API ---

@app.post("/api/chat", response_model=schemas.ChatResponse)
def execute_chat(request: schemas.ChatCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    session_obj = db.query(models.Session).filter(models.Session.id == request.session_id, models.Session.user_id == current_user.id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
        
    history = db.query(models.ChatHistory).filter(models.ChatHistory.session_id == session_obj.id).order_by(models.ChatHistory.id.asc()).all()
    
    formatted_history = []
    
    # Always send all session transcripts joined as context to start the conversation memory
    notes = db.query(models.Note).filter(models.Note.session_id == session_obj.id).all()
    combined_transcripts = "\n\n".join([n.transcript for n in notes if n.transcript])

    # Start history with the context only if history is empty, otherwise just load DB history
    if not history:
        formatted_history.append({
            "role": "user",
            "parts": [{"text": f"Here is the context/transcript from all videos in this session:\n{combined_transcripts}\n\nPlease help me answer questions related to it. Important Rules for Answering: 1) Use Markdown tables to organize data when comparing information or lists. 2) When explaining complex concepts, architectures, or workflows, PLEASE include a Mermaid.js diagram using ```mermaid code blocks. 3) Always provide clear, well-formatted markdown. 4) For Mermaid diagrams, ONLY use `graph TD` style flowcharts and avoid using square brackets `[` or `]` inside node text; use round brackets instead."}]
        })
        formatted_history.append({
             "role": "model",
             "parts": [{"text": "Understood! I will use Mermaid.js diagrams and Markdown tables in my responses when applicable. Let me know what questions you have about the video context."}]
        })
    else:
        # If we have history, we provide the context in a way that doesn't break the User->Model sequence
        # We'll prepend the context to the VERY FIRST user message in the history if it exists
        first_user_idx = -1
        for i, h in enumerate(history):
            if h.role == "user":
                first_user_idx = i
                break
        
        if first_user_idx != -1:
            for i, h in enumerate(history):
                content = h.content
                if i == first_user_idx:
                    content = f"CONTEXT (Videos):\n{combined_transcripts}\n\n---\n\nUSER QUESTION:\n{content}"
                formatted_history.append({"role": "user" if h.role == "user" else "model", "parts": [{"text": content}]})
        else:
            # Fallback if no history yet (though history check handles this)
            formatted_history.append({"role": "user", "parts": [{"text": f"Context: {combined_transcripts}"}]})
            formatted_history.append({"role": "model", "parts": [{"text": "Context received."}]})

    try:
        # Using gemini-flash-latest for chat to ensure compatibility and adhere to requirements
        model = genai.GenerativeModel("gemini-flash-latest") 
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(request.message)
        
        # Save both messages to DB after successful API call
        user_msg = models.ChatHistory(session_id=session_obj.id, role="user", content=request.message)
        db.add(user_msg)
        
        model_msg = models.ChatHistory(session_id=session_obj.id, role="model", content=response.text)
        db.add(model_msg)
        
        db.commit()
        db.refresh(model_msg)
        
        return model_msg
    except Exception as e:
        print(f"CHAT ERROR: {str(e)}") # Add logging for debug
        raise HTTPException(status_code=500, detail=str(e))
