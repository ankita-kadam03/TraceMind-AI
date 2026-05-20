import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from opentelemetry.sdk.resources import Resource

# OTEL_EXPORTER: "console" (default) or "jaeger"
EXPORTER_TYPE  = os.getenv("OTEL_EXPORTER", "console")
JAEGER_HOST    = os.getenv("JAEGER_HOST", "localhost")
JAEGER_PORT    = int(os.getenv("JAEGER_PORT", "4317"))


def setup_tracing(service_name: str = "voice-emotion-rag") -> TracerProvider:
    """
    Initialize OpenTelemetry tracing.

    Console mode (default):
        spans print as JSON to terminal — zero setup needed.

    Jaeger mode:
        set env var OTEL_EXPORTER=jaeger
        then run:  docker-compose up -d
        then open: http://localhost:16686
    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if EXPORTER_TYPE == "jaeger":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(
                endpoint=f"http://{JAEGER_HOST}:{JAEGER_PORT}",
                insecure=True,
            )
            provider.add_span_processor(BatchSpanProcessor(exporter))
            print(f"[OTEL] Jaeger exporter → http://{JAEGER_HOST}:{JAEGER_PORT}")
            print(f"[OTEL] View traces at  → http://localhost:16686")
        except ImportError:
            print("[OTEL] WARNING: otlp exporter not installed. Falling back to console.")
            print("[OTEL] Install with: pip install opentelemetry-exporter-otlp-proto-grpc")
            provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    else:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        print("[OTEL] Console exporter active (set OTEL_EXPORTER=jaeger for Jaeger UI)")

    trace.set_tracer_provider(provider)
    return provider


def get_tracer(name: str):
    return trace.get_tracer(name)

