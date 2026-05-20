import time
from typing import List, Dict
from opentelemetry import trace
from transformers import pipeline

tracer = trace.get_tracer("llm")

DEFAULT_MODEL = "facebook/opt-125m"
_generator = None


def _get_generator(model_name: str):
    global _generator
    if _generator is None:
        print(f"[LLM] Loading model {model_name} (first run downloads it)...")
        _generator = pipeline(
            "text-generation",
            model=model_name,
            device=-1,
        )
        print("[LLM] Model loaded.")
    return _generator


def build_prompt(user_text: str, emotion_context: str, retrieved_docs: List[Dict]) -> str:
    docs_text = "\n".join(f"- {d['content'][:200]}" for d in retrieved_docs)
    return f"""You are a supportive assistant. {emotion_context}. 
Relevant info: {docs_text}
User said: {user_text}
Response:"""


def generate(
    user_text: str,
    emotion_context: str,
    retrieved_docs: List[Dict],
    model: str = DEFAULT_MODEL,
) -> Dict:
    with tracer.start_as_current_span("llm_generate") as span:
        span.set_attribute("model", model)
        span.set_attribute("user_text", user_text)

        prompt = build_prompt(user_text, emotion_context, retrieved_docs)
        gen = _get_generator(model)

        t0 = time.time()
        output = gen(
            prompt,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7,
            pad_token_id=50256,
        )
        latency_ms = int((time.time() - t0) * 1000)

        full_text = output[0]["generated_text"]
        response = full_text.split("Response:")[-1].strip()

        span.set_attribute("latency_ms", latency_ms)

        return {
            "response": response,
            "latency_ms": latency_ms,
            "tokens": len(response.split()),
        }