# services/cold_caller_service.py - NOVÝ SOUBOR
"""
Služba pro cold calling - propojená s cold_calling_db
"""

from twilio.rest import Client
from datetime import datetime
import time

from core import AIEngine
from config import Config
from database.cold_calling_db import ColdCallingDB


class ColdCallerService:
    """Služba pro odchozí cold calling"""
    
    def __init__(self, campaign_name):
        print(f"Inicializuji ColdCallerService...")
        
        try:
            self.twilio = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
            print("  ✓ Twilio OK")
        except Exception as e:
            print(f"  ✗ Twilio chyba: {e}")
            raise
        
        try:
            self.ai = AIEngine()
            print("  ✓ AIEngine OK")
        except Exception as e:
            print(f"  ✗ AIEngine chyba: {e}")
            raise
        
        try:
            self.db = ColdCallingDB()
            print("  ✓ ColdCallingDB OK")
        except Exception as e:
            print(f"  ✗ ColdCallingDB chyba: {e}")
            raise
        
        # Najdi kampaň
        campaigns = self.db.get_campaigns()
        self.campaign = next((c for c in campaigns if c['name'] == campaign_name), None)
        
        if not self.campaign:
            raise ValueError(f"Kampaň '{campaign_name}' nenalezena!")
        
        print(f"\n{'='*50}")
        print(f"✅ Cold Caller připraven")
        print(f"Kampaň: {self.campaign['name']} (ID: {self.campaign['id']})")
        print(f"{'='*50}\n")
    
    def call_contact(self, contact, webhook_base_url):
        """Zavolá kontakt"""
        try:
            print(f"\n{'='*60}")
            print(f"📞 VOLÁM: {contact['name']} - {contact['phone']}")
            if contact.get('company'):
                print(f"   Firma: {contact['company']}")
            print(f"{'='*60}")
            
            # Webhook URL
            base_url = webhook_base_url.rstrip('/')
            
            import urllib.parse
            params = urllib.parse.urlencode({
                'name': contact['name'],
                'company': contact.get('company', ''),
                'campaign': self.campaign['id']
            })
            
            webhook = f"{base_url}/outbound?{params}"
            status_callback = f"{base_url}/call-status"
            
            print(f"📡 Webhook: {webhook}")
            
            # ZAVOLAT
            call = self.twilio.calls.create(
                to=contact['phone'],
                from_=Config.TWILIO_PHONE_NUMBER,
                url=webhook,
                status_callback=status_callback,
                status_callback_event=['completed'],
                timeout=30
            )
            
            print(f"✅ Hovor zahájen!")
            print(f"   Call SID: {call.sid}")
            
            # Updatuj status
            self.db.update_contact_status(contact['id'], 'calling')
            
            return {'success': True, 'sid': call.sid}
            
        except Exception as e:
            print(f"❌ CHYBA: {e}")
            import traceback
            traceback.print_exc()
            
            self.db.update_contact_status(contact['id'], 'error')
            return {'success': False, 'error': str(e)}
    
    def run_campaign(self, webhook_base_url, max_calls=None):
        """Spustí kampaň"""
        print(f"\n{'='*60}")
        print(f"🚀 SPOUŠTÍM KAMPAŇ: {self.campaign['name']}")
        print(f"{'='*60}\n")
        
        # Získej pending kontakty
        contacts = self.db.get_contacts(
            campaign_id=self.campaign['id'],
            status='pending'
        )
        
        if not contacts:
            print("❌ Žádné kontakty k zavolání!")
            return
        
        if max_calls:
            contacts = contacts[:max_calls]
        
        print(f"📊 Obvolám {len(contacts)} kontaktů\n")
        
        made = 0
        failed = 0
        
        for i, contact in enumerate(contacts, 1):
            print(f"\n[{i}/{len(contacts)}]")
            
            # Zavolat
            result = self.call_contact(contact, webhook_base_url)
            
            if result['success']:
                made += 1
            else:
                failed += 1
            
            # Pauza mezi hovory
            if i < len(contacts):
                wait = 30
                print(f"\n⏳ Čekám {wait}s...")
                time.sleep(wait)
        
        # VÝSLEDKY
        print(f"\n{'='*60}")
        print(f"📊 KAMPAŇ DOKONČENA")
        print(f"{'='*60}")
        print(f"✅ Úspěšných: {made}")
        print(f"❌ Selhání: {failed}")
        print(f"\n💡 Výsledky: http://localhost:5000/admin/campaign/{self.campaign['id']}")
        print(f"{'='*60}\n")