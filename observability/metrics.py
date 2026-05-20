import time
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class TurnMetrics:
    """Metrics for one voice interaction turn."""
    transcript: str = ""
    top_emotion: str = ""
    top_emotion_score: float = 0.0
    all_emotions: List[Dict] = field(default_factory=list)
    docs_retrieved: int = 0
    retrieval_scores: List[float] = field(default_factory=list)
    llm_latency_ms: int = 0
    tokens_generated: int = 0
    total_latency_ms: int = 0
    hallucination_risk: str = "unknown"


def compute_grounding_score(retrieval_scores: List[float]) -> float:
    """
    Simple grounding score = average similarity of retrieved docs.
    Higher = response is more grounded in retrieved knowledge.
    """
    if not retrieval_scores:
        return 0.0
    return round(sum(retrieval_scores) / len(retrieval_scores), 4)


def estimate_hallucination_risk(grounding_score: float) -> str:
    if grounding_score >= 0.75:
        return "Low"
    elif grounding_score >= 0.50:
        return "Medium"
    else:
        return "High"


def build_metrics(
    transcript: str,
    emotions: List[Dict],
    docs: List[Dict],
    llm_result: Dict,
    start_time: float,
) -> TurnMetrics:
    m = TurnMetrics()
    m.transcript = transcript
    m.all_emotions = emotions
    m.top_emotion = emotions[0]["label"] if emotions else "unknown"
    m.top_emotion_score = emotions[0]["score"] if emotions else 0.0
    m.docs_retrieved = len(docs)
    m.retrieval_scores = [d["score"] for d in docs]
    m.llm_latency_ms = llm_result.get("latency_ms", 0)
    m.tokens_generated = llm_result.get("tokens", 0)
    m.total_latency_ms = int((time.time() - start_time) * 1000)

    grounding = compute_grounding_score(m.retrieval_scores)
    m.hallucination_risk = estimate_hallucination_risk(grounding)

    return m
