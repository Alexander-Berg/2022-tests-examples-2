from testsuite.utils import ordered_object

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage import models
import tests_eats_rest_menu_storage.menu_get.menu_response as menu_response
import tests_eats_rest_menu_storage.menu_update.handler as update_handler


UPDATE_HANDLER = '/internal/v1/update/menu'
MENU_HANDLER = '/internal/v1/menu'
GET_ITEMS_HANDLER = '/internal/v1/get-items'
PLACE_ID = 1
MENU_REQUEST = {'place_id': str(PLACE_ID), 'shipping_types': ['delivery']}
GET_ITEMS_REQUEST = {
    'shipping_types': ['delivery', 'pickup'],
    'legacy_ids': [],
    'places': [{'place_id': '1', 'items': []}],
}


async def test_lifecycle(
        taxi_eats_rest_menu_storage,
        update_menu_handler,
        setup_brand_and_place,
):
    """
        1. Изначально база пустая
        2. Заливаем меню с 2 категориями (одна родительская для другой),
           в дочерней категории  лежит 1 айтем
           с 1 внутренней опцией, 1 группой опций, в группе 1 опция.
        3. Проверяем 200 ок на заливку
        4. Вызываем ручку отдачи меню, проверяем,
           что отдается ровно то же, что и было залито
        5. Вызываем ручку забора айтема по id, проверяем
           что отдается ровно то же, что было залито
    """
    update_categories = [
        update_handler.UpdateCategory(
            origin_id='category_origin_id_1',
            name='testsuite_name_1',
            available=True,
            legacy_id=1,
        ),
        update_handler.UpdateCategory(
            origin_id='category_origin_id_2',
            name='testsuite_name_2',
            parent_origin_id='category_origin_id_1',
            available=True,
            legacy_id=2,
        ),
    ]

    update_items = [
        update_handler.UpdateItem(
            origin_id='item_origin_id_1',
            name='testsuite_item_1',
            adult=False,
            category_origin_ids=['category_origin_id_2'],
            inner_options=[
                update_handler.UpdateInnerOption(
                    name='testsuite_inner_option_1',
                    origin_id='inner_opton_origin_id_1',
                    group_name='inner_option_group_name_1',
                    group_origin_id='inner_option_group_origin_id_1',
                ),
            ],
            options_groups=[
                update_handler.UpdateOptionsGroup(
                    origin_id='group_origin_id_1',
                    name='option_group_name_1',
                    is_required=True,
                    options=[
                        update_handler.UpdateOption(
                            origin_id='option_origin_id_1',
                            name='option_name_1',
                            multiplier=1,
                        ),
                    ],
                ),
            ],
            shipping_types=[definitions.ShippingType.Delivery],
            legacy_id=10,
            description='tasty testsuite burger',
            weight=update_handler.Weight(unit='g', value='200'),
            vat='5.5',
            price='100.5',
            promo_price='50.5',
            sort=100,
            ordinary=True,
            choosable=True,
            available=True,
            stock=10,
            short_name='name_1',
            nutrients=models.Nutrients(
                calories='1', proteins='2', fats='3', carbohydrates='4',
            ),
        ),
    ]

    update_response = await update_menu_handler(
        place_id=PLACE_ID, categories=update_categories, items=update_items,
    )
    assert update_response.status_code == 200

    menu_handler_response = await taxi_eats_rest_menu_storage.post(
        MENU_HANDLER, json=MENU_REQUEST,
    )

    expected_items = [
        menu_response.Item(
            id=update_response.json()['items'][0]['id'],
            origin_id='item_origin_id_1',
            name='testsuite_item_1',
            adult=False,
            inner_options=[
                menu_response.InnerOption(
                    id=update_response.json()['inner_options'][0]['id'],
                    name='testsuite_inner_option_1',
                    origin_id='inner_opton_origin_id_1',
                    group_name='inner_option_group_name_1',
                    group_origin_id='inner_option_group_origin_id_1',
                ),
            ],
            options_groups=[
                menu_response.OptionsGroup(
                    id=update_response.json()['options_groups'][0]['id'],
                    origin_id='group_origin_id_1',
                    name='option_group_name_1',
                    is_required=True,
                    options=[
                        menu_response.Option(
                            id=update_response.json()['options'][0]['id'],
                            origin_id='option_origin_id_1',
                            name='option_name_1',
                            multiplier=1,
                            price='100',
                        ),
                    ],
                ),
            ],
            shipping_types=[definitions.ShippingType.Delivery],
            legacy_id=10,
            description='tasty testsuite burger',
            weight_unit='g',
            weight_value='200',
            vat='5.5',
            price='100.5',
            promo_price='50.5',
            sort=100,
            ordinary=True,
            choosable=True,
            available=True,
            stock=10,
            short_name='name_1',
            categories_ids=[
                definitions.CategoryIds(
                    id=update_response.json()['categories'][1]['id'],
                    legacy_id=2,
                ),
            ],
            nutrients=models.Nutrients(
                calories='1', proteins='2', fats='3', carbohydrates='4',
            ),
        ),
    ]

    expected_categories = [
        menu_response.Category(
            id=update_response.json()['categories'][0]['id'],
            available=True,
            legacy_id=1,
            name='testsuite_name_1',
            origin_id='category_origin_id_1',
        ),
        menu_response.Category(
            id=update_response.json()['categories'][1]['id'],
            available=True,
            legacy_id=2,
            name='testsuite_name_2',
            origin_id='category_origin_id_2',
            parent_ids=[update_response.json()['categories'][0]['id']],
        ),
    ]

    expected_menu_response = menu_response.MenuResponse(
        items=expected_items, categories=expected_categories,
    )

    assert menu_handler_response.status_code == 200

    ordered_object.assert_eq(
        expected_menu_response.as_dict(),
        menu_handler_response.json(),
        ['items', 'items.categories', 'categories'],
    )

    expected_get_items_response = menu_response.GetItemsResponse(
        places=[
            menu_response.GetItemsPlaceResponse(
                place_id=str(PLACE_ID),
                place_slug=f'place_{PLACE_ID}',
                items=expected_items,
            ),
        ],
    )

    GET_ITEMS_REQUEST['places'][0]['items'] = [
        update_response.json()['items'][0]['id'],
    ]

    get_items_handler_response = await taxi_eats_rest_menu_storage.post(
        GET_ITEMS_HANDLER, json=GET_ITEMS_REQUEST,
    )

    assert get_items_handler_response.status_code == 200
    ordered_object.assert_eq(
        expected_get_items_response.as_dict(),
        get_items_handler_response.json(),
        ['places', 'places.items', 'places.items.categories'],
    )


async def test_big_legacy_id(
        taxi_eats_rest_menu_storage,
        update_menu_handler,
        setup_brand_and_place,
):
    """
        Заливаем айтем у которого
        legacy_id = 9223372036854775806
        и проверяем, что в ответе ручки menu
        возвраащется ровно то же число
    """

    big_id = 9223372036854775806

    update_items = [
        update_handler.UpdateItem(
            origin_id='item_origin_id_1',
            name='testsuite_item_1',
            adult=False,
            category_origin_ids=['category_origin_id_2'],
            legacy_id=big_id,
            available=True,
        ),
    ]

    update_response = await update_menu_handler(
        place_id=PLACE_ID, items=update_items,
    )
    assert update_response.status_code == 200

    menu_handler_response = await taxi_eats_rest_menu_storage.post(
        MENU_HANDLER, json=MENU_REQUEST,
    )

    assert menu_handler_response.status_code == 200
    assert menu_handler_response.json()['items'][0]['legacy_id'] == big_id
