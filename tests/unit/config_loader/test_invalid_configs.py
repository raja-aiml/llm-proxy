# tests/unit/config_loader/test_invalid_configs.py

import logging
import llm_wrapper.server.config_loader as cl

def test_load_all_configs_with_invalid_yaml(config_path, caplog):
    # Ensure log level is low enough
    caplog.set_level(logging.DEBUG)

    # Add a temporary plain StreamHandler to root logger
    logger = logging.getLogger("llm-server")
    logger.propagate = True  # Ensure logs propagate to root logger

    # Write a bad config file
    bad_file = config_path / "bad.yaml"
    bad_file.write_text("::: not valid yaml :::")

    # Load configs
    configs = cl.load_all_configs()

    # Check the bad config was not loaded
    assert "bad" not in configs

    # Inspect log capture
    logs = caplog.text.lower()
    assert "failed to load config file" in logs

    errors = [record.message for record in caplog.records if record.levelname == "ERROR"]
    assert any("failed to load" in msg.lower() for msg in errors)