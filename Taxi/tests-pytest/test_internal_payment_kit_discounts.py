import datetime

from taxi.internal import dbh
from taxi.internal.payment_kit import discounts
from taxi.util import math_numbers

import pytest

import assertions


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'cost,driver_cost,toll_road_cost,minimal_cost,max_value,expected_discount',
    [
        (
            150,
            200,
            None,
            99,
            math_numbers.INFINITY,
            '50.00',
        ),
        # restricted by max_value
        (
            150,
            200,
            None,
            99,
            30,
            '30.00',
        ),
        # not restricted by max_value
        (
            150,
            200,
            None,
            99,
            80,
            '50.00',
        ),
        # toll_road_cost is not empty
        (
            150,
            200,
            50,
            100,
            math_numbers.INFINITY,
            '0',
        ),
        # no driver_cost
        (
            150,
            None,
            None,
            100,
            math_numbers.INFINITY,
            '0',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTIONS_DISCOUNT_LIMIT_FOR_ORDERS_AFTER='2000-01-01 00:00:00',
)
@pytest.inline_callbacks
def test_get_discount(
        cost,
        driver_cost,
        toll_road_cost,
        minimal_cost,
        max_value,
        expected_discount,
):
    order = dbh.orders.Doc({})
    order.cost = cost
    if toll_road_cost:
        order['toll_road'] = {'toll_road_price': toll_road_cost}
    order.request.due = datetime.datetime(2017, 6, 23)
    order.driver_cost.cost = driver_cost
    discount_class = yield discounts.get_class('subvention-fix')
    if not isinstance(expected_discount, str):
        with pytest.raises(expected_discount):
            yield discount_class.get_discount(order, minimal_cost, max_value)
    else:
        actual_discount = yield discount_class.get_discount(
            order, minimal_cost, max_value,
        )
        assertions.assert_decimal_equal(
            actual_discount.value, expected_discount,
        )
