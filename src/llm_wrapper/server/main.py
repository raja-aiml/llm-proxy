import time
import uvicorn
import os
from llm_wrapper.lib.logging import setup_logger
import logging  # retain for TelemetrySetup and opentelemetry internals

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse

from llm_wrapper.lib.telemetry.telemetry import TelemetrySetup
from llm_wrapper.server.models import ChatCompletionRequest, ModelList, ModelData
from llm_wrapper.server.api import call_completion, stream_completion
from llm_wrapper.server.config_loader import CONFIGS
from llm_wrapper.server.deps import get_chat_request, get_system_prompt
from llm_wrapper.server.handlers.chat import (
    _trace_input,
    _trace_system_prompt,
    _handle_streaming,
    _handle_completion,
    _trace_error,
)

from opentelemetry import trace, metrics

# Logging setup using structured logger
logger = setup_logger(
    "llm-server",
    os.getenv("LOG_FILE", "logs/server.log"),
    console=True
)

# Initialize OpenTelemetry or use no-op tracer/meter if disabled
_disable_telemetry = os.getenv("DISABLE_TELEMETRY", "false").lower() in ("1", "true", "yes")
if _disable_telemetry:
    logger.info("Telemetry disabled via DISABLE_TELEMETRY env var")
    telemetry = None
    # No-op implementations
    class _NoOpSpan:
        def set_attribute(self, key, value): return self
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass
    class _NoOpTracer:
        def start_as_current_span(self, name): return _NoOpSpan()
    class _NoOpCounter:
        def __init__(self, *args, **kwargs): pass
        def add(self, value, attributes=None): pass
    class _NoOpHistogram(_NoOpCounter):
        def record(self, value, attributes=None): pass
    class _NoOpMeter:
        def create_counter(self, name, unit=None, description=None): return _NoOpCounter()
        def create_histogram(self, name, unit=None, description=None): return _NoOpHistogram()
    tracer = _NoOpTracer()
    meter = _NoOpMeter()
else:
    telemetry = TelemetrySetup(
        service_name="llm-wrapper",
        otlp_endpoint="http://localhost:4318/v1/traces",
        prometheus_port=9464
    )
    tracer = telemetry.get_tracer()
    meter = telemetry.get_meter()

# Prometheus Metrics
request_counter = meter.create_counter(
    name="http_requests_total",
    unit="1",
    description="Total HTTP requests received"
)

chat_completion_counter = meter.create_counter(
    name="chat_completions_total",
    unit="1",
    description="Total chat completion requests"
)

response_length_histogram = meter.create_histogram(
    name="chat_completion_response_length_bytes",
    unit="bytes",
    description="Size of chat completion responses"
)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Wrapper API",
    description="OpenAI-compatible wrapper with tracing and metrics",
    version="1.0.0"
)

# Configs loaded at import time in config_loader module
logger.info("Server startup complete. Loaded models: %s", list(CONFIGS.keys()))


@app.get("/health")
def health_check():
    with tracer.start_as_current_span("health_check"):
        request_counter.add(1, {"route": "/health"})
        logger.info("Health check successful")
        return {"status": "ok"}


@app.get("/v1/models", response_model=ModelList)
def list_models():
    with tracer.start_as_current_span("list_models"):
        request_counter.add(1, {"route": "/v1/models"})
        timestamp = int(time.time())
        models = [ModelData(id=model_id, created=timestamp) for model_id in CONFIGS.keys()]
        return ModelList(data=models)


@app.post("/v1/chat/completions")
async def chat_completion(
    chat_request: ChatCompletionRequest = Depends(get_chat_request),
    system_prompt: str = Depends(get_system_prompt)
):
    """
    Handles OpenAI-compatible chat completion requests with optional streaming.
    Includes fine-grained tracing and Prometheus metrics.
    """
    with tracer.start_as_current_span("chat_completion") as root_span:
        root_span.set_attribute("model", chat_request.model)
        root_span.set_attribute("streaming", chat_request.stream)

        # Track request
        request_counter.add(1, {"route": "/v1/chat/completions"})
        chat_completion_counter.add(1, {"model": chat_request.model})

        # Attach input to trace
        if chat_request.messages:
            root_span.set_attribute("input.message_count", len(chat_request.messages))
            # Fix here - using dot notation instead of subscript
            root_span.set_attribute("input.last_message", chat_request.messages[-1].content[:100])

        try:
            _trace_input(chat_request)
            _trace_system_prompt(system_prompt)

            if chat_request.stream:
                return _handle_streaming(chat_request, system_prompt)

            # Non-streaming: directly call completion and measure
            response = await call_completion(chat_request, system_prompt)

            response_str = str(response)
            response_length = len(response_str)

            root_span.set_attribute("output.preview", response_str[:200])
            root_span.set_attribute("output.length", response_length)
            response_length_histogram.record(response_length, {"model": chat_request.model})

            return response

        except Exception as e:
            _trace_error(e)
            raise HTTPException(
                status_code=500,
                detail="Internal server error",
                headers={"X-Error": "Internal Server Error"}
            ) from e

@app.exception_handler(HTTPException)
async def openai_style_error(request: Request, exc: HTTPException):
    with tracer.start_as_current_span("http_exception"):
        logger.error("HTTPException %s: %s", exc.status_code, exc.detail)
        detail = exc.detail
        # If detail is a dict, merge fields; otherwise stringify
        if isinstance(detail, dict):
            err = detail.copy()
            err["type"] = "api_error"
        else:
            err = {"message": str(detail), "type": "api_error"}
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": err}
        )


def run():
    logger.info("🚀 Starting FastAPI app on http://0.0.0.0:8000")
    # Start Uvicorn without reload flag to match testing signature
    uvicorn.run("llm_wrapper.server.main:app", "0.0.0.0", 8000)

# Alias for script entrypoint and test compatibility
run_server = run


if __name__ == "__main__":
    run()