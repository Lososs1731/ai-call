# core/ai_engine.py - KOMPLETNĚ PŘEPSANÉ
"""
AI Engine s vylepšeným porozuměním češtině
Rychlejší, přirozenější, inteligentní cleanup
"""

import openai
from config import Config
import re


class AIEngine:
    """AI engine pro konverzace s Knowledge Base podporou"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.conversations = {}
        self.model = "gpt-4o-mini"  # ✅ Rychlejší než gpt-4
        
        # ✅ IMPORT KB
        try:
            from database.knowledge_base import get_context_for_query
            self.kb_retriever = get_context_for_query
            print("  ✅ Knowledge Base načtena")
        except Exception as e:
            print(f"  ⚠️  KB import error: {e}")
            self.kb_retriever = None
    
    def _cleanup_czech_input(self, text):
        """
        Vyčistí a normalizuje český vstup z STT
        Opraví časté chyby rozpoznávání
        """
        # Lowercase pro porovnání
        cleaned = text.lower().strip()
        
        # Časté STT chyby v češtině
        replacements = {
            'slyšíme se dobrý den': 'dobrý den',
            'dobry den dobry den': 'dobrý den',
            'jo jo': 'jo',
            'ne ne': 'ne',
            'tak tak': 'tak',
            'já já': 'já',
            'mám mám': 'mám',
            'takhle takhle': 'takhle',
            'uvažuji uvažuji': 'uvažuji'
        }
        
        for wrong, correct in replacements.items():
            if wrong in cleaned:
                cleaned = cleaned.replace(wrong, correct)
        
        # Odstraň vícenásobné mezery
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def start_conversation(self, call_sid, system_prompt):
        """Zahájí novou konverzaci"""
        self.conversations[call_sid] = [
            {'role': 'system', 'content': system_prompt}
        ]
        print(f"[AIEngine] Konverzace {call_sid} zahájena")
    
    def get_response(self, call_sid, user_message):
        """
        Získá odpověď od AI s automatickým KB kontextem
        VYLEPŠENO: Čistí český vstup, rychlejší, přirozenější
        """
        if call_sid not in self.conversations:
            raise ValueError(f"Konverzace {call_sid} neexistuje!")
        
        # ✅ VYČISTI ČESKÝ VSTUP
        cleaned_message = self._cleanup_czech_input(user_message)
        print(f"  🧹 Cleaned: '{cleaned_message}'")
        
        # ✅ VYHLEDEJ KONTEXT Z KB
        kb_context = ""
        if self.kb_retriever:
            try:
                kb_context = self.kb_retriever(cleaned_message)
                if kb_context:
                    print(f"  📚 KB context: {kb_context[:100]}...")
            except Exception as e:
                print(f"  ⚠️  KB retrieval error: {e}")
        
        # ✅ VYTVOŘ ZPRÁVU S KONTEXTEM
        if kb_context:
            enhanced_message = f"{cleaned_message}\n\n[INFO Z DATABÁZE]:\n{kb_context}"
        else:
            enhanced_message = cleaned_message
        
        # Přidej do historie
        self.conversations[call_sid].append({
            'role': 'user',
            'content': enhanced_message
        })
        
        # ✅ ZAVOLEJ OpenAI - RYCHLÉ PARAMETRY
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=self.conversations[call_sid],
                temperature=0.9,  # ✅ Více kreativní = zábavnější
                max_tokens=60,    # ✅ KRATŠÍ = rychlejší (max 2 věty)
                presence_penalty=0.4,  # ✅ Méně opakování
                frequency_penalty=0.4,  # ✅ Rozmanitější slovník
                top_p=0.95  # ✅ Přirozenější volba slov
            )
            
            ai_reply = response.choices[0].message.content.strip()
            
            # ✅ VYČISTI ODPOVĚĎ (odstraň markdown, emojis apod.)
            ai_reply = self._cleanup_ai_response(ai_reply)
            
            # Ulož odpověď
            self.conversations[call_sid].append({
                'role': 'assistant',
                'content': ai_reply
            })
            
            return ai_reply
            
        except Exception as e:
            print(f"[AIEngine] OpenAI error: {e}")
            raise
    
    def _cleanup_ai_response(self, text):
        """Vyčistí AI odpověď pro TTS"""
        # Odstraň markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # *italic*
        
        # Odstraň emojis
        text = re.sub(r'[😀-🙏🌀-🗿🚀-🛿]', '', text)
        
        # Odstraň vícenásobné tečky
        text = re.sub(r'\.{2,}', '.', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def end_conversation(self, call_sid):
        """Ukončí konverzaci a vrátí historii"""
        if call_sid not in self.conversations:
            return []
        
        history = self.conversations[call_sid].copy()
        
        # ⚠️ NESMAŽ JEŠTĚ! Learning system potřebuje přístup
        # del self.conversations[call_sid]
        
        print(f"[AIEngine] Konverzace {call_sid} ukončena ({len(history)} zpráv)")
        return history
    
    def get_conversation_history(self, call_sid):
        """Vrátí historii konverzace"""
        return self.conversations.get(call_sid, [])