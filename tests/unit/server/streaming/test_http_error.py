# tests/unit/server_streaming/test_http_error.py

import pytest
from llm_wrapper.server.api import stream_completion
import llm_wrapper.server.api as api
from unit.server.streaming.dummy_session import DummySession

@pytest.mark.asyncio
async def test_stream_completion_http_error(monkeypatch, stream_request):
    class DummyErrorStream:
        def __init__(self): self.status = 500
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        async def text(self): return "error"
        content = []

    monkeypatch.setattr(api.aiohttp, "ClientSession", lambda: DummySession(DummyErrorStream()))
    parts = [chunk async for chunk in stream_completion(stream_request)]
    assert any("error" in p.lower() for p in parts)
    assert parts[-1].strip() == "data: [DONE]"