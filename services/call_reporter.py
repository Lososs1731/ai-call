# services/call_reporter.py
"""
AI Reporter - vyhodnocuje hovory pomocí GPT
Analyzuje úspěšnost, generuje skóre a shrnutí
"""

from openai import OpenAI
from config import Config
import json


class CallReporter:
    """AI služba pro vyhodnocení hovorů"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Levnější a rychlejší
    
    def analyze_call(self, call_sid, conversation):
        """
        Analyzuje hovor a vrátí report
        
        Args:
            call_sid: ID hovoru
            conversation: List zpráv [{'role': 'assistant', 'content': '...'}, ...]
        
        Returns:
            {
                'outcome': 'meeting_scheduled' | 'interested' | 'rejected' | 'no_interest',
                'sales_score': 0-100,
                'ai_summary': 'Shrnutí hovoru...',
                'key_points': ['bod 1', 'bod 2'],
                'next_action': 'Co dělat dál'
            }
        """
        
        print(f"\n🤖 AI Reporter - analyzuji hovor {call_sid}...")
        
        try:
            # Připrav konverzaci pro AI (bez system zpráv)
            messages_text = []
            for msg in conversation:
                if msg.get('role') in ['assistant', 'user']:
                    role = "Pavel (prodejce)" if msg['role'] == 'assistant' else "Zákazník"
                    messages_text.append(f"{role}: {msg['content']}")
            
            conversation_str = "\n".join(messages_text)
            
            # AI Prompt pro vyhodnocení
            prompt = f"""Analyzuj tento cold calling hovor o prodeji webových stránek.

KONVERZACE:
{conversation_str}

VYHODNOŤ:

1. VÝSLEDEK (outcome):
   - "meeting_scheduled" = Schůzka domluvena nebo silný zájem
   - "interested" = Zájem, ale nerozhodnut
   - "callback_needed" = Zavolat později
   - "rejected" = Tvrdé odmítnutí
   - "no_interest" = Žádný zájem

2. SALES SKÓRE (0-100):
   - 90-100: Schůzka domluvena
   - 70-89: Silný zájem, pravděpodobná schůzka
   - 50-69: Střední zájem
   - 30-49: Slabý zájem
   - 0-29: Odmítnutí

3. SHRNUTÍ (2-3 věty):
   - Co se stalo
   - Jak zákazník reagoval
   - Důvod výsledku

4. KLÍČOVÉ BODY:
   - 2-3 nejdůležitější věci z hovoru

5. DALŠÍ AKCE:
   - Co dělat dál (zavolat, poslat email, atd.)

VRAŤ JSON:
{{
  "outcome": "...",
  "sales_score": X,
  "ai_summary": "...",
  "key_points": ["...", "..."],
  "next_action": "..."
}}

ODPOVĚĎ (POUZE JSON):"""

            # Zavolej GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Jsi AI analytik prodejních hovorů. Analyzuješ cold calling a vracíš JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parsuj odpověď
            result_text = response.choices[0].message.content.strip()
            
            # Extrahuj JSON (pokud je v markdown blocích)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            print(f"✅ AI Report hotový!")
            print(f"   Outcome: {result.get('outcome')}")
            print(f"   Skóre: {result.get('sales_score')}/100")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"   Raw: {result_text}")
            
            # Fallback - pokus se extrahovat data ručně
            return {
                'outcome': 'unknown',
                'sales_score': 0,
                'ai_summary': 'Chyba při parsování AI odpovědi',
                'key_points': [],
                'next_action': 'Zkontrolovat manuálně',
                'error': str(e)
            }
            
        except Exception as e:
            print(f"❌ AI Reporter error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'outcome': 'error',
                'sales_score': 0,
                'ai_summary': f'Chyba: {str(e)}',
                'key_points': [],
                'next_action': 'Zkontrolovat manuálně',
                'error': str(e)
            }
    
    def get_stats_summary(self, calls):
        """
        Vygeneruje celkové shrnutí kampaně
        
        Args:
            calls: List hovorů s AI reporty
        
        Returns:
            {
                'total_calls': X,
                'success_rate': X%,
                'avg_score': X,
                'best_practices': ['...'],
                'improvement_areas': ['...']
            }
        """
        
        if not calls:
            return {
                'total_calls': 0,
                'success_rate': 0,
                'avg_score': 0,
                'best_practices': [],
                'improvement_areas': []
            }
        
        # Základní stats
        total = len(calls)
        successful = len([c for c in calls if c.get('outcome') in ['meeting_scheduled', 'interested']])
        success_rate = round((successful / total * 100) if total > 0 else 0, 1)
        
        scores = [c.get('sales_score', 0) for c in calls if c.get('sales_score')]
        avg_score = round(sum(scores) / len(scores) if scores else 0, 1)
        
        return {
            'total_calls': total,
            'success_rate': success_rate,
            'avg_score': avg_score,
            'successful_calls': successful,
            'failed_calls': total - successful
        }