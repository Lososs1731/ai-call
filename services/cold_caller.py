"""
Sluzba pro cold calling
"""

from twilio.rest import Client
from datetime import datetime
import time
import os

from core import AIEngine, TTSEngine
from config import Config, CallConfig, Prompts
from database import CallDB


class ColdCallerService:
    """Sluzba pro odchozi cold calling"""
    
    def __init__(self, campaign_name, product_name=None):
        self.twilio = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.ai = AIEngine()
        self.db = CallDB()
        self.campaign = campaign_name
        
        # Ziskej produkt z databaze
        if product_name:
            self.product = self.db.get_product_by_name(product_name)
        else:
            # Default produkt
            self.product = self.db.get_product_by_name("Tvorba webů na míru")
        
        if not self.product:
            raise ValueError(f"Produkt '{product_name}' nenalezen v databazi!")
        
        print(f"\n{'='*50}")
        print(f"Cold Caller pripraven")
        print(f"Kampan: {campaign_name}")
        print(f"Produkt: {self.product['name']}")
        print(f"Popis: {self.product['description']}")
        print(f"{'='*50}\n")
    
    def call_contact(self, contact, webhook_base_url):
        """Zavola kontakt"""
        try:
            print(f"\n{'='*60}")
            print(f"📞 PRIPRAVUJI HOVOR")
            print(f"{'='*60}")
            print(f"Jmeno: {contact['name']}")
            print(f"Telefon: {contact['phone']}")
            if contact.get('company'):
                print(f"Firma: {contact['company']}")
            
            # PŘIPRAVIT WEBHOOK URL s parametry
            base_url = webhook_base_url.rstrip('/')
            
            import urllib.parse
            params = urllib.parse.urlencode({
                'name': contact['name'],
                'company': contact.get('company', ''),
                'product_id': self.product['id']
            })
            
            webhook = f"{base_url}/outbound?{params}"
            status_callback = f"{base_url}/call-status"
            
            print(f"\n📡 Webhook:")
            print(f"   {webhook}")
            
            # ZAVOLAT!
            print(f"\n📞 VOLÁM...")
            
            call = self.twilio.calls.create(
                to=contact['phone'],
                from_=Config.TWILIO_PHONE_NUMBER,
                url=webhook,
                status_callback=status_callback,
                status_callback_event=['completed'],
                record=CallConfig.RECORD_CALLS,
                timeout=30
            )
            
            print(f"   ✅ Hovor zahájen!")
            print(f"   📋 Call SID: {call.sid}")
            print(f"   📊 Status: {call.status}")
            
            # ULOŽIT DO DB
            self.db.add_call({
                'sid': call.sid,
                'type': 'outbound',
                'direction': 'outbound',
                'phone': contact['phone']
            })
            
            # Update kontaktu
            self.db.update_contact(contact['phone'], {
                'last_call': datetime.now().isoformat(),
                'call_count': contact.get('call_count', 0) + 1,
                'status': 'contacted'
            })
            
            print(f"   ✅ Uloženo do DB")
            print(f"{'='*60}\n")
            
            return {'success': True, 'sid': call.sid}
            
        except Exception as e:
            print(f"\n❌ CHYBA při volání: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def run_campaign(self, webhook_base_url, max_calls=None):
        """Spusti kampan"""
        print(f"\n{'='*60}")
        print(f"🚀 SPOUŠTÍM KAMPAŇ: {self.campaign}")
        print(f"{'='*60}")
        
        contacts = self.db.get_contacts(status='new', limit=max_calls or 1000)
        
        if not contacts:
            print("❌ Žádné kontakty k zavolání")
            return
        
        print(f"📊 Kontaktů k zavolání: {len(contacts)}")
        print(f"🎯 Produkt: {self.product['name']}")
        print(f"{'='*60}")
        
        made = 0
        failed = 0
        
        for i, contact in enumerate(contacts, 1):
            print(f"\n[{i}/{len(contacts)}]")
            
            # Kontrola volací doby
            if not self._can_call():
                print("⏰ Mimo volací dobu - ukončuji kampaň")
                break
            
            # Zavolat
            result = self.call_contact(contact, webhook_base_url)
            
            if result['success']:
                made += 1
                print(f"✅ Úspěch #{made}")
            else:
                failed += 1
                print(f"❌ Selhání: {result.get('error', 'Unknown')}")
            
            # Pauza mezi hovory
            if i < len(contacts):
                wait = 60 / CallConfig.CALLS_PER_MINUTE
                print(f"\n⏳ Čekám {wait:.0f}s před dalším hovorem...")
                time.sleep(wait)
        
        # VÝSLEDKY
        print(f"\n{'='*60}")
        print(f"📊 KAMPAŇ DOKONČENA")
        print(f"{'='*60}")
        print(f"✅ Úspěšných hovorů: {made}")
        print(f"❌ Selhání: {failed}")
        print(f"📞 Celkem pokusů: {made + failed}")
        print(f"{'='*60}\n")
    
    def _can_call(self):
        """Kontrola volaci doby"""
        now = datetime.now()
        
        # Kontrola dne v týdnu
        if now.weekday() not in CallConfig.WORK_DAYS:
            print(f"⏰ Dnes ({now.strftime('%A')}) není pracovní den")
            return False
        
        # Kontrola hodiny
        if not (CallConfig.START_HOUR <= now.hour < CallConfig.END_HOUR):
            print(f"⏰ Mimo pracovní dobu ({CallConfig.START_HOUR}-{CallConfig.END_HOUR}h)")
            return False
        
        return True