# tests/unit/server_main/conftest.py

import pytest
from llm_wrapper.server.models import ChatCompletionRequest

@pytest.fixture
def sample_request():
    return ChatCompletionRequest(
        model="test-model",
        messages=[{"role": "user", "content": "hello"}],
        stream=False
    )