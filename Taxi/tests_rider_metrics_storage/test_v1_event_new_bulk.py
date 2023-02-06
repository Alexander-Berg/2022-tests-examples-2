# -*- coding: utf-8 -*-

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
async def test_v1_event_new_bulk_400(
        suffix, tvm, code, taxi_rider_metrics_storage,
):
    response = await taxi_rider_metrics_storage.post(
        'v1/event/new/bulk' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code


@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_bulk_missed_parameter(taxi_rider_metrics_storage):
    for field in ['idempotency_token', 'user_id', 'type', 'created']:
        json_object = {
            'idempotency_token': 'idempotency_token-' + field,
            'user_id': UNIQUE_RIDER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        }
        del json_object[field]
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new/bulk', json={'events': [json_object]},
        )
        assert response.status_code == 400
        assert response.json()['code'] == '400'


@pytest.mark.config(RIDER_METRICS_STORAGE_EVENT_NEW_BULK_LIMIT=2)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_bulk_exceed_limit(taxi_rider_metrics_storage):
    response = await taxi_rider_metrics_storage.post(
        'v1/event/new/bulk',
        json={
            'events': [
                {
                    'idempotency_token': 'idempotency_token-0',
                    'user_id': UNIQUE_RIDER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-1',
                    'user_id': UNIQUE_RIDER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '1'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 1',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-2',
                    'user_id': UNIQUE_RIDER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '2'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 2',
                    'tariff_zone': 'moscow',
                },
            ],
        },
    )
    assert [response.status_code, response.json()] == [
        400,
        {'code': '400', 'message': 'events number 3 exceeds the limit 2'},
    ]


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_bulk_complete(taxi_rider_metrics_storage, pgsql):
    response = await taxi_rider_metrics_storage.post(
        'v1/event/new/bulk',
        json={
            'events': [
                {
                    'idempotency_token': 'idempotency_token-0',
                    'user_id': UNIQUE_RIDER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-1',
                    'user_id': UNIQUE_RIDER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '1'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 1',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-2',
                    'user_id': UNIQUE_RIDER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '2'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 2',
                    'tariff_zone': 'moscow',
                },
            ],
        },
    )
    assert [response.status_code, response.json()] == [
        200,
        {
            'events': [
                {'idempotency_token': 'idempotency_token-0'},
                {'idempotency_token': 'idempotency_token-1'},
                {'idempotency_token': 'idempotency_token-2'},
            ],
        },
    ]

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new/bulk',
        json={
            'events': [
                {
                    'idempotency_token': 'idempotency_token-0',
                    'user_id': UNIQUE_RIDER_ID1,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-1',
                    'user_id': UNIQUE_RIDER_ID1,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '1'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 1',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-2',
                    'user_id': UNIQUE_RIDER_ID1,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '2'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 2',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-3',
                    'user_id': UNIQUE_RIDER_ID0,
                    'type': 'type-wrong',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-4',
                    'user_id': UNIQUE_RIDER_ID0,
                    'type': 'type-wrong-2',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'name': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
            ],
        },
    )

    assert [response.status_code, response.json()] == [
        200,
        {
            'events': [
                {'idempotency_token': 'idempotency_token-0'},
                {'idempotency_token': 'idempotency_token-1'},
                {'idempotency_token': 'idempotency_token-2'},
                {
                    'idempotency_token': 'idempotency_token-3',
                    'error': {
                        'code': '403',
                        'message': 'invalid event type type-wrong',
                    },
                },
                {
                    'idempotency_token': 'idempotency_token-4',
                    'error': {
                        'code': '403',
                        'message': 'invalid event type type-wrong-2',
                    },
                },
            ],
        },
    ]

    # NOTE: That assert is needed because v1/events/unprocessed/list
    # doesn't return events just added
    # It should be understood in
    # https://st.yandex-team.ru/EFFICIENCYDEV-5808
    assert (
        select_named(
            'select event_id,unique_rider,event_type_id '
            'from events.queue_64, common.unique_riders where '
            'common.unique_riders.unique_rider_id '
            '= events.queue_64.unique_rider_id '
            'order by event_id',
            pgsql,
        )
        == [
            {
                'event_id': 1,
                'event_type_id': 1,
                'unique_rider': '100000000000000000000000',
            },
            {
                'event_id': 2,
                'event_type_id': 2,
                'unique_rider': '100000000000000000000000',
            },
            {
                'event_id': 3,
                'event_type_id': 1,
                'unique_rider': '100000000000000000000000',
            },
            {
                'event_id': 4,
                'event_type_id': 1,
                'unique_rider': '100000000000000000000000',
            },
            {
                'event_id': 5,
                'event_type_id': 3,
                'unique_rider': '300000000000000000000000',
            },
            {
                'event_id': 6,
                'event_type_id': 2,
                'unique_rider': '400000000000000000000000',
            },
            {
                'event_id': 7,
                'event_type_id': 1,
                'unique_rider': '500000000000000000000000',
            },
            {
                'event_id': 8,
                'event_type_id': 1,
                'unique_rider': '600000000000000000000000',
            },
            {
                'event_id': 9,
                'event_type_id': 2,
                'unique_rider': '200000000000000000000000',
            },
            {
                'event_id': 10,
                'event_type_id': 3,
                'unique_rider': UNIQUE_RIDER_ID0,
            },
            {
                'event_id': 11,
                'event_type_id': 3,
                'unique_rider': UNIQUE_RIDER_ID0,
            },
            {
                'event_id': 12,
                'event_type_id': 3,
                'unique_rider': UNIQUE_RIDER_ID0,
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
