import pytest


@pytest.mark.parametrize(
    'excluded_hierarchies',
    (
        pytest.param(
            ['place_delivery_discounts', 'cart_discounts'],
            id='two_hierarchies_for_exclude',
        ),
        pytest.param([], id='no_hierarchies_for_exclude'),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_hierarchy_descriptions(
        check_hierarchy_descriptions, taxi_config, excluded_hierarchies,
):
    taxi_config.set(EATS_DISCOUNTS_EXCLUDED_HIERARCHIES=excluded_hierarchies)
    await check_hierarchy_descriptions(excluded_hierarchies)
