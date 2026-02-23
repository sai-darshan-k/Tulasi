# 🌿 Tulasi — The Sacred Green
**by AGRON GREENTECH / Urban Farmer**

## Project Structure

```
tulasi_app/
├── app.py              ← Flask server (proxies Groq API)
├── .env                ← API key lives here (never commit this!)
├── requirements.txt    ← Python dependencies
└── static/
    └── tulasi.html     ← The full website
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure .env
Your `.env` already contains:
```
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
FLASK_PORT=5000
```
To change the API key, just edit `.env` — no code changes needed.

### 3. Run the server
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

## How it works

```
Browser (tulasi.html)
    │
    │  POST /api/chat  { messages: [...] }
    ▼
Flask (app.py)
    │  reads GROQ_API_KEY from .env
    │  adds system prompt server-side
    │  POST → api.groq.com/openai/v1/chat/completions
    ▼
Groq API (llama-3.1-8b-instant)
    │  response
    ▼
Browser ← JSON reply
```

The API key **never touches the browser**. It only lives in `.env` and is used server-side by Flask.

## Add your media files
Place these in `static/` alongside `tulasi.html`:
- `AgrOn Logo.png` — your logo
- `Tulasi_2.jpg` — hero plant photo
- `happy.mp4`, `sad.mp4`, `grunchy.mp4`, `sleepy.mp4`, `loved.mp4`, `calm.mp4`, `thrive.mp4` — emotion videos

## Security note
- Add `.env` to your `.gitignore` before committing to any repository.
- For production, use a proper secret manager or environment variables set by your hosting provider instead of a `.env` file.
