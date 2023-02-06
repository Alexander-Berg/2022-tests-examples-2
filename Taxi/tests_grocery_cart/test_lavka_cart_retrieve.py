import pytest

from tests_grocery_cart import common
from tests_grocery_cart.plugins import keys

DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'eats:123',
    'X-YaTaxi-User': 'eats_user_id=12345',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}
DELIVERY_SKIP = pytest.mark.skipif(
    True, reason='diff data for delivery steps has been removed',
)


async def test_not_found(taxi_grocery_cart):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': 'ffffffff-ffff-40ff-ffff-ffffffffffff',
            'offer_id': 'offer_id',
        },
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'catalog_price,exp_reasons,surge_minimum_order,sum_to_min_order,diff_data',
    [
        ('345', {'available_for_checkout': True}, '300', '0', {}),
        (
            '400',
            {
                'available_for_checkout': False,
                'checkout_unavailable_reason': 'price-mismatch',
            },
            '500',
            '100',
            {
                'products': [
                    {
                        'price': {
                            'actual_template': '400 $SIGN$$CURRENCY$',
                            'diff_template': '55 $SIGN$$CURRENCY$',
                            'previous_template': '345 $SIGN$$CURRENCY$',
                            'trend': 'increase',
                        },
                        'product_id': 'item_id_1',
                    },
                ],
                'cart_total': {
                    'actual_template': '400 $SIGN$$CURRENCY$',
                    'diff_template': '55 $SIGN$$CURRENCY$',
                    'previous_template': '345 $SIGN$$CURRENCY$',
                    'trend': 'increase',
                },
            },
        ),
    ],
)
@pytest.mark.now(keys.TS_NOW)
async def test_basic(
        taxi_grocery_cart,
        catalog_price,
        exp_reasons,
        surge_minimum_order,
        sum_to_min_order,
        diff_data,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
):
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=keys.CREATED_OFFER_ID,
        offer_time=keys.TS_NOW,
        minimum_order=surge_minimum_order,
        is_surge=True,
        delivery={'cost': '0', 'next_threshold': '99999', 'next_cost': '0'},
    )
    item_id = 'item_id_1'
    overlord_catalog.add_product(product_id=item_id, price=catalog_price)

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'offer_id': keys.CREATED_OFFER_ID,
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('next_idempotency_token')
    response_json.pop('reward_block')
    assert response_json == {
        'available_delivery_types': ['eats_dispatch'],
        'total_price_template': f'{catalog_price} $SIGN$$CURRENCY$',
        'total_price_no_delivery_template': (
            f'{catalog_price} $SIGN$$CURRENCY$'
        ),
        'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
        'cart_version': 1,
        'delivery_type': 'eats_dispatch',
        'depot': {
            'status': 'available',
            'switch_time': '2020-03-13T21:00:00+00:00',
        },
        'is_surge': True,
        'items': [
            {
                'currency': 'RUB',
                'id': item_id,
                'price': '345',
                'title': f'title for {item_id}',
                'subtitle': f'subtitle for {item_id}',
                'image_url_template': f'url for {item_id}',
                'image_url_templates': [f'url for {item_id}'],
                'catalog_price': catalog_price,
                'catalog_price_template': f'{catalog_price} $SIGN$$CURRENCY$',
                'catalog_total_price_template': (
                    f'{catalog_price} $SIGN$$CURRENCY$'
                ),
                'quantity': '1',
                'quantity_limit': '100',
                'restrictions': [],
            },
        ],
        'offer_id': 'created_offer_id',
        'l10n': {
            'market_promocode_unavailable': (
                'Промокоды, выданные в Маркете не '
                'распространяются на заказы в Лавке'
            ),
        },
        'valid_until': '2020-02-06T13:33:54.827958+00:00',
        'requirements': {
            'sum_to_min_order': sum_to_min_order,
            'sum_to_min_order_template': _to_template(sum_to_min_order),
        },
        **exp_reasons,
        'order_conditions': {
            'delivery_cost': '0',
            'delivery_cost_template': '0 $SIGN$$CURRENCY$',
            'minimum_order_price': surge_minimum_order,
            'minimum_order_price_template': _to_template(surge_minimum_order),
        },
        'diff_data': diff_data,
        'order_flow_version': 'eats_core',
        'currency_sign': '₽',
    }
    assert overlord_catalog.times_called() == 1


@pytest.mark.parametrize(
    'catalog_price,cur_surge,prev_surge,diff_data',
    [
        (
            '400',  # catalog_price
            '100',  # cur_surge
            '500',  # prev_surge
            {
                'products': [
                    {
                        'price': {
                            'actual_template': '400 $SIGN$$CURRENCY$',
                            'diff_template': '55 $SIGN$$CURRENCY$',
                            'previous_template': '345 $SIGN$$CURRENCY$',
                            'trend': 'increase',
                        },
                        'product_id': 'item_id_1',
                    },
                ],
                'minimum_order': {
                    'actual_template': '100 $SIGN$$CURRENCY$',
                    'diff_template': '400 $SIGN$$CURRENCY$',
                    'previous_template': '500 $SIGN$$CURRENCY$',
                    'trend': 'decrease',
                },
                'cart_total': {
                    'actual_template': '400 $SIGN$$CURRENCY$',
                    'diff_template': '55 $SIGN$$CURRENCY$',
                    'previous_template': '345 $SIGN$$CURRENCY$',
                    'trend': 'increase',
                },
            },
        ),
    ],
)
@pytest.mark.now(keys.TS_NOW)
@pytest.mark.skipif(True, reason='No min_order diff in native surge')
async def test_diff(
        taxi_grocery_cart,
        catalog_price,
        cur_surge,
        prev_surge,
        diff_data,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
):
    item_id = 'item_id_1'
    overlord_catalog.add_product(product_id=item_id, price=catalog_price)
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        minimum_order=prev_surge,
        offer_id=keys.CREATED_OFFER_ID,
        offer_time=keys.TS_NOW,
        delivery={'cost': '0', 'next_cost': '0', 'next_threshold': '99999'},
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'offer_id': keys.CREATED_OFFER_ID,
        },
    )
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        minimum_order=cur_surge,
        offer_id=keys.CREATED_OFFER_ID,
        offer_time=keys.TS_NOW,
        delivery={'cost': '0', 'next_cost': '0', 'next_threshold': '99999'},
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'offer_id': keys.CREATED_OFFER_ID,
        },
    )
    assert response.status_code == 200
    assert response.json()['diff_data'] == diff_data


@DELIVERY_SKIP
@pytest.mark.parametrize('accept_delivery_cost', (True, False))
@pytest.mark.parametrize(
    'prev_delivery_cost,cur_delivery_cost', [('200', '100')],
)
async def test_diff_delivery(
        taxi_grocery_cart,
        cart,
        accept_delivery_cost,
        prev_delivery_cost,
        cur_delivery_cost,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
):
    item_id = 'item_id_1'
    price = '345'
    prev_delivery = {
        'cost': prev_delivery_cost,
        'next_cost': '100',
        'next_threshold': '400',
    }
    cur_delivery = {
        'cost': cur_delivery_cost,
        'next_cost': '100',
        'next_threshold': '400',
    }

    cart.cart_id = '8da556be-0971-4f3b-a454-d980130662cc'
    cart.cart_version = 1

    overlord_catalog.add_product(product_id=item_id, price=price)

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id_1',
        delivery=prev_delivery,
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'position': cart.position,
            'cart_id': cart.cart_id,
            'offer_id': cart.offer_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['diff_data'] == {}

    if accept_delivery_cost:
        await cart.accept_delivery_cost(
            prev_delivery_cost,
            headers={
                'X-Idempotency-Token': (
                    common.APPLY_PROMOCODE_IDEMPOTENCY_TOKEN
                ),
                **DEFAULT_HEADERS,
            },
        )
        prev_delivery = None

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id_2',
        delivery=cur_delivery,
        minimum_order='100',
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'position': cart.position,
            'cart_id': cart.cart_id,
            'offer_id': cart.offer_id,
        },
    )

    diff = abs(int(cur_delivery_cost) - int(prev_delivery_cost))
    actual_cart_total = int(cur_delivery_cost) + int(price)
    prev_cart_total = int(prev_delivery_cost) + int(price)

    assert response.status_code == 200
    assert response.json()['diff_data'] == {
        'delivery_cost': {
            'actual_template': _to_template(cur_delivery_cost),
            'diff_template': _to_template(diff),
            'previous_template': _to_template(prev_delivery_cost),
            'trend': _trend(prev=prev_delivery_cost, actual=cur_delivery_cost),
        },
        'cart_total': {
            'actual_template': _to_template(actual_cart_total),
            'diff_template': _to_template(diff),
            'previous_template': _to_template(prev_cart_total),
            'trend': _trend(prev=prev_cart_total, actual=actual_cart_total),
        },
    }


@pytest.mark.parametrize('item_price', [200, 400])
@pytest.mark.now(keys.TS_NOW)
async def test_requirements(
        taxi_grocery_cart,
        overlord_catalog,
        item_price,
        offers,
        experiments3,
        grocery_surge,
):
    min_order = 300
    next_delivery_threshold = 500
    delivery_cost = 100
    next_delivery_cost = 50

    delivery = {
        'cost': str(delivery_cost),
        'next_cost': str(next_delivery_cost),
        'next_threshold': str(next_delivery_threshold),
    }

    overlord_catalog.add_product(product_id='item_id_1', price=str(item_price))
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id_1',
        offer_time=keys.TS_NOW,
        delivery=delivery,
        minimum_order=str(min_order),
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'offer_id': 'offer_id',
        },
    )

    assert response.status_code == 200

    if min_order > item_price:
        assert response.json()['requirements'] == {
            'next_delivery_cost': str(delivery_cost),
            'next_delivery_cost_template': _to_template(delivery_cost),
            'next_delivery_threshold': str(min_order),
            'next_delivery_threshold_template': _to_template(min_order),
            'sum_to_min_order': str(min_order - item_price),
            'sum_to_min_order_template': _to_template(min_order - item_price),
            'sum_to_next_delivery': str(min_order - item_price),
            'sum_to_next_delivery_template': _to_template(
                min_order - item_price,
            ),
        }
    else:
        assert response.json()['requirements'] == {
            'next_delivery_cost': str(next_delivery_cost),
            'next_delivery_cost_template': _to_template(next_delivery_cost),
            'next_delivery_threshold': str(next_delivery_threshold),
            'next_delivery_threshold_template': _to_template(
                next_delivery_threshold,
            ),
            'sum_to_min_order': '0',
            'sum_to_min_order_template': '0 $SIGN$$CURRENCY$',
            'sum_to_next_delivery': str(next_delivery_threshold - item_price),
            'sum_to_next_delivery_template': _to_template(
                next_delivery_threshold - item_price,
            ),
        }


@DELIVERY_SKIP
async def test_cart_total_diff(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
):
    item_id = 'item_id'
    prev_quantity = 10
    actual_limit = 5
    prev_price = 50
    actual_price = 100
    prev_delivery_cost = 200
    actual_delivery_cost = 100
    next_delivery_threshold = 10000
    next_delivery_cost = 50

    delivery = {
        'cost': str(actual_delivery_cost),
        'next_cost': str(next_delivery_cost),
        'next_threshold': str(next_delivery_threshold),
    }

    overlord_catalog.add_product(product_id=item_id, price=str(prev_price))
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id_1',
        delivery=delivery,
    )

    await cart.modify(
        {item_id: {'p': str(prev_price), 'q': str(prev_quantity)}},
    )

    overlord_catalog.add_product(
        product_id=item_id,
        price=str(actual_price),
        in_stock=str(actual_limit),
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=common.TAXI_HEADERS,
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': cart.cart_id,
            'offer_id': 'offer_id',
        },
    )

    assert response.status_code == 200
    cart_total_diff = response.json()['diff_data']['cart_total']

    actual_cart_total = actual_price * actual_limit + actual_delivery_cost
    prev_cart_total = prev_quantity * prev_price + prev_delivery_cost
    diff = abs(prev_cart_total - actual_cart_total)

    assert cart_total_diff == {
        'actual_template': _to_template(actual_cart_total),
        'diff_template': _to_template(diff),
        'previous_template': _to_template(prev_cart_total),
        'trend': _trend(prev=prev_cart_total, actual=actual_cart_total),
    }


@pytest.mark.now(keys.TS_NOW)
async def test_master_categories_passed_to_discounts(
        mockserver, taxi_grocery_cart, overlord_catalog,
):
    master_categories = ['master_category1', 'master_category2']

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def _discount_modifiers(request):
        assert (
            request.json['items'][0]['master_categories'] == master_categories
        )
        return {'modifiers': []}

    item_id = 'item_id_1'

    overlord_catalog.add_product(
        product_id=item_id, master_categories=master_categories,
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=DEFAULT_HEADERS,
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'offer_id': keys.CREATED_OFFER_ID,
        },
    )
    assert response.status_code == 200
    assert _discount_modifiers.times_called == 1


def _trend(*, prev, actual):
    if int(prev) < int(actual):
        return 'increase'
    return 'decrease'


def _to_template(price):
    return f'{str(price)} $SIGN$$CURRENCY$'
