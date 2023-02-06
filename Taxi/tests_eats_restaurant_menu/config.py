import pytest


def eats_restaurant_menu(max_item_kilocalories: str = '900'):
    return pytest.mark.config(
        EATS_RESTAURANT_MENU={'max_item_kilocalories': max_item_kilocalories},
    )
