# services/receptionist.py - OPRAVENO

from core import AIEngine, TTSEngine
from config import Prompts

# ✅ IMPORT S FALLBACKEM
try:
    from database import CallDB
    CALLDB_AVAILABLE = True
except:
    CallDB = None
    CALLDB_AVAILABLE = False
    print("  ⚠️  CallDB nedostupná - používám fallback")


class ReceptionistService:
    """Recepcni sluzba pro prichozi hovory"""
    
    def __init__(self):
        print("Inicializuji ReceptionistService...")
        
        # ✅ IMPORT RECEPČNÍ KB
        try:
            from database.knowledge_base import get_receptionist_prompt, RECEPTION_KB
            self.kb_available = True
            print("  ✅ Knowledge Base načtena")
        except Exception as e:
            self.kb_available = False
            print(f"  ⚠️  KB nedostupná: {e}")
        
        try:
            self.ai = AIEngine()
            print("  ✓ AIEngine OK")
        except Exception as e:
            print(f"  ✗ AIEngine chyba: {e}")
            raise
        
        try:
            self.tts = TTSEngine()
            print("  ✓ TTSEngine OK")
        except Exception as e:
            print(f"  ✗ TTSEngine chyba: {e}")
            raise
        
        # ✅ CALLDB JEN POKUD JE DOSTUPNÁ
        if CALLDB_AVAILABLE:
            try:
                self.db = CallDB()
                print("  ✓ CallDB OK")
            except Exception as e:
                print(f"  ✗ CallDB chyba: {e}")
                self.db = None
        else:
            self.db = None
            print("  ⚠️  CallDB není dostupná - pokračuji bez ní")
        
        print("ReceptionistService ready!")
    
    def handle_call(self, call_sid, caller_number):
        """
        Zpracuje prichozi hovor
        """
        print(f"\n[ReceptionistService] handle_call({call_sid})")
        
        # Ulozeni do DB (pouze pokud je DB dostupná)
        if self.db:
            try:
                print("  Ukladam do DB...")
                self.db.add_call({
                    'sid': call_sid,
                    'type': 'inbound',
                    'direction': 'inbound',
                    'phone': caller_number
                })
                print("  ✓ Ulozeno do DB")
            except Exception as e:
                print(f"  ✗ DB chyba: {e}")
        
        try:
            # ✅ POUŽIJ RECEPČNÍ PROMPT Z KB
            if self.kb_available:
                from database.knowledge_base import get_receptionist_prompt, RECEPTION_KB
                receptionist_prompt = get_receptionist_prompt()
                print("  ✅ Použit RECEPČNÍ prompt z KB")
                
                # Dynamický pozdrav z KB
                firma_nazev = RECEPTION_KB['firma']['nazev']
                greeting = f"Dobrý den, {firma_nazev}, recepce. Jak vám mohu pomoci?"
            else:
                # Fallback
                from config import Prompts
                receptionist_prompt = Prompts.RECEPTIONIST
                greeting = "Dobrý den, recepce. Jak vám mohu pomoci?"
                print("  ⚠️  Použit fallback prompt")
            
            # Zahajeni konverzace
            print("  Zahajuji konverzaci...")
            self.ai.start_conversation(call_sid, receptionist_prompt)
            print("  ✓ Konverzace zahajena")
            
        except Exception as e:
            print(f"  ✗ AI chyba: {e}")
            greeting = "Dobrý den, jak vám mohu pomoci?"
        
        print(f"  Vracim pozdrav: {greeting}")
        return greeting
    
    def process_message(self, call_sid, user_message):
        """Zpracuje zpravu od uzivatele"""
        print(f"\n[ReceptionistService] process_message({call_sid})")
        print(f"  User: {user_message}")
        
        try:
            reply = self.ai.get_response(call_sid, user_message)
            print(f"  AI: {reply}")
            return reply
        except Exception as e:
            print(f"  ✗ AI chyba: {e}")
            return "Omlouvam se, nastala chyba."
    
    def end_call(self, call_sid, duration):
        """Ukonci hovor"""
        print(f"\n[ReceptionistService] end_call({call_sid}, {duration}s)")
        
        try:
            history = self.ai.end_conversation(call_sid)
            print(f"  Konverzace ukoncena ({len(history)} zprav)")
        except Exception as e:
            print(f"  ✗ AI chyba: {e}")
            history = []
        
        # Ulož do DB pouze pokud je dostupná
        if self.db:
            try:
                self.db.update_call(call_sid, {
                    'status': 'completed',
                    'duration': duration,
                    'transcript': str(history)
                })
                print("  ✓ DB aktualizovana")
            except Exception as e:
                print(f"  ✗ DB chyba: {e}")
        
        return history