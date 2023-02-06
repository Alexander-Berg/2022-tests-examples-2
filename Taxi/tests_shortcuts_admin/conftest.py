import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from shortcuts_admin_plugins import *  # noqa: F403 F401


@pytest.fixture(scope='session')
def find_shortcuts():
    def _find_shortcuts(
            shortcuts,
            data,
            category_id=None,
            brand_id=None,
            metacategory_id=None,
    ):
        def form_subset(id_, key):
            return [i for i in data if i[key] == id_]

        subset = []
        if category_id is not None:
            subset = form_subset(category_id, 'category_id')
        elif brand_id is not None:
            subset = form_subset(brand_id, 'brand_id')
        elif metacategory_id is not None:
            subset = form_subset(metacategory_id, 'mcid')

        return [
            sh for i in subset for sh in shortcuts if i['slug'] == sh['slug']
        ]

    return _find_shortcuts
