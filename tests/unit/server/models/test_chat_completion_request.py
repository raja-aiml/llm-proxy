# tests/unit/server_models/test_chat_completion_request.py

import pytest
from pydantic import ValidationError
from llm_wrapper.server.models import ChatCompletionRequest, Function, Tool

def test_chatcompletionrequest_invalid_with_both_functions_and_tools():
    data = {
        "model": "m",
        "messages": [],
        "functions": [Function(name="f")],
        "tools": [Tool(type="function", function=Function(name="t"))]
    }
    with pytest.raises(ValidationError) as exc:
        ChatCompletionRequest(**data)

    # Match actual error string
    assert "Cannot provide both 'functions' and 'tools'" in str(exc.value)

    