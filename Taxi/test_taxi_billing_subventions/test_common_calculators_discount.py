import decimal

import pytest

from taxi import billing

from taxi_billing_subventions.common import models
from taxi_billing_subventions.common.calculators import discount

_MAX_DISCOUNT = billing.Money(decimal.Decimal(1000), 'RUB')
_UNKNOWN_MPH_LIMIT = None


def _make_money(money_str: str) -> billing.Money:
    amount_str, currency = money_str.split()
    amount = decimal.Decimal(amount_str)
    return billing.Money(amount, currency)


def _make_amendments(money_str: str, reason: str):
    return models.order.Amendment(value=_make_money(money_str), reason=reason)


def _make_discount_details(money_str, amendments):
    return models.order.DiscountDetails(
        discount=_make_money(money_str), amendments=amendments,
    )


@pytest.mark.parametrize(
    'order_json, expected_details',
    [
        ('order_with_discount.json', _make_discount_details('10 RUB', [])),
        (
            'order_with_discount_and_declines.json',
            _make_discount_details(
                '1000 RUB', [_make_amendments('100.12 RUB', 'reason')],
            ),
        ),
        (
            'order_without_discount_value.json',
            _make_discount_details('0 RUB', []),
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_details(order_json, expected_details, load_py_json_dir):
    order: models.calculators.Order = load_py_json_dir(
        'test_get_details', order_json,
    )
    actual_details = discount.get_details(order=order)
    assert expected_details == actual_details
