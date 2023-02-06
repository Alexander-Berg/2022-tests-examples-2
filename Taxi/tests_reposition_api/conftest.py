import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from reposition_api_plugins import *  # noqa: F403 F401


USER_AGENT = 'Taxi-Reposition'

# this variable is used in generated ticket in case of TVM testing
DRIVER_PROTOCOL_TVM_ID = 1234


@pytest.fixture(autouse=True)
def mock_client_notify(mockserver):
    @mockserver.json_handler('/client-notify/v2/bulk-push')
    async def _mock_cn(request):
        recipients = request.json['recipients']

        return {
            'notifications': [
                {'notification_id': 'whatever'} for _ in recipients
            ],
        }
