"""
Flask server pro Twilio webhooky
"""

from flask import Flask, request, Response, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
import os

from core import TTSEngine
from services import ReceptionistService
from config import Prompts, Config

app = Flask(__name__, static_folder='../static', static_url_path='/static')

receptionist = ReceptionistService()
tts = TTSEngine()


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servuje staticke soubory"""
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_dir, filename)


@app.route("/voice", methods=['POST'])
@app.route("/inbound", methods=['POST'])
def inbound_call():
    """Prichozi hovory"""
    call_sid = request.values.get('CallSid')
    caller = request.values.get('From')
    
    print(f"\n{'='*50}")
    print(f"PRICHOZI HOVOR")
    print(f"Od: {caller}")
    print(f"CallSid: {call_sid}")
    print(f"{'='*50}")
    
    greeting = receptionist.handle_call(call_sid, caller)
    
    response = VoiceResponse()
    
    try:
        audio_url = tts.generate(greeting, use_cache=True)
        if audio_url:
            print(f"  Pouzivam TTS: {audio_url}")
            response.play(audio_url)
        else:
            print("  Pouzivam Twilio TTS")
            response.say(greeting, language='cs-CZ', voice='woman')
    except Exception as e:
        print(f"TTS chyba: {e}")
        response.say(greeting, language='cs-CZ', voice='woman')
    
    gather = Gather(
        input='speech',
        action='/process',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=10,
        profanity_filter=False
    )
    
    response.append(gather)
    response.redirect('/voice')
    
    return Response(str(response), mimetype='text/xml')
@app.route("/outbound", methods=['POST'])
def outbound_call():
    """Odchozi hovory - POUZE ELEVENLABS"""
    call_sid = request.values.get('CallSid')
    name = request.values.get('name', 'pane')
    company = request.values.get('company', '')
    product_id = request.values.get('product_id', 1)
    pregenerated = request.values.get('pregenerated', '0')
    
    print(f"\n{'='*50}")
    print(f"📞 ODCHOZI HOVOR")
    print(f"Kontakt: {name}")
    print(f"Firma: {company}")
    print(f"CallSid: {call_sid}")
    print(f"Pregenerated: {pregenerated}")
    print(f"{'='*50}")
    
    from database import CallDB
    db = CallDB()
    product = db.get_product_by_name("Tvorba webů na míru")
    
    # STEJNÝ TEXT jako v cold_caller!
    if company:
        greeting = f"Dobry den, {name} z {company}, volam z Lososs Web Development."
    else:
        greeting = f"Dobry den, {name}, volam z Lososs Web Development."
    
    print(f"  📝 Pozdrav: {greeting}")
    
    # Zahaj AI konverzaci
    sales_prompt = Prompts.get_sales_prompt(product, name)
    receptionist.ai.start_conversation(call_sid, sales_prompt)
    
    response = VoiceResponse()
    
    # GENERUJ TTS (použije cache pokud existuje)
    print("  🔍 Hledám/generuji TTS audio...")
    
    try:
        audio_url = tts.generate(greeting, use_cache=True)
        
        if audio_url:
            # Zkontroluj že soubor OPRAVDU existuje
            import os
            
            # Relativní cesta → absolutní
            if audio_url.startswith('/static/'):
                audio_path = audio_url.replace('/static/', 'static/').replace('/', os.sep)
            else:
                audio_path = f"static/{audio_url}"
            
            print(f"  📂 Cesta k souboru: {audio_path}")
            
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"  ✅ Audio nalezeno! Velikost: {file_size} bytes")
                
                # Přehraj POUZE ElevenLabs
                response.play(audio_url)
            else:
                print(f"  ❌ Soubor NEEXISTUJE: {audio_path}")
                print(f"  🔇 Dávám ticho místo špatného hlasu")
                response.pause(length=2)
        else:
            print(f"  ❌ TTS vrátilo None")
            print(f"  🔇 Dávám ticho")
            response.pause(length=2)
            
    except Exception as e:
        print(f"  ❌ TTS CHYBA: {e}")
        import traceback
        traceback.print_exc()
        print(f"  🔇 Dávám ticho")
        response.pause(length=2)
    
    # Gather pro odpověď
    gather = Gather(
        input='speech',
        action='/process',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=15,
        profanity_filter=False,
        hints='web, webové stránky, ano, ne, děkuji, zajem'
    )
    
    response.append(gather)
    response.redirect('/voice')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/process", methods=['POST'])
def process_speech():
    """Zpracovani reci"""
    call_sid = request.values.get('CallSid')
    user_input = request.values.get('SpeechResult', '')
    
    print(f"\nUzivatel: {user_input}")
    
    response = VoiceResponse()
    
    if not user_input:
        response.say("Nerozumel jsem.", language='cs-CZ', voice='woman')
        response.redirect('/voice')
        return Response(str(response), mimetype='text/xml')
    
    try:
        ai_reply = receptionist.process_message(call_sid, user_input)
        print(f"AI: {ai_reply}")
        
        if len(ai_reply) > 200:
            sentences = ai_reply.split('.')
            ai_reply = '. '.join(sentences[:2]) + '.'
        
        audio_url = tts.generate(ai_reply, use_cache=True)
        
        if audio_url:
            print(f"  Pouzivam TTS: {audio_url}")
            response.play(audio_url)
        else:
            response.say(ai_reply, language='cs-CZ', voice='woman')
            
    except Exception as e:
        print(f"Chyba: {e}")
        response.say("Omlouvam se, nastala chyba.", language='cs-CZ', voice='woman')
    
    gather = Gather(
        input='speech',
        action='/process',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=15,
        profanity_filter=False
    )
    
    response.append(gather)
    response.redirect('/voice')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/call-status", methods=['POST'])
def call_status():
    """Status callback"""
    call_sid = request.values.get('CallSid')
    status = request.values.get('CallStatus')
    duration = request.values.get('CallDuration', 0)
    
    print(f"\n{'='*50}")
    print(f"STATUS UPDATE")
    print(f"CallSid: {call_sid}")
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    print(f"{'='*50}")
    
    try:
        receptionist.end_call(call_sid, int(duration))
    except Exception as e:
        print(f"Chyba: {e}")
    
    return Response('OK', mimetype='text/plain')


@app.route("/health", methods=['GET'])
def health():
    """Health check"""
    return {'status': 'ok', 'service': 'AI Phone Assistant'}


if __name__ == "__main__":
    print("=" * 60)
    print("   AI TELEFONNI ASISTENT - SERVER")
    print("=" * 60)
    print(f"Server: http://localhost:{Config.SERVER_PORT}")
    print(f"Cislo: {Config.TWILIO_PHONE_NUMBER}")
    print(f"Static: {app.static_folder}")
    print("\nEndpointy:")
    print("  /voice       - Prichozi hovory")
    print("  /inbound     - Prichozi hovory")
    print("  /outbound    - Odchozi hovory")
    print("  /process     - Zpracovani reci")
    print("  /call-status - Status callback")
    print("  /health      - Health check")
    print("  /static/*    - Audio soubory")
    print("=" * 60)
    
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=Config.DEBUG
    )