from typing import Optional

import pytest

from tests_grocery_discounts import common

CATEGORY_SUPPORT_RU = {
    'has_localization': True,
    'label': 'Поддержка открытия',
    'name': 'support_for_opening',
}

CATEGORY_FIRST_TEST_RU = {
    'has_localization': True,
    'label': 'Первый тест',
    'name': 'first_test',
}

CATEGORY_FIRST_TEST_EN = {
    'has_localization': True,
    'label': 'First test',
    'name': 'first_test',
}

CATEGORY_SUPPORT_EN = {
    'has_localization': True,
    'label': 'Support for opening',
    'name': 'support_for_opening',
}

CATEGORY_SECOND_TEST_EN = {
    'has_localization': True,
    'label': 'Second test',
    'name': 'second_test',
}

CATEGORY_WITHOUT_TRANSLATE = {
    'has_localization': False,
    'label': 'without_translate',
    'name': 'without_translate',
}

EXPECTED_JSON = {
    'default_ru': {
        'discount_categories': [CATEGORY_SUPPORT_RU, CATEGORY_FIRST_TEST_RU],
    },
    'default_en': {
        'discount_categories': [CATEGORY_SUPPORT_EN, CATEGORY_FIRST_TEST_EN],
    },
    'menu_discounts_en': {
        'discount_categories': [
            CATEGORY_SECOND_TEST_EN,
            CATEGORY_WITHOUT_TRANSLATE,
        ],
    },
    'menu_cashback_ru': {
        'discount_categories': [
            CATEGORY_SUPPORT_RU,
            CATEGORY_WITHOUT_TRANSLATE,
        ],
    },
}

TANKER = {
    'support_for_opening': {
        'ru': 'Поддержка открытия',
        'en': 'Support for opening',
    },
    'first_test': {'ru': 'Первый тест', 'en': 'First test'},
    'second_test': {'ru': 'Второй тест', 'en': 'Second test'},
}

CONFIG_CATEGORIES = {
    'enabling_validation': False,
    'tanker_keys_by_hierarchy': {
        '__default__': ['support_for_opening', 'first_test'],
        'menu_discounts': ['second_test', 'without_translate'],
        'menu_cashback': ['support_for_opening', 'without_translate'],
    },
}


@pytest.mark.config(
    GROCERY_DISCOUNTS_DISCOUNT_CATEGORIES_BY_HIERARCHY=CONFIG_CATEGORIES,
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.translations(grocery_discounts_discount_categories=TANKER)
@pytest.mark.parametrize(
    'locale, hierarchy_name, excepted',
    (
        (None, None, EXPECTED_JSON['default_en']),
        ('en', None, EXPECTED_JSON['default_en']),
        ('ru', None, EXPECTED_JSON['default_ru']),
        ('fr', None, EXPECTED_JSON['default_en']),
        ('bad', None, EXPECTED_JSON['default_en']),
        (None, 'menu_discounts', EXPECTED_JSON['menu_discounts_en']),
        ('ru', 'menu_cashback', EXPECTED_JSON['menu_cashback_ru']),
    ),
)
@pytest.mark.now('2019-01-01T10:00:00+0000')
async def test_admin_get_discount_categories(
        taxi_grocery_discounts,
        taxi_config,
        locale: Optional[str],
        hierarchy_name: Optional[str],
        excepted: dict,
):
    """
    checking the handle "/v3/admin/discount-categories"
    """
    headers: dict = common.DEFAULT_DISCOUNTS_HEADERS
    if locale is not None:
        headers['Accept-Language'] = locale
    params = {}
    if hierarchy_name:
        params['hierarchy_name'] = hierarchy_name
    response = await taxi_grocery_discounts.get(
        '/v3/admin/discount-categories',
        params=params,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status == 200
    assert response.json() == excepted


@pytest.mark.config(
    GROCERY_DISCOUNTS_DISCOUNT_CATEGORIES_BY_HIERARCHY=CONFIG_CATEGORIES,
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.translations(grocery_discounts_discount_categories=TANKER)
@pytest.mark.now('2019-01-01T10:00:00+0000')
async def test_admin_get_discount_categories_bad_hierarchy(
        taxi_grocery_discounts, taxi_config,
):
    """
    Checking invalid hierarchy_name field
    """
    response = await taxi_grocery_discounts.get(
        '/v3/admin/discount-categories',
        params={'hierarchy_name': 'bad_hieararchy'},
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status == 400
