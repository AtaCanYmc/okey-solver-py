# src/okey_server/logging_config.py
import structlog
from opentelemetry import trace


def inject_otel_trace_id(logger, method_name, event_dict):
    """
    Extracts trace_id and span_id from the active OpenTelemetry context
    and injects them into the structlog event dictionary.
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        context = span.get_span_context()
        event_dict["trace_id"] = f"{context.trace_id:032x}"
        event_dict["span_id"] = f"{context.span_id:016x}"
    return event_dict


def setup_logging() -> None:
    """
    Configures structlog with JSON rendering and correlation trace ID injection.
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        inject_otel_trace_id,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
