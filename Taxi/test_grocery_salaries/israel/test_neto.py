# flake8: noqa: E501
from decimal import Decimal

import pandas as pd

from grocery_salaries.salaries.calculations.calculators import neto


async def test_set_shift_hours():
    result = pd.DataFrame(
        [
            (
                10,
                '2021-12-20',
                Decimal('5.0'),
                '2021-12-20 17:23:34',
                Decimal('5.0'),
                Decimal('0.0'),
                Decimal('0.0'),
            ),
            (
                10,
                '2021-12-20',
                Decimal('4.0'),
                '2021-12-20 18:23:34',
                Decimal('3.0'),
                Decimal('1.0'),
                Decimal('0.0'),
            ),
            (
                10,
                '2021-12-20',
                Decimal('5.0'),
                '2021-12-20 18:33:34',
                Decimal('0.0'),
                Decimal('1.0'),
                Decimal('4.0'),
            ),
            (
                10,
                '2021-12-21',
                Decimal('3.8'),
                '2021-12-21 22:33:34',
                Decimal('3.8'),
                Decimal('0.0'),
                Decimal('0.0'),
            ),
            (
                10,
                '2021-12-21',
                Decimal('7.2'),
                '2021-12-21 22:34:34',
                Decimal('4.2'),
                Decimal('2.0'),
                Decimal('1.0'),
            ),
            (
                11,
                '2021-12-19',
                Decimal('9.6'),
                '2021-12-19 14:35:34',
                Decimal('8.0'),
                Decimal('1.6'),
                Decimal('0.0'),
            ),
            (
                11,
                '2021-12-19',
                Decimal('0.5'),
                '2021-12-19 14:36:34',
                Decimal('0.0'),
                Decimal('0.4'),
                Decimal('0.1'),
            ),
        ],
        columns=[
            'courier_id',
            'date',
            'hours',
            'lcl_fact_started_dttm',
            'hour100',
            'hour125',
            'hour150',
        ],
    )

    calculator = object.__new__(neto.Calculator)
    calculator.shifts = result[
        ['courier_id', 'date', 'hours', 'lcl_fact_started_dttm']
    ].copy()
    calculator._set_shift_hours()  # pylint: disable=W0212
    pd.testing.assert_frame_equal(calculator.shifts, result)


def test_calc_shift_total_per_order():
    result = pd.DataFrame(
        [
            (
                Decimal('1.0'),
                Decimal('2.0'),
                Decimal('3'),
                Decimal('4'),
                Decimal('1.0'),
                Decimal('2.0'),
                Decimal('3.0'),
                Decimal('4.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('3.0'),
                Decimal('8.0'),
                Decimal('11.0'),
                Decimal('11.75'),
            ),
            (
                Decimal('15.0'),
                Decimal('20.0'),
                Decimal('11'),
                Decimal('0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('1.0'),
                Decimal('2.0'),
                Decimal('3.0'),
                Decimal('4.0'),
                Decimal('165.0'),
                Decimal('0.0'),
                Decimal('165.0'),
                Decimal('11.75'),
            ),
            (
                Decimal('15.0'),
                Decimal('20.0'),
                Decimal('0'),
                Decimal('11'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('20.0'),
                Decimal('20.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('220.0'),
                Decimal('220.0'),
                Decimal('500.0'),
            ),
            (
                Decimal('15.0'),
                Decimal('15.0'),
                Decimal('11'),
                Decimal('11'),
                Decimal('10.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('10.0'),
                Decimal('20.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('20.0'),
                Decimal('165.0'),
                Decimal('165.0'),
                Decimal('330.0'),
                Decimal('750.0'),
            ),
        ],
        columns=[
            'order_rate_mw',
            'order_rate_we',
            'orders_mw',
            'orders_we',
            'hour_rate_mw',
            'hour100_mw',
            'hour125_mw',
            'hour150_mw',
            'hour_rate_we',
            'hour100_we',
            'hour125_we',
            'hour150_we',
            'total_po_mw',
            'total_po_we',
            'total_po',
            'total_ph',
        ],
    )

    calculator = object.__new__(neto.Calculator)
    calculator.shifts = result.drop(
        columns=['total_po_mw', 'total_po_we', 'total_po', 'total_ph'],
    ).copy()
    calculator._calculate_shifts_income()  # pylint: disable=W0212
    pd.testing.assert_frame_equal(calculator.shifts, result)


def test_calc_salary():
    result = pd.DataFrame(
        [
            (
                Decimal('1.0'),
                Decimal('2.0'),
                Decimal('0.0'),
                Decimal('3.0'),
                Decimal('4.0'),
                Decimal('0.0'),
                Decimal('10.0'),
            ),
            (
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('0.0'),
                Decimal('10.0'),
                Decimal('10.0'),
                Decimal('0.0'),
                Decimal('40.0'),
            ),
            (
                Decimal('1.5'),
                Decimal('2.3'),
                Decimal('0.0'),
                Decimal('7.6'),
                Decimal('5.8'),
                Decimal('0.0'),
                Decimal('17.2'),
            ),
            (
                Decimal('12.33'),
                Decimal('42.7'),
                Decimal('0.0'),
                Decimal('34.5'),
                Decimal('87.3'),
                Decimal('0.0'),
                Decimal('176.83'),
            ),
        ],
        columns=[
            'total_ph',
            'total_po',
            'rainy_bonus_po',
            'tips',
            'adjustments',
            'daily_fare',
            'salary',
        ],
    )

    calculator = object.__new__(neto.Calculator)
    calculator.payouts_by_day = result.drop(columns='salary').copy()
    calculator._calculate_total_income()  # pylint: disable=W0212
    pd.testing.assert_frame_equal(calculator.payouts_by_day, result)
