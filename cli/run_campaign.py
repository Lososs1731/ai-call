# cli/run_campaign.py - OPRAVENÁ VERZE (původní struktura)
"""
Spusteni cold calling kampane z prikazove radky

Pouziti:
    python -m cli.run_campaign
"""

from services.cold_caller import ColdCallerService
from database.cold_calling_db import ColdCallingDB  # ← ZMĚNA!
import sys


def main():
    print("=" * 60)
    print("   COLD CALLING - SPUSTENI KAMPANE")
    print("=" * 60)
    
    # ✅ Inicializace COLD_CALLING_DB
    db = ColdCallingDB()
    
    # ✅ 1. Vyber kampaně
    print("\nDostupne kampane:")
    campaigns = db.get_campaigns()
    
    if not campaigns:
        print("CHYBA: Zadne kampane v databazi!")
        print("\n💡 Vytvor kampan v admin panelu:")
        print("   http://localhost:5000/admin")
        sys.exit(1)
    
    for i, campaign in enumerate(campaigns, 1):
        stats = db.get_campaign_stats(campaign['id'])
        print(f"\n  {i}. {campaign['name']}")
        print(f"     {campaign['description']}")
        print(f"     Kontaktu: {stats['total_contacts']} ({stats['pending']} ceka)")
    
    campaign_choice = input(f"\nVyber kampan (1-{len(campaigns)}): ").strip()
    
    try:
        campaign_idx = int(campaign_choice) - 1
        selected_campaign = campaigns[campaign_idx]
    except (ValueError, IndexError):
        print("CHYBA: Neplatna volba")
        sys.exit(1)
    
    print(f"\n✓ Vybrana kampan: {selected_campaign['name']}")
    
    # ✅ 2. Ziskani ngrok URL
    print("\n" + "=" * 60)
    print("NASTAVENI WEBHOOKU")
    print("=" * 60)
    print("1. Ujisti se, ze mas spusteny server (python run.py)")
    print("2. Zkopiruj ngrok URL z terminu serveru")
    
    ngrok_url = input("\nZadej ngrok URL (https://...): ").strip()
    
    if not ngrok_url.startswith('https://'):
        print("CHYBA: URL musi zacinat https://")
        sys.exit(1)
    
    # ✅ 3. Kontrola kontaktu
    contacts = db.get_contacts(
        campaign_id=selected_campaign['id'],
        status='pending'
    )
    
    if not contacts:
        print("\n" + "=" * 60)
        print("CHYBA: Zadne kontakty v kampani!")
        print("=" * 60)
        print("\nImportuj kontakty:")
        print("  python -m cli.import_contacts")
        print(f"  → Vyber kampan ID: {selected_campaign['id']}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("KONTAKTY K ZAVOLANI")
    print("=" * 60)
    print(f"\nNalezeno {len(contacts)} kontaktu:")
    for i, contact in enumerate(contacts[:5], 1):
        print(f"  {i}. {contact['name']} - {contact['phone']}")
        if contact.get('company'):
            print(f"     {contact['company']}")
    if len(contacts) > 5:
        print(f"  ... a dalsich {len(contacts) - 5}")
    
    # ✅ 4. Kolik hovoru
    max_calls = input(f"\nKolik hovoru chces uskutecnit? (max {len(contacts)}): ").strip()
    
    try:
        max_calls = int(max_calls)
        if max_calls < 1 or max_calls > len(contacts):
            raise ValueError()
    except ValueError:
        print("CHYBA: Zadej cislo mezi 1 a", len(contacts))
        sys.exit(1)
    
    # ✅ 5. Potvrzeni
    print("\n" + "=" * 60)
    print("POTVRZENI")
    print("=" * 60)
    print(f"Kampan: {selected_campaign['name']}")
    print(f"Pocet hovoru: {max_calls}")
    print(f"Kontakty: {', '.join([c['name'] for c in contacts[:max_calls]])}")
    
    confirm = input(f"\nOpravdu spustit kampan? (ano/ne): ").strip().lower()
    
    if confirm not in ['ano', 'a', 'yes', 'y']:
        print("Zruseno")
        sys.exit(0)
    
    # ✅ 6. Vytvoreni a spusteni kampane
    print("\n" + "=" * 60)
    print("SPOUSTIM KAMPAN...")
    print("=" * 60)
    
    try:
        # ✅ POUŽIJ ColdCallerService s názvem kampaně
        caller = ColdCallerService(
            campaign_name=selected_campaign['name']
        )
        
        caller.run_campaign(
            webhook_base_url=ngrok_url,
            max_calls=max_calls
        )
        
    except Exception as e:
        print(f"\nCHYBA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ✅ 7. Vysledky
    print("\n" + "=" * 60)
    print("KAMPAN DOKONCENA!")
    print("=" * 60)
    
    # Statistiky z cold_calling_db
    stats = db.get_campaign_stats(selected_campaign['id'])
    print(f"\nStatistiky kampane:")
    print(f"  Celkem kontaktu: {stats['total_contacts']}")
    print(f"  Zavolano: {stats['called']}")
    print(f"  Uspesnych: {stats['success']}")
    print(f"  Neuspesnych: {stats['failed']}")
    print(f"  Uspesnost: {stats['success_rate']}%")
    
    print(f"\n💡 Sleduj vysledky:")
    print(f"   http://localhost:5000/admin/campaign/{selected_campaign['id']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKampan prerusena uzivatelem")
        sys.exit(0)
    except Exception as e:
        print(f"\nNEOCEKAVANA CHYBA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)