# tests/unit/server_api/conftest.py

import pytest
from llm_wrapper.server.models import ChatCompletionRequest, Message
import llm_wrapper.server.api as api

@pytest.fixture
def patch_config_and_payload(monkeypatch):
    monkeypatch.setattr(api, "get_config_or_raise", lambda model: {
        "api": {"url": "http://x"},
        "model": {"path": "p"},
        "parameters": {},
        "system_prompt": ""
    })
    monkeypatch.setattr(api, "build_upstream_payload", lambda req, cfg: {"dummy": True})
    yield

@pytest.fixture
def chat_request():
    return ChatCompletionRequest(model="m", messages=[Message(role="user", content="hi")])

@pytest.fixture
def base_config():
    return {
        "model": {"path": "mp"},
        "parameters": {"temperature": 0.5, "top_p": 0.6, "top_k": 10},
        "system_prompt": "sp"
    }