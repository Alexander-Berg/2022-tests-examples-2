import json

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_uber_gw_plugins import *  # noqa: F403 F401


@pytest.fixture
def push_message(taxi_grocery_uber_gw):
    async def impl(message):
        response = await taxi_grocery_uber_gw.post(
            'tests/grocery-event-bus', data=json.dumps(message),
        )
        assert response.status_code == 200

    return impl


@pytest.fixture(name='push_event')
def _push_event(push_message):  # pylint: disable=W0621
    async def _push_event(event, consumer, topic=None):
        assert consumer, 'Consumer should be non empty'
        message = {
            'consumer': consumer,
            'topic': topic if topic else consumer,
            'cookie': f'cookie_1',
        }
        message['data'] = event.json()
        await push_message(message)

    return _push_event
