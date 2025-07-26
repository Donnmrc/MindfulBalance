# data_layer/database/connection.py
import sqlite3
import os
from contextlib import contextmanager
from typing import Optional

class DatabaseConnection:
    """Handles SQLite database connections and basic operations."""
    
    def __init__(self, db_path: str = "data_layer/database/mental_health_tracker.db"):
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def initialize_database(self):
        """Initialize database with schema."""
        schema = """
        BEGIN TRANSACTION;
        DROP TABLE IF EXISTS "users";
        CREATE TABLE IF NOT EXISTS "users" (
            "user_id"	INTEGER,
            "username"	TEXT NOT NULL UNIQUE,
            "email"	TEXT NOT NULL UNIQUE,
            "password"	TEXT NOT NULL,
            "created_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY("user_id" AUTOINCREMENT)
        );
        DROP TABLE IF EXISTS "journal_entries";
        CREATE TABLE IF NOT EXISTS "journal_entries" (
            "entry_id"	INTEGER,
            "user_id"	INTEGER NOT NULL,
            "content"	TEXT NOT NULL,
            "timestamp"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
            PRIMARY KEY("entry_id" AUTOINCREMENT)
        );
        DROP TABLE IF EXISTS "mood_logs";
        CREATE TABLE IF NOT EXISTS "mood_logs" (
            "mood_id"	INTEGER,
            "user_id"	INTEGER NOT NULL,
            "mood_level"	INTEGER NOT NULL CHECK("mood_level" BETWEEN 1 AND 10),
            "notes"	TEXT,
            "timestamp"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY("mood_id" AUTOINCREMENT),
            FOREIGN KEY("user_id") REFERENCES "users"("user_id")
        );
        DROP TABLE IF EXISTS "coping_strategies";
        CREATE TABLE IF NOT EXISTS "coping_strategies" (
            "strategy_id"	INTEGER,
            "title"	TEXT NOT NULL,
            "description"	TEXT NOT NULL,
            "category"	TEXT,
            PRIMARY KEY("strategy_id" AUTOINCREMENT)
        );
        COMMIT;
        """
        
        with self.get_connection() as conn:
            conn.executescript(schema)
            conn.commit()