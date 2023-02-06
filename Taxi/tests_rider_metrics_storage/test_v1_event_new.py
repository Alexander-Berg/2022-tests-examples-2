# -*- coding: utf-8 -*-

import datetime
import json

import pytest


# Generated via `tvmknife unittest service -s 111 -d 2016409`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCZiXs:FD5dO1l2Hn2MEIW7IYswAaXjui3PMStRmXRN-C'
    'RYW'
    'zhDNx2G4Dc05kqXKgZTgn0IYU9efNCeW_V8lP2YXvlWJMksZxsUhTXJu135LUUB0Slj-EiNqS'
    '_6n'
    'DSIs0fH2fxy4mWv0sBTptRW76eKjVnksHfXCNb7OuiivZwG_Nn4DK4'
)

WRONG_TIMESTAMP = '2019-01-01T00:00:00+0000'
CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
UNIQUE_RIDER_ID0 = '0123456789AB0123456789AB'
UNIQUE_RIDER_ID1 = '02468AbCdEfF02468AbCdEfF'
UNIQUE_RIDER_WRONG = ''


def select_named(query, pgsql):
    cursor = pgsql['dbridermetrics'].conn.cursor()
    cursor.execute(query)
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def hide_ticket(item):
    assert 'ticket_id' in item
    assert isinstance(item['ticket_id'], int)
    assert item['ticket_id'] > 0
    item['ticket_id'] = '*'
    return item


def to_map(items, key, transform=None):
    result = {}
    for item in items:
        result[item[key]] = item if transform is None else transform(item)
    assert len(items) == len(result)
    return result


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'rider-metrics-storage'}],
)
@pytest.mark.parametrize('suffix', ['', '/'])
@pytest.mark.parametrize('tvm,code', [(True, 400), (False, 401)])
async def test_v1_event_new_400(suffix, tvm, code, taxi_rider_metrics_storage):
    response = await taxi_rider_metrics_storage.post(
        'v1/event/new' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code


@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_missed_parameter(taxi_rider_metrics_storage):
    for field in ['idempotency_token', 'user_id', 'type', 'created']:
        json_object = {
            'idempotency_token': 'idempotency_token-' + field,
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        }
        del json_object[field]
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new', json=json_object,
        )
        assert response.status_code == 400
        assert response.json()['code'] == '400'


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_invalid_datetime(taxi_rider_metrics_storage):
    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-wrong-ts',
            'user_id': UNIQUE_RIDER_ID1,
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

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-wrong-ts',
            'user_id': UNIQUE_RIDER_ID1,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-correct-ts',
            'user_id': UNIQUE_RIDER_ID1,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        },
    )
    assert [response.status_code, response.json()] == [200, {}]


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_custom_user(taxi_rider_metrics_storage):
    custom_user = 'WroNGUdIDat62WroNGUdIDat62'

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-wrong-user',
            'user_id': custom_user,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    # NOTE(arkcoon): Non-hex value is applicable
    # assert [response.status_code, response.json()] == [
    #    400,
    #    {
    #        'code': '400',
    #        'message': (
    #            'Value of \'user_id\': value ('
    #            + custom_user
    #            + ') doesn\'t match pattern \'^[0-9a-fA-F]{24}$\''
    #        ),
    #    },
    # ]

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-correct-user',
            'user_id': UNIQUE_RIDER_ID1,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        },
    )
    assert [response.status_code, response.json()] == [200, {}]


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_extra_data_is_object(taxi_rider_metrics_storage):
    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-extra_data-is-a-string',
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'extra_data': 'How can a clam cram in a clean cream can?',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-extra_data-is-an-array',
            'user_id': UNIQUE_RIDER_ID0,
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

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-extra_data-is-an-object',
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'extra_data': {
                'extra_field': 'How can a clam cram in a clean cream can?',
            },
        },
    )
    assert [response.status_code, response.json()] == [200, {}]


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_descriptor_is_too_long(taxi_rider_metrics_storage):
    descriptor = {'name': '', 'type': 'type-Z'}
    while len(json.dumps(descriptor)) < 2048:
        descriptor['name'] += '_seq_' + str(len(descriptor))

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-too-long-descriptor',
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'descriptor': descriptor,
        },
    )
    assert [response.status_code, response.json()] == [
        400,
        {'code': '400', 'message': 'descriptor is too long (>= 1024)'},
    ]


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_order_id_is_too_long(taxi_rider_metrics_storage):
    order_id = ''.join(['a'] * 256)

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-too-long-order-id',
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'order_id': order_id,
        },
    )
    assert [response.status_code, response.json()] == [
        400,
        {'code': '400', 'message': 'order_id is too long (>= 255)'},
    ]


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_complete(taxi_rider_metrics_storage, pgsql):
    for x in range(3):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'user_id': UNIQUE_RIDER_ID0,
                'type': 'type-Z',
                'created': CORRECT_TIMESTAMP,
                'extra_data': {'extra_field': str(x)},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'name': 'user_test',
                },
                'order_id': 'order_id: ' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    for x in range(3):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'user_id': UNIQUE_RIDER_ID0,
                'type': 'type-Z',
                'created': CORRECT_TIMESTAMP,
                'extra_data': {'extra_field': str(x)},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'name': 'user_test',
                },
                'order_id': 'order_id: ' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    assert (
        select_named(
            'select * from events.tokens where token_id>9 order by token_id',
            pgsql,
        )
        == [
            {
                'deadline': datetime.datetime(2019, 1, 2, 0, 0),
                'token': 'idempotency_token-0',
                'token_id': 10,
            },
            {
                'deadline': datetime.datetime(2019, 1, 2, 0, 0),
                'token': 'idempotency_token-1',
                'token_id': 11,
            },
            {
                'deadline': datetime.datetime(2019, 1, 2, 0, 0),
                'token': 'idempotency_token-2',
                'token_id': 12,
            },
        ]
    )

    assert (
        select_named(
            'select * from events.queue_64 where event_id>9 order by event_id',
            pgsql,
        )
        == [
            {
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': 10,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"0"}',
                'order_id': 'order_id: 0',
                'tariff_zone_id': 1,
                'unique_rider_id': 1,
            },
            {
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': 11,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"1"}',
                'order_id': 'order_id: 1',
                'tariff_zone_id': 1,
                'unique_rider_id': 1,
            },
            {
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': 12,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"2"}',
                'order_id': 'order_id: 2',
                'tariff_zone_id': 1,
                'unique_rider_id': 1,
            },
        ]
    )

    response = await taxi_rider_metrics_storage.post(
        'v1/event/complete', json={'event_id': 3, 'ticket_id': 1},
    )
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert response.status_code == 200
    assert to_map(response.json()['items'], 'user_id', hide_ticket) == {
        '200000000000000000000000': {
            'events': [
                {
                    'event_id': 9,
                    'extra_data': {},
                    'order_id': 'order_id2',
                    'tariff_zone': 'spb',
                    'created': '2000-01-01T00:10:00+00:00',
                    'type': 'type-Y',
                },
            ],
            'ticket_id': '*',
            'user_id': '200000000000000000000000',
        },
        '300000000000000000000000': {
            'events': [
                {
                    'event_id': 5,
                    'extra_data': {},
                    'created': '2000-01-01T00:40:00+00:00',
                    'type': 'type-Z',
                },
            ],
            'ticket_id': '*',
            'user_id': '300000000000000000000000',
        },
        '400000000000000000000000': {
            'events': [
                {
                    'event_id': 6,
                    'extra_data': {},
                    'tariff_zone': 'moscow',
                    'created': '2000-01-01T00:00:50+00:00',
                    'type': 'type-Y',
                },
            ],
            'ticket_id': '*',
            'user_id': '400000000000000000000000',
        },
        '500000000000000000000000': {
            'events': [
                {
                    'event_id': 7,
                    'extra_data': {},
                    'tariff_zone': 'spb',
                    'created': '2000-01-01T00:01:00+00:00',
                    'type': 'type-X',
                },
            ],
            'ticket_id': '*',
            'user_id': '500000000000000000000000',
        },
        '600000000000000000000000': {
            'events': [
                {
                    'event_id': 8,
                    'extra_data': {},
                    'created': '2000-01-01T00:01:10+00:00',
                    'type': 'type-X',
                },
            ],
            'ticket_id': '*',
            'user_id': '600000000000000000000000',
        },
    }

    for item in response.json()['items']:
        for event in item['events']:
            response = await taxi_rider_metrics_storage.post(
                'v1/event/complete',
                json={
                    'event_id': event['event_id'],
                    'ticket_id': item['ticket_id'],
                },
            )
            assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert [response.status_code, response.json()] == [200, {'items': []}]


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 1},
        'type-Z': {'__default__': 22, 'custom': 11},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_ttl(taxi_rider_metrics_storage, pgsql):

    cursor = pgsql['dbridermetrics'].conn.cursor()
    cursor.execute('delete from events.queue_64')

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-1',
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-wrong',
            'created': CORRECT_TIMESTAMP,
            'descriptor': {'name': 'user_test'},
        },
    )
    assert [response.status_code, response.json()] == [
        403,
        {'code': '403', 'message': 'invalid event type type-wrong'},
    ]

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-2',
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'descriptor': {'name': 'user_test'},
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-3',
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'descriptor': {'name': 'custom'},
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    assert (
        select_named(
            'select descriptor, extra_data, deadline '
            'from events.queue_64 order by deadline',
            pgsql,
        )
        == [
            {
                'deadline': datetime.datetime(2019, 1, 1, 0, 11),
                'descriptor': '{"name":"custom"}',
                'extra_data': '{}',
            },
            {
                'deadline': datetime.datetime(2019, 1, 1, 0, 22),
                'descriptor': '{"name":"user_test"}',
                'extra_data': '{}',
            },
        ]
    )
