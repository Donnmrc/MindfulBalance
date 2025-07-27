# data_layer/dao/user_dao.py
from typing import Optional, Dict, Any
from data_layer.database.connection import DatabaseConnection
import sqlite3

class UserDAO:
    """Data Access Object for User operations."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_user(self, username: str, email: str, password: str) -> Optional[int]:
        """
        Create a new user in the database.
        
        Args:
            username: Unique username
            email: Unique email address
            password: Hashed password
            
        Returns:
            User ID if successful, None if failed
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, password)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Username or email already exists
            return None
        except sqlite3.Error:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User dictionary if found, None otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, username, email, password, created_at FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row['user_id'],
                        'username': row['username'],
                        'email': row['email'],
                        'password': row['password'],
                        'created_at': row['created_at']
                    }
                return None
        except sqlite3.Error:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User dictionary if found, None otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, username, email, password, created_at FROM users WHERE email = ?",
                    (email,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row['user_id'],
                        'username': row['username'],
                        'email': row['email'],
                        'password': row['password'],
                        'created_at': row['created_at']
                    }
                return None
        except sqlite3.Error:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User dictionary if found, None otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, username, email, created_at FROM users WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row['user_id'],
                        'username': row['username'],
                        'email': row['email'],
                        'created_at': row['created_at']
                    }
                return None
        except sqlite3.Error:
            return None
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        return self.get_user_by_username(username) is not None
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return self.get_user_by_email(email) is not None