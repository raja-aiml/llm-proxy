import pytest
from fastapi.testclient import TestClient
from llm_wrapper.server.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_list_models(client):
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_completion_non_streaming(client):
    payload = {
        "model": "expert",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False
    }
    response = client.post("/v1/chat/completions", json=payload)
    # Ensure status code before inspecting JSON
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data.get("id"), str)
    assert data.get("object") == "chat.completion"
    assert isinstance(data.get("choices"), list) and data["choices"], "Expected non-empty choices"
    first = data["choices"][0]
    assert isinstance(first.get("message", {}).get("content"), str)
    assert isinstance(data.get("usage", {}).get("total_tokens"), int)

def test_chat_completion_streaming(client):
    payload = {
        "model": "expert",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True
    }
    # Invoke streaming endpoint against upstream service
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    lines = list(response.iter_lines())
    # Ensure we received at least one data event and a DONE marker
    assert any(line.startswith("data: ") for line in lines), "No data events received"
    assert any("[DONE]" in line for line in lines), "No end-of-stream [DONE] marker"