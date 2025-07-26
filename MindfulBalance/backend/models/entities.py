# entities.py
from datetime import datetime

class User:
    def __init__(self, username: str, password_hash: str):
        self.username = username
        self.password_hash = password_hash

class MoodEntry:
    def __init__(self, user_id: int, mood: str, tags: list[str], timestamp: datetime):
        self.user_id = user_id
        self.mood = mood
        self.tags = tags
        self.timestamp = timestamp

class JournalEntry:
    def __init__(self, user_id: int, content: str, timestamp: datetime):
        self.user_id = user_id
        self.content = content
        self.timestamp = timestamp

class Recommendation:
    def __init__(self, mood_pattern: str, strategy: str):
        self.mood_pattern = mood_pattern
        self.strategy = strategy