# database/cold_calling_db.py
"""
Databáze pro cold calling kampaně
Ukládá kontakty, hovory, výsledky
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class ColdCallingDB:
    def __init__(self, db_path="data/cold_calling.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializuje databázi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabulka kampaní
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
        """)
        
        # Tabulka kontaktů
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            name TEXT NOT NULL,
            company TEXT,
            phone TEXT NOT NULL UNIQUE,
            email TEXT,
            notes TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
        """)
        
        # Tabulka hovorů
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            call_sid TEXT UNIQUE,
            phone TEXT NOT NULL,
            duration INTEGER DEFAULT 0,
            status TEXT,
            outcome TEXT,
            sales_score INTEGER DEFAULT 0,
            ai_summary TEXT,
            transcript TEXT,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ Cold calling databáze inicializována: {self.db_path}")
    
    # ============================================================
    # KAMPANĚ
    # ============================================================
    
    def create_campaign(self, name, description=""):
        """Vytvoří novou kampaň"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO campaigns (name, description)
            VALUES (?, ?)
        """, (name, description))
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Kampaň '{name}' vytvořena (ID: {campaign_id})")
        return campaign_id
    
    def get_campaigns(self):
        """Vrátí všechny kampaně"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM campaigns ORDER BY created_at DESC")
        campaigns = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return campaigns
    
    # ============================================================
    # KONTAKTY
    # ============================================================
    
    def add_contact(self, campaign_id, name, phone, company="", email="", notes=""):
        """Přidá kontakt do kampaně"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO contacts (campaign_id, name, company, phone, email, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (campaign_id, name, company, phone, email, notes))
            
            contact_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return contact_id
        except sqlite3.IntegrityError:
            print(f"⚠️  Kontakt {phone} už existuje")
            conn.close()
            return None
    
    def import_contacts_csv(self, campaign_id, csv_path):
        """Importuje kontakty z CSV"""
        import csv
        
        imported = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contact_id = self.add_contact(
                    campaign_id=campaign_id,
                    name=row.get('name', ''),
                    phone=row.get('phone', ''),
                    company=row.get('company', ''),
                    email=row.get('email', ''),
                    notes=row.get('notes', '')
                )
                if contact_id:
                    imported += 1
        
        print(f"✅ Importováno {imported} kontaktů")
        return imported
    
    def get_contacts(self, campaign_id=None, status=None):
        """Vrátí kontakty"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []
        
        if campaign_id:
            query += " AND campaign_id = ?"
            params.append(campaign_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        contacts = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return contacts
    
    def update_contact_status(self, contact_id, status):
        """Aktualizuje status kontaktu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE contacts SET status = ? WHERE id = ?
        """, (status, contact_id))
        
        conn.commit()
        conn.close()
    
    # ============================================================
    # HOVORY
    # ============================================================
    
    def save_call(self, contact_id, call_sid, phone, duration, status, 
                  outcome="", sales_score=0, ai_summary="", transcript=""):
        """Uloží hovor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO calls (
                contact_id, call_sid, phone, duration, status,
                outcome, sales_score, ai_summary, transcript,
                started_at, ended_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact_id, call_sid, phone, duration, status,
            outcome, sales_score, ai_summary, transcript,
            datetime.now(), datetime.now()
        ))
        
        call_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Aktualizuj status kontaktu
        if outcome == "meeting_scheduled":
            self.update_contact_status(contact_id, "success")
        elif outcome == "rejected":
            self.update_contact_status(contact_id, "failed")
        else:
            self.update_contact_status(contact_id, "contacted")
        
        return call_id
    
    def get_calls(self, campaign_id=None, contact_id=None):
        """Vrátí hovory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if contact_id:
            query = """
                SELECT * FROM calls WHERE contact_id = ?
                ORDER BY created_at DESC
            """
            cursor.execute(query, (contact_id,))
        elif campaign_id:
            query = """
                SELECT c.* FROM calls c
                JOIN contacts co ON c.contact_id = co.id
                WHERE co.campaign_id = ?
                ORDER BY c.created_at DESC
            """
            cursor.execute(query, (campaign_id,))
        else:
            query = "SELECT * FROM calls ORDER BY created_at DESC"
            cursor.execute(query)
        
        calls = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return calls
    
    # ============================================================
    # STATISTIKY
    # ============================================================
    
    def get_campaign_stats(self, campaign_id):
        """Vrátí statistiky kampaně"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Celkový počet kontaktů
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE campaign_id = ?", (campaign_id,))
        total_contacts = cursor.fetchone()[0]
        
        # Zavolané
        cursor.execute("""
            SELECT COUNT(*) FROM contacts 
            WHERE campaign_id = ? AND status != 'pending'
        """, (campaign_id,))
        called = cursor.fetchone()[0]
        
        # Úspěšné
        cursor.execute("""
            SELECT COUNT(*) FROM contacts 
            WHERE campaign_id = ? AND status = 'success'
        """, (campaign_id,))
        success = cursor.fetchone()[0]
        
        # Neúspěšné
        cursor.execute("""
            SELECT COUNT(*) FROM contacts 
            WHERE campaign_id = ? AND status = 'failed'
        """, (campaign_id,))
        failed = cursor.fetchone()[0]
        
        # Průměrné skóre
        cursor.execute("""
            SELECT AVG(c.sales_score) FROM calls c
            JOIN contacts co ON c.contact_id = co.id
            WHERE co.campaign_id = ?
        """, (campaign_id,))
        avg_score = cursor.fetchone()[0] or 0
        
        # Průměrná délka hovoru
        cursor.execute("""
            SELECT AVG(c.duration) FROM calls c
            JOIN contacts co ON c.contact_id = co.id
            WHERE co.campaign_id = ?
        """, (campaign_id,))
        avg_duration = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_contacts': total_contacts,
            'called': called,
            'pending': total_contacts - called,
            'success': success,
            'failed': failed,
            'success_rate': round((success / called * 100) if called > 0 else 0, 1),
            'avg_score': round(avg_score, 1),
            'avg_duration': round(avg_duration, 0)
        }