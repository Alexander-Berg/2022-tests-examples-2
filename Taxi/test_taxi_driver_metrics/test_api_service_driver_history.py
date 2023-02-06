import datetime
import json

import pytest

HANDLER_PATH = 'v1/service/driver/history'
DRIVER_UDID = '5b7b0c694f007eaf8578b531'
TST_ZONE = 'burgund'
TST_ORDER_ID = 'dlsjfslkfj'
TIMESTAMP = datetime.datetime.fromisoformat('2016-08-25T18:50:36+00:00')
TST_TIMEPOINT_1 = datetime.datetime(year=2018, month=1, day=1)
TST_ISO_FORMAT_TIMESTAMP = (
    TST_TIMEPOINT_1.isoformat(timespec='microseconds') + 'Z'
)
TEST_DMS_RESPONSE = [
    {
        'event': {
            'event_id': 'event_id_1',
            'type': 'order',
            'order_id': 'string',
            'order_alias': 'string',
            'park_driver_profile_id': 'string',
            'tariff_zone': 'string',
            'extra': {'value': 2000},
            'extra_data': json.dumps({'value': 2000}),
            'descriptor': {'type': 'type1'},
            'datetime': '2019-01-01T11:40:31.043Z',
        },
        'activity_change': 5,
        'loyalty_change': 2,
        'priority_change': 1,
        'complete_score_change': 3,
        'priority_absolute': 5,
    },
    {
        'event': {
            'event_id': 'event_id_2',
            'type': 'order',
            'order_id': 'string',
            'order_alias': 'string',
            'park_driver_profile_id': 'string',
            'tariff_zone': 'string',
            'extra_data': json.dumps({'value': 2000}),
            'extra': {'value': 2000},
            'descriptor': {'type': 'type1', 'tags': ['3443', 'ere']},
            'datetime': '2017-01-01T11:40:31.043Z',
        },
        'activity_change': -8,
        'loyalty_change': 0,
    },
    {
        'event': {
            'event_id': 'event_id_3',
            'type': 'not_order',
            'order_id': 'string',
            'order_alias': 'string',
            'park_driver_profile_id': 'string',
            'tariff_zone': 'string',
            'extra': {'value': 1000, 'tst_dict': {'key': 1}},
            'extra_data': json.dumps({'value': 1000, 'tst_dict': {'key': 1}}),
            'descriptor': {'type': 'type1', 'tags': ['3443', 'ere']},
            'datetime': '2016-01-01T11:40:31.043Z',
        },
        'activity_change': 10,
        'loyalty_change': 20,
        'priority_change': 1,
        'complete_score_change': 3,
        'priority_absolute': 5,
    },
]

TST_EVENT_1 = {
    'event': {
        'event_id': 'event_id_1',
        'created': '2019-01-01T11:40:31.043000Z',
        'park_driver_profile_id': 'string',
        'order_id': 'string',
        'order_alias_id': 'string',
        'zone': 'string',
        'event_type': 'order',
        'event_descriptor': {'name': 'type1'},
        'additional_properties': {'value': 2000},
    },
    'result': {
        'activity': 5,
        'loyalty': 2,
        'priority': 1,
        'complete_score': 3,
        'priority_absolute': 5,
        'driver_bans': [
            {
                'blocking_id': '5d680b964ddfc26d824315e1',
                'blocking_type': 'activity',
                'ending': '2016-05-04T11:00:00Z',
                'duration': 3600,
                'rule_name': 'activity_block_1',
                'is_active': False,
            },
        ],
    },
}

TST_EVENT_2 = {
    'event': {
        'event_id': 'event_id_2',
        'created': '2017-01-01T11:40:31.043000Z',
        'park_driver_profile_id': 'string',
        'order_id': 'string',
        'order_alias_id': 'string',
        'zone': 'string',
        'event_type': 'order',
        'additional_properties': {'value': 2000},
        'event_descriptor': {'name': 'type1', 'tags': ['3443', 'ere']},
    },
    'result': {
        'activity': -8,
        'loyalty': 0,
        'driver_bans': [
            {
                'blocking_id': '5d680b964ddfc26d824315e2',
                'blocking_type': 'actions',
                'ending': '2016-05-06T09:00:00Z',
                'duration': 176400,
                'rule_name': 'actions_block_1',
                'is_active': False,
            },
        ],
    },
}

TST_EVENT_3 = {
    'event': {
        'event_id': 'event_id_3',
        'created': '2016-01-01T11:40:31.043000Z',
        'park_driver_profile_id': 'string',
        'order_id': 'string',
        'order_alias_id': 'string',
        'zone': 'string',
        'event_type': 'not_order',
        'event_descriptor': {'name': 'type1', 'tags': ['3443', 'ere']},
        'additional_properties': {'value': 1000, 'tst_dict': {'key': 1}},
    },
    'result': {
        'activity': 10,
        'loyalty': 20,
        'priority': 1,
        'complete_score': 3,
        'priority_absolute': 5,
        'driver_bans': [
            {
                'blocking_id': '5d680b964ddfc26d824315e3',
                'blocking_type': 'actions',
                'ending': '2016-05-06T10:00:00Z',
                'duration': 36000,
                'rule_name': 'actions_block_1',
                'is_active': False,
            },
        ],
    },
}


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'tst_request, response_code',
    [
        ({'unique_driver_id': ''}, 400),
        ({'unique_driver_id': DRIVER_UDID}, 200),
        ({'unique_driver_id': DRIVER_UDID, 'limit': 'vasya'}, 400),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'limit': 100,
                'older_than': '2018-08-25V12:12:12',
            },
            400,
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'limit': 100,
                'older_than': '2018-08-25T12:12:12.000000Z',
            },
            200,
        ),
    ],
)
async def test_base(
        taxi_driver_metrics, tst_request, response_code, mockserver,
):
    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    def patch_dms(*args, **kwargs):
        return {'events': []}

    response = await taxi_driver_metrics.post(HANDLER_PATH, json=tst_request)
    assert response
    assert response.status == response_code
    if response_code > 200:
        return
    assert patch_dms.times_called
    assert await response.json()


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'tst_request, result_len, result',
    [
        (
            {'unique_driver_id': DRIVER_UDID},
            3,
            [TST_EVENT_1, TST_EVENT_2, TST_EVENT_3],
        ),
        (
            {'unique_driver_id': DRIVER_UDID, 'limit': 2},
            2,
            [TST_EVENT_1, TST_EVENT_2],
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'limit': 1,
                'older_than': TST_ISO_FORMAT_TIMESTAMP,
            },
            1,
            [TST_EVENT_2],
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'limit': 3,
                'older_than': TST_ISO_FORMAT_TIMESTAMP,
            },
            2,
            [TST_EVENT_2, TST_EVENT_3],
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'limit': 3,
                'older_than': TST_ISO_FORMAT_TIMESTAMP,
                'event_types': ['not_order', 'order'],
            },
            2,
            [TST_EVENT_2, TST_EVENT_3],
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'limit': 3,
                'older_than': TST_ISO_FORMAT_TIMESTAMP,
                'event_types': ['order'],
            },
            1,
            [TST_EVENT_2],
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'limit': 3,
                'older_than': '2014-08-25T12:12:12.000000Z',
            },
            0,
            [],
        ),
    ],
)
async def test_data(
        taxi_driver_metrics, tst_request, result_len, result, mockserver,
):
    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    def patch_post_request(*args, **kwargs):
        data = args[0].json
        timestamp_to = data.get('datetime_to')
        event_types = data.get('event_types')
        if event_types and not isinstance(event_types, list):
            assert False
        if timestamp_to:
            response = [
                event
                for event in TEST_DMS_RESPONSE
                if event['event']['datetime'] < timestamp_to
                and (not event_types or event['event']['type'] in event_types)
            ]
        else:
            response = TEST_DMS_RESPONSE
        limit = data.get('limit', len(response))
        if not data.get('with_additional_info', True):
            assert False

        return {'events': response[:limit]}

    response = await taxi_driver_metrics.post(HANDLER_PATH, json=tst_request)

    assert patch_post_request.times_called
    assert response.status == 200
    content = await response.json()
    assert len(content['items']) == result_len == content['count']
    assert content['unique_driver_id'] == tst_request['unique_driver_id']
    if result:
        assert content['items'] == result
