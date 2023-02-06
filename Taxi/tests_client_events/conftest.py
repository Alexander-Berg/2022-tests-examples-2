import json

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from client_events_plugins import *  # noqa: F403 F401


@pytest.fixture(name='client_notify', autouse=True)
def _client_notify(mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push(request):
        return mockserver.make_response(json.dumps({}), status=200)


@pytest.fixture(name='push_events', autouse=True)
def _push_events(taxi_client_events):
    async def _push(events):
        for event in events:
            response = await taxi_client_events.post('push', json=event)
            assert response.status_code == 200

    return _push
