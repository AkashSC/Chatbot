import os
import json
from flask import Flask, request
from twilio.rest import Client
from google.cloud import dialogflow_v2 as dialogflow
from dotenv import load_dotenv
from google.oauth2 import service_account

# Load .env when running locally
load_dotenv()

app = Flask(__name__)

# ==============================
# Load configuration from environment variables
# ==============================
PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Google service account JSON from env variable
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")  # Entire JSON as string

if not GOOGLE_CREDENTIALS_JSON:
    raise ValueError("Missing GOOGLE_CREDENTIALS_JSON environment variable.")

# Create credentials object from JSON string
credentials_info = json.loads(GOOGLE_CREDENTIALS_JSON)
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Initialize clients
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
dialogflow_session_client = dialogflow.SessionsClient(credentials=credentials)


# ==============================
# Webhook endpoint for WhatsApp via Twilio
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From')

    if not incoming_msg:
        return "No message received", 400

    # Create a unique session for the user
    session_id = from_number
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)

    # Send text to Dialogflow
    text_input = dialogflow.types.TextInput(text=incoming_msg, language_code='en')
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(
        session=session, query_input=query_input
    )

    reply_text = response.query_result.fulfillment_text or "I didn't understand that."

    # Reply back to WhatsApp via Twilio
    twilio_client.messages.create(
        body=reply_text,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=from_number
    )

    return "OK", 200


# ==============================
# Health check route
# ==============================
@app.route("/", methods=["GET"])
def health():
    return "WhatsApp + Dialogflow Bot is running!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)), debug=True)
