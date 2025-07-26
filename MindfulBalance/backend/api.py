# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
import bcrypt
from pathlib import Path
import random
import httpx

DB_PATH = Path(__file__).parent / "MindfulBalance.db"
app = FastAPI()

TIPS = [
    "Take a deep breath. You’ve survived 100% of your worst days.",
    "Write down 3 things you're grateful for.",
    "Go for a short walk to refresh your mind.",
    "Disconnect for 30 minutes and do something offline.",
    "Talk to a friend or loved one today.",
]

@app.get("/resources")
def get_tip():
    try:
        response = httpx.get("https://zenquotes.io/api/random", timeout=5)
        data = response.json()
        quote = data[0]["q"] + " — " + data[0]["a"]
        return {"tip": quote}
    except Exception:
        return {"tip": random.choice(TIPS)}

class RegisterRequest(BaseModel):
    username: str
    password: str

class MoodRequest(BaseModel):
    username: str
    mood: str
    tags: list[str]

class JournalRequest(BaseModel):
    username: str
    content: str

def get_connection():
    return sqlite3.connect(DB_PATH)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def get_user_id(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    raise Exception("User not found")

@app.on_event("startup")
def startup():
    from backend.database import initialize_database
    initialize_database()

@app.post("/register")
def register_user(req: RegisterRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = hash_password(req.password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (req.username, hashed))
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

@app.post("/login")
def login_user(req: RegisterRequest):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (req.username,))
    result = cursor.fetchone()
    conn.close()

    if result and verify_password(req.password, result[0]):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/mood")
def log_mood(req: MoodRequest):
    user_id = get_user_id(req.username)
    timestamp = datetime.now().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    tags_str = ",".join(req.tags) if req.tags else ""
    cursor.execute(
        "INSERT INTO mood_entries (user_id, mood, tags, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, req.mood, tags_str, timestamp)
    )
    conn.commit()
    conn.close()
    return {"message": "Mood logged"}

@app.post("/journal")
def save_journal(req: JournalRequest):
    user_id = get_user_id(req.username)
    timestamp = datetime.now().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO journal_entries (user_id, content, timestamp) VALUES (?, ?, ?)",
        (user_id, req.content, timestamp)
    )
    conn.commit()
    conn.close()
    return {"message": "Journal entry saved"}

@app.get("/recommendation")
def get_recommendation(username: str):
    user_id = get_user_id(username)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT mood FROM mood_entries WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5",
        (user_id,)
    )
    moods = [row[0] for row in cursor.fetchall()]
    conn.close()

    if moods.count("stressed") >= 3:
        return {"strategy": "Try a breathing exercise or journaling prompt."}
    elif moods.count("sad") >= 3:
        return {"strategy": "Listen to uplifting music or talk to a friend."}
    else:
        return {"strategy": "Keep tracking your mood. You're doing great!"}

@app.get("/stats")
def get_stats(username: str):
    user_id = get_user_id(username)
    conn = get_connection()
    cursor = conn.cursor()

    # Today's Mood
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT mood FROM mood_entries WHERE user_id = ? AND DATE(timestamp) = ? ORDER BY timestamp DESC LIMIT 1",
        (user_id, today)
    )
    row = cursor.fetchone()
    today_mood = row[0] if row else None

    # Mood Streak
    cursor.execute(
        "SELECT DISTINCT DATE(timestamp) FROM mood_entries WHERE user_id = ? ORDER BY DATE(timestamp) DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    streak = 0
    if rows:
        today_date = datetime.now().date()
        for r in rows:
            entry_date = datetime.strptime(r[0], "%Y-%m-%d").date()
            if entry_date == today_date - timedelta(days=streak):
                streak += 1
            else:
                break

    # Journal Count
    cursor.execute(
        "SELECT COUNT(*) FROM journal_entries WHERE user_id = ?",
        (user_id,)
    )
    journal_count = cursor.fetchone()[0]

    conn.close()
    return {
        "today_mood": today_mood,
        "streak": streak,
        "journal_count": journal_count
    }

@app.get("/latest_journal")
def latest_journal(username: str):
    user_id = get_user_id(username)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT content, timestamp 
        FROM journal_entries 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
        """,
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "content": row[0],
            "timestamp": row[1]
        }
    return {
        "content": "",
        "timestamp": None
    }

from datetime import datetime, timedelta

@app.get("/streak")
def get_streak(username: str):
    user_id = get_user_id(username)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT DATE(timestamp) FROM mood_entries WHERE user_id = ? ORDER BY DATE(timestamp) DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return {"streak": 0}
    streak = 0
    today = datetime.now().date()
    for row in rows:
        entry_date = datetime.strptime(row[0], "%Y-%m-%d").date()
        if entry_date == today - timedelta(days=streak):
            streak += 1
        else:
            break
    return {"streak": streak}