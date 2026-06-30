import time
from typing import List, Dict
from opentelemetry import trace
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

tracer = trace.get_tracer("llm")

_generator = None


def _get_groq_response(prompt: str) -> Dict:
    """Generate response using Groq API (OpenAI-compatible)"""
    from groq import Groq
    
    if not config.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured. Set it in .env file.")
    
    client = Groq(api_key=config.GROQ_API_KEY)
    
    t0 = time.time()
    
    message = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a supportive, empathetic mental health assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7,
    )
    
    latency_ms = int((time.time() - t0) * 1000)
    text = message.choices[0].message.content
    tokens = message.usage.completion_tokens if message.usage else len(text.split())
    
    return {
        "text": text,
        "tokens": tokens,
        "latency_ms": latency_ms,
        "provider": "groq"
    }


def _get_grok_response(prompt: str) -> Dict:
    """Generate response using Grok AI via xAI API"""
    import requests
    
    if not config.GROK_API_KEY:
        raise ValueError("GROK_API_KEY not configured. Set it in .env file.")
    
    headers = {
        "Authorization": f"Bearer {config.GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": config.GROK_MODEL,
        "messages": [
            {"role": "system", "content": "You are a supportive, empathetic mental health assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
    }
    
    t0 = time.time()
    response = requests.post(
        f"{config.GROK_ENDPOINT}/chat/completions",
        json=payload,
        headers=headers,
        timeout=30
    )
    latency_ms = int((time.time() - t0) * 1000)
    
    if response.status_code != 200:
        raise Exception(f"Grok API error: {response.status_code} - {response.text}")
    
    data = response.json()
    text = data["choices"][0]["message"]["content"]
    tokens = data.get("usage", {}).get("completion_tokens", len(text.split()))
    
    return {
        "text": text,
        "tokens": tokens,
        "latency_ms": latency_ms,
        "provider": "grok"
    }


def _get_ollama_response(prompt: str) -> Dict:
    """Generate response using local Ollama"""
    from transformers import pipeline
    
    global _generator
    if _generator is None:
        print(f"[LLM] Loading Ollama model {config.OLLAMA_MODEL}...")
        _generator = pipeline(
            "text-generation",
            model=f"mistralai/Mistral-7B",
            device=-1,
        )
        print("[LLM] Model loaded.")
    
    t0 = time.time()
    gen = _generator
    
    output = gen(
        prompt,
        max_new_tokens=150,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    
    latency_ms = int((time.time() - t0) * 1000)
    text = output[0]["generated_text"][len(prompt):]
    
    return {
        "text": text,
        "tokens": len(text.split()),
        "latency_ms": latency_ms,
        "provider": "ollama"
    }


def build_prompt(user_text: str, emotion_context: str, retrieved_docs: List[Dict]) -> str:
    """Build prompt with context"""
    docs_text = "\n".join(f"- {d['content'][:200]}" for d in retrieved_docs)
    return f"""You are a supportive assistant. {emotion_context}. 
Relevant guidance: {docs_text}
User said: {user_text}
Your response:"""


def generate(
    user_text: str,
    emotion_context: str,
    retrieved_docs: List[Dict],
) -> Dict:
    """Generate response using configured LLM provider"""
    with tracer.start_as_current_span("llm_generate") as span:
        span.set_attribute("provider", config.LLM_PROVIDER)
        span.set_attribute("user_text", user_text)

        prompt = build_prompt(user_text, emotion_context, retrieved_docs)
        
        try:
            if config.LLM_PROVIDER == "groq":
                result = _get_groq_response(prompt)
            elif config.LLM_PROVIDER == "grok":
                result = _get_grok_response(prompt)
            else:
                result = _get_ollama_response(prompt)
            
            span.set_attribute("model", result["provider"])
            span.set_attribute("latency_ms", result.get("latency_ms", 0))
            span.set_attribute("tokens", result["tokens"])
            
            return result
        except Exception as e:
            print(f"[LLM] Error generating response: {e}")
            # Fallback response
            return {
                "text": "I'm having trouble connecting to the AI service. Please try again.",
                "tokens": 15,
                "latency_ms": 0,
                "provider": "error"
            }
