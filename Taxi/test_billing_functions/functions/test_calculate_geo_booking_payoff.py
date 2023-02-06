import decimal

import pytest

from billing_models.generated.models import taxi_geo_booking_shift as models

from billing_functions.functions import calculate_geo_booking_payoff

Query = calculate_geo_booking_payoff.Query


@pytest.mark.parametrize(
    'query, expected_payoff',
    [
        pytest.param(
            Query(
                min_online_minutes=decimal.Decimal(7),
                rule_type='add',
                rate_free_per_minute=decimal.Decimal(1),
                rate_on_order_per_minute=decimal.Decimal(2),
                free_minutes=3,
                on_order_minutes=4,
                income=decimal.Decimal(10),
                online_time=decimal.Decimal(7),
            ),
            models.GeoBookingPayoff(amount='11', online_cost='11'),
            id='enough online time for add',
        ),
        pytest.param(
            Query(
                min_online_minutes=decimal.Decimal(7),
                rule_type='add',
                rate_free_per_minute=decimal.Decimal(1),
                rate_on_order_per_minute=decimal.Decimal(2),
                free_minutes=3,
                on_order_minutes=4,
                income=decimal.Decimal(10),
                online_time=decimal.Decimal(6),
            ),
            models.GeoBookingPayoff(amount='0', online_cost='11'),
            id='not enough online time for add',
        ),
        pytest.param(
            Query(
                min_online_minutes=decimal.Decimal(7),
                rule_type='add',
                rate_free_per_minute=None,
                rate_on_order_per_minute=None,
                free_minutes=3,
                on_order_minutes=4,
                income=decimal.Decimal(10),
                online_time=decimal.Decimal(7),
            ),
            models.GeoBookingPayoff(amount='0', online_cost='0'),
            id='no rates',
        ),
        pytest.param(
            Query(
                min_online_minutes=decimal.Decimal(7),
                rule_type='guarantee',
                rate_free_per_minute=decimal.Decimal(1),
                rate_on_order_per_minute=decimal.Decimal(2),
                free_minutes=3,
                on_order_minutes=4,
                income=decimal.Decimal(10),
                online_time=decimal.Decimal(7),
            ),
            models.GeoBookingPayoff(amount='1', online_cost='11'),
            id='income is less than guarantee',
        ),
        pytest.param(
            Query(
                min_online_minutes=decimal.Decimal(7),
                rule_type='guarantee',
                rate_free_per_minute=decimal.Decimal(1),
                rate_on_order_per_minute=decimal.Decimal(2),
                free_minutes=3,
                on_order_minutes=4,
                income=decimal.Decimal(12),
                online_time=decimal.Decimal(7),
            ),
            models.GeoBookingPayoff(amount='0', online_cost='11'),
            id='income is greater than guarantee',
        ),
    ],
)
def test_calculate_bonus(query, expected_payoff):
    actual_payoff = calculate_geo_booking_payoff.execute(query)
    assert actual_payoff.serialize() == expected_payoff.serialize()
