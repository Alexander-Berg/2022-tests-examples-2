import decimal

import pytest

from billing_functions.functions.core.subventions import geo_booking


@pytest.mark.parametrize(
    'rate_free, rate_on_order, free_min, on_order_min, expected_result',
    [
        (decimal.Decimal(1), decimal.Decimal(2), 3, 4, decimal.Decimal(11)),
        (None, decimal.Decimal(3), 5, 6, decimal.Decimal(18)),
        (decimal.Decimal(4), None, 7, 8, decimal.Decimal(28)),
    ],
)
def test_calculate_online_cost(
        rate_free, rate_on_order, free_min, on_order_min, expected_result,
):
    actual_result = geo_booking.calculate_online_cost(
        rate_free, rate_on_order, free_min, on_order_min,
    )
    assert actual_result == expected_result
