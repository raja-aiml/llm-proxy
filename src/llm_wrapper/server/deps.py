# deps.py handles request parsing manually for DI
from fastapi import Depends, Body

# Dependencies to extract and override the system prompt via DI
from llm_wrapper.server.api import get_config_or_raise
from llm_wrapper.server.models import ChatCompletionRequest

async def get_chat_request(
    chat_request: ChatCompletionRequest = Body(...)
) -> ChatCompletionRequest:
    """Dependency that parses the ChatCompletionRequest body."""
    return chat_request

async def get_system_prompt(
    chat_request: ChatCompletionRequest = Depends(get_chat_request)
) -> str:
    """
    Retrieve the system prompt for a chat completion, from config.
    Can be overridden in tests via app.dependency_overrides(get_system_prompt).
    """
    config = get_config_or_raise(chat_request.model)
    return config.get("system_prompt", "")