# tests/unit/server_deps/test_get_chat_request.py

import pytest
import llm_wrapper.server.deps as deps_mod

@pytest.mark.asyncio
async def test_get_chat_request(dummy_request):
    result = await deps_mod.get_chat_request(dummy_request)
    assert result is dummy_request