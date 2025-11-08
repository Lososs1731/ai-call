# database/admin_db.py
"""
Databáze pro administrátory (uživatele)
"""

import sqlite3
import hashlib
from pathlib import Path


class AdminDB:
    def __init__(self, db_path="data/admin.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializuj databázi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ Admin DB inicializována: {self.db_path}")
    
    def hash_password(self, password):
        """Zahashuj heslo"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email=""):
        """Vytvoř nového uživatele"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            """, (username, password_hash, email))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Uživatel '{username}' vytvořen")
            return user_id
        except sqlite3.IntegrityError:
            print(f"⚠️  Uživatel '{username}' už existuje")
            conn.close()
            return None
    
    def verify_user(self, username, password):
        """Ověř přihlášení"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute("""
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def get_user(self, user_id):
        """Získej uživatele podle ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None