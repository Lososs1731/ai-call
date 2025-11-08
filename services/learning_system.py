# services/learning_system.py - KOMPLETNĚ PŘEPSANÉ
"""
Enhanced Learning System - učí se z úspěšných I neúspěšných hovorů
Auto-optimalizuje sales prompty a námitky handling
"""

import json
from datetime import datetime
from pathlib import Path


class LearningSystem:
    def __init__(self):
        self.data_dir = Path("data/learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.success_log = self.data_dir / "successful_calls.json"
        self.fail_log = self.data_dir / "failed_calls.json"
        self.namitky_log = self.data_dir / "objections.json"
        self.optimization_log = self.data_dir / "prompt_optimizations.json"
        
        self._init_logs()
    
    def _init_logs(self):
        """Inicializace log souborů"""
        for log_file in [self.success_log, self.fail_log, self.namitky_log, self.optimization_log]:
            if not log_file.exists():
                log_file.write_text(json.dumps([], indent=2))
    
    def learn_from_successful_call(self, call_sid, report):
        """
        Učí se z ÚSPĚŠNÉHO hovoru
        - Co fungovalo?
        - Jaké fráze vedly k úspěchu?
        - Jak překonal námitky?
        """
        print(f"\n🧠 LEARNING Z ÚSPĚŠNÉHO HOVORU")
        print(f"   Call SID: {call_sid}")
        print(f"   Sales Score: {report.get('sales_score', 0)}/100")
        
        # Načti existující data
        successes = json.loads(self.success_log.read_text())
        
        # Analyzuj co fungovalo
        learning_data = {
            "call_sid": call_sid,
            "timestamp": datetime.now().isoformat(),
            "sales_score": report.get('sales_score', 0),
            "outcome": report.get('outcome', ''),
            "ai_summary": report.get('ai_summary', ''),
            "key_phrases": self._extract_key_phrases(report),
            "objections_overcome": self._extract_objections(report),
            "closing_technique": self._extract_closing(report)
        }
        
        successes.append(learning_data)
        self.success_log.write_text(json.dumps(successes, indent=2, ensure_ascii=False))
        
        print(f"   ✅ Úspěšný hovor uložen do learning DB")
        
        # Auto-optimalizace promptu
        if len(successes) >= 5:
            self._optimize_prompt(successes)
    
    def learn_from_failed_call(self, call_sid, report):
        """
        Učí se z NEÚSPĚŠNÉHO hovoru
        - Proč to nevyšlo?
        - Jaká námitka nebyla překonána?
        - Co mohlo být jinak?
        """
        print(f"\n📚 LEARNING Z NEÚSPĚŠNÉHO HOVORU")
        print(f"   Call SID: {call_sid}")
        print(f"   Sales Score: {report.get('sales_score', 0)}/100")
        
        # Načti existující data
        fails = json.loads(self.fail_log.read_text())
        
        # Analyzuj proč to nevyšlo
        learning_data = {
            "call_sid": call_sid,
            "timestamp": datetime.now().isoformat(),
            "sales_score": report.get('sales_score', 0),
            "outcome": report.get('outcome', ''),
            "ai_summary": report.get('ai_summary', ''),
            "failure_reason": self._analyze_failure(report),
            "unresolved_objection": self._find_unresolved_objection(report),
            "what_could_be_better": self._suggest_improvement(report)
        }
        
        fails.append(learning_data)
        self.fail_log.write_text(json.dumps(fails, indent=2, ensure_ascii=False))
        
        print(f"   ✅ Failed hovor uložen pro analýzu")
        print(f"   💡 Důvod: {learning_data['failure_reason']}")
        
        # Přidej novou best practice pro námitku
        if learning_data['unresolved_objection']:
            self._update_objection_handling(learning_data)
    
    def _extract_key_phrases(self, report):
        """Extrahuje klíčové fráze, které vedly k úspěchu"""
        # TODO: NLP analýza konverzace
        # Prozatím placeholder
        return ["moderní web", "přivede zákazníky", "rychlá realizace"]
    
    def _extract_objections(self, report):
        """Extrahuje námitky, které byly překonány"""
        summary = report.get('ai_summary', '').lower()
        
        objections = []
        if 'čas' in summary or 'nemám minutku' in summary:
            objections.append("nema_cas")
        if 'drahé' in summary or 'peníze' in summary:
            objections.append("je_to_drahe")
        if 'už máme' in summary:
            objections.append("uz_mame_web")
        
        return objections
    
    def _extract_closing(self, report):
        """Detekuje jaký closing technique byl použit"""
        summary = report.get('ai_summary', '').lower()
        
        if 'schůzka' in summary or 'sejít' in summary:
            return "meeting_close"
        elif 'email' in summary or 'pošlu' in summary:
            return "email_close"
        else:
            return "unknown"
    
    def _analyze_failure(self, report):
        """Analyzuje proč hovor nevyšel"""
        summary = report.get('ai_summary', '').lower()
        outcome = report.get('outcome', '').lower()
        
        if 'nezájem' in summary or 'nechci' in summary:
            return "hard_rejection"
        elif 'čas' in summary:
            return "timing_issue"
        elif 'drahé' in summary:
            return "price_objection_not_overcome"
        elif 'už máme' in summary:
            return "existing_solution"
        else:
            return "unknown"
    
    def _find_unresolved_objection(self, report):
        """Najde námitku, která nebyla překonána"""
        reason = self._analyze_failure(report)
        
        objection_map = {
            "price_objection_not_overcome": "je_to_drahe",
            "timing_issue": "nema_cas",
            "existing_solution": "uz_mame_web"
        }
        
        return objection_map.get(reason)
    
    def _suggest_improvement(self, report):
        """Navrhne co mohlo být jinak"""
        reason = self._analyze_failure(report)
        
        suggestions = {
            "hard_rejection": "Možná přílišný push. Zkus soft approach.",
            "timing_issue": "Nabídnout jiný termín místo pushování teď.",
            "price_objection_not_overcome": "Víc zdůraznit ROI a ztrátu zákazníků bez webu.",
            "existing_solution": "Ptát se na kvalitu webu (rychlost, mobil) místo pouze nabídky."
        }
        
        return suggestions.get(reason, "Analýza potřebuje více dat.")
    
    def _update_objection_handling(self, learning_data):
        """Aktualizuje handling námitek na základě failů"""
        objections = json.loads(self.namitky_log.read_text())
        
        objection_key = learning_data['unresolved_objection']
        if not objection_key:
            return
        
        # Najdi existující nebo vytvoř nový
        existing = next((o for o in objections if o['key'] == objection_key), None)
        
        if existing:
            existing['fail_count'] = existing.get('fail_count', 0) + 1
            existing['last_fail'] = datetime.now().isoformat()
            existing['suggested_improvement'] = learning_data['what_could_be_better']
        else:
            objections.append({
                "key": objection_key,
                "fail_count": 1,
                "last_fail": datetime.now().isoformat(),
                "suggested_improvement": learning_data['what_could_be_better']
            })
        
        self.namitky_log.write_text(json.dumps(objections, indent=2, ensure_ascii=False))
        print(f"   ✅ Objection handling aktualizován: {objection_key}")
    
    def _optimize_prompt(self, successes):
        """
        Auto-optimalizace sales promptu na základě úspěšných hovorů
        Po každých 5 úspěších analyzuje co funguje a upraví prompt
        """
        print(f"\n🔬 AUTO-OPTIMALIZACE PROMPTU")
        print(f"   Analýza {len(successes)} úspěšných hovorů...")
        
        # Analýza nejčastějších successful patterns
        recent_successes = successes[-10:]  # Posledních 10
        
        common_phrases = {}
        common_closings = {}
        common_objections = {}
        
        for call in recent_successes:
            # Fráze
            for phrase in call.get('key_phrases', []):
                common_phrases[phrase] = common_phrases.get(phrase, 0) + 1
            
            # Closingy
            closing = call.get('closing_technique', 'unknown')
            common_closings[closing] = common_closings.get(closing, 0) + 1
            
            # Námitky
            for obj in call.get('objections_overcome', []):
                common_objections[obj] = common_objections.get(obj, 0) + 1
        
        # Vytvoř optimization report
        optimization = {
            "timestamp": datetime.now().isoformat(),
            "analyzed_calls": len(recent_successes),
            "avg_score": sum(c.get('sales_score', 0) for c in recent_successes) / len(recent_successes),
            "top_phrases": sorted(common_phrases.items(), key=lambda x: x[1], reverse=True)[:5],
            "best_closing": max(common_closings.items(), key=lambda x: x[1])[0] if common_closings else None,
            "most_overcome_objections": sorted(common_objections.items(), key=lambda x: x[1], reverse=True)[:3],
            "recommendation": self._generate_prompt_recommendation(common_phrases, common_closings)
        }
        
        # Ulož
        opts = json.loads(self.optimization_log.read_text())
        opts.append(optimization)
        self.optimization_log.write_text(json.dumps(opts, indent=2, ensure_ascii=False))
        
        print(f"   ✅ Optimalizace dokončena!")
        print(f"   📊 Avg score: {optimization['avg_score']:.1f}/100")
        print(f"   💡 Best closing: {optimization['best_closing']}")
        print(f"   🎯 Top phrases: {[p[0] for p in optimization['top_phrases'][:3]]}")
    
    def _generate_prompt_recommendation(self, phrases, closings):
        """Generuje doporučení pro úpravu promptu"""
        top_phrase = max(phrases.items(), key=lambda x: x[1])[0] if phrases else None
        best_closing = max(closings.items(), key=lambda x: x[1])[0] if closings else None
        
        recommendations = []
        
        if top_phrase:
            recommendations.append(f"Zdůraznit frázi: '{top_phrase}' - funguje nejlépe")
        
        if best_closing == "meeting_close":
            recommendations.append("Prioritizovat domlouvání schůzky místo emailu")
        elif best_closing == "email_close":
            recommendations.append("Email close funguje - pokračovat v tomto stylu")
        
        return " | ".join(recommendations)
    
    def get_optimized_prompt(self, product, contact_name):
        """
        Vrací optimalizovaný prompt na základě learnings
        """
        from database.knowledge_base import get_sales_prompt_with_kb
        
        # Základní prompt z KB
        base_prompt = get_sales_prompt_with_kb(product, contact_name)
        
        # Načti optimalizace
        if self.optimization_log.exists():
            opts = json.loads(self.optimization_log.read_text())
            if opts:
                latest = opts[-1]
                
                # Přidej learned insights
                insights = f"""

--- LEARNED INSIGHTS (Auto-optimalizováno) ---
✅ Nejúspěšnější fráze: {', '.join([p[0] for p in latest.get('top_phrases', [])[:3]])}
✅ Best closing: {latest.get('best_closing', 'unknown')}
✅ Doporučení: {latest.get('recommendation', '')}

POUŽIJ TYTO INSIGHTS v konverzaci!
"""
                base_prompt += insights
        
        return base_prompt
    
    def get_stats(self):
        """Vrátí statistiky learningu"""
        successes = json.loads(self.success_log.read_text()) if self.success_log.exists() else []
        fails = json.loads(self.fail_log.read_text()) if self.fail_log.exists() else []
        
        total = len(successes) + len(fails)
        success_rate = (len(successes) / total * 100) if total > 0 else 0
        
        return {
            "total_calls_analyzed": total,
            "successful": len(successes),
            "failed": len(fails),
            "success_rate": f"{success_rate:.1f}%",
            "avg_success_score": sum(c.get('sales_score', 0) for c in successes) / len(successes) if successes else 0,
            "avg_fail_score": sum(c.get('sales_score', 0) for c in fails) / len(fails) if fails else 0
        }