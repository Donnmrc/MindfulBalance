import sys
import os

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from business_layer.models.user import User
from data_layer.database.connection import DatabaseConnection
from typing import Tuple, Optional

class UserService:
    def __init__(self):
        self.db = DatabaseConnection()

    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str, Optional['User']]:
        """Register a new user."""
        try:
            if not username or not email or not password:
                return False, "All fields are required", None

            if len(username) < 3:
                return False, "Username must be at least 3 characters", None

            if len(password) < 6:
                return False, "Password must be at least 6 characters", None

            if "@" not in email or "." not in email:
                return False, "Invalid email address", None

            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return False, "Username or email already exists", None

            # Store password directly (temporarily, until we implement proper hashing)
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()

            # Retrieve the user_id of the newly inserted user
            cursor.execute("SELECT last_insert_rowid()")
            user_id = cursor.fetchone()[0]

            user = User(user_id=user_id, username=username, email=email)
            return True, "User registered successfully", user
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None
        finally:
            if conn:
                conn.close()

    def authenticate_user(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional['User']]:
        """Authenticate user login."""
        try:
            print(f"Attempting to authenticate: {username_or_email}")  # Debug log

            if not username_or_email or not password:
                return False, "Please enter both username/email and password", None

            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Query the database
            cursor.execute("""
                SELECT user_id, username, email, password
                FROM users
                WHERE username = ? OR email = ?
            """, (username_or_email, username_or_email))
            row = cursor.fetchone()

            if row:
                user_id, username, email, stored_password = row
                # If you implement password hashing, use self._verify_password
                if password == stored_password:
                    user = User(user_id=user_id, username=username, email=email)
                    return True, "Authentication successful", user
                else:
                    return False, "Incorrect password", None
            else:
                return False, "User not found", None
        except Exception as e:
            return False, f"An error occurred during authentication: {str(e)}", None
        finally:
            if conn:
                conn.close()