import sqlite3
import datetime
from typing import List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_name="bmi_data.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            conn.commit()

    def add_user(self, name: str) -> bool:
        """Adds a new user. Returns True if successful, False if user already exists."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_users(self) -> List[str]:
        """Returns a list of all user names."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM users")
            return [row[0] for row in cursor.fetchall()]

    def get_user_id(self, name: str) -> Optional[int]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def add_record(self, user_name: str, weight: float, height: float, bmi: float, category: str):
        user_id = self.get_user_id(user_name)
        if user_id is None:
            raise ValueError("User not found")
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO records (user_id, date, weight, height, bmi, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, date_str, weight, height, bmi, category))
            conn.commit()

    def get_history(self, user_name: str) -> List[Tuple]:
        user_id = self.get_user_id(user_name)
        if user_id is None:
            return []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, weight, height, bmi, category 
                FROM records 
                WHERE user_id = ? 
                ORDER BY date ASC
            """, (user_id,))
            return cursor.fetchall()
