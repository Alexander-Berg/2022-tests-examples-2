# flake8: noqa: E501
from decimal import Decimal

import pandas as pd
import pytest

from grocery_salaries.salaries.calculations.calculators import selfemployed
from grocery_salaries.salaries.calculations.data_source import (
    SaleforceDataSource,
)


@pytest.mark.parametrize(
    'tax_system, result',
    [
        ('УСН', Decimal('0')),
        ('USN', Decimal('0')),
        ('ОСН', Decimal('0.17')),
        ('OCH', Decimal('0.17')),
        ('OSN', Decimal('0.17')),
        ('усн', Decimal('0')),
        ('usn', Decimal('0')),
        ('осн', Decimal('0.17')),
        ('och', Decimal('0.17')),
        ('osn', Decimal('0.17')),
        ('OСН', Decimal('0.17')),
    ],
)
def test_get_vat(tax_system, result, cron_context, mock_jns):
    data_source = SaleforceDataSource(cron_context)
    get_vat = data_source._get_vat_calculator()  # pylint: disable=W0212
    assert get_vat(tax_system) == result
    assert not mock_jns.sent


def test_get_vat_invalid(cron_context, mock_jns):
    tax_system = 'aaa'
    result = 0
    data_source = SaleforceDataSource(cron_context)
    get_vat = data_source._get_vat_calculator()  # pylint: disable=W0212
    assert get_vat(tax_system) == result
    assert mock_jns.sent


def test_calc_shift_total():
    result = pd.DataFrame(
        [
            (
                Decimal('1.0'),
                Decimal('2.0'),
                Decimal('3.0'),
                Decimal('4.0'),
                Decimal('5.0'),
                Decimal('6.0'),
                Decimal('7.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('5.0'),
                Decimal('12.0'),
                Decimal('21.0'),
                Decimal('32.0'),
                Decimal('17.0'),
                Decimal('53.0'),
                Decimal('70.0'),
            ),
            (
                Decimal('45.0'),
                Decimal('50.0'),
                Decimal('15.0'),
                Decimal('20.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('11.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('360.0'),
                Decimal('0.0'),
                Decimal('165.0'),
                Decimal('0.0'),
                Decimal('360.0'),
                Decimal('165.0'),
                Decimal('525.0'),
            ),
            (
                Decimal('45.0'),
                Decimal('50.0'),
                Decimal('15.0'),
                Decimal('20.0'),
                Decimal('0.0'),
                Decimal('8.0'),
                Decimal('0.0'),
                Decimal('11.0'),
                Decimal('0.0'),
                Decimal('0.0'),
                Decimal('400.0'),
                Decimal('0.0'),
                Decimal('220.0'),
                Decimal('400.0'),
                Decimal('220.0'),
                Decimal('620.0'),
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
            'rainy_bonus_po',
            'total_ph_mw',
            'total_ph_we',
            'total_po_mw',
            'total_po_we',
            'total_ph',
            'total_po',
            'total',
        ],
    )

    calculator = object.__new__(selfemployed.Calculator)
    calculator.shifts = result.drop(
        columns=[
            'total_ph_mw',
            'total_ph_we',
            'total_po_mw',
            'total_po_we',
            'total_ph',
            'total_po',
            'total',
        ],
    ).copy()

    calculator._calculate_shifts_income()  # pylint: disable=W0212
    pd.testing.assert_frame_equal(calculator.shifts, result)
