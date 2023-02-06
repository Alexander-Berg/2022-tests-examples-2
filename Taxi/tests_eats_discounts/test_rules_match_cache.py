import pytest


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_invalid_rules_match(check_invalid_rules_match) -> None:
    await check_invalid_rules_match(True)
