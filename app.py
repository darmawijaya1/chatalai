from flask import Flask, send_from_directory, request, jsonify, render_template
from openai import AzureOpenAI
from datetime import datetime
import os
import re
import csv

# === Config ===
SECRET_KEY = "supersecretkey"

AZURE_API_KEY = "01j1Vu4DAb1ArRNEzcr3Y1TvaByU82JZ6M0yLtsOvFamKKxLiIiOaJQQJ99BHACYeBjFXJ3w3AAAAACOGko6r"
AZURE_ENDPOINT = "https://eyesxa.services.ai.azure.com/"
AZURE_DEPLOYMENT = "gpt-4.1curhat"

# === Azure OpenAI Client ===
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version="2023-05-15",
    azure_endpoint=AZURE_ENDPOINT
)

# === Flask Setup ===
app = Flask(__name__, static_folder='assets')
app.secret_key = SECRET_KEY

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

# === Risiko ===
def check_risk_keywords(text):
    risk_keywords = [
        "suicide", "self-harm", "want to disappear", "end it all", "too tired", "end my life"
    ]
    return any(keyword in text.lower() for keyword in risk_keywords)

def log_chat(user_message, mood, reply):
    if os.getenv("VERCEL") == "1":
        return  # skip writing log on vercel
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

# === Run Flask App ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
