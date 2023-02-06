import pytest

from tests_grocery_payments_tracking import experiments
from tests_grocery_payments_tracking import headers

CART_ID = '00000000-0000-0000-0000-d98013100500'
CART_VERSION = 22


@pytest.fixture(name='lavka_check_tracking')
async def _lavka_check_tracking(taxi_grocery_payments_tracking):
    async def _inner(expected_code=200, cart_id=CART_ID):
        request = {'cart_id': cart_id, 'cart_version': CART_VERSION}

        response = await taxi_grocery_payments_tracking.post(
            '/lavka/v1/payments-tracking/v1/check-tracking',
            json=request,
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == expected_code

        return response.json()

    return _inner


@pytest.mark.parametrize(
    'exp_enabled, verified, need_tracking_payment',
    [
        (False, None, False),
        (False, True, False),
        (False, False, True),
        (True, None, True),
    ],
)
async def test_basic(
        experiments3,
        lavka_check_tracking,
        grocery_cart,
        exp_enabled,
        verified,
        need_tracking_payment,
):
    experiments.set_payment_tracking_enabled(experiments3, exp_enabled)
    grocery_cart.set_cart_data(cart_id=CART_ID, cart_version=CART_VERSION)
    grocery_cart.set_payment_method(
        {
            'type': 'card',
            'id': 'test_payment_method_id',
            'meta': {'card': {'verified': verified}},
        },
    )

    response = await lavka_check_tracking()

    assert need_tracking_payment == response['need_track_payment']


async def test_not_found(lavka_check_tracking, grocery_cart):
    grocery_cart.default_cart.set_error_code(
        handler='cart_retrieve_raw', code=404,
    )

    await lavka_check_tracking(expected_code=404)


async def test_bad_version(lavka_check_tracking, grocery_cart):
    grocery_cart.set_cart_data(cart_id=CART_ID, cart_version=CART_VERSION + 1)

    response = await lavka_check_tracking(expected_code=409)

    assert response['code'] == 'WRONG_CART_VERSION'


async def test_kwargs(lavka_check_tracking, grocery_cart, experiments3):
    payment_type = 'applepay'
    experiments.set_payment_tracking_enabled(experiments3, enabled=True)
    exp3_recorder = experiments3.record_match_tries(
        'grocery_orders_payment_tracking_enabled',
    )

    grocery_cart.set_cart_data(cart_id=CART_ID, cart_version=CART_VERSION)
    grocery_cart.set_payment_method(
        {'type': payment_type, 'id': 'test_payment_method_id'},
    )

    await lavka_check_tracking()

    exp3_matches = await exp3_recorder.get_match_tries(ensure_ntries=1)
    exp3_kwargs = exp3_matches[0].kwargs

    assert exp3_kwargs['payment_method_type'] == payment_type
