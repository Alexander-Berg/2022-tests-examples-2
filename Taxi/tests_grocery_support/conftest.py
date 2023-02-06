# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json
from typing import Dict
from typing import Iterable

import pytest

from grocery_support_plugins import *  # noqa: F403 F401


@pytest.fixture
def push_message(taxi_grocery_support):
    async def impl(message):
        response = await taxi_grocery_support.post(
            'tests/grocery-event-bus', data=json.dumps(message),
        )
        assert response.status_code == 200

    return impl


@pytest.fixture
def push_message_bulk(
        taxi_grocery_support, push_message,  # pylint: disable=W0621
):
    async def impl(msg_bulk: Iterable[Dict]):
        for msg in msg_bulk:
            await push_message(msg)

    return impl


@pytest.fixture(name='push_event_bulk')
def _push_event_bulk(push_message_bulk):  # pylint: disable=W0621
    async def _push_events(event_list: Iterable, consumer, topic=None):
        assert consumer, 'Consumer should be non empty'
        messages = []
        for idx, event in enumerate(event_list):
            messages.append(
                {
                    'consumer': consumer,
                    'data': event.json(),
                    'topic': topic if topic else consumer,
                    'cookie': f'cookie_{idx}',
                },
            )
        if messages:
            await push_message_bulk(messages)

    return _push_events
