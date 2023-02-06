# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart
import pytest


DEFAULT_CART_ID = '01234567-89ab-cdef-000a-000000000001'
DEFAULT_ITEM = {
    'currency': 'RUB',
    'discount_pricing': {
        'cashback': '7',
        'discount_label': 'some label',
        'is_price_uncrossed': False,
        'price': '99',
        'price_template': '99 $SIGN$$CURRENCY$',
        'total_price_template': '297 ' '$SIGN$$CURRENCY$',
    },
    'image_url_templates': ['cart_item_1.jpg'],
    'item_id': 'item-id-1',
    'pricing': {
        'price': '150',
        'price_template': '150 $SIGN$$CURRENCY$',
        'total_price_template': '450 $SIGN$$CURRENCY$',
    },
    'quantity': '3',
    'quantity_limit': '10',
    'subtitle': 'item-1-subtitle',
    'title': 'item-1-title',
}
DEFAULT_CART_VERSION = 1
DEFAULT_OFFER_ID = '01234567-741d-410e-9f04-476f46ad43c7'
DEFAULT_CART_RESPONSE = {
    'cart_discount_pricing': {
        'basic_cart_discount_applied': {
            'discount_template': '300 ' '$SIGN$$CURRENCY$',
            'info_template': (
                'Скидка 300 $SIGN$$CURRENCY на '
                'заказ от 3000 $SIGN$$CURRENCY'
            ),
            'picture': 'basic_cart_discount_applied.jpg',
        },
        'basic_cart_discount_suggested': {
            'info_template': (
                'Скидка 400 $SIGN$$CURRENCY на '
                'заказ от 4000 $SIGN$$CURRENCY'
            ),
            'picture': 'basic_cart_discount_suggested.jpg',
        },
        'basic_cart_money_discount_applied': {
            'discount_template': '100 ' '$SIGN$$CURRENCY$',
            'info_template': (
                'Скидка 100 $SIGN$$CURRENCY на '
                'заказ от 1000 $SIGN$$CURRENCY'
            ),
        },
        'basic_cart_money_discount_suggested': {
            'discount_template': '200 ' '$SIGN$$CURRENCY$',
            'info_template': (
                'Скидка 200 $SIGN$$CURRENCY на '
                'заказ от 2000 $SIGN$$CURRENCY'
            ),
        },
        'discount_descriptions': [
            {
                'cart_description_template': (
                    'Скидка $SIGN$50$CURRENCY$ ' 'по карте Mastercard'
                ),
                'description_template': (
                    'Скидка $SIGN$50$CURRENCY$ ' 'по карте Mastercard'
                ),
                'discount_value': '50',
                'type': 'mastercard',
            },
        ],
        'discount_profit_no_delivery_template': '100 ' '$SIGN$$CURRENCY$',
        'discount_profit_template': '200 $SIGN$$CURRENCY$',
        'total_price_no_delivery_template': '900 ' '$SIGN$$CURRENCY$',
        'total_price_template': '1000 $SIGN$$CURRENCY$',
    },
    'cart_id': DEFAULT_CART_ID,
    'cart_pricing': {
        'total_price_no_delivery_template': '1100 $SIGN$$CURRENCY$',
        'total_price_template': '1200 $SIGN$$CURRENCY$',
    },
    'cart_version': DEFAULT_CART_VERSION,
    'cashback': {'amount_to_gain': '21'},
    'currency_sign': '$',
    'is_surge': True,
    'items': [DEFAULT_ITEM],
    'l10n': {'some_key': 'some_value'},
    'next_idempotency_token': '01234567-abcd-ef00-9f04-476f46ad43c7',
    'offer_id': DEFAULT_OFFER_ID,
    'order_conditions': {
        'delivery_cost': '100',
        'delivery_cost_template': '100 $SIGN$$CURRENCY$',
        'max_eta': 25,
        'min_eta': 10,
        'minimum_order_price': '200',
        'minimum_order_price_template': '200 $SIGN$$CURRENCY$',
    },
    'requirements': {
        'next_delivery_cost': '50',
        'next_delivery_cost_template': '50 $SIGN$$CURRENCY$',
        'next_delivery_threshold': '5000',
        'next_delivery_threshold_template': '5000 $SIGN$$CURRENCY$',
        'sum_to_min_order': '300',
        'sum_to_min_order_template': '300 $SIGN$$CURRENCY$',
        'sum_to_next_delivery': '700',
        'sum_to_next_delivery_template': '700 $SIGN$$CURRENCY$',
    },
    'informers': [],
}


async def test_proxies_grocery_cart_response(
        taxi_grocery_market_gw, grocery_cart, personal,
):
    """ Check common cart response proxying from grocery-cart """

    cart_id = DEFAULT_CART_ID
    grocery_cart.add_cart(cart_id)

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/retrieve',
        json={
            'cart_id': cart_id,
            'position': {'location': [55, 37]},
            'offer_id': 'some-offer-id',
        },
    )
    assert response.status == 200
    assert response.json() == DEFAULT_CART_RESPONSE


@pytest.mark.parametrize(
    'price_trend,return_price_informer',
    [
        pytest.param('increase', True, id='price increased'),
        pytest.param('decrease', False, id='price decreased'),
    ],
)
@pytest.mark.parametrize(
    'cashback_trend,return_cashback_informer',
    [
        pytest.param('increase', False, id='cashback increase'),
        pytest.param('decrease', True, id='cashback decreased'),
    ],
)
async def test_cart_diff_data_as_informers(
        taxi_grocery_market_gw,
        grocery_cart,
        price_trend,
        return_price_informer,
        cashback_trend,
        return_cashback_informer,
):
    """ Check cart diff_data proxing as
    informers from grocery-cart """

    cart_id = DEFAULT_CART_ID
    cart = grocery_cart.add_cart(cart_id)

    cart_total_diff = {
        'previous_template': '100 $SIGN$$CURRENCY$',
        'actual_template': '250 $SIGN$$CURRENCY$',
        'diff_template': '150 $SIGN$$CURRENCY$',
        'trend': 'increase',
    }

    cart_total_cashback_diff = {
        'previous_value': '70',
        'actual_value': '50',
        'diff': '20',
        'trend': 'decrease',
    }

    diff_item = {
        'product_id': DEFAULT_ITEM['item_id'],
        'price': {
            'previous_template': '100 $SIGN$$CURRENCY$',
            'actual_template': '250 $SIGN$$CURRENCY$',
            'diff_template': '150 $SIGN$$CURRENCY$',
            'trend': price_trend,
        },
        'quantity': {'wanted': '70', 'actual_limit': '50'},
        'cashback': {
            'previous_value': '70',
            'actual_value': '50',
            'diff': '20',
            'trend': cashback_trend,
        },
    }

    diff_data = {
        'products': [diff_item],
        'cart_total': cart_total_diff,
        'cart_total_cashback': cart_total_cashback_diff,
    }

    price_informer = {
        'content': {
            'items': [
                {
                    'image_url_templates': DEFAULT_ITEM['image_url_templates'],
                    'new_value_template': diff_item['price'][
                        'actual_template'
                    ],
                    'old_value_template': diff_item['price'][
                        'previous_template'
                    ],
                    'title': DEFAULT_ITEM['title'],
                },
            ],
            'new_value_template': cart_total_diff['actual_template'],
            'old_value_template': cart_total_diff['previous_template'],
        },
        'type': 'price-mismatch',
    }

    cashback_informer = {
        'content': {
            'items': [
                {
                    'image_url_templates': DEFAULT_ITEM['image_url_templates'],
                    'new_value': diff_item['cashback']['actual_value'],
                    'old_value': diff_item['cashback']['previous_value'],
                    'title': DEFAULT_ITEM['title'],
                },
            ],
            'new_value': cart_total_cashback_diff['actual_value'],
            'old_value': cart_total_cashback_diff['previous_value'],
        },
        'type': 'cashback-mismatch',
    }

    quantity_informer = {
        'content': {
            'items': [
                {
                    'image_url_templates': DEFAULT_ITEM['image_url_templates'],
                    'new_value': diff_item['quantity']['actual_limit'],
                    'old_value': diff_item['quantity']['wanted'],
                    'title': DEFAULT_ITEM['title'],
                },
            ],
            'new_value_template': cart_total_diff['actual_template'],
            'old_value_template': cart_total_diff['previous_template'],
        },
        'type': 'quantity-over-limit',
    }

    expected_informers = []
    if return_price_informer:
        expected_informers.append(price_informer)
    if return_cashback_informer:
        expected_informers.append(cashback_informer)
    expected_informers.append(quantity_informer)

    cart.set_diff_data(diff_data)

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/retrieve',
        json={
            'cart_id': cart_id,
            'position': {'location': [55, 37]},
            'offer_id': 'some-offer-id',
        },
    )
    assert response.status == 200

    assert response.json()['informers'] == expected_informers


@pytest.mark.parametrize('trend', ['increase', 'decrease'])
@pytest.mark.parametrize('silent', [True, False, None])
async def test_cart_do_update_on_mismatches(
        taxi_grocery_market_gw, grocery_cart, silent, trend,
):
    """ cart update should be called with all items
    if there any mismatch and silent is not true """
    diff_data = {
        'products': [
            {
                'product_id': DEFAULT_ITEM['item_id'],
                'price': {
                    'previous_template': '100 $SIGN$$CURRENCY$',
                    'actual_template': '250 $SIGN$$CURRENCY$',
                    'diff_template': '150 $SIGN$$CURRENCY$',
                    'trend': trend,
                },
            },
        ],
        'cart_total': {
            'previous_template': '100 $SIGN$$CURRENCY$',
            'actual_template': '250 $SIGN$$CURRENCY$',
            'diff_template': '150 $SIGN$$CURRENCY$',
            'trend': trend,
        },
    }

    cart_id = DEFAULT_CART_ID
    cart = grocery_cart.add_cart(cart_id)
    cart.set_diff_data(diff_data)
    position = {'location': [55, 37]}
    offer_id = 'some-offer-id'

    request_json = {
        'cart_id': cart_id,
        'position': position,
        'offer_id': offer_id,
    }

    if silent is not None:
        request_json['silent'] = silent

    cart_fix_request_json = {
        'cart_id': cart_id,
        'position': position,
        'offer_id': DEFAULT_OFFER_ID,
        'cart_version': DEFAULT_CART_VERSION,
        'items': [
            {
                'id': DEFAULT_ITEM['item_id'],
                'price': DEFAULT_ITEM['discount_pricing']['price'],
                'quantity': str(
                    min(
                        int(DEFAULT_ITEM['quantity']),
                        int(DEFAULT_ITEM['quantity_limit']),
                    ),
                ),
                'currency': DEFAULT_ITEM['currency'],
                'cashback': DEFAULT_ITEM['discount_pricing']['cashback'],
            },
        ],
    }

    grocery_cart.check_request(
        cart_fix_request_json, handler=mock_grocery_cart.Handler.update,
    )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/cart/retrieve', json=request_json,
    )
    assert response.status == 200
    assert (grocery_cart.mock_update_times_called() == 1) != (silent is True)
