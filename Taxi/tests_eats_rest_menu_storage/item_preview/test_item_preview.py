import copy

import pytest

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage.item_preview import item_preview
from tests_eats_rest_menu_storage.menu_get import utils

# pylint: disable=redefined-outer-name

BRAND_ID = 1
PLACE_ID = 1

HANDLER = '/internal/v1/items-preview'
REQUEST = {
    'places': [{'place_id': str(PLACE_ID), 'items': []}],
    'shipping_types': ['delivery'],
}

USE_CTID_QUERY = pytest.mark.config(
    EATS_REST_MENU_STORAGE_MENU_SETTINGS={'use_ctid_items_query': True},
)


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


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
@pytest.mark.parametrize(
    'use_ctid_items_query',
    (
        pytest.param(False, id='default'),
        pytest.param(True, marks=USE_CTID_QUERY, id='ctid'),
    ),
)
async def test_items(
        taxi_eats_rest_menu_storage,
        eats_rest_menu_storage,
        database,
        use_ctid_items_query,
):
    items_uuids, categorie_uuids = insert_items(eats_rest_menu_storage)

    expected_items = [
        item_preview.ItemPreview(
            id=items_uuids[(BRAND_ID, 'item_origin_id_1')],
            name='brand_name_1',
            adult=False,
            weight_value='10.5',
            weight_unit='ml',
            price='10.5',
        ).as_dict(),
        item_preview.ItemPreview(
            id=items_uuids[(BRAND_ID, 'item_origin_id_2')],
            adult=True,
            name='place_name_2',
            weight_value='20.5',
            weight_unit='l',
            legacy_id=2,
            pictures=[
                definitions.Picture(ratio=0.5, url='url2'),
                definitions.Picture(ratio=1.0, url='url1'),
            ],
            price='10.5',
            categories=[
                definitions.CategoryInfo(
                    id=categorie_uuids[(BRAND_ID, 'category_origin_id_1')],
                    name='category_name_1',
                    legacy_id=10,
                ),
            ],
        ).as_dict(),
    ]

    request = copy.deepcopy(REQUEST)

    request['places'][0]['items'] = list(items_uuids.values())

    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=request)

    assert response.status_code == 200

    response_places = list(
        sorted(response.json()['places'], key=lambda x: x['place_id']),
    )

    response_items = response_places[0]['items']

    assert sorted(expected_items, key=lambda d: d['id']) == sorted(
        response_items, key=lambda d: d['id'],
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


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_menu_item_statuses(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage,
):
    items_ids, items_uuids = utils.default_items_insert(
        eats_rest_menu_storage, item_amount=4,
    )
    insert_item_statuses(eats_rest_menu_storage, items_ids)

    expected_item_statuses = {
        items_uuids[(PLACE_ID, 'item_origin_id_1')]: True,
        items_uuids[(PLACE_ID, 'item_origin_id_2')]: True,
        items_uuids[(PLACE_ID, 'item_origin_id_3')]: False,
        items_uuids[(PLACE_ID, 'item_origin_id_4')]: False,
    }

    request = copy.deepcopy(REQUEST)
    request['places'][0]['items'] = list(items_uuids.values())

    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=request)

    response_item_statuses = {}

    response_places = list(
        sorted(response.json()['places'], key=lambda x: x['place_id']),
    )

    for item in response_places[0]['items']:
        response_item_statuses[item['id']] = item['available']

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


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_item_with_categories_statuses(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage,
):
    insert_categories(eats_rest_menu_storage)

    _, items_uuids = utils.default_items_insert(
        eats_rest_menu_storage, item_amount=3,
    )

    insert_category_items(eats_rest_menu_storage)

    expected_item_statuses = {
        items_uuids[(PLACE_ID, 'item_origin_id_1')]: True,
        items_uuids[(PLACE_ID, 'item_origin_id_2')]: False,
        items_uuids[(PLACE_ID, 'item_origin_id_3')]: False,
    }

    request = copy.deepcopy(REQUEST)
    request['places'][0]['items'] = list(items_uuids.values())

    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=request)

    response_item_statuses = {}

    response_places = list(
        sorted(response.json()['places'], key=lambda x: x['place_id']),
    )

    response_items = response_places[0]['items']

    for item in response_items:
        response_item_statuses[item['id']] = item['available']

    assert response.status_code == 200
    assert expected_item_statuses == response_item_statuses


@pytest.mark.parametrize(
    'choosable',
    (pytest.param(False, id='false'), pytest.param(True, id='true')),
)
async def test_choosable(
        taxi_eats_rest_menu_storage, place_menu_db, choosable,
):
    """
    Проверяем что поле choosable возвращается в ответе ручки
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
        ),
    )

    item = models.PlaceMenuItem(
        place_id=PLACE_ID,
        brand_menu_item_id='',
        origin_id='item_1',
        name='item 1',
        choosable=choosable,
    )
    db.add_item(category_id, item)

    response = await taxi_eats_rest_menu_storage.post(
        '/internal/v1/items-preview',
        json={
            'places': [
                {
                    'place_id': str(PLACE_ID),
                    'items': [item.brand_menu_item_id],
                },
            ],
            'shipping_types': ['delivery'],
        },
    )

    assert response.status_code == 200
    assert response.json()['places'][0]['items'][0]['choosable'] == choosable
