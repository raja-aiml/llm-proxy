# tests/unit/server_api/test_get_config_or_raise.py

import pytest
import json
from fastapi import HTTPException
import llm_wrapper.server.api as api

def test_get_config_or_raise_valid(monkeypatch):
    expected = {
        "api": {"url": "http://x"},
        "model": {"path": "p"},
        "parameters": {},
        "system_prompt": ""
    }
    monkeypatch.setattr(api, "CONFIGS", {"a": expected})
    config = api.get_config_or_raise("a")
    assert config == expected

def test_get_config_or_raise_invalid(monkeypatch):
    monkeypatch.setattr(api, "CONFIGS", {})
    with pytest.raises(HTTPException) as exc:
        api.get_config_or_raise("b")
    assert exc.value.status_code == 404
    assert "Model 'b' not found" in json.dumps(exc.value.detail)