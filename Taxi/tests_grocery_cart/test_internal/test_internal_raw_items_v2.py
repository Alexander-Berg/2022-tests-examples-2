# pylint: disable=too-many-lines

import dataclasses
import decimal

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart import models
from tests_grocery_cart.plugins import keys

# pylint: disable=invalid-name
Decimal = decimal.Decimal

INTERNAL_RAW_HANDLER = '/internal/v1/cart/retrieve/raw'
ITEMS_PRICING_ENABLED_DISABLED = pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=experiments.ITEMS_PRICING_ENABLED),
        pytest.param(
            marks=pytest.mark.config(GROCERY_CART_ITEMS_PRICING_ENABLED=False),
        ),
    ],
)


@dataclasses.dataclass
class CartPriceConfig:
    currency_min_value: str
    minimum_total_cost: str
    minimum_item_price: str
    currency_precision: int = 1
    promocode_rounding_value: str = '0.01'


DEFAULT_CART_PRICES_CONFIG = CartPriceConfig(
    currency_min_value='0.01',
    minimum_total_cost='1',
    minimum_item_price='1',
    promocode_rounding_value='0.01',
)


@pytest.fixture
def _checkout_cart(
        experiments3,
        overlord_catalog,
        grocery_p13n,
        cart,
        grocery_coupons,
        eats_promocodes,
        offers,
        grocery_surge,
):
    async def _do(
            init_items,
            splitted_items,
            cashback_to_pay=None,
            promocode_fixed_value=None,
            cart_prices_config: CartPriceConfig = None,
            ignore_overflow=False,
            delivery_cost=None,
            discounts_apply_flow=None,
            service_fee=None,
            supplier_tin=None,
    ):

        if delivery_cost is not None:
            actual_delivery = {
                'cost': delivery_cost,
                'next_cost': '0',
                'next_threshold': '9999999',
            }

            common.create_offer(
                offers,
                experiments3,
                grocery_surge,
                offer_id='offer_id',
                offer_time=keys.TS_NOW,
            )
            common.add_delivery_conditions(
                experiments3, delivery=actual_delivery,
            )
        if cart_prices_config is None:
            cart_prices_config = DEFAULT_CART_PRICES_CONFIG

        _validate_input(
            init_items,
            splitted_items,
            cashback_to_pay=cashback_to_pay,
            promocode_fixed_value=promocode_fixed_value,
            ignore_overflow=ignore_overflow,
            cart_prices_config=cart_prices_config,
        )

        experiments.add_lavka_cart_prices_config(
            experiments3,
            currency_min_value=cart_prices_config.currency_min_value,
            precision=cart_prices_config.currency_precision,
            minimum_total_cost=cart_prices_config.minimum_total_cost,
            minimum_item_price=cart_prices_config.minimum_item_price,
            promocode_rounding_value=(
                cart_prices_config.promocode_rounding_value
            ),
        )

        experiments.set_checkout_discounts_apply_flow(
            experiments3, discounts_apply_flow or 'default',
        )

        cart_items = {}
        for index, item in enumerate(init_items):
            item_id = f'item-{index}'

            price = item['p']
            full_price = item.get('full_price', price)
            vat = item.get('vat', '20')

            overlord_catalog.add_product(
                product_id=item_id,
                price=full_price,
                vat=vat,
                supplier_tin=supplier_tin,
            )

            if price != full_price:
                grocery_p13n.add_modifier(
                    product_id=item_id,
                    value=str(round(float(full_price) - float(price), 2)),
                )
            cart_items[item_id] = item

        grocery_p13n.set_cashback_info_response(
            payment_available=True, balance='999999',
        )

        await cart.modify(cart_items)
        await cart.set_payment('card')

        if cashback_to_pay is not None:
            await cart.set_cashback_flow('charge')

        if promocode_fixed_value is not None:
            grocery_coupons.set_check_response_custom(
                promocode_fixed_value, promocode_type='fixed',
            )
            await cart.apply_promocode('some_code')

        response = await cart.checkout(
            cashback_to_pay=cashback_to_pay,
            grocery_flow_version='grocery_flow_v1',
            service_fee=service_fee,
        )
        assert 'checkout_unavailable_reason' not in response

    return _do


@pytest.fixture
def _get_response_with_items_v2(cart, taxi_grocery_cart, _checkout_cart):
    async def _do(
            init_items,
            splitted_items,
            cashback_to_pay=None,
            promocode_fixed_value=None,
            cart_prices_config: CartPriceConfig = None,
            ignore_overflow=False,
            delivery_cost=None,
            discounts_apply_flow=None,
            service_fee=None,
            supplier_tin=None,
    ):
        await _checkout_cart(
            init_items=init_items,
            splitted_items=splitted_items,
            cashback_to_pay=cashback_to_pay,
            promocode_fixed_value=promocode_fixed_value,
            cart_prices_config=cart_prices_config,
            ignore_overflow=ignore_overflow,
            delivery_cost=delivery_cost,
            discounts_apply_flow=discounts_apply_flow,
            service_fee=service_fee,
            supplier_tin=supplier_tin,
        )

        response = await taxi_grocery_cart.post(
            INTERNAL_RAW_HANDLER,
            json={'cart_id': cart.cart_id, 'source': 'SQL'},
        )

        assert response.status_code == 200
        return response

    return _do


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        '__default__': {'grocery': 0.01, '__default__': 1},
    },
)
@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'cashback_to_pay, init_items, splitted_items',
    [
        (
            '100',
            [{'p': '150', 'q': '1'}],
            [[{'p': '50', 'q': '1', 'cashback': '100'}]],
        ),
        (
            '101',
            [{'p': '100', 'q': '2'}],
            [[{'p': '49.5', 'q': '2', 'cashback': '50.5'}]],
        ),
        (
            '20',
            [{'p': '50.35', 'q': '1'}],
            [[{'p': '30.35', 'q': '1', 'cashback': '20'}]],
        ),
        (
            '19',
            [{'p': '10.4', 'q': '1'}, {'p': '10.8', 'q': '1'}],
            [
                [{'p': '1', 'q': '1', 'cashback': '9.4'}],
                [{'p': '1.2', 'q': '1', 'cashback': '9.6'}],
            ],
        ),
        (
            '20',
            [{'p': '10.45', 'q': '2'}, {'p': '10.8', 'q': '1'}],
            [
                [{'p': '3.78', 'q': '2', 'cashback': '6.67'}],
                [{'p': '4.14', 'q': '1', 'cashback': '6.66'}],
            ],
        ),
        (
            '1',
            [{'p': '2', 'q': '3'}],
            [
                [
                    {'p': '1.66', 'q': '1', 'cashback': '0.34'},
                    {'p': '1.67', 'q': '2', 'cashback': '0.33'},
                ],
            ],
        ),
    ],
)
async def test_cashback_to_pay(
        cashback_to_pay,
        init_items,
        splitted_items,
        _get_response_with_items_v2,
):
    response = await _get_response_with_items_v2(
        init_items, splitted_items, cashback_to_pay=cashback_to_pay,
    )
    _check_response(response, init_items, splitted_items)


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        '__default__': {'grocery': 0.01, '__default__': 1},
    },
)
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
async def test_cashback_with_correct_without_items_pricing(
        taxi_grocery_cart, cart, _get_response_with_items_v2,
):
    cashback_to_pay = '20'
    init_items = [{'p': '10.45', 'q': '2'}, {'p': '10.8', 'q': '1'}]
    splitted_items = [
        [{'p': '3.78', 'q': '2', 'cashback': '6.67'}],
        [{'p': '4.14', 'q': '1', 'cashback': '6.66'}],
    ]
    response = await _get_response_with_items_v2(
        init_items, splitted_items, cashback_to_pay=cashback_to_pay,
    )
    _check_response(response, init_items, splitted_items)

    cart.upsert_items(
        [
            models.CartItem(
                item_id='item-1',
                price='10.8',
                quantity='0',
                currency='RUB',
                vat='20',
                reserved=None,
            ),
        ],
    )
    response = await taxi_grocery_cart.post(
        INTERNAL_RAW_HANDLER, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )
    assert response.status_code == 200

    init_items[1]['q'] = '0'
    new_splitted_items = [
        [{'p': '1', 'q': '2', 'cashback': '9.45'}],
        [{'p': '10.8', 'q': '0', 'cashback': '0'}],
    ]
    _check_response(response, init_items, new_splitted_items)


@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'cashback_to_pay, promocode_fixed_value, init_items, splitted_items',
    [
        pytest.param(
            '100',
            '100',
            [
                {'p': '50', 'q': '1'},
                {'p': '100', 'q': '2'},
                {'p': '150', 'q': '2'},
            ],
            [
                [{'p': '20.9', 'q': '1', 'cashback': '20', 'promo': '9.1'}],
                [{'p': '61.82', 'q': '2', 'cashback': '20', 'promo': '18.18'}],
                [
                    {
                        'p': '102.73',
                        'q': '2',
                        'cashback': '20',
                        'promo': '27.27',
                    },
                ],
            ],
            id='basic test',
        ),
        pytest.param(
            '200',
            '100',
            [
                {'p': '50', 'q': '1'},
                {'p': '100', 'q': '2'},
                {'p': '150', 'q': '2'},
            ],
            [
                [{'p': '1', 'q': '1', 'cashback': '39.9', 'promo': '9.1'}],
                [
                    {
                        'p': '41.79',
                        'q': '2',
                        'cashback': '40.03',
                        'promo': '18.18',
                    },
                ],
                [
                    {
                        'p': '82.71',
                        'q': '2',
                        'cashback': '40.02',
                        'promo': '27.27',
                    },
                ],
            ],
            id='different values of promocode and cashback',
        ),
        pytest.param(
            '200',
            '100',
            [
                {'p': '1', 'q': '1'},
                {'p': '200', 'q': '1'},
                {'p': '300', 'q': '1'},
            ],
            [
                [{'p': '1', 'q': '1', 'cashback': '0', 'promo': '0'}],
                [{'p': '60', 'q': '1', 'cashback': '100', 'promo': '40'}],
                [{'p': '140', 'q': '1', 'cashback': '100', 'promo': '60'}],
            ],
            id='No discount for one of items',
        ),
        pytest.param(
            '387',
            '113',
            [
                {'p': '33', 'q': '2'},
                {'p': '78', 'q': '3'},
                {'p': '206', 'q': '1'},
            ],
            [
                [{'p': '1', 'q': '2', 'cashback': '24.63', 'promo': '7.37'}],
                [
                    {
                        'p': '1',
                        'q': '1',
                        'cashback': '59.58',
                        'promo': '17.42',
                    },
                    {
                        'p': '1',
                        'q': '2',
                        'cashback': '59.59',
                        'promo': '17.41',
                    },
                ],
                [{'p': '1', 'q': '1', 'cashback': '158.98', 'promo': '46.02'}],
            ],
            id='cashback + promocode == full payment',
        ),
    ],
)
async def test_split_with_promocode_and_cashback(
        cashback_to_pay,
        promocode_fixed_value,
        init_items,
        splitted_items,
        eats_promocodes,
        _get_response_with_items_v2,
):
    response = await _get_response_with_items_v2(
        init_items,
        splitted_items,
        cashback_to_pay=cashback_to_pay,
        promocode_fixed_value=promocode_fixed_value,
    )
    _check_response(response, init_items, splitted_items)


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        '__default__': {'grocery': 0.01, '__default__': 1},
    },
)
@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value, init_items, splitted_items',
    [
        (
            '100',
            [{'p': '150', 'q': '1'}],
            [[{'p': '50', 'q': '1', 'cashback': '0', 'promo': '100'}]],
        ),
        (
            '101',
            [{'p': '100', 'q': '2'}],
            [[{'p': '49.5', 'q': '2', 'cashback': '0', 'promo': '50.5'}]],
        ),
        (
            '20',
            [{'p': '50.35', 'q': '1'}],
            [[{'p': '30.35', 'q': '1', 'cashback': '0', 'promo': '20'}]],
        ),
        (
            '19',
            [{'p': '10.4', 'q': '1'}, {'p': '10.8', 'q': '1'}],
            [
                [{'p': '1.07', 'q': '1', 'cashback': '0', 'promo': '9.33'}],
                [{'p': '1.13', 'q': '1', 'cashback': '0', 'promo': '9.67'}],
            ],
        ),
        (
            '20',
            [{'p': '10.45', 'q': '2'}, {'p': '10.8', 'q': '1'}],
            [
                [
                    {'p': '3.85', 'q': '1', 'cashback': '0', 'promo': '6.6'},
                    {'p': '3.86', 'q': '1', 'cashback': '0', 'promo': '6.59'},
                ],
                [{'p': '3.99', 'q': '1', 'cashback': '0', 'promo': '6.81'}],
            ],
        ),
        (
            '1',
            [{'p': '2', 'q': '3'}],
            [
                [
                    {'p': '1.66', 'q': '1', 'cashback': '0', 'promo': '0.34'},
                    {'p': '1.67', 'q': '2', 'cashback': '0', 'promo': '0.33'},
                ],
            ],
        ),
    ],
)
async def test_split_with_promocode_only(
        promocode_fixed_value,
        init_items,
        splitted_items,
        eats_promocodes,
        _get_response_with_items_v2,
):
    response = await _get_response_with_items_v2(
        init_items,
        splitted_items,
        promocode_fixed_value=promocode_fixed_value,
    )
    _check_response(response, init_items, splitted_items)


@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value, init_items, splitted_items',
    [
        pytest.param(
            '100',
            [{'p': '150', 'q': '1'}],
            [[{'p': '50', 'q': '1', 'cashback': '0', 'promo': '100'}]],
            id='basic',
        ),
        pytest.param(
            '100',
            [{'p': '30', 'q': '1'}, {'p': '50', 'q': '1'}],
            [
                [{'p': '5', 'q': '1', 'cashback': '0', 'promo': '25'}],
                [{'p': '5', 'q': '1', 'cashback': '0', 'promo': '45'}],
            ],
            id='min_item_price',
        ),
        pytest.param(
            '100',
            [{'p': '30', 'q': '1'}],
            [[{'p': '10', 'q': '1', 'cashback': '0', 'promo': '20'}]],
            id='min_total_cost',
        ),
        pytest.param(
            '100',
            [{'p': '100', 'q': '1'}, {'p': '200', 'q': '1'}],
            [
                [{'p': '66.66', 'q': '1', 'cashback': '0', 'promo': '33.34'}],
                [{'p': '133.34', 'q': '1', 'cashback': '0', 'promo': '66.66'}],
            ],
            id='ceil_prices',
        ),
        pytest.param(
            '1',
            [{'p': '6', 'q': '2'}],
            [[{'p': '5.5', 'q': '2', 'cashback': '0', 'promo': '0.5'}]],
            id='split_one_item',
        ),
        pytest.param(
            '1',
            [{'p': '6', 'q': '3'}],
            [
                [
                    {'p': '5.66', 'q': '1', 'cashback': '0', 'promo': '0.34'},
                    {'p': '5.67', 'q': '2', 'cashback': '0', 'promo': '0.33'},
                ],
            ],
            id='sub_items',
        ),
    ],
)
async def test_split_promocode_with_custom_prices_config(
        promocode_fixed_value,
        init_items,
        splitted_items,
        eats_promocodes,
        _get_response_with_items_v2,
):
    cart_price_config = CartPriceConfig(
        currency_min_value='0.01',
        minimum_total_cost='10',
        minimum_item_price='5',
    )
    response = await _get_response_with_items_v2(
        init_items,
        splitted_items,
        promocode_fixed_value=promocode_fixed_value,
        cart_prices_config=cart_price_config,
        ignore_overflow=True,
    )
    _check_response(response, init_items, splitted_items)


@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value, cashback_to_pay, init_items, splitted_items',
    [
        pytest.param(
            '20',
            '35',
            [{'p': '30', 'q': '1'}, {'p': '50', 'q': '1'}],
            [
                [{'p': '5', 'q': '1', 'cashback': '17.5', 'promo': '7.5'}],
                [{'p': '20', 'q': '1', 'cashback': '17.5', 'promo': '12.5'}],
            ],
            id='min_item_price',
        ),
        pytest.param(
            '20',
            '200',
            [{'p': '30', 'q': '1'}, {'p': '50', 'q': '1'}],
            [
                [{'p': '5', 'q': '1', 'cashback': '17.5', 'promo': '7.5'}],
                [{'p': '5', 'q': '1', 'cashback': '32.5', 'promo': '12.5'}],
            ],
            id='min_total_cost',
        ),
    ],
)
async def test_split_all_with_custom_prices_config(
        promocode_fixed_value,
        cashback_to_pay,
        init_items,
        splitted_items,
        eats_promocodes,
        _get_response_with_items_v2,
):
    cart_price_config = CartPriceConfig(
        currency_min_value='0.01',
        minimum_total_cost='10',
        minimum_item_price='5',
    )
    response = await _get_response_with_items_v2(
        init_items,
        splitted_items,
        promocode_fixed_value=promocode_fixed_value,
        cashback_to_pay=cashback_to_pay,
        cart_prices_config=cart_price_config,
        ignore_overflow=True,
    )
    _check_response(response, init_items, splitted_items)


@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value, currency_min_value, init_items, splitted_items',
    [
        pytest.param(
            '25',
            '5',
            [{'p': '123', 'q': '1'}, {'p': '456', 'q': '1'}],
            [
                [{'p': '113', 'q': '1', 'cashback': '0', 'promo': '10'}],
                [{'p': '441', 'q': '1', 'cashback': '0', 'promo': '15'}],
            ],
            id='discount_is_multiple_of_5',
        ),
        pytest.param(
            '25',
            '1',
            [{'p': '123', 'q': '1'}, {'p': '456', 'q': '1'}],
            [
                [{'p': '117', 'q': '1', 'cashback': '0', 'promo': '6'}],
                [{'p': '437', 'q': '1', 'cashback': '0', 'promo': '19'}],
            ],
            id='discount_is_multiple_of_1',
        ),
        pytest.param(
            '25',
            '0.01',
            [{'p': '123', 'q': '1'}, {'p': '456', 'q': '1'}],
            [
                [{'p': '117.67', 'q': '1', 'cashback': '0', 'promo': '5.33'}],
                [{'p': '436.33', 'q': '1', 'cashback': '0', 'promo': '19.67'}],
            ],
            id='discount_is_multiple_of_0.01',
        ),
        pytest.param(
            '23',
            '5',
            [{'p': '123', 'q': '1'}, {'p': '456', 'q': '1'}],
            [
                [{'p': '123', 'q': '1', 'cashback': '0', 'promo': '0'}],
                [{'p': '436', 'q': '1', 'cashback': '0', 'promo': '20'}],
            ],
            id='discount_is_multiple_of_5_with_rounding',
        ),
    ],
)
async def test_currency_min_value(
        promocode_fixed_value,
        currency_min_value,
        init_items,
        splitted_items,
        _get_response_with_items_v2,
):
    cart_price_config = CartPriceConfig(
        currency_min_value=currency_min_value,
        minimum_total_cost='1',
        minimum_item_price='1',
    )
    response = await _get_response_with_items_v2(
        init_items,
        splitted_items,
        promocode_fixed_value=promocode_fixed_value,
        cart_prices_config=cart_price_config,
        ignore_overflow=True,
    )
    _check_response(response, init_items, splitted_items)


@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value,promocode_rounding_value,'
    'init_items,splitted_items',
    [
        pytest.param(
            '25',
            '5',
            [{'p': '123', 'q': '1'}, {'p': '456', 'q': '1'}],
            [
                [{'p': '117', 'q': '1', 'cashback': '0', 'promo': '6'}],
                [{'p': '437', 'q': '1', 'cashback': '0', 'promo': '19'}],
            ],
            id='promocode_is_multiple_of_5',
        ),
        pytest.param(
            '23',
            '5',
            [{'p': '123', 'q': '1'}, {'p': '456', 'q': '1'}],
            [
                [{'p': '117', 'q': '1', 'cashback': '0', 'promo': '6'}],
                [{'p': '437', 'q': '1', 'cashback': '0', 'promo': '19'}],
            ],
            id='promocode_is_multiple_of_5_with_rounding',
        ),
    ],
)
async def test_promocode_rounding_value(
        promocode_fixed_value,
        promocode_rounding_value,
        init_items,
        splitted_items,
        _get_response_with_items_v2,
):
    cart_price_config = CartPriceConfig(
        promocode_rounding_value=promocode_rounding_value,
        currency_min_value='1',
        minimum_total_cost='1',
        minimum_item_price='1',
    )
    response = await _get_response_with_items_v2(
        init_items,
        splitted_items,
        promocode_fixed_value=promocode_fixed_value,
        cart_prices_config=cart_price_config,
        ignore_overflow=True,
    )
    _check_response(response, init_items, splitted_items)


@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value, min_item_price, init_items, splitted_items',
    [
        pytest.param(
            '10000',
            '0',
            [{'p': '1', 'q': '1'}, {'p': '10000', 'q': '1'}],
            [
                [{'p': '0', 'q': '1', 'cashback': '0', 'promo': '1'}],
                [{'p': '1', 'q': '1', 'cashback': '0', 'promo': '9999'}],
            ],
            id='zero_price_because_of_almost_full_promo_code',
        ),
        pytest.param(
            '10000',
            '0.01',
            [{'p': '1', 'q': '1'}, {'p': '10001', 'q': '1'}],
            [
                [{'p': '0.01', 'q': '1', 'cashback': '0', 'promo': '0.99'}],
                [{'p': '1.99', 'q': '1', 'cashback': '0', 'promo': '9999.01'}],
            ],
            id='always_non_zero_item',
        ),
    ],
)
async def test_min_item_price(
        promocode_fixed_value,
        min_item_price,
        init_items,
        splitted_items,
        _get_response_with_items_v2,
):
    cart_price_config = CartPriceConfig(
        currency_min_value='0.01',
        minimum_total_cost='1',
        minimum_item_price=min_item_price,
    )
    response = await _get_response_with_items_v2(
        init_items,
        splitted_items,
        promocode_fixed_value=promocode_fixed_value,
        cart_prices_config=cart_price_config,
    )
    _check_response(response, init_items, splitted_items)


@ITEMS_PRICING_ENABLED_DISABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value, cashback_to_pay, ' 'init_items, splitted_items',
    [
        pytest.param(
            '20',
            '0',
            [{'p': '30', 'q': '1'}, {'p': '50', 'q': '1'}],
            [
                [{'p': '22.5', 'q': '1', 'promo': '7.5'}],
                [{'p': '37.5', 'q': '1', 'promo': '12.5'}],
            ],
            id='equals_vat_promocode',
        ),
        pytest.param(
            '20',
            '30',
            [{'p': '30', 'q': '1'}, {'p': '50', 'q': '1'}],
            [
                [
                    {
                        'p': '11.25',
                        'q': '1',
                        'promo': '7.5',
                        'cashback': '11.25',
                    },
                ],
                [
                    {
                        'p': '18.75',
                        'q': '1',
                        'promo': '12.5',
                        'cashback': '18.75',
                    },
                ],
            ],
            id='equals_vat_promocode_cashback',
        ),
        pytest.param(
            '20',
            '0',
            [
                {'p': '30', 'q': '1', 'vat': '20'},
                {'p': '50', 'q': '1', 'vat': '10'},
            ],
            [
                [{'p': '10', 'q': '1', 'promo': '20'}],
                [{'p': '50', 'q': '1', 'promo': '0'}],
            ],
            id='not_equals_vat_promocode',
        ),
        pytest.param(
            '20',
            '30',
            [
                {'p': '30', 'q': '1', 'vat': '20'},
                {'p': '50', 'q': '1', 'vat': '10'},
            ],
            [
                [{'p': '1', 'q': '1', 'promo': '20', 'cashback': '9'}],
                [{'p': '29', 'q': '1', 'promo': '0', 'cashback': '21'}],
            ],
            id='not_equals_vat_promocode_cashback',
        ),
        pytest.param(
            '311.9',
            '53',
            [
                {'p': '259', 'q': '1', 'vat': '20'},
                {'p': '399', 'q': '1', 'vat': '20'},
                {'p': '1499', 'q': '1', 'vat': '20'},
                {'p': '879', 'q': '1', 'vat': '10', 'full_price': '1099'},
                {'p': '83', 'q': '1', 'vat': '10', 'full_price': '119'},
            ],
            [
                [
                    {
                        'p': '215.17',
                        'q': '1',
                        'promo': '37.46',
                        'cashback': '6.37',
                    },
                ],
                [
                    {
                        'p': '331.49',
                        'q': '1',
                        'promo': '57.7',
                        'cashback': '9.81',
                    },
                ],
                [
                    {
                        'p': '1245.44',
                        'q': '1',
                        'promo': '216.74',
                        'cashback': '36.82',
                    },
                ],
                [{'p': '879', 'q': '1', 'promo': '0', 'cashback': '0'}],
                [{'p': '83', 'q': '1', 'promo': '0', 'cashback': '0'}],
            ],
            id='share_low_values',
        ),
    ],
)
async def test_share_policy_by_vat(
        promocode_fixed_value,
        cashback_to_pay,
        init_items,
        splitted_items,
        _get_response_with_items_v2,
):
    response = await _get_response_with_items_v2(
        init_items,
        splitted_items,
        promocode_fixed_value=promocode_fixed_value,
        cashback_to_pay=cashback_to_pay,
        cart_prices_config=DEFAULT_CART_PRICES_CONFIG,
        ignore_overflow=True,
        discounts_apply_flow='priority_by_vat',
    )
    _check_response(response, init_items, splitted_items)


@common.GROCERY_ORDER_CYCLE_ENABLED
@ITEMS_PRICING_ENABLED_DISABLED
async def test_without_cashback(
        taxi_grocery_cart, cart, overlord_catalog, tristero_parcels,
):
    parcel_product_id_base = 'parcels_id_1'
    parcel_product_id = parcel_product_id_base + ':st-pa'
    product_id = 'item-id'
    price = '100'

    tristero_parcels.add_parcel(parcel_id=parcel_product_id)
    overlord_catalog.add_product(product_id=product_id, price=price)

    cart_items = {
        product_id: {'p': price, 'q': '1'},
        parcel_product_id: {'p': 0, 'q': 1},
    }

    await cart.modify(cart_items)
    await cart.set_payment('card')
    await cart.set_cashback_flow('disabled')
    response = await cart.checkout()
    assert 'checkout_unavailable_reason' not in response

    response = await taxi_grocery_cart.post(
        INTERNAL_RAW_HANDLER, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200
    assert response.json()['items_v2'] == [
        {
            'info': {
                'item_id': product_id,
                'refunded_quantity': '0',
                'shelf_type': 'store',
                'title': f'title for {product_id}',
                'vat': '20',
            },
            'sub_items': [
                {
                    'item_id': product_id + '_0',
                    'full_price': price,
                    'paid_with_cashback': '0',
                    'paid_with_promocode': '0',
                    'price': price,
                    'quantity': '1',
                },
            ],
        },
        {
            'info': {
                'item_id': parcel_product_id_base,
                'refunded_quantity': '0',
                'shelf_type': 'parcel',
                'title': f'title for {parcel_product_id}',
            },
            'sub_items': [
                {
                    'item_id': parcel_product_id + '_0',
                    'full_price': '0',
                    'paid_with_cashback': '0',
                    'paid_with_promocode': '0',
                    'price': '0',
                    'quantity': '1',
                },
            ],
        },
    ]


@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize('checked_out', [True, False])
async def test_no_items_v2_before_checkout(
        taxi_grocery_cart, cart, checked_out,
):
    await cart.init(['test_item'])

    if checked_out:
        await cart.checkout()

    response = await taxi_grocery_cart.post(
        INTERNAL_RAW_HANDLER, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200
    assert bool('items_v2' in response.json()) == checked_out


@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize(
    'diff_quantity, is_success_checkout', [(-1, True), (+1, False)],
)
async def test_no_items_v2_after_bad_checkout(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        diff_quantity,
        is_success_checkout,
        fetch_cart,
):
    product_id = 'item-1'
    price = '10'
    quantity = 3
    overlord_catalog.add_product(
        product_id=product_id, price=price, in_stock=str(quantity),
    )

    cart_items = {product_id: {'p': price, 'q': str(quantity + diff_quantity)}}

    await cart.modify(cart_items)

    response = await cart.checkout()
    assert (
        bool('checkout_unavailable_reason' not in response)
        == is_success_checkout
    )

    response = await taxi_grocery_cart.post(
        INTERNAL_RAW_HANDLER, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200

    assert bool('items_v2' in response.json()) == is_success_checkout


@experiments.ITEMS_PRICING_ENABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value, cashback_to_pay, init_items, splitted_items',
    [
        (
            '250',
            '100',
            [
                {'p': '150', 'full_price': '300', 'q': '1'},
                {'p': '200', 'full_price': '400', 'q': '3'},
                {'p': '600', 'full_price': '700', 'q': '2'},
            ],
            [
                [
                    {
                        'p': '114.09',
                        'q': '1',
                        'cashback': '16.67',
                        'promo': '19.24',
                    },
                ],
                [
                    {
                        'p': '157.69',
                        'q': '3',
                        'cashback': '16.67',
                        'promo': '25.64',
                    },
                ],
                [
                    {
                        'p': '506.42',
                        'q': '2',
                        'cashback': '16.66',
                        'promo': '76.92',
                    },
                ],
            ],
        ),
        (
            '43.5',
            '384.5',
            [
                {'p': '85', 'q': '2'},
                {'p': '65', 'q': '2'},
                {'p': '45', 'q': '3'},
            ],
            [
                [{'p': '1', 'q': '2', 'cashback': '75.5', 'promo': '8.5'}],
                [{'p': '1', 'q': '2', 'cashback': '57.5', 'promo': '6.5'}],
                [{'p': '1', 'q': '3', 'cashback': '39.5', 'promo': '4.5'}],
            ],
        ),
    ],
)
async def test_save_items_pricing(
        _checkout_cart,
        fetch_cart,
        cart,
        promocode_fixed_value,
        cashback_to_pay,
        init_items,
        splitted_items,
):
    await _checkout_cart(
        init_items,
        splitted_items,
        cashback_to_pay=cashback_to_pay,
        promocode_fixed_value=promocode_fixed_value,
    )

    cart_pg = fetch_cart(cart.cart_id)
    _check_items_pricing(cart_pg.items_pricing, init_items, splitted_items)


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'RUB': {'__default__': 1, 'grocery': 0.01}},
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2}},
)
@experiments.ITEMS_PRICING_ENABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'promocode_fixed_value, cashback_to_pay, delivery_cost, init_items, '
    'splitted_items, service_fee',
    [
        pytest.param(
            '2',
            '1',
            '3.51',
            [
                {'p': '0.69', 'full_price': '1.34', 'q': '3'},
                {'p': '1.29', 'q': '2'},
                {'p': '0.1', 'full_price': '0.4', 'q': '4'},
            ],
            [
                [
                    {
                        'p': '0.25',
                        'q': '1',
                        'cashback': '0.16',
                        'promo': '0.28',
                    },
                    {
                        'p': '0.26',
                        'q': '2',
                        'cashback': '0.15',
                        'promo': '0.28',
                    },
                ],
                [{'p': '0.62', 'q': '2', 'cashback': '0.15', 'promo': '0.52'}],
                [{'p': '0.01', 'q': '4', 'cashback': '0.06', 'promo': '0.03'}],
            ],
            '1.15',
            id='small prices',
        ),
        pytest.param(
            '20',
            '10',
            '99',
            [
                {'p': '10', 'full_price': '30', 'q': '3'},
                {'p': '40', 'q': '2'},
                {'p': '99', 'full_price': '456', 'q': '4'},
            ],
            [
                [
                    {
                        'p': '8.48',
                        'q': '1',
                        'cashback': '1.12',
                        'promo': '0.4',
                    },
                    {
                        'p': '8.49',
                        'q': '2',
                        'cashback': '1.11',
                        'promo': '0.4',
                    },
                ],
                [
                    {
                        'p': '37.31',
                        'q': '2',
                        'cashback': '1.11',
                        'promo': '1.58',
                    },
                ],
                [
                    {
                        'p': '93.98',
                        'q': '4',
                        'cashback': '1.11',
                        'promo': '3.91',
                    },
                ],
            ],
            '29',
            id='usual prices',
        ),
    ],
)
@pytest.mark.now(keys.TS_NOW)
async def test_price_data_in_response(
        promocode_fixed_value,
        cashback_to_pay,
        delivery_cost,
        init_items,
        splitted_items,
        service_fee,
        _get_response_with_items_v2,
):
    cart_price_config = CartPriceConfig(
        currency_min_value='0.01',
        minimum_total_cost='0.01',
        minimum_item_price='0.01',
    )

    response = await _get_response_with_items_v2(
        init_items,
        splitted_items=splitted_items,
        promocode_fixed_value=promocode_fixed_value,
        cashback_to_pay=cashback_to_pay,
        cart_prices_config=cart_price_config,
        delivery_cost=delivery_cost,
        service_fee=service_fee,
    )

    _check_response(response, init_items, splitted_items)

    data = response.json()

    total_items_discount = Decimal(0)
    full_total = Decimal(0)
    items_price = Decimal(0)

    for item in init_items:
        total_items_discount += _item_discount(item)
        full_total += _item_full_total(item)
        items_price += _item_total(item)

    items_full_price = full_total

    client_price = Decimal(0)
    for item in splitted_items:
        for sub_item in item:
            client_price += _item_total(sub_item)

    client_price += Decimal(delivery_cost)
    full_total += Decimal(delivery_cost)

    client_price += Decimal(service_fee)
    full_total += Decimal(service_fee)

    total_init_discount = (
        Decimal(cashback_to_pay)
        + Decimal(promocode_fixed_value)
        + total_items_discount
    )

    assert Decimal(data['total_discount']) == total_init_discount
    assert Decimal(data['client_price']) == client_price

    full_total_resp = _from_template(data['full_total_template'])
    assert full_total_resp == full_total

    items_full_price_resp = _from_template(data['items_full_price_template'])
    assert items_full_price_resp == items_full_price

    items_price_resp = _from_template(data['items_price_template'])
    assert items_price_resp == items_price

    promocode_discount_resp = Decimal(data['promocode_discount'])
    assert promocode_discount_resp == Decimal(promocode_fixed_value)

    total_item_discounts_resp = _from_template(
        data['total_item_discounts_template'],
    )
    assert total_item_discounts_resp == total_items_discount

    total_promocode_discount_resp = _from_template(
        data['total_promocode_discount_template'],
    )
    assert total_promocode_discount_resp == Decimal(promocode_fixed_value)

    service_fee_resp = Decimal(data['service_fee'])
    assert service_fee_resp == Decimal(service_fee)

    service_fee_template_resp = _from_template(data['service_fee_template'])
    assert service_fee_template_resp == Decimal(service_fee)

    discounts_info = _get_discounts_info(init_items, splitted_items)
    _check_discounts_info(data['discounts_info'], discounts_info)


async def test_supplier_tin_in_response(_get_response_with_items_v2):
    supplier_tin = 'supplier-tin'
    init_items = [{'p': '2', 'q': '3', 'supplier_tin': supplier_tin}]
    splitted_items = [[{'p': '2', 'q': '3'}]]

    cart_price_config = CartPriceConfig(
        currency_min_value='0.01',
        minimum_total_cost='0.01',
        minimum_item_price='0.01',
    )

    response = await _get_response_with_items_v2(
        init_items,
        splitted_items=splitted_items,
        cart_prices_config=cart_price_config,
        supplier_tin=supplier_tin,
    )

    _check_response(response, init_items, splitted_items)


def _get_discounts_info(init_items, splitted_items):
    items_to_discounts_info = {}

    for idx, item in enumerate(splitted_items):
        item_id = f'item-{idx}'
        items_to_discounts_info[item_id] = {}

        full_price = init_items[idx].get('full_price', init_items[idx]['p'])

        item_discount = Decimal(0)
        cashback_discount = Decimal(0)
        promocode_discount = Decimal(0)
        for sub_item in item:
            item_discount += Decimal(
                _item_money_discount(sub_item, full_price),
            )
            cashback_discount += _item_cashback_discount(sub_item)
            promocode_discount += _item_promocode_discount(sub_item)

        items_to_discounts_info[item_id] = {
            'item': item_discount,
            'cashback': cashback_discount,
            'promocode': promocode_discount,
        }

    return items_to_discounts_info


def _check_discounts_info(discounts_info_resp, discounts_info):
    for discount_info_resp in discounts_info_resp:
        item_id = discount_info_resp['item_id']
        expected_total_discount = Decimal(0)

        for discount in discount_info_resp['discounts']:
            discount_type = discount['type']

            expected = Decimal(discounts_info[item_id][discount_type])
            actual = _from_template(discount['value_template'])
            expected_total_discount += expected

            assert expected == Decimal(discount['value'])
            assert actual == expected

        actual_total_discount = _from_template(
            discount_info_resp['total_discount_template'],
        )
        assert actual_total_discount == expected_total_discount, item_id


def _item_money_discount(item, full_price):
    full_price = Decimal(full_price)
    price = Decimal(item['p'])
    quantity = Decimal(item['q'])
    cashback = Decimal(item.get('cashback', '0'))
    promo = Decimal(item.get('promo', '0'))

    return str((full_price - price - cashback - promo) * quantity)


def _item_discount(item):
    price = Decimal(item['p'])
    full_price = Decimal(item.get('full_price', item['p']))
    quantity = Decimal(item['q'])

    return (full_price - price) * quantity


def _item_cashback_discount(item):
    cashback = Decimal(item.get('cashback', '0'))
    quantity = Decimal(item['q'])

    return cashback * quantity


def _item_promocode_discount(item):
    promo = Decimal(item.get('promo', '0'))
    quantity = Decimal(item['q'])

    return promo * quantity


def _item_full_total(item):
    full_price = Decimal(item.get('full_price', item['p']))
    quantity = Decimal(item['q'])

    return full_price * quantity


def _from_template(price_tmpl):
    return Decimal(
        price_tmpl.replace(' $SIGN$$CURRENCY$', '').replace(',', '.'),
    )


def _item_total(item):
    return Decimal(item['p']) * Decimal(item['q'])


def _validate_input(
        items_v2,
        result,
        cashback_to_pay=None,
        promocode_fixed_value=None,
        ignore_overflow=False,
        cart_prices_config=None,
):
    if cashback_to_pay is None:
        cashback_to_pay = Decimal(0)
    if promocode_fixed_value is None:
        promocode_fixed_value = Decimal(0)

    total_cashback_discount = Decimal(0)
    total_money_discount = Decimal(0)

    items_count = len(items_v2)
    for idx in range(items_count):
        input_item = items_v2[idx]
        result_item = result[idx]

        for sub_item in result_item:
            with_cashback = Decimal(sub_item.get('cashback', '0'))
            quantity = Decimal(sub_item['q'])
            result_price = Decimal(sub_item['p'])
            input_price = Decimal(input_item['p'])

            total_cashback_discount += with_cashback * quantity
            total_money_discount += (
                input_price - with_cashback - result_price
            ) * quantity

    if ignore_overflow:
        assert total_cashback_discount <= Decimal(cashback_to_pay)
        promocode_overflow = total_money_discount - Decimal(
            promocode_fixed_value,
        )
        assert promocode_overflow < Decimal(
            cart_prices_config.promocode_rounding_value,
        )
    else:
        assert total_cashback_discount == Decimal(cashback_to_pay)
        assert total_money_discount == Decimal(promocode_fixed_value)


def _check_response(response, init_items, splitted_items):
    items_v2 = response.json()['items_v2']
    for index, item in enumerate(init_items):
        item_id = f'item-{index}'
        _check_item_in_response(items_v2, item_id, item, splitted_items[index])


def _check_items_pricing(items_pricing, init_items, splitted_items):
    for index, item in enumerate(init_items):
        item_id = f'item-{index}'
        price = item['p']
        full_price = item.get('full_price', price)

        for item_pricing in items_pricing['items']:
            if item_pricing['item_id'] != item_id:
                continue

            _check_sub_items(
                item_id,
                item_pricing['sub_items'],
                full_price,
                splitted_items[index],
            )


def _check_item_in_response(items_v2, item_id, item_raw, splitted_items):
    if splitted_items is None:
        assert items_v2 == []

    full_price = item_raw.get('full_price', item_raw['p'])
    vat = item_raw.get('vat', '20')
    supplier_tin = item_raw.get('supplier_tin', None)

    for item_v2 in items_v2:
        if item_v2['info']['item_id'] != item_id:
            continue

        assert item_v2['info']['item_id'] == item_id
        assert item_v2['info']['vat'] == vat
        assert item_v2['info']['title'] == f'title for {item_id}'

        if supplier_tin is not None:
            assert item_v2['info']['supplier_tin'] == supplier_tin

        _check_sub_items(
            item_id, item_v2['sub_items'], full_price, splitted_items,
        )

        return

    assert False, (item_id, items_v2)


def _check_sub_items(item_id, sub_items, full_price, splitted_items):
    for idx, sub_item in enumerate(sub_items):
        splitted_item = splitted_items[idx]

        assert sub_item['item_id'] == item_id + '_' + str(idx)
        assert sub_item['full_price'] == full_price, sub_items
        if 'cashback' in splitted_item:
            assert (
                sub_item['paid_with_cashback'] == splitted_item['cashback']
            ), sub_item['item_id']
        if 'promo' in splitted_item:
            assert (
                sub_item['paid_with_promocode'] == splitted_item['promo']
            ), sub_item['item_id']
        assert sub_item['price'] == splitted_item['p'], sub_item['item_id']
        assert sub_item['quantity'] == splitted_item['q'], sub_item['item_id']
