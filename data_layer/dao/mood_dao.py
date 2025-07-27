# data_layer/dao/mood_dao.py
from typing import Optional, Dict, Any, List
from data_layer.database.connection import DatabaseConnection
import sqlite3
from datetime import datetime, date

class MoodDAO:
    """Data Access Object for Mood operations."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_mood_entry(self, user_id: int, mood_level: int, notes: str = "") -> Optional[int]:
        """
        Create a new mood entry in the database.
        
        Args:
            user_id: User ID
            mood_level: Mood level (1-10)
            notes: Optional notes about the mood
            
        Returns:
            Mood ID if successful, None if failed
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO mood_logs (user_id, mood_level, notes) VALUES (?, ?, ?)",
                    (user_id, mood_level, notes)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def get_mood_by_id(self, mood_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve mood entry by ID.
        
        Args:
            mood_id: Mood ID to search for
            
        Returns:
            Mood dictionary if found, None otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT mood_id, user_id, mood_level, notes, timestamp FROM mood_logs WHERE mood_id = ?",
                    (mood_id,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'mood_id': row['mood_id'],
                        'user_id': row['user_id'],
                        'mood_level': row['mood_level'],
                        'notes': row['notes'],
                        'timestamp': row['timestamp']
                    }
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def get_user_moods(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get mood entries for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of entries to return
            
        Returns:
            List of mood dictionaries
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT mood_id, user_id, mood_level, notes, timestamp 
                       FROM mood_logs 
                       WHERE user_id = ? 
                       ORDER BY timestamp DESC 
                       LIMIT ?""",
                    (user_id, limit)
                )
                rows = cursor.fetchall()
                return [{
                    'mood_id': row['mood_id'],
                    'user_id': row['user_id'],
                    'mood_level': row['mood_level'],
                    'notes': row['notes'],
                    'timestamp': row['timestamp']
                } for row in rows]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_today_mood(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get today's mood entry for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Mood dictionary if found, None otherwise
        """
        try:
            today = date.today().strftime('%Y-%m-%d')
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT mood_id, user_id, mood_level, notes, timestamp 
                       FROM mood_logs 
                       WHERE user_id = ? AND date(timestamp) = ?
                       ORDER BY timestamp DESC 
                       LIMIT 1""",
                    (user_id, today)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'mood_id': row['mood_id'],
                        'user_id': row['user_id'],
                        'mood_level': row['mood_level'],
                        'notes': row['notes'],
                        'timestamp': row['timestamp']
                    }
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def update_mood_entry(self, mood_id: int, mood_level: int, notes: str = "") -> bool:
        """
        Update an existing mood entry.
        
        Args:
            mood_id: Mood ID to update
            mood_level: New mood level
            notes: Updated notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE mood_logs SET mood_level = ?, notes = ? WHERE mood_id = ?",
                    (mood_level, notes, mood_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def delete_mood_entry(self, mood_id: int) -> bool:
        """
        Delete a mood entry.
        
        Args:
            mood_id: Mood ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mood_logs WHERE mood_id = ?", (mood_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_mood_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get mood statistics for a user over a specified period.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with mood statistics
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT 
                        COUNT(*) as total_entries,
                        AVG(mood_level) as average_mood,
                        MIN(mood_level) as lowest_mood,
                        MAX(mood_level) as highest_mood
                       FROM mood_logs 
                       WHERE user_id = ? AND datetime(timestamp) >= datetime('now', '-{} days')""".format(days),
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'total_entries': row['total_entries'],
                        'average_mood': round(row['average_mood'], 1) if row['average_mood'] else 0,
                        'lowest_mood': row['lowest_mood'],
                        'highest_mood': row['highest_mood']
                    }
                return {
                    'total_entries': 0,
                    'average_mood': 0,
                    'lowest_mood': 0,
                    'highest_mood': 0
                }
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {
                'total_entries': 0,
                'average_mood': 0,
                'lowest_mood': 0,
                'highest_mood': 0
            }