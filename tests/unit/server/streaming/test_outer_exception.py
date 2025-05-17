# tests/unit/server_streaming/test_outer_exception.py

import pytest
from llm_wrapper.server.api import stream_completion
import llm_wrapper.server.api as api

@pytest.mark.asyncio
async def test_stream_completion_outer_exception(monkeypatch, stream_request):
    class FailingSession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        def post(self, *args, **kwargs): raise RuntimeError("connection fail")

    monkeypatch.setattr(api.aiohttp, "ClientSession", lambda: FailingSession())
    parts = [chunk async for chunk in stream_completion(stream_request)]
    assert any("connection fail" in p for p in parts)
    assert parts[-1].strip() == "data: [DONE]"