import uuid

import pytest

from tests_grocery_market_gw import models


DEFAULT_HEADERS = {'X-Request-Language': 'ru'}


@pytest.mark.config(
    GROCERY_MARKET_GW_ORDER_URL_TEMPLATES={
        'grocery_tracking': 'https://lavka.tracking/{order_id}',
        'eats_tracking': 'https://eats.tracking/{order_id}',
        'grocery_order_info': 'https://lavka.order-info/{order_id}',
        'eats_order_info': 'https://eats.order-info/{order_id}',
    },
)
async def test_simple(
        taxi_grocery_market_gw,
        overlord_catalog,
        grocery_orders,
        grocery_cart,
        grocery_order_log,
):
    overlord_catalog.add_product_data(
        product_id='product_id_1',
        title='Product 1',
        image_url_template='https://image.product/1',
    )

    overlord_catalog.add_product_data(
        product_id='product_id_2',
        title='Product 2',
        image_url_template='https://image.product/2',
    )

    cart_id_1 = str(uuid.uuid4())
    grocery_orders.add_order_state(
        yandex_uid='yandex_uid_1',
        order_id='order_id_1',
        short_order_id='short_order_id_1',
        status='delivering',
        delivery_eta_min=1,
        cart_id=cart_id_1,
        client_price_template='100 $SIGN$$CURRENCY$',
    )

    cart_id_2 = str(uuid.uuid4())
    grocery_orders.add_order_state(
        yandex_uid='yandex_uid_1',
        order_id='order_id_2',
        short_order_id='short_order_id_2',
        status='delivering',
        delivery_eta_min=2,
        cart_id=cart_id_2,
        client_price_template='300 $SIGN$$CURRENCY$',
    )

    cart = grocery_cart.add_cart(cart_id_1)
    cart.set_client_price('100')
    cart.set_items(
        [
            models.GroceryCartItem(
                item_id='product_id_1',
                title='Product 1',
                quantity='1',
                price='100',
            ),
        ],
    )

    cart = grocery_cart.add_cart(cart_id_2)
    cart.set_client_price('300')
    cart.set_items(
        [
            models.GroceryCartItem(
                item_id='product_id_1',
                title='Product 1',
                quantity='1',
                price='100',
            ),
            models.GroceryCartItem(
                item_id='product_id_2',
                title='Product 2',
                quantity='2',
                price='200',
            ),
        ],
    )

    eats_order_id = '000000-000001'
    grocery_order_log.add_order(
        yandex_uid='yandex_uid_1',
        order_id=eats_order_id,
        status='assembling',
        items=[
            models.Product(
                product_id='product_id_1',
                name='Product 1',
                price='170',
                count=1,
            ),
        ],
        price='170',
    )
    grocery_order_log.add_order(
        yandex_uid='yandex_uid_1',
        order_id='grocery_order_id',
        status='assembling',
        items=[
            models.Product(
                product_id='product_id_1',
                name='Product 1',
                price='0',
                count=1,
            ),
        ],
        price='0',
    )

    # this orders shound not present in response
    grocery_order_log.add_order(
        yandex_uid='yandex_uid_1',
        order_id='000000-000002',
        status='closed',
        items=[
            models.Product(
                product_id='product_id_1',
                name='Product 1',
                price='0',
                count=1,
            ),
        ],
        price='0',
    )
    grocery_order_log.add_order(
        yandex_uid='yandex_uid_1',
        order_id='000000-000003',
        status='canceled',
        items=[
            models.Product(
                product_id='product_id_1',
                name='Product 1',
                price='0',
                count=1,
            ),
        ],
        price='0',
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/current',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': 'yandex_uid_1'},
    )

    assert response.status == 200
    assert response.json() == {
        'orders': [
            {
                'order_id': 'short_order_id_1',
                'grocery_order_id': 'order_id_1',
                'delivery_eta_min': 1,
                'status': 'delivering',
                'total_price': '100',
                'items': [
                    {
                        'item_id': 'product_id_1',
                        'image_url_template': 'https://image.product/1',
                        'title': 'Product 1',
                        'quantity': 1,
                        'price': '100',
                    },
                ],
                'order_info_url': 'https://lavka.order-info/order_id_1',
                'order_tracking_url': 'https://lavka.tracking/order_id_1',
                'localization': {
                    'order_info_button': 'Детали заказа',
                    'status': (
                        'Заказ доставляется и будет у вас через 1 минуту'
                    ),
                    'status_subtitle': 'Курьер уже рядом',
                    'tracking_button': 'Отслеживать заказ',
                },
            },
            {
                'order_id': 'short_order_id_2',
                'grocery_order_id': 'order_id_2',
                'delivery_eta_min': 2,
                'status': 'delivering',
                'total_price': '300',
                'items': [
                    {
                        'item_id': 'product_id_1',
                        'image_url_template': 'https://image.product/1',
                        'title': 'Product 1',
                        'quantity': 1,
                        'price': '100',
                    },
                    {
                        'item_id': 'product_id_2',
                        'image_url_template': 'https://image.product/2',
                        'title': 'Product 2',
                        'quantity': 2,
                        'price': '200',
                    },
                ],
                'order_info_url': f'https://lavka.order-info/order_id_2',
                'order_tracking_url': f'https://lavka.tracking/order_id_2',
                'localization': {
                    'order_info_button': 'Детали заказа',
                    'status': (
                        'Заказ доставляется и будет у вас через 2 минуты'
                    ),
                    'status_subtitle': 'Курьер уже рядом',
                    'tracking_button': 'Отслеживать заказ',
                },
            },
            {
                'order_id': eats_order_id,
                'grocery_order_id': eats_order_id,
                'status': 'assembling',
                'created': '2020-12-31T21:00:00+00:00',
                'total_price': '170',
                'items': [
                    {
                        'item_id': 'product_id_1',
                        'image_url_template': 'https://image.product/1',
                        'title': 'Product 1',
                        'quantity': 1,
                        'price': '170',
                    },
                ],
                'order_info_url': f'https://eats.order-info/{eats_order_id}',
                'order_tracking_url': f'https://eats.tracking/{eats_order_id}',
                'localization': {
                    'order_info_button': 'Детали заказа',
                    'status': 'Заказ собирается',
                    'status_subtitle': 'Заказ собирается и скоро отправится',
                    'tracking_button': 'Отслеживать заказ',
                },
            },
        ],
    }

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/current',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': 'yandex_uid_2'},
    )
    assert response.status == 200
    assert not response.json()['orders']


async def test_deliverng_order_without_eta(
        taxi_grocery_market_gw, grocery_order_log, grocery_orders,
):
    eats_order_id = '000000-000001'

    grocery_order_log.add_order(
        yandex_uid='yandex_uid_1',
        order_id=eats_order_id,
        status='delivering',
        items=[],
        price='0',
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/current',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': 'yandex_uid_1'},
    )
    assert response.status == 200
    assert (
        response.json()['orders'][0]['localization']['status']
        == 'Заказ доставляется'
    )


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
        grocery_cart,
        filter_market,
):
    for order_id, order_source in (
            ('order_id_1', 'market'),
            ('order_id_2', 'web'),
            ('order_id_3', None),
    ):
        cart_id = str(uuid.uuid4())
        grocery_orders.add_order_state(
            yandex_uid='yandex_uid',
            order_id=order_id,
            short_order_id=order_id,
            status='assembled',
            cart_id=cart_id,
            client_price_template='100 $SIGN$$CURRENCY$',
            order_source=order_source,
        )
        cart = grocery_cart.add_cart(cart_id)
        cart.set_client_price('200')
        cart.set_items([])

    for order_id, order_source in (
            ('000000-000001', 'lavka'),
            ('000000-000002', 'market'),
            ('000000-000003', None),
    ):
        grocery_order_log.add_order(
            yandex_uid='yandex_uid',
            order_id=order_id,
            status='delivering',
            items=[],
            price='0',
            order_source=order_source,
        )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/orders/current',
        headers=DEFAULT_HEADERS,
        json={'yandex_uid': 'yandex_uid'},
    )

    assert response.status == 200
    if filter_market:
        assert grocery_cart.retrieve_times_called() == 1
        assert len(response.json()['orders']) == 2
        assert response.json()['orders'][0]['order_id'] == 'order_id_1'
        assert response.json()['orders'][0]['grocery_order_id'] == 'order_id_1'
        assert response.json()['orders'][1]['order_id'] == '000000-000002'
        assert (
            response.json()['orders'][1]['grocery_order_id'] == '000000-000002'
        )

    else:
        assert grocery_cart.retrieve_times_called() == 3
        assert len(response.json()['orders']) == 6
