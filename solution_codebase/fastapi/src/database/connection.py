# database/connection.py - Database connection utilities
import sqlite3
import os

# Database file path (relative to the project root)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "time_deposits.db")

def get_database_connection():
    """
    Get a connection to the SQLite database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn

def init_database():
    """
    Initialize the database with schema if it doesn't exist.
    """
    if not os.path.exists(DATABASE_PATH):
        print("Database not found. Please run the schema setup first.")
        return False
    return True
