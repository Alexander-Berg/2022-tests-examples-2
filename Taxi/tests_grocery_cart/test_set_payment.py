import copy

import pytest

from tests_grocery_cart import common
from tests_grocery_cart.plugins import keys

BASIC_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': common.UPDATE_IDEMPOTENCY_TOKEN,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}


@pytest.mark.parametrize('payment_method_id', ['test_payment_method_id', None])
@pytest.mark.parametrize(
    'payment_method_meta',
    [
        {
            'card': {
                'issuer_country': 'USA',
                'verified': True,
                'is_yandex_card': True,
            },
        },
        None,
    ],
)
async def test_basic(
        taxi_grocery_cart,
        overlord_catalog,
        cart,
        payment_method_id,
        payment_method_meta,
        grocery_coupons,
        grocery_p13n,
):
    payment_method_type = 'test_payment_method_type'

    overlord_catalog.add_product(product_id='test_item', price='345')
    await cart.modify({'test_item': {'p': 345, 'q': 1}})

    assert grocery_p13n.discount_modifiers_times_called == 1
    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-payment',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': cart.cart_id,
            'payment_method': {
                'type': payment_method_type,
                'id': payment_method_id,
                'meta': payment_method_meta,
            },
            'cart_version': 1,
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers={
            'X-Idempotency-Token': common.APPLY_PROMOCODE_IDEMPOTENCY_TOKEN,
            **BASIC_HEADERS,
            'User-Agent': keys.DEFAULT_USER_AGENT,
        },
    )
    assert response.status_code == 200

    cart_doc = cart.fetch_db()
    assert cart_doc.payment_method_type == payment_method_type
    assert cart_doc.payment_method_id == payment_method_id
    assert cart_doc.payment_method_meta == payment_method_meta

    assert grocery_p13n.discount_modifiers_times_called == 2


@pytest.mark.pgsql('grocery_cart', files=['localized_product.sql'])
@pytest.mark.parametrize('locale', ['ru', 'en', 'he'])
async def test_localized_products(
        taxi_grocery_cart, overlord_catalog, locale, load_json,
):
    localized = load_json('expected_product_localization.json')
    payment_method_type = 'test_payment_method_type'

    overlord_catalog.add_product(product_id='localized_product', price='345')

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-payment',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee005',
            'payment_method': {
                'type': payment_method_type,
                'id': 'test_payment_method_id',
            },
            'cart_version': 1,
        },
        headers={
            **BASIC_HEADERS,
            'X-Idempotency-Token': common.APPLY_PROMOCODE_IDEMPOTENCY_TOKEN,
            'X-YaTaxi-User': 'eats_user_id=12345',
            'X-YaTaxi-Session': 'eats:123',
            'X-Request-Language': locale,
        },
    )
    assert response.status_code == 200

    item = response.json()['items'][0]
    assert item['title'] == localized[locale]['title']
    assert item['subtitle'] == localized[locale]['subtitle']


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        user_api,
        has_personal_phone_id,
):
    payment_method_type = 'test_payment_method_type'

    headers = copy.deepcopy(BASIC_HEADERS)
    headers['X-Yandex-UID'] = 'some_uid'
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    overlord_catalog.add_product(product_id='test_item', price='345')
    await cart.modify({'test_item': {'p': 345, 'q': 1}})

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-payment',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': cart.cart_id,
            'payment_method': {'type': payment_method_type},
            'cart_version': 1,
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert user_api.times_called == (1 if has_personal_phone_id else 0)


@common.GROCERY_ORDER_CYCLE_ENABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
async def test_order_flow_exp(
        taxi_grocery_cart, overlord_catalog, cart, experiments3,
):
    payment_method_type = 'card'
    issuer = 'RUS'

    overlord_catalog.add_product(product_id='test_item', price='345')
    await cart.modify({'test_item': {'p': 345, 'q': 1}})

    exp3_recorder = experiments3.record_match_tries(
        'grocery_order_flow_version',
    )
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-payment',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': cart.cart_id,
            'payment_method': {
                'type': payment_method_type,
                'meta': {'card': {'issuer_country': issuer}},
            },
            'cart_version': 1,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200

    exp3_matches = await exp3_recorder.get_match_tries(1)
    assert exp3_matches[0].kwargs['card_issuer_country'] == issuer
    assert exp3_matches[0].kwargs['payment_method_type'] == payment_method_type
