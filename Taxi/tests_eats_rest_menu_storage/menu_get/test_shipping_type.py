import pytest

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage import sql
import tests_eats_rest_menu_storage.menu_get.utils as utils


MENU_HANDLER = '/internal/v1/menu'
GET_ITEMS_HANDLER = '/internal/v1/get-items'

BRAND_ID = 1


def insert_items(eats_rest_menu_storage, database):
    sql.insert_place(
        database, models.Place(place_id=2, brand_id=1, slug='2_place_slug'),
    )

    items_uuids = eats_rest_menu_storage.insert_brand_menu_items(
        [
            models.BrandMenuItem(
                brand_id=BRAND_ID,
                origin_id='item_origin_id_1',
                name='brand_name_1',
                adult=False,
            ),
            models.BrandMenuItem(
                brand_id=BRAND_ID,
                origin_id='item_origin_id_2',
                name='brand_name_2',
                adult=False,
            ),
            models.BrandMenuItem(
                brand_id=BRAND_ID,
                origin_id='item_origin_id_3',
                name='brand_name_3',
                adult=False,
            ),
            models.BrandMenuItem(
                brand_id=BRAND_ID,
                origin_id='item_origin_id_4',
                name='brand_name_4',
                adult=False,
            ),
        ],
    )

    items_ids = eats_rest_menu_storage.insert_place_menu_items(
        [
            # первый плейс
            models.PlaceMenuItem(
                place_id=1,
                brand_menu_item_id=items_uuids[(BRAND_ID, 'item_origin_id_1')],
                origin_id='item_origin_id_1',
                shipping_types=[definitions.ShippingType.Delivery],
            ),
            models.PlaceMenuItem(
                place_id=1,
                brand_menu_item_id=items_uuids[(BRAND_ID, 'item_origin_id_2')],
                origin_id='item_origin_id_2',
                shipping_types=[definitions.ShippingType.Pickup],
            ),
            models.PlaceMenuItem(
                place_id=1,
                brand_menu_item_id=items_uuids[(BRAND_ID, 'item_origin_id_3')],
                origin_id='item_origin_id_3',
                legacy_id=3,
                shipping_types=[
                    definitions.ShippingType.Delivery,
                    definitions.ShippingType.Pickup,
                ],
            ),
            # второй плейс
            models.PlaceMenuItem(
                place_id=2,
                brand_menu_item_id=items_uuids[(BRAND_ID, 'item_origin_id_2')],
                origin_id='item_origin_id_2',
                shipping_types=[definitions.ShippingType.Pickup],
            ),
            models.PlaceMenuItem(
                place_id=2,
                brand_menu_item_id=items_uuids[(BRAND_ID, 'item_origin_id_4')],
                origin_id='item_origin_id_4',
                shipping_types=[definitions.ShippingType.Delivery],
            ),
        ],
    )

    eats_rest_menu_storage.insert_place_menu_item_prices(
        [
            # 1 плейс
            models.PlaceMenuItemPrice(
                place_menu_item_id=items_ids[(1, 'item_origin_id_1')],
                price=10.5,
            ),
            models.PlaceMenuItemPrice(
                place_menu_item_id=items_ids[(1, 'item_origin_id_2')],
                price=10.5,
            ),
            models.PlaceMenuItemPrice(
                place_menu_item_id=items_ids[(1, 'item_origin_id_3')],
                price=10.5,
            ),
            # 2 плейс
            models.PlaceMenuItemPrice(
                place_menu_item_id=items_ids[(2, 'item_origin_id_2')],
                price=10.5,
            ),
            models.PlaceMenuItemPrice(
                place_menu_item_id=items_ids[(2, 'item_origin_id_4')],
                price=10.5,
            ),
        ],
    )

    return items_uuids


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_get_items_places(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage, database,
):
    """
    Проверяет правильно ли ручка get-items обрабатывает запрос где айтемы:
    1) в разных плейсах
    2) запрошен через legacy_id
    """
    items_uuids = insert_items(eats_rest_menu_storage, database)

    places_1_items_uuids = [
        items_uuids[(1, 'item_origin_id_1')],
        items_uuids[(1, 'item_origin_id_2')],
    ]

    places_2_items_uuids = [
        items_uuids[(1, 'item_origin_id_2')],
        items_uuids[(1, 'item_origin_id_4')],
    ]

    request = {
        'shipping_types': ['delivery', 'pickup'],
        'legacy_ids': [3],
        'places': [
            {'place_id': '1', 'items': places_1_items_uuids},
            {'place_id': '2', 'items': places_2_items_uuids},
        ],
    }

    response = await taxi_eats_rest_menu_storage.post(
        GET_ITEMS_HANDLER, json=request,
    )

    response_places = sorted(
        response.json()['places'], key=lambda d: d['place_id'],
    )

    # ассерт айтемов первого плейса
    response_uuids_place_1 = []

    for item in response_places[0]['items']:
        response_uuids_place_1.append(item['origin_id'])

    assert sorted(response_uuids_place_1) == [
        'item_origin_id_1',
        'item_origin_id_2',
        'item_origin_id_3',
    ]

    # ассерт айтемов второго плейса
    response_uuids_place_2 = []
    for item in response_places[1]['items']:
        response_uuids_place_2.append(item['origin_id'])

    assert sorted(response_uuids_place_2) == [
        'item_origin_id_2',
        'item_origin_id_4',
    ]
    assert response.status_code == 200


@pytest.mark.parametrize(
    'shipping_types, expected_origin_ids',
    [
        pytest.param(
            ['pickup'],
            ['item_origin_id_2', 'item_origin_id_3'],
            id='test_get_items_pickup',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
        pytest.param(
            ['delivery'],
            ['item_origin_id_1', 'item_origin_id_3'],
            id='test_get_items_delivery',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
        pytest.param(
            ['delivery', 'pickup'],
            ['item_origin_id_1', 'item_origin_id_2', 'item_origin_id_3'],
            id='test_get_items_both_types',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
    ],
)
async def test_menu_delivery_type(
        taxi_eats_rest_menu_storage,
        eats_rest_menu_storage,
        database,
        shipping_types,
        expected_origin_ids,
):
    """
    Проверяет правильно ли обе ручки menu_get и get-items
    обрабатывают запросы с разными типами доставки
    Например, только [delivery]
    """

    # тест ручки get-items
    items_uuids = insert_items(eats_rest_menu_storage, database)

    get_items_request = {
        'shipping_types': shipping_types,
        'legacy_ids': [],
        'places': [{'place_id': '1', 'items': list(items_uuids.values())}],
    }

    get_items_response = await taxi_eats_rest_menu_storage.post(
        utils.HandlerTypes.GET_ITEMS.value, json=get_items_request,
    )

    assert get_items_response.status_code == 200

    response_origin_ids = []

    for item in get_items_response.json()['places'][0]['items']:
        response_origin_ids.append(item['origin_id'])

    assert sorted(response_origin_ids) == expected_origin_ids

    # тест ручки menu

    menu_request = {'place_id': '1', 'shipping_types': shipping_types}

    menu_get_response = await taxi_eats_rest_menu_storage.post(
        utils.HandlerTypes.MENU.value, json=menu_request,
    )

    assert menu_get_response.status_code == 200

    response_origin_ids = []

    for item in menu_get_response.json()['items']:
        response_origin_ids.append(item['origin_id'])

    assert sorted(response_origin_ids) == expected_origin_ids
