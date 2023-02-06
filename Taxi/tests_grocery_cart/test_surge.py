import pytest

from tests_grocery_cart import common
from tests_grocery_cart.plugins import keys


EXISTING_CART_ID = '8da556be-0971-4f3b-a454-d980130662cc'
DEFAULT_IDEMPOTENCY_TOKEN = 'checkout-token'
BASIC_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}


@pytest.mark.parametrize(
    'offer_data,expected_unavailable_reason',
    [
        ({'is_surge': False}, 'checkedout'),
        ({'minimum_order': '300', 'is_surge': True}, 'checkedout'),
        ({'minimum_order': '500', 'is_surge': True}, 'minimum-price'),
        (
            {
                'previous_minimum_order': '300',
                'minimum_order': '500',
                'is_surge': True,
            },
            'minimum-price',
        ),
        (
            {
                'previous_minimum_order': '500',
                'minimum_order': '300',
                'is_surge': True,
            },
            'checkedout',
        ),
    ],
)
@pytest.mark.pgsql('grocery_cart', files=['taxi_one_item.sql'])
@pytest.mark.now(keys.TS_NOW)
async def test_surge(
        taxi_grocery_cart,
        overlord_catalog,
        mockserver,
        offer_data,
        expected_unavailable_reason,
        grocery_surge,
        offers,
        umlaas_eta,
        experiments3,
):
    overlord_catalog.add_product(
        product_id='item_id_1', price='345', in_stock='10',
    )

    if offer_data:
        delivery = {'cost': '100', 'next_cost': '0', 'next_threshold': '400'}
        minimum_order = None
        if 'minimum_order' in offer_data:
            minimum_order = offer_data['minimum_order']
        common.create_offer(
            offers,
            experiments3,
            grocery_surge,
            offer_id=keys.CREATED_OFFER_ID,
            delivery=delivery,
            min_eta='33',
            max_eta='77',
            minimum_order=minimum_order,
            is_surge=offer_data['is_surge'],
            offer_time=keys.TS_NOW,
        )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers={
            'X-Idempotency-Token': DEFAULT_IDEMPOTENCY_TOKEN,
            **BASIC_HEADERS,
        },
        json={
            'position': {
                'location': keys.DEFAULT_DEPOT_LOCATION,
                'uri': 'test_url',
            },
            'cart_id': EXISTING_CART_ID,
            'cart_version': 1,
            'offer_id': keys.CREATED_OFFER_ID,
        },
    )

    assert response.status_code == 200
    response_json = response.json()

    if expected_unavailable_reason != 'checkedout':
        assert not response_json['available_for_checkout']
        assert (
            response_json.get('checkout_unavailable_reason')
            == expected_unavailable_reason
        )
    else:
        assert response_json['available_for_checkout']

    surge_minimum_order = None
    if offer_data is not None:
        surge_minimum_order = offer_data.get('minimum_order')
    order_conditions = response_json.get('order_conditions', {})
    min_order_template = order_conditions.get('minimum_order_price_template')
    if surge_minimum_order is None:
        assert not min_order_template
    else:
        assert min_order_template == f'{surge_minimum_order} $SIGN$$CURRENCY$'
