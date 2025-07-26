# business_layer/models/user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """User model representing a user entity."""
    
    user_id: Optional[int] = None
    username: str = ""
    email: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate user data after initialization."""
        if self.username:
            self.username = self.username.strip()
        if self.email:
            self.email = self.email.strip().lower()
    
    @property
    def is_valid_email(self) -> bool:
        """Check if email format is valid."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.email))
    
    @property
    def is_valid_username(self) -> bool:
        """Check if username is valid (3-20 chars, alphanumeric + underscore)."""
        import re
        if not self.username or len(self.username) < 3 or len(self.username) > 20:
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, self.username))
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create User instance from dictionary."""
        user = cls(
            user_id=data.get('user_id'),
            username=data.get('username', ''),
            email=data.get('email', '')
        )
        
        # Handle datetime conversion
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                try:
                    user.created_at = datetime.fromisoformat(data['created_at'])
                except ValueError:
                    # Handle SQLite datetime format
                    user.created_at = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
            elif isinstance(data['created_at'], datetime):
                user.created_at = data['created_at']
        
        return user