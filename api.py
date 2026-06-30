"""
FastAPI REST API for VoiceEmotionRAG
Provides endpoints for the React frontend
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services import VoiceEmotionService
import config

# ============ API Models ============

class ProcessRequest(BaseModel):
    text: str


class EmotionResponse(BaseModel):
    fear: float
    surprise: float
    anger: float
    joy: float
    sadness: float
    neutral: float
    disgust: float
    top_emotion: str
    top_score: float


class MetricsResponse(BaseModel):
    latency_ms: float
    tokens_out: int
    total_latency_ms: float
    rag_latency_ms: float
    grounding: float
    hallucination: float
    llm_provider: str


class ProcessResponse(BaseModel):
    response: str
    emotion: EmotionResponse
    metrics: MetricsResponse


class HealthResponse(BaseModel):
    status: str
    llm_provider: str


# ============ FastAPI Setup ============

app = FastAPI(
    title="VoiceEmotionRAG API",
    version="2.0.0",
    description="REST API for Voice Emotion Detection & RAG with Grok/Ollama LLM"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm_provider": config.LLM_PROVIDER
    }


@app.post("/process", response_model=ProcessResponse)
async def process_input(request: ProcessRequest):
    """
    Process text input through emotion detection → RAG → LLM pipeline
    
    Returns:
    - AI response text
    - Emotion scores with top emotion
    - Performance metrics
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = VoiceEmotionService.process_text(request.text)
        
        return ProcessResponse(
            response=result.response,
            emotion=EmotionResponse(**result.emotion),
            metrics=MetricsResponse(**result.metrics)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Process failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio file to text using faster-whisper
    
    Returns:
    - transcript: The recognized text
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            contents = await audio.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            transcript = VoiceEmotionService.transcribe_audio(tmp_path)
            return {"transcript": transcript}
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@app.get("/config")
async def get_config():
    """Get current configuration (for debugging)"""
    return {
        "llm_provider": config.LLM_PROVIDER,
        "llm_model": config.GROK_MODEL if config.LLM_PROVIDER == "grok" else config.OLLAMA_MODEL,
        "embedding_model": config.EMBEDDING_MODEL,
        "whisper_model": config.WHISPER_MODEL,
    }


if __name__ == "__main__":
    import uvicorn
    
    print(f"\n{'='*60}")
    print(f"🚀 VoiceEmotionRAG API")
    print(f"{'='*60}")
    print(f"🤖 LLM Provider: {config.LLM_PROVIDER.upper()}")
    if config.LLM_PROVIDER == "groq":
        print(f"   Model: {config.GROQ_MODEL}")
        print(f"   API Key: {'✓ Set' if config.GROQ_API_KEY else '✗ Not set'}")
    elif config.LLM_PROVIDER == "grok":
        print(f"   Model: {config.GROK_MODEL}")
        print(f"   API Key: {'✓ Set' if config.GROK_API_KEY else '✗ Not set'}")
    else:
        print(f"   Model: {config.OLLAMA_MODEL}")
        print(f"   Host: {config.OLLAMA_HOST}")
    print(f"📝 Embedding: {config.EMBEDDING_MODEL}")
    print(f"🎤 Whisper: {config.WHISPER_MODEL}")
    print(f"🌐 API: http://{config.API_HOST}:{config.API_PORT}")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT
    )

