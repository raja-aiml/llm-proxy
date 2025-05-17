# tests/unit/client_cli/test_interactive_mode.py

import llm_wrapper.client.cli as cli_mod


import re

ansi_escape = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text):
    return ansi_escape.sub("", text)

def test_cli_interactive_mode(monkeypatch, cli_runner):
    class DummyNoCallOpenAI:
        def __init__(self, base_url, api_key): pass
        @property
        def chat(self): return self
        @property
        def completions(self): return self
        def create(self, model, messages, temperature=None, stream=False):
            raise AssertionError("Should not be called")

    monkeypatch.setattr(cli_mod, "openai", type("Fake", (), {"OpenAI": DummyNoCallOpenAI}))
    result = cli_runner.invoke(cli_mod.client, [], input="exit\n")
    
    clean_output = strip_ansi(result.output)  # 👈 strip color codes

    assert result.exit_code == 0
    assert "Interactive LLM Chat" in clean_output
    assert "Type 'exit' or 'quit' to end." in clean_output
def test_cli_interactive_dispatch(cli_runner):
    result = cli_runner.invoke(cli_mod.client, [], input="hello world\nexit\n")
    assert result.exit_code == 0
    assert "You:" in result.output
    assert "Assistant:" in result.output
    assert "hello world" in result.output