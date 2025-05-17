# tests/unit/server_deps/conftest.py

import pytest
from llm_wrapper.server.models import ChatCompletionRequest, Message

@pytest.fixture
def dummy_request():
    return ChatCompletionRequest(model="m", messages=[Message(role="user", content="hi")])