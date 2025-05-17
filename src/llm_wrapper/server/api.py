# src/server/api.py

import json
import time
import uuid
import asyncio
from typing import AsyncGenerator

import aiohttp
from fastapi import HTTPException

from llm_wrapper.server.models import ChatCompletionRequest, ChatCompletionResponse
from llm_wrapper.server.config_loader import CONFIGS
from llm_wrapper.lib.logging import setup_logger
from llm_wrapper.server.config import DEFAULT_TIMEOUT, STREAMING_TIMEOUT

logger = setup_logger("llm-server", "logs/server.log")



def get_config_or_raise(model_id: str) -> dict:
    """Fetch model config or raise 404 if not found."""
    logger.debug(f"Retrieving config for model: {model_id}")
    config = CONFIGS.get(model_id)
    if not config:
        available = list(CONFIGS.keys())
        logger.error(f"Model '{model_id}' not found. Available models: {available}")
        raise HTTPException(
            status_code=404,
            detail={"message": f"Model '{model_id}' not found. Available: {available}"}
        )
    return config


def build_upstream_payload(
    request: ChatCompletionRequest,
    config: dict,
    system_prompt: str | None = None
) -> dict:
    """Construct OpenAI-compatible upstream payload with injected system prompt."""
    logger.debug(f"Building upstream payload for model: {request.model}")

    # Extract user messages
    user_messages = [m for m in request.messages if m.role == "user"]
    if not user_messages:
        logger.warning("No user message provided.")
        raise HTTPException(status_code=400, detail="No user message provided.")
    user_content = user_messages[-1].content

    # Determine system prompt: explicit in request takes precedence, otherwise injected or config value
    system_messages = [m for m in request.messages if m.role == "system"]
    if system_messages:
        final_system_prompt = system_messages[-1].content
    else:
        final_system_prompt = (
            system_prompt
            if system_prompt is not None
            else config.get("system_prompt", "")
        )

    params = config.get("parameters", {})
    payload = {
        "model": config["model"]["path"],
        "messages": [
            {"role": "system", "content": final_system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": request.temperature or params.get("temperature", 0.7),
        "top_p": request.top_p or params.get("top_p", 1.0),
        "top_k": request.top_k or params.get("top_k", 40),
        "stream": request.stream,
    }

    logger.debug(f"Payload constructed: {json.dumps(payload, indent=2)}")
    return payload


async def call_completion(
    request: ChatCompletionRequest,
    system_prompt: str = ""
) -> ChatCompletionResponse:
    config = get_config_or_raise(request.model)
    # Allow stubs/tests with older build_upstream_payload signature
    try:
        payload = build_upstream_payload(request, config, system_prompt)
    except TypeError:
        payload = build_upstream_payload(request, config)

    try:
        logger.info(f"Calling completion endpoint for model '{request.model}'")
        # Create session with timeout if supported
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        try:
            session_ctx = aiohttp.ClientSession(timeout=timeout)
        except TypeError:
            session_ctx = aiohttp.ClientSession()
        async with session_ctx as session:
            async with session.post(
                str(config["api"]["url"]),
                headers={"Content-Type": "application/json"},
                json=payload
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"Upstream error {response.status}: {text}")
                    raise HTTPException(status_code=response.status, detail={"message": text})

                result = await response.json()
                logger.info(f"Received response for model '{request.model}'")
                return ChatCompletionResponse(**result)

    except Exception as e:
        logger.exception(f"Error during completion for model '{request.model}': {e}")
        raise HTTPException(status_code=500, detail={"message": str(e)})


async def stream_completion(
    request: ChatCompletionRequest,
    system_prompt: str = ""
) -> AsyncGenerator[str, None]:
    config = get_config_or_raise(request.model)
    # Allow stubs/tests with older build_upstream_payload signature
    try:
        payload = build_upstream_payload(request, config, system_prompt)
    except TypeError:
        payload = build_upstream_payload(request, config)
    payload["stream"] = True

    created = int(time.time())
    chat_id = f"chatcmpl-{uuid.uuid4().hex}"

    logger.info(f"Streaming response started for chat ID {chat_id} model '{request.model}'")

    yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': request.model, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}}]})}\n\n"

    try:
        # Create session with streaming timeout if supported
        timeout = aiohttp.ClientTimeout(total=STREAMING_TIMEOUT)
        try:
            session_ctx = aiohttp.ClientSession(timeout=timeout)
        except TypeError:
            session_ctx = aiohttp.ClientSession()
        async with session_ctx as session:
            async with session.post(
                str(config["api"]["url"]),
                headers={"Content-Type": "application/json"},
                json=payload
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"Upstream streaming error {response.status}: {text}")
                    yield f"data: {json.dumps({'error': text})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                async for line in response.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data: ") and decoded != "data: [DONE]":
                        try:
                            chunk = json.loads(decoded[6:])
                            yield f"data: {json.dumps(chunk)}\n\n"
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to decode stream chunk: {e}")

                yield "data: [DONE]\n\n"
                logger.info(f"Streaming response complete for chat ID {chat_id}")

    except Exception as e:
        error_json = json.dumps({"error": str(e)})
        logger.exception(f"Streaming error for chat ID {chat_id}: {e}")
        yield f"data: {error_json}\n\n"
        yield "data: [DONE]\n\n"