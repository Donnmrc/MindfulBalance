# business_layer/services/mood_service.py
from typing import Optional, Tuple, List
from business_layer.models.mood import Mood
from data_layer.dao.mood_dao import MoodDAO
from datetime import datetime

class MoodService:
    """Business logic for mood operations."""
    
    def __init__(self):
        self.mood_dao = MoodDAO()
    
    def log_mood(self, user_id: int, mood_level: int, notes: str = "") -> Tuple[bool, str, Optional[Mood]]:
        """
        Log a new mood entry.
        
        Args:
            user_id: User ID
            mood_level: Mood level (1-10)
            notes: Optional notes about the mood
            
        Returns:
            Tuple of (success, message, mood_object)
        """
        # Validate input
        if not user_id or user_id <= 0:
            return False, "Invalid user ID", None
        
        if mood_level < 1 or mood_level > 10:
            return False, "Mood level must be between 1 and 10", None
        
        # Create mood entry
        mood_id = self.mood_dao.create_mood_entry(user_id, mood_level, notes)
        
        if mood_id:
            # Create mood object
            mood = Mood(
                mood_id=mood_id,
                user_id=user_id,
                mood_level=mood_level,
                notes=notes,
                timestamp=datetime.now()
            )
            return True, "Mood logged successfully", mood
        else:
            return False, "Failed to log mood. Please try again.", None
    
    def get_today_mood(self, user_id: int) -> Optional[Mood]:
        """
        Get today's mood for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Mood object if found, None otherwise
        """
        mood_data = self.mood_dao.get_today_mood(user_id)
        if mood_data:
            return Mood.from_dict(mood_data)
        return None
    
    def update_mood(self, mood_id: int, mood_level: int, notes: str = "") -> Tuple[bool, str]:
        """
        Update an existing mood entry.
        
        Args:
            mood_id: Mood ID to update
            mood_level: New mood level (1-10)
            notes: Updated notes
            
        Returns:
            Tuple of (success, message)
        """
        # Validate input
        if mood_level < 1 or mood_level > 10:
            return False, "Mood level must be between 1 and 10"
        
        success = self.mood_dao.update_mood_entry(mood_id, mood_level, notes)
        
        if success:
            return True, "Mood updated successfully"
        else:
            return False, "Failed to update mood. Please try again."
    
    def get_user_mood_history(self, user_id: int, limit: int = 10) -> List[Mood]:
        """
        Get mood history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of entries to return
            
        Returns:
            List of Mood objects
        """
        mood_data_list = self.mood_dao.get_user_moods(user_id, limit)
        return [Mood.from_dict(mood_data) for mood_data in mood_data_list]
    
    def get_mood_statistics(self, user_id: int, days: int = 30) -> dict:
        """
        Get mood statistics for a user.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with mood statistics
        """
        stats = self.mood_dao.get_mood_statistics(user_id, days)
        
        # Add interpretive information
        if stats['average_mood'] > 0:
            if stats['average_mood'] >= 8:
                stats['mood_trend'] = "Excellent"
            elif stats['average_mood'] >= 7:
                stats['mood_trend'] = "Good"
            elif stats['average_mood'] >= 5:
                stats['mood_trend'] = "Fair"
            elif stats['average_mood'] >= 3:
                stats['mood_trend'] = "Poor"
            else:
                stats['mood_trend'] = "Concerning"
        else:
            stats['mood_trend'] = "No data"
        
        return stats
    
    def get_mood_recommendations(self, user_id: int) -> List[str]:
        """
        Get mood-based recommendations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Get recent mood
        today_mood = self.get_today_mood(user_id)
        recent_moods = self.get_user_mood_history(user_id, 7)  # Last 7 entries
        
        if today_mood:
            if today_mood.mood_level <= 3:
                recommendations.extend([
                    "Consider reaching out to a trusted friend or family member",
                    "Try some deep breathing exercises or meditation",
                    "Take a short walk outside if possible",
                    "Consider speaking with a mental health professional"
                ])
            elif today_mood.mood_level <= 5:
                recommendations.extend([
                    "Try journaling about your feelings",
                    "Listen to some uplifting music",
                    "Practice gratitude by listing three things you're thankful for",
                    "Consider doing some light exercise"
                ])
            elif today_mood.mood_level >= 8:
                recommendations.extend([
                    "Great mood! Consider sharing your positivity with others",
                    "This is a good time to tackle challenging tasks",
                    "Reflect on what's contributing to your good mood",
                    "Consider planning something fun for the future"
                ])
        
        # Add general recommendations if no specific ones
        if not recommendations:
            recommendations.extend([
                "Remember to practice self-care",
                "Stay connected with loved ones",
                "Maintain a regular sleep schedule",
                "Consider keeping a daily mood journal"
            ])
        
        return recommendations[:3]  # Return top 3 recommendations