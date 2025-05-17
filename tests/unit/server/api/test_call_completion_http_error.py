# tests/unit/server_api/test_call_completion_http_error.py

import pytest
from fastapi import HTTPException
import llm_wrapper.server.api as api
from llm_wrapper.server.api import call_completion
from unit.server.api.dummy_responses import DummyResponseError, DummySession

@pytest.mark.asyncio
async def test_call_completion_http_error(monkeypatch, chat_request, patch_config_and_payload):
    monkeypatch.setattr(api.aiohttp, "ClientSession", lambda: DummySession(DummyResponseError(400, "bad request")))
    with pytest.raises(HTTPException) as exc:
        await call_completion(chat_request)
    assert exc.value.status_code == 500
    assert "bad request" in str(exc.value.detail)