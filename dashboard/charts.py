from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box

console = Console()

EMOTION_COLORS = {
    "joy":      "green",
    "sadness":  "blue",
    "anger":    "red",
    "fear":     "magenta",
    "disgust":  "yellow",
    "surprise": "cyan",
    "neutral":  "white",
}

EMOTION_EMOJIS = {
    "joy":      "😊",
    "sadness":  "😔",
    "anger":    "😠",
    "fear":     "😨",
    "disgust":  "🤢",
    "surprise": "😲",
    "neutral":  "😐",
}


def _bar(score: float, width: int = 20) -> str:
    filled = int(score * width)
    return "█" * filled + "░" * (width - filled)


def print_header():
    console.print(
        Panel(
            "[bold cyan]Voice Emotion RAG[/] — [dim]OpenTelemetry Observability[/]",
            box=box.DOUBLE,
            style="cyan",
        )
    )


def print_transcript(text: str):
    console.print(
        Panel(f"[bold white]{text}[/]", title="[cyan]You said[/]", box=box.ROUNDED)
    )


def print_emotions(emotions: list):
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta")
    table.add_column("Emotion", width=12)
    table.add_column("Confidence", width=24)
    table.add_column("Score", width=8)

    for e in emotions[:5]:
        label = e["label"]
        score = e["score"]
        color = EMOTION_COLORS.get(label, "white")
        emoji = EMOTION_EMOJIS.get(label, "")
        bar = _bar(score)
        table.add_row(
            f"[{color}]{emoji} {label}[/]",
            f"[{color}]{bar}[/]",
            f"[{color}]{score:.2%}[/]",
        )

    console.print(Panel(table, title="[magenta]Emotion detection[/]", box=box.ROUNDED))


def print_retrieved_docs(docs: list):
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold green")
    table.add_column("Source", width=30)
    table.add_column("Similarity", width=12)
    table.add_column("Preview", width=50)

    for d in docs:
        sim = d["score"]
        color = "green" if sim >= 0.75 else "yellow" if sim >= 0.5 else "red"
        source = d["source"].split("/")[-1]
        preview = d["content"][:80].replace("\n", " ") + "..."
        table.add_row(
            f"[dim]{source}[/]",
            f"[{color}]{sim:.2f}[/]",
            f"[dim]{preview}[/]",
        )

    console.print(Panel(table, title="[green]Retrieved documents[/]", box=box.ROUNDED))


def print_response(response: str):
    console.print(
        Panel(
            f"[bold white]{response}[/]",
            title="[bold cyan]AI Response[/]",
            box=box.ROUNDED,
            style="cyan",
        )
    )


def print_metrics(metrics):
    grounding = (
        sum(metrics.retrieval_scores) / len(metrics.retrieval_scores)
        if metrics.retrieval_scores else 0.0
    )
    halluc_pct = round((1 - grounding) * 100, 1)
    grounding_pct = round(grounding * 100, 1)

    risk_color = {"Low": "green", "Medium": "yellow", "High": "red"}.get(
        metrics.hallucination_risk, "white"
    )

    # Trace timeline panel
    timeline = Text()
    timeline.append("  Audio captured\n", style="dim")
    timeline.append("  ↓ Speech transcribed\n", style="dim")
    timeline.append("  ↓ Emotion analyzed\n", style="dim")
    timeline.append("  ↓ Docs retrieved\n", style="dim")
    timeline.append("  ↓ LLM responded\n", style="dim")

    # Metrics panel
    stats = Table(box=box.SIMPLE, show_header=False)
    stats.add_column("Key", style="dim", width=22)
    stats.add_column("Value", width=20)
    stats.add_row("Top emotion",   f"[bold]{metrics.top_emotion}[/] ({metrics.top_emotion_score:.0%})")
    stats.add_row("Docs retrieved", str(metrics.docs_retrieved))
    stats.add_row("LLM latency",   f"{metrics.llm_latency_ms} ms")
    stats.add_row("Tokens out",    str(metrics.tokens_generated))
    stats.add_row("Total latency", f"{metrics.total_latency_ms} ms")
    stats.add_row("Grounding",     f"[green]{grounding_pct}%[/]")
    stats.add_row("Hallucination", f"[{risk_color}]{halluc_pct}% ({metrics.hallucination_risk})[/]")

    console.print(
        Columns(
            [
                Panel(timeline, title="[yellow]Trace timeline[/]", box=box.ROUNDED, width=36),
                Panel(stats,    title="[yellow]Observability metrics[/]", box=box.ROUNDED),
            ]
        )
    )


def print_separator():
    console.rule(style="dim")
