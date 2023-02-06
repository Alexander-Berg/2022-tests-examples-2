import datetime as dt
import json
from typing import List

import pytest

from tests_contractor_events_producer import db_tools
from tests_contractor_events_producer import online_events


def to_online_db_events(raw_event: str):
    event_json = json.loads(raw_event)
    return online_events.OnlineDbEvent(
        event_json['park_id'],
        event_json['driver_id'],
        event_json['status'],
        dt.datetime.fromisoformat(event_json['updated_at']),
    )


@pytest.mark.pgsql(
    'contractor_events_producer',
    queries=[
        db_tools.insert_online_status_history(
            [
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-16T22:59:59+03:00'),
                ),
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-13T22:59:59+03:00'),
                ),
                online_events.OnlineDbEvent(
                    'dbid2',
                    'uuid2',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-15T22:59:59+03:00'),
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'expect_left_events_count, expect_online_events_to_send',
    (
        pytest.param(
            0,
            [
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-16T22:59:59+03:00'),
                ),
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-13T22:59:59+03:00'),
                ),
                online_events.OnlineDbEvent(
                    'dbid2',
                    'uuid2',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-15T22:59:59+03:00'),
                ),
            ],
            id='send events with default limit',
        ),
        pytest.param(
            3,
            [
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
            ],
            marks=[
                pytest.mark.config(
                    CONTRACTOR_EVENTS_PRODUCER_ONLINE_EVENTS_RELAY={
                        'polling_delay_ms': 1000,
                        'events_chunk_size': 1,
                        'remove_from_db_attempts': 3,
                        'remove_from_db_retry_ms': 100,
                    },
                ),
            ],
            id='send events with limit 1',
        ),
    ),
)
async def test_read_clear_status_history(
        pgsql,
        mockserver,
        testpoint,
        taxi_contractor_events_producer,
        expect_left_events_count: int,
        expect_online_events_to_send: List[online_events.OnlineDbEvent],
):
    @testpoint('online-events-relay-testpoint')
    def online_events_relay_testpoint(arg):
        pass

    @testpoint('logbroker_publish')
    def logbroker_commit(data):
        pass

    async with taxi_contractor_events_producer.spawn_task(
            'workers/online-events-relay',
    ):
        await online_events_relay_testpoint.wait_call()

    assert logbroker_commit.times_called == len(expect_online_events_to_send)

    for expected_event in expect_online_events_to_send:
        message = logbroker_commit.next_call()['data']
        assert message['name'] == 'contractor-online-events'
        assert to_online_db_events(message['data']) == expected_event

    actual_left_events_count = len(db_tools.get_online_events_in_outbox(pgsql))

    assert actual_left_events_count == expect_left_events_count


async def test_not_send_already_sended(
        pgsql, mockserver, testpoint, taxi_contractor_events_producer,
):
    fill_outbox_query = db_tools.insert_online_status_history(
        [
            online_events.OnlineDbEvent(
                'dbid1',
                'uuid1',
                online_events.OFFLINE_STATUS,
                dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
            ),
            online_events.OnlineDbEvent(
                'dbid2',
                'uuid2',
                online_events.ONLINE_STATUS,
                dt.datetime.fromisoformat('2020-11-16T22:59:59+03:00'),
            ),
        ],
    )

    pgsql['contractor_events_producer'].cursor().execute(fill_outbox_query)

    inject_error = True

    @testpoint('online-events-relay::error-injector')
    def relay_error_testpoint(data):
        nonlocal inject_error
        return {'inject_failure': inject_error}

    @testpoint('online-events-relay-testpoint')
    def relay_testpoint(arg):
        pass

    @testpoint('logbroker_publish')
    def logbroker_commit(data):
        pass

    with pytest.raises(taxi_contractor_events_producer.TestsuiteTaskFailed):
        async with taxi_contractor_events_producer.spawn_task(
                'workers/online-events-relay',
        ):
            await relay_error_testpoint.wait_call()

    assert logbroker_commit.times_called == 2

    actual_left_events_count = len(db_tools.get_online_events_in_outbox(pgsql))
    # events not deleted in db because of injected error
    assert actual_left_events_count == 2

    inject_error = False

    async with taxi_contractor_events_producer.spawn_task(
            'workers/online-events-relay',
    ):
        await relay_testpoint.wait_call()

    # no new lb calls
    assert logbroker_commit.times_called == 2

    actual_left_events_count = len(db_tools.get_online_events_in_outbox(pgsql))

    assert actual_left_events_count == 0
