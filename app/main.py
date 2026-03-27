import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from bot import procesar

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    numero = request.values.get("From", "")
    body   = request.values.get("Body", "").strip()
    resp   = MessagingResponse()
    procesar(numero, body, resp)
    return str(resp)

@app.route("/")
def home():
    return "E-Bot activo ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
