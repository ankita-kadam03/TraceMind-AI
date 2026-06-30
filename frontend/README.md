# VoiceEmotionRAG Frontend

A modern React + TypeScript web interface for the VoiceEmotionRAG project. Features real-time voice input, emotion detection visualization, and an interactive chat-like UI.

## Tech Stack

- **React 18** — UI framework
- **TypeScript** — Type safety
- **Vite** — Lightning-fast build tool
- **Tailwind CSS** — Utility-first styling
- **Axios** — HTTP client
- **Web Audio API** — Microphone recording

## Features

✨ **Voice Input** — Record and transcribe audio with the microphone
✨ **Text Input** — Type messages directly
✨ **Emotion Detection** — Real-time emotion analysis with visual feedback
✨ **Metrics Display** — View response latency, tokens, grounding, and hallucination scores
✨ **Interactive Chat UI** — Clean, modern chatbot-like interface
✨ **Expandable Emotion Sidebar** — Click emotions to see detailed breakdown

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env.local` file (or copy from `.env.example`):

```bash
cp .env.example .env.local
```

Edit `.env.local` if your backend is on a different host/port:

```
VITE_API_URL=http://localhost:8000
```

### 3. Start the Backend API

In the project root, start the FastAPI server:

```bash
# Make sure your venv is activated
pip install fastapi uvicorn python-multipart

python api.py
```

The API runs on `http://localhost:8000`

### 4. Start the Frontend Dev Server

```bash
npm run dev
```

The frontend runs on `http://localhost:5173`

Open your browser and navigate to `http://localhost:5173`

## Usage

### Mic Recording
- Click the **microphone button** to start recording (5-second default)
- Click **stop button** while recording to finish
- Audio is sent to backend for transcription and processing

### Text Input
- Type your message in the **text input field**
- Press **Enter** or click the **Send button**

### View Emotion Details
- Click any emotion display to expand it in the right sidebar
- See all emotion scores with confidence percentages

### Metrics
- After each response, view performance metrics:
  - **Response time** — LLM generation latency
  - **Tokens** — Output token count
  - **Grounding** — How much is grounded in retrieved docs
  - **Hallucination** — Estimated hallucination percentage

## Build for Production

```bash
npm run build
```

Outputs optimized files to `dist/` directory.

Preview production build:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx   ← Main chat UI
│   │   ├── MicInput.tsx        ← Microphone recorder
│   │   └── EmotionDisplay.tsx  ← Emotion visualization
│   ├── services/
│   │   └── api.ts             ← Backend API client
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## API Endpoints

### POST /process
Process text and get response with emotion and metrics

**Request:**
```json
{ "text": "I feel anxious and overwhelmed" }
```

**Response:**
```json
{
  "response": "AI response text...",
  "emotion": {
    "fear": 0.97,
    "surprise": 0.02,
    "anger": 0.0,
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
Transcribe audio file to text

**Request:** Form data with audio file
**Response:** `{ "transcript": "transcribed text" }`

### GET /health
Health check endpoint

## Troubleshooting

### Microphone not working
- Ensure browser has microphone permissions
- Check that microphone is enabled in system settings
- Try in a different browser

### Backend connection error
- Ensure `api.py` is running on the configured port
- Check `VITE_API_URL` in `.env.local` matches backend address
- Verify CORS is enabled (it is by default in `api.py`)

### Slow response times
- First model load downloads weights (~300MB) — this is normal
- Subsequent requests are faster
- Monitor metrics in the UI to see where time is spent

## Next Steps

- Add conversation history persistence
- Implement user preferences/settings
- Add export/download chat transcripts
- Integrate with Jaeger traces in the UI
- Add voice output (text-to-speech)
- Dark mode toggle

## License

Same as parent VoiceEmotionRAG project (Open Source)
