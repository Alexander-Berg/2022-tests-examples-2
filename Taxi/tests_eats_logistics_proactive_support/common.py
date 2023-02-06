import datetime

import psycopg2

TEST_DELIVERY_ID = '000000'
TEST_DELIVERY_TYPE = 'eats'
TEST_SOURCE_LATITUDE = 0.0
TEST_SOURCE_LONGITUDE = 0.0
TEST_SOURCE_PROMISE = '2021-03-04T14:30:00+00:00'
TEST_DESTINATION_LATITUDE = 1.0
TEST_DESTINATION_LONGITUDE = 1.0
TEST_DESTINATION_PROMISE = '2021-03-04T15:30:00+00:00'

DEFAULT_DELIVERY = {
    'delivery_id': TEST_DELIVERY_ID,
    'delivery_type': TEST_DELIVERY_TYPE,
    'source': {
        'position': [TEST_SOURCE_LATITUDE, TEST_SOURCE_LONGITUDE],
        'promise': TEST_SOURCE_PROMISE,
    },
    'destination': {
        'position': [TEST_DESTINATION_LATITUDE, TEST_DESTINATION_LONGITUDE],
        'promise': TEST_DESTINATION_PROMISE,
    },
}

DEFAULT_EVENT = {
    'delivery_id': TEST_DELIVERY_ID,
    'event_type': 'assign',
    'meta_info': {
        'position': [TEST_DESTINATION_LATITUDE, TEST_DESTINATION_LONGITUDE],
        'promise': TEST_DESTINATION_PROMISE,
    },
}


def pg_dttm(date_time):
    pg_tz = psycopg2.tz.FixedOffsetTimezone(offset=180)
    date_time_timezone = datetime.datetime.fromisoformat(date_time)
    return date_time_timezone.replace(tzinfo=pg_tz)


RAW_DELIVERY = (
    TEST_DELIVERY_ID,
    TEST_DELIVERY_TYPE,
    TEST_SOURCE_LATITUDE,
    TEST_SOURCE_LONGITUDE,
    pg_dttm(TEST_SOURCE_PROMISE),
    TEST_DESTINATION_LATITUDE,
    TEST_DESTINATION_LONGITUDE,
    pg_dttm(TEST_DESTINATION_PROMISE),
)

DELIVERIES_DATA = [
    (
        '000002',
        'eats',
        0.0,
        0.0,
        datetime.datetime.fromisoformat('2021-03-04T14:45:00+00:00'),
        1.0,
        1.0,
        datetime.datetime.fromisoformat('2021-03-04T15:30:00+00:00'),
    ),
    (
        '000003',
        'eats',
        5.0,
        0.0,
        datetime.datetime.fromisoformat('2021-03-04T15:30:00+00:00'),
        1.0,
        1.0,
        datetime.datetime.fromisoformat('2021-03-04T16:30:00+00:00'),
    ),
    (
        '000004',
        'eats',
        0.0,
        10.0,
        datetime.datetime.fromisoformat('2021-03-04T18:00:00+00:00'),
        1.0,
        1.0,
        datetime.datetime.fromisoformat('2021-03-04T20:00:00+00:00'),
    ),
]

EVENTS_DATA = [
    (
        '000002',
        'assign',
        {'position': [3.0, 5.0], 'promise': '2021-03-04T14:50:00+00:00'},
    ),
    (
        '000002',
        'assign',
        {'position': [4.0, 5.5], 'promise': '2021-03-04T14:55:00+00:00'},
    ),
    (
        '000003',
        'assign',
        {'position': [4.0, 0.0], 'promise': '2021-03-04T15:35:00+00:00'},
    ),
]


def modify_delivery(update_data):
    default_copy = DEFAULT_DELIVERY.copy()
    default_copy.update(update_data)
    return default_copy


def modify_event(update_data):
    default_copy = DEFAULT_EVENT.copy()
    default_copy.update(update_data)
    return default_copy


def select_deliveries(pgsql):
    cursor = pgsql['eats_logistics_proactive_support'].cursor()
    cursor.execute(
        (
            f'SELECT *'
            f'FROM eats_logistics_proactive_support.tracked_deliveries'
        ),
    )
    return list(cursor)


def select_events(delivery_id, pgsql):
    cursor = pgsql['eats_logistics_proactive_support'].cursor()
    cursor.execute(
        (
            f'SELECT * '
            f'FROM eats_logistics_proactive_support.tracked_delivery_events '
            f'WHERE delivery_id = \'{delivery_id}\''
        ),
    )
    return list(cursor)
