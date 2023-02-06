import base64
import datetime
import json

import pytest


ENDPOINT = 'fleet/fleet-orders/v1/orders/schedule'


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
    check_date(
        cursor['query']['interval']['from'],
        request['query']['interval']['from'],
    )
    check_date(
        cursor['query']['interval']['to'], request['query']['interval']['to'],
    )
    assert cursor['version'] == 'v1'
    if request['query'].get('filter'):
        assert cursor['query']['filter'] == request['query']['filter']
    if request['query'].get('offset'):
        assert cursor['query']['offset'] == request['query']['offset']


def decode_cursor(cursor_str):
    return json.loads(base64.b64decode(cursor_str))


@pytest.mark.parametrize(
    'query',
    [
        (
            {
                'query': {
                    'interval': {
                        'from': '2021-02-09T00:00:00+03:00',
                        'to': '2021-02-10T00:00:00+03:00',
                    },
                },
            }
        ),
        (
            {
                'query': {
                    'interval': {
                        'from': '2021-02-09T00:00:00+03:00',
                        'to': '2021-02-10T00:00:00+03:00',
                    },
                    'filter': 'john',
                },
            }
        ),
        (
            {
                'query': {
                    'interval': {
                        'from': '2021-02-09T00:00:00+03:00',
                        'to': '2021-02-10T00:00:00+03:00',
                    },
                    'offset': 1,
                },
            }
        ),
        (
            {
                'query': {
                    'interval': {
                        'from': '2021-02-09T00:00:00+03:00',
                        'to': '2021-02-10T00:00:00+03:00',
                    },
                    'filter': 'john',
                    'offset': 1,
                },
            }
        ),
    ],
)
async def test_fleet_orders_schedule_get_cursor(taxi_fleet_orders, query):
    response = await taxi_fleet_orders.post(
        ENDPOINT, json=query, headers=build_headers('park_id1'),
    )

    cursor_str = response.json()['cursor']
    check_cursor(decode_cursor(cursor_str), query)


async def test_schedule_get_cursor_bad_query(taxi_fleet_orders):
    query = {
        'query': {
            'interval': {
                'from': '2021-02-10T00:00:00+03:00',
                'to': '2021-02-09T00:00:00+03:00',
            },
        },
    }

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=query, headers=build_headers('park_id1'),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'time interval end is before start',
    }
