import pytest

from order_notify.repositories.payment.payment_info import get_tips_percent
from order_notify.repositories.payment.payment_info import OrderPaymentTech


def test_type():
    payment_tech = OrderPaymentTech({'type': 'card'})
    assert payment_tech.type == 'card'


@pytest.mark.parametrize(
    'payment_tech, expected_accept',
    [
        pytest.param({}, False, id='None_need_accept'),
        pytest.param({'need_accept': False}, False, id='false_accept'),
        pytest.param({'need_accept': True}, True, id='true_accept'),
    ],
)
def test_need_accept(payment_tech, expected_accept):
    add_type(payment_tech)
    accept = OrderPaymentTech(payment_tech).need_accept
    assert accept == expected_accept


@pytest.mark.parametrize(
    'payment_tech, expected_tips',
    [
        pytest.param({}, 0, id='no_user_to_pay'),
        pytest.param({'user_to_pay': {}}, 0, id='no_tips'),
        pytest.param({'user_to_pay': {'tips': 213}}, 213, id='exist_tips'),
    ],
)
def test_tips(payment_tech, expected_tips):
    add_type(payment_tech)
    accept = OrderPaymentTech(payment_tech).tips
    assert accept == expected_tips


@pytest.mark.parametrize(
    'payment_tech, expected_cashback',
    [
        pytest.param({}, 0, id='no_user_to_pay'),
        pytest.param({'user_to_pay': {}}, 0, id='no_cashback'),
        pytest.param(
            {'user_to_pay': {'cashback': 213}}, 213, id='exist_cashback',
        ),
    ],
)
def test_cashback(payment_tech, expected_cashback):
    add_type(payment_tech)
    cashback = OrderPaymentTech(payment_tech).cashback
    assert cashback == expected_cashback


@pytest.mark.parametrize(
    'payment_tech, expected_cost_without_vat',
    [
        pytest.param({}, 0, id='no_without_vat_to_pay'),
        pytest.param({'without_vat_to_pay': {}}, 0, id='no_ride'),
        pytest.param(
            {'without_vat_to_pay': {'ride': 213}}, 213, id='exist_ride',
        ),
    ],
)
def test_cost_without_vat(payment_tech, expected_cost_without_vat):
    add_type(payment_tech)
    cost_without_vat = OrderPaymentTech(payment_tech).cost_without_vat
    assert cost_without_vat == expected_cost_without_vat


@pytest.mark.parametrize(
    'payment_tech, expected_cost_without_vat_with_tips',
    [
        pytest.param({}, 0, id='no_without_vat_to_pay'),
        pytest.param({'without_vat_to_pay': {}}, 0, id='no_ride_no_tips'),
        pytest.param(
            {'without_vat_to_pay': {'ride': 213}},
            213,
            id='exist_ride_no_tips',
        ),
        pytest.param(
            {'without_vat_to_pay': {'tips': 24}}, 24, id='no_ride_exist_tips',
        ),
        pytest.param(
            {'without_vat_to_pay': {'ride': 213, 'tips': 24}},
            237,
            id='exist_ride_exist_tips',
        ),
    ],
)
def test_cost_without_vat_with_tips(
        payment_tech, expected_cost_without_vat_with_tips,
):
    add_type(payment_tech)
    cost_without_vat = OrderPaymentTech(
        payment_tech,
    ).cost_without_vat_with_tips
    assert cost_without_vat == expected_cost_without_vat_with_tips


@pytest.mark.parametrize(
    'payment_tech, expected_cost',
    [
        pytest.param({}, 0, id='no_user_to_pay'),
        pytest.param({'user_to_pay': {}}, 0, id='empty_user_to_pay'),
        pytest.param({'user_to_pay': {'ride': 213}}, 213, id='ride'),
        pytest.param(
            {'user_to_pay': {'ride': 213, 'tips': 5}}, 218, id='ride_tips',
        ),
        pytest.param(
            {'user_to_pay': {'ride': 21, 'cashback': 3}},
            24,
            id='ride_cashback',
        ),
        pytest.param(
            {'user_to_pay': {'ride': 213, 'tips': 5, 'cashback': 27}},
            245,
            id='ride_tips_cashback',
        ),
        pytest.param({'user_to_pay': {'tips': 2}}, 2, id='tips'),
        pytest.param(
            {'user_to_pay': {'tips': 2, 'cashback': 132}},
            134,
            id='tips_cashback',
        ),
        pytest.param({'user_to_pay': {'cashback': 45}}, 45, id='cashback'),
    ],
)
def test_cost(payment_tech, expected_cost):
    add_type(payment_tech)
    cost = OrderPaymentTech(payment_tech).cost
    assert cost == expected_cost


def add_type(payment_tech: dict):
    payment_tech['type'] = 'cash'


@pytest.mark.parametrize(
    'credit_card, expected_tips_percent',
    [
        pytest.param(None, None, id='None_credit_card'),
        pytest.param({}, None, id='empty_credit_card'),
        pytest.param({'tips': {}}, None, id='empty_tips'),
        pytest.param(
            {'tips': {}, 'tips_perc_default': 10}, 10, id='tips_perc_default',
        ),
        pytest.param(
            {'tips': {'value': 15, 'type': 'percent'}},
            15,
            id='value_type_percent',
        ),
        pytest.param(
            {'tips': {'value': 17, 'type': 'bruh'}},
            None,
            id='value_type_not_percent',
        ),
        pytest.param({'tips': {'value': 15}}, 15, id='value'),
    ],
)
def test_get_tips_percent(credit_card, expected_tips_percent):
    tips_percent = get_tips_percent(credit_card)
    assert tips_percent == expected_tips_percent
