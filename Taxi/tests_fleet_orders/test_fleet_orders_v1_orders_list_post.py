import base64
import datetime
import json

import pytest


ENDPOINT = 'fleet/fleet-orders/v1/orders/list'


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }

    return headers


def parse_date(date):
    return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')


def check_date(date1, date2):
    assert parse_date(date1) == parse_date(date2)


def check_cursor(cursor, request):
    assert (
        cursor['query']['sort']['field'] == request['query']['sort']['field']
    )
    assert cursor['query']['sort']['dir'] == request['query']['sort']['dir']
    if request['query'].get('created_at'):
        if request['query']['created_at'].get('from'):
            check_date(
                cursor['query']['created_at']['from'],
                request['query']['created_at']['from'],
            )
        if request['query']['created_at'].get('to'):
            check_date(
                cursor['query']['created_at']['to'],
                request['query']['created_at']['to'],
            )
    if request['query'].get('driver_id'):
        assert cursor['query']['driver_id'] == request['query']['driver_id']
    if request['query'].get('number'):
        assert cursor['query']['number'] == request['query']['number']
    if request['query'].get('vehicle_id'):
        assert cursor['query']['vehicle_id'] == request['query']['vehicle_id']
    if request['query'].get('statuses'):
        assert cursor['query']['statuses'] == request['query']['statuses']
    if request['query'].get('customer_phone_number'):
        assert (
            cursor['query']['customer_phone_number']
            == request['query']['customer_phone_number']
        )
    if request['query'].get('is_park_creator'):
        assert (
            cursor['query']['is_park_creator']
            == request['query']['is_park_creator']
        )
    if request['query'].get('booked_at'):
        if request['query']['booked_at'].get('from'):
            check_date(
                cursor['query']['booked_at']['from'],
                request['query']['booked_at']['from'],
            )
        if request['query']['booked_at'].get('to'):
            check_date(
                cursor['query']['booked_at']['to'],
                request['query']['booked_at']['to'],
            )
    assert cursor['version'] == 'v1'


def decode_cursor(cursor_str):
    return json.loads(base64.b64decode(cursor_str))


@pytest.mark.parametrize(
    'query',
    [
        {'sort': {'field': 'order_created_at', 'dir': 'desc'}},
        {
            'sort': {'field': 'order_created_at', 'dir': 'desc'},
            'created_at': {
                'from': '2021-05-05T20:10:00+03:00',
                'to': '2021-05-05T20:20:00+03:00',
            },
        },
        {
            'sort': {'field': 'order_created_at', 'dir': 'asc'},
            'created_at': {'from': '2021-05-05T20:10:00+03:00'},
        },
        {
            'sort': {'field': 'order_created_at', 'dir': 'desc'},
            'created_at': {'to': '2021-05-05T20:11:00+03:00'},
        },
        {
            'sort': {'field': 'order_created_at', 'dir': 'desc'},
            'created_at': {
                'from': '2021-04-30T21:00:00+00:00',
                'to': '2021-05-09T21:00:00+00:00',
            },
            'driver_id': 'driver_id1',
        },
        {
            'sort': {'field': 'order_created_at', 'dir': 'desc'},
            'created_at': {
                'from': '2021-04-30T21:00:00+00:00',
                'to': '2021-05-10T21:00:00+00:00',
            },
            'vehicle_id': 'car_id2',
        },
        {'sort': {'field': 'order_created_at', 'dir': 'desc'}, 'number': 2},
        {
            'created_at': {
                'from': '2021-04-30T21:00:00+00:00',
                'to': '2021-05-09T21:00:00+00:00',
            },
            'sort': {'field': 'order_created_at', 'dir': 'desc'},
            'statuses': ['transporting', 'driving'],
        },
        {
            'sort': {'field': 'order_created_at', 'dir': 'desc'},
            'scheduled': True,
        },
        {
            'sort': {'field': 'order_booked_at', 'dir': 'desc'},
            'customer_phone_number': '+491111222222',
        },
        {
            'sort': {'field': 'order_booked_at', 'dir': 'asc'},
            'is_park_creator': False,
        },
        {
            'sort': {'field': 'order_booked_at', 'dir': 'desc'},
            'booked_at': {
                'from': '2021-02-09T00:00:00+01:00',
                'to': '2021-02-10T00:00:00+01:00',
            },
        },
    ],
)
async def test_fleet_orders_get_cursor(taxi_fleet_orders, query):
    request = {'query': query}

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=request, headers=build_headers('park_id1'),
    )

    cursor_str = response.json()['cursor']
    check_cursor(decode_cursor(cursor_str), request)


async def test_fleet_orders_get_cursor_filter(taxi_fleet_orders):
    request = {
        'query': {
            'created_at': {
                'from': '2021-05-01T00:00:00+03:00',
                'to': '2021-05-10T00:00:00+03:00',
            },
            'sort': {'field': 'order_created_at', 'dir': 'desc'},
        },
    }

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=request, headers=build_headers('park_id1'),
    )

    cursor_str = response.json()['cursor']
    check_cursor(decode_cursor(cursor_str), request)
