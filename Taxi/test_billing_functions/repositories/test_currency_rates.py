import decimal

import pytest

from taxi.billing.util import dates

from billing_functions.repositories import currency_rates


async def test_chooses_correct_value(stq3_context):
    on_date = dates.parse_date('2021-03-01')
    rate = await stq3_context.currency_rates.fetch('RUB', 'USD', on_date)
    assert rate == decimal.Decimal('0.01')


async def test_raises_not_found_error(stq3_context):
    on_date = dates.parse_date('2020-12-31')
    with pytest.raises(currency_rates.CurrencyRateNotFoundError):
        await stq3_context.currency_rates.fetch('RUB', 'USD', on_date)
