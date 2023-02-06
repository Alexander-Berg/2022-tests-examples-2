import pytest

from tests_eats_menu_categories import configs
from tests_eats_menu_categories import models
from tests_eats_menu_categories import utils

MENU_ITEM_ID: str = '1'
TIME_NOW = '2021-12-10T20:00:00+03:00'

CATEGORY = models.Category(
    category_id='category_1',
    slug='category_1',
    name='My category number one',
    status=models.CategoryStatus.PUBLISHED,
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
)
RULE = models.Rule(
    rule_id='rule_1',
    slug='rule_1',
    name='My rule nunmer one',
    effect=models.RuleEffect.MAP,
    category_ids=['category_1'],
    type=models.RuleType.PREDICATE,
    enabled=True,
    payload=utils.make_eq_predicate(arg_name='item_id', value=MENU_ITEM_ID),
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
)


@configs.enable_menu_items_consumer()
@pytest.mark.categories(CATEGORY)
@pytest.mark.rules(RULE)
async def test_processing_via_lb(
        taxi_eats_menu_categories,
        items_mappings,
        menu_items_logbroker_topic,
        menu_items_consumer_one_shot,
):
    """
    Проверяет, что процессинг поверх lobgroker работает, если передано сырое
    сообщение.
    """

    mappings = await items_mappings.get_items_categories([MENU_ITEM_ID])
    assert not mappings

    await menu_items_logbroker_topic.send_message(
        models.MenuItemMessage(int(MENU_ITEM_ID)),
    )
    await menu_items_consumer_one_shot()
    await menu_items_logbroker_topic.wait_read()

    mappings = await items_mappings.get_items_categories([MENU_ITEM_ID])
    assert mappings == [
        utils.make_item_mapping(MENU_ITEM_ID, [CATEGORY.category_id]),
    ]
