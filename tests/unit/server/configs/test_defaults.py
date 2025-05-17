# tests/unit/server_config/test_defaults.py

import llm_wrapper.server.config as config

def test_config_defaults():
    assert isinstance(config.HOST, str)
    assert isinstance(config.PORT, int)
    assert config.PORT > 0
    assert isinstance(config.DEFAULT_TIMEOUT, int)
    assert isinstance(config.STREAMING_TIMEOUT, int)
    assert config.DEFAULT_TIMEOUT <= config.STREAMING_TIMEOUT