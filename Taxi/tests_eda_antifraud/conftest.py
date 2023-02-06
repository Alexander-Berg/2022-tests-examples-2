# pylint: disable=wildcard-import, unused-wildcard-import, import-error,
# pylint: disable=unused-variable
import pytest

from eda_antifraud_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def signature_service(mockserver):
    @mockserver.json_handler('/antifraud/v1/events/eda/signature')
    def signature_handler(request):
        assert request.json == {
            'couriers': [{'uid': 'courier-id', 'signature': 'signature'}],
        }
        return {}
