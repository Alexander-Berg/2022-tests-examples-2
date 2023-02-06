# pylint: disable=import-only-modules
import datetime
import json

import pytest

from tests_reposition_watcher.utils import select_named


EVENTS_FLUSHER_TASK_NAME = 'oec-flusher'
EVENTS_PROCESSOR_TASK_NAME = 'oec-processor'


@pytest.mark.now('2020-05-28T12:00:00+0000')
@pytest.mark.pgsql('reposition_watcher', files=['order_events.sql'])
async def test_message(
        taxi_reposition_watcher, taxi_config, pgsql, testpoint, mockserver,
):
    _events = []

    @mockserver.json_handler('/reposition-api/v1/service/session/add_events')
    def _mock_add_event(request):
        events = json.loads(request.get_data())['events']

        for event in events:
            _events.append(event)

        return {'results': [{'has_failed': False} for _ in events]}

    _cookie = 0

    @testpoint('logbroker_commit')
    def commit(cookie):
        nonlocal _cookie

        _cookie += 1
        assert _cookie == int(cookie)

    @testpoint('order-events-processor::end')
    def on_processor_end(data):
        pass

    def _fetch_checks():
        return select_named(
            """SELECT state_id, order_in_progress
               FROM state.transporting_arrival
               ORDER BY state_id ASC""",
            pgsql['reposition_watcher'],
        )

    def _fetch_events():
        return select_named(
            """
            SELECT
                session_id,
                event,
                ta_event
            FROM
                state.order_events
            ORDER BY
                id ASC
            """,
            pgsql['reposition_watcher'],
        )

    def _fetch_waiting_sessions():
        return select_named(
            """SELECT session_id, dbid_uuid
               FROM state.waiting_sessions
               ORDER BY session_id ASC""",
            pgsql['reposition_watcher'],
        )

    taxi_config.set_values(
        {
            'REPOSITION_WATCHER_ORDER_EVENTS_CONSUMER_CONFIG': {
                'order_offer_rejected_event': 'handle_offer_reject',
                'order_cancelled_by_user_event': 'handle_cancel_by_user',
                'order_cancelled_by_park_event': 'handle_cancel_by_park',
                'order_started_event': 'handle_assigning',
                'order_in_progress_event': 'handle_transporting',
                'order_completed_event': 'handle_complete',
                'order_finished_event': 'handle_post_finish',
            },
        },
    )

    now = datetime.datetime(
        2020, 5, 28, 12, 0, 0, tzinfo=datetime.timezone.utc,
    )

    assert _fetch_events() == []
    assert _fetch_waiting_sessions() == [
        {'session_id': 1512, 'dbid_uuid': '(dbid888,777)'},
    ]
    assert _fetch_checks() == [
        {'state_id': 101, 'order_in_progress': False},
        {'state_id': 102, 'order_in_progress': False},
    ]

    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_assigning',
                        'db_id': 'dbid777',
                        'driver_id': 'clid_999',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
    await taxi_reposition_watcher.run_periodic_task(EVENTS_FLUSHER_TASK_NAME)
    await taxi_reposition_watcher.run_periodic_task(EVENTS_PROCESSOR_TASK_NAME)

    assert _fetch_events() == [
        {'session_id': 1511, 'event': 'STARTED', 'ta_event': None},
    ]

    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_transporting',
                        'db_id': 'dbid777',
                        'driver_id': 'clid_999',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
    await taxi_reposition_watcher.run_periodic_task(EVENTS_FLUSHER_TASK_NAME)
    await taxi_reposition_watcher.run_periodic_task(EVENTS_PROCESSOR_TASK_NAME)

    assert _fetch_events() == [
        {'session_id': 1511, 'event': 'STARTED', 'ta_event': None},
        {'session_id': 1511, 'event': 'IN_PROGRESS', 'ta_event': 'BEGIN'},
    ]

    # this is one in dry run, so 'begin' event skipped
    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_transporting',
                        'db_id': 'dbid666',
                        'driver_id': 'clid_888',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
    await taxi_reposition_watcher.run_periodic_task(EVENTS_FLUSHER_TASK_NAME)
    await taxi_reposition_watcher.run_periodic_task(EVENTS_PROCESSOR_TASK_NAME)

    assert _fetch_events() == [
        {'session_id': 1511, 'event': 'STARTED', 'ta_event': None},
        {'session_id': 1511, 'event': 'IN_PROGRESS', 'ta_event': 'BEGIN'},
        {'session_id': 1513, 'event': 'IN_PROGRESS', 'ta_event': None},
    ]

    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_cancel_by_park',
                        'db_id': 'dbid888',
                        'driver_id': 'clid_777',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
    await taxi_reposition_watcher.run_periodic_task(EVENTS_FLUSHER_TASK_NAME)
    await taxi_reposition_watcher.run_periodic_task(EVENTS_PROCESSOR_TASK_NAME)

    assert _fetch_events() == [
        {'session_id': 1511, 'event': 'STARTED', 'ta_event': None},
        {'session_id': 1511, 'event': 'IN_PROGRESS', 'ta_event': 'BEGIN'},
        {'session_id': 1513, 'event': 'IN_PROGRESS', 'ta_event': None},
        {'session_id': 1512, 'event': 'CANCELLED_BY_PARK', 'ta_event': None},
    ]

    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_post_finish',
                        'db_id': 'dbid888',
                        'driver_id': 'clid_777',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()

    # same event to ensure it's not saved twice
    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_post_finish',
                        'db_id': 'dbid888',
                        'driver_id': 'clid_777',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
    await taxi_reposition_watcher.run_periodic_task(EVENTS_FLUSHER_TASK_NAME)
    await taxi_reposition_watcher.run_periodic_task(EVENTS_PROCESSOR_TASK_NAME)

    assert _fetch_events() == [
        {'session_id': 1511, 'event': 'STARTED', 'ta_event': None},
        {'session_id': 1511, 'event': 'IN_PROGRESS', 'ta_event': 'BEGIN'},
        {'session_id': 1513, 'event': 'IN_PROGRESS', 'ta_event': None},
        {'session_id': 1512, 'event': 'CANCELLED_BY_PARK', 'ta_event': None},
        {'session_id': 1512, 'event': 'FINISHED', 'ta_event': 'END'},
    ]

    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_offer_reject',
                        'db_id': 'dbid111',
                        'driver_id': 'clid_333',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
    await taxi_reposition_watcher.run_periodic_task(EVENTS_FLUSHER_TASK_NAME)
    await taxi_reposition_watcher.run_periodic_task(EVENTS_PROCESSOR_TASK_NAME)

    assert _fetch_events() == [
        {'session_id': 1511, 'event': 'STARTED', 'ta_event': None},
        {'session_id': 1511, 'event': 'IN_PROGRESS', 'ta_event': 'BEGIN'},
        {'session_id': 1513, 'event': 'IN_PROGRESS', 'ta_event': None},
        {'session_id': 1512, 'event': 'CANCELLED_BY_PARK', 'ta_event': None},
        {'session_id': 1512, 'event': 'FINISHED', 'ta_event': 'END'},
        {'session_id': 1514, 'event': 'OFFER_REJECTED', 'ta_event': None},
    ]

    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_cancel_by_user',
                        'db_id': 'dbid111',
                        'driver_id': 'clid_333',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()

    # same as previous, as periodic tasks are not executed
    assert _fetch_events() == [
        {'session_id': 1511, 'event': 'STARTED', 'ta_event': None},
        {'session_id': 1511, 'event': 'IN_PROGRESS', 'ta_event': 'BEGIN'},
        {'session_id': 1513, 'event': 'IN_PROGRESS', 'ta_event': None},
        {'session_id': 1512, 'event': 'CANCELLED_BY_PARK', 'ta_event': None},
        {'session_id': 1512, 'event': 'FINISHED', 'ta_event': 'END'},
        {'session_id': 1514, 'event': 'OFFER_REJECTED', 'ta_event': None},
    ]

    response = await taxi_reposition_watcher.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-watcher',
                'data': json.dumps(
                    {
                        'event_key': 'handle_complete',
                        'db_id': 'dbid111',
                        'driver_id': 'clid_333',
                        'updated': now.timestamp(),
                    },
                ),
                'topic': 'order-events',
                'cookie': str(_cookie + 1),
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
    await taxi_reposition_watcher.run_periodic_task(EVENTS_FLUSHER_TASK_NAME)
    await taxi_reposition_watcher.run_periodic_task(EVENTS_PROCESSOR_TASK_NAME)

    # + 2 events, as periodic tasks are executed
    assert _fetch_events() == [
        {'session_id': 1511, 'event': 'STARTED', 'ta_event': None},
        {'session_id': 1511, 'event': 'IN_PROGRESS', 'ta_event': 'BEGIN'},
        {'session_id': 1513, 'event': 'IN_PROGRESS', 'ta_event': None},
        {'session_id': 1512, 'event': 'CANCELLED_BY_PARK', 'ta_event': None},
        {'session_id': 1512, 'event': 'FINISHED', 'ta_event': 'END'},
        {'session_id': 1514, 'event': 'OFFER_REJECTED', 'ta_event': None},
        {'session_id': 1514, 'event': 'CANCELLED_BY_USER', 'ta_event': None},
        {'session_id': 1514, 'event': 'COMPLETED', 'ta_event': None},
    ]

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': 'order-events-processor'},
    )
    assert response.status_code == 200

    await on_processor_end.wait_call()

    assert _mock_add_event.times_called == 1
    assert _events == [
        {
            'session_id': 1511,
            'type': 'order_started',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1511,
            'type': 'order_in_progress',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1511,
            'type': 'transporting_arrival_begin',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1512,
            'type': 'order_cancelled_by_park',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1512,
            'type': 'order_finished',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1512,
            'type': 'transporting_arrival_end',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1513,
            'type': 'order_in_progress',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1514,
            'type': 'order_offer_rejected',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1514,
            'type': 'order_cancelled_by_user',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
        {
            'session_id': 1514,
            'type': 'order_completed',
            'occurred_at': '2020-05-28T12:00:00+00:00',
        },
    ]

    assert _fetch_events() == []
    assert _fetch_waiting_sessions() == [
        {'session_id': 1511, 'dbid_uuid': '(dbid777,999)'},
    ]
    assert _fetch_checks() == [
        {'state_id': 101, 'order_in_progress': True},
        {'state_id': 102, 'order_in_progress': False},
    ]


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.pgsql('reposition_watcher', files=['stale_order_events.sql'])
async def test_stale_events_cleaner(
        taxi_reposition_watcher, pgsql, testpoint, mockserver,
):
    @testpoint('stale-events-cleaner::end')
    def on_cleaner_end(data):
        pass

    def _fetch_order_events():
        return select_named(
            """SELECT session_id
               FROM state.order_events""",
            pgsql['reposition_watcher'],
        )

    assert _fetch_order_events() == [
        {'session_id': 1511},
        {'session_id': 1513},
    ]

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': 'stale-events-cleaner'},
    )
    assert response.status_code == 200

    await on_cleaner_end.wait_call()

    assert _fetch_order_events() == [{'session_id': 1513}]


@pytest.mark.now('2020-05-28T12:00:00+0000')
@pytest.mark.pgsql('reposition_watcher', files=['waiting_sessions.sql'])
async def test_waiting_sessions_cleaner(
        taxi_reposition_watcher, pgsql, testpoint, mockserver,
):
    @testpoint('waiting-sessions-cleaner::end')
    def on_cleaner_end(data):
        pass

    def _fetch_waiting_sessions():
        return select_named(
            """SELECT session_id, dbid_uuid
               FROM state.waiting_sessions""",
            pgsql['reposition_watcher'],
        )

    assert _fetch_waiting_sessions() == [
        {'session_id': 1, 'dbid_uuid': '(dbid777,999)'},
        {'session_id': 2, 'dbid_uuid': '(dbid888,777)'},
    ]

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': 'waiting-sessions-cleaner'},
    )
    assert response.status_code == 200

    await on_cleaner_end.wait_call()

    assert _fetch_waiting_sessions() == [
        {'session_id': 2, 'dbid_uuid': '(dbid888,777)'},
    ]
