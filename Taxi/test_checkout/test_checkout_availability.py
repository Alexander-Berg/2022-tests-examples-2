import pytest

from tests_grocery_cart import common
from tests_grocery_cart.plugins import keys

EXISTING_CART_ID = '8da556be-0971-4f3b-a454-d980130662cc'
DEFAULT_IDEMPOTENCY_TOKEN = 'checkout-token'
BASIC_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Request-Language': 'en',
    'X-Request-Application': 'app_name=android',
}


@pytest.mark.pgsql('grocery_cart', files=['taxi_one_item.sql'])
async def test_price_changed(taxi_grocery_cart, overlord_catalog):
    catalog_price = '400'
    overlord_catalog.add_product(product_id='item_id_1', price=catalog_price)

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers={
            'X-Idempotency-Token': DEFAULT_IDEMPOTENCY_TOKEN,
            **BASIC_HEADERS,
        },
        json={
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': EXISTING_CART_ID,
            'cart_version': 1,
        },
    )

    assert response.status_code == 200
    response_json = response.json()

    assert not response_json['available_for_checkout']
    assert not response_json['checkout_unavailable_reason'] == 'invalid-price'

    assert response_json['items'][0]['price'] == '345'
    assert response_json['items'][0]['catalog_price'] == catalog_price


async def test_quantity_over_limit(cart, overlord_catalog):
    overlord_catalog.add_product(
        product_id='item_id_1', price='345', in_stock='1',
    )
    response = await cart.modify({'item_id_1': {'q': 2, 'p': 345}})
    assert not response['available_for_checkout']
    assert response['checkout_unavailable_reason'] == 'quantity-over-limit'


async def test_no_product_in_overlord(cart, overlord_catalog):
    overlord_catalog.add_product(
        product_id='item_id_1', price='345', in_stock='1',
    )

    await cart.modify({'item_id_1': {'q': 1, 'p': 345}})

    overlord_catalog.remove_product(product_id='item_id_1')

    response = await cart.retrieve()
    assert not response['available_for_checkout']
    assert response['checkout_unavailable_reason'] == 'quantity-over-limit'


@pytest.mark.skipif(
    True, reason='diff data for delivery steps has been removed',
)
@pytest.mark.parametrize('accept_delivery_cost', (True, False))
@pytest.mark.parametrize(
    'previous_delivery,actual_delivery',
    [
        pytest.param(
            {'cost': '200', 'next_threshold': '400', 'next_cost': '100'},
            {'cost': '400', 'next_threshold': '400', 'next_cost': '300'},
            id='delivery cost increased',
        ),
        pytest.param(
            {'cost': '200', 'next_threshold': '400', 'next_cost': '100'},
            {'cost': '100', 'next_threshold': '400', 'next_cost': '300'},
            id='delivery cost decreased',
        ),
    ],
)
async def test_delivery_changed_retrieve(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        accept_delivery_cost,
        previous_delivery,
        actual_delivery,
        offers,
        experiments3,
        grocery_surge,
):
    overlord_catalog.add_product(product_id='item_id_1')

    await cart.modify(['item_id_1'])

    if accept_delivery_cost:
        await cart.accept_delivery_cost(previous_delivery['cost'])

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        delivery=actual_delivery,
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers={
            'X-Idempotency-Token': DEFAULT_IDEMPOTENCY_TOKEN,
            **BASIC_HEADERS,
        },
        json={
            'position': cart.position,
            'cart_id': cart.cart_id,
            'offer_id': cart.offer_id,
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['available_for_checkout'] is False
    assert response_json['checkout_unavailable_reason'] == 'delivery-cost'


@pytest.mark.skipif(
    True, reason='diff data for delivery steps has been removed',
)
@pytest.mark.parametrize('accept_delivery_cost', (True, False))
@pytest.mark.parametrize(
    'previous_delivery,actual_delivery',
    [
        pytest.param(
            {'cost': '200', 'next_threshold': '400', 'next_cost': '100'},
            {'cost': '400', 'next_threshold': '400', 'next_cost': '300'},
            id='delivery cost increased',
        ),
        pytest.param(
            {'cost': '200', 'next_threshold': '400', 'next_cost': '100'},
            {'cost': '100', 'next_threshold': '400', 'next_cost': '300'},
            id='delivery cost descreased',
        ),
    ],
)
async def test_delivery_changed_checkout(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        accept_delivery_cost,
        previous_delivery,
        actual_delivery,
        offers,
        experiments3,
        grocery_surge,
):
    overlord_catalog.add_product(product_id='item_id_1')

    await cart.modify(['item_id_1'])

    if accept_delivery_cost:
        await cart.accept_delivery_cost(previous_delivery['cost'])

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        delivery=actual_delivery,
    )

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout',
        headers={
            'X-Idempotency-Token': DEFAULT_IDEMPOTENCY_TOKEN,
            **BASIC_HEADERS,
        },
        json={
            'position': cart.position,
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['checkout_unavailable_reason'] == 'delivery-cost'
