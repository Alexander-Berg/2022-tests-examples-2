import pytest


@pytest.mark.parametrize(
    'params',
    [
        # without user indentity
        {},
        # more than one identity
        {'eats_user_id': 123, 'taxi_user_id': '123'},
        {'taxi_user_id': '123', 'yandex_uid': '123'},
        {'eats_user_id': 123, 'yandex_uid': '123'},
        {'eats_user_id': 123, 'taxi_user_id': '123', 'yandex_uid': '123'},
        # wrong types
        {'eats_user_id': '123'},
        {'taxi_user_id': 123},
        {'yandex_uid': 123},
        {'eats_user_id': 123, 'cart': 'false'},
        {'eats_user_id': 123, 'days': '1'},
        {'eats_user_id': 123, 'orders': '1'},
        {'eats_user_id': 123, 'types': 'eda'},
        {'eats_user_id': 123, 'offset': '1'},
    ],
)
async def test_wrong_input(taxi_eats_ordershistory, params):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'params, query',
    [
        (
            {'eats_user_id': 123},
            'SELECT order_id, order_source, eats_user_id, taxi_user_id, '
            'yandex_uid, place_id, status, delivery_location, total_amount, '
            'is_asap, cancel_reason, created_at, delivered_at, flow_type, '
            'order_type, original_total_amount, currency, shipping_type, '
            'delivery_type, last_revision_id, cancelled_at, '
            'ready_to_delivery_at, taken_at '
            'FROM eats_ordershistory.orders '
            'WHERE ((eats_user_id = ANY($1))) '
            'ORDER BY created_at DESC LIMIT $6 OFFSET $7;',
        ),
        (
            {'taxi_user_id': '123'},
            'SELECT order_id, order_source, eats_user_id, taxi_user_id, '
            'yandex_uid, place_id, status, delivery_location, total_amount, '
            'is_asap, cancel_reason, created_at, delivered_at, flow_type, '
            'order_type, original_total_amount, currency, shipping_type, '
            'delivery_type, last_revision_id, cancelled_at, '
            'ready_to_delivery_at, taken_at '
            'FROM eats_ordershistory.orders '
            'WHERE ((taxi_user_id = ANY($2))) '
            'ORDER BY created_at DESC LIMIT $6 OFFSET $7;',
        ),
        (
            {'yandex_uid': '123'},
            'SELECT order_id, order_source, eats_user_id, taxi_user_id, '
            'yandex_uid, place_id, status, delivery_location, total_amount, '
            'is_asap, cancel_reason, created_at, delivered_at, flow_type, '
            'order_type, original_total_amount, currency, shipping_type, '
            'delivery_type, last_revision_id, cancelled_at, '
            'ready_to_delivery_at, taken_at '
            'FROM eats_ordershistory.orders '
            'WHERE ((eats_user_id = ANY($1)) '
            'OR (yandex_uid = ANY($3))) '
            'ORDER BY created_at DESC LIMIT $6 OFFSET $7;',
        ),
        (
            {'eats_user_id': 123, 'orders': 3},
            'SELECT order_id, order_source, eats_user_id, taxi_user_id, '
            'yandex_uid, place_id, status, delivery_location, total_amount, '
            'is_asap, cancel_reason, created_at, delivered_at, flow_type, '
            'order_type, original_total_amount, currency, shipping_type, '
            'delivery_type, last_revision_id, cancelled_at, '
            'ready_to_delivery_at, taken_at '
            'FROM eats_ordershistory.orders '
            'WHERE ((eats_user_id = ANY($1))) '
            'ORDER BY created_at DESC LIMIT $6 OFFSET $7;',
        ),
        (
            {'eats_user_id': 123, 'types': ['native']},
            'SELECT order_id, order_source, eats_user_id, taxi_user_id, '
            'yandex_uid, place_id, status, delivery_location, total_amount, '
            'is_asap, cancel_reason, created_at, delivered_at, flow_type, '
            'order_type, original_total_amount, currency, shipping_type, '
            'delivery_type, last_revision_id, cancelled_at, '
            'ready_to_delivery_at, taken_at '
            'FROM eats_ordershistory.orders '
            'WHERE ((eats_user_id = ANY($1))) '
            'AND (order_type::TEXT = ANY($4)) '
            'ORDER BY created_at DESC LIMIT $6 OFFSET $7;',
        ),
        (
            {'eats_user_id': 123, 'days': 3},
            'SELECT order_id, order_source, eats_user_id, taxi_user_id, '
            'yandex_uid, place_id, status, delivery_location, total_amount, '
            'is_asap, cancel_reason, created_at, delivered_at, flow_type, '
            'order_type, original_total_amount, currency, shipping_type, '
            'delivery_type, last_revision_id, cancelled_at, '
            'ready_to_delivery_at, taken_at '
            'FROM eats_ordershistory.orders '
            'WHERE ((eats_user_id = ANY($1))) '
            'AND (created_at >= $5) '
            'ORDER BY created_at DESC LIMIT $6 OFFSET $7;',
        ),
        (
            {
                'yandex_uid': '123',
                'bound_uids': ['456'],
                'types': ['native'],
                'days': 3,
                'orders': 3,
            },
            'SELECT order_id, order_source, eats_user_id, taxi_user_id, '
            'yandex_uid, place_id, status, delivery_location, total_amount, '
            'is_asap, cancel_reason, created_at, delivered_at, flow_type, '
            'order_type, original_total_amount, currency, shipping_type, '
            'delivery_type, last_revision_id, cancelled_at, '
            'ready_to_delivery_at, taken_at '
            'FROM eats_ordershistory.orders '
            'WHERE ((eats_user_id = ANY($1)) '
            'OR (yandex_uid = ANY($3))) '
            'AND (order_type::TEXT = ANY($4)) '
            'AND (created_at >= $5) '
            'ORDER BY created_at DESC LIMIT $6 OFFSET $7;',
        ),
        (
            {'eats_user_id': 123, 'orders': 1, 'offset': 1},
            'SELECT order_id, order_source, eats_user_id, taxi_user_id, '
            'yandex_uid, place_id, status, delivery_location, total_amount, '
            'is_asap, cancel_reason, created_at, delivered_at, flow_type, '
            'order_type, original_total_amount, currency, shipping_type, '
            'delivery_type, last_revision_id, cancelled_at, '
            'ready_to_delivery_at, taken_at '
            'FROM eats_ordershistory.orders '
            'WHERE ((eats_user_id = ANY($1))) '
            'ORDER BY created_at DESC LIMIT $6 OFFSET $7;',
        ),
    ],
)
@pytest.mark.config(EATS_ORDERSHISTORY_CONVERT_UIDS_ENABLED=True)
async def test_get_query(
        taxi_eats_ordershistory, mockserver, testpoint, params, query,
):
    @mockserver.json_handler('eats-core-eater/find-by-passport-uid')
    def _mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'eater': {
                    'id': '123456',
                    'uuid': '123546',
                    'personal_phone_id': '',
                    'personal_email_id': '',
                    'created_at': '2020-06-23T17:20:00+03:00',
                    'updated_at': '2020-06-23T17:20:00+03:00',
                },
            },
        )
        # return {'eater': {'id': '123456'}}

    @testpoint('get-orders-handler-query')
    def check_query(request):
        assert request == query

    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    assert check_query.times_called == 1


@pytest.mark.parametrize(
    'params',
    [
        # without cart parametrs (default cart should be false)
        {'eats_user_id': 1},
        # with cart params
        {'eats_user_id': 1, 'cart': False},
    ],
)
async def test_without_cart_response(taxi_eats_ordershistory, params):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for order in orders:
        assert 'cart' not in order


@pytest.mark.parametrize(
    'params',
    [
        {'eats_user_id': 1, 'cart': True, 'orders': 1},
        {'eats_user_id': 2, 'cart': True, 'orders': 1},
    ],
)
async def test_has_cart(taxi_eats_ordershistory, params):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for order in orders:
        assert 'cart' in order


@pytest.mark.parametrize(
    'params, expected_source',
    [
        ({'eats_user_id': 1, 'types': ['native']}, 'native'),
        ({'eats_user_id': 1, 'types': ['lavka']}, 'lavka'),
    ],
)
async def test_source(taxi_eats_ordershistory, params, expected_source):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for order in orders:
        assert order['type'] == expected_source


@pytest.mark.parametrize(
    'params, expected_orders_ids_chain',
    [
        ({'eats_user_id': 1, 'days': 1}, ['euid-1', 'euid-3']),
        (
            {'eats_user_id': 1, 'days': 2},
            ['euid-1', 'euid-3', 'euid-4', 'euid-5'],
        ),
        (
            {'eats_user_id': 1, 'days': 3},
            ['euid-1', 'euid-3', 'euid-4', 'euid-5', 'euid-6'],
        ),
        (
            {'eats_user_id': 1, 'days': 10},
            ['euid-1', 'euid-3', 'euid-4', 'euid-5', 'euid-6'],
        ),
    ],
)
@pytest.mark.now('2020-06-15T12:00:00+00:00')
async def test_days(
        taxi_eats_ordershistory, params, expected_orders_ids_chain,
):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == len(expected_orders_ids_chain)
    for index, order in enumerate(orders):
        assert order['order_id'] == expected_orders_ids_chain[index]


@pytest.mark.parametrize(
    'params, expected_orders_ids_chain',
    [
        ({'eats_user_id': 1, 'orders': 1}, ['euid-1']),
        ({'eats_user_id': 1, 'orders': 2}, ['euid-1', 'euid-3']),
        (
            {'eats_user_id': 1, 'orders': 4},
            ['euid-1', 'euid-3', 'euid-4', 'euid-5'],
        ),
        (
            {'eats_user_id': 1, 'orders': 5},
            ['euid-1', 'euid-3', 'euid-4', 'euid-5', 'euid-6'],
        ),
        (
            {'eats_user_id': 1, 'orders': 10},
            ['euid-1', 'euid-3', 'euid-4', 'euid-5', 'euid-6', 'euid-7'],
        ),
        ({'eats_user_id': 1, 'orders': 1, 'offset': 1}, ['euid-3']),
    ],
)
async def test_orders(
        taxi_eats_ordershistory, params, expected_orders_ids_chain,
):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == len(expected_orders_ids_chain)
    for index, order in enumerate(orders):
        assert order['order_id'] == expected_orders_ids_chain[index]


@pytest.mark.parametrize(
    'params, expected_orders_chain',
    [
        (
            {
                'eats_user_id': 3,
                'orders': 1,
                'cart': True,
                'delivery_address': True,
            },
            [
                {
                    'cancel_reason': 'any reason',
                    'cancelled_at': '2020-06-15T11:00:00+00:00',
                    'created_at': '2020-05-06T21:48:44.747+00:00',
                    'currency': 'RUB',
                    'delivered_at': '2020-05-06T22:24:21.747+00:00',
                    'delivery_location': {'lat': 4.56, 'lon': 5.67},
                    'delivery_type': 'native',
                    'is_asap': False,
                    'order_id': 'euid-8',
                    'order_type': 'lavka',
                    'original_total_amount': '100.00',
                    'place_id': 123,
                    'shipping_type': 'delivery',
                    'status': 'taken',
                    'total_amount': '45',
                    'type': 'lavka',
                    'cart': [
                        {
                            'name': 'title-1',
                            'quantity': 4,
                            'origin_id': '3',
                            'catalog_type': 'core_catalog',
                        },
                        {
                            'name': 'title-2',
                            'quantity': 8,
                            'origin_id': '5',
                            'catalog_type': 'core_catalog',
                        },
                    ],
                    'delivery_address': {
                        'full_address': 'address7',
                        'entrance': '29',
                        'floor': '43',
                        'office': '83',
                        'doorcode': '12',
                        'comment': 'comment7',
                    },
                },
            ],
        ),
    ],
)
async def test_orders_content(
        taxi_eats_ordershistory, params, expected_orders_chain,
):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == len(expected_orders_chain)
    for index, order in enumerate(orders):
        assert order == expected_orders_chain[index]


@pytest.mark.parametrize(
    'params, expected_orders_ids_chain',
    [
        ({'eats_user_id': 1, 'orders': 1}, ['euid-1']),
        ({'eats_user_id': 1, 'types': ['native']}, ['euid-1', 'euid-3']),
        ({'eats_user_id': 2, 'days': 1}, ['euid-2']),
        ({'eats_user_id': 2, 'cart': False}, ['euid-2']),
    ],
)
async def test_eats_user_id(
        taxi_eats_ordershistory, params, expected_orders_ids_chain,
):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for index, order in enumerate(orders):
        assert order['order_id'] == expected_orders_ids_chain[index]


@pytest.mark.parametrize(
    'params, expected_orders_ids_chain',
    [
        ({'taxi_user_id': '1', 'days': 1}, ['euid-2']),
        ({'taxi_user_id': '1', 'cart': False}, ['euid-2']),
        ({'taxi_user_id': '2', 'orders': 1}, ['euid-1']),
        ({'taxi_user_id': '2', 'types': ['native']}, ['euid-1', 'euid-3']),
    ],
)
async def test_taxi_user_id(
        taxi_eats_ordershistory, params, expected_orders_ids_chain,
):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for index, order in enumerate(orders):
        assert order['order_id'] == expected_orders_ids_chain[index]


@pytest.mark.parametrize(
    'params, expected_orders_ids_chain',
    [
        ({'yandex_uid': 'ya1'}, ['euid-1', 'euid-3']),
        ({'yandex_uid': 'ya2', 'days': 3}, ['euid-2']),
    ],
)
async def test_yandex_uid(
        taxi_eats_ordershistory, params, expected_orders_ids_chain,
):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for index, order in enumerate(orders):
        assert order['order_id'] == expected_orders_ids_chain[index]


@pytest.mark.parametrize(
    'params',
    [{'yandex_uid': 'ya1', 'orders': 1}, {'yandex_uid': 'ya2', 'orders': 1}],
)
async def test_has_feedback(taxi_eats_ordershistory, params):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for order in orders:
        assert 'feedback' in order


@pytest.mark.parametrize('params', [{'eats_user_id': 1}, {'eats_user_id': 2}])
async def test_has_required_fields(taxi_eats_ordershistory, params):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for order in orders:
        assert 'order_id' in order
        assert 'place_id' in order
        assert 'status' in order
        assert 'delivery_location' in order
        assert 'total_amount' in order
        assert 'is_asap' in order
        assert 'created_at' in order


@pytest.mark.parametrize(
    'request_json, expected_orders_ids, eats_core_responses',
    [
        ({'yandex_uid': 'uid-1'}, ['order-uid-1'], {'uid-1': 'fail'}),
        ({'yandex_uid': 'uid-1'}, ['order-uid-1'], {'uid-1': 'not-found'}),
        (
            {'yandex_uid': 'uid-1'},
            ['order-uid-2', 'order-uid-1'],
            {'uid-1': '1234'},
        ),
        (
            {'yandex_uid': 'uid-1', 'bound_uids': ['uid-2']},
            ['order-uid-3', 'order-uid-1'],
            {'uid-1': 'fail', 'uid-2': 'fail'},
        ),
        (
            {'yandex_uid': 'uid-1', 'bound_uids': ['uid-2']},
            ['order-uid-4', 'order-uid-3', 'order-uid-1'],
            {'uid-1': 'fail', 'uid-2': '12345'},
        ),
        (
            {'yandex_uid': 'uid-1', 'bound_uids': ['uid-2']},
            ['order-uid-3', 'order-uid-2', 'order-uid-1'],
            {'uid-1': '1234', 'uid-2': 'fail'},
        ),
        (
            {'yandex_uid': 'uid-1', 'bound_uids': ['uid-2']},
            ['order-uid-4', 'order-uid-3', 'order-uid-2', 'order-uid-1'],
            {'uid-1': '1234', 'uid-2': '12345'},
        ),
    ],
)
@pytest.mark.config(EATS_ORDERSHISTORY_CONVERT_UIDS_ENABLED=True)
async def test_bound_uids(
        taxi_eats_ordershistory,
        mockserver,
        request_json,
        expected_orders_ids,
        eats_core_responses,
):
    @mockserver.json_handler('eats-core-eater/find-by-passport-uid')
    def _mock(request):
        request_uid = request.json['passport_uid']
        response_id = eats_core_responses[request_uid]

        if response_id == 'fail':
            return mockserver.make_response(status=500)
        if response_id == 'not-found':
            return mockserver.make_response(status=404)

        return mockserver.make_response(
            status=200,
            json={
                'eater': {
                    'id': response_id,
                    'passport_uid': '123546',
                    'uuid': '123546',
                    'personal_phone_id': '',
                    'personal_email_id': '',
                    'created_at': '2020-06-23T17:20:00+03:00',
                    'updated_at': '2020-06-23T17:20:00+03:00',
                },
            },
        )

    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=request_json,
    )
    assert response.status_code == 200
    response_order_ids = [o['order_id'] for o in response.json()['orders']]
    assert response_order_ids == expected_orders_ids


@pytest.mark.parametrize(
    'params, expected_delivery_address',
    [
        (
            {
                'eats_user_id': 3,
                'orders': 1,
                'cart': False,
                'delivery_address': True,
            },
            {
                'full_address': 'address7',
                'entrance': '29',
                'floor': '43',
                'office': '83',
                'doorcode': '12',
                'comment': 'comment7',
            },
        ),
        (
            {
                'eats_user_id': 1234,
                'orders': 1,
                'cart': False,
                'delivery_address': True,
                'types': ['lavka'],
            },
            {},
        ),
        (
            {
                'eats_user_id': 1234,
                'orders': 1,
                'cart': False,
                'delivery_address': True,
                'types': ['native'],
            },
            {'comment': 'comment8'},
        ),
    ],
)
async def test_delivery_address(
        taxi_eats_ordershistory, params, expected_delivery_address,
):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['delivery_address'] == expected_delivery_address


@pytest.mark.parametrize(
    'params',
    [
        # without delivery_address parameters
        # (default delivery_address should be false)
        {'eats_user_id': 1},
        # with delivery_address params
        {'eats_user_id': 1, 'delivery_address': False},
    ],
)
async def test_without_delivery_address_response(
        taxi_eats_ordershistory, params,
):
    response = await taxi_eats_ordershistory.post(
        '/v2/get-orders', json=params,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    for order in orders:
        assert 'delivery_address' not in order
