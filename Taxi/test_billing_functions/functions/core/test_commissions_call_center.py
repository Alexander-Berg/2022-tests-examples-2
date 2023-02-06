import decimal

import pytest

from billing_functions.functions.core.commissions import call_center
from billing_functions.repositories import commission_agreements as ca


@pytest.mark.parametrize(
    'source,agreement_attrs,call_center_cost,use_call_center_cost,expected',
    (
        # source missed
        (None, None, None, False, decimal.Decimal()),
        # agreement absent, pricing not activated
        ('call_center', None, None, False, decimal.Decimal()),
        # agreement from base commission rule, pricing not activated
        (
            'call_center',
            {'rate': ca.RateFlat(value=decimal.Decimal('0.05'))},
            None,
            False,
            decimal.Decimal('6'),
        ),
        # category agreement absent, pricing activated
        (
            'call_center',
            None,
            decimal.Decimal('5.5'),
            True,
            decimal.Decimal('5.5'),
        ),
        # category agreement with rate, pricing activated
        (
            'call_center',
            {
                'rate': ca.RateFlat(value=decimal.Decimal('0.05')),
                'category': ca.Category(
                    kind='call_center', fields='call_center',
                ),
            },
            decimal.Decimal('5.5'),
            True,
            decimal.Decimal('6'),
        ),
        # category agreement with fixed value, pricing activated
        (
            'call_center',
            {
                'rate': ca.RateAbsolute(value=decimal.Decimal('3')),
                'category': ca.Category(
                    kind='call_center', fields='call_center',
                ),
            },
            decimal.Decimal('5.5'),
            True,
            decimal.Decimal('3'),
        ),
    ),
)
def test_call_center_calculate_surcharge(
        make_agreement,
        source,
        agreement_attrs,
        call_center_cost,
        use_call_center_cost,
        expected,
):
    agreement = (
        make_agreement(
            kind='call_center', group='call_center', **agreement_attrs,
        )
        if agreement_attrs is not None
        else None
    )
    call_center_data = (
        call_center.CallCenter(cost=call_center_cost)
        if call_center_cost
        else None
    )
    actual = call_center.calculate_surcharge(
        agreement=agreement,
        source=source,
        cost=decimal.Decimal(126),
        call_center=call_center_data,
        use_call_center_cost=use_call_center_cost,
    )
    assert actual == expected
