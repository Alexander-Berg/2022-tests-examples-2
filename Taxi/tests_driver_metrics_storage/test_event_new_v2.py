# -*- coding: utf-8 -*-

import datetime
import json

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
WRONG_TIMESTAMP = '2019-01-01T00:00:00+0000'
CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
UDID_ID0 = '0123456789AB0123456789AB'
UDID_ID1 = '02468AbCdEfF02468AbCdEfF'
UDID_WRONG = ''


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-metrics-storage'}],
)
@pytest.mark.parametrize('suffix', ['', '/'])
@pytest.mark.parametrize('tvm,code', [(True, 400), (False, 401)])
async def test_v2_event_new_400(
        suffix, tvm, code, taxi_driver_metrics_storage,
):
    response = await taxi_driver_metrics_storage.post(
        'v2/event/new' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code


@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_event_new_missed_parameter(taxi_driver_metrics_storage):
    for field in ['idempotency_token', 'unique_driver_id', 'type', 'created']:
        json_object = {
            'idempotency_token': 'idempotency_token-' + field,
            'unique_driver_id': UDID_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        }
        del json_object[field]
        response = await taxi_driver_metrics_storage.post(
            'v2/event/new', json=json_object,
        )
        assert response.status_code == 400
        assert response.json()['code'] == '400'


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_event_new_invalid_datetime(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-wrong-ts',
            'unique_driver_id': UDID_ID1,
            'type': 'type-Z',
            'created': WRONG_TIMESTAMP,
        },
    )
    # Т.к. в запросе часовой пояс даты может быть трех видов -
    # без разделителя ':', c ':' и 'Z'-like, этот тест всегда будет провален,
    # поэтому будем отслеживать момент появления более строгой валидации.
    # assert [response.status_code, response.json()] == [400, {
    #        'code': '400',
    #        'message': "Failed to parse request",
    #        }]
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-wrong-ts',
            'unique_driver_id': UDID_ID1,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-correct-ts',
            'unique_driver_id': UDID_ID1,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        },
    )
    assert [response.status_code, response.json()] == [200, {}]


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_event_new_wrong_udid(taxi_driver_metrics_storage):
    wrong_udid = 'WroNGUdIDat62WroNGUdIDat62'

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-wrong-udid',
            'unique_driver_id': wrong_udid,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-correct-udid',
            'unique_driver_id': UDID_ID1,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        },
    )
    assert [response.status_code, response.json()] == [200, {}]


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_event_new_extra_data_is_object(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-extra_data-is-a-string',
            'unique_driver_id': UDID_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'extra_data': 'How can a clam cram in a clean cream can?',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-extra_data-is-an-array',
            'unique_driver_id': UDID_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'extra_data': [
                'How can a clam cram in a clean cream can?',
                False,
                0,
            ],
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-extra_data-is-an-object',
            'unique_driver_id': UDID_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'extra_data': {
                'extra_field': 'How can a clam cram in a clean cream can?',
            },
        },
    )
    assert [response.status_code, response.json()] == [200, {}]


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_event_new_extra_data_is_too_long(
        taxi_driver_metrics_storage,
):
    extra_data = {}
    while len(json.dumps(extra_data)) < 2048:
        extra_data['seq_name_' + str(len(extra_data))] = 1

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-too-long-extra_data',
            'unique_driver_id': UDID_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'extra_data': extra_data,
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.parametrize('order_type', ['order_id', 'order_alias'])
async def test_v2_event_new_order_is_too_long(
        order_type, taxi_driver_metrics_storage,
):
    order = ''.join(['a'] * 256)

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-too-long-extra_data',
            'unique_driver_id': UDID_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            order_type: order,
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_event_new_complete(taxi_driver_metrics_storage, pgsql):
    for x in range(3):
        response = await taxi_driver_metrics_storage.post(
            'v2/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'unique_driver_id': UDID_ID0,
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
        'v3/event/complete',
        json={
            'event_id': 3,
            'ticket_id': 1,
            'wallet_increment': 1,
            'activity': {'increment': 5, 'value_to_set': 10},
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_driver_metrics_storage.post(
        'v3/event/complete',
        json={
            'event_id': 3,
            'ticket_id': 1,
            'wallet_increment': 1,
            'activity': {'increment': 5},
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert response.status_code == 200
    assert (
        util.to_map(
            response.json()['items'], 'unique_driver_id', util.hide_ticket,
        )
        == {
            '200000000000000000000000': {
                'current_activity': 222,
                'events': [
                    {
                        'park_driver_profile_id': 'dbid_uuid2',
                        'event_id': 9,
                        'extra_data': {},
                        'order_id': 'order_id2',
                        'tariff_zone': 'spb',
                        'created': '2000-01-01T00:10:00+00:00',
                        'type': 'type-Y',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '200000000000000000000000',
            },
            '300000000000000000000000': {
                'events': [
                    {
                        'park_driver_profile_id': 'dbid_uuid1',
                        'event_id': 5,
                        'extra_data': {},
                        'created': '2000-01-01T00:40:00+00:00',
                        'type': 'type-Z',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '300000000000000000000000',
            },
            '400000000000000000000000': {
                'current_activity': 444,
                'events': [
                    {
                        'park_driver_profile_id': 'dbid_uuid2',
                        'event_id': 6,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'created': '2000-01-01T00:00:50+00:00',
                        'type': 'type-Y',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '400000000000000000000000',
            },
            '500000000000000000000000': {
                'events': [
                    {
                        'park_driver_profile_id': 'dbid_uuid2',
                        'event_id': 7,
                        'extra_data': {},
                        'tariff_zone': 'spb',
                        'created': '2000-01-01T00:01:00+00:00',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '500000000000000000000000',
            },
            '600000000000000000000000': {
                'events': [
                    {
                        'park_driver_profile_id': 'dbid_uuid2',
                        'event_id': 8,
                        'extra_data': {},
                        'created': '2000-01-01T00:01:10+00:00',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '600000000000000000000000',
            },
        }
    )

    for item in response.json()['items']:
        if 'current_activity' in item:
            current_activity = item['current_activity']
            desired_activity = current_activity
        else:
            desired_activity = 0
        for event in item['events']:
            desired_activity += 5
            response = await taxi_driver_metrics_storage.post(
                'v3/event/complete',
                json={
                    'event_id': event['event_id'],
                    'ticket_id': item['ticket_id'],
                    'wallet_increment': 1,
                    'activity': {
                        'increment': 5,
                        'value_to_set': desired_activity,
                    },
                },
            )
            assert [response.status_code, response.json()] == [200, {}]
            current_activity = desired_activity

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert [response.status_code, response.json()] == [200, {'items': []}]


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 1},
        'type-Z': {'__default__': 22, 'custom': 11},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_event_ttl(taxi_driver_metrics_storage, pgsql):

    cursor = pgsql['drivermetrics'].conn.cursor()
    cursor.execute('delete from events.queue_64')

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-1',
            'unique_driver_id': UDID_ID0,
            'type': 'type-wrong',
            'created': CORRECT_TIMESTAMP,
            'descriptor': {'type': 'user_test'},
        },
    )
    assert [response.status_code, response.json()] == [
        403,
        {'code': '403', 'message': 'invalid event type type-wrong'},
    ]

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-2',
            'unique_driver_id': UDID_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'descriptor': {'type': 'user_test'},
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_driver_metrics_storage.post(
        'v2/event/new',
        json={
            'idempotency_token': 'idempotency_token-3',
            'unique_driver_id': UDID_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'descriptor': {'type': 'custom'},
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    assert (
        util.select_named(
            'select descriptor, extra_data, deadline from events.queue_64'
            ' order by deadline',
            pgsql,
        )
        == [
            {
                'descriptor': '{"type":"custom"}',
                'deadline': datetime.datetime(2019, 1, 1, 0, 11),
                'extra_data': '{}',
            },
            {
                'descriptor': '{"type":"user_test"}',
                'deadline': datetime.datetime(2019, 1, 1, 0, 22),
                'extra_data': '{}',
            },
        ]
    )
