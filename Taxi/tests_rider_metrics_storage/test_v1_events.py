# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_rider_metrics_storage import util

# Generated via `tvmknife unittest service -s 111 -d 2016409`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCZiXs:FD5dO1l2Hn2MEIW7IYswAaXjui3PMStRmXRN-C'
    'RYW'
    'zhDNx2G4Dc05kqXKgZTgn0IYU9efNCeW_V8lP2YXvlWJMksZxsUhTXJu135LUUB0Slj-EiNqS'
    '_6n'
    'DSIs0fH2fxy4mWv0sBTptRW76eKjVnksHfXCNb7OuiivZwG_Nn4DK4'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'rider-metrics-storage'}],
)
@pytest.mark.parametrize('suffix', ['', '/'])
@pytest.mark.parametrize('tvm,code', [(True, 400), (False, 401)])
async def test_400(suffix, tvm, code, taxi_rider_metrics_storage):
    response = await taxi_rider_metrics_storage.post(
        'v1/event/new' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code
    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code if code == 401 else 200
    response = await taxi_rider_metrics_storage.post(
        'v1/event/complete' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code
    response = await taxi_rider_metrics_storage.post(
        'v1/events/history' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code if code == 401 else 200


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_new(taxi_rider_metrics_storage, pgsql):
    for x in range(3):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new',
            json={
                'idempotency_token': 'token-' + str(x),
                'user_id': '100000000000000000000000',
                'type': 'type-Z',
                'created': '2019-01-01T00:00:00+0000',
                'extra_data': {'data': str(x)},
                'order_id': 'order_id: ' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert response.status_code == 200
        assert response.json() == {}

    for x in range(3):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new',
            json={
                'idempotency_token': 'eid-' + str(x + 1),
                'user_id': '100000000000000000000000',
                'type': 'type-Z',
                'created': '2019-01-01T00:00:00+0000',
            },
        )
        assert response.status_code == 200
        assert response.json() == {}

    assert (
        util.select_named(
            'select * from events.queue_64 where event_id>9 order by event_id',
            pgsql,
        )
        == [
            {
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'event_id': 10,
                'event_type_id': 3,
                'extra_data': '{"data":"0"}',
                'descriptor': None,
                'order_id': 'order_id: 0',
                'tariff_zone_id': 1,
                'unique_rider_id': 1001,
            },
            {
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'event_id': 11,
                'event_type_id': 3,
                'extra_data': '{"data":"1"}',
                'descriptor': None,
                'order_id': 'order_id: 1',
                'tariff_zone_id': 1,
                'unique_rider_id': 1001,
            },
            {
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'activation': datetime.datetime(2019, 1, 1, 0, 0, 0, 200000),
                'event_id': 12,
                'event_type_id': 3,
                'extra_data': '{"data":"2"}',
                'descriptor': None,
                'order_id': 'order_id: 2',
                'tariff_zone_id': 1,
                'unique_rider_id': 1001,
            },
        ]
    )

    assert (
        util.select_named(
            'select * from events.tokens where token_id>9 order by token_id',
            pgsql,
        )
        == [
            {
                'deadline': datetime.datetime(2019, 1, 2, 0, 0),
                'token': 'token-0',
                'token_id': 10,
            },
            {
                'deadline': datetime.datetime(2019, 1, 2, 0, 0),
                'token': 'token-1',
                'token_id': 11,
            },
            {
                'deadline': datetime.datetime(2019, 1, 2, 0, 0),
                'token': 'token-2',
                'token_id': 12,
            },
        ]
    )


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('dbridermetrics', files=['test.sql'])
async def test_unprocessed_complete(taxi_rider_metrics_storage, pgsql):
    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert response.status_code == 200
    assert (
        util.to_map(response.json()['items'], 'user_id', util.hide_ticket)
        == {
            '100000000000000000000000': {
                'events': [
                    {
                        'event_id': 1,
                        'extra_data': {},
                        'order_id': 'order_id',
                        'tariff_zone': 'moscow',
                        'created': '2000-01-01T00:00:00+00:00',
                        'type': 'type-X',
                    },
                    {
                        'event_id': 2,
                        'extra_data': {},
                        'tariff_zone': 'spb',
                        'created': '2000-01-01T00:10:00+00:00',
                        'type': 'type-Y',
                    },
                    {
                        'event_id': 3,
                        'extra_data': {},
                        'created': '2000-01-01T00:20:00+00:00',
                        'type': 'type-X',
                    },
                    {
                        'event_id': 4,
                        'extra_data': {},
                        'created': '2000-01-01T00:30:00+00:00',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'user_id': '100000000000000000000000',
            },
            '200000000000000000000000': {
                'events': [
                    {
                        'event_id': 9,
                        'extra_data': {},
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
    )

    assert (
        util.to_map(
            util.select_named(
                'select t.*,u.unique_rider from events.tickets_64 t'
                ' left join common.unique_riders u'
                ' on t.unique_rider_id=u.unique_rider_id',
                pgsql,
            ),
            'unique_rider_id',
            util.hide_ticket,
        )
        == {
            1001: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'ticket_id': '*',
                'unique_rider_id': 1001,
                'unique_rider': '100000000000000000000000',
                'down_counter': 4,
            },
            1002: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'ticket_id': '*',
                'unique_rider_id': 1002,
                'unique_rider': '200000000000000000000000',
                'down_counter': 1,
            },
            1003: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'ticket_id': '*',
                'unique_rider_id': 1003,
                'unique_rider': '300000000000000000000000',
                'down_counter': 1,
            },
            1004: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'ticket_id': '*',
                'unique_rider_id': 1004,
                'unique_rider': '400000000000000000000000',
                'down_counter': 1,
            },
            1005: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'ticket_id': '*',
                'unique_rider_id': 1005,
                'unique_rider': '500000000000000000000000',
                'down_counter': 1,
            },
            1006: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'ticket_id': '*',
                'unique_rider_id': 1006,
                'unique_rider': '600000000000000000000000',
                'down_counter': 1,
            },
        }
    )

    items = response.json()['items']
    for item in items:
        for i in range(len(item['events'])):
            event = item['events'][i]
            for _ in range(2):
                response = await taxi_rider_metrics_storage.post(
                    'v1/event/complete',
                    json={
                        'ticket_id': item['ticket_id'],
                        'event_id': event['event_id'],
                    },
                )
                if response.status_code != 409:
                    break
            assert response.status_code == 200
            assert response.json() == {}

            response = await taxi_rider_metrics_storage.post(
                'v1/event/complete',
                json={
                    'ticket_id': item['ticket_id'],
                    'event_id': event['event_id'],
                },
            )
            assert response.status_code == 409
            err = [
                'Invalid event_id='
                + str(event['event_id'])
                + ' ticket(id='
                + str(item['ticket_id'])
                + ', unique_rider_id=1001, down_counter='
                + str(len(item['events']) - i - 1)
                + ', deadline=2019-01-01T00:01:00+0000'
                + ', now=2019-01-01T00:00:00+0000)',
                'Invalid event_id='
                + str(event['event_id'])
                + ' or ticket not found('
                + str(item['ticket_id'])
                + ')',
                # 'Invalid ticket.down_counter ticket(id=' +
                # str(item['ticket_id']) + ', udid_id=' +
                # str(udids[item['unique_driver_id']]['udid_id']) +
                # ', down_counter=-1, ' +
                # 'deadline=2019-01-01T00:00:00.3+0000,' +
                # ' now=2019-01-01T00:00:00+0000)',
            ]
            assert (response.json()) == (
                {
                    'code': '409',
                    'message': (
                        err[0] if i < len(item['events']) - 1 else err[1]
                    ),
                }
            )

    assert util.select_named('select * from events.queue_64', pgsql) == []

    assert (
        util.to_map(
            util.select_named(
                'select * from events.logs_64_partitioned', pgsql,
            ),
            'event_id',
        )
        == {
            1: {
                'created': datetime.datetime(2000, 1, 1, 0, 0),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 1,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_id': 'order_id',
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': 1,
                'unique_rider_id': 1001,
            },
            2: {
                'created': datetime.datetime(2000, 1, 1, 0, 10),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 2,
                'event_type_id': 2,
                'extra_data': None,
                'descriptor': None,
                'order_id': None,
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': 2,
                'unique_rider_id': 1001,
            },
            3: {
                'created': datetime.datetime(2000, 1, 1, 0, 20),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 3,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_id': None,
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': None,
                'unique_rider_id': 1001,
            },
            4: {
                'created': datetime.datetime(2000, 1, 1, 0, 30),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 4,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_id': None,
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': None,
                'unique_rider_id': 1001,
            },
            5: {
                'created': datetime.datetime(2000, 1, 1, 0, 40),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 5,
                'event_type_id': 3,
                'extra_data': None,
                'descriptor': None,
                'order_id': None,
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': None,
                'unique_rider_id': 1003,
            },
            6: {
                'created': datetime.datetime(2000, 1, 1, 0, 0, 50),
                'deadline': datetime.datetime(2019, 1, 1, 0, 15),
                'event_id': 6,
                'event_type_id': 2,
                'extra_data': None,
                'descriptor': None,
                'order_id': None,
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': 1,
                'unique_rider_id': 1004,
            },
            7: {
                'created': datetime.datetime(2000, 1, 1, 0, 1),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 7,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_id': None,
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': 2,
                'unique_rider_id': 1005,
            },
            8: {
                'created': datetime.datetime(2000, 1, 1, 0, 1, 10),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 8,
                'event_type_id': 1,
                'extra_data': None,
                'descriptor': None,
                'order_id': None,
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': None,
                'unique_rider_id': 1006,
            },
            9: {
                'created': datetime.datetime(2000, 1, 1, 0, 10),
                'deadline': datetime.datetime(2100, 1, 1, 0, 0),
                'event_id': 9,
                'event_type_id': 2,
                'extra_data': None,
                'descriptor': None,
                'order_id': None,
                'processed': datetime.datetime(2019, 1, 1, 0, 0),
                'tariff_zone_id': 2,
                'unique_rider_id': 1002,
            },
        }
    )

    response = await taxi_rider_metrics_storage.post(
        'v1/events/history',
        json={
            'user_id': '100000000000000000000000',
            'created_after': '2000-01-01T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event_id': 1,
                'extra_data': '{}',
                'created': '2000-01-01T00:00:00+00:00',
                'order_id': 'order_id',
                'tariff_zone': 'moscow',
                'type': 'type-X',
            },
            {
                'event_id': 2,
                'extra_data': '{}',
                'created': '2000-01-01T00:10:00+00:00',
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
            {
                'event_id': 3,
                'extra_data': '{}',
                'created': '2000-01-01T00:20:00+00:00',
                'type': 'type-X',
            },
            {
                'event_id': 4,
                'extra_data': '{}',
                'created': '2000-01-01T00:30:00+00:00',
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/history',
        json={
            'user_id': '100000000000000000000000',
            'created_after': '2000-01-01T00:20:00+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event_id': 3,
                'extra_data': '{}',
                'created': '2000-01-01T00:20:00+00:00',
                'type': 'type-X',
            },
            {
                'event_id': 4,
                'extra_data': '{}',
                'created': '2000-01-01T00:30:00+00:00',
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/history',
        json={
            'user_id': 'X00000000000000000000000',
            'created_after': '2000-01-01T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}


@pytest.mark.pgsql('dbridermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_unprocessed_limit(taxi_rider_metrics_storage, pgsql):
    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 1},
    )
    assert response.status_code == 200
    assert (
        util.to_map(response.json()['items'], 'user_id', util.hide_ticket)
        == {
            '100000000000000000000000': {
                'events': [
                    {
                        'event_id': 1,
                        'extra_data': {},
                        'order_id': 'order_id',
                        'tariff_zone': 'moscow',
                        'created': '2000-01-01T00:00:00+00:00',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'user_id': '100000000000000000000000',
            },
        }
    )

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 3},
    )
    assert response.status_code == 200
    assert (
        util.to_map(response.json()['items'], 'user_id', util.hide_ticket)
        == {
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
    )


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
    RIDER_METRICS_STORAGE_EVENTS_THROTTLE_SETTINGS={
        'events_latency': {
            'weight_factor_cent': 50,
            'panic_level_ms': 50000,
            'relax_level_ms': 20000,
        },
        'queue_size': {
            'weight_factor_cent': 99,
            'panic_level': 11,
            'relax_level': 11,
        },
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_events_throttle_queue_size(
        taxi_rider_metrics_storage, pgsql, testpoint,
):
    @testpoint('call::handlers-events-throttle::queue_size_task')
    def task_testpoint(data):
        pass

    await taxi_rider_metrics_storage.enable_testpoints()
    await task_testpoint.wait_call()

    for x in range(4):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'user_id': '0123456789AB0123456789AB',
                'type': 'type-Z',
                'created': '2019-01-01T00:00:00+00:00',
                'extra_data': {'extra_field': str(x)},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'name': 'user_test',
                },
                'order_id': 'order_id_' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

        await taxi_rider_metrics_storage.run_periodic_task('queue_size_task')
        await task_testpoint.wait_call()

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-3',
            'user_id': '0123456789AB0123456789AB',
            'type': 'type-Z',
            'created': '2019-01-01T00:00:00+00:00',
            'extra_data': {'extra_field': '3'},
            'descriptor': {
                'tags': ['yam-yam', 'tas_teful'],
                'name': 'user_test',
            },
            'order_id': 'order_id_3',
            'tariff_zone': 'moscow',
        },
    )
    assert [response.status_code, response.json()] == [
        429,
        {
            'code': '429',
            'message': 'EventsThrottle current queue size (12) is too big!',
        },
    ]


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_SPLITTING=2,
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
    RIDER_METRICS_STORAGE_EVENTS_THROTTLE_SETTINGS={
        'events_latency': {
            'weight_factor_cent': 99,
            'panic_level_ms': 1000,
            'relax_level_ms': 1000,
        },
        'queue_size': {
            'weight_factor_cent': 99,
            'panic_level': 1000,
            'relax_level': 1000,
        },
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['test.sql'])
@pytest.mark.now('2000-01-01T00:59:59')
async def test_events_throttle_latency(taxi_rider_metrics_storage, pgsql):
    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-0',
            'user_id': '0123456789AB0123456789AB',
            'type': 'type-Z',
            'created': '2019-01-01T00:00:00+00:00',
            'extra_data': {'extra_field': '0'},
            'descriptor': {
                'tags': ['yam-yam', 'tas_teful'],
                'name': 'user_test',
            },
            'order_id': 'order_id_0',
            'tariff_zone': 'moscow',
        },
    )
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_rider_metrics_storage.post(
        'v1/event/complete', json={'event_id': 1, 'ticket_id': -1},
    )
    assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_rider_metrics_storage.post(
        'v1/event/new',
        json={
            'idempotency_token': 'idempotency_token-1',
            'user_id': '0123456789AB0123456789AB',
            'type': 'type-Z',
            'created': '2019-01-01T00:00:00+00:00',
            'extra_data': {'extra_field': '1'},
            'descriptor': {
                'tags': ['yam-yam', 'tas_teful'],
                'name': 'user_test',
            },
            'order_id': 'order_id_1',
            'tariff_zone': 'moscow',
        },
    )
    assert [response.status_code, response.json()] == [
        429,
        {
            'code': '429',
            'message': (
                'EventsThrottle current latency (3563010ms) is too big!'
            ),
        },
    ]
