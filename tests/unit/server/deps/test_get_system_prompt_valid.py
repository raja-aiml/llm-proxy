# tests/unit/server_deps/test_get_system_prompt_valid.py

import pytest
import llm_wrapper.server.deps as deps_mod

@pytest.mark.asyncio
async def test_get_system_prompt_valid(monkeypatch, dummy_request):
    expected_prompt = "custom prompt"
    monkeypatch.setattr(deps_mod, "get_config_or_raise", lambda model: {"system_prompt": expected_prompt})
    result = await deps_mod.get_system_prompt(dummy_request)
    assert result == expected_prompt