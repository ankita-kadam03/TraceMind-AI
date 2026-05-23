import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from opentelemetry.sdk.resources import Resource

# Env config
EXPORTER_TYPE = os.getenv("OTEL_EXPORTER", "console")   # "console" | "jaeger"
JAEGER_HOST   = os.getenv("JAEGER_HOST", "localhost")
JAEGER_PORT   = int(os.getenv("JAEGER_PORT", "4317"))
METRICS_PORT  = int(os.getenv("METRICS_PORT", "9464"))   # Prometheus scrape port


def setup_tracing(service_name: str = "tracemind-ai") -> TracerProvider:
    """
    Initialize OpenTelemetry tracing + Prometheus metrics.

    Tracing modes:
        console (default) → spans print as JSON to terminal
        jaeger            → set OTEL_EXPORTER=jaeger, run docker-compose up -d
                            view at http://localhost:16686

    Metrics (always on):
        Prometheus scrapes http://localhost:9464/metrics
        Grafana reads from Prometheus at http://localhost:3000
    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # ── Tracing exporter ──────────────────────────────────────
    if EXPORTER_TYPE == "jaeger":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(
                endpoint=f"http://{JAEGER_HOST}:{JAEGER_PORT}",
                insecure=True,
            )
            provider.add_span_processor(BatchSpanProcessor(exporter))
            print(f"[OTEL] Jaeger exporter  → http://{JAEGER_HOST}:{JAEGER_PORT}")
            print(f"[OTEL] Jaeger UI        → http://localhost:16686")
        except ImportError:
            print("[OTEL] WARNING: otlp exporter not installed. Falling back to console.")
            provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    else:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        print("[OTEL] Console exporter active (set OTEL_EXPORTER=jaeger for Jaeger UI)")

    trace.set_tracer_provider(provider)

    # ── Prometheus metrics (always on) ────────────────────────
    try:
        from observability.metrics import setup_metrics
        setup_metrics(port=METRICS_PORT)
        print(f"[OTEL] Prometheus metrics → http://localhost:{METRICS_PORT}/metrics")
        print(f"[OTEL] Grafana dashboard  → http://localhost:3000")
        print(f"[OTEL]   login: admin / tracemind")
    except Exception as e:
        print(f"[OTEL] WARNING: Prometheus metrics not started: {e}")
        print(f"[OTEL] Install with: pip install opentelemetry-exporter-prometheus prometheus-client")

    return provider


def get_tracer(name: str):
    return trace.get_tracer(name)
