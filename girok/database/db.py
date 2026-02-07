"""
SQLite database management for Girok.
Handles connection, schema creation, and core database operations.
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional

from girok.constants import APP_DIR

# Database file path
DB_PATH = os.path.join(APP_DIR, "girok.db")


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize the database schema if it doesn't exist."""
    # Ensure app directory exists
    if not os.path.isdir(APP_DIR):
        os.makedirs(APP_DIR)

    with get_db() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Categories table (hierarchical via parent_id)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                parent_id INTEGER,
                name TEXT NOT NULL,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE,
                UNIQUE(user_id, parent_id, name)
            )
        """)

        # Create index for faster category lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_categories_user_parent 
            ON categories(user_id, parent_id)
        """)

        # Events/Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER,
                name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                start_time TEXT,
                end_date TEXT,
                end_time TEXT,
                repetition_type TEXT,
                repetition_end_date TEXT,
                priority TEXT,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        """)

        # Create index for faster event lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_user 
            ON events(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_dates 
            ON events(start_date, end_date)
        """)

        # Event-Tag junction table (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_tags (
                event_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                PRIMARY KEY (event_id, tag),
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        """)


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email address."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_user(email: str, password_hash: str) -> int:
    """Create a new user and return their ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )
        return cursor.lastrowid
