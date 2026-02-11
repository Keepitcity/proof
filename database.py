"""
User Authentication and Tracking Database for Proof by Aerial Canvas
Handles user management, waitlist, and per-user statistics.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List, Tuple


class UserDatabase:
    """SQLite database for user authentication and tracking"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'users.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table - stores authenticated users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                picture_url TEXT,
                is_team_member BOOLEAN DEFAULT FALSE,
                is_waitlist BOOLEAN DEFAULT FALSE,
                first_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0
            )
        ''')

        # User stats table - aggregate stats per user
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                total_videos_analyzed INTEGER DEFAULT 0,
                total_photos_analyzed INTEGER DEFAULT 0,
                total_clips_sorted INTEGER DEFAULT 0,
                total_issues_found INTEGER DEFAULT 0,
                total_time_saved_seconds INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Waitlist table - for non-team signups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waitlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def create_user(self, email: str, name: str = None, picture_url: str = None) -> int:
        """Create a new user and return their ID"""
        is_team_member = email.lower().endswith('@aerialcanvas.com')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (email, name, picture_url, is_team_member, last_login, login_count)
            VALUES (?, ?, ?, ?, datetime('now'), 1)
        ''', (email, name, picture_url, is_team_member))
        user_id = cursor.lastrowid

        # Initialize user stats
        cursor.execute('''
            INSERT INTO user_stats (user_id) VALUES (?)
        ''', (user_id,))

        conn.commit()
        conn.close()
        return user_id

    def update_user_login(self, email: str, name: str = None, picture_url: str = None) -> Dict:
        """Update user's last login and increment login count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update login info
        if name and picture_url:
            cursor.execute('''
                UPDATE users
                SET last_login = datetime('now'),
                    login_count = login_count + 1,
                    name = ?,
                    picture_url = ?
                WHERE email = ?
            ''', (name, picture_url, email))
        else:
            cursor.execute('''
                UPDATE users
                SET last_login = datetime('now'),
                    login_count = login_count + 1
                WHERE email = ?
            ''', (email,))

        conn.commit()
        conn.close()

        return self.get_user_by_email(email)

    def get_or_create_user(self, email: str, name: str = None, picture_url: str = None) -> Tuple[Dict, bool]:
        """Get existing user or create new one. Returns (user_dict, is_new_user)"""
        user = self.get_user_by_email(email)
        if user:
            # Update login info
            user = self.update_user_login(email, name, picture_url)
            return user, False
        else:
            # Create new user
            user_id = self.create_user(email, name, picture_url)
            user = self.get_user_by_email(email)
            return user, True

    def is_team_member(self, email: str) -> bool:
        """Check if email is an Aerial Canvas team member"""
        return email.lower().endswith('@aerialcanvas.com')

    # Waitlist management
    def add_to_waitlist(self, email: str, name: str = None, notes: str = None) -> bool:
        """Add user to waitlist. Returns True if added, False if already exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO waitlist (email, name, notes)
                VALUES (?, ?, ?)
            ''', (email, name, notes))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def is_on_waitlist(self, email: str) -> bool:
        """Check if email is on the waitlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM waitlist WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def get_waitlist(self) -> List[Dict]:
        """Get all waitlist entries"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM waitlist ORDER BY signup_date DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # User stats management
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get stats for a specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def increment_user_stat(self, user_id: int, stat_name: str, amount: int = 1):
        """Increment a user's stat by amount"""
        valid_stats = [
            'total_videos_analyzed',
            'total_photos_analyzed',
            'total_clips_sorted',
            'total_issues_found',
            'total_time_saved_seconds'
        ]
        if stat_name not in valid_stats:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE user_stats
            SET {stat_name} = {stat_name} + ?
            WHERE user_id = ?
        ''', (amount, user_id))
        conn.commit()
        conn.close()

    def update_user_stats(self, user_id: int, videos: int = 0, photos: int = 0,
                          clips: int = 0, issues: int = 0, time_saved: int = 0):
        """Update multiple stats at once"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_stats
            SET total_videos_analyzed = total_videos_analyzed + ?,
                total_photos_analyzed = total_photos_analyzed + ?,
                total_clips_sorted = total_clips_sorted + ?,
                total_issues_found = total_issues_found + ?,
                total_time_saved_seconds = total_time_saved_seconds + ?
            WHERE user_id = ?
        ''', (videos, photos, clips, issues, time_saved, user_id))
        conn.commit()
        conn.close()

    # Aggregate stats
    def get_total_users(self) -> int:
        """Get total number of users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_total_team_members(self) -> int:
        """Get number of team members"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_team_member = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_aggregate_stats(self) -> Dict:
        """Get aggregate stats across all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                SUM(total_videos_analyzed) as videos,
                SUM(total_photos_analyzed) as photos,
                SUM(total_clips_sorted) as clips,
                SUM(total_issues_found) as issues,
                SUM(total_time_saved_seconds) as time_saved
            FROM user_stats
        ''')
        row = cursor.fetchone()
        conn.close()

        return {
            'total_videos': row[0] or 0,
            'total_photos': row[1] or 0,
            'total_clips': row[2] or 0,
            'total_issues': row[3] or 0,
            'total_time_saved_seconds': row[4] or 0
        }


# Global instance
user_db = UserDatabase()
