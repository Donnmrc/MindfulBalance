# database.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "MindfulBalance.db"

def get_connection():
    """Get a database connection with proper error handling"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

def initialize_database():
    """Initialize the database with all required tables"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create journal_entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create mood_logs table  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mood_logs (
                mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood_level INTEGER NOT NULL CHECK(mood_level BETWEEN 1 AND 10),
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create coping_strategies table (matches your SQL schema)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coping_strategies (
                strategy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT
            )
        """)
        
        # Add default coping strategies if table is empty
        cursor.execute("SELECT COUNT(*) FROM coping_strategies")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO coping_strategies (title, description, category) VALUES (?, ?, ?)",
                [
                    ("Deep Breathing", "Inhale for 4 seconds, hold for 4, exhale for 6", "Anxiety"),
                    ("Gratitude Journal", "Write 3 things you're grateful for", "Depression"),
                    ("Nature Walk", "Spend 10 minutes outside", "Stress"),
                    ("Progressive Muscle Relaxation", "Tense and relax each muscle group", "Stress"),
                    ("Mindful Meditation", "Focus on your breath for 5-10 minutes", "Anxiety"),
                    ("Positive Affirmations", "Repeat encouraging statements to yourself", "Depression")
                ]
            )
        
        conn.commit()
        print(f"Database initialized successfully at: {DB_PATH.absolute()}")
        
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def test_connection():
    """Test if the database connection is working"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()[0]
        print(f"SQLite connection successful! Version: {version}")
        print(f"Database location: {DB_PATH.absolute()}")
        conn.close()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

# Utility functions for database operations
def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
            return cursor.lastrowid if query.strip().upper().startswith('INSERT') else cursor.rowcount
        else:
            return cursor.fetchall()
            
    except sqlite3.Error as e:
        print(f"Query execution error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

# Initialize database when module is imported
if __name__ == "__main__":
    initialize_database()
    test_connection()
