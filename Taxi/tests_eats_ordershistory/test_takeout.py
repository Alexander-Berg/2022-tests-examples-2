import pytest


@pytest.mark.parametrize(
    'request_json, data_category, orders_remain',
    [
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'ya1', 'is_portal': True}],
            },
            'eats',
            [],
            id='one uid-eats',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'ya1', 'is_portal': True},
                    {'uid': 'ya2', 'is_portal': True},
                ],
            },
            'eats',
            [],
            id='multiple uids-eats',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'ya1', 'is_portal': True},
                    {'uid': 'ya2', 'is_portal': True},
                ],
            },
            'grocery',
            ['euid-1', 'euid-3'],
            id='multiple uids-grocery',
        ),
    ],
)
async def test_takeout_delete(
        mockserver,
        taxi_eats_ordershistory,
        pgsql,
        request_json,
        data_category,
        orders_remain,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        assert 'passport_uids' in request.json
        return {'eaters': [], 'pagination': {'limit': 1000, 'has_more': False}}

    uids = tuple([uid['uid'] for uid in request_json['yandex_uids']])
    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT order_id FROM eats_ordershistory.orders '
        'WHERE yandex_uid IN %s;',
        (uids,),
    )
    orders_before = list(row[0] for row in cursor)

    assert orders_before

    response = await taxi_eats_ordershistory.post(
        f'/takeout/v1/delete/{data_category}', json=request_json,
    )
    assert response.status_code == 200

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT order_id FROM eats_ordershistory.orders '
        'WHERE yandex_uid IN %s;',
        (uids,),
    )
    orders = set(row[0] for row in cursor)

    assert orders == set(orders_remain)

    for order_id in set(orders_before) - set(orders_remain):
        cursor = pgsql['eats_ordershistory'].cursor()
        cursor.execute(
            'SELECT * FROM eats_ordershistory.cart_items '
            'WHERE order_id = %s;',
            (order_id,),
        )
        cart_items = list(cursor)

        assert not cart_items

        cursor = pgsql['eats_ordershistory'].cursor()
        cursor.execute(
            'SELECT * FROM eats_ordershistory.addresses '
            'WHERE order_id = %s;',
            (order_id,),
        )
        addresses = list(cursor)

        assert not addresses

        cursor = pgsql['eats_ordershistory'].cursor()
        cursor.execute(
            'SELECT * FROM eats_ordershistory.feedbacks '
            'WHERE order_id = %s;',
            (order_id,),
        )
        feedbacks = list(cursor)
        assert not feedbacks


@pytest.mark.parametrize(
    'request_json, data_category, response_json',
    [
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'ya1', 'is_portal': True}],
            },
            'eats',
            {'data_state': 'ready_to_delete'},
            id='one eats uid with eats orders',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'ya2', 'is_portal': True}],
            },
            'eats',
            {'data_state': 'ready_to_delete'},
            id='one eats uid with grocery orders',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'ya1', 'is_portal': True},
                    {'uid': 'ya2', 'is_portal': True},
                ],
            },
            'eats',
            {'data_state': 'ready_to_delete'},
            id='multiple uids',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'without_orders_1', 'is_portal': True},
                    {'uid': 'without_orders_2', 'is_portal': True},
                ],
            },
            'eats',
            {'data_state': 'empty'},
            id='multiple missing uids',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'ya1', 'is_portal': True},
                    {'uid': 'without_orders_2', 'is_portal': True},
                ],
            },
            'eats',
            {'data_state': 'ready_to_delete'},
            id='multiple uids mixed',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'yandex_uid-666', 'is_portal': True}],
            },
            'grocery',
            {'data_state': 'empty'},
            id='one uid without grocery orders',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'ya2', 'is_portal': True}],
            },
            'grocery',
            {'data_state': 'ready_to_delete'},
            id='one uid with grocery orders',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'ya1', 'is_portal': True}],
            },
            'grocery',
            {'data_state': 'ready_to_delete'},
            id='grocery orders without uid',
        ),
    ],
)
async def test_takeout_status(
        mockserver,
        taxi_eats_ordershistory,
        request_json,
        response_json,
        data_category,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        assert 'passport_uids' in request.json
        return {'eaters': [], 'pagination': {'limit': 1000, 'has_more': False}}

    response = await taxi_eats_ordershistory.post(
        f'/takeout/v1/status/{data_category}', json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == response_json


@pytest.mark.parametrize(
    'request_json, eater_id',
    [
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'yandex_uid-777', 'is_portal': True}],
            },
            '777',
            id='yandex_uid-777',
        ),
    ],
)
async def test_takeout_delete_fallback_to_eaters(
        mockserver, taxi_eats_ordershistory, pgsql, request_json, eater_id,
):
    uids = tuple([uid['uid'] for uid in request_json['yandex_uids']])

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        assert 'passport_uids' in request.json
        return {
            'eaters': [
                {
                    'personal_phone_id': 'phone_id',
                    'id': eater_id,
                    'uuid': uids[0],
                    'created_at': '2021-06-01T00:00:00+00:00',
                    'updated_at': '2021-06-01T00:00:00+00:00',
                },
            ],
            'pagination': {'limit': 1000, 'has_more': False},
        }

    response = await taxi_eats_ordershistory.post(
        f'/takeout/v1/delete/eats', json=request_json,
    )
    assert response.status_code == 200

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT order_id FROM eats_ordershistory.orders '
        'WHERE eats_user_id = %s;',
        (eater_id,),
    )

    assert not list(cursor)


@pytest.mark.parametrize(
    'request_json, eater_id',
    [
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'yandex_uid-666', 'is_portal': True}],
            },
            '666',
            id='yandex_uid-666',
        ),
    ],
)
async def test_takeout_delete_all_orders_withoutfallback(
        mockserver, taxi_eats_ordershistory, pgsql, request_json, eater_id,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        assert False

    response = await taxi_eats_ordershistory.post(
        f'/takeout/v1/delete/eats', json=request_json,
    )
    assert response.status_code == 200

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT order_id FROM eats_ordershistory.orders '
        'WHERE eats_user_id = %s;',
        (eater_id,),
    )

    assert not list(cursor)
