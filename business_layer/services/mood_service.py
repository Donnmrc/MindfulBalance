# business_layer/services/mood_service.py
from typing import Optional, Tuple, List
from business_layer.models.mood import Mood
from data_layer.dao.mood_dao import MoodDAO
from data_layer.database.connection import DatabaseConnection
from datetime import datetime, timedelta

class MoodService:
    """Business logic for mood operations."""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.mood_dao = MoodDAO()
    
    def log_mood(self, user_id: int, mood_level: int) -> Tuple[bool, str, Optional[dict]]:
        """Log a new mood entry and return updated statistics."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Insert new mood entry
            cursor.execute(
                "INSERT INTO moods (user_id, mood_level) VALUES (?, ?)",
                (user_id, mood_level)
            )
            conn.commit()
            
            # Get updated statistics
            cursor.execute("""
                SELECT COUNT(*) as total,
                       AVG(mood_level) as average
                FROM moods
                WHERE user_id = ?
            """, (user_id,))
            
            total, average = cursor.fetchone()
            
            return True, "Mood logged successfully", {
                "total_entries": total,
                "average_mood": round(float(average) if average else 0, 1)
            }
            
        except Exception as e:
            print(f"Error logging mood: {e}")
            return False, str(e), None
        finally:
            if 'conn' in locals():
                conn.close()

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
    
    def get_mood_statistics(self, user_id: int) -> dict:
        """Get mood statistics for a user."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get total entries and average mood
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_entries,
                    AVG(mood_level) as average_mood,
                    MIN(mood_level) as lowest_mood,
                    MAX(mood_level) as highest_mood
                FROM moods 
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                total_entries = row[0]
                average_mood = row[1] if row[1] is not None else 0
                return {
                    'total_entries': total_entries,
                    'average_mood': round(average_mood, 1),
                    'lowest_mood': row[2] if row[2] is not None else 0,
                    'highest_mood': row[3] if row[3] is not None else 0
                }
            return {
                'total_entries': 0,
                'average_mood': 0,
                'lowest_mood': 0,
                'highest_mood': 0
            }
            
        except Exception as e:
            print(f"Error getting mood statistics: {e}")
            return {
                'total_entries': 0,
                'average_mood': 0,
                'lowest_mood': 0,
                'highest_mood': 0
            }
        finally:
            if 'conn' in locals():
                conn.close()
    
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