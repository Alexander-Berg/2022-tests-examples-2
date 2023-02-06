# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_driver_metrics_storage import util

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76'
    'Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXDiiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848P'
    'W-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkH'
    'R3s'
)

CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
UDID_ID1 = '100000000000000000000000'


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_new_complete(taxi_driver_metrics_storage, pgsql):
    for x in range(3):
        response = await taxi_driver_metrics_storage.post(
            'v2/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'unique_driver_id': UDID_ID1,
                'type': 'type-Z',
                'created': CORRECT_TIMESTAMP,
                'park_driver_profile_id': 'qwerty',
                'extra_data': {'extra_field': str(x)},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'type': 'user_test',
                },
                'order_id': 'order_id: ' + str(x),
                'order_alias': 'order_alias: ' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_driver_metrics_storage.post(
        'v2/activity_values/list',
        json={
            'unique_driver_ids': [
                UDID_ID1,
                'W',
                'E',
                'R',
                'T',
                'Y',
                'U',
                'BAD_UDID',
            ],
            'strict': True,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'unique_driver_id': '100000000000000000000000', 'value': 100},
            {'unique_driver_id': 'W', 'value': 222},
            {'unique_driver_id': 'E', 'value': 100},
            {'unique_driver_id': 'R', 'value': 444},
            {'unique_driver_id': 'T', 'value': 100},
            {'unique_driver_id': 'Y', 'value': 100},
            {'unique_driver_id': 'U', 'value': 100},
            {'unique_driver_id': 'BAD_UDID', 'value': 100},
        ],
    }

    assert (
        util.select_named(
            'select * from events.logs_64_partitioned ' 'order by event_id',
            pgsql,
        )
        == [
            {
                'created': datetime.datetime(2000, 1, 1, 0, 0),
                'dbid_uuid_id': None,
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 1,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_alias': None,
                'order_id': 'order_id',
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': 1,
                'udid_id': 1,
            },
            {
                'created': datetime.datetime(2000, 1, 1, 0, 10),
                'dbid_uuid_id': None,
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 2,
                'event_type_id': 2,
                'extra_data': None,
                'descriptor': None,
                'order_alias': 'order_alias',
                'order_id': None,
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': 2,
                'udid_id': 1,
            },
            {
                'created': datetime.datetime(2000, 1, 1, 0, 20),
                'dbid_uuid_id': None,
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 3,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_alias': None,
                'order_id': None,
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': None,
                'udid_id': 1,
            },
            {
                'created': datetime.datetime(2000, 1, 1, 0, 30),
                'dbid_uuid_id': None,
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 4,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_alias': None,
                'order_id': None,
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': None,
                'udid_id': 1,
            },
            {
                'created': datetime.datetime(2000, 1, 1, 0, 40),
                'dbid_uuid_id': None,
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 5,
                'event_type_id': 3,
                'extra_data': None,
                'descriptor': None,
                'order_alias': None,
                'order_id': None,
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': None,
                'udid_id': 3,
            },
            {
                'created': datetime.datetime(2000, 1, 1, 0, 0, 50),
                'dbid_uuid_id': None,
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 6,
                'event_type_id': 2,
                'extra_data': None,
                'descriptor': None,
                'order_alias': None,
                'order_id': None,
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': 1,
                'udid_id': 4,
            },
            {
                'created': datetime.datetime(2000, 1, 1, 0, 1),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'dbid_uuid_id': None,
                'event_id': 7,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_alias': None,
                'order_id': None,
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': 2,
                'udid_id': 5,
            },
            {
                'created': datetime.datetime(2000, 1, 1, 0, 1, 10),
                'dbid_uuid_id': None,
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 8,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_alias': None,
                'order_id': None,
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': None,
                'udid_id': 6,
            },
            {
                'created': datetime.datetime(2000, 1, 1, 0, 10),
                'dbid_uuid_id': None,
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 9,
                'event_type_id': 2,
                'extra_data': None,
                'descriptor': None,
                'order_alias': None,
                'order_id': None,
                'processed': datetime.datetime(2000, 1, 1, 0, 0),
                'tariff_zone_id': 2,
                'udid_id': 2,
            },
        ]
    )

    assert (
        util.select_named(
            'select '
            'created,'
            'dbid_uuid_id,'
            'deadline,'
            'activation,'
            'event_id,'
            'event_type_id,'
            'extra_data,'
            'descriptor,'
            'order_alias,'
            'order_id,'
            'tariff_zone_id,'
            'udid_id '
            'from events.queue_64 order by event_id',
            pgsql,
        )
        == [
            {
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'dbid_uuid_id': 1,
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'event_id': 10,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"0"}',
                'descriptor': (
                    '{"type":"user_test",' '"tags":["yam-yam","tas_teful"]}'
                ),
                'order_alias': 'order_alias: 0',
                'order_id': 'order_id: 0',
                'tariff_zone_id': 1,
                'udid_id': 1,
            },
            {
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'dbid_uuid_id': 1,
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'event_id': 11,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"1"}',
                'descriptor': (
                    '{"type":"user_test",' '"tags":["yam-yam","tas_teful"]}'
                ),
                'order_alias': 'order_alias: 1',
                'order_id': 'order_id: 1',
                'tariff_zone_id': 1,
                'udid_id': 1,
            },
            {
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'dbid_uuid_id': 1,
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'event_id': 12,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"2"}',
                'descriptor': (
                    '{"type":"user_test",' '"tags":["yam-yam","tas_teful"]}'
                ),
                'order_alias': 'order_alias: 2',
                'order_id': 'order_id: 2',
                'tariff_zone_id': 1,
                'udid_id': 1,
            },
        ]
    )

    assert (
        util.select_named(
            'select udid_id,updated,value'
            + ' from data.activity_values order by udid_id',
            pgsql,
        )
        == [
            {
                'udid_id': 2,
                'updated': datetime.datetime(2000, 1, 1, 0, 0),
                'value': 222,
            },
            {
                'udid_id': 4,
                'updated': datetime.datetime(2000, 1, 1, 0, 0),
                'value': 444,
            },
        ]
    )
