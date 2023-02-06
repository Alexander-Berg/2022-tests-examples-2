# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from client_notify_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(autouse=True, name='mock_xiva')
def _mock_xiva(mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe(request):
        return mockserver.make_response('{}', 200)
