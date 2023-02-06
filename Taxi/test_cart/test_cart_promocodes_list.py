import copy

import pytest

from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys

YANDEX_UID = '555'
PHONE_ID = 'phone_id'
PERSONAL_PHONE_ID = 'personal_phone_id'

HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': 'update-token',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Yandex-Uid': YANDEX_UID,
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-YaTaxi-User': f'personal_phone_id={PERSONAL_PHONE_ID}',
}

EXPIRE_AT = '2020-11-12T13:00:50.283761+00:00'

DEFAULT_COUPONS_LIST_RESPONSE = {
    'coupons': [
        {
            'title': 'Промокод на 100 рублей',
            'subtitle': 'При заказе от 500 рублей',
            'valid': True,
            'promocode': 'LAVKA100',
            'type': 'percent',
            'value': '10',
            'limit': '100',
            'expire_at': EXPIRE_AT,
            'currency_code': 'RUB',
            'reason_type': 'referral_reward',
            'min_cart_cost': '500',
            'min_cart_cost_template': '500 $SIGN$$CURRENCY$',
            'value_template': '10 $SIGN$$CURRENCY$',
        },
        {
            'title': 'Промокод на 200 рублей',
            'valid': False,
            'promocode': 'LAVKA200',
            'error_message': 'На заказ от 500 рублей',
            'type': 'fixed',
            'value': '200',
        },
    ],
}


@pytest.mark.parametrize('cart_available', [True, False])
async def test_basic(
        cart, overlord_catalog, grocery_coupons, cart_available, grocery_p13n,
):
    await cart.modify(
        {'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE}}, headers=HEADERS,
    )

    overlord_catalog.add_product(
        product_id='test-item', price=str(keys.DEFAULT_PRICE),
    )

    assert grocery_p13n.discount_modifiers_times_called == 1

    grocery_coupons.set_list_response(
        response_body=DEFAULT_COUPONS_LIST_RESPONSE,
    )

    if cart_available:
        grocery_coupons.check_list_request(
            cart_id=cart.cart_id,
            cart_version=cart.cart_version,
            cart_cost=str(keys.DEFAULT_PRICE),
            depot_id='0',
        )
    else:
        grocery_coupons.check_list_request(
            cart_id=None,
            cart_version=None,
            cart_cost=None,
            depot_id='0',
            skip_cart_check=True,
        )

    response = await cart.promocodes_list(
        headers=HEADERS, required_status=200, include_cart_info=cart_available,
    )

    assert response['promocodes'] == DEFAULT_COUPONS_LIST_RESPONSE['coupons']
    if cart_available:
        assert grocery_p13n.discount_modifiers_times_called == 2
    else:
        assert grocery_p13n.discount_modifiers_times_called == 1


@pytest.mark.parametrize(
    'has_personal_phone_id, response_code', [(True, 200), (False, 400)],
)
async def test_no_phone_id(
        user_api, grocery_coupons, cart, has_personal_phone_id, response_code,
):
    headers = copy.deepcopy(HEADERS)
    del headers['X-YaTaxi-PhoneId']

    if not has_personal_phone_id:
        del headers['X-YaTaxi-User']

    grocery_coupons.set_list_response(
        response_body=DEFAULT_COUPONS_LIST_RESPONSE,
    )

    await cart.promocodes_list(headers=headers, required_status=response_code)
    assert user_api.times_called == (1 if has_personal_phone_id else 0)


@pytest.mark.parametrize(
    'yandex_uid, personal_phone_id, newbie_scoring_enabled',
    [
        ('yandex-uid', 'personal-phone-id', False),
        ('yandex-uid', '', True),
        (None, 'personal-phone-id', True),
        ('yandex-uid', 'personal-phone-id', True),
    ],
)
async def test_score_newbie(
        grocery_coupons,
        cart,
        processing,
        experiments3,
        yandex_uid,
        personal_phone_id,
        newbie_scoring_enabled,
):
    app_info = (
        'app_brand=yataxi,app_ver3=0,device_make=xiaomi,'
        'app_name=mobileweb_android,app_build=release,'
        'device_model=redmi 6,app_ver2=9,app_ver1=4,platform_ver1=9'
    )
    headers = {
        'X-Yandex-UID': yandex_uid,
        'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}',
        'X-YaTaxi-PhoneId': PHONE_ID,
        'X-Request-Application': app_info,
    }
    experiments.grocery_api_enable_newbie_scoring(
        experiments3=experiments3, enabled=newbie_scoring_enabled,
    )

    grocery_coupons.set_list_response(
        response_body=DEFAULT_COUPONS_LIST_RESPONSE,
    )

    await cart.promocodes_list(headers=headers)

    events = list(processing.events(scope='grocery', queue='users'))

    if newbie_scoring_enabled and yandex_uid and personal_phone_id:
        assert len(events) == 1
        event = events[0]

        assert event.payload['personal_phone_id'] == personal_phone_id
        assert event.payload['user_identity'] == {
            'yandex_uid': yandex_uid,
            'bound_yandex_uids': [],
        }
        assert event.payload['range'] == {'count': 1}
        assert event.payload['reason'] == 'score_newbie'
        assert 'event_policy' not in event.payload
    else:
        assert not events
