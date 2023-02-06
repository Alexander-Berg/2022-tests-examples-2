import pytest

from . import configs
from . import experiments
from . import headers
from . import models
from . import order_v2_submit_consts


@experiments.available_payment_types_ext(
    {
        models.Country.Russia.country_iso3: ['card'],
        models.Country.France.country_iso3: ['corp'],
    },
    ['badge'],
)
@pytest.mark.parametrize(
    'country_iso3,'
    + 'cart_payment_method_type,'
    + 'cart_payment_method_id,'
    + 'expected_response,'
    + 'expected_error_message',
    [
        (
            models.Country.Russia.country_iso3,
            'applepay',
            'id',
            400,
            'payment type: applepay is not supported',
        ),
        (models.Country.France.country_iso3, 'corp', 'id', 200, None),
        (
            models.Country.France.country_iso3,
            'corp',
            order_v2_submit_consts.BADGE_PAYMENT_METHOD_ID,
            400,
            'payment type: badge is not supported',
        ),
        (
            models.Country.Israel.country_iso3,
            'corp',
            order_v2_submit_consts.BADGE_PAYMENT_METHOD_ID,
            200,
            None,
        ),
    ],
)
async def test_submit_payment_types(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        yamaps,
        personal,
        country_iso3,
        cart_payment_method_type,
        cart_payment_method_id,
        expected_response,
        expected_error_message,
):
    grocery_cart.set_depot_id(depot_id=order_v2_submit_consts.DEPOT_ID)
    grocery_cart.set_payment_method(
        {'type': cart_payment_method_type, 'id': cart_payment_method_id},
    )
    grocery_depots.add_depot(
        legacy_depot_id=order_v2_submit_consts.DEPOT_ID,
        country_iso3=country_iso3,
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit',
        json=order_v2_submit_consts.SUBMIT_BODY,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == expected_response

    if expected_error_message is not None:
        assert response.json()['message'] == expected_error_message


@configs.GROCERY_PAYMENT_METHOD_VALIDATION
@experiments.available_payment_types_ext(
    {
        models.Country.Russia.country_iso3: ['corp', 'badge'],
        models.Country.France.country_iso3: ['badge'],
        models.Country.Israel.country_iso3: ['corp'],
    },
    ['card'],
)
@pytest.mark.parametrize(
    'country_iso3, pm_id, pm_type, expected_type, expected_response',
    [
        (models.Country.Russia.country_iso3, 'corp_id', 'corp', 'corp', 200),
        (
            models.Country.Russia.country_iso3,
            order_v2_submit_consts.BADGE_PAYMENT_METHOD_ID,
            'corp',
            'badge',
            200,
        ),
        (models.Country.France.country_iso3, 'corp_id', 'corp', None, 400),
        (
            models.Country.France.country_iso3,
            order_v2_submit_consts.BADGE_PAYMENT_METHOD_ID,
            'corp',
            'badge',
            200,
        ),
        (models.Country.Israel.country_iso3, 'corp_id', 'corp', 'corp', 200),
        (
            models.Country.Israel.country_iso3,
            order_v2_submit_consts.BADGE_PAYMENT_METHOD_ID,
            'corp',
            None,
            400,
        ),
        (
            models.Country.GreatBritain.country_iso3,
            'corp_id',
            'corp',
            None,
            400,
        ),
        (
            models.Country.GreatBritain.country_iso3,
            order_v2_submit_consts.BADGE_PAYMENT_METHOD_ID,
            'corp',
            None,
            400,
        ),
    ],
)
async def test_corp_badge_pm_validation(
        taxi_grocery_orders,
        grocery_cart,
        grocery_payments,
        grocery_depots,
        country_iso3,
        pm_id,
        pm_type,
        expected_type,
        expected_response,
):
    grocery_cart.set_payment_method({'type': pm_type, 'id': pm_id})
    grocery_depots.add_depot(
        legacy_depot_id=order_v2_submit_consts.DEPOT_ID,
        country_iso3=country_iso3,
    )

    grocery_payments.check_validate(
        payment_methods=[{'id': pm_id, 'type': expected_type}],
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit',
        json=order_v2_submit_consts.SUBMIT_BODY,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == expected_response
