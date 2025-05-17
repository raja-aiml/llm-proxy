# tests/unit/config_loader/test_missing_configs.py

import llm_wrapper.server.config_loader as cl

def test_load_all_configs_missing(isolate_config_dir):
    configs = cl.load_all_configs()
    assert configs == {}