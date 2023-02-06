import datetime

import psycopg2
import pytest


EVENTS_IN_LB = [
    {
        'park_id': 'p1',
        'device_id': 'device_id_test2',
        'event_id': '54b3d7ec-30f6-xxx6-94a8-afs6e8fe404c',
        'event_type': 'sleep',
        'event_at': '2027-02-27T23:55:00+00:00',
        'gnss': {'lat': 54.99550072, 'lon': 72.94622044},
    },
    {
        'park_id': 'p1',
        'device_id': 'device_id_test2',
        'event_id': '74b3d7ec-30f6-xxx6-94a8-afs6e8fe404c',
        'event_type': 'sleep',
        'event_at': '2020-02-27T23:55:00+00:00',
        'gnss': {'lat': 54.99550072, 'lon': 72.94622044},
    },
    {
        'park_id': 'p1',
        'device_id': 'device_id_test2',
        'event_id': 'fasxxx6c-30f6-43cf-94a8-911bc8fe404c',
        'event_type': 'sleep',
        'event_at': '2020-02-27T13:00:00+00:00',
        'gnss': {'lat': 54.99250000, 'lon': 73.36861111},
    },
]

WHITELIST = [
    {
        'event_type': 'sleep',
        'is_critical': True,
        'is_violation': False,
        'fixation_config_path': 'some_path',
    },
    {
        'event_type': 'distraction',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'some_path',
    },
    {
        'event_type': 'driver_lost',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'some_path',
    },
]


@pytest.mark.pgsql(
    'signal_device_api_meta_db', ['signal_device_api_meta_db.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_LB_EVENTS_PRODUCER_SETTINGS={
        'polling_delay_ms': 1000,
        'events_chunk_size': 30,
        'update_cursor_attempts': 3,
        'update_cursor_retry_ms': 100,
        'enabled': True,
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST,
)
async def test_events_producer(
        pgsql, mockserver, testpoint, taxi_signal_device_api,
):
    @testpoint('lb-events-producer-testpoint')
    def lb_events_producer_testpoint(arg):
        pass

    @testpoint('logbroker_publish')
    def logbroker_commit(data):
        pass

    async with taxi_signal_device_api.spawn_task('workers/lb-events-producer'):
        await lb_events_producer_testpoint.wait_call()

    assert logbroker_commit.times_called == 3

    for event in EVENTS_IN_LB:
        message = logbroker_commit.next_call()['data']
        assert message['name'] == 'lb-events-producer'
        assert message['data'] == event['event_id']

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('SELECT * FROM signal_device_api.lb_events_producer')

    expected_dt = datetime.datetime(
        2020,
        2,
        26,
        3,
        14,
        59,
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
    )
    assert list(db)[0] == (expected_dt, 'fasxxx6c-30f6-43cf-94a8-911bc8fe404c')
