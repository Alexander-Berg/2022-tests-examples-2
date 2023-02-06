import pytest


def enable_menu_items_consumer():
    return pytest.mark.config(
        EATS_MENU_CATEGORIES_MENU_ITEMS_CONSUMER={'enabled': True},
    )
