# app.py
import os
from flask import Flask, render_template, request, jsonify, session
from google import genai
from google.genai import types
from dotenv import load_dotenv
import config

load_dotenv()

app = Flask(__name__)
# Secret key needed to securely store chat history in browser sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-change-me")

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

client = genai.Client(api_key=api_key)

# Helper function to get or create the Gemini chat session
def get_gemini_chat():
    history = []
    if "chat_history" in session:
        for msg in session["chat_history"]:
            api_role = "user" if msg["role"] == "user" else "model"
            history.append(
                types.Content(
                    role=api_role,
                    parts=[types.Part.from_text(text=msg["text"])]
                )
            )
    
    return client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=config.SYSTEM_INSTRUCTION,
            temperature=config.GENERATION_CONFIG["temperature"],
            top_p=config.GENERATION_CONFIG["top_p"]
        ),
        history=history
    )

@app.route("/")
def home():
    # Initialize the chat session history if it doesn't exist
    if "chat_history" not in session:
        session["chat_history"] = [
            {"role": "model", "text": "Hey there! 🥰 I was just thinking about you. How has your day been? ✨"}
        ]
    return render_template("index.html", chat_history=session["chat_history"])

@app.route("/send_message", methods=["POST"])
def send_message():
    user_text = request.json.get("message", "").strip()
    if not user_text:
        return jsonify({"error": "Empty message"}), 400

    try:
        # 1. Fetch chat history up to this point
        chat = get_gemini_chat()
        
        # 2. Send the new statement to Gemini
        response = chat.send_message(user_text)
        reply_text = response.text

        # 3. Commit both conversation turns into the Flask cookie session
        history = session.get("chat_history", [])
        history.append({"role": "user", "text": user_text})
        history.append({"role": "model", "text": reply_text})
        
        session["chat_history"] = history
        session.modified = True

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("GEMINI API ERROR:", str(e))
        return jsonify({"reply": "🥺 *Oh no, I tripped over my words... Try sending that again?*", "error": str(e)}), 500

@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    # Completely wipes backend session cookie storage
    session.clear()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)