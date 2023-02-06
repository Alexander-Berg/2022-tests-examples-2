# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import copy
import os

from eda_shortcuts_plugins import *  # noqa: F403 F401
import pytest

CONSUMER = 'eda-shortcuts'

BASE_DIR = os.path.dirname(__file__)
SHORTCUTS_MOCK_PATH = os.path.abspath(
    os.path.join(
        BASE_DIR, '../resources/shortcuts/shortcuts/shortcuts_base.json',
    ),
)


@pytest.fixture(autouse=True)
def shortcuts_admin_global_mock(mockserver, load_json):
    shortcuts_base = load_json(SHORTCUTS_MOCK_PATH)

    @mockserver.json_handler('/shortcuts-admin/v1/admin/shortcuts/eats/list')
    def _eats_mock(_):
        eats_shortcuts = shortcuts_base['eats_place_shortcuts']
        for shortcut in eats_shortcuts:
            price_category_id = shortcut.pop('price_category_id', -1)
            if price_category_id != -1:
                shortcut['price_category'] = price_category_id
        return {'shortcuts': eats_shortcuts}

    @mockserver.json_handler(
        '/shortcuts-admin/v2/admin/shortcuts/grocery/list',
    )
    def _grocery_mock(_):
        grocery_shortcuts = copy.deepcopy(
            shortcuts_base['grocery_category_shortcuts'],
        )
        for i, shortcut in enumerate(grocery_shortcuts):
            shortcut['category_id'] = str(shortcut['category_id'])
            shortcut['place_id'] = str(shortcut['place_id'])
            shortcut['relevance'] = 10 + i
            shortcut.pop('slug', None)
            shortcut.pop('image_tag', None)
        return {'shortcuts': grocery_shortcuts}

    return {'grocery_mock': _grocery_mock, 'eats_mock': _eats_mock}


def exp3_content(name, value):
    return dict(
        name=name,
        consumers=[CONSUMER],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


def exp3_decorator(name, value):
    return pytest.mark.experiments3(**exp3_content(name, value))


def get_eda_params(shortcut, key):
    return shortcut['scenario_params']['eats_place_params'][key]
