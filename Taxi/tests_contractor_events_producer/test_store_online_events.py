import datetime as dt
from typing import List

import pytest

from tests_contractor_events_producer import db_tools
from tests_contractor_events_producer import online_events
from tests_contractor_events_producer import status_events


@pytest.mark.config(
    CONTRACTOR_EVENTS_PRODUCER_EVENTS_CONSUMER_SETTINGS={
        'max_pipeline_size': 1000,
        'processing_retry_deadline_sec': 300,
        'processing_retry_interval_ms': 500,
        'processing_upload_online_events_chunk_size': 2,
    },
)
@pytest.mark.now('2021-11-14T23:59:59.0+00:00')
async def test_store_new_events(
        taxi_contractor_events_producer, pgsql, testpoint,
):
    logbroker_testpoint = status_events.make_logbroker_testpoint(testpoint)

    await status_events.post_event(
        taxi_contractor_events_producer,
        [
            status_events.make_raw_event(
                'dbid1',
                'uuid1',
                status_events.OFFLINE_STATUS,
                '2020-11-14T23:59:59+00:00',
            ),
            status_events.make_raw_event(
                'dbid1',
                'uuid1',
                status_events.BUSY_STATUS,
                '2020-11-15T23:59:59+00:00',
            ),
            status_events.make_raw_event(
                'dbid1',
                'uuid2',
                status_events.OFFLINE_STATUS,
                '2020-11-16T23:59:59+00:00',
            ),
            status_events.make_raw_event(
                'dbid2',
                'uuid3',
                status_events.ONLINE_STATUS,
                '2020-11-16T23:59:59+00:00',
            ),
        ],
    )

    await logbroker_testpoint.wait_call()

    expected_online_events = [
        online_events.OnlineDbEvent(
            'dbid1',
            'uuid1',
            online_events.OFFLINE_STATUS,
            dt.datetime.fromisoformat('2020-11-15T23:59:59+00:00'),
        ),
        online_events.OnlineDbEvent(
            'dbid1',
            'uuid2',
            online_events.OFFLINE_STATUS,
            dt.datetime.fromisoformat('2020-11-16T23:59:59+00:00'),
        ),
        online_events.OnlineDbEvent(
            'dbid2',
            'uuid3',
            online_events.ONLINE_STATUS,
            dt.datetime.fromisoformat('2020-11-16T23:59:59+00:00'),
        ),
    ]

    assert db_tools.get_online_events(pgsql) == expected_online_events


@pytest.mark.pgsql(
    'contractor_events_producer',
    queries=[
        db_tools.insert_online_events(
            [
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'raw_status_events, expected_online_events',
    (
        pytest.param(
            [
                status_events.make_raw_event(
                    'dbid1',
                    'uuid1',
                    status_events.OFFLINE_STATUS,
                    '2020-11-15T23:59:59+00:00',
                ),
            ],
            [
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    online_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
            ],
            id='not update same status',
        ),
        pytest.param(
            [
                status_events.make_raw_event(
                    'dbid1',
                    'uuid1',
                    status_events.ONLINE_STATUS,
                    '2020-11-13T23:59:59+00:00',
                ),
            ],
            [
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    status_events.OFFLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
            ],
            id='not update new status from past',
        ),
        pytest.param(
            [
                status_events.make_raw_event(
                    'dbid1',
                    'uuid1',
                    status_events.ONLINE_STATUS,
                    '2020-11-15T23:59:59+00:00',
                ),
            ],
            [
                online_events.OnlineDbEvent(
                    'dbid1',
                    'uuid1',
                    status_events.ONLINE_STATUS,
                    dt.datetime.fromisoformat('2020-11-15T23:59:59+00:00'),
                ),
            ],
            id='update new status',
        ),
    ),
)
@pytest.mark.now('2021-11-14T23:59:59+00:00')
async def test_update_existings_events(
        taxi_contractor_events_producer,
        pgsql,
        testpoint,
        raw_status_events: List[str],
        expected_online_events: List[online_events.OnlineDbEvent],
):
    logbroker_testpoint = status_events.make_logbroker_testpoint(testpoint)

    await status_events.post_event(
        taxi_contractor_events_producer, raw_status_events,
    )

    await logbroker_testpoint.wait_call()

    assert db_tools.get_online_events(pgsql) == expected_online_events
