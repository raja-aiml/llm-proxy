# tests/unit/config_loader/conftest.py

import pytest
import llm_wrapper.server.config_loader as cl

@pytest.fixture(autouse=True)
def isolate_config_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(cl, "CONFIG_DIR", str(tmp_path / "configs"))
    return tmp_path

@pytest.fixture
def config_path(isolate_config_dir):
    path = isolate_config_dir / "configs"
    path.mkdir()
    return path