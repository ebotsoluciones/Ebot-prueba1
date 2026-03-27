from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "OK ROOT"

@app.route("/webhook", methods=["GET","POST"])
def webhook():
    return "OK WEBHOOK"
