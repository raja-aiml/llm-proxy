# tests/unit/client_cli/test_chat_errors.py

import llm_wrapper.client.cli as cli_mod

class TestChatErrors:

    def test_cli_single_response_error(self, monkeypatch, cli_runner):
        class ErrorOpenAI:
            def __init__(self, base_url, api_key): pass
            @property
            def chat(self): return self
            @property
            def completions(self): return self
            def create(self, model, messages, temperature=None, stream=False):
                raise RuntimeError("test error")
        monkeypatch.setattr(cli_mod, "openai", type("Fake", (), {"OpenAI": ErrorOpenAI}))
        result = cli_runner.invoke(cli_mod.client, ["--query", "test", "--no-stream"])
        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_cli_stream_response_error(self, monkeypatch, cli_runner):
        class ErrorOpenAI:
            def __init__(self, base_url, api_key): pass
            @property
            def chat(self): return self
            @property
            def completions(self): return self
            def create(self, model, messages, temperature=None, stream=False):
                raise RuntimeError("stream error")
        monkeypatch.setattr(cli_mod, "openai", type("Fake", (), {"OpenAI": ErrorOpenAI}))
        result = cli_runner.invoke(cli_mod.client, ["--query", "test", "--stream"])
        assert result.exit_code != 0
        assert "Error:" in result.output