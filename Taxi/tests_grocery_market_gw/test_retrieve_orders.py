import re
import uuid

import pytest

from tests_grocery_market_gw import models


DEFAULT_HEADERS = {'X-Request-Language': 'ru'}

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        GROCERY_MARKET_GW_ORDER_URL_TEMPLATES={
            'grocery_tracking': 'https://lavka.tracking/{order_id}',
            'eats_tracking': 'https://eats.tracking/{order_id}',
            'grocery_order_info': 'https://lavka.order-info/{order_id}',
            'eats_order_info': 'https://eats.order-info/{order_id}',
        },
    ),
]


async def check_order_paging(
        taxi_grocery_market_gw, yandex_uid, page, count, expected_orders,
):
    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'yandex_uid': yandex_uid,
            'cursor': {'page': page, 'count': count},
        },
    )

    def check_keys(json, expected_values):
        for key, value in expected_values.items():
            assert json[key] == value

    assert response.status == 200
    assert len(response.json()['orders']) == len(expected_orders)
    assert response.json()['total_orders_count'] == 3
    for i, expected_order in enumerate(expected_orders):
        expected_values = {'order_id': expected_order, 'status': 'assembling'}
        check_keys(response.json()['orders'][i], expected_values)


async def test_simple(
        taxi_grocery_market_gw,
        grocery_order_log,
        grocery_orders,
        overlord_catalog,
):
    yandex_uid = 'yandex_uid'

    def get_order_id(i):
        return f'order_id_{i}'

    def get_short_order_id(i):
        return f'short_order_id_{i}'

    overlord_catalog.add_product_data(
        product_id='product_1',
        title='product 1',
        image_url_template='https://image.product/1',
    )

    overlord_catalog.add_product_data(
        product_id='product_2',
        title='product 2',
        image_url_template='https://image.product/2',
    )

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=get_order_id(1),
        short_order_id=get_short_order_id(1),
        status='assembling',
        items=[
            models.Product(
                product_id='product_1', name='product 1', price='3', count=1,
            ),
            models.Product(
                product_id='product_2', name='product 2', price='7', count=2,
            ),
        ],
        price='10',
    )

    for i in range(2, 4):
        grocery_order_log.add_order(
            yandex_uid=yandex_uid,
            order_id=get_order_id(i),
            status='assembling',
            items=[],
            price='0',
        )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': yandex_uid, 'cursor': {'page': 1, 'count': 1}},
    )

    assert response.status == 200
    assert response.json() == {
        'orders': [
            {
                'order_id': get_short_order_id(1),
                'grocery_order_id': get_order_id(1),
                'created': '2020-12-31T21:00:00+00:00',
                'status': 'assembling',
                'total_price': '10',
                'items': [
                    {
                        'item_id': 'product_1',
                        'image_url_template': 'https://image.product/1',
                        'title': 'product 1',
                        'quantity': 1,
                        'price': '3',
                    },
                    {
                        'item_id': 'product_2',
                        'image_url_template': 'https://image.product/2',
                        'title': 'product 2',
                        'quantity': 2,
                        'price': '7',
                    },
                ],
                'order_info_url': (
                    f'https://lavka.order-info/{get_order_id(1)}'
                ),
                'order_tracking_url': (
                    f'https://lavka.tracking/{get_order_id(1)}'
                ),
                'localization': {
                    'order_info_button': 'Детали заказа',
                    'tracking_button': 'Отслеживать заказ',
                    'status': 'Заказ собирается',
                    'status_subtitle': 'Заказ собирается и скоро отправится',
                },
            },
        ],
        'total_orders_count': 3,
    }

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': 'other_yandex_uid'},
    )
    assert response.status == 200
    assert response.json() == {'orders': [], 'total_orders_count': 0}

    all_orders = [get_short_order_id(1), get_order_id(2), get_order_id(3)]
    default_args = {
        'taxi_grocery_market_gw': taxi_grocery_market_gw,
        'yandex_uid': yandex_uid,
    }

    await check_order_paging(
        **default_args, page=1, count=3, expected_orders=all_orders,
    )
    await check_order_paging(
        **default_args, page=1, count=2, expected_orders=all_orders[:-1],
    )
    await check_order_paging(
        **default_args, page=3, count=1, expected_orders=all_orders[2:],
    )
    await check_order_paging(
        **default_args, page=3, count=2, expected_orders=[],
    )


async def test_closed_order(
        taxi_grocery_market_gw, grocery_order_log, grocery_orders,
):
    yandex_uid = 'yandex_uid'
    order_id = 'order_id'
    short_order_id = 'short_order_id'

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        short_order_id=short_order_id,
        status='closed',
        items=[],
        price='10',
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': yandex_uid, 'cursor': {'page': 1, 'count': 1}},
    )

    assert response.status == 200
    assert response.json() == {
        'orders': [
            {
                'order_id': short_order_id,
                'grocery_order_id': order_id,
                'status': 'closed',
                'created': '2020-12-31T21:00:00+00:00',
                'total_price': '10',
                'items': [],
                'order_info_url': f'https://lavka.order-info/{order_id}',
                'localization': {
                    'order_info_button': 'Детали заказа',
                    'status': 'Заказ доставлен',
                },
            },
        ],
        'total_orders_count': 1,
    }


@pytest.mark.parametrize(
    'order_status, eta', [('delivering', 1), ('closed', None)],
)
async def test_merging_with_grocery_orders(
        taxi_grocery_market_gw,
        grocery_order_log,
        grocery_orders,
        order_status,
        eta,
):
    yandex_uid = 'yandex_uid'
    order_id = 'order_id'
    short_order_id = 'short_order_id'

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        short_order_id=short_order_id,
        status='delivering',
        items=[],
        price='0',
    )
    grocery_orders.add_order_state(
        yandex_uid=yandex_uid,
        order_id=order_id,
        short_order_id=short_order_id,
        status=order_status,
        delivery_eta_min=eta,
        cart_id=str(uuid.uuid4()),
        client_price_template='100 $SIGN$$CURRENCY$',
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': yandex_uid, 'cursor': {'page': 1, 'count': 1}},
    )

    assert response.status == 200
    assert response.json()['orders'][0]['status'] == order_status
    if eta:
        assert response.json()['orders'][0]['delivery_eta_min'] == eta


async def test_right_orders_status_and_tracking_url(
        taxi_grocery_market_gw, grocery_order_log, grocery_orders,
):
    yandex_uid = 'yandex_uid'
    order_id = 'order_id'
    short_order_id = 'short_order_id'

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        short_order_id=short_order_id,
        status='delivering',
        items=[],
        price='0',
    )
    grocery_orders.add_order_state(
        yandex_uid=yandex_uid,
        order_id=order_id,
        short_order_id=short_order_id,
        status='closed',
        cart_id=str(uuid.uuid4()),
        client_price_template='100 $SIGN$$CURRENCY$',
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': yandex_uid, 'cursor': {'page': 1, 'count': 1}},
    )

    assert response.status == 200
    assert response.json()['orders'][0]['status'] == 'closed'
    assert 'order_tracking_url' not in response.json()['orders'][0].keys()


async def test_grocery_orders_error(
        taxi_grocery_market_gw, grocery_order_log, grocery_orders,
):
    yandex_uid = 'yandex_uid'
    order_id = 'order_id'
    short_order_id = 'short_order_id'

    grocery_orders.mock_error_response(404)

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        short_order_id=short_order_id,
        status='delivering',
        items=[],
        price='0',
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': yandex_uid, 'cursor': {'page': 1, 'count': 1}},
    )

    assert response.status == 200
    assert response.json()['orders'][0]['status'] == 'delivering'


async def test_order_log_404(
        taxi_grocery_market_gw, grocery_order_log, grocery_orders,
):
    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': '123', 'cursor': {'page': 1, 'count': 1}},
    )
    assert response.status == 200
    assert response.json() == {'orders': [], 'total_orders_count': 0}


@pytest.mark.parametrize(
    'filter_market',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                GROCERY_MARKET_GW_FILTER_MARKET_ORDERS=False,
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                GROCERY_MARKET_GW_FILTER_MARKET_ORDERS=True,
            ),
        ),
    ],
)
async def test_filtering_market_orders(
        taxi_grocery_market_gw,
        grocery_order_log,
        grocery_orders,
        filter_market,
):
    yandex_uid = 'yandex_uid'
    orders = (
        ('order_1', 'lavka'),
        ('order_id_2', 'market'),
        ('order_id_3', None),
        ('000000-000001', 'lavka'),
        ('000000-000002', 'market'),
        ('000000-000002', None),
    )

    for order_id, order_source in orders:
        grocery_order_log.add_order(
            yandex_uid=yandex_uid,
            order_id=order_id,
            short_order_id=order_id,
            status='delivering',
            items=[],
            price='0',
            order_source=order_source,
        )
        if re.match(r'[0-9]{6}-[0-9]{6}', order_id):
            continue
        grocery_orders.add_order_state(
            yandex_uid=yandex_uid,
            order_id=order_id,
            short_order_id=order_id,
            status='delivering',
            cart_id=str(uuid.uuid4()),
            client_price_template='100 $SIGN$$CURRENCY$',
            order_source=order_source,
        )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/retrieve',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': 'yandex_uid', 'cursor': {'page': 1, 'count': 10}},
    )

    assert response.status == 200
    if filter_market:
        assert len(response.json()['orders']) == 2
        assert response.json()['orders'][0]['order_id'] == 'order_id_2'
        assert response.json()['orders'][1]['order_id'] == '000000-000002'
    else:
        assert len(response.json()['orders']) == 6
