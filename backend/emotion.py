from transformers import pipeline
from opentelemetry import trace
from typing import Dict, List

tracer = trace.get_tracer("emotion")

MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"

_classifier = None


def _get_classifier():
    global _classifier
    if _classifier is None:
        print("[EMOTION] Loading emotion model (first run downloads ~300MB)...")
        _classifier = pipeline(
            "text-classification",
            model=MODEL_NAME,
            top_k=None,
            device=-1,  # CPU
        )
        print("[EMOTION] Model loaded.")
    return _classifier


def detect_emotions(text: str) -> List[Dict]:
    """
    Returns a sorted list of emotions with scores.
    Example: [{"label": "sadness", "score": 0.75}, ...]
    """
    with tracer.start_as_current_span("detect_emotions") as span:
        span.set_attribute("input_text", text)

        clf = _get_classifier()
        results = clf(text)[0]

        sorted_emotions = sorted(results, key=lambda x: x["score"], reverse=True)

        for e in sorted_emotions:
            span.set_attribute(f"emotion.{e['label']}", round(e["score"], 4))

        top = sorted_emotions[0]
        span.set_attribute("top_emotion", top["label"])
        span.set_attribute("top_score", round(top["score"], 4))

        return sorted_emotions


def top_emotion(text: str) -> tuple[str, float]:
    """Returns (label, confidence) for the dominant emotion."""
    emotions = detect_emotions(text)
    return emotions[0]["label"], emotions[0]["score"]


def emotion_context_string(text: str) -> str:
    """
    Builds a context string for RAG query augmentation.
    Example: 'User feels sadness (0.75), stress (0.61)'
    """
    emotions = detect_emotions(text)
    top3 = emotions[:3]
    parts = [f"{e['label']} ({e['score']:.2f})" for e in top3]
    return "User feels " + ", ".join(parts)
