# business_layer/models/mood.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Mood:
    """Mood model representing a mood entry."""
    
    mood_id: Optional[int] = None
    user_id: int = 0
    mood_level: int = 5  # 1-10 scale
    notes: str = ""
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate mood data after initialization."""
        if self.notes:
            self.notes = self.notes.strip()
        
        # Ensure mood_level is within valid range
        if self.mood_level < 1:
            self.mood_level = 1
        elif self.mood_level > 10:
            self.mood_level = 10
    
    @property
    def mood_description(self) -> str:
        """Get mood description based on level."""
        mood_descriptions = {
            1: "Terrible",
            2: "Very Bad",
            3: "Bad", 
            4: "Poor",
            5: "Okay",
            6: "Fair",
            7: "Good",
            8: "Very Good",
            9: "Great",
            10: "Excellent"
        }
        return mood_descriptions.get(self.mood_level, "Unknown")
    
    @property
    def mood_emoji(self) -> str:
        """Get emoji representation of mood."""
        mood_emojis = {
            1: "😢", 2: "😞", 3: "🙁", 4: "😕", 5: "😐",
            6: "🙂", 7: "😊", 8: "😄", 9: "😁", 10: "🤩"
        }
        return mood_emojis.get(self.mood_level, "😐")
    
    def to_dict(self) -> dict:
        """Convert mood to dictionary."""
        return {
            'mood_id': self.mood_id,
            'user_id': self.user_id,
            'mood_level': self.mood_level,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Mood':
        """Create Mood instance from dictionary."""
        mood = cls(
            mood_id=data.get('mood_id'),
            user_id=data.get('user_id', 0),
            mood_level=data.get('mood_level', 5),
            notes=data.get('notes', '')
        )
        
        # Handle datetime conversion
        if data.get('timestamp'):
            if isinstance(data['timestamp'], str):
                try:
                    mood.timestamp = datetime.fromisoformat(data['timestamp'])
                except ValueError:
                    # Handle SQLite datetime format
                    mood.timestamp = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
            elif isinstance(data['timestamp'], datetime):
                mood.timestamp = data['timestamp']
        
        return mood