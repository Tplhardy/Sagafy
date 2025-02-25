import sqlite3
from sqlite3 import Error
import os
from datetime import datetime

DATABASE = "workhistory.db"

def get_db_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
    
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    
    if conn is not None:
        try:
            # Create users table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create sessions table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                current_section TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # Create messages table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                section TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
            ''')
            
            conn.commit()
            print("Database initialized successfully")
        except Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

def clear_db():
    """Clear all data from the database (for testing purposes)"""
    conn = get_db_connection()
    
    if conn is not None:
        try:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM sessions")
            conn.execute("DELETE FROM users")
            conn.commit()
            print("Database cleared successfully")
        except Error as e:
            print(f"Database clear error: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")