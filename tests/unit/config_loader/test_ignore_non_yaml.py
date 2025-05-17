# tests/unit/config_loader/test_ignore_non_yaml.py

import yaml
import llm_wrapper.server.config_loader as cl

def test_load_all_configs_ignores_non_yaml(config_path):
    (config_path / "ignore.txt").write_text("ignore me")
    (config_path / "good.yml").write_text(yaml.safe_dump({
        "model": {"path": "p"},
        "api": {"url": "u"}
    }))
    configs = cl.load_all_configs()
    assert "ignore" not in configs
    assert "good" in configs