#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from fastapi.responses import StreamingResponse

from opentelemetry import trace
from llm_wrapper.server.models import ChatCompletionRequest
from llm_wrapper.server.api import call_completion, stream_completion


# Setup logger and tracer
server_name = "llm-server-wrapper"
logger = logging.getLogger(server_name)
tracer = trace.get_tracer(server_name)


def _trace_input(chat_request: ChatCompletionRequest):
    with tracer.start_as_current_span("chat_completion.prepare_input") as span:
        messages = chat_request.messages or []
        span.set_attribute("messages.count", len(messages))
        if messages and "content" in messages[-1]:
            span.set_attribute("user_input.length", len(messages[-1]["content"]))


def _trace_system_prompt(system_prompt: str):
    with tracer.start_as_current_span("chat_completion.load_system_prompt") as span:
        span.set_attribute("system_prompt.length", len(system_prompt))


def _handle_streaming(chat_request: ChatCompletionRequest, system_prompt: str):
    logger.info("Streaming chat completion")
    with tracer.start_as_current_span("chat_completion.stream_response") as span:
        span.set_attribute("streaming.enabled", True)
        return StreamingResponse(
            stream_completion(chat_request, system_prompt),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked",
                "X-Accel-Buffering": "no"
            }
        )


async def _handle_completion(chat_request: ChatCompletionRequest, system_prompt: str):
    logger.info("Non-streaming chat completion")
    with tracer.start_as_current_span("chat_completion.call_llm") as span:
        span.set_attribute("llm.model", chat_request.model)
        response = await call_completion(chat_request, system_prompt)
        span.set_attribute("response.length", len(str(response)))
        return response


def _trace_error(e: Exception):
    with tracer.start_as_current_span("chat_completion.error") as span:
        span.set_attribute("error", True)
        span.record_exception(e)
        logger.exception("Unhandled error during chat completion")