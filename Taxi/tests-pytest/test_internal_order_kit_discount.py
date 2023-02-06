import collections
import datetime

from taxi.core import async
from taxi.internal import dbh
from taxi.internal.order_kit import discount
from taxi.util import math_numbers

import pytest

import assertions


TariffInfo = collections.namedtuple(
    'TariffInfo',
    [
        'tariff_id',
        'category_id',
        'tariff_class',
        'tariff_currency',
        'is_synchronizable',
        'zone_ids',
    ]
)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'cost,driver_cost,minimal_cost,max_value,expected_discount',
    [
        (
            150,
            200,
            99,
            math_numbers.INFINITY,
            '50.00',
        ),
        # restricted by max_value
        (
            150,
            200,
            99,
            30,
            '30.00',
        ),
        # not restricted by max_value
        (
            150,
            200,
            99,
            80,
            '50.00',
        ),
        # no driver_cost
        (
            150,
            None,
            100,
            math_numbers.INFINITY,
            '0',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTIONS_DISCOUNT_LIMIT_FOR_ORDERS_AFTER='2000-01-01 00:00:00'
)
@pytest.inline_callbacks
def test_get_discount(
        patch, cost, driver_cost, minimal_cost, max_value, expected_discount):
    tariff = dbh.tariffs.Doc({})
    tariff._id = 'tariff_pk'
    tariff.minimal = minimal_cost
    tariff.currency = 'RUB'
    order_proc = dbh.order_proc.Doc({})
    order_proc.cost = cost
    order_proc.order.cost = cost
    order_proc.order.request.due = datetime.datetime(2017, 6, 23)
    order_proc.candidates = [order_proc.new_candidate(
        alias_id='alias_id',
        driver_id='driver_id',
        car_number='car_number',
        driver_license='license',
        driver_license_personal_id='license_id',
        tariff_info=TariffInfo(
            tariff_id='tariff_id',
            category_id='tariff_pk',
            tariff_class='XXX',
            tariff_currency='RUB',
            is_synchronizable=False,
            zone_ids=None,
        )
    )]
    order_proc.performer.candidate_index = 0
    order_proc.order.driver_cost.cost = driver_cost

    @patch('taxi.internal.dbh.tariffs.find_category_by_id')
    @async.inline_callbacks
    def find_category_by_id(*args, **kwargs):
        yield
        async.return_value(tariff)

    @patch('taxi.internal.mph.check_single_order')
    @async.inline_callbacks
    def check_single_order(*args, **kwargs):
        yield
        async.return_value(None)

    @patch('taxi.internal.payment_kit.discounts.get_max_discount_payback')
    def get_max_discount_payback(*args, **kwars):
        return max_value

    actual_discount = yield discount.calc_discount(order_proc)
    if not isinstance(expected_discount, str):
        assert actual_discount is None
    else:
        assertions.assert_decimal_equal(
            actual_discount.value,
            expected_discount,
        )
