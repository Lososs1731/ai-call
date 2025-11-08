# database/call_analytics.py
"""
Databáze pro analytiku hovorů
Ukládá výsledky z AI reporteru
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


class CallAnalytics:
    def __init__(self, db_path="data/call_analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializuj databázi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_sid TEXT UNIQUE NOT NULL,
            contact_phone TEXT,
            duration INTEGER DEFAULT 0,
            outcome TEXT,
            sales_score INTEGER DEFAULT 0,
            ai_summary TEXT,
            conversation TEXT,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ Call Analytics DB inicializována: {self.db_path}")
    
    def save_call(self, call_data):
        """
        Ulož hovor do databáze
        
        Args:
            call_data (dict): {
                'call_sid': str,
                'contact_phone': str,
                'duration': int,
                'outcome': str,
                'sales_score': int,
                'ai_summary': str,
                'conversation': list,
                'started_at': datetime,
                'ended_at': datetime
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Konverzaci převeď na JSON string
        conversation_json = json.dumps(call_data.get('conversation', []))
        
        try:
            cursor.execute("""
                INSERT INTO calls (
                    call_sid, contact_phone, duration, outcome,
                    sales_score, ai_summary, conversation,
                    started_at, ended_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_data.get('call_sid'),
                call_data.get('contact_phone'),
                call_data.get('duration', 0),
                call_data.get('outcome'),
                call_data.get('sales_score', 0),
                call_data.get('ai_summary'),
                conversation_json,
                call_data.get('started_at'),
                call_data.get('ended_at')
            ))
            
            call_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Hovor {call_data.get('call_sid')} uložen (ID: {call_id})")
            return call_id
            
        except sqlite3.IntegrityError:
            # Hovor už existuje - updatni ho
            print(f"⚠️  Hovor {call_data.get('call_sid')} už existuje - aktualizuji")
            
            cursor.execute("""
                UPDATE calls SET
                    contact_phone = ?,
                    duration = ?,
                    outcome = ?,
                    sales_score = ?,
                    ai_summary = ?,
                    conversation = ?,
                    ended_at = ?
                WHERE call_sid = ?
            """, (
                call_data.get('contact_phone'),
                call_data.get('duration', 0),
                call_data.get('outcome'),
                call_data.get('sales_score', 0),
                call_data.get('ai_summary'),
                conversation_json,
                call_data.get('ended_at'),
                call_data.get('call_sid')
            ))
            
            conn.commit()
            conn.close()
            return None
    
    def get_all_calls(self, limit=None):
        """Vrátí všechny hovory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM calls ORDER BY created_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        calls = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parsuj conversation zpět na list
        for call in calls:
            try:
                call['conversation'] = json.loads(call.get('conversation', '[]'))
            except:
                call['conversation'] = []
        
        return calls
    
    def get_call_by_sid(self, call_sid):
        """Vrátí konkrétní hovor podle SID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM calls WHERE call_sid = ?", (call_sid,))
        call = cursor.fetchone()
        
        conn.close()
        
        if call:
            call = dict(call)
            try:
                call['conversation'] = json.loads(call.get('conversation', '[]'))
            except:
                call['conversation'] = []
            return call
        
        return None
    
    def get_calls_by_outcome(self, outcome):
        """Vrátí hovory podle výsledku"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM calls 
            WHERE outcome = ?
            ORDER BY created_at DESC
        """, (outcome,))
        
        calls = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        for call in calls:
            try:
                call['conversation'] = json.loads(call.get('conversation', '[]'))
            except:
                call['conversation'] = []
        
        return calls
    
    def get_stats(self):
        """Vrátí statistiky"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Celkem
        cursor.execute("SELECT COUNT(*) FROM calls")
        total = cursor.fetchone()[0]
        
        # Úspěšné
        cursor.execute("SELECT COUNT(*) FROM calls WHERE outcome = 'meeting_scheduled'")
        successful = cursor.fetchone()[0]
        
        # Neúspěšné
        cursor.execute("SELECT COUNT(*) FROM calls WHERE outcome IN ('rejected', 'no_interest')")
        failed = cursor.fetchone()[0]
        
        # Průměrné skóre
        cursor.execute("SELECT AVG(sales_score) FROM calls")
        avg_score = cursor.fetchone()[0] or 0
        
        # Průměrná délka
        cursor.execute("SELECT AVG(duration) FROM calls")
        avg_duration = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': round((successful / total * 100) if total > 0 else 0, 1),
            'avg_score': round(avg_score, 1),
            'avg_duration': round(avg_duration, 0)
        }
    
    def delete_call(self, call_sid):
        """Smaž hovor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM calls WHERE call_sid = ?", (call_sid,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Hovor {call_sid} smazán")