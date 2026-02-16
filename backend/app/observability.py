"""OpenTelemetry tracing initialisation for FastAPI and SQLAlchemy."""

import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracing(app, sqlalchemy_engine: Optional[object] = None) -> None:
    """Initialize OpenTelemetry tracing with OTLP exporter.

    - Reads endpoint from OTEL_EXPORTER_OTLP_ENDPOINT (default: http://jaeger:4317)
    - Sets resource attributes for service name and environment.
    - Instruments FastAPI, SQLAlchemy (if engine provided), and requests.
    """
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317")
    service_name = os.getenv("OTEL_SERVICE_NAME", "expense-backend")
    environment = os.getenv("OTEL_ENVIRONMENT", os.getenv("ENVIRONMENT", "dev"))

    resource = Resource.create(
        {
            "service.name": service_name,
            "deployment.environment": environment,
        }
    )
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Auto-instrument frameworks/libraries
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
    if sqlalchemy_engine is not None:
        try:
            SQLAlchemyInstrumentor().instrument(engine=sqlalchemy_engine)
        except Exception:
            # Best-effort instrumentation
            pass
