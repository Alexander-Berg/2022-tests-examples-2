from taxi.internal.payment_kit import pool
from taxi.util import decimal

import pytest


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'taximeter_cost,sum_of_costs,max_diff,expected_expected_cost', [
        # commission
        (
            decimal.Decimal(1000),
            decimal.Decimal(1500),
            decimal.Decimal(500),
            decimal.Decimal('1425.90267004180000'),
        ),
        # large value
        (
            decimal.Decimal(1000),
            decimal.Decimal(1),
            decimal.Decimal(2000),
            decimal.Decimal('770.096058277090000'),
        ),
        # large value
        (
            decimal.Decimal(1),
            decimal.Decimal(1000),
            decimal.Decimal(2000),
            decimal.Decimal('2.4'),
        ),
        # max_diff is 40
        (
            decimal.Decimal(1000),
            decimal.Decimal(1500),
            decimal.Decimal(40),
            decimal.Decimal('1460'),
        ),
        # subvention
        (
            decimal.Decimal(1000),
            decimal.Decimal(800),
            decimal.Decimal(500),
            decimal.Decimal('841.2669585956000'),
        ),
        # max_diff is 40
        (
            decimal.Decimal(1000),
            decimal.Decimal(800),
            decimal.Decimal(40),
            decimal.Decimal('840'),
        ),
    ]
)
def test_get_expected_cost(
        taximeter_cost, sum_of_costs, max_diff, expected_expected_cost):
    actual_expected_cost = pool.get_expected_cost(
        taximeter_cost=taximeter_cost,
        sum_of_costs=sum_of_costs,
        ks=decimal.Decimal('2.7'),
        kc=decimal.Decimal('0.4'),
        min_rel_profit=decimal.Decimal('0.77'),
        max_rel_profit=decimal.Decimal('2.4'),
        max_diff=max_diff,
    )
    assert actual_expected_cost == expected_expected_cost
