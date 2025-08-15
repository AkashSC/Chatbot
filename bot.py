import os
from flask import Flask, request
from twilio.rest import Client
from google.cloud import dialogflow_v2 as dialogflow
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# ==============================
# Load configuration from environment variables
# ==============================

# Dialogflow
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # Path to service account JSON
PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") # Default sandbox number

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize Dialogflow client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
dialogflow_session_client = dialogflow.SessionsClient()


# ==============================
# Webhook endpoint for WhatsApp via Twilio
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From')

    if not incoming_msg:
        return "No message received", 400

    # Unique session ID (could also be per user)
    session_id = from_number
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)

    # Send message to Dialogflow
    text_input = dialogflow.types.TextInput(text=incoming_msg, language_code='en')
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(
        session=session, query_input=query_input
    )

    reply_text = response.query_result.fulfillment_text or "I didn't understand that."

    # Send reply back via Twilio WhatsApp
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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
import os
from flask import Flask, request
from twilio.rest import Client
from google.cloud import dialogflow_v2 as dialogflow

app = Flask(__name__)

# ==============================
# Load configuration from environment variables
# ==============================

# Dialogflow
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # Path to service account JSON
PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") # Default sandbox number

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize Dialogflow client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
dialogflow_session_client = dialogflow.SessionsClient()


# ==============================
# Webhook endpoint for WhatsApp via Twilio
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From')

    if not incoming_msg:
        return "No message received", 400

    # Unique session ID (could also be per user)
    session_id = from_number
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)

    # Send message to Dialogflow
    text_input = dialogflow.types.TextInput(text=incoming_msg, language_code='en')
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(
        session=session, query_input=query_input
    )

    reply_text = response.query_result.fulfillment_text or "I didn't understand that."

    # Send reply back via Twilio WhatsApp
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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
    #app.run(port='5006', debug=True)