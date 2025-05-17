# tests/unit/server_deps/test_get_system_prompt_invalid.py

import pytest
from fastapi import HTTPException
import llm_wrapper.server.deps as deps_mod

@pytest.mark.asyncio
async def test_get_system_prompt_invalid(monkeypatch, dummy_request):
    def raise_exc(model):
        raise HTTPException(status_code=404, detail="not found")
    monkeypatch.setattr(deps_mod, "get_config_or_raise", raise_exc)
    with pytest.raises(HTTPException):
        await deps_mod.get_system_prompt(dummy_request)