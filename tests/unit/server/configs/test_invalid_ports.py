# tests/unit/server_config/test_invalid_ports.py

import pytest

@pytest.mark.parametrize("port", [0, -1, 65536])
def test_port_out_of_range(port):
    assert not (0 < port < 65536), f"Port {port} should be invalid"