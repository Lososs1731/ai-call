"""
Sluzba pro recepcni rezim
"""

from core import AIEngine, TTSEngine
from config import Prompts
from database import CallDB


class ReceptionistService:
    """Recepcni sluzba pro prichozi hovory"""
    
    def __init__(self):
        print("Inicializuji ReceptionistService...")
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
        
        try:
            self.db = CallDB()
            print("  ✓ CallDB OK")
        except Exception as e:
            print(f"  ✗ CallDB chyba: {e}")
            raise
        
        print("ReceptionistService ready!")
    
    def handle_call(self, call_sid, caller_number):
        """
        Zpracuje prichozi hovor
        """
        print(f"\n[ReceptionistService] handle_call({call_sid})")
        
        try:
            # Ulozeni do DB
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
            # Zahajeni konverzace
            print("  Zahajuji konverzaci...")
            self.ai.start_conversation(call_sid, Prompts.RECEPTIONIST)
            print("  ✓ Konverzace zahajena")
        except Exception as e:
            print(f"  ✗ AI chyba: {e}")
        
        # Pozdrav
        greeting = "Ahoj, jak ti muzu pomoct?"
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
        
        try:
            self.db.update_call(call_sid, {
                'status': 'completed',
                'duration': duration,
                'transcript': str(history)
            })
            print("  ✓ DB aktualizovana")
        except Exception as e:
            print(f"  ✗ DB chyba: {e}")