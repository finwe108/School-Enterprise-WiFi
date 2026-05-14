import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from ..core.network_model import SavedProfile, SecurityType


class WiFiDatabase:
    """SQLite database for managing saved WiFi profiles."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            home = os.path.expanduser("~")
            db_path = os.path.join(home, ".wifi_manager", "profiles.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create saved profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ssid TEXT UNIQUE NOT NULL,
                    security TEXT NOT NULL,
                    auto_connect INTEGER DEFAULT 0,
                    last_connected TEXT,
                    connection_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create connection history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connection_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ssid TEXT NOT NULL,
                    connected_at TEXT NOT NULL,
                    disconnected_at TEXT,
                    duration_seconds INTEGER,
                    success INTEGER DEFAULT 1
                )
            """)
            
            conn.commit()

    def add_profile(self, profile: SavedProfile) -> bool:
        """Add a new saved profile."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO saved_profiles 
                    (ssid, security, auto_connect, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    profile.ssid,
                    profile.security.value,
                    1 if profile.auto_connect else 0,
                    now,
                    now
                ))
                
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error adding profile: {e}")
            return False

    def get_profile(self, ssid: str) -> Optional[SavedProfile]:
        """Get a saved profile by SSID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ssid, security, auto_connect, last_connected, connection_count
                    FROM saved_profiles
                    WHERE ssid = ?
                """, (ssid,))
                
                row = cursor.fetchone()
                if row:
                    return SavedProfile(
                        ssid=row[0],
                        security=SecurityType(row[1]),
                        auto_connect=bool(row[2]),
                        last_connected=row[3],
                        connection_count=row[4]
                    )
        except Exception as e:
            print(f"Error getting profile: {e}")
        
        return None

    def get_all_profiles(self) -> List[SavedProfile]:
        """Get all saved profiles."""
        profiles = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ssid, security, auto_connect, last_connected, connection_count
                    FROM saved_profiles
                    ORDER BY connection_count DESC
                """)
                
                for row in cursor.fetchall():
                    profiles.append(SavedProfile(
                        ssid=row[0],
                        security=SecurityType(row[1]),
                        auto_connect=bool(row[2]),
                        last_connected=row[3],
                        connection_count=row[4]
                    ))
        except Exception as e:
            print(f"Error getting profiles: {e}")
        
        return profiles

    def update_profile(self, profile: SavedProfile) -> bool:
        """Update an existing profile."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute("""
                    UPDATE saved_profiles
                    SET security = ?, auto_connect = ?, updated_at = ?
                    WHERE ssid = ?
                """, (
                    profile.security.value,
                    1 if profile.auto_connect else 0,
                    now,
                    profile.ssid
                ))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False

    def delete_profile(self, ssid: str) -> bool:
        """Delete a saved profile."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM saved_profiles WHERE ssid = ?", (ssid,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting profile: {e}")
            return False

    def record_connection(self, ssid: str, success: bool = True) -> bool:
        """Record a connection attempt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO connection_history (ssid, connected_at, success)
                    VALUES (?, ?, ?)
                """, (ssid, now, 1 if success else 0))
                
                # Update last_connected and connection_count
                if success:
                    cursor.execute("""
                        UPDATE saved_profiles
                        SET last_connected = ?, connection_count = connection_count + 1
                        WHERE ssid = ?
                    """, (now, ssid))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording connection: {e}")
            return False

    def get_auto_connect_profiles(self) -> List[SavedProfile]:
        """Get profiles set to auto-connect."""
        profiles = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ssid, security, auto_connect, last_connected, connection_count
                    FROM saved_profiles
                    WHERE auto_connect = 1
                    ORDER BY connection_count DESC
                """)
                
                for row in cursor.fetchall():
                    profiles.append(SavedProfile(
                        ssid=row[0],
                        security=SecurityType(row[1]),
                        auto_connect=bool(row[2]),
                        last_connected=row[3],
                        connection_count=row[4]
                    ))
        except Exception as e:
            print(f"Error getting auto-connect profiles: {e}")
        
        return profiles
