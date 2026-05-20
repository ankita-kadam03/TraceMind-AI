# VoiceEmotionRAG

> Terminal-based AI assistant: speaks → detects emotion → retrieves knowledge → responds.
> Fully open source. No paid APIs. OpenTelemetry observability with Jaeger UI support.

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

### 1. Install Ollama

Download from https://ollama.ai then:

```bash
ollama pull mistral
ollama serve
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Build vector database

```bash
python main.py --build-index
```

### 4. Run

```bash
# Text mode (no mic — good for testing)
python main.py --text "I feel anxious and overwhelmed"

# Voice mode (5 second recording)
python main.py

# Longer recording
python main.py --duration 10

# Different Ollama model
python main.py --model llama3
```

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
├── main.py                       ← entry point
├── requirements.txt
├── docker-compose.yml            ← Jaeger one-command setup
├── backend/
│   ├── speech.py                 ← mic + faster-whisper STT
│   ├── emotion.py                ← HuggingFace emotion detection
│   ├── rag.py                    ← LangChain + ChromaDB retrieval
│   └── llm.py                    ← Ollama local LLM
├── observability/
│   ├── tracing.py                ← OTel setup (console + Jaeger)
│   └── metrics.py                ← grounding + hallucination score
├── dashboard/
│   └── charts.py                 ← Rich terminal UI panels
├── data/                         ← knowledge base (.txt files)
└── vectorDB/                     ← ChromaDB index (auto-created)
```

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
