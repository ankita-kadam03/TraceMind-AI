import time
from dataclasses import dataclass, field
from typing import List, Dict
from prometheus_client import start_http_server, Counter, Histogram, Gauge, REGISTRY

_metrics_initialized = False

# Prometheus metrics
REQUEST_COUNTER     = None
EMOTION_COUNTER     = None
EMOTION_CONFIDENCE  = None
LLM_LATENCY         = None
RAG_LATENCY         = None
TOTAL_LATENCY       = None
GROUNDING_GAUGE     = None
HALLUCINATION_GAUGE = None
TOKENS_COUNTER      = None

def setup_metrics(port: int = 9464):
    global _metrics_initialized
    global REQUEST_COUNTER, EMOTION_COUNTER, EMOTION_CONFIDENCE
    global LLM_LATENCY, RAG_LATENCY, TOTAL_LATENCY
    global GROUNDING_GAUGE, HALLUCINATION_GAUGE, TOKENS_COUNTER

    if _metrics_initialized:
        return

    REQUEST_COUNTER     = Counter("tracemind_requests_total", "Total pipeline requests")
    EMOTION_COUNTER     = Counter("tracemind_emotion_count", "Emotion count", ["emotion"])
    EMOTION_CONFIDENCE  = Gauge("tracemind_emotion_confidence", "Emotion confidence", ["emotion"])
    LLM_LATENCY         = Histogram("tracemind_llm_latency_ms", "LLM latency ms", buckets=[500,1000,2000,5000,10000,30000])
    RAG_LATENCY         = Histogram("tracemind_rag_latency_ms", "RAG latency ms", buckets=[100,500,1000,5000,10000])
    TOTAL_LATENCY       = Histogram("tracemind_total_latency_ms", "Total latency ms", buckets=[1000,5000,10000,30000,60000])
    GROUNDING_GAUGE     = Gauge("tracemind_grounding_score", "Grounding score 0-1")
    HALLUCINATION_GAUGE = Gauge("tracemind_hallucination_score", "Hallucination risk 0-1")
    TOKENS_COUNTER      = Counter("tracemind_tokens_generated_total", "Tokens generated")

    start_http_server(port)
    print(f"[METRICS] Prometheus scrape endpoint → http://localhost:{port}/metrics")
    _metrics_initialized = True

@dataclass
class TurnMetrics:
    transcript: str = ""
    top_emotion: str = ""
    top_emotion_score: float = 0.0
    all_emotions: List[Dict] = field(default_factory=list)
    docs_retrieved: int = 0
    retrieval_scores: List[float] = field(default_factory=list)
    llm_latency_ms: int = 0
    rag_latency_ms: int = 0
    tokens_generated: int = 0
    total_latency_ms: int = 0
    hallucination_risk: str = "unknown"
    grounding_score: float = 0.0

def compute_grounding_score(retrieval_scores):
    if not retrieval_scores:
        return 0.0
    return round(sum(retrieval_scores) / len(retrieval_scores), 4)

def estimate_hallucination_risk(grounding_score):
    if grounding_score >= 0.75:
        return "Low"
    elif grounding_score >= 0.50:
        return "Medium"
    return "High"

def build_metrics(transcript, emotions, docs, llm_result, start_time, rag_latency_ms=0):
    m = TurnMetrics()
    m.transcript        = transcript
    m.all_emotions      = emotions
    m.top_emotion       = emotions[0]["label"] if emotions else "unknown"
    m.top_emotion_score = emotions[0]["score"]  if emotions else 0.0
    m.docs_retrieved    = len(docs)
    m.retrieval_scores  = [d["score"] for d in docs]
    m.llm_latency_ms    = llm_result.get("latency_ms", 0)
    m.rag_latency_ms    = rag_latency_ms
    m.tokens_generated  = llm_result.get("tokens", 0)
    m.total_latency_ms  = int((time.time() - start_time) * 1000)
    m.grounding_score   = compute_grounding_score(m.retrieval_scores)
    m.hallucination_risk = estimate_hallucination_risk(m.grounding_score)

    if _metrics_initialized:
        REQUEST_COUNTER.inc()
        EMOTION_COUNTER.labels(emotion=m.top_emotion).inc()
        for e in emotions:
            EMOTION_CONFIDENCE.labels(emotion=e["label"]).set(e["score"])
        LLM_LATENCY.observe(m.llm_latency_ms)
        RAG_LATENCY.observe(m.rag_latency_ms)
        TOTAL_LATENCY.observe(m.total_latency_ms)
        GROUNDING_GAUGE.set(m.grounding_score)
        HALLUCINATION_GAUGE.set(1 - m.grounding_score)
        TOKENS_COUNTER.inc(m.tokens_generated)

    return m
