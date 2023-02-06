import socket

import pytest


@pytest.fixture(scope='session')
def _host():
    host = socket.gethostbyaddr(socket.gethostname())[0]
    return host


@pytest.fixture(autouse=True)
def mock_conductor(mockserver, _host: str):
    @mockserver.json_handler('/conductor/api/hosts/' + _host)
    def mock_conductor_hosts(request):
        return [{'fqdn': 'test.fqdn', 'root_datacenter_name': 'test'}]
