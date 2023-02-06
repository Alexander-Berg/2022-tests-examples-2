import pytest


@pytest.fixture
def hierarchy_descriptions_url():
    return 'v3/admin/match-discounts/hierarchy-descriptions'


@pytest.mark.parametrize(
    'missing_hierarchies',
    (
        pytest.param(set(), id='all_hierarchies'),
        pytest.param(set('dynamic_discounts'), id='no_dynamic_discounts'),
        pytest.param(set('menu_discounts'), id='no_menu_discounts'),
        pytest.param(set('cart_discounts'), id='no_cart_discounts'),
        pytest.param(
            set('payment_method_discounts'), id='no_payment_method_discounts',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
async def test_hierarchy_descriptions(
        check_hierarchy_descriptions, missing_hierarchies,
) -> None:
    await check_hierarchy_descriptions(missing_hierarchies)
