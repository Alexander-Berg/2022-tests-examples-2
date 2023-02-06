import pytest

from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage.menu_update import handler

UPDATE_HANDLER = '/internal/v1/update/menu'
MENU_HANDLER = '/internal/v1/menu'
PLACE_ID = 1
BRAND_ID = 1
MENU_REQUEST = {'place_id': str(PLACE_ID), 'shipping_types': ['delivery']}


@pytest.mark.parametrize(
    'available,stock',
    [
        pytest.param(False, None, id='test_item_stop_list'),
        pytest.param(False, 0, id='test_item_stock_stop_list'),
    ],
)
async def test_item(
        taxi_eats_rest_menu_storage,
        setup_basic_item,
        update_menu_handler,
        place_menu_db,
        available,
        stock,
):
    """
    test_item_stop_list
        1. Изначально в базе плейс с одним доступным айтемом в меню
        2. Делаем запрос на обновление меню,
           где выставляем available: false
        3. Вызываем ручку отдачи меню, проверяем,
           что айтем отдается, но с available: false

    test_item_stock_stop_list
        1. Изначально в базе плейс с одним доступным айтемом в меню
        2. Делаем запрос на обновление меню,
           где выставляем stock: 0
        3. Вызываем ручку отдачи меню, проверяем,
           что айтем отдается, но с available: false
    """
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    setup_basic_item(db)
    update_items = [
        handler.UpdateItem(
            origin_id='origin_id_1',
            available=available,
            name='brand_name_1',
            adult=False,
            price='10',
            promo_price='5',
            ordinary=True,
            choosable=True,
            stock=stock,
        ),
    ]

    update_response = await update_menu_handler(
        place_id=PLACE_ID, items=update_items,
    )
    assert update_response.status_code == 200

    menu_get_response = await taxi_eats_rest_menu_storage.post(
        MENU_HANDLER, json=MENU_REQUEST,
    )

    assert menu_get_response.json()['items'][0]['available'] is available


async def test_option_stop_list(
        taxi_eats_rest_menu_storage,
        setup_basic_item,
        update_menu_handler,
        place_menu_db,
):
    """
        1. Изначально в базе плейс с одним доступным айтемом,
           опцией и категорией в меню
        2. Делаем запрос на обновление меню,
           где выставляем категории available: false
        3. Вызываем ручку отдачи меню, проверяем,
           что категория отдается, но с available: false
    """
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)

    setup_basic_item(db)

    db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=1,
            origin_id='group_origin_id_1',
        ),
    )

    db.add_option(
        models.PlaceMenuItemOption(
            brand_menu_item_option='',
            place_menu_item_option_group_id=1,
            origin_id='option_origin_id_1',
        ),
    )

    update_items = [
        handler.UpdateItem(
            origin_id='origin_id_1',
            available=True,
            name='brand_name_1',
            options_groups=[
                handler.UpdateOptionsGroup(
                    origin_id='group_origin_id_1',
                    name='option_group_name_1',
                    options=[
                        handler.UpdateOption(
                            origin_id='option_origin_id_1',
                            name='option_name_1',
                            available=False,
                        ),
                    ],
                ),
            ],
        ),
    ]

    update_response = await update_menu_handler(
        place_id=PLACE_ID, items=update_items,
    )
    assert update_response.status_code == 200

    menu_get_response = await taxi_eats_rest_menu_storage.post(
        MENU_HANDLER, json=MENU_REQUEST,
    )

    assert (
        menu_get_response.json()['items'][0]['options_groups'][0]['options'][
            0
        ]['available']
        is False
    )


async def test_category_stop_list(
        taxi_eats_rest_menu_storage,
        place_menu_db,
        setup_basic_item,
        update_menu_handler,
):
    """
        1. Изначально в базе плейс
           с одним доступным айтемом и категорией в меню
        2. Делаем запрос на обновление меню,
           где выставляем категории available: false
        3. Вызываем ручку отдачи меню, проверяем,
           что категория отдается, но с available: false
    """
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    setup_basic_item(db)
    update_categories = [
        handler.UpdateCategory(
            origin_id='category_origin_id_1',
            available=False,
            name='category_name_1',
        ),
    ]

    update_response = await update_menu_handler(
        place_id=PLACE_ID, categories=update_categories,
    )
    assert update_response.status_code == 200

    menu_get_response = await taxi_eats_rest_menu_storage.post(
        MENU_HANDLER, json=MENU_REQUEST,
    )
    assert menu_get_response.status_code == 200

    assert menu_get_response.json()['categories'][0]['available'] is False


async def test_items_stop_category(
        taxi_eats_rest_menu_storage,
        place_menu_db,
        setup_basic_item,
        update_menu_handler,
):
    """
        1. Изначально в базе плейс с одним доступным айтемом в меню
        2. Делаем запрос на обновление меню,
           где меняем расписание категории айтема на недоступное
        3. Вызываем ручку отдачи меню, проверяем,
           что айтем отдается, но с available: false
    """
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    setup_basic_item(db)
    update_categories = [
        handler.UpdateCategory(
            origin_id='category_origin_id_1',
            available=True,
            name='category_name_1',
            synced_schedule=False,
            schedule=[{'day': 1, 'from': 0, 'to': 1}],
        ),
    ]

    update_response = await update_menu_handler(
        place_id=PLACE_ID, categories=update_categories,
    )
    assert update_response.status_code == 200

    menu_get_response = await taxi_eats_rest_menu_storage.post(
        MENU_HANDLER, json=MENU_REQUEST,
    )
    assert menu_get_response.status_code == 200

    assert menu_get_response.json()['items'][0]['available'] is False
