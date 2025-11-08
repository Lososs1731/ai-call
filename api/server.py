"""
Flask server pro Twilio webhooky + Admin Panel
OPRAVENO: Přihlášení, dashboard, statistiky
"""

# Flask imports
from flask import (
    Flask,
    request,
    Response,
    send_from_directory,
    render_template,
    redirect,
    url_for,
    jsonify,
    session,
    flash
)

# Twilio
from twilio.twiml.voice_response import VoiceResponse, Gather

# Standard library
import os
from pathlib import Path
from datetime import datetime
from functools import wraps

# Tvoje moduly
from core import TTSEngine
from services import ReceptionistService
from config import Prompts, Config
from database.cold_calling_db import ColdCallingDB
from database.admin_db import AdminDB

# ============================================================
# CESTY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

print("\n" + "=" * 60)
print("🔍 KONTROLA CEST")
print("=" * 60)
print(f"📁 BASE_DIR: {BASE_DIR}")
print(f"📁 TEMPLATE_DIR: {TEMPLATE_DIR}")
print(f"📁 Templates existuje? {TEMPLATE_DIR.exists()}")

if TEMPLATE_DIR.exists():
    templates = list(TEMPLATE_DIR.glob('*.html'))
    print(f"📄 Nalezené HTML soubory:")
    for t in templates:
        print(f"   ✓ {t.name}")
else:
    print("❌ SLOŽKA TEMPLATES NEEXISTUJE!")
print("=" * 60 + "\n")

# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path='/static'
)

# Secret key pro sessions
app.secret_key = 'zmenit-na-silne-heslo-2025'  # ← ZMĚŇ TO!

# Inicializuj služby
try:
    cold_db = ColdCallingDB()
    admin_db = AdminDB()
    receptionist = ReceptionistService()
    tts = TTSEngine()
    print("✅ Všechny služby inicializovány")
except Exception as e:
    print(f"❌ Chyba při inicializaci: {e}")
    raise


# ============================================================
# MIDDLEWARE - PŘIHLÁŠENÍ
# ============================================================

def login_required(f):
    """Decorator - vyžaduje přihlášení"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Musíte být přihlášeni', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# AUTH ROUTES
# ============================================================

@app.route('/')
def index():
    """Hlavní stránka - redirect na admin nebo login"""
    if 'user_id' in session:
        return redirect('/admin')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlášení"""
    # Pokud už je přihlášený, přesměruj
    if 'user_id' in session:
        return redirect('/admin')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = admin_db.verify_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Vítejte, {user["username"]}!', 'success')
            return redirect('/admin')
        else:
            flash('Nesprávné přihlašovací údaje', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registrace"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email', '')
        
        if len(password) < 6:
            flash('Heslo musí mít alespoň 6 znaků', 'error')
            return render_template('register.html')
        
        user_id = admin_db.create_user(username, password, email)
        
        if user_id:
            flash('Účet vytvořen! Můžete se přihlásit.', 'success')
            return redirect('/login')
        else:
            flash('Uživatelské jméno už existuje', 'error')
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Odhlášení"""
    username = session.get('username', 'Uživatel')
    session.clear()
    flash(f'Byl jste odhlášen', 'info')
    return redirect('/login')


# ============================================================
# ADMIN PANEL
# ============================================================

# api/server.py - UPRAVENÁ SEKCE ADMIN PANELU

# ... (začátek souboru zůstává stejný)

# ============================================================
# ADMIN PANEL - PROPOJENÉ S REAL DATY
# ============================================================

# api/server.py - OPRAVENÁ SEKCE ADMIN PANELU

@app.route('/admin')
@login_required
def admin_panel():
    """Hlavní admin panel - zobrazí kampaně z COLD_CALLING_DB"""
    user = admin_db.get_user(session['user_id'])
    
    try:
        # ✅ POUŽIJ COLD_CALLING_DB (ne CallAnalytics!)
        campaigns = cold_db.get_campaigns()
        
        # Přidej statistiky
        for campaign in campaigns:
            try:
                stats = cold_db.get_campaign_stats(campaign['id'])
                campaign.update(stats)
            except Exception as e:
                print(f"⚠️  Chyba stats: {e}")
        
        # Získej poslední hovory (pokud existují)
        try:
            from database.call_analytics import CallAnalytics
            analytics = CallAnalytics()
            recent_calls = analytics.get_all_calls(limit=10)
        except:
            recent_calls = []
        
        return render_template('admin_dashboard.html', 
                              user=user, 
                              campaigns=campaigns,
                              calls=recent_calls)
        
    except Exception as e:
        print(f"❌ Chyba: {e}")
        import traceback
        traceback.print_exc()
        
        flash(f'Chyba: {e}', 'error')
        return render_template('admin_dashboard.html', 
                              user=user, 
                              campaigns=[],
                              calls=[])


@app.route('/admin/calls')
@login_required
def admin_calls_list():
    """Seznam všech hovorů"""
    user = admin_db.get_user(session['user_id'])
    
    try:
        from database.call_analytics import CallAnalytics
        analytics = CallAnalytics()
        
        # Filtry
        outcome_filter = request.args.get('outcome', '')
        
        all_calls = analytics.get_all_calls()
        
        # Aplikuj filtr
        if outcome_filter:
            all_calls = [c for c in all_calls if c.get('outcome') == outcome_filter]
        
        return render_template('admin_calls.html',
                              user=user,
                              calls=all_calls,
                              outcome_filter=outcome_filter)
        
    except Exception as e:
        flash(f'Chyba: {e}', 'error')
        return redirect('/admin')


@app.route('/admin/call/<call_sid>')
@login_required
def admin_call_detail_real(call_sid):
    """Detail konkrétního hovoru - REAL DATA"""
    user = admin_db.get_user(session['user_id'])
    
    try:
        from database.call_analytics import CallAnalytics
        analytics = CallAnalytics()
        
        # Načti hovor
        call = analytics.get_call_by_sid(call_sid)
        
        if not call:
            flash('Hovor nenalezen', 'error')
            return redirect('/admin/calls')
        
        # Parsuj konverzaci
        import json
        try:
            if isinstance(call.get('conversation'), str):
                conversation = json.loads(call['conversation'])
            else:
                conversation = call.get('conversation', [])
        except:
            conversation = []
        
        # Vyfiltruj jen user/assistant zprávy (ne system)
        conversation = [msg for msg in conversation if msg.get('role') in ['user', 'assistant']]
        
        return render_template('admin_call_detail.html',
                              user=user,
                              call=call,
                              conversation=conversation)
        
    except Exception as e:
        flash(f'Chyba: {e}', 'error')
        return redirect('/admin/calls')


@app.route('/admin/export-all')
@login_required
def admin_export_all():
    """Export všech hovorů do CSV"""
    try:
        from database.call_analytics import CallAnalytics
        import csv
        from io import StringIO
        
        analytics = CallAnalytics()
        all_calls = analytics.get_all_calls()
        
        # Vytvoř CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'CallSid', 'Telefon', 'Délka (s)', 'Výsledek', 
            'Skóre', 'AI Shrnutí', 'Datum'
        ])
        
        # Data
        for call in all_calls:
            writer.writerow([
                call.get('call_sid', ''),
                call.get('contact_phone', ''),
                call.get('duration', 0),
                call.get('outcome', ''),
                call.get('sales_score', 0),
                call.get('ai_summary', '')[:100],
                call.get('started_at', '')
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=all_calls_export.csv'
            }
        )
        
    except Exception as e:
        flash(f'Chyba při exportu: {e}', 'error')
        return redirect('/admin')
    
# api/server.py - PŘIDEJ TUTO ROUTE

@app.route('/admin/create-campaign', methods=['POST'])
@login_required
def admin_create_campaign():
    """Vytvoř novou kampaň"""
    name = request.form.get('name')
    description = request.form.get('description', '')
    
    if not name:
        flash('Zadejte název kampaně', 'error')
        return redirect('/admin')
    
    try:
        campaign_id = cold_db.create_campaign(name, description)
        flash(f'Kampaň "{name}" vytvořena!', 'success')
        return redirect(f'/admin/campaign/{campaign_id}')
    except Exception as e:
        flash(f'Chyba: {e}', 'error')
        return redirect('/admin')
    
# api/server.py - PŘIDEJ

@app.route('/admin/campaign/<int:campaign_id>')
@login_required
def admin_campaign(campaign_id):
    """Detail kampaně"""
    user = admin_db.get_user(session['user_id'])
    
    try:
        stats = cold_db.get_campaign_stats(campaign_id)
        contacts = cold_db.get_contacts(campaign_id=campaign_id)
        calls = cold_db.get_calls(campaign_id=campaign_id)
        
        return render_template('admin_campaign.html',
                              user=user,
                              campaign_id=campaign_id,
                              stats=stats,
                              contacts=contacts,
                              calls=calls)
    except Exception as e:
        flash(f'Chyba: {e}', 'error')
        return redirect('/admin')


@app.route('/admin/add-contact', methods=['POST'])
@login_required
def admin_add_contact():
    """Přidej kontakt ručně"""
    campaign_id = int(request.form.get('campaign_id'))
    
    contact_id = cold_db.add_contact(
        campaign_id=campaign_id,
        name=request.form.get('name'),
        phone=request.form.get('phone'),
        company=request.form.get('company', ''),
        email=request.form.get('email', '')
    )
    
    if contact_id:
        flash('Kontakt přidán!', 'success')
    else:
        flash('Kontakt s tímto telefonem už existuje', 'error')
    
    return redirect(f'/admin/campaign/{campaign_id}')


# api/server.py - PŘIDEJ ROUTE

@app.route('/admin/call-detail/<int:call_id>')
@login_required
def admin_call_detail(call_id):
    """Detail hovoru s transkriptem"""
    user = admin_db.get_user(session['user_id'])
    
    try:
        # Najdi hovor v cold_calling_db
        all_calls = cold_db.get_calls()
        call = next((c for c in all_calls if c['id'] == call_id), None)
        
        if not call:
            flash('Hovor nenalezen', 'error')
            return redirect('/admin')
        
        # Parsuj transcript
        import json
        try:
            if call.get('transcript'):
                conversation = eval(call['transcript'])  # nebo json.loads
            else:
                conversation = []
        except:
            conversation = []
        
        return render_template('admin_call_detail.html',
                              user=user,
                              call=call,
                              conversation=conversation)
        
    except Exception as e:
        flash(f'Chyba: {e}', 'error')
        return redirect('/admin')
# ============================================================
# TWILIO WEBHOOKS (bez změny)
# ============================================================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servuje staticke soubory"""
    return send_from_directory(str(STATIC_DIR), filename)


@app.route("/voice", methods=['POST'])
@app.route("/inbound", methods=['POST'])
def inbound_call():
    """Příchozí hovory"""
    call_sid = request.values.get('CallSid')
    caller = request.values.get('From')
    
    print(f"\n{'='*50}")
    print(f"📞 PŘÍCHOZÍ HOVOR")
    print(f"Od: {caller}")
    print(f"CallSid: {call_sid}")
    print(f"{'='*50}")
    
    if call_sid in receptionist.ai.conversations:
        print(f"  ⚠️  Mažu starou konverzaci")
        del receptionist.ai.conversations[call_sid]
    
    greeting_text = receptionist.handle_call(call_sid, caller)
    response = VoiceResponse()
    
    try:
        audio_url = tts.generate(greeting_text, use_cache=True)
        if audio_url:
            response.play(audio_url)
        else:
            response.say(greeting_text, language='cs-CZ', voice='woman')
    except Exception as e:
        print(f"  ❌ TTS chyba: {e}")
        response.say(greeting_text, language='cs-CZ', voice='woman')
    
    gather = Gather(
        input='speech',
        action='/process?call_time=0',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=6,
        speech_model='phone_call',
        profanity_filter=False,
        enhanced=True,
        hints='dobrý den, objednání, termín, cena, otevřeno'
    )
    
    response.append(gather)
    response.redirect('/process?call_time=0')
    
    return Response(str(response), mimetype='text/xml')


# api/server.py - OPRAV OUTBOUND ROUTE

@app.route("/outbound", methods=['POST'])
def outbound_call():
    """Odchozí hovory - COLD CALLING s KB"""
    call_sid = request.values.get('CallSid')
    name = request.values.get('name', 'pane')
    company = request.values.get('company', '')
    campaign_id = request.values.get('campaign', '')
    
    print(f"\n{'='*50}")
    print(f"📞 ODCHOZÍ HOVOR (COLD CALLING)")
    print(f"Kontakt: {name}")
    print(f"Firma: {company}")
    print(f"Kampaň ID: {campaign_id}")
    print(f"CallSid: {call_sid}")
    print(f"{'='*50}")
    
    # Český pozdrav
    if company:
        greeting = f"Dobrý den, {name} z {company}, volám z MoravskéWeby"
    else:
        greeting = f"Dobrý den, {name}, volám z MoravskéWeby"
    
    print(f"  📝 Greeting: '{greeting}'")
    
    # ✅ POUŽIJ SALES PROMPT Z KNOWLEDGE BASE!
    try:
        from database.knowledge_base import get_sales_prompt_with_kb
        
        # Vytvoř dummy product pro KB
        product = {
            'id': 1,
            'name': 'Tvorba webů na míru',
            'description': 'Profesionální weby od 8 000 Kč'
        }
        
        sales_prompt = get_sales_prompt_with_kb(product, name)
        print(f"  ✅ Použit SALES prompt z KB!")
        
    except Exception as e:
        print(f"  ⚠️  KB nedostupná: {e}")
        sales_prompt = f"Jsi Pavel z MoravskéWeby. Voláš {name} ohledně tvorby webů."
    
    # Zahaj AI konverzaci
    receptionist.ai.start_conversation(call_sid, sales_prompt)
    
    # Přidej greeting do konverzace
    receptionist.ai.conversations[call_sid].append({
        'role': 'assistant',
        'content': greeting
    })
    
    # TwiML response
    response = VoiceResponse()
    
    try:
        audio_url = tts.generate(greeting, use_cache=True)
        if audio_url:
            response.play(audio_url)
        else:
            response.say(greeting, language='cs-CZ', voice='woman')
    except:
        response.say(greeting, language='cs-CZ', voice='woman')
    
    gather = Gather(
        input='speech',
        action='/process?call_time=0',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=15,
        profanity_filter=False,
        enhanced=True,
        hints='web, webové stránky, ano, ne, zájem'
    )
    
    response.append(gather)
    response.redirect('/process?call_time=0')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/process", methods=['POST'])
def process_speech():
    """Zpracování řeči"""
    call_sid = request.values.get('CallSid')
    user_input = request.values.get('SpeechResult', '')
    retry_count = int(request.values.get('retry', '0'))
    call_time = int(request.values.get('call_time', '0'))
    
    print(f"\n🎤 '{user_input}' (retry: {retry_count}, time: {call_time}s)")
    
    response = VoiceResponse()
    
    # Timeout
    if call_time >= 300:
        print("  ⏰ TIMEOUT")
        response.say("Musím ukončit hovor. Hezký den!", language='cs-CZ', voice='woman')
        response.hangup()
        return Response(str(response), mimetype='text/xml')
    
    # Prázdný vstup
    if not user_input or len(user_input.strip()) < 2:
        if retry_count >= 2:
            response.say("Omlouvám se, neslyším vás. Hezký den.", language='cs-CZ', voice='woman')
            response.hangup()
            return Response(str(response), mimetype='text/xml')
        
        gather = Gather(
            input='speech',
            action=f'/process?retry={retry_count + 1}&call_time={call_time + 4}',
            language='cs-CZ',
            speech_timeout='auto',
            timeout=6,
            speech_model='phone_call',
            profanity_filter=False,
            enhanced=True
        )
        gather.say("Neslyším vás dobře. Můžete zopakovat?", language='cs-CZ', voice='woman')
        response.append(gather)
        response.redirect(f'/process?retry={retry_count + 1}&call_time={call_time + 4}')
        return Response(str(response), mimetype='text/xml')
    
    # AI odpověď
    try:
        ai_reply = receptionist.process_message(call_sid, user_input)
        print(f"  AI: {ai_reply}")
        
        # Zkrať
        if len(ai_reply) > 200:
            ai_reply = ai_reply.split('.')[0] + '.'
        
        # Detekuj rozloučení
        goodbye_phrases = ['hezký den', 'nashledanou', 'děkuji za volání']
        is_goodbye = any(phrase in ai_reply.lower() for phrase in goodbye_phrases)
        
        try:
            audio_url = tts.generate(ai_reply, use_cache=True)
        except:
            audio_url = None
        
        if is_goodbye:
            print("  👋 ROZLOUČENÍ")
            if audio_url:
                response.play(audio_url)
            else:
                response.say(ai_reply, language='cs-CZ', voice='woman')
            response.hangup()
            receptionist.end_call(call_sid, call_time + 5)
            return Response(str(response), mimetype='text/xml')
        
        # Normální odpověď
        gather = Gather(
            input='speech',
            action=f'/process?retry=0&call_time={call_time + 8}',
            language='cs-CZ',
            speech_timeout='auto',
            timeout=6,
            speech_model='phone_call',
            profanity_filter=False,
            enhanced=True
        )
        
        if audio_url:
            gather.play(audio_url)
        else:
            gather.say(ai_reply, language='cs-CZ', voice='woman')
        
        response.append(gather)
        response.redirect(f'/process?retry=0&call_time={call_time + 8}')
        
        return Response(str(response), mimetype='text/xml')
        
    except Exception as e:
        print(f"  ❌ AI chyba: {e}")
        response.say("Omlouvám se, nastala chyba.", language='cs-CZ', voice='woman')
        response.hangup()
        return Response(str(response), mimetype='text/xml')

# api/server.py - OPRAV CALL-STATUS
# api/server.py - OPRAV CALL-STATUS

@app.route("/call-status", methods=['POST'])
def call_status():
    """Status callback - AI REPORT + uložení do cold_calling_db"""
    call_sid = request.values.get('CallSid')
    status = request.values.get('CallStatus')
    duration = request.values.get('CallDuration', 0)
    caller = request.values.get('From', '')
    to_number = request.values.get('To', '')
    
    print(f"\n{'='*50}")
    print(f"📊 STATUS UPDATE")
    print(f"CallSid: {call_sid}")
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    print(f"{'='*50}")
    
    try:
        duration = int(duration)
    except:
        duration = 0
    
    # ✅ ZÍSKEJ KONVERZACI PŘED end_call!
    conversation = []
    if call_sid in receptionist.ai.conversations:
        conversation = receptionist.ai.conversations[call_sid].copy()
        print(f"  ✅ Konverzace nalezena ({len(conversation)} zpráv)")
    else:
        print(f"  ⚠️  Konverzace už byla smazána!")
    
    # Ukonči hovor
    try:
        receptionist.end_call(call_sid, duration)
    except:
        pass
    
    # ✅ AI REPORT - POUZE pokud je completed a má konverzaci
    if status == 'completed' and duration >= 10 and len(conversation) > 2:
        print(f"\n{'='*60}")
        print(f"🤖 SPOUŠTÍM AI VYHODNOCENÍ")
        print(f"{'='*60}")
        
        try:
            from services.call_reporter import CallReporter
            from database.call_analytics import CallAnalytics
            
            reporter = CallReporter()
            analytics = CallAnalytics()
            
            # ✅ AI REPORT
            result = reporter.analyze_call(call_sid, conversation)
            
            if 'error' not in result:
                print(f"\n✅ AI REPORT VYGENEROVÁN!")
                print(f"   Výsledek: {result.get('outcome', 'N/A')}")
                print(f"   Skóre: {result.get('sales_score', 0)}/100")
                print(f"   Shrnutí: {result.get('ai_summary', 'N/A')[:100]}...")
                
                # ✅ ULOŽ DO CALL_ANALYTICS
                call_data = {
                    'call_sid': call_sid,
                    'contact_phone': to_number if to_number.startswith('+420') else caller,
                    'duration': duration,
                    'conversation': conversation,
                    'started_at': None,
                    'ended_at': None,
                    **result
                }
                
                analytics.save_call(call_data)
                print(f"   ✅ Uloženo do call_analytics!")
                
                # ✅ ULOŽ TAKÉ DO COLD_CALLING_DB
                try:
                    # Najdi kontakt podle telefonu
                    phone = to_number if to_number.startswith('+420') else caller
                    contacts = cold_db.get_contacts()
                    contact = next((c for c in contacts if c['phone'] == phone), None)
                    
                    if contact:
                        cold_db.save_call(
                            contact_id=contact['id'],
                            call_sid=call_sid,
                            phone=phone,
                            duration=duration,
                            status='completed',
                            outcome=result.get('outcome', ''),
                            sales_score=result.get('sales_score', 0),
                            ai_summary=result.get('ai_summary', ''),
                            transcript=str(conversation)
                        )
                        print(f"   ✅ Uloženo do cold_calling_db!")
                    else:
                        print(f"   ⚠️  Kontakt {phone} nenalezen v cold_calling_db")
                        
                except Exception as e:
                    print(f"   ⚠️  Cold calling DB error: {e}")
                
            else:
                print(f"\n❌ Report error: {result['error']}")
                
        except Exception as e:
            print(f"\n❌ Report failed: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print(f"  ⚠️  Přeskakuji AI report (status={status}, duration={duration}s, msgs={len(conversation)})")
    
    return Response('OK', mimetype='text/plain')


@app.route("/health", methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'AI Phone Assistant'})


# ============================================================
# SPUŠTĚNÍ
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("   🔐 AI ASISTENT + ADMIN PANEL")
    print("=" * 60)
    print(f"Server: http://localhost:{Config.SERVER_PORT}")
    print(f"Admin: http://localhost:{Config.SERVER_PORT}/admin")
    print(f"Login: http://localhost:{Config.SERVER_PORT}/login")
    print("=" * 60)
    
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=Config.DEBUG
    )