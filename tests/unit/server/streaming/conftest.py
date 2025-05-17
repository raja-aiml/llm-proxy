# tests/unit/server_streaming/conftest.py

import pytest
from llm_wrapper.server.models import ChatCompletionRequest, Message
import llm_wrapper.server.api as api

@pytest.fixture
def stream_request():
    return ChatCompletionRequest(model="m", messages=[Message(role="user", content="hi")], stream=True)

@pytest.fixture(autouse=True)
def patch_stream_config(monkeypatch):
    monkeypatch.setattr(api, "get_config_or_raise", lambda model: {
        "api": {"url": "http://x"},
        "model": {"path": "p"},
        "parameters": {},
        "system_prompt": ""
    })
    monkeypatch.setattr(api, "build_upstream_payload", lambda req, cfg: {"dummy": True})
    yield