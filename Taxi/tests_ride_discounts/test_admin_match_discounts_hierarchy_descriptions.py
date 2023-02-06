import pytest


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_hierarchy_descriptions(check_hierarchy_descriptions) -> None:
    await check_hierarchy_descriptions(set())
