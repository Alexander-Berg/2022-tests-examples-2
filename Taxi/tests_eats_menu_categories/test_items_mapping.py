from typing import List

import pytest

from tests_eats_menu_categories import models
from tests_eats_menu_categories import utils


TIME_NOW = '2021-12-01T12:00:00+00:00'
DEFAULT_RULE = models.Rule(
    rule_id='1',
    slug='rule-1',
    name='My rule 1',
    effect=models.RuleEffect.MAP,
    category_ids=['category-1'],
    type=models.RuleType.PREDICATE,
    enabled=True,
    payload={},
    created_at='2021-12-08T22:00:00+00:00',
    updated_at='2021-12-08T23:00:00+00:00',
)


async def test_get_items_categories_empty_request(taxi_eats_menu_categories):
    """
    Тест проверяет что запрос в ручку /items-categories
    не может быть пустым
    """

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/items-categories',
        json={'items': []},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_item_ids,expected_items',
    [
        pytest.param(['menu_item_1'], [], id='one item, no categories'),
        pytest.param(
            ['menu_item_1'],
            [utils.make_item_mapping('menu_item_1', ['1', '2'])],
            marks=pytest.mark.mappings(
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='1', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='2', rule_id='1',
                ),
            ),
            id='one item, many categories',
        ),
        pytest.param(
            ['menu_item_1'],
            [utils.make_item_mapping('menu_item_1', ['1'])],
            marks=pytest.mark.mappings(
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='1', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='3', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='4', rule_id='1',
                ),
            ),
            id='one item, only available categories',
        ),
        pytest.param(
            ['menu_item_1', 'menu_item_2'],
            [
                utils.make_item_mapping('menu_item_2', ['1']),
                utils.make_item_mapping('menu_item_1', ['1', '2']),
            ],
            marks=pytest.mark.mappings(
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='1', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='2', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_2', category_id='1', rule_id='1',
                ),
            ),
            id='many items, all with categories',
        ),
        pytest.param(
            ['menu_item_1', 'menu_item_2'],
            [utils.make_item_mapping('menu_item_1', ['1'])],
            marks=pytest.mark.mappings(
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='1', rule_id='1',
                ),
            ),
            id='many items, not all has categoires',
        ),
    ],
)
@pytest.mark.rules(DEFAULT_RULE)
@pytest.mark.menu_items(
    models.MenuItem(menu_item_id='menu_item_1', place_id='101'),
    models.MenuItem(menu_item_id='menu_item_2', place_id='101'),
)
@pytest.mark.categories(
    models.Category(
        category_id='1',
        slug='burgers',
        name='Бургеры',
        status=models.CategoryStatus.PUBLISHED,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
    models.Category(
        category_id='2',
        slug='pizza',
        name='Пицца',
        status=models.CategoryStatus.PUBLISHED,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
    models.Category(
        category_id='3',
        slug='breakfasts',
        name='Завтраки',
        status=models.CategoryStatus.HIDDEN,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
    models.Category(
        category_id='4',
        slug='salads',
        name='Салаты',
        status=models.CategoryStatus.DRAFT,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
)
async def test_get_items_categories(
        taxi_eats_menu_categories,
        items_mappings,
        request_item_ids: List[str],
        expected_items: List[models.ItemWithCategories],
):
    """
    Проверяем что /internal/eats-menu-categories/v1/items-categories
    возвращает все доступные категории для указанных товаров
    """

    items_categories = await items_mappings.get_items_categories(
        request_item_ids,
    )
    assert items_categories == expected_items


async def test_get_place_categories_empty_request(taxi_eats_menu_categories):
    """
    Тест проверяет что запрос в ручку /place-category-items
    не может быть пустым
    """

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/place-category-items',
        json={'place_id': '101', 'categories': []},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_category_ids,expected_items',
    [
        pytest.param(['1'], [], id='one category, no items'),
        pytest.param(
            ['1'],
            [
                utils.make_item_mapping('menu_item_2', ['1']),
                utils.make_item_mapping('menu_item_1', ['1']),
            ],
            marks=pytest.mark.mappings(
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='1', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_2', category_id='1', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_3', category_id='1', rule_id='1',
                ),
            ),
            id='one category, items found',
        ),
        pytest.param(
            ['1', '2'],
            [
                utils.make_item_mapping('menu_item_2', ['2']),
                utils.make_item_mapping('menu_item_1', ['1']),
            ],
            marks=pytest.mark.mappings(
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='1', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_2', category_id='2', rule_id='1',
                ),
            ),
            id='many categories, items found',
        ),
        pytest.param(
            ['3', '4'],
            [],
            marks=pytest.mark.mappings(
                models.Mapping(
                    menu_item_id='menu_item_1', category_id='3', rule_id='1',
                ),
                models.Mapping(
                    menu_item_id='menu_item_2', category_id='4', rule_id='1',
                ),
            ),
            id='items from unavailable categories',
        ),
    ],
)
@pytest.mark.rules(DEFAULT_RULE)
@pytest.mark.menu_items(
    models.MenuItem(menu_item_id='menu_item_1', place_id='101'),
    models.MenuItem(menu_item_id='menu_item_2', place_id='101'),
    models.MenuItem(menu_item_id='menu_item_3', place_id='102'),
)
@pytest.mark.categories(
    models.Category(
        category_id='1',
        slug='burgers',
        name='Бургеры',
        status=models.CategoryStatus.PUBLISHED,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
    models.Category(
        category_id='2',
        slug='pizza',
        name='Пицца',
        status=models.CategoryStatus.PUBLISHED,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
    models.Category(
        category_id='3',
        slug='breakfasts',
        name='Завтраки',
        status=models.CategoryStatus.HIDDEN,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
    models.Category(
        category_id='4',
        slug='salads',
        name='Салаты',
        status=models.CategoryStatus.DRAFT,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
)
async def test_get_place_categories(
        taxi_eats_menu_categories,
        items_mappings,
        request_category_ids: List[str],
        expected_items: List[models.ItemWithCategories],
):
    """
    Проверяем что /internal/eats-menu-categories/v1/place-category-items
    возвращает все доступные блюда определенных категорий
    в определенном ресторане.
    """

    place_id = '101'
    items_categories = await items_mappings.get_place_items_categories(
        place_id, request_category_ids,
    )
    assert items_categories == expected_items
