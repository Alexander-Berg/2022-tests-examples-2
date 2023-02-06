import json

import pytest

HANDLER_PATH = 'v1/activity/history'
DRIVER_UDID = '5b7b0c694f007eaf8578b531'
TST_ZONE = 'burgund'
TST_ORDER_ID = 'dlsjfslkfj'


TEST_DMS_RESPONSE = [
    {
        'event': {
            'event_id': 'event_id_1',
            'type': 'order',
            'order_id': 'string',
            'order_alias': 'string',
            'park_driver_profile_id': 'string',
            'tariff_zone': 'string',
            'extra': {'value': 500},
            'extra_data': json.dumps({'value': 500}),
            'descriptor': {'type': 'type1', 'tags': ['dispatch_short']},
            'datetime': '2019-01-01T11:40:31.043Z',
        },
        'activity_change': 1,
        'loyalty_change': 1,
    },
    {
        'event': {
            'event_id': 'event_id_3',
            'type': 'order',
            'order_id': 'string',
            'order_alias': 'string',
            'park_driver_profile_id': 'dbid_uuid',
            'tariff_zone': 'string',
            'extra': {
                'value': 200,
                'tst_dict': {'key': 1},
                'driver_id': '32gdh3_dad8lucn58003nnbc3',
            },
            'extra_data': json.dumps(
                {
                    'value': 200,
                    'tst_dict': {'key': 1},
                    'driver_id': '32gdh3_dad8lucn58003nnbc3',
                },
            ),
            'descriptor': {
                'type': 'type1',
                'tags': ['3443', 'ere', 'dispatch_long'],
            },
            'datetime': '2016-01-01T11:40:31.043Z',
        },
        'activity_change': 1,
        'loyalty_change': 5,
    },
    {
        'event': {
            'event_id': 'event_id_4',
            'type': 'custom',
            'tariff_zone': 'string',
            'order_alias': 'string',
            'order_id': 'string',
            'park_driver_profile_id': 'dbid_uuid',
            'datetime': '2016-01-01T11:40:31.043Z',
            'extra_data': json.dumps({}),
            'descriptor': {'type': 'type1', 'tags': ['dispatch_short']},
        },
        'activity_change': 0,
        'loyalty_change': 0,
    },
]

EXPECTED_RESULT = [
    {
        'id': 'event_id_1',
        'activity_value_change': 1,
        'timestamp': '2019-01-01T11:40:31.043000Z',
        'driver_id': None,
        'db_id': '',
        'time_to_a': 0,
        'distance_to_a': 0,
        'dispatch_traits': {'distance': 'short'},
        'order_id': 'string',
        'order_alias_id': 'string',
        'zone': 'string',
        'activity_value_before': 0,
        'event_type': 'order',
        'event_descriptor': {'name': 'type1', 'tags': ['dispatch_short']},
    },
    {
        'activity_value_before': 0,
        'activity_value_change': 1,
        'db_id': 'dbid',
        'distance_to_a': 0,
        'driver_id': '32gdh3_dad8lucn58003nnbc3',
        'event_descriptor': {
            'name': 'type1',
            'tags': ['3443', 'ere', 'dispatch_long'],
        },
        'event_type': 'order',
        'id': 'event_id_3',
        'order_alias_id': 'string',
        'order_id': 'string',
        'time_to_a': 0,
        'timestamp': '2016-01-01T11:40:31.043000Z',
        'zone': 'string',
        'dispatch_traits': {'distance': 'long'},
    },
]


@pytest.mark.parametrize(
    'tst_request, expected_result',
    [
        (
            {
                'udid': '5b7b0c694f007eaf8578b531',
                'dbid_uuid': '100czsda40da0_39jfdg608349384',
            },
            EXPECTED_RESULT,
        ),
        ({'udid': '5b7b0c694f007eaf8578b531'}, EXPECTED_RESULT),
        ({'driver_id': '3242dbs_djajos2343ndjdla39sm'}, None),
    ],
)
async def test_dms_history(
        mockserver, taxi_driver_metrics, tst_request, expected_result,
):
    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    async def patch_post_request(*args, **kwargs):
        return {'events': TEST_DMS_RESPONSE}

    response = await taxi_driver_metrics.post(HANDLER_PATH, json=tst_request)

    if expected_result:
        assert response.status == 200
        items = await response.json()
        assert items['items'] == expected_result
        assert patch_post_request.times_called
    else:
        assert response.status == 400
