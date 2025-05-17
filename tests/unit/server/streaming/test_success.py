# tests/unit/server_streaming/test_success.py

import pytest
from llm_wrapper.server.api import stream_completion
import llm_wrapper.server.api as api
from unit.server.streaming.dummy_session import DummySession

@pytest.mark.asyncio
async def test_stream_completion_success(monkeypatch, stream_request):
    class DummyStreamResponse:
        def __init__(self, lines):
            self.status = 200
            class AsyncIter:
                def __init__(self, lines): self._it = iter(lines)
                def __aiter__(self): return self
                async def __anext__(self):
                    try: return next(self._it)
                    except StopIteration: raise StopAsyncIteration
            self.content = AsyncIter(lines)
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass

    lines = [b'data: {"k": "v"}\n', b'data: [DONE]\n']
    monkeypatch.setattr(api.aiohttp, "ClientSession", lambda: DummySession(DummyStreamResponse(lines)))

    parts = [chunk async for chunk in stream_completion(stream_request)]
    assert any('"k"' in p and '"v"' in p for p in parts)
    assert parts[-1].strip() == "data: [DONE]"