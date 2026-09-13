import json
import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# CORS configuration - MUST be placed before any route definitions
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://emotranotepad.vercel.app",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "notes.json")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

class UserAuth(BaseModel):
    username: str
    password: str

class NoteItem(BaseModel):
    title: str
    text: str
    emotion: str = "Neutral"
    image_base64: Optional[str] = None

def read_json(path):
    if not os.path.exists(path):
        return [] if path == DATA_FILE else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return [] if path == DATA_FILE else {}

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.post("/api/register")
def register(user: UserAuth):
    users = read_json(USERS_FILE)
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    users[user.username] = user.password
    write_json(USERS_FILE, users)
    return {"message": "User registered successfully"}

@app.post("/api/login")
def login(user: UserAuth):
    users = read_json(USERS_FILE)
    if users.get(user.username) != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"token": user.username}

@app.get("/api/notes")
def get_notes(x_user: Optional[str] = Header(None)):
    if not x_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    all_notes = read_json(DATA_FILE)
    user_notes = [n for n in all_notes if n.get("user") == x_user]
    return user_notes

@app.post("/api/notes")
def create_note(note: NoteItem, x_user: Optional[str] = Header(None)):
    if not x_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not note.text.strip():
        raise HTTPException(status_code=400, detail="Note text is required")
    
    all_notes = read_json(DATA_FILE)
    new_entry = {
        "id": int(time.time() * 1000),
        "user": x_user,
        "title": note.title.strip() or "Untitled Note",
        "date": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
        "text": note.text.strip(),
        "emotion": note.emotion,
        "image": note.image_base64
    }
    all_notes.insert(0, new_entry)
    write_json(DATA_FILE, all_notes)
    return new_entry

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int, x_user: Optional[str] = Header(None)):
    if not x_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    all_notes = read_json(DATA_FILE)
    filtered_notes = [n for n in all_notes if not (n.get("id") == note_id and n.get("user") == x_user)]
    write_json(DATA_FILE, filtered_notes)
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
