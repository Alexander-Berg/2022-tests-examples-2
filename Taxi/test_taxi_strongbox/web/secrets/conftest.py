import logging
import socket

import pytest

from taxi_strongbox.components.sessions import conductor_session as cs


@pytest.fixture
def patch_get_host_name(patch_aiohttp_session, response_mock, patch):
    # Special hack for mac os
    # _socket.getaddrinfo on mac osx works incorrect
    @patch('taxi_strongbox.api.secrets_list._get_host_name')
    def _handler(request, log_extra) -> str:
        orig_ip_address = request.x_real_ip
        host_name = socket.getfqdn(orig_ip_address)
        return host_name


@pytest.fixture
def patch_conductor_session(patch_aiohttp_session, response_mock):
    def _patch_conductor_session(conductor_response):
        @patch_aiohttp_session(cs.ConductorSession.base_url, 'GET')
        def _request(method, url, *args, **kwargs):
            return response_mock(conductor_response)

    return _patch_conductor_session


@pytest.fixture
def patched_logs(monkeypatch):
    logs = []

    original_emit = logging.StreamHandler.emit

    def emit(self, record):
        if getattr(record, '_link', None):
            log_message = self.format(record)
            logs.append(log_message)
        return original_emit(self, record)

    monkeypatch.setattr('taxi.logs.log.StreamHandler.emit', emit)

    return logs
