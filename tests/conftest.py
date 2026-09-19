import importlib.util
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixtures(tmp_path_factory):
    root = Path(__file__).parents[1]
    spec = importlib.util.spec_from_file_location(
        "generator", root / "scripts/generate_test_workbooks.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    destination = tmp_path_factory.mktemp("fixtures")
    module.generate(destination)
    return destination


@pytest.fixture(autouse=True)
def block_external_network(monkeypatch):
    import ipaddress
    import socket

    original = socket.socket.connect

    def guarded(sock, address):
        if isinstance(address, tuple):
            try:
                allowed = ipaddress.ip_address(address[0]).is_loopback
            except ValueError:
                allowed = False
            if not allowed:
                raise AssertionError("Tests may not contact external network services")
        return original(sock, address)

    monkeypatch.setattr(socket.socket, "connect", guarded)
