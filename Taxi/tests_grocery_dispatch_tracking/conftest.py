# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import asyncio
import base64
from collections import abc
import json
from typing import Dict
from typing import Iterable
from typing import List
from typing import Sequence
from typing import Union

from google.protobuf import message as pb_message
import pytest

from grocery_dispatch_tracking_plugins import *  # noqa: F403 F401

from tests_grocery_dispatch_tracking import events


@pytest.fixture(autouse=True)
async def database(pgsql):
    pass


@pytest.fixture
def push_message(taxi_grocery_dispatch_tracking):
    async def impl(message):
        response = await taxi_grocery_dispatch_tracking.post(
            'tests/grocery-event-bus', data=json.dumps(message),
        )
        assert response.status_code == 200

    return impl


@pytest.fixture
def push_message_bulk(
        taxi_grocery_dispatch_tracking, push_message,  # pylint: disable=W0621
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
        if isinstance(event, pb_message.Message):
            message['data_b64'] = base64.b64encode(
                event.SerializeToString(),
            ).decode()
        else:
            message['data'] = event.json()
        await push_message(message)

    return _push_event


@pytest.fixture(name='insert_depot_state')
def _insert_depot_state(pgsql):
    def _insert_depot_state(*, depot_id, orders, performers, updated):
        cursor = pgsql['grocery_dispatch_tracking'].cursor()
        cursor.execute(
            'INSERT INTO dispatch_tracking.depot_state(depot_id, orders, performers, updated)'  # noqa: E501
            'VALUES (%s, %s, %s, %s)',
            (
                depot_id,
                json.dumps(orders),
                json.dumps(performers),
                str(updated),
            ),
        )

    return _insert_depot_state


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
        taxi_grocery_dispatch_tracking, testpoint, push_event, push_event_bulk,
):
    async def _process_event(
            event: Union[events.BaseEvent, Sequence[events.BaseEvent]],
    ):
        if isinstance(event, abc.Iterable):
            assert event, 'Should be passed at least one event'
            consumer = event[0].consumer
            assert all(
                item.consumer == consumer for item in event
            ), 'All events must have same consumer'
        else:
            consumer = event.consumer

        @testpoint(f'{consumer}-stats')
        def event_stats(data):
            pass

        if isinstance(event, abc.Iterable):
            await push_event_bulk(event, consumer)
        else:
            await push_event(event, consumer)

        await taxi_grocery_dispatch_tracking.run_task(
            f'{consumer}-consumer-task',
        )
        return (await event_stats.wait_call())['data']

    return _process_event


@pytest.fixture(name='process_events')
async def _process_events(process_event):
    async def _process_events(*events_: events.BaseEvent) -> List[Dict]:
        return [await process_event(event) for event in events_]

    return _process_events


@pytest.fixture(name='check_event_stats')
def check_event_stats_fixture(process_event):
    async def _check_event_stats(
            event, expected_stats, prev_stats=None, is_full=False,
    ):
        """Check statistics after event.

        """
        if not isinstance(expected_stats, list):
            expected_stats = [expected_stats]

        stats = (await process_event(event))['stats']

        for idx, cur_stat in enumerate(stats):
            if is_full:
                assert expected_stats[idx].keys() == cur_stat.keys()

            if prev_stats is None:
                assert expected_stats[idx].items() <= cur_stat.items(), (
                    'Dictionary of expected values are not contained in the '
                    'next statistics.'
                )
            else:
                assert cur_stat.keys() == prev_stats.keys(), (
                    'The keys of the next statistics must match the keys '
                    'of the previous one.'
                )
                assert (
                    cur_stat.items() - prev_stats.items()
                    == expected_stats[idx].items()
                ), 'New values from current statistics differ from expected'
                prev_stats = cur_stat

        # return last stats
        return stats[-1]

    return _check_event_stats


@pytest.fixture(name='stats_context')
async def stats_context_fixture(check_event_stats):
    class StatsContext:
        def __init__(self, initial_stats=None):
            self.last_stats = initial_stats

        async def check(
                self, event, expected_stats, *, check_prev=True, is_full=False,
        ):
            self.last_stats = await check_event_stats(
                event,
                expected_stats,
                prev_stats=self.last_stats if check_prev else None,
                is_full=is_full,
            )

    def _create_stats_context(initial_stats=None):
        return StatsContext(initial_stats)

    return _create_stats_context
