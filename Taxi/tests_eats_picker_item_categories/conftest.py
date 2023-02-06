# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_picker_item_categories_plugins import *  # noqa: F403 F401


@pytest.fixture()
def check_category():
    def do_check_category(
            category,
            category_id,
            category_name,
            category_level,
            category_priority=None,
            hierarchy_number=0,
    ):
        assert category['category_id'] == category_id
        assert category['category_name'] == category_name
        assert category['category_level'] == category_level
        assert category['hierarchy_number'] == hierarchy_number
        assert abs(category['category_priority'] - category_priority) < 1e-6

    return do_check_category
