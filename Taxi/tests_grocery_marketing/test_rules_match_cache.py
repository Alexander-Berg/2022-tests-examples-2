import pytest


@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
async def test_invalid_rules_match(check_invalid_rules_match) -> None:
    await check_invalid_rules_match(False)
