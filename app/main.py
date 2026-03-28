from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("✅ Bot activo! Funciona.")
    return str(resp)

@app.route("/")
def home():
    return "E-Bot activo ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

Y el `Procfile`:
```
web: python app/main.py
