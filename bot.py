import os
import json
from flask import Flask, request
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account

app = Flask(__name__)

# ---- Load Dialogflow credentials from Render secret ----
# Make sure you set GOOGLE_APPLICATION_CREDENTIALS in Render's environment variables
creds_dict = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
credentials = service_account.Credentials.from_service_account_info(creds_dict)

# ---- Your Dialogflow setup ----
PROJECT_ID = "pizzabot-tbot"  # change to your project id
SESSION_ID = "whatsapp-session"
LANGUAGE_CODE = "en"

def detect_intent_texts(text, session_id=SESSION_ID):
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session = session_client.session_path(PROJECT_ID, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text

# ---- Webhook for Twilio WhatsApp ----
@app.route("/webhook", methods=["POST"])
def webhook():
    from twilio.twiml.messaging_response import MessagingResponse

    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()

    if incoming_msg:
        reply = detect_intent_texts(incoming_msg)
        resp.message(reply)

    return str(resp)

@app.route("/")
def home():
    return "WhatsApp + Dialogflow bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
