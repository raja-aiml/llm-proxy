# tests/unit/client_cli/test_chat_core.py

import llm_wrapper.client.cli as cli_mod

class TestChatCLI:

    def test_cli_chat_default(self, cli_runner):
        result = cli_runner.invoke(cli_mod.client, ["--query", "test"])
        assert result.exit_code == 0
        assert "Assistant" in result.output
        assert "hello world" in result.output

    def test_cli_chat_markdown(self, cli_runner):
        result = cli_runner.invoke(cli_mod.client, ["--query", "test", "--markdown", "--no-stream"])
        assert result.exit_code == 0
        assert "Rendered Markdown" in result.output
        assert "hello world" in result.output

    def test_cli_chat_streaming(self, cli_runner):
        result = cli_runner.invoke(cli_mod.client, ["--query", "test", "--stream"])
        assert result.exit_code == 0
        assert "Assistant" in result.output
        assert "hello world" in result.output

    def test_cli_stream_markdown(self, cli_runner):
        result = cli_runner.invoke(cli_mod.client, ["--query", "test", "--stream", "--markdown"])
        assert result.exit_code == 0
        assert "Rendered Markdown" in result.output