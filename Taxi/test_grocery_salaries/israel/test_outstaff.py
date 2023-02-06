# flake8: noqa: E501
from decimal import Decimal

import pandas as pd

from grocery_salaries.salaries.calculations.calculators import outstaff


def test_calculate_shifts_income():
    result = pd.DataFrame(
        [
            (
                Decimal('1.0'),
                Decimal('2.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('3.0'),
                Decimal('4.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('3.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('11.0'),
                Decimal('0.0'),
            ),
            (
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('1.0'),
                Decimal('2.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('3.0'),
                Decimal('4.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('3.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('11.0'),
            ),
            (
                Decimal('45.0'),
                Decimal('15.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('360.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('360.0'),
                Decimal('0.0'),
            ),
            (
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('45.0'),
                Decimal('15.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('360.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('360.0'),
            ),
            (
                Decimal('45.0'),
                Decimal('15.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('120.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('120.0'),
                Decimal('0.0'),
            ),
            (
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('45.0'),
                Decimal('15.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('120.0'),
                Decimal('0.0'),
                Decimal('120.0'),
            ),
            (
                Decimal('45.0'),
                Decimal('15.0'),
                Decimal('50.0'),
                Decimal('20.0'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('450.0'),
                Decimal('150.0'),
                Decimal('500.0'),
                Decimal('200.0'),
                Decimal('600.0'),
                Decimal('700.0'),
            ),
            (
                Decimal('50.0'),
                Decimal('20.0'),
                Decimal('45.0'),
                Decimal('15.0'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('500.0'),
                Decimal('200.0'),
                Decimal('450.0'),
                Decimal('150.0'),
                Decimal('700.0'),
                Decimal('600.0'),
            ),
        ],
        columns=[
            'hour_rate_mw',
            'hour_rate_we',
            'order_rate_mw',
            'order_rate_we',
            'hours_mw',
            'hours_we',
            'orders_mw',
            'orders_we',
            'total_ph_mw',
            'total_ph_we',
            'total_po_mw',
            'total_po_we',
            'total_ph',
            'total_po',
        ],
    )
    calculator = object.__new__(outstaff.Calculator)
    calculator.shifts = result.drop(
        columns=[
            'total_ph_mw',
            'total_ph_we',
            'total_ph',
            'total_po_mw',
            'total_po_we',
            'total_po',
        ],
    ).copy()
    calculator._calculate_shifts_income()  # pylint: disable=W0212
    pd.testing.assert_frame_equal(calculator.shifts, result)


def test_calculate_total_income():
    result = pd.DataFrame(
        [
            (
                Decimal('1.0'),
                Decimal('2.0'),
                Decimal('0.0'),
                Decimal('3.0'),
                Decimal('4.0'),
                Decimal('10.0'),
            ),
            (
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('0.0'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('40.0'),
            ),
            (
                Decimal('1.5'),
                Decimal('2.1'),
                Decimal('0.0'),
                Decimal('7.6'),
                Decimal('5.8'),
                Decimal('17.0'),
            ),
            (
                Decimal('12.33'),
                Decimal('22.34'),
                Decimal('0.0'),
                Decimal('34.5'),
                Decimal('87.3'),
                Decimal('156.47'),
            ),
        ],
        columns=[
            'total_ph',
            'total_po',
            'rainy_bonus_po',
            'tips',
            'adjustments',
            'salary',
        ],
    )

    calculator = object.__new__(outstaff.Calculator)
    calculator.payouts_by_day = result[
        ['total_ph', 'total_po', 'rainy_bonus_po', 'tips', 'adjustments']
    ].copy()
    calculator._calculate_total_income()  # pylint: disable=W0212
    pd.testing.assert_frame_equal(calculator.payouts_by_day, result)
