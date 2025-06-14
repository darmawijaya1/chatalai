from flask import Flask, send_from_directory, request, jsonify, session, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from openai import AzureOpenAI
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import re
import csv

# === Config Variables (TANPA .env) ===
SECRET_KEY = "supersecretkey"
DATABASE_URI = "mysql+pymysql://root:rootpassword@localhost/mydatabase"

AZURE_API_KEY = "EDCcDvLQI5S4vhQbNHPiqc2bd3BHP3WRRHaIbiWHZEXWVtDYIkyWJQQJ99BFACfhMk5XJ3w3AAAAACOG62XY"
AZURE_ENDPOINT = "https://adarm-mbp20fil-swedencentral.services.ai.azure.com/"
AZURE_DEPLOYMENT = "gpt-4.1curhat"

# === Azure OpenAI Client ===
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version="2023-05-15",
    azure_endpoint=AZURE_ENDPOINT
)

# === Flask App Setup ===
app = Flask(__name__, static_folder='assets')
app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



# === User Loader ===
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === Mood Detection ===
def detect_mood(text):
    text = text.lower()
    if re.search(r"\bsedih|menangis|kecewa|terluka\b", text):
        return "Sad"
    elif re.search(r"\bcemas|khawatir|takut|panik\b", text):
        return "Anxious"
    elif re.search(r"\bmarah|kesal|geram\b", text):
        return "Angry"
    elif re.search(r"\bsenang|bahagia|lega|bersyukur\b", text):
        return "Happy"
    else:
        return "Neutral"

# === Risk Keyword Detection ===
def check_risk_keywords(text):
    risk_keywords = [
        "suicide", "self-harm", "want to disappear", "end it all", "too tired", "end my life"
    ]
    return any(keyword in text.lower() for keyword in risk_keywords)

# === Logging Function ===
def log_chat(user_message, mood, reply):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "message": user_message,
        "mood": mood,
        "reply": reply
    }
    with open("chat_logs.csv", "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=log_data.keys())
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(log_data)

# === Routes ===

@app.route("/")
def index():
    return send_from_directory(os.getcwd(), "index.html")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/chat", methods=["GET"])
def chat_page():
    return render_template("chat/chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.form.get("message", "")

        if check_risk_keywords(user_message):
            emergency_reply = (
                "💡 I hear you, and I care deeply. "
                "If you feel overwhelmed or have thoughts of self-harm, please reach out to someone you trust or a professional service."
            )
            log_chat(user_message, detect_mood(user_message), emergency_reply)
            return jsonify({"reply": emergency_reply})

        mood = detect_mood(user_message)

        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a compassionate, friendly, and professional AI psychologist..."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        log_chat(user_message, mood, reply)
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"❌ Error: {str(e)}"}), 500



app = Flask(__name__)
