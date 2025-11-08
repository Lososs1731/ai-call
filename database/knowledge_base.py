# database/knowledge_base.py
"""
Knowledge Base pro AI calling systém
- SALES KB: Pro cold calling (odchozí hovory)
- RECEPTION KB: Pro recepci (příchozí hovory)
"""

# ============================================================
# SALES KNOWLEDGE BASE (pro cold calling)
# ============================================================

KNOWLEDGE_BASE = {
    "firma": {
        "nazev": "MoravskeWeby (Lososs Web Development)",
        "kontakt": {
            "majitel": "Ondřej Hyža",
            "telefon": "+420 735 744 433",
            "email": "ondra.hyza@seznam.cz"
        },
        "specialization": "Profesionální tvorba webových stránek na míru"
    },
    
    "sluzby": {
        "webove_stranky_na_miru": {
            "popis": "Originální webové prezentace tvořené podle požadavků bez použití šablon",
            "technologie": ["HTML", "CSS", "JavaScript", "Mobile-first"],
            "vyhody": [
                "Ruční kódování bez šablon",
                "Maximální výkon a rychlost",
                "SEO optimalizace",
                "Responzivní design (mobile-first)",
                "Originální design přesně podle požadavků"
            ]
        },
        "seo_optimalizace": {
            "popis": "Optimalizace pro vyhledávače zajistí lepší viditelnost a přivede více klientů",
            "vyhody": [
                "Lepší pozice ve vyhledávačích",
                "Více organického trafficu",
                "Přivede potenciální zákazníky"
            ]
        },
        "rychlost_a_vykon": {
            "popis": "Rychlé načítání stránek pro lepší uživatelský zážitek",
            "vyhody": [
                "Lepší uživatelský zážitek",
                "Lepší SEO výsledky",
                "Vyšší konverze"
            ]
        },
        "hosting_a_domena": {
            "popis": "Zajištění webhostingu a domény",
            "included": True
        }
    },
    
    "cenik": {
        "onepage": {
            "nazev": "One-page web",
            "cena": "8 000 Kč",
            "popis": "Jednoduchý web na jedné stránce, ideální pro vizitku nebo landing page",
            "vhodne_pro": ["vizitka", "landing page", "portfolio", "prezentace služby"]
        },
        "vicestranky": {
            "nazev": "Vícestránkový web",
            "cena": "12 000 Kč",
            "popis": "Komplexní web s více podstránkami",
            "vhodne_pro": ["firemní prezentace", "portfolio", "kompletní služby"]
        },
        "personalizovane": {
            "nazev": "Personalizované řešení",
            "cena": "dle požadavků (od 12 000 Kč)",
            "popis": "Web přesně na míru s pokročilými funkcemi",
            "vhodne_pro": ["e-shopy", "rezervační systémy", "pokročilé funkce", "komplexní projekty"]
        }
    },
    
    "namitky_a_reseni": {
        "nema_cas": {
            "namitka": "Nemám čas / nemám minutku",
            "typ": "soft_rejection",
            "best_response": "Chápu, že jste vytížený. Stačí jen 2 minuty - ptám se, jestli máte moderní web? Bez něj většina lidí najde konkurenci...",
            "success_rate": 55,
            "follow_up": "Můžu zavolat jindy? Večer po 18:00?"
        },
        "je_to_drahe": {
            "namitka": "To je drahé / nemám peníze",
            "typ": "objection",
            "best_response": "Chápu. Web od 8 tisíc je ale investice, která se vrátí už prvními zákazníky. Kolik zákazníků teď ztrácíte, když vás na netu nenajdou?",
            "success_rate": 40,
            "follow_up": "Můžeme začít one-page řešením za 8 000 a postupně rozšiřovat"
        },
        "uz_mame_web": {
            "namitka": "Už máme web",
            "typ": "objection",
            "best_response": "To je skvělé! Můžu se zeptat - je rychlý a funguje dobře na mobilu? Dnes většina lidí hledá na telefonu...",
            "success_rate": 35,
            "follow_up": "Když vám pošlu analýzu rychlosti vašeho webu zdarma, zajímalo by vás to?"
        },
        "nemame_web": {
            "namitka": "Nemáme web / nemáme stránky",
            "typ": "opportunity",
            "best_response": "To je přesně důvod, proč volám! Dnes bez webu přicházíte o zákazníky každý den. Konkurence vás předbíhá...",
            "success_rate": 75,
            "follow_up": "PUSH! Můžeme mít hotovo za 2 týdny. Domluvíme konzultaci?"
        },
        "stary_web": {
            "namitka": "Máme starý web / nefunguje dobře",
            "typ": "opportunity",
            "best_response": "Presne! Starý web vás může stát zákazníky. Moderní, rychlý web od 12 tisíc vám přinese víc obchodů...",
            "success_rate": 70,
            "follow_up": "PUSH! Pošlu vám portfolio a můžeme se sejít tento týden?"
        },
        "nema_zajem": {
            "namitka": "Nemám zájem / nechci",
            "typ": "hard_rejection",
            "best_response": "Rozumím, díky za čas. Hezký den.",
            "success_rate": 5,
            "action": "hangup"
        },
        "poslete_email": {
            "namitka": "Pošlete mi to emailem",
            "typ": "soft_rejection",
            "best_response": "Jasně, pošlu. Ale aby to mělo smysl - potřebujete spíš one-page za 8 tisíc nebo komplexnější řešení?",
            "success_rate": 45,
            "follow_up": "Email pošlu dnes, můžu vám pak zavolat zítra?"
        },
        "musim_se_poradit": {
            "namitka": "Musím se poradit / rozhoduje někdo jiný",
            "typ": "objection",
            "best_response": "Chápu. S kým se potřebujete poradit? Můžu poslat info pro rozhodování...",
            "success_rate": 50,
            "follow_up": "Kdy byste věděli? Můžu zavolat příští týden?"
        }
    }
}


# ============================================================
# RECEPTION KNOWLEDGE BASE (pro recepci)
# ============================================================
# database/knowledge_base.py - BARBER SHOP VERZE

RECEPTION_KB = {
    "firma": {
        "nazev": "Barber Shop Moravec",  # ← Změň na jméno salonu
        "kontakt": {
            "majitel": "Ondřej Hyža",  # ← Změň na jméno majitele
            "telefon": "+420 735 744 433",
            "email": "info@barbershop.cz",  # ← Změň email
            "adresa": "Hlavní 123, Praha 1"  # ← Přidej adresu
        },
        "oteviraci_doba": {
            "pondelі_patek": "9:00-19:00",
            "sobota": "9:00-15:00",
            "nedele": "zavřeno"
        }
    },
    
    "sluzby": {
        "panske_strihani": {
            "nazev": "Pánské stříhání",
            "cena": "350 Kč",
            "trvani": "30 minut",
            "popis": "Klasický pánský střih nůžkami nebo strojkem"
        },
        "holeni": {
            "nazev": "Holení břitvou",
            "cena": "250 Kč",
            "trvani": "20 minut",
            "popis": "Tradiční holení břitvou s teplým ručníkem"
        },
        "vousy": {
            "nazev": "Úprava vousů",
            "cena": "200 Kč",
            "trvani": "15 minut",
            "popis": "Tvarování a úprava vousů a knírů"
        },
        "komplet": {
            "nazev": "Kompletní péče",
            "cena": "700 Kč",
            "trvani": "60 minut",
            "popis": "Stříhání + holení + úprava vousů + péče o pleť"
        },
        "damske_strihani": {
            "nazev": "Dámské stříhání",
            "cena": "400 Kč",
            "trvani": "40 minut",
            "popis": "Střih + mytí + foukaná"
        },
        "detske_strihani": {
            "nazev": "Dětské stříhání",
            "cena": "250 Kč",
            "trvani": "20 minut",
            "popis": "Střih pro děti do 12 let"
        },
        "barveni": {
            "nazev": "Barvení vlasů",
            "cena": "od 500 Kč",
            "trvani": "45-60 minut",
            "popis": "Profesionální barvení"
        }
    },
    
    "cenik": {
        "zakladni": {
            "nazev": "Základní služby",
            "polozky": [
                {"sluzba": "Pánské stříhání", "cena": "350 Kč"},
                {"sluzba": "Dámské stříhání", "cena": "400 Kč"},
                {"sluzba": "Dětské stříhání", "cena": "250 Kč"}
            ]
        },
        "specialni": {
            "nazev": "Speciální péče",
            "polozky": [
                {"sluzba": "Holení břitvou", "cena": "250 Kč"},
                {"sluzba": "Úprava vousů", "cena": "200 Kč"},
                {"sluzba": "Kompletní péče", "cena": "700 Kč"}
            ]
        },
        "doplnky": {
            "nazev": "Doplňkové služby",
            "polozky": [
                {"sluzba": "Barvení", "cena": "od 500 Kč"},
                {"sluzba": "Mytí vlasů", "cena": "100 Kč"}
            ]
        }
    },
    
    "rezervace": {
        "metody": ["Telefon: +420 735 744 433", "Online: www.barbershop.cz/rezervace", "Osobně v salonu"],
        "stornovani": "Zdarma při zrušení min. 3 hodiny předem",
        "platba": ["Hotově", "Kartou", "Apple Pay / Google Pay"]
    },
    
    "faq": {
        "rezervace": {
            "otazka": "Jak si mohu objednat termín?",
            "odpoved": "Můžete zavolat na +420 735 744 433, objednat online na webu, nebo přijít osobně."
        },
        "cena_strih": {
            "otazka": "Kolik stojí pánský střih?",
            "odpoved": "Pánské stříhání stojí 350 Kč a trvá asi 30 minut."
        },
        "oteviraci_doba": {
            "otazka": "Kdy máte otevřeno?",
            "odpoved": "Po-Pá 9-19h, Sobota 9-15h, Neděle zavřeno."
        },
        "bez_objednavky": {
            "otazka": "Můžu přijít bez objednání?",
            "odpoved": "Ano, ale doporučujeme rezervaci, abychom vám zaručili volný termín."
        },
        "platba": {
            "otazka": "Jak můžu zaplatit?",
            "odpoved": "Hotově, kartou, Apple Pay nebo Google Pay."
        },
        "parkovani": {
            "otazka": "Kde zaparkuju?",
            "odpoved": "Parkoviště je za rohem nebo veřejné parkování na Hlavní ulici."
        },
        "prvni_navsteva": {
            "otazka": "Co potřebuji k první návštěvě?",
            "odpoved": "Nic speciálního! Stačí přijít, máme vše potřebné."
        }
    },
    
    "typicke_dotazy": {
        "objednavka_termin": {
            "trigger": ["chci se objednat", "termín", "rezervace", "objednání"],
            "odpoved": "Samozřejmě! Na kdy byste chtěl termín? Máme volno zítra od 14h."
        },
        "cena_dotaz": {
            "trigger": ["kolik to stojí", "jaká je cena", "cena", "ceny"],
            "odpoved": "Pánský střih 350 Kč, dámský 400 Kč, holení 250 Kč. Co vás zajímá?"
        },
        "oteviraci_doba_dotaz": {
            "trigger": ["kdy máte otevřeno", "otevírací doba", "kdy otevíráte"],
            "odpoved": "Po-Pá 9-19h, Sobota 9-15h, Neděle zavřeno."
        },
        "kde_jste": {
            "trigger": ["kde jste", "adresa", "jak se k vám dostanu"],
            "odpoved": "Hlavní 123, Praha 1. Chcete zavolat navigaci?"
        },
        "stornovani": {
            "trigger": ["zrušit termín", "přesunout termín", "změnit"],
            "odpoved": "Žádný problém. Na jaké jméno máte rezervaci?"
        },
        "co_nabizite": {
            "trigger": ["co nabízíte", "jaké služby", "co děláte"],
            "odpoved": "Stříhání pánské, dámské, dětské, holení břitvou, úprava vousů. Co vás zajímá?"
        }
    },
    
    "dny_v_tydnu": {
        "pondeli": "9:00-19:00",
        "utery": "9:00-19:00",
        "streda": "9:00-19:00",
        "ctvrtek": "9:00-19:00",
        "patek": "9:00-19:00",
        "sobota": "9:00-15:00",
        "nedele": "zavřeno"
    }
}


# ============================================================
# FUNKCE PRO SALES (cold calling)
# ============================================================

def get_context_for_query(user_message):
    """
    Vyhledá relevantní kontext z SALES KB pro cold calling
    """
    context_parts = []
    msg_lower = user_message.lower().strip()
    
    # Skip krátké zprávy a pozdravy
    if len(msg_lower) < 10 or msg_lower in ['dobrý den', 'ahoj', 'dobry den', 'slyšíme se']:
        return ""
    
    # Detekce ceny
    price_keywords = ['kolik stojí', 'cena', 'kolik to', 'za kolik', 'platit']
    if any(keyword in msg_lower for keyword in price_keywords):
        context_parts.append("CENÍK:")
        context_parts.append("- One-page web: 8 000 Kč")
        context_parts.append("- Vícestránkový web: 12 000 Kč")
        context_parts.append("- Personalizované: od 12 000 Kč")
    
    # Detekce času
    time_keywords = ['jak dlouho', 'kdy', 'trvá', 'termín']
    if any(keyword in msg_lower for keyword in time_keywords):
        context_parts.append("REALIZACE: 2-4 týdny")
    
    # Detekce služeb
    service_keywords = ['co nabízíte', 'co děláte', 'jaké služby']
    if any(keyword in msg_lower for keyword in service_keywords):
        context_parts.append("SLUŽBY:")
        context_parts.append("- Weby na míru (ruční kódování)")
        context_parts.append("- SEO optimalizace")
        context_parts.append("- Rychlost a výkon")
    
    # Příležitost
    opportunity_phrases = ['nemáme web', 'nemám web', 'starý web', 'zastaralý', 'nefunguje']
    if any(phrase in msg_lower for phrase in opportunity_phrases):
        context_parts.append("🎯 PŘÍLEŽITOST! Nemá/špatný web!")
        context_parts.append("AKCE: Push na schůzku!")
    
    # Námitky
    kb = KNOWLEDGE_BASE['namitky_a_reseni']
    
    if any(word in msg_lower for word in ['drahé', 'nemám peníze']):
        namitka = kb['je_to_drahe']
        context_parts.append(f"NÁMITKA: {namitka['best_response']}")
    
    if any(word in msg_lower for word in ['nemám čas', 'teď ne', 'spěchám']):
        namitka = kb['nema_cas']
        context_parts.append(f"NÁMITKA: {namitka['best_response']}")
    
    if any(word in msg_lower for word in ['nemám zájem', 'nechci']):
        namitka = kb['nema_zajem']
        context_parts.append(f"HARD REJECTION → Rozluč se!")
    
    return "\n".join(context_parts) if context_parts else ""


def get_sales_prompt_with_kb(product, contact_name):
    """
    Sales prompt pro cold calling
    """
    prompt = f"""Jsi Pavel, obchodník z MoravskeWeby.
Voláš {contact_name} ohledně tvorby moderních webů.

INFO:
- Firma: MoravskeWeby (Lososs Web Development)
- Majitel: Ondřej Hyža, +420 735 744 433

CENY (říkej jen když se ptají):
- One-page: 8 000 Kč
- Vícestránkový: 12 000 Kč
- Na míru: od 12 000 Kč

CÍL: Domluvit SCHŮZKU s Ondrou nebo poslat nabídku

STYLE:
✅ Krátké odpovědi (max 1-2 věty!)
✅ Ptej se aktivně
✅ Reaguj na kontext
✅ Když PŘÍLEŽITOST (nemá web) → push na schůzku!
✅ Když NEZÁJEM → rozluč se

❌ Nedělej:
❌ Dlouhé monology
❌ Random odpovědi
❌ Ignorování zákazníka

REAKCE:
- "Uvažuji o webu" → "Skvělé! Máte už něco, nebo od nuly?"
- "Nemáme web" → "Bez webu ztrácíte zákazníky. Můžeme se sejít?"
- "Drahé" → "8k se vrátí hned. Kolik teď ztrácíte bez webu?"
- "Nemám čas" → "Chápu. Jen 2 minuty - máte moderní web?"
- "Nemám zájem" → "Rozumím, hezký den." (KONEC)

Mluv česky, přirozeně, max 1-2 věty!"""
    
    return prompt


# ============================================================
# FUNKCE PRO RECEPCI (příchozí hovory)
# ============================================================
def get_reception_context(user_message):
    """
    Vyhledá relevantní kontext z BARBER SHOP KB
    """
    context_parts = []
    msg_lower = user_message.lower().strip()
    
    # Skip krátké
    if len(msg_lower) < 5:
        return ""
    
    kb = RECEPTION_KB  # ✅ BARBER KB
    
    # Typické dotazy
    for key, dotaz in kb['typicke_dotazy'].items():
        if any(trigger in msg_lower for trigger in dotaz['trigger']):
            context_parts.append(f"TYP DOTAZU: {key}")
            context_parts.append(f"ODPOVĚĎ: {dotaz['odpoved']}")
    
    # FAQ
    for key, faq in kb['faq'].items():
        if any(word in msg_lower for word in faq['otazka'].lower().split()[:3]):
            context_parts.append(f"FAQ: {faq['odpoved']}")
    
    # Služby a ceny
    if any(word in msg_lower for word in ['cena', 'kolik', 'stojí', 'služby']):
        context_parts.append("CENÍK SLUŽEB:")
        context_parts.append("- Pánský střih: 350 Kč (30 min)")
        context_parts.append("- Dámský střih: 400 Kč (40 min)")
        context_parts.append("- Dětský střih: 250 Kč (20 min)")
        context_parts.append("- Holení: 250 Kč (20 min)")
        context_parts.append("- Vousy: 200 Kč (15 min)")
        context_parts.append("- Komplet: 700 Kč (60 min)")
    
    # Rezervace/Termín
    if any(word in msg_lower for word in ['objednat', 'termín', 'rezervace', 'volno']):
        context_parts.append("REZERVACE:")
        context_parts.append(f"Telefon: {kb['firma']['kontakt']['telefon']}")
        context_parts.append("Online: www.barbershop.cz/rezervace")
        context_parts.append("AKCE: Nabídni konkrétní časy (např. 14:00, 15:30, 17:00)")
    
    # Otevírací doba
    if any(word in msg_lower for word in ['otevřeno', 'otevírací', 'zavřeno']):
        context_parts.append("OTEVÍRACÍ DOBA:")
        context_parts.append("Po-Pá: 9:00-19:00")
        context_parts.append("Sobota: 9:00-15:00")
        context_parts.append("Neděle: zavřeno")
    
    # Adresa/Kde jste
    if any(word in msg_lower for word in ['kde', 'adresa', 'najdu', 'dostanu']):
        context_parts.append(f"ADRESA: {kb['firma']['kontakt']['adresa']}")
        context_parts.append("Parkoviště: za rohem nebo Hlavní ulice")
    
    return "\n".join(context_parts) if context_parts else ""

def get_receptionist_prompt():
    """
    Prompt pro BARBER SHOP recepčního
    """
    kb = RECEPTION_KB  # ✅ Tady se bere BARBER KB!
    
    prompt = f"""Jsi recepční barber shopu "{kb['firma']['nazev']}".
Přijímáš objednávky a zodpovídáš dotazy po telefonu.

INFO O SALONU:
- Název: {kb['firma']['nazev']}
- Telefon: {kb['firma']['kontakt']['telefon']}
- Adresa: {kb['firma']['kontakt']['adresa']}
- Otevírací doba: Po-Pá 9-19h, So 9-15h, Ne zavřeno

SLUŽBY A CENY:
- Pánský střih: 350 Kč (30 min)
- Dámský střih: 400 Kč (40 min)
- Dětský střih: 250 Kč (20 min)
- Holení břitvou: 250 Kč (20 min)
- Úprava vousů: 200 Kč (15 min)
- Kompletní péče: 700 Kč (60 min)

JAK KOMUNIKOVAT:
✅ Přátelský a profesionální tón
✅ VELMI KRÁTKÉ odpovědi (max 1-2 věty!)
✅ Odpovídej přesně na otázku
✅ Nabízej termíny - buď konkrétní!
✅ Neptej se zbytečně

❌ NEDĚLEJ:
❌ Dlouhé odpovědi
❌ Formální korporátní řeč
❌ Neptej se na jméno hned (ptej se až když rezervuješ)

PŘÍKLADY SPRÁVNÉ KOMUNIKACE:

Zákazník: "Kolik stojí pánský střih?"
✅ TY: "350 korun, trvá půl hodiny. Chcete se objednat?"

Zákazník: "Chtěl bych se objednat."
✅ TY: "Výborně! Kdy vám to vyhovuje? Zítra máme volno od 14h."

Zákazník: "Máte volno zítra odpoledne?"
✅ TY: "Ano, třeba 14:00, 15:30 nebo 17:00. Co vám vyhovuje?"

Zákazník: "14:00 by bylo fajn."
✅ TY: "Skvělé! Na jaké jméno to mám zapsat?"

Zákazník: "Kdy máte otevřeno?"
✅ TY: "Po-Pá 9-19h, Sobota 9-15h. Neděle zavřeno."

Zákazník: "Kde jste?"
✅ TY: "Hlavní 123, Praha 1. Je to kousek od metra."

Zákazník: "Kolik stojí holení?"
✅ TY: "250 korun, trvá 20 minut. Chcete se objednat?"

PRAVIDLA:
- MAX 1-2 věty za odpověď!
- Když rezervuje → zeptej se: Kdy? → Potvrď termín → Jméno → Hotovo!
- Buď konkrétní s časy (ne "odpoledne" - řekni "14:00, 15:30...")
- Neptej se zbytečně
- Buď přátelský ale profesionální

Mluv přirozeně česky, KRÁTCE a KONKRÉTNĚ!"""
    
    return prompt