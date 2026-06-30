"""
Configuration management for VoiceEmotionRAG
Loads settings from environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()

# === API Configuration ===
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# === LLM Configuration ===
# Options: "groq", "grok" or "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# Groq API settings (https://console.groq.com)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1"

# Grok AI settings (xAI API)
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-2")
GROK_ENDPOINT = "https://api.x.ai/v1"

# Ollama settings (local fallback)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# === Speech Configuration ===
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 16000))

# === RAG Configuration ===
CHROMA_DIR = os.getenv("CHROMA_DIR", "vectorDB")
DATA_DIR = os.getenv("DATA_DIR", "data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# === Observability Configuration ===
OTEL_EXPORTER = os.getenv("OTEL_EXPORTER", "console")  # "console" or "jaeger"
JAEGER_HOST = os.getenv("JAEGER_HOST", "localhost")
JAEGER_PORT = int(os.getenv("JAEGER_PORT", 4317))
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 9464))

# === Validation ===
if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
    print("[WARNING] GROQ_API_KEY not set. Please set it in .env file")
    print("[INFO] Fallback to Ollama (local). Install with: ollama pull mistral")
elif LLM_PROVIDER == "grok" and not GROK_API_KEY:
    print("[WARNING] GROK_API_KEY not set. Please set it in .env file")
    print("[INFO] Fallback to Ollama (local). Install with: ollama pull mistral")

