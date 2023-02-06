import datetime as dt
import decimal
import typing as tp

import pytest

from taxi_billing_subventions.common import db as common_db


@pytest.mark.parametrize(
    'from_currency, to_currency, date, expected_rate',
    [
        (
            'KZT',
            'USD',
            dt.date(2019, 3, 18),
            decimal.Decimal('0.002641938125809093551029034900'),
        ),
        (
            'KZT',
            'USD',
            dt.date(2019, 3, 25),
            decimal.Decimal('0.002656748140276301806588735388'),
        ),
        ('USD', 'KZT', dt.date(2019, 3, 18), decimal.Decimal('378.51')),
        ('USD', 'KZT', dt.date(2019, 3, 25), decimal.Decimal('376.4')),
        ('RUB', 'RUB', dt.date(2019, 3, 25), decimal.Decimal('1')),
        ('BYN', 'XOF', dt.date(2019, 3, 25), None),
    ],
)
@pytest.mark.filldb(currency_rates='for_test_fetch_rate')
async def test_fetch_rate(db, from_currency, to_currency, date, expected_rate):
    rate: tp.Optional[decimal.Decimal] = None
    try:
        rate = await common_db.currency_rates.fetch_currency_rate(
            database=db,
            from_currency=from_currency,
            to_currency=to_currency,
            date=date,
        )
    except common_db.currency_rates.CurrencyRateNotFoundError:
        pass
    assert rate == expected_rate
