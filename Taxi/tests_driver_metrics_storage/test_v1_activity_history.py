import copy

import pytest


def get_udid(num):
    num_str = str(num)
    return '0' * (24 - len(num_str)) + num_str


def get_dbid_udid(num):
    return get_udid(num) + '_' + get_udid(num)


CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
DRIVER_ID0 = '32gdh3_dad8lucn58003nnbc3'
UDID0 = get_udid(1)
DBID_UUID0 = get_dbid_udid(101)
DB_ID0 = get_udid(30303)


EXPECTED_RESULT = [
    {
        'activity_value_change': 7,
        'db_id': DB_ID0,
        'dispatch_traits': {'distance': 'long'},
        'distance_to_a': 5.0,
        'driver_id': DRIVER_ID0,
        'event_descriptor': {
            'tags': ['yam-yam', 'tas_teful'],
            'type': 'user_test',
        },
        'event_type': 'order',
        'id': '2',
        'order_alias_id': '',
        'order_id': 'order_id_2',
        'time_to_a': 120.0,
        'timestamp': '2019-01-01T00:00:02+00:00',
        'zone': 'moscow',
    },
    {
        'activity_value_change': 6,
        'event_descriptor': {
            'tags': ['yam-yam', 'tas_teful'],
            'type': 'user_test',
        },
        'event_type': 'order',
        'id': '1',
        'order_alias_id': '',
        'order_id': 'order_id_1',
        'timestamp': '2019-01-01T00:00:01+00:00',
        'zone': 'moscow',
    },
]

EXPECTED_RESULT_APPENDIX = [
    {
        'activity_value_change': -8,
        'event_descriptor': {'type': 'set_activity_value'},
        'event_type': 'dm_service_manual',
        'id': '3',
        'order_alias_id': '',
        'order_id': '',
        'timestamp': '2019-01-01T00:00:00+00:00',
        'zone': '',
    },
]


@pytest.mark.config(DRIVER_METRICS_STORAGE_REQUEST_LIMITS={'__default__': 1})
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_v1_activity_history_limit_above_max(
        taxi_driver_metrics_storage,
):
    # XXX: it is also checks no exception thrown on request with limit gt max
    response = await taxi_driver_metrics_storage.post(
        'v1/activity/history', json={'udid': UDID0, 'limit': 10},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [EXPECTED_RESULT[0]]}


@pytest.mark.config(DRIVER_METRICS_STORAGE_REQUEST_LIMITS={'__default__': 1})
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_v1_activity_history_response_400(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v1/activity/history',
        json={
            'udid': UDID0,
            'timestamp_from': '2019-01-01T00:00:01+00:00',
            'timestamp_to': '2019-01-01T00:00:00+00:00',
            'limit': 10,
        },
    )
    assert response.status_code == 400


@pytest.mark.config(DRIVER_METRICS_STORAGE_REQUEST_LIMITS={'__default__': 10})
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.parametrize(
    'history_settings, event_types',
    [
        pytest.param({}, ['order'], id='Empty settings'),
        pytest.param(
            {'order': {'filter_out': []}},
            ['dm_service_manual'],
            id='Wrong event_types',
        ),
    ],
)
async def test_v1_activity_history_bad_event_type(
        taxi_driver_metrics_storage,
        history_settings,
        event_types,
        taxi_config,
):
    taxi_config.set_values(
        {'DRIVER_METRICS_STORAGE_HISTORY_SETTINGS': history_settings},
    )
    response = await taxi_driver_metrics_storage.post(
        'v1/activity/history',
        json={
            'udid': UDID0,
            'timestamp_from': '2019-01-01T00:00:01+00:00',
            'timestamp_to': '2019-01-05T00:00:00+00:00',
            'event_types': event_types,
            'limit': 10,
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_HISTORY_SETTINGS={
        'order': {'filter_out': []},
        'dm_service_manual': {'filter_out': []},
    },
)
@pytest.mark.parametrize(
    'request_json, expected_result',
    [
        ({'udid': UDID0}, EXPECTED_RESULT),
        ({'udid': UDID0, 'dbid_uuid': DBID_UUID0}, EXPECTED_RESULT),
        ({'driver_id': DRIVER_ID0}, None),
        ({'udid': UDID0, 'driver_id': DRIVER_ID0}, EXPECTED_RESULT),
        (
            {'udid': UDID0, 'driver_id': DRIVER_ID0, 'event_types': ['order']},
            EXPECTED_RESULT,
        ),
        (
            {'udid': UDID0, 'event_types': ['order', 'dm_service_manual']},
            EXPECTED_RESULT + EXPECTED_RESULT_APPENDIX,
        ),
    ],
)
@pytest.mark.parametrize(
    'hard_limit, request_limit',
    # We can't use hard_limit less or equal to count of events in
    # result of select due to it will raise exception
    [
        pytest.param(None, None, id='No limits'),
        pytest.param(None, 1, id='Limited(2) by request'),
        pytest.param(2, 1, id='Both limits, but min 1'),
        pytest.param(3, 2, id='Both limits, but min 2'),
        pytest.param(3, None, id='Limited(3) by config'),
    ],
)
@pytest.mark.parametrize(
    'from_replica',
    (
        pytest.param(True, id='from_replica'),
        pytest.param(False, id='from_master'),
    ),
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_dms_activity_history(
        mockserver,
        taxi_driver_metrics_storage,
        request_json,
        expected_result,
        taxi_config,
        mocked_time,
        hard_limit,
        request_limit,
        from_replica,
):
    # XXX: request_json should be copied because a scope of case of
    # `parametrize` uses the same object of higher scope level.
    # NOTE: `request` name is reserved for pytest module
    request_json = copy.deepcopy(request_json)

    history_limit = {'__default__': 100}
    if hard_limit:
        history_limit['activity/history'] = hard_limit
    taxi_config.set_values(
        {
            'DRIVER_METRICS_STORAGE_REQUEST_LIMITS': history_limit,
            'DRIVER_METRICS_STORAGE_EVENTS_PROCESSED_FROM_REPLICA': (
                from_replica
            ),
        },
    )

    if request_limit:
        request_json['limit'] = request_limit

    response = await taxi_driver_metrics_storage.post(
        '/v1/activity/history', json=request_json,
    )

    if expected_result:
        assert response.status == 200
        items = response.json()
        # Left, right and both cases in 4 lines
        if hard_limit or request_limit:
            expected_result = expected_result[
                : min(request_limit or hard_limit, hard_limit or request_limit)
            ]
        assert expected_result == items['items']
    else:
        assert response.status == 400
