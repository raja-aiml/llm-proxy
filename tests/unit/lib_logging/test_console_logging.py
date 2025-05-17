# tests/unit/lib_logging/test_console_logging.py

import logging
from llm_wrapper.lib.logging import setup_logger

def test_setup_logger_file_and_console(tmp_path, capsys):
    log_file = tmp_path / "test.log"
    logger = setup_logger("test_logger", str(log_file), level=logging.INFO, console=True)

    logger.info("hello world")
    captured = capsys.readouterr()

    # Assert console output
    assert "hello world" in captured.err
    # Assert file output
    content = log_file.read_text()
    assert "hello world" in content
    # Assert handler types
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)