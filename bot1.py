import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google.cloud import dialogflow_v2 as dialogflow
from dotenv import load_dotenv

# Load environment variables from .env (only in local dev)
load_dotenv()

# Flask app
app = Flask(__name__)

# Get credentials from env
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

# Ensure Google credentials file path is set for Dialogflow
if not GOOGLE_APPLICATION_CREDENTIALS:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in environment variables")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# Dialogflow session client
PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")
SESSION_ID = "whatsapp-session"
LANGUAGE_CODE = "en"

session_client = dialogflow.SessionsClient()

@app.route("/webhook", methods=["POST"])
def webhook():
    """Webhook endpoint for Twilio WhatsApp"""
    incoming_msg = request.form.get("Body")
    sender_id = request.form.get("From")

    # Send message to Dialogflow
    session = session_client.session_path(PROJECT_ID, SESSION_ID)
    text_input = dialogflow.TextInput(text=incoming_msg, language_code=LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(request={"session": session, "query_input": query_input})

    bot_reply = response.query_result.fulfillment_text

    # Reply back to WhatsApp
    twiml_resp = MessagingResponse()
    twiml_resp.message(bot_reply)
    return str(twiml_resp)

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp + Dialogflow bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)