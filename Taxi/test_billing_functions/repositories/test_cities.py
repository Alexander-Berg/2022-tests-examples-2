import decimal

import pytest

from billing_functions.repositories import cities


async def test_chooses_correct_value(stq3_context):
    multipliers = await stq3_context.cities.fetch_donate_multipliers('Курск')
    assert multipliers.default == decimal.Decimal('1.06')
    assert multipliers.discounts == decimal.Decimal('1.07')


async def test_raises_not_found_error(stq3_context):
    with pytest.raises(cities.CityNotFoundError):
        await stq3_context.cities.fetch_donate_multipliers('Мордор')
