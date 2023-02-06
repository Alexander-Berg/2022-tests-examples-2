# pylint: disable=wildcard-import, unused-wildcard-import, import-error, import-only-modules,
# pylint: disable=redefined-outer-name
# flake8: noqa IS001
import asyncio
import collections.abc
import json
from typing import Dict, Iterable, List, Sequence, Union

import pytest

from grocery_performer_watcher_plugins import *  # noqa: F403 F401

from tests_grocery_performer_watcher import constants as consts
from tests_grocery_performer_watcher import events


@pytest.fixture
def push_message(taxi_grocery_performer_watcher):
    async def impl(message):
        response = await taxi_grocery_performer_watcher.post(
            'tests/grocery-event-bus', data=json.dumps(message),
        )
        assert response.status_code == 200

    return impl


@pytest.fixture
def push_message_bulk(
        taxi_grocery_performer_watcher, push_message,  # pylint: disable=W0621
):
    async def impl(msg_bulk: Iterable[Dict]):
        for msg in msg_bulk:
            await push_message(msg)

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


@pytest.fixture(name='published_events')
async def _published_events(testpoint):
    """Wait and return events published to logbroker."""

    @testpoint('logbroker_publish')
    def publish_event(request):
        pass

    class Events:
        async def _wait_next(self):
            request = (await publish_event.wait_call())['request']
            return request['name'], json.loads(request['data'])

        async def _wait(self, alias=None):
            while True:
                event_alias, event = await self._wait_next()
                if alias is None or event_alias == alias:
                    return event_alias, event

        async def wait(self, alias=None, timeout=5):
            return await asyncio.wait_for(self._wait(alias), timeout)

        async def count(self, alias=None, timeout=5):
            return await asyncio.wait_for(self._wait(alias), timeout)

    return Events()


@pytest.fixture(name='process_event')
async def _process_event(
        taxi_grocery_performer_watcher, testpoint, push_event, push_event_bulk,
):
    async def _process_event(
            event: Union[events.BaseEvent, Sequence[events.BaseEvent]],
    ):
        if isinstance(event, collections.abc.Iterable):
            assert event, 'Should be passed at least one event'
            consumer = event[0].consumer
            assert all(
                item.consumer == consumer for item in event
            ), 'All events must have same consumer'
        else:
            consumer = event.consumer

        @testpoint('logbroker_commit')
        def event_commit(cookie):
            pass

        if isinstance(event, collections.abc.Iterable):
            await push_event_bulk(event, consumer)
        else:
            await push_event(event, consumer)

        await taxi_grocery_performer_watcher.run_task(
            f'{consumer}-consumer-task',
        )
        await event_commit.wait_call()

    return _process_event


@pytest.fixture(name='process_events')
async def _process_events(process_event):
    async def _process_events(*events_: events.BaseEvent) -> List[Dict]:
        return [await process_event(event) for event in events_]

    return _process_events


@pytest.fixture(autouse=True)
async def add_depot(grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=int(consts.DEPOT_ID),
        auto_add_zone=False,
        location=consts.DEPOT_LOCATION,
    )
