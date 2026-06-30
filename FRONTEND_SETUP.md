# Frontend Setup Complete! 🚀

Your VoiceEmotionRAG project now has a modern web interface. Here's what was created:

## 📁 What's New

```
VoiceEmotionRAG/
├── frontend/                          ← NEW: React + TypeScript web UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx      ← Main chat UI component
│   │   │   ├── MicInput.tsx           ← Microphone recording component
│   │   │   └── EmotionDisplay.tsx     ← Emotion visualization
│   │   ├── services/
│   │   │   └── api.ts                 ← API client for backend
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css                  ← Tailwind CSS
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── README.md
│
├── api.py                             ← NEW: FastAPI wrapper for frontend
├── setup-frontend.ps1                 ← NEW: Windows setup script
└── [existing files]
```

## 🎯 Features

✨ **Live Microphone Input** — Record and transcribe audio
✨ **Text Input** — Type directly in the chat
✨ **Emotion Visualization** — See detailed emotion breakdowns
✨ **Performance Metrics** — View latency, tokens, grounding, hallucination scores
✨ **Modern UI** — Beautiful chat interface with Tailwind CSS
✨ **Responsive Design** — Works on desktop and mobile

## ⚡ Quick Start

### Option 1: Automated Setup (Windows PowerShell)
```powershell
.\setup-frontend.ps1
```

### Option 2: Manual Setup

**Step 1: Install Node dependencies**
```bash
cd frontend
npm install
cd ..
```

**Step 2: Install Python API dependencies**
```bash
pip install fastapi uvicorn python-multipart
```

**Step 3: Create frontend environment file**
```bash
cd frontend
copy .env.example .env.local
# Edit .env.local if your backend is on a different port
cd ..
```

**Step 4: Start Ollama** (if not already running)
```bash
ollama serve
```

**Step 5: Start the API backend**
```bash
python api.py
```
✅ Backend API running on http://localhost:8000

**Step 6: Start the frontend dev server** (in a new terminal)
```bash
cd frontend
npm run dev
```
✅ Frontend running on http://localhost:5173

**Step 7: Open in browser**
Navigate to: **http://localhost:5173**

## 🎤 How to Use

### Recording Audio
1. Click the **large microphone button** in the center
2. Speak clearly into your microphone
3. Click the **red stop button** when done (or wait ~5 seconds)
4. The audio will be transcribed and sent to the AI

### Typing Text
1. Type your message in the **text input field** at the bottom
2. Press **Enter** or click the **Send button** (➤)
3. Watch the AI respond with emotion analysis and advice

### Viewing Emotions
- Click on the emotion display card to see detailed breakdown
- View confidence scores for all 7 emotions
- Sidebar shows expanded emotion breakdown

### Understanding Metrics
- **Response time** — How fast the LLM responded (ms)
- **Tokens** — Number of words in the response
- **Grounding** — % of response grounded in knowledge base docs
- **Hallucination** — % of response that might be hallucinated

## 📱 Frontend Architecture

```
React Components:
├── App.tsx (main entry, gradient background)
└── ChatInterface.tsx (main component)
    ├── MicInput.tsx (microphone button)
    ├── EmotionDisplay.tsx (emotion bars)
    └── Chat message rendering

Services:
└── api.ts (axios client for /process, /transcribe endpoints)

Styling:
└── Tailwind CSS (utility-first)
└── Custom animations (pulse effect on mic recording)
```

## 🔌 API Endpoints

All endpoints are served by `api.py` running on port 8000:

### POST /process
```json
// Request
{ "text": "I feel anxious and overwhelmed" }

// Response
{
  "response": "AI response text...",
  "emotion": {
    "fear": 0.97,
    "surprise": 0.02,
    ...
    "top_emotion": "fear",
    "top_score": 0.97
  },
  "metrics": {
    "latency_ms": 1234,
    "tokens_out": 45,
    "total_latency_ms": 5678,
    "grounding": 0.85,
    "hallucination": 0.15
  }
}
```

### POST /transcribe
- Upload audio file
- Returns: `{ "transcript": "transcribed text" }`

### GET /health
- Health check endpoint
- Returns: `{ "status": "healthy" }`

## 🐛 Troubleshooting

**Q: "Connection refused" error**
- Ensure `api.py` is running: `python api.py`
- Check VITE_API_URL in frontend/.env.local

**Q: Microphone button not working**
- Allow microphone access when browser asks
- Check System Settings → Privacy → Microphone

**Q: "Module not found" errors in api.py**
- Ensure you're in the venv: `. venv\Scripts\Activate.ps1`
- Install requirements: `pip install -r requirements.txt`

**Q: Slow first response**
- Models download on first run (~300MB total)
- This is normal, subsequent requests are faster

**Q: Port already in use**
- Frontend: Edit `vite.config.ts` to change port
- Backend: Edit `api.py` to change port, update frontend .env.local

## 📚 Next Steps

- [ ] Build for production: `cd frontend && npm run build`
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Add dark mode toggle
- [ ] Integrate chat history persistence
- [ ] Add text-to-speech for AI responses
- [ ] Visualize Jaeger traces in the UI

## 📖 More Info

- Frontend README: [frontend/README.md](frontend/README.md)
- Main Project README: [README.md](README.md)
- API Source: [api.py](api.py)

---

**Happy building! 🎉**

If you run into issues, check the console output in both the API terminal and browser dev tools (F12).
