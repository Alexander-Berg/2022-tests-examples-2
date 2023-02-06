from typing import Set

import discounts_match  # pylint: disable=E0401
import pytest


@pytest.mark.parametrize(
    'missing_hierarchies',
    (
        pytest.param(set(), id='all_hierarchies'),
        pytest.param(
            {'menu_tags'},
            marks=discounts_match.remove_hierarchies('menu_tags'),
            id='no_menu_tags',
        ),
    ),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
async def test_hierarchy_descriptions(
        check_hierarchy_descriptions, missing_hierarchies: Set[str],
) -> None:
    await check_hierarchy_descriptions(missing_hierarchies)
