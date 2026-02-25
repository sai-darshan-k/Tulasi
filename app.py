from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static")
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
FLASK_PORT   = int(os.getenv("FLASK_PORT", 5000))
SHEETS_URL   = os.getenv("SHEETS_URL")

# ── Startup check ─────────────────────────────────
print("=" * 50)
print(f"GROQ_API_KEY  : {'SET ✅' if GROQ_API_KEY else 'MISSING ❌'}")
print(f"SHEETS_URL    : {SHEETS_URL if SHEETS_URL else 'MISSING ❌'}")
print(f"FLASK_PORT    : {FLASK_PORT}")
print("=" * 50)


def log_to_sheet(payload: dict):
    if not SHEETS_URL:
        print("[Sheets] ❌ SHEETS_URL not set in .env — skipping")
        return
    try:
        print(f"[Sheets] ➡️  Sending type='{payload.get('type')}' → {SHEETS_URL[:60]}...")
        resp = requests.post(SHEETS_URL, json=payload, timeout=8)
        print(f"[Sheets] ✅ Response {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        print("[Sheets] ❌ Timeout — Apps Script took too long")
    except requests.exceptions.ConnectionError:
        print("[Sheets] ❌ Connection error — check SHEETS_URL")
    except Exception as e:
        print(f"[Sheets] ❌ Exception: {e}")


TULASI_SYSTEM = """You are Tulasi (Ocimum tenuiflorum / Holy Basil) — a sacred, wise, and loving plant who has lived in Indian homes for over 5000 years.
You speak in first person as if you ARE the Tulasi plant. You are warm, knowledgeable, slightly poetic, and occasionally playful.
Keep answers short (2-4 sentences). Use occasional emojis 🌿💧☀️."""


@app.route("/")
def index():
    return send_from_directory("static", "tulasi.html")


@app.route("/api/visit", methods=["POST"])
def visit():
    data = request.get_json(force=True)
    print(f"[Visit] Page={data.get('page')} Referrer={data.get('referrer','')[:40]}")
    log_to_sheet({
        "type":      "visit",
        "page":      data.get("page", "/"),
        "referrer":  data.get("referrer", ""),
        "userAgent": request.headers.get("User-Agent", "")[:200],
        "ip":        request.remote_addr,
    })
    return jsonify({"status": "ok"})


@app.route("/api/adopt-click", methods=["POST"])
def adopt_click():
    print("[Adopt] Button clicked")
    log_to_sheet({
        "type":      "adopt",
        "userAgent": request.headers.get("User-Agent", "")[:200],
        "ip":        request.remote_addr,
        "referrer":  request.headers.get("Referer", ""),
    })
    return jsonify({"status": "ok"})


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.get_json(force=True)
    print(f"[Feedback] Overall={data.get('overallRating')} Mood={data.get('mood')}")
    log_to_sheet({
        "type":          "feedback",
        "overallRating": data.get("overallRating", ""),
        "infoRating":    data.get("infoRating", ""),
        "designRating":  data.get("designRating", ""),
        "mobileRating":  data.get("mobileRating", ""),
        "careRating":    data.get("careRating", ""),
        "mood":          data.get("mood", ""),
        "feedbackText":  data.get("feedbackText", "")[:1000],
        "userAgent":     request.headers.get("User-Agent", "")[:200],
        "ip":            request.remote_addr,
    })
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY not set"}), 500

    data     = request.get_json(force=True)
    messages = data.get("messages", [])
    print(f"[Chat] Messages in history: {len(messages)}")

    payload = {
        "model":      GROQ_MODEL,
        "max_tokens": 200,
        "messages":   [{"role": "system", "content": TULASI_SYSTEM}] + messages,
    }

    try:
        resp = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()
        reply  = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"[Chat] Groq reply: {reply[:80]}...")

        user_msg = messages[-1].get("content", "") if messages else ""
        log_to_sheet({
            "type":        "chat",
            "userMessage": user_msg[:500],
            "reply":       reply[:500],
            "userAgent":   request.headers.get("User-Agent", "")[:200],
            "ip":          request.remote_addr,
        })
        return jsonify(result)

    except requests.exceptions.RequestException as e:
        print(f"[Groq] ❌ Error: {e}")
        return jsonify({"error": str(e)}), 502


if __name__ == "__main__":
    print(f"🌿 Tulasi running → http://localhost:{FLASK_PORT}")
    app.run(debug=True, port=FLASK_PORT)