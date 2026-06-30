# VoiceEmotionRAG

> Voice & text AI assistant: detects emotion → retrieves knowledge → generates response.
> **Now with web UI + Grok AI support!**
> Fully open source. Optional paid APIs (Grok) or fully local (Ollama). OpenTelemetry observability with Jaeger UI.

---

## Architecture

```
Voice Input
    ↓
faster-whisper       (Speech to text, CPU)
    ↓
distilroberta        (Emotion detection, HuggingFace)
    ↓
ChromaDB + sentence-transformers  (RAG retrieval)
    ↓
Ollama + Mistral/Llama3           (Local LLM)
    ↓
Rich terminal output

Parallel: OpenTelemetry → Console  OR  Jaeger UI
```

---

## Quick Start

### Setup

1. **Create & activate virtual environment:**
```bash
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate  # macOS/Linux
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure LLM provider:**
```bash
cp .env.example .env
# Edit .env and choose: Grok AI (cloud) or Ollama (local)
```

---

### Option A: Web Frontend (Modern UI) ⭐ **Recommended**

**Terminal 1 - Start API:**
```bash
python api.py
```
✅ API running on `http://localhost:8000`

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm install  # first time only
npm run dev
```
✅ Frontend running on `http://localhost:5173`

**Open in browser:** `http://localhost:5173`

---

### Option B: CLI (Terminal) 

**Voice mode:**
```bash
python main.py
```

**Text mode:**
```bash
python main.py --text "I feel anxious"
```

**Other options:**
```bash
python main.py --duration 10          # Longer recording
python main.py --model llama3         # Different Ollama model
python main.py --build-index          # Rebuild vector DB
```

---

## LLM Provider: Grok AI vs Ollama

### 🧠 Grok AI (Cloud - Recommended)

**What:** xAI's advanced reasoning model via REST API
**Cost:** Pay-per-use ($0.02-0.10 per request)
**Setup:** Get API key from https://console.x.ai

```bash
# .env
LLM_PROVIDER=grok
GROK_API_KEY=xai_your_key_here
GROK_MODEL=grok-2
```

**Pros:** Fast, no local GPU, no model downloads
**Cons:** Requires API key, internet required

---

### 🏠 Ollama (Local)

**What:** Run Mistral/Llama models locally on your machine
**Cost:** Free
**Setup:** Download from https://ollama.ai

```bash
# Terminal 1
ollama pull mistral
ollama serve

# .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_HOST=http://localhost:11434
```

**Pros:** Fully offline, privacy-first, free
**Cons:** Slow on CPU (needs GPU), downloads 5-40GB models

---

## Observability

### Option A — Console (default, zero setup)

Spans print as JSON to terminal automatically. No configuration needed.

### Option B — Jaeger UI (visual trace explorer)

**Step 1:** Start Jaeger with Docker:

```bash
docker-compose up -d
```

**Step 2:** Set the exporter environment variable:

```bash
# Linux / macOS
export OTEL_EXPORTER=jaeger
python main.py --text "I feel stressed"

# Windows (PowerShell)
$env:OTEL_EXPORTER = "jaeger"
python main.py --text "I feel stressed"
```

**Step 3:** Open Jaeger UI in your browser:

```
http://localhost:16686
```

Select service `voice-emotion-rag` → Find Traces → click any trace to see the full span waterfall with latencies for every step.

**Stop Jaeger:**

```bash
docker-compose down
```

---

## Knowledge Base

The `data/` folder contains 7 topic files the RAG system searches:

| File | Topic |
|------|-------|
| `breathing_techniques.txt`  | CBT breathing, 4-7-8, box breathing |
| `sleep_guide.txt`           | Sleep hygiene, circadian rhythm |
| `mental_health_guide.txt`   | Stress, anxiety, overwhelm |
| `anger_management.txt`      | Anger, frustration, triggers |
| `focus_productivity.txt`    | Focus, procrastination, motivation |
| `social_connection.txt`     | Loneliness, relationships, social anxiety |
| `grief_and_loss.txt`        | Grief, loss, life transitions |
| `joy_and_gratitude.txt`     | Gratitude, savouring, positive wellbeing |
| `confidence_selfesteem.txt` | Confidence, self-talk, self-esteem |

### Adding your own knowledge

Drop any `.txt` file into `data/` then rebuild:

```bash
python main.py --build-index
```

---

## Project Structure

```
VoiceEmotionRAG/
├── frontend/                      # React + TypeScript web UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx  # Main chat component
│   │   │   ├── MicInput.tsx       # Microphone recorder
│   │   │   └── EmotionDisplay.tsx # Emotion visualization
│   │   ├── services/
│   │   │   └── api.ts             # API client
│   │   └── main.tsx
│   └── package.json
│
├── backend/
│   ├── speech.py                  # Audio transcription (faster-whisper)
│   ├── emotion.py                 # Emotion detection (HuggingFace)
│   ├── rag.py                     # Document retrieval (ChromaDB)
│   └── llm.py                     # LLM generation (Grok/Ollama)
│
├── services/                      # Service layer
│   └── emotion_service.py         # Pipeline orchestration
│
├── observability/
│   ├── tracing.py                 # OpenTelemetry setup
│   └── metrics.py                 # Prometheus metrics
│
├── dashboard/
│   └── charts.py                  # Rich terminal UI
│
├── data/                          # Knowledge base (7 .txt files)
├── vectorDB/                      # ChromaDB embeddings (auto-created)
│
├── main.py                        # CLI entry point
├── api.py                         # FastAPI REST API
├── config.py                      # Configuration management
├── requirements.txt
└── .env.example
```

For detailed architecture see [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Environment Variables

| Variable         | Default     | Options              |
|-----------------|-------------|----------------------|
| `OTEL_EXPORTER` | `console`   | `console`, `jaeger`  |
| `JAEGER_HOST`   | `localhost` | any hostname/IP      |
| `JAEGER_PORT`   | `4317`      | OTLP gRPC port       |

---

## Full Open Source Stack

| Component       | Library                              | License      |
|----------------|--------------------------------------|--------------|
| Audio capture  | sounddevice + scipy                  | MIT / BSD    |
| Speech to text | faster-whisper                       | MIT          |
| Emotion model  | distilroberta-base (HuggingFace)     | Apache 2.0   |
| Embeddings     | sentence-transformers all-MiniLM-L6  | Apache 2.0   |
| Vector DB      | ChromaDB                             | Apache 2.0   |
| RAG framework  | LangChain                            | MIT          |
| LLM inference  | Ollama + Mistral / Llama3            | MIT / Apache |
| Observability  | OpenTelemetry SDK                    | Apache 2.0   |
| Trace UI       | Jaeger (Docker)                      | Apache 2.0   |
| Terminal UI    | Rich                                 | MIT          |
