# tests/unit/client_cli/conftest.py

import pytest
from click.testing import CliRunner
import llm_wrapper.client.cli as cli_mod
from unit.client.cli.dummy_openai import DummyOpenAI


@pytest.fixture
def cli_runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def stub_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setattr(cli_mod, "openai", type("FakeOpenAI", (), {"OpenAI": DummyOpenAI}))
    return monkeypatch