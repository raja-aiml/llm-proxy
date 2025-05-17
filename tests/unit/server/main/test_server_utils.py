# tests/unit/server_main/test_server_utils.py

import llm_wrapper.server.main as main_mod

def test_run_server_calls_uvicorn(monkeypatch):
    called = {}
    monkeypatch.setattr(main_mod.uvicorn, "run", lambda app, host, port: called.update({"host": host, "port": port}))
    main_mod.run_server()
    assert called["host"] == "0.0.0.0"
    assert called["port"] == 8000

def test_health_check():
    result = main_mod.health_check()
    assert result == {"status": "ok"}

def test_list_models_returns_ids(monkeypatch):
    monkeypatch.setattr(main_mod, "CONFIGS", {"a": {}, "b": {}})
    models = main_mod.list_models()
    ids = {m.id for m in models.data}
    assert ids == {"a", "b"}
    assert all(isinstance(m.created, int) for m in models.data)