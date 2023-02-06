import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys
from tests_grocery_cart.plugins import mock_eats_promocodes

BASIC_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-YaTaxi-Session': 'taxi:1234',
    'X-YaTaxi-User': 'eats_user_id=12345',
    'X-Yandex-UID': 'some_uid',
}


async def test_not_found_cart_id(taxi_grocery_cart, cart, overlord_catalog):
    item_id = 'item_id_1'
    price = '123'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': '1', 'p': price}})

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve/raw',
        json={'cart_id': 'ffffffff-ffff-40ff-ffff-ffffffffffff'},
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 404


async def test_not_found_different_user(
        taxi_grocery_cart, cart, overlord_catalog,
):
    item_id = 'item_id_1'
    price = '123'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': '1', 'p': price}})

    other_user_headers = {
        'X-YaTaxi-Session': 'other_taxi:1234',
        'X-YaTaxi-User': 'eats_other_user_id=12345',
        'X-Yandex-UID': 'some_other_uid',
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve/raw',
        json={'cart_id': cart.cart_id},
        headers=other_user_headers,
    )
    assert response.status_code == 404


async def test_not_checked_out(taxi_grocery_cart, cart, overlord_catalog):
    item_id = 'item_id_1'
    price = '123'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': '1', 'p': price}})

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve/raw',
        json={'cart_id': cart.cart_id},
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 404


@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'RUB': {'__default__': 1, 'grocery': 0.01}},
    CURRENCY_FORMATTING_RULES={
        'RUB': {
            '__default__': 1,
            'grocery': 2,  # проверяем что возьмется именно grocery
        },
    },
)
async def test_basic(
        taxi_grocery_cart, cart, overlord_catalog, tristero_parcels,
):
    item_id = 'item_id_1'
    parcel_id = 'parcel_id:st-pa'
    price = '123.12'
    overlord_catalog.add_product(
        product_id=item_id, price=price, legal_restrictions=['RU_18+'],
    )
    tristero_parcels.add_parcel(parcel_id=parcel_id)

    await cart.modify(
        {item_id: {'q': '1', 'p': price}, parcel_id: {'q': '1', 'p': '0'}},
        currency='RUB',
    )
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve/raw',
        json={'cart_id': cart.cart_id},
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'cart_id': cart.cart_id,
        'full_price_no_delivery_template': '123,12 $SIGN$$CURRENCY$',
        'total_price_template': '123,12 $SIGN$$CURRENCY$',
        'total_price_no_delivery_template': '123,12 $SIGN$$CURRENCY$',
        'currency_sign': '₽',
        'delivery_type': 'eats_dispatch',
        'order_conditions': {
            'delivery_cost': '0',
            'delivery_cost_template': '0 $SIGN$$CURRENCY$',
        },
        'items': [
            {
                'catalog_price': '123.12',
                'catalog_price_template': '123,12 $SIGN$$CURRENCY$',
                'catalog_total_price_template': '123,12 $SIGN$$CURRENCY$',
                'id': item_id,
                'price': '123.12',
                'quantity': '1',
                'currency': 'RUB',
                'title': 'title for item_id_1',
                'image_url_templates': [f'url for {item_id}'],
                'restrictions': ['ru_18+'],
            },
            {
                'catalog_price': '0',
                'catalog_price_template': '0 $SIGN$$CURRENCY$',
                'catalog_total_price_template': '0 $SIGN$$CURRENCY$',
                'id': parcel_id,
                'price': '0',
                'quantity': '1',
                'currency': 'RUB',
                'title': f'title for {parcel_id}',
                'image_url_templates': [f'url for {parcel_id}'],
            },
        ],
    }


@pytest.mark.now(keys.TS_NOW)
async def test_discounts(
        mockserver,
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        grocery_coupons,
        grocery_p13n,
        offers,
        experiments3,
        grocery_surge,
):
    item_id = 'item_id_2'
    price = 345
    discount_value = 150
    grocery_p13n.add_modifier(product_id=item_id, value=discount_value)
    overlord_catalog.add_product(product_id=item_id, price=str(price))
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        offer_time=keys.TS_NOW,
        delivery={'cost': '200', 'next_threshold': '999', 'next_cost': '100'},
        minimum_order='100',
    )
    await cart.modify(
        {item_id: {'q': '1', 'p': str(price - discount_value)}},
        currency='RUB',
    )

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def mock_validate(request):
        return mock_eats_promocodes.discount_payload(discount='100')

    await cart.apply_promocode('some_promocode')
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve/raw',
        json={'cart_id': cart.cart_id},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert (
        response_json['full_price_no_delivery_template']
        == '345 $SIGN$$CURRENCY$'
    )
    assert (
        response_json['order_conditions']['delivery_cost_template']
        == '200 $SIGN$$CURRENCY$'
    )
    assert response_json['total_price_template'] == '295 $SIGN$$CURRENCY$'
    assert response_json['total_discount_template'] == '250 $SIGN$$CURRENCY$'
    assert (
        response_json['total_discount_no_promocode_template']
        == '150 $SIGN$$CURRENCY$'
    )
    assert (
        response_json['total_promocode_discount_template']
        == '100 $SIGN$$CURRENCY$'
    )

    assert mock_validate.times_called == 2


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize('tips_payment_flow', ['separate', 'with_order'])
async def test_tips(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        offers,
        grocery_surge,
        grocery_coupons,
        experiments3,
        eats_promocodes,
        tips_payment_flow,
):
    item_id = 'item_id_1'
    price = '123'
    delivery_cost = '50'
    promocode_fixed_value = '20'
    cashback_to_pay = '10'

    experiments.set_tips_payment_flow(experiments3, tips_payment_flow)

    overlord_catalog.add_product(product_id=item_id, price=price)

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        offer_time=keys.TS_NOW,
        delivery={
            'cost': delivery_cost,
            'next_threshold': '999999',
            'next_cost': '80',
        },
        minimum_order='100',
    )

    eats_promocodes.set_valid(False)
    grocery_coupons.set_check_response_custom(
        promocode_fixed_value, promocode_type='fixed',
    )

    await cart.modify({item_id: {'q': '1', 'p': price}}, currency='RUB')
    await cart.set_tips(dict(amount='10', amount_type='percent'))
    await cart.apply_promocode('test_promocode_01')
    await cart.set_cashback_flow(flow='charge')
    await cart.checkout(cashback_to_pay=cashback_to_pay)

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve/raw',
        json={'cart_id': cart.cart_id},
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert (
        response_json['full_price_no_delivery_template']
        == f'{price} $SIGN$$CURRENCY$'
    )
    if tips_payment_flow == 'with_order':
        assert response_json['total_price_template'] == '167 $SIGN$$CURRENCY$'
    else:
        assert response_json['total_price_template'] == '153 $SIGN$$CURRENCY$'
    assert (
        response_json['total_price_no_delivery_template']
        == '103 $SIGN$$CURRENCY$'
    )
    assert (
        response_json['order_conditions']['tips_template']
        == '14 $SIGN$$CURRENCY$'
    )


# Проверяем, что возвращаем флаг private_label
@pytest.mark.parametrize('private_label', [True, False])
async def test_private_label(
        taxi_grocery_cart, cart, overlord_catalog, private_label,
):
    item_1 = 'item_1'
    price = '100'
    overlord_catalog.add_product(
        product_id=item_1, private_label=private_label,
    )
    await cart.modify({item_1: {'q': '1', 'p': price}})
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve/raw',
        json={'cart_id': cart.cart_id},
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    assert not response.json()['items'][0]['private_label'] ^ private_label
