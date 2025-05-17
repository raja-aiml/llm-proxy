# tests/unit/server_main/test_chat_completion.py

import pytest
from starlette.responses import StreamingResponse
from llm_wrapper.server.models import ChatCompletionRequest
import llm_wrapper.server.main as main_mod

@pytest.mark.asyncio
async def test_chat_completion_non_streaming(monkeypatch, sample_request):
    prompt = "sys"

    async def fake_call(req, prompt):
        assert req is sample_request
        return {"ok": True}

    monkeypatch.setattr(main_mod, "call_completion", fake_call)
    result = await main_mod.chat_completion(sample_request, prompt)
    assert result == {"ok": True}

@pytest.mark.asyncio
async def test_chat_completion_streaming(monkeypatch):
    request = ChatCompletionRequest(
        model="test-model",
        messages=[{"role": "user", "content": "hello"}],
        stream=True
    )
    prompt = "sys"

    async def fake_stream(req, prompt):
        assert req is request
        yield b"chunk1"
        yield b"chunk2"

    monkeypatch.setattr(main_mod, "stream_completion", fake_stream)
    result = await main_mod.chat_completion(request, prompt)

    assert isinstance(result, StreamingResponse)
    assert result.media_type == "text/event-stream"
    assert result.headers["Cache-Control"] == "no-cache"
    assert result.headers["Connection"] == "keep-alive"
    assert result.headers["Transfer-Encoding"] == "chunked"
    assert result.headers["X-Accel-Buffering"] == "no"