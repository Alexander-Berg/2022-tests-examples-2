# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import pytest

from bank_access_control_plugins import *  # noqa: F403 F401
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401


@pytest.fixture(autouse=True)
def jwks_content():
    class Data:
        def __init__(self):
            self.data = []

        def set_data(self, data):
            self.data = data

    return Data()


@pytest.fixture(autouse=True)
def jwks_mock(mockserver, jwks_content):
    class Mock:
        @mockserver.json_handler('core-auth/v1/jwt/.well-known/jwks.json')
        @staticmethod
        async def _handler(request):
            return jwks_content.data

    return Mock()
