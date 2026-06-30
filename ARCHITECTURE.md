# VoiceEmotionRAG - System Architecture

## 🏗️ Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 5173)                   │
│                   (Microphone + Chat UI)                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓ REST API
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Port 8000)                    │
│                    Service Layer (api.py)                        │
└─────────────────────────────────────────────────────────────────┘
         ↓                ↓                ↓                ↓
    ┌────────┐     ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Speech │     │ Emotion  │    │   RAG    │    │   LLM    │
    │ Module │     │ Detection│    │ Retrieval│    │ Provider │
    └────────┘     └──────────┘    └──────────┘    └──────────┘
        ↓               ↓                ↓                ↓
    faster-whisper  HuggingFace    ChromaDB Vector   Grok AI
                  distilroberta    + LangChain      or Ollama
```

---

## 📁 Project Structure

```
VoiceEmotionRAG/
├── frontend/                      # React + TypeScript web UI
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── ChatInterface.tsx  # Main chat UI
│   │   │   ├── MicInput.tsx       # Microphone recorder
│   │   │   └── EmotionDisplay.tsx # Emotion visualization
│   │   ├── services/
│   │   │   └── api.ts            # Frontend API client
│   │   └── main.tsx
│   └── package.json
│
├── backend/                       # Core ML/AI modules
│   ├── emotion.py                 # Emotion detection (HuggingFace)
│   ├── rag.py                     # Document retrieval (ChromaDB)
│   ├── llm.py                     # LLM generation (Grok/Ollama)
│   └── speech.py                  # Audio transcription (faster-whisper)
│
├── services/                      # Business logic layer (NEW)
│   ├── __init__.py
│   └── emotion_service.py         # Orchestrates backend modules
│
├── observability/                 # Monitoring & metrics
│   ├── metrics.py                 # Prometheus metrics
│   └── tracing.py                 # OpenTelemetry tracing
│
├── dashboard/                     # Terminal UI
│   └── charts.py                  # Rich terminal panels
│
├── data/                          # Knowledge base
│   ├── mental_health_guide.txt
│   ├── breathing_techniques.txt
│   └── [7 other .txt files]
│
├── vectorDB/                      # ChromaDB embeddings (auto-created)
│
├── main.py                        # CLI entry point
├── api.py                         # FastAPI REST API (NEW)
├── config.py                      # Configuration management (NEW)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md
```

---

## 🔄 Data Flow

### Processing a User Input

```
1. Frontend (React)
   └─> User types or speaks text
   
2. HTTP Request to API
   POST /process or POST /transcribe
   
3. Service Layer (emotion_service.py)
   │
   ├─> backend.emotion.detect_emotions()
   │   └─> HuggingFace distilroberta model
   │       └─> Returns: [{"label": "fear", "score": 0.97}, ...]
   │
   ├─> backend.rag.retrieve()
   │   └─> ChromaDB similarity search
   │       └─> Returns: [{"content": "...", "score": 0.37}, ...]
   │
   ├─> backend.llm.generate()
   │   ├─> Option A: Grok AI (xAI API)
   │   │   └─> httpx.post("https://api.x.ai/v1/chat/completions")
   │   │
   │   └─> Option B: Ollama (local)
   │       └─> HuggingFace transformers pipeline
   │
   └─> observability.metrics.compute_grounding_score()
       └─> Returns: (grounding, hallucination) metrics
   
4. ProcessingResult
   ├─> response: str (AI's response)
   ├─> emotion: Dict (emotion scores)
   └─> metrics: Dict (latency, tokens, grounding, etc.)
   
5. HTTP Response
   └─> JSON with all the above
   
6. Frontend renders
   └─> Chat message + emotion bars + metrics
```

---

## 🤖 LLM Configuration

### Option 1: Grok AI (Cloud - Recommended)

**Setup:**
```bash
# 1. Get API key from https://console.x.ai
# 2. Create .env file:
cp .env.example .env

# 3. Edit .env:
LLM_PROVIDER=grok
GROK_API_KEY=xai_xxxxxxxxxxxx
GROK_MODEL=grok-2

# 4. Start API
python api.py
```

**Pros:**
- ✅ No local GPU needed
- ✅ Fast inference
- ✅ No model downloads
- ✅ Pay-per-use pricing

**Cons:**
- ❌ Requires API key
- ❌ Internet dependent

---

### Option 2: Ollama (Local)

**Setup:**
```bash
# 1. Install Ollama: https://ollama.ai
ollama pull mistral
ollama serve

# 2. Create .env file:
cp .env.example .env

# 3. Edit .env:
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_HOST=http://localhost:11434

# 4. Start API (in another terminal)
python api.py
```

**Pros:**
- ✅ Fully local/offline
- ✅ No API keys needed
- ✅ Privacy-first

**Cons:**
- ❌ Requires GPU or slow on CPU
- ❌ First run downloads 5-40GB models

---

## 🚀 Quick Start

### Complete Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure LLM provider
cp .env.example .env
# Edit .env with your API key (Grok) or Ollama host

# 4. Terminal 1: Start API
python api.py

# 5. Terminal 2: Start Frontend
cd frontend
npm install  # first time only
npm run dev

# 6. Open http://localhost:5173 in browser
```

---

## 📊 API Endpoints

### POST /process
Process text through the pipeline

**Request:**
```json
{
  "text": "I feel anxious and overwhelmed"
}
```

**Response:**
```json
{
  "response": "You're experiencing fear and anxiety...",
  "emotion": {
    "fear": 0.97,
    "surprise": 0.02,
    "anger": 0.0,
    "joy": 0.0,
    "sadness": 0.0,
    "neutral": 0.0,
    "disgust": 0.0,
    "top_emotion": "fear",
    "top_score": 0.97
  },
  "metrics": {
    "latency_ms": 1234,
    "tokens_out": 45,
    "total_latency_ms": 5678,
    "rag_latency_ms": 234,
    "grounding": 0.85,
    "hallucination": 0.15,
    "llm_provider": "grok"
  }
}
```

### POST /transcribe
Convert audio to text

**Request:** Form data with audio file
**Response:** `{ "transcript": "transcribed text" }`

### GET /health
Health check

**Response:**
```json
{
  "status": "healthy",
  "llm_provider": "grok"
}
```

### GET /config
Get current configuration

**Response:**
```json
{
  "llm_provider": "grok",
  "llm_model": "grok-2",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "whisper_model": "base"
}
```

---

## 🏗️ Service Layer Design

The `services/emotion_service.py` module provides clean abstraction:

```python
from services import VoiceEmotionService

# Single method handles entire pipeline
result = VoiceEmotionService.process_text("I feel sad")

# Returns ProcessingResult with:
# - result.response: str
# - result.emotion: Dict
# - result.metrics: Dict
```

**Benefits:**
- ✅ Decouples frontend from backend
- ✅ Easy to test
- ✅ Single source of truth for business logic
- ✅ Easy to add new features (logging, caching, etc.)

---

## ⚙️ Configuration Management

Use `config.py` for all environment-dependent settings:

```python
from config import LLM_PROVIDER, GROK_API_KEY, API_PORT
```

All settings come from `.env` file or environment variables with sensible defaults.

---

## 🔍 Debugging

### Check LLM Provider
```bash
curl http://localhost:8000/config
```

### Check Health
```bash
curl http://localhost:8000/health
```

### View Logs
- **API logs** → Terminal where you ran `python api.py`
- **Frontend logs** → Browser console (F12)
- **Backend logs** → Also in API terminal

### Common Issues

| Issue | Solution |
|-------|----------|
| "GROK_API_KEY not set" | Create `.env` with your API key |
| "Connection refused" | Ensure `python api.py` is running |
| "Grok API error 401" | Check GROK_API_KEY is valid |
| "Ollama not responding" | Start Ollama: `ollama serve` |
| Slow first response | Models downloading (normal, one-time) |

---

## 📦 Dependencies

### Frontend
- React 18, TypeScript, Vite
- Tailwind CSS, Axios, Lucide icons

### Backend
- FastAPI, Uvicorn
- Transformers, PyTorch, Sentence-Transformers
- faster-whisper, LangChain, ChromaDB
- OpenTelemetry, Prometheus

### LLM
- Grok API via `httpx`
- OR Ollama (local transformers)

---

## 🎯 Next Steps

- [ ] Add conversation history/persistence
- [ ] Implement caching layer
- [ ] Add user authentication
- [ ] Deploy API to cloud (AWS/GCP)
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Add voice output (TTS)
- [ ] Integrate with Jaeger traces in UI
- [ ] Add Dark mode to frontend

---

## 📝 License

Open Source - Same as VoiceEmotionRAG project
