import datetime

import pytest

from tests_grocery_order_log import models

ORDERS = [
    {
        'yandex_uid': '1000',
        'personal_phone_id': '+79008005555',
        'personal_email_id': '4cab5f88213a40759cdc6a105adeecc9',
        'order_created_date': datetime.datetime(2020, 3, 13),
        'order_state': 'closed',
    },
    {
        'yandex_uid': '1000',
        'personal_phone_id': '+79008005555',
        'personal_email_id': '4cab5f88213a40759cdc6a105adeecc9',
        'order_created_date': datetime.datetime(2020, 4, 13),
        'order_state': 'canceled',
    },
    {
        'yandex_uid': '1000',
        'personal_phone_id': '+79008000000',
        'order_created_date': datetime.datetime(2020, 5, 13),
        'order_state': 'delivering',
    },
    {
        'yandex_uid': '1001',
        'order_created_date': datetime.datetime(2020, 6, 13),
        'order_state': 'delivering',
    },
    {
        'yandex_uid': '1002',
        'order_created_date': datetime.datetime(2020, 7, 13),
    },
]


def _request(**kwargs):
    return {**kwargs}


def _period(start, end):
    return {'start': _to_iso_format(start), 'end': _to_iso_format(end)}


def _range(offset, limit):
    return {'offset': offset, 'limit': limit}


def _to_iso_format(date, time_zone='+00:00'):
    return date.isoformat() + time_zone


@pytest.mark.parametrize(
    'request_data, expected_orders',
    [
        (_request(yandex_uid='1000', range=_range(0, 9)), [0, 1, 2]),
        (_request(yandex_uid='1000', range=_range(1, 1)), [1]),
        (_request(yandex_uid='1001', range=_range(0, 9)), [3]),
        (
            _request(personal_phone_id='+79008005555', range=_range(0, 9)),
            [0, 1],
        ),
        (
            _request(
                personal_email_id='4cab5f88213a40759cdc6a105adeecc9',
                range=_range(0, 9),
            ),
            [0, 1],
        ),
        (
            _request(personal_phone_id='+79008000000', range=_range(0, 9)),  #
            [2],
        ),
        (
            _request(
                yandex_uid='1000',
                period=_period(
                    datetime.datetime(2020, 4, 1),
                    datetime.datetime(2020, 9, 1),
                ),
            ),
            [1, 2],
        ),
        (
            _request(
                yandex_uid='1000',
                period=_period(
                    datetime.datetime(2020, 4, 1),
                    datetime.datetime(2020, 5, 1),
                ),
            ),
            [1],
        ),
        (
            _request(
                yandex_uid='1000',
                range=_range(0, 9),
                filter_by_status='not_closed',
            ),
            [2],
        ),
        (
            _request(
                yandex_uid='1000',
                range=_range(0, 9),
                filter_by_status='canceled',
            ),
            [1],
        ),
        (
            _request(
                yandex_uid='1000',
                filter_by_status='closed',
                range=_range(0, 9),
            ),
            [0],
        ),
        (
            _request(
                personal_email_id='4cab5f88213a40759cdc6a105adeecc9',
                period=_period(
                    datetime.datetime(2020, 3, 12),
                    datetime.datetime(2020, 4, 8),
                ),
            ),
            [0],
        ),
    ],
)
async def test_basic(
        taxi_grocery_order_log, pgsql, request_data, expected_orders,
):
    for order_id, order in enumerate(ORDERS):
        models.OrderLogIndex(pgsql, order_id=order_id, **order).update_db()

    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/ids-by-range', json=request_data,
    )

    assert response.status_code == 200
    expected_orders = list(map(str, expected_orders))
    if (
            'range' in request_data
            or 'personal_phone_id' in request_data
            or 'filter_by_status' in request_data
    ):
        expected_orders = list(reversed(expected_orders))
        assert response.json().get('order_ids', []) == expected_orders
    else:
        assert all(
            map(
                lambda v: v in response.json().get('order_ids', []),
                expected_orders,
            ),
        )


@pytest.mark.parametrize('order_type', ['all', 'eats', 'grocery'])
async def test_order_type(taxi_grocery_order_log, pgsql, order_type):
    yandex_uid = '1000'
    request = _request(yandex_uid=yandex_uid, range=_range(0, 10))
    if order_type != 'all':
        request['order_type'] = order_type
    for i in range(10):
        order_id = 'order_' + str(i)
        if i % 2 == 0:
            order_id += '-grocery'
        models.OrderLogIndex(
            pgsql, order_id=order_id, yandex_uid=yandex_uid,
        ).update_db()

    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/ids-by-range', json=request,
    )

    assert response.status_code == 200
    orders_ids = response.json().get('order_ids', [])
    grocery_ids = [
        order_id for order_id in orders_ids if 'grocery' in order_id
    ]
    if order_type == 'all':
        assert len(orders_ids) == 10
        assert len(grocery_ids) == 5
    if order_type == 'eats':
        assert len(orders_ids) == 5
        assert not grocery_ids
    if order_type == 'grocery':
        assert len(orders_ids) == 5
        assert len(grocery_ids) == 5


@pytest.mark.parametrize(
    'request_data',
    [
        _request(),
        _request(yandex_uid='1001'),
        _request(personal_phone_id='+79008005555'),
        _request(range=_range(0, 9)),
        _request(
            period=_period(
                datetime.datetime(2020, 4, 1), datetime.datetime(2020, 9, 1),
            ),
        ),
    ],
)
async def test_400(taxi_grocery_order_log, request_data):
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/ids-by-range', json=request_data,
    )

    assert response.status_code == 400
