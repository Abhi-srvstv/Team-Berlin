import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.voice_response import VoiceResponse

# Load env
load_dotenv()

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sms.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EmergencySMS:

    def __init__(self):
        self.sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone = os.getenv("TWILIO_PHONE_NUMBER")

        if self.sid and self.token:
            self.client = Client(self.sid, self.token)
        else:
            logger.warning("Twilio not configured")
            self.client = None

    # =========================
    # FORMAT MESSAGE
    # =========================
    def format_message(self, user, lat, lng):
        return f"""
EMERGENCY ALERT

User: {user}
Location: https://maps.google.com/?q={lat},{lng}
Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}

Send help immediately.
""".strip()

    # =========================
    # SEND SMS
    # =========================
    def send_sms(self, to, message):
        if not self.client:
            return False

        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.phone,
                to=to
            )
            logger.info(f"SMS sent: {msg.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"SMS failed: {e}")
            return False

    # =========================
    # VOICE CALL
    # =========================
    def send_call(self, to, message):
        if not self.client:
            return False

        try:
            response = VoiceResponse()
            response.say(message, voice='alice')

            call = self.client.calls.create(
                twiml=str(response),
                from_=self.phone,
                to=to
            )

            logger.info(f"Call sent: {call.sid}")
            return True

        except Exception as e:
            logger.error(f"Call failed: {e}")
            return False

    # =========================
    # MAIN ALERT SYSTEM
    # =========================
    def send_alert(self, user, contacts, lat, lng):

        if isinstance(contacts, str):
            contacts = json.loads(contacts)

        message = self.format_message(user, lat, lng)

        results = {
            "sms": 0,
            "calls": 0,
            "failed": 0
        }

        for contact in contacts:
            contact = contact.strip()

            if not contact.startswith("+"):
                contact = "+91" + contact.lstrip("0")

            # SMS
            if self.send_sms(contact, message):
                results["sms"] += 1

            # Delay for reliability
            time.sleep(0.5)

            # Call
            if self.send_call(contact, "Emergency alert. Please check SMS."):
                results["calls"] += 1
            else:
                results["failed"] += 1

        logger.info(f"Alert result: {results}")
        return results


# Global instance
sms_service = EmergencySMS()


# =========================
# HELPER FUNCTION (FOR FLASK)
# =========================
def trigger_alert(user, contacts, lat, lng):
    return sms_service.send_alert(user, contacts, lat, lng)


# =========================
# TEST
# =========================
if __name__ == "__main__":
    print("Testing system...")

    result = trigger_alert(
        "Test User",
        ["+91XXXXXXXXXX"],
        28.6139,
        77.2090
    )

    print(result)