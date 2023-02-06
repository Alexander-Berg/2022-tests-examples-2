from testsuite.utils import ordered_object

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage.menu_get import menu_response
from tests_eats_rest_menu_storage.menu_update import handler

UPDATE_HANDLER = '/internal/v1/update/menu'
MENU_HANDLER = '/internal/v1/menu'
PLACE_ID = 1
BRAND_ID = 1
MENU_REQUEST = {'place_id': str(PLACE_ID), 'shipping_types': ['delivery']}


async def test_update_item_category(
        taxi_eats_rest_menu_storage,
        setup_basic_item,
        update_menu_handler,
        place_menu_db,
):
    """
        1. Изначально в базе плейс с одним доступным айтемом в меню
        2. Делаем запрос на обновление меню, где меняем категорию айтема
        3. Вызываем ручку отдачи меню, проверяем,
           что айтем отдается в новой категории
    """
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    setup_basic_item(db)

    categories = [
        handler.UpdateCategory(
            origin_id='category_origin_id_2',
            name='category_name_2',
            available=True,
        ),
    ]

    items = [
        handler.UpdateItem(
            origin_id='origin_id_1',
            name='brand_name_1',
            adult=False,
            category_origin_ids=['category_origin_id_2'],
            choosable=True,
            ordinary=True,
        ),
    ]

    update_response = await update_menu_handler(
        place_id=PLACE_ID, categories=categories, items=items,
    )

    assert update_response.status_code == 200

    menu_get_response = await taxi_eats_rest_menu_storage.post(
        MENU_HANDLER, json=MENU_REQUEST,
    )

    assert menu_get_response.status_code == 200

    assert menu_get_response.json()['items'][0]['categories_ids'] == [
        definitions.CategoryIds(
            id=update_response.json()['categories'][0]['id'],
        ).as_dict(),
    ]


async def test_adding_new_items(
        taxi_eats_rest_menu_storage,
        setup_basic_item,
        update_menu_handler,
        place_menu_db,
        sql_get_origin_id_uuid_mapping,
):
    """
        1. Изначально в базе плейс
           с одним доступным айтемом в меню
        2. Делаем запрос на обновление меню,
           где добавляем новые айтемы/категории
        3. Вызываем ручку отдачи меню, проверяем,
           что отдаются как старые, так и новые категории/айтемы
    """
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    setup_basic_item(db)

    update_categories = [
        handler.UpdateCategory(
            origin_id='category_origin_id_2',
            name='category_name_2',
            available=True,
        ),
    ]
    update_items = [
        handler.UpdateItem(
            origin_id='origin_id_2',
            name='brand_name_2',
            adult=False,
            category_origin_ids=['category_origin_id_1'],
            choosable=True,
            ordinary=True,
        ),
        handler.UpdateItem(
            origin_id='origin_id_3',
            name='brand_name_3',
            adult=False,
            category_origin_ids=['category_origin_id_2'],
            choosable=True,
            ordinary=True,
        ),
    ]

    update_response = await update_menu_handler(
        place_id=PLACE_ID, categories=update_categories, items=update_items,
    )
    assert update_response.status_code == 200

    items_mapping = sql_get_origin_id_uuid_mapping('place_menu_items')

    categories_mapping = sql_get_origin_id_uuid_mapping(
        'place_menu_categories',
    )

    response_items = [
        menu_response.Item(
            adult=False,
            available=True,
            choosable=True,
            id=items_mapping['origin_id_1'],
            name='brand_name_origin_id_1',
            ordinary=True,
            origin_id='origin_id_1',
            price='500',
            categories_ids=[
                definitions.CategoryIds(
                    id=categories_mapping['category_origin_id_1'],
                ),
            ],
        ),
        menu_response.Item(
            id=items_mapping['origin_id_2'],
            origin_id='origin_id_2',
            name='brand_name_2',
            adult=False,
            categories_ids=[
                definitions.CategoryIds(
                    categories_mapping['category_origin_id_1'],
                ),
            ],
            choosable=True,
            ordinary=True,
        ),
        menu_response.Item(
            origin_id='origin_id_3',
            id=items_mapping['origin_id_3'],
            name='brand_name_3',
            adult=False,
            categories_ids=[
                definitions.CategoryIds(
                    categories_mapping['category_origin_id_2'],
                ),
            ],
            choosable=True,
            ordinary=True,
        ),
    ]

    response_categories = [
        menu_response.Category(
            id=categories_mapping['category_origin_id_1'],
            origin_id='category_origin_id_1',
            name='category_name_1',
            available=True,
        ),
        menu_response.Category(
            id=categories_mapping['category_origin_id_2'],
            origin_id='category_origin_id_2',
            name='category_name_2',
            available=True,
        ),
    ]

    expected_menu_response = menu_response.MenuResponse(
        categories=response_categories, items=response_items,
    )

    response = await taxi_eats_rest_menu_storage.post(
        MENU_HANDLER, json=MENU_REQUEST,
    )

    ordered_object.assert_eq(
        expected_menu_response.as_dict(),
        response.json(),
        ['categories', 'items'],
    )
