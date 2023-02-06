import pytest

from tests_eats_orders_info import utils


ORDERSHISTORY_URL = '/eats-ordershistory/internal/v2/get-orders/list'


@pytest.mark.parametrize(
    'order_nr',
    [
        pytest.param('123-123', id='is_not_removed_order'),
        pytest.param('124-124', id='is_removed_order'),
        pytest.param('100-100', id='unknown_yet_order'),
    ],
)
@pytest.mark.pgsql('eats_orders_info', files=['default_database.sql'])
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
async def test_remove_order_green_flow(
        taxi_eats_orders_info,
        taxi_eats_orders_info_monitor,
        pg_realdict_cursor,
        mockserver,
        order_nr,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def mock_orders(request):
        assert request.method == 'POST'
        assert 'order_ids' in request.json['filters']
        assert 'eater_ids' in request.json['filters']
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    {
                        'order_id': order_nr,
                        'place_id': 123,
                        'status': 'finished',
                        'order_type': 'native',
                        'delivery_location': {'lat': 1, 'lon': 1},
                        'total_amount': '123',
                        'is_asap': True,
                        'created_at': '2020-04-28T12:00:00+03:00',
                    },
                ],
            },
        )

    response = await taxi_eats_orders_info.post(
        '/eats/v1/orders-info/v1/remove-order',
        headers=utils.get_auth_headers(eater_id='21'),
        json={'order_nr': order_nr},
    )
    assert mock_orders.times_called == 1
    assert response.status_code == 200

    assert await utils.db_check_orders_removed_dict(
        pg_realdict_cursor, [order_nr],
    ) == {'order_nr': order_nr}

    metrics = await taxi_eats_orders_info_monitor.get_metric(
        'eats-orders-info-metrics',
    )
    assert metrics['removed_orders'] == 1
    await taxi_eats_orders_info.tests_control(reset_metrics=True)


async def test_remove_order_400(taxi_eats_orders_info):
    response = await taxi_eats_orders_info.post(
        '/eats/v1/orders-info/v1/remove-order',
        headers=utils.get_auth_headers(),
        json={'order_nr': 111},
    )
    assert response.status_code == 400


async def test_remove_order_401(taxi_eats_orders_info):
    response = await taxi_eats_orders_info.post(
        '/eats/v1/orders-info/v1/remove-order', json={'order_nr': '111'},
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'ordershistory_body, ordershistory_code, expected_body, expected_code',
    [
        pytest.param(
            {'orders': []},
            200,
            {'message': 'Заказ не найден', 'code': 'not_found'},
            404,
            id='not_found_order',
        ),
        pytest.param(
            {
                'orders': [
                    {
                        'order_id': '127-127',
                        'place_id': 123,
                        # active order
                        'status': 'confirmed',
                        'order_type': 'native',
                        'delivery_location': {'lat': 1, 'lon': 1},
                        'total_amount': '123',
                        'is_asap': True,
                        'created_at': '2020-04-28T12:00:00+03:00',
                    },
                ],
            },
            200,
            {
                'message': 'Этот заказ нельзя удалить',
                'code': 'cant_be_removed',
            },
            400,
            id='cant_remove_order',
        ),
    ],
)
@pytest.mark.pgsql('eats_orders_info', files=['default_database.sql'])
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
async def test_ordershistory_responses(
        taxi_eats_orders_info,
        mockserver,
        pg_realdict_cursor,
        ordershistory_body,
        ordershistory_code,
        expected_body,
        expected_code,
):
    order_nr = '127-127'

    @mockserver.json_handler(ORDERSHISTORY_URL)
    def mock_eater_order(request):
        assert request.method == 'POST'
        assert 'order_ids' in request.json['filters']
        assert 'eater_ids' in request.json['filters']
        return mockserver.make_response(
            status=ordershistory_code, json=ordershistory_body,
        )

    response = await taxi_eats_orders_info.post(
        '/eats/v1/orders-info/v1/remove-order',
        headers=utils.get_auth_headers(eater_id='21'),
        json={'order_nr': order_nr},
    )
    assert mock_eater_order.times_called == 1
    assert response.status_code == expected_code
    assert response.json() == expected_body

    assert not await utils.db_check_orders_removed_dict(
        pg_realdict_cursor, [order_nr],
    )


@pytest.mark.parametrize(
    'input_order_nrs, expected_order_nrs',
    [
        pytest.param([], [], id='empty_input'),
        pytest.param(['121-121', '122-122'], [], id='not_removed_orders'),
        pytest.param(
            ['122-122', '123-123', '127-127'],
            ['123-123', '127-127'],
            id='parlty_removed_orders',
        ),
        pytest.param(
            ['125-125', '126-126', '127-127'],
            ['125-125', '126-126', '127-127'],
            id='full_removed_orders',
        ),
    ],
)
@pytest.mark.pgsql('eats_orders_info', files=['check_removed_orders.sql'])
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
async def test_check_orders_removed(
        taxi_eats_orders_info, input_order_nrs, expected_order_nrs,
):
    response = await taxi_eats_orders_info.post(
        '/internal/orders-info/v1/check-orders-removed',
        json={'order_nrs': input_order_nrs},
    )
    assert response.status_code == 200
    assert response.json() == {'removed_order_nrs': expected_order_nrs}


@pytest.mark.pgsql('eats_orders_info', files=['check_removed_orders.sql'])
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
async def test_check_orders_removed_400(taxi_eats_orders_info):
    response = await taxi_eats_orders_info.post(
        '/internal/orders-info/v1/check-orders-removed',
        json={'bad_order_nrs': []},
    )
    assert response.status_code == 400
