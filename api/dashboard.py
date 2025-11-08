# dashboard.py
"""
Web dashboard pro cold calling kampaně
"""

from flask import Flask, render_template, request, jsonify, send_file
from database.cold_calling_db import ColdCallingDB
import csv
from io import StringIO

app = Flask(__name__)
db = ColdCallingDB()


@app.route('/')
def index():
    """Hlavní stránka - přehled kampaní"""
    campaigns = db.get_campaigns()
    return render_template('dashboard.html', campaigns=campaigns)


@app.route('/campaign/<int:campaign_id>')
def campaign_detail(campaign_id):
    """Detail kampaně"""
    stats = db.get_campaign_stats(campaign_id)
    contacts = db.get_contacts(campaign_id=campaign_id)
    calls = db.get_calls(campaign_id=campaign_id)
    
    return render_template('campaign_detail.html', 
                          campaign_id=campaign_id,
                          stats=stats,
                          contacts=contacts,
                          calls=calls)


@app.route('/contact/<int:contact_id>')
def contact_detail(contact_id):
    """Detail kontaktu"""
    contacts = db.get_contacts()
    contact = next((c for c in contacts if c['id'] == contact_id), None)
    calls = db.get_calls(contact_id=contact_id)
    
    return render_template('contact_detail.html', 
                          contact=contact,
                          calls=calls)


@app.route('/export/<int:campaign_id>')
def export_campaign(campaign_id):
    """Export kampaně do CSV"""
    contacts = db.get_contacts(campaign_id=campaign_id)
    calls_dict = {}
    
    for call in db.get_calls(campaign_id=campaign_id):
        calls_dict[call['contact_id']] = call
    
    # Vytvoř CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Jméno', 'Firma', 'Telefon', 'Email', 
        'Status', 'Výsledek', 'Skóre', 'Délka hovoru (s)', 
        'AI Shrnutí', 'Datum'
    ])
    
    # Data
    for contact in contacts:
        call = calls_dict.get(contact['id'], {})
        writer.writerow([
            contact['name'],
            contact.get('company', ''),
            contact['phone'],
            contact.get('email', ''),
            contact['status'],
            call.get('outcome', ''),
            call.get('sales_score', 0),
            call.get('duration', 0),
            call.get('ai_summary', ''),
            call.get('created_at', '')
        ])
    
    # Vrať CSV
    output.seek(0)
    return send_file(
        StringIO(output.getvalue()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'campaign_{campaign_id}_export.csv'
    )


if __name__ == '__main__':
    print("=" * 60)
    print("   📊 COLD CALLING DASHBOARD")
    print("=" * 60)
    print("   Dashboard: http://localhost:5001")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)