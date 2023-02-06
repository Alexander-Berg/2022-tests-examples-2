import pytest

from tests_eats_rest_menu_storage import models
import tests_eats_rest_menu_storage.menu_get.utils as utils

BRAND_ID = 1
PLACE_ID = 1

NUTRIENTS = models.Nutrients(
    calories='1.1', proteins='2.2', fats='3.3', carbohydrates='4.4',
)


@pytest.mark.parametrize(
    'handler',
    [
        pytest.param(utils.HandlerTypes.GET_ITEMS, id='test_get_items_items'),
        pytest.param(utils.HandlerTypes.MENU, id='test_menu_get_items'),
    ],
)
async def test_nutrients(
        taxi_eats_rest_menu_storage,
        place_menu_db,
        handler: utils.HandlerTypes,
):
    """
    Проверяем что КБЖУ возвращается из ручек
    /menu и /get-items
    """

    db = place_menu_db(BRAND_ID, PLACE_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
            name='category_1',
        ),
    )

    item = models.PlaceMenuItem(
        place_id=PLACE_ID,
        brand_menu_item_id='',
        origin_id='item_1',
        name='item_1',
        nutrients=NUTRIENTS,
    )

    db.add_item(category_id, item)

    request = utils.get_basic_request(handler, list([item.brand_menu_item_id]))

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    assert response.status_code == 200
    data = response.json()

    if handler is utils.HandlerTypes.GET_ITEMS:
        response_items = data['places'][0]['items']
    else:
        response_items = data['items']

    assert len(response_items) == 1
    assert response_items[0]['nutrients'] == NUTRIENTS.as_dict()
