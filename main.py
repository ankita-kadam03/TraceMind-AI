"""
VoiceEmotionRAG — Terminal App
==============================
Usage:
    python main.py                    # 5 second voice recording
    python main.py --duration 10      # 10 second recording
    python main.py --text "I feel stressed"  # skip mic, use text directly
    python main.py --build-index      # rebuild vector DB from data/
"""

import argparse
import sys
import time

# Setup OTel FIRST before importing any module that uses trace
from observability.tracing import setup_tracing
setup_tracing("voice-emotion-rag")

from backend.speech   import record_and_transcribe
from backend.emotion  import detect_emotions, emotion_context_string
from backend.rag      import retrieve, build_vectorstore
from backend.llm      import generate
from observability.metrics import build_metrics
from dashboard.charts import (
    print_header,
    print_transcript,
    print_emotions,
    print_retrieved_docs,
    print_response,
    print_metrics,
    print_separator,
    console,
)


def run_pipeline(text: str = None, duration: int = 5, model: str = "mistral"):
    start = time.time()
    print_separator()

    # Step 1 — Speech to text
    if text:
        transcript = text
        console.print(f"[dim][TEXT MODE] Using: {transcript}[/]")
    else:
        transcript = record_and_transcribe(duration=duration, model_size="base")

    print_transcript(transcript)

    # Step 2 — Emotion detection
    console.print("[dim]Detecting emotions...[/]")
    emotions = detect_emotions(transcript)
    emotion_ctx = emotion_context_string(transcript)
    print_emotions(emotions)

    # Step 3 — RAG retrieval
    console.print("[dim]Retrieving relevant documents...[/]")
    docs = retrieve(transcript, emotion_context=emotion_ctx, k=3)
    print_retrieved_docs(docs)

    # Step 4 — LLM response
    console.print("[dim]Generating response...[/]")
    llm_result = generate(transcript, emotion_ctx, docs, model=model)
    print_response(llm_result["response"])

    # Step 5 — Metrics + observability dashboard
    metrics = build_metrics(transcript, emotions, docs, llm_result, start)
    print_metrics(metrics)
    print_separator()


def main():
    parser = argparse.ArgumentParser(description="VoiceEmotionRAG — terminal app")
    parser.add_argument("--duration",    type=int, default=5,       help="Recording duration in seconds")
    parser.add_argument("--text",        type=str, default=None,    help="Skip mic, use text directly")
    parser.add_argument("--model",       type=str, default="facebook/opt-125m", help="Ollama model name")
    parser.add_argument("--build-index", action="store_true",       help="Rebuild ChromaDB index and exit")
    args = parser.parse_args()

    print_header()

    if args.build_index:
        build_vectorstore()
        console.print("[green]Vector store built successfully.[/]")
        sys.exit(0)

    # Interactive loop
    console.print("[dim]Press Ctrl+C to quit.[/]\n")
    try:
        while True:
            run_pipeline(
                text=args.text,
                duration=args.duration,
                model=args.model,
            )
            if args.text:
                break  # one-shot if text mode
    except KeyboardInterrupt:
        console.print("\n[dim]Bye![/]")


if __name__ == "__main__":
    main()
