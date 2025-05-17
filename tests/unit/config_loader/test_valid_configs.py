# tests/unit/config_loader/test_valid_configs.py

import yaml
import llm_wrapper.server.config_loader as cl

def test_load_all_configs_with_valid_yaml(config_path):
    file_path = config_path / "foo.yaml"
    file_path.write_text(yaml.safe_dump({
        "model": {"path": "p"},
        "api": {"url": "u"}
    }))
    configs = cl.load_all_configs()
    assert "foo" in configs
    assert configs["foo"]["model"]["path"] == "p"
    assert configs["foo"]["api"]["url"] == "u"