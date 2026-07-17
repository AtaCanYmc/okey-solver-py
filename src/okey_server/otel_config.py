# src/okey_server/otel_config.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI


def setup_opentelemetry(app: FastAPI) -> None:
    """
    Sets up OpenTelemetry Tracer Provider and instruments the FastAPI app.
    Spans are exported to standard output/console for tracing log outputs.
    """
    provider = TracerProvider()

    # Simple span processor to write traces to the console
    processor = SimpleSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    # Automatically instrument incoming FastAPI routes with span contexts
    FastAPIInstrumentor.instrument_app(app)
