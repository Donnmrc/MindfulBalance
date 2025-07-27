# data_layer/database/connection.py
import sqlite3
import os

class DatabaseConnection:
    """Handles SQLite database connections and basic operations."""
    
    def __init__(self):
        # Create data directory in the project root
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.data_dir = os.path.join(self.project_root, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Set database file path
        self.db_path = os.path.join(self.data_dir, "mindfulbalance.db")
        
        # Initialize database if it doesn't exist
        self.initialize_database()

    def get_connection(self):
        """Create a connection to the SQLite database with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn

    def initialize_database(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create mood_logs table (matching your DAO expectations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mood_logs (
                mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood_level INTEGER NOT NULL CHECK(mood_level BETWEEN 1 AND 10),
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        # Create journal_entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        # Create coping_strategies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coping_strategies (
                strategy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT
            )
        """)

        conn.commit()
        conn.close()

    def test_connection(self):
        """Test the database connection and print the location"""
        try:
            conn = self.get_connection()
            print(f"Successfully connected to database at: {self.db_path}")
            conn.close()
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False