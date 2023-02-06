import pytest

from tests_eats_menu_categories import models
from tests_eats_menu_categories import utils


TIME_NOW = '2021-12-10T20:00:00+03:00'


@pytest.mark.categories(
    models.Category(
        category_id='category_1',
        slug='category_1',
        name='My category number one',
        status=models.CategoryStatus.PUBLISHED,
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
)
@pytest.mark.rules(
    models.Rule(
        rule_id='rule_1',
        slug='rule_1',
        name='My rule nunmer one',
        effect=models.RuleEffect.MAP,
        category_ids=['category_1'],
        type=models.RuleType.PREDICATE,
        enabled=True,
        payload=utils.make_eq_predicate(arg_name='item_id', value='1'),
        created_at=TIME_NOW,
        updated_at=TIME_NOW,
    ),
)
async def test_map_menu_item(taxi_eats_menu_categories, items_mappings):
    menu_item_id: str = '1'

    mappings = await items_mappings.get_items_categories([menu_item_id])
    assert not mappings

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/menu-item/map',
        headers={'x-yandex-login': 'testsuite'},
        json={
            'item': {
                'id': menu_item_id,
                'place_id': '1',
                'name': 'картошечка с пюрешечкой',
                'updated_at': TIME_NOW,
            },
        },
    )
    assert response.status_code == 200

    mappings = await items_mappings.get_items_categories([menu_item_id])
    assert mappings == [utils.make_item_mapping(menu_item_id, ['category_1'])]
