# tests/unit/lib_logging/test_file_logging.py

import logging
from llm_wrapper.lib.logging import setup_logger

def test_setup_logger_no_console(tmp_path, capsys):
    log_file = tmp_path / "test_no_console.log"
    logger = setup_logger("test_logger_no_console", str(log_file), level=logging.WARNING, console=False)

    logger.info("this should not show")
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == ""
    assert "this should not show" not in log_file.read_text()

    logger.warning("warn message")
    log_content = log_file.read_text()
    assert "warn message" in log_content
    assert "WARNING" in log_content