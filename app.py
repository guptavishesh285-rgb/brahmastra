import os
import mimetypes
import sqlite3
import urllib.parse
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

# Ensure Windows recognizes modern image types like AVIF
mimetypes.add_type("image/avif", ".avif")
mimetypes.add_type("image/webp", ".webp")

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "surakshayatra.db")
STATIC_DIR = os.path.join(BASE_DIR, "static")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema_path = os.path.join(BASE_DIR, "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = f.read()
        conn = get_db()
        conn.executescript(schema)
        conn.commit()
        conn.close()

if not os.path.exists(DATABASE):
    init_db()

@app.route("/")
def index():
    return render_template("index.html")

# Serves images whether the user saved them in static/ OR in the project root folder
@app.route("/static/<path:filename>")
def serve_static(filename):
    decoded_name = urllib.parse.unquote(filename)
    # 1. Check inside static/
    if os.path.exists(os.path.join(STATIC_DIR, decoded_name)):
        return send_from_directory(STATIC_DIR, decoded_name)
    # 2. Check inside project root as fallback
    if os.path.exists(os.path.join(BASE_DIR, decoded_name)):
        return send_from_directory(BASE_DIR, decoded_name)
    return ("File not found", 404)

@app.route("/<path:filename>")
def serve_root_fallback(filename):
    decoded_name = urllib.parse.unquote(filename)
    if os.path.exists(os.path.join(STATIC_DIR, decoded_name)):
        return send_from_directory(STATIC_DIR, decoded_name)
    if os.path.exists(os.path.join(BASE_DIR, decoded_name)):
        return send_from_directory(BASE_DIR, decoded_name)
    return ("Not Found", 404)

# ================= API ENDPOINTS =================

@app.route("/api/safety", methods=["GET"])
def get_safety():
    location = request.args.get("location", "New Delhi")
    
    city_defaults = {
        "New Delhi": {
            "safety_score": 92,
            "hygiene_index": 88,
            "route": {
                "name": "Red Fort → Chandni Chowk",
                "meta": "1.8 km • 24 min • Well-lit • High footfall",
                "score": 94
            }
        },
        "Jaipur": {
            "safety_score": 94,
            "hygiene_index": 91,
            "route": {
                "name": "Hawa Mahal → Johari Bazaar",
                "meta": "1.2 km • 16 min • Well-lit • High footfall",
                "score": 96
            }
        },
        "Goa": {
            "safety_score": 89,
            "hygiene_index": 86,
            "route": {
                "name": "Calangute → Fort Aguada",
                "meta": "3.4 km • 31 min • Lit • Active services",
                "score": 91
            }
        }
    }
    
    data = city_defaults.get(location, city_defaults["New Delhi"])
    return jsonify(data)

@app.route("/api/guides", methods=["GET"])
def get_guides():
    location = request.args.get("location", "New Delhi")
    
    guides_list = [
        {
            "name": "Arjun Mehta",
            "area": "Heritage & Street Food",
            "rating": "4.9",
            "price": "₹600 / tour",
            "initials": "AM",
            "photo": "/static/arjun.jpg",
            "bio": f"Local verified heritage guide specializing in historic walks and food corridors across {location}."
        },
        {
            "name": "Meera Sharma",
            "area": "Culture & Local Life",
            "rating": "4.8",
            "price": "₹750 / tour",
            "initials": "MS",
            "photo": "/static/Meera Sharma.avif",
            "bio": f"Culture-focused guide for traditional markets, craft museums and neighborhood experiences in {location}."
        },
        {
            "name": "Rohan Khan",
            "area": "Markets & Night Walks",
            "rating": "4.9",
            "price": "₹500 / tour",
            "initials": "RK",
            "photo": "/static/Rohan Khan.jpg",
            "bio": f"Verified escort guide ensuring safe, well-lit evening walks and shopping corridors in {location}."
        }
    ]
    return jsonify(guides_list)

@app.route("/api/sos", methods=["POST"])
def trigger_sos():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id", "demo-traveller")
    lat = payload.get("latitude")
    lng = payload.get("longitude")
    city = payload.get("city", "New Delhi")
    
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO incidents (user_id, emergency_type, latitude, longitude, city, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, "SOS", lat, lng, city, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        app.logger.warning(f"DB insert skipped: {e}")
        
    loc_str = f"https://maps.google.com/?q={lat},{lng}" if lat and lng else "Location unavailable"
    return jsonify({
        "status": "success",
        "message": f"SOS alert logged in {city}. Emergency link: {loc_str}",
        "whatsapp_url": f"https://wa.me/?text={urllib.parse.quote(f'EMERGENCY SOS: {loc_str}')}" if lat else None
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)