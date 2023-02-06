import pytest

from tests_eats_menu_categories import models


TIME_NOW = '2021-12-08T22:00:00+00:00'


@pytest.mark.menu_items(
    models.MenuItem(menu_item_id='i_am_menu_item_1', place_id='i_am_place_1'),
    models.MenuItem(menu_item_id='i_am_menu_item_2', place_id='i_am_place_1'),
)
@pytest.mark.rules(
    models.Rule(
        rule_id='1',
        slug='rule-1',
        name='My rule 1',
        effect=models.RuleEffect.MAP,
        category_ids=['category-1'],
        type=models.RuleType.PREDICATE,
        enabled=True,
        payload={},
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
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
)
async def test_mapping(taxi_eats_menu_categories, items_mappings):

    # Test SaveMappings

    response = await taxi_eats_menu_categories.post(
        '/test/mapping/save-mappings',
        json={
            'mappings': [
                {
                    'scored_category': {'category_id': '1', 'score': 0.1},
                    'menu_item_id': 'i_am_menu_item_1',
                    'place_id': 'i_am_place_1',
                    'rule_id': '1',
                },
                {
                    'scored_category': {'category_id': '2', 'score': 1},
                    'menu_item_id': 'i_am_menu_item_1',
                    'place_id': 'i_am_place_1',
                    'rule_id': '1',
                },
                {
                    'scored_category': {'category_id': '2', 'score': 0.2},
                    'menu_item_id': 'i_am_menu_item_2',
                    'place_id': 'i_am_place_1',
                    'rule_id': '1',
                },
            ],
        },
    )

    assert response.status_code == 204

    # Check whether the saved mappings are available

    item_categories = await items_mappings.get_items_categories(
        ['i_am_menu_item_1', 'i_am_menu_item_2', 'i_am_non_existend_item'],
    )
    expected_items_categories = [
        models.ItemWithCategories(
            item_id='i_am_menu_item_2',
            categories=[models.ScoredCategory(category_id='2', score=0.2)],
        ),
        models.ItemWithCategories(
            item_id='i_am_menu_item_1',
            categories=[
                models.ScoredCategory(category_id='1', score=0.1),
                models.ScoredCategory(category_id='2', score=1.0),
            ],
        ),
    ]
    assert item_categories == expected_items_categories

    # Test RemoveMappingsForItems

    response = await taxi_eats_menu_categories.post(
        '/test/mapping/remove-mappings-for-items',
        json={'menu_items': ['i_am_menu_item_1', 'i_am_menu_item_2']},
    )

    assert response.status_code == 204

    item_categories = await items_mappings.get_items_categories(
        ['i_am_menu_item_1', 'i_am_menu_item_2', 'i_am_non_existend_item'],
    )
    assert not item_categories


async def test_nonexistent_insert(taxi_eats_menu_categories):

    response = await taxi_eats_menu_categories.post(
        '/test/mapping/save-mappings',
        json={
            'mappings': [
                {
                    'scored_category': {'category_id': '2', 'score': 0.2},
                    'menu_item_id': 'i_am_menu_item_2',
                    'place_id': 'i_am_place_1',
                    'rule_id': '1',
                },
            ],
        },
    )

    assert response.status_code == 500
