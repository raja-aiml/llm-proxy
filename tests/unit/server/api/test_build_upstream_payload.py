# tests/unit/server_api/test_build_upstream_payload.py

import pytest
import llm_wrapper.server.api as api
from llm_wrapper.server.models import ChatCompletionRequest, Message
from fastapi import HTTPException

def test_basic_payload_injection(base_config):
    req = ChatCompletionRequest(model="m", messages=[Message(role="user", content="hi")])
    payload = api.build_upstream_payload(req, base_config)

    assert "messages" in payload
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
    assert payload["temperature"] == 1.0
    assert payload["top_p"] == 1.0
    assert payload["top_k"] == 10
    assert payload["stream"] is False

def test_preserves_user_and_system_roles(base_config):
    req = ChatCompletionRequest(
        model="m",
        messages=[
            Message(role="system", content="sys"),
            Message(role="user", content="usr")
        ],
        temperature=1.0,
        top_p=1.0,
        top_k=5,
        stream=True
    )
    payload = api.build_upstream_payload(req, base_config)

    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][0]["content"] == "sys"
    assert payload["messages"][1]["content"] == "usr"
    assert payload["top_k"] == 5
    assert payload["stream"] is True

def test_raises_on_missing_user_message(base_config):
    req = ChatCompletionRequest(model="m", messages=[Message(role="system", content="sys")])
    with pytest.raises(HTTPException):
        api.build_upstream_payload(req, base_config)