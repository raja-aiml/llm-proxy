# tests/unit/server_api/test_call_completion_success.py

import pytest
import llm_wrapper.server.api as api
from llm_wrapper.server.api import call_completion
from unit.server.api.dummy_responses import DummyResponse200, DummySession

@pytest.mark.asyncio
async def test_call_completion_success(monkeypatch, chat_request, patch_config_and_payload):
    payload = {
        "id": "id",
        "object": "chat.completion",
        "created": 1,
        "model": "p",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
    }
    monkeypatch.setattr(api.aiohttp, "ClientSession", lambda: DummySession(DummyResponse200(payload)))
    result = await call_completion(chat_request)
    assert result.id == "id"
    assert result.choices[0].message.content == "ok"