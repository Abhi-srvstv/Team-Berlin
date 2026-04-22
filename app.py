from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from datetime import datetime
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV
# =========================
load_dotenv(dotenv_path=".env")

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///she_safe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# SOCKET
# =========================
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

# =========================
# TWILIO
# =========================
from twilio.rest import Client

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

print("SID:", TWILIO_SID)
print("TOKEN:", TWILIO_TOKEN)
print("NUMBER:", TWILIO_NUMBER)

client = None
if TWILIO_SID and TWILIO_TOKEN and TWILIO_NUMBER:
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    print("✅ Twilio Connected")
else:
    print("❌ Twilio not configured")

# =========================
# MODEL
# =========================
class SafetyAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    address = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# =========================
# ROUTES
# =========================
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/sos', methods=['POST'])
def sos():
    try:
        data = request.get_json()

        lat = data.get('lat')
        lng = data.get('lng')

        # ✅ fallback (IMPORTANT FIX)
        if not lat or not lng:
            print("⚠️ Using fallback location")
            lat, lng = 28.6139, 77.2090

        print("📍 SOS:", lat, lng)

        alert = SafetyAlert(
            user_id=1,
            lat=lat,
            lng=lng,
            address="Live Location"
        )
        db.session.add(alert)
        db.session.commit()

        numbers = [
            "+916396462355",
            "+919508944533"
        ]

        if client:
            for number in numbers:
                try:
                    msg = client.messages.create(
                        body=f"SOS ALERT!\nhttps://maps.google.com/?q={lat},{lng}",
                        from_=TWILIO_NUMBER,
                        to=number
                    )
                    print("✅ SMS SENT:", msg.sid)
                except Exception as e:
                    print("❌ TWILIO ERROR:", e)

        socketio.emit("new_alert", {"msg": "SOS Triggered"})

        return jsonify({"status": "success"})

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": "server error"}), 500


# =========================
# RUN
# =========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    socketio.run(app, host="0.0.0.0", port=5002)