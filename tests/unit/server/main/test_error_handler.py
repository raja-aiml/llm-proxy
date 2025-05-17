# tests/unit/server_main/test_error_handler.py

import pytest
import json
from fastapi import HTTPException
from starlette.responses import JSONResponse
import llm_wrapper.server.main as main_mod

@pytest.mark.asyncio
async def test_error_handler_str_detail():
    exc = HTTPException(status_code=400, detail="error occurred")
    response = await main_mod.openai_style_error(None, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    data = json.loads(response.body.decode())
    assert data["error"]["message"] == "error occurred"
    assert data["error"]["type"] == "api_error"

@pytest.mark.asyncio
async def test_error_handler_dict_detail():
    exc = HTTPException(status_code=422, detail={"message": "err", "code": 123})
    response = await main_mod.openai_style_error(None, exc)
    data = json.loads(response.body.decode())["error"]
    assert data["message"] == "err"
    assert data["type"] == "api_error"
    assert data["code"] == 123

@pytest.mark.asyncio
async def test_error_handler_other_detail():
    exc = HTTPException(status_code=500, detail=["unexpected"])
    response = await main_mod.openai_style_error(None, exc)
    error = json.loads(response.body.decode())["error"]
    assert error["message"] == str(["unexpected"])
    assert error["type"] == "api_error"