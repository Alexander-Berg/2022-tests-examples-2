import pytest

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage import models
import tests_eats_rest_menu_storage.menu_get.menu_response as menu_response
import tests_eats_rest_menu_storage.menu_get.utils as utils

# pylint: disable=redefined-outer-name

BRAND_ID = 1
PLACE_ID = 1


def insert_items(eats_rest_menu_storage):
    categorie_uuids = eats_rest_menu_storage.insert_brand_menu_categories(
        [
            models.BrandMenuCategory(  # доступна
                brand_id=BRAND_ID,
                origin_id='category_origin_id_1',
                name='category_name_1',
            ),
        ],
    )
    category_ids = eats_rest_menu_storage.insert_place_menu_categories(
        [
            models.PlaceMenuCategory(  # доступна
                brand_menu_category_id=categorie_uuids[
                    (BRAND_ID, 'category_origin_id_1')
                ],
                place_id=PLACE_ID,
                origin_id='category_origin_id_1',
                legacy_id=10,
            ),
        ],
    )

    items_uuids = eats_rest_menu_storage.insert_brand_menu_items(
        [
            models.BrandMenuItem(  # все данные у бренда
                brand_id=BRAND_ID,
                origin_id='item_origin_id_1',
                name='brand_name_1',
                adult=False,
                description='brand_description_1',
                weight_value=10.5,
                weight_unit='ml',
                short_name='brand_short_name_1',
            ),
            models.BrandMenuItem(  # все данные у плейса
                brand_id=BRAND_ID,
                origin_id='item_origin_id_2',
                name='brand_name_2',
                adult=False,
            ),
            models.BrandMenuItem(  # удален
                brand_id=BRAND_ID,
                origin_id='item_origin_id_3',
                name='brand_name_3',
                adult=False,
            ),
        ],
    )

    items_ids = eats_rest_menu_storage.insert_place_menu_items(
        [
            models.PlaceMenuItem(
                place_id=PLACE_ID,
                brand_menu_item_id=items_uuids[(BRAND_ID, 'item_origin_id_1')],
                origin_id='item_origin_id_1',
                adult=False,
            ),
            models.PlaceMenuItem(
                place_id=PLACE_ID,
                brand_menu_item_id=items_uuids[(BRAND_ID, 'item_origin_id_2')],
                origin_id='item_origin_id_2',
                adult=True,
                name='place_name_2',
                sort=20,
                description='place_description_2',
                weight_value=20.5,
                weight_unit='l',
                legacy_id=2,
                short_name='place_short_name_2',
            ),
            models.PlaceMenuItem(
                place_id=PLACE_ID,
                brand_menu_item_id=items_uuids[(BRAND_ID, 'item_origin_id_3')],
                origin_id='item_origin_id_3',
                name='brand_name_3',
                adult=False,
                deleted_at=models.DELETED_AT,  # удален
            ),
        ],
    )

    eats_rest_menu_storage.insert_item_categories(
        [
            models.PlaceMenuItemCategory(
                place_id=PLACE_ID,
                place_menu_category_id=category_ids[
                    (PLACE_ID, 'category_origin_id_1')
                ],
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_2')],
            ),
        ],
    )

    eats_rest_menu_storage.insert_place_menu_item_prices(
        [
            models.PlaceMenuItemPrice(
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_1')],
                price=10.5,
            ),
            models.PlaceMenuItemPrice(
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_2')],
                price=10.5,
                promo_price=5.5,
                vat=3.555,
            ),
            models.PlaceMenuItemPrice(
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_3')],
                price=10.5,
            ),
        ],
    )

    eats_rest_menu_storage.insert_item_pictures(
        [
            models.ItemPicture(
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_2')],
                picture_id=1,
            ),
            models.ItemPicture(
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_2')],
                picture_id=2,
            ),
        ],
    )

    return items_uuids, categorie_uuids


@pytest.mark.parametrize(
    'handler',
    [
        pytest.param(
            utils.HandlerTypes.GET_ITEMS,
            id='test_get_items_items',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
        pytest.param(
            utils.HandlerTypes.MENU,
            id='test_menu_get_items',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
    ],
)
async def test_items(
        taxi_eats_rest_menu_storage,
        eats_rest_menu_storage,
        handler: utils.HandlerTypes,
):
    items_uuids, categorie_uuids = insert_items(eats_rest_menu_storage)

    expected_items = [
        menu_response.Item(
            id=items_uuids[(BRAND_ID, 'item_origin_id_1')],
            origin_id='item_origin_id_1',
            name='brand_name_1',
            adult=False,
            description='brand_description_1',
            weight_value='10.5',
            weight_unit='ml',
            short_name='brand_short_name_1',
            price='10.5',
            choosable=True,
            ordinary=True,
        ).as_dict(),
        menu_response.Item(
            id=items_uuids[(BRAND_ID, 'item_origin_id_2')],
            origin_id='item_origin_id_2',
            adult=True,
            name='place_name_2',
            sort=20,
            description='place_description_2',
            weight_value='20.5',
            weight_unit='l',
            legacy_id=2,
            short_name='place_short_name_2',
            pictures=[
                definitions.Picture(ratio=0.5, url='url2'),
                definitions.Picture(ratio=1.0, url='url1'),
            ],
            price='10.5',
            choosable=True,
            ordinary=True,
            vat='3.56',
            promo_price='5.5',
            categories_ids=[
                definitions.CategoryIds(
                    id=categorie_uuids[(BRAND_ID, 'category_origin_id_1')],
                    legacy_id=10,
                ),
            ],
        ).as_dict(),
    ]

    request = utils.get_basic_request(handler, list(items_uuids.values()))

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    assert response.status_code == 200

    if handler is utils.HandlerTypes.GET_ITEMS:
        response_places = list(
            sorted(response.json()['places'], key=lambda x: x['place_id']),
        )
        response_items = response_places[0]['items']
    else:
        response_items = response.json()['items']

    assert sorted(expected_items, key=lambda d: d['origin_id']) == sorted(
        response_items, key=lambda d: d['origin_id'],
    )


def insert_item_statuses(eats_rest_menu_storage, items_ids):
    eats_rest_menu_storage.insert_place_menu_item_statuses(
        [
            models.PlaceMenuItemStatus(
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_2')],
                active=True,
            ),
            models.PlaceMenuItemStatus(
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_4')],
                active=False,
            ),
        ],
    )
    eats_rest_menu_storage.insert_place_menu_item_stocks(
        [
            models.PlaceMenuItemStock(
                place_menu_item_id=items_ids[(PLACE_ID, 'item_origin_id_3')],
                stock=0,
            ),
        ],
    )


@pytest.mark.parametrize(
    'handler',
    [
        pytest.param(
            utils.HandlerTypes.GET_ITEMS,
            id='test_get_items_items_statuses',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
        pytest.param(
            utils.HandlerTypes.MENU,
            id='test_menu_get_items_statuses',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
    ],
)
async def test_menu_item_statuses(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage, handler,
):
    items_ids, items_uuids = utils.default_items_insert(
        eats_rest_menu_storage, item_amount=4,
    )
    insert_item_statuses(eats_rest_menu_storage, items_ids)

    expected_item_statuses = {
        'item_origin_id_1': True,
        'item_origin_id_2': True,
        'item_origin_id_3': False,
        'item_origin_id_4': False,
    }

    request = utils.get_basic_request(handler, list(items_uuids.values()))

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    response_item_statuses = {}

    if handler is utils.HandlerTypes.GET_ITEMS:
        response_places = list(
            sorted(response.json()['places'], key=lambda x: x['place_id']),
        )
        response_items = response_places[0]['items']
    else:
        response_items = response.json()['items']

    for item in response_items:
        response_item_statuses[item['origin_id']] = item['available']

    assert response.status_code == 200
    assert expected_item_statuses == response_item_statuses


def insert_categories(eats_rest_menu_storage):
    uuids = eats_rest_menu_storage.insert_brand_menu_categories(
        [
            models.BrandMenuCategory(  # доступна
                brand_id=BRAND_ID,
                origin_id='category_origin_id_1',
                name='category_name_1',
            ),
            models.BrandMenuCategory(  # не доступна
                brand_id=BRAND_ID,
                origin_id='category_origin_id_2',
                name='category_name_2',
            ),
            models.BrandMenuCategory(  # удалена
                brand_id=BRAND_ID,
                origin_id='category_origin_id_3',
                name='category_name_3',
            ),
        ],
    )
    ids = eats_rest_menu_storage.insert_place_menu_categories(
        [
            models.PlaceMenuCategory(  # доступна
                brand_menu_category_id=uuids[
                    (BRAND_ID, 'category_origin_id_1')
                ],
                place_id=PLACE_ID,
                origin_id='category_origin_id_1',
            ),
            models.PlaceMenuCategory(  # не доступна
                brand_menu_category_id=uuids[
                    (BRAND_ID, 'category_origin_id_2')
                ],
                place_id=PLACE_ID,
                origin_id='category_origin_id_2',
            ),
            models.PlaceMenuCategory(  # удалена
                brand_menu_category_id=uuids[
                    (BRAND_ID, 'category_origin_id_3')
                ],
                place_id=PLACE_ID,
                origin_id='category_origin_id_3',
                deleted_at=models.DELETED_AT,
            ),
        ],
    )

    eats_rest_menu_storage.insert_category_statuses(
        [
            models.PlaceMenuCategoryStatus(
                place_menu_category_id=ids[(PLACE_ID, 'category_origin_id_1')],
                active=True,
            ),
            models.PlaceMenuCategoryStatus(
                place_menu_category_id=ids[(PLACE_ID, 'category_origin_id_2')],
                active=False,
            ),
        ],
    )


def insert_category_items(eats_rest_menu_storage):
    eats_rest_menu_storage.insert_item_categories(
        [
            models.PlaceMenuItemCategory(
                place_id=PLACE_ID,
                place_menu_item_id=1,
                place_menu_category_id=1,
            ),
            models.PlaceMenuItemCategory(
                place_id=PLACE_ID,
                place_menu_item_id=2,
                place_menu_category_id=1,
            ),
            models.PlaceMenuItemCategory(
                place_id=PLACE_ID,
                place_menu_item_id=2,
                place_menu_category_id=2,
            ),
            models.PlaceMenuItemCategory(
                place_id=PLACE_ID,
                place_menu_item_id=3,
                place_menu_category_id=2,
            ),
        ],
    )


@pytest.mark.parametrize(
    'handler',
    [
        pytest.param(
            utils.HandlerTypes.GET_ITEMS,
            id='test_get_items_item_with_categories_statuses',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
        pytest.param(
            utils.HandlerTypes.MENU,
            id='test_menu_get_item_with_categories_statuses',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
    ],
)
async def test_item_with_categories_statuses(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage, handler,
):
    insert_categories(eats_rest_menu_storage)

    _, items_uuids = utils.default_items_insert(
        eats_rest_menu_storage, item_amount=3,
    )

    insert_category_items(eats_rest_menu_storage)

    expected_item_statuses = {
        'item_origin_id_1': True,
        'item_origin_id_2': False,
        'item_origin_id_3': False,
    }

    request = utils.get_basic_request(handler, list(items_uuids.values()))

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    response_item_statuses = {}

    if handler is utils.HandlerTypes.GET_ITEMS:
        response_places = list(
            sorted(response.json()['places'], key=lambda x: x['place_id']),
        )
        response_items = response_places[0]['items']
    else:
        response_items = response.json()['items']

    for item in response_items:
        response_item_statuses[item['origin_id']] = item['available']

    assert response.status_code == 200
    assert expected_item_statuses == response_item_statuses
