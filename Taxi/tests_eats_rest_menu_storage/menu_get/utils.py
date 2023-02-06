import enum

from tests_eats_rest_menu_storage import models


class HandlerTypes(enum.Enum):
    GET_ITEMS = '/internal/v1/get-items'
    MENU = '/internal/v1/menu'


def get_basic_request(handler, brand_items_uuids, place_id=1):

    get_items_basic_request = {
        'shipping_types': ['delivery', 'pickup'],
        'legacy_ids': [],
        'places': [{'place_id': str(place_id), 'items': []}],
    }

    menu_basic_request = {
        'place_id': str(place_id),
        'shipping_types': ['delivery', 'pickup'],
    }

    if handler is HandlerTypes.GET_ITEMS:
        request = get_items_basic_request
        request['places'][0]['items'] = brand_items_uuids
    else:
        request = menu_basic_request
    return request


def default_items_insert(
        eats_rest_menu_storage, item_amount, place_id=1, brand_id=1,
):
    items_uuids = {}
    items_ids = {}
    for i in range(1, item_amount + 1):
        origin_id = origin_id = 'item_origin_id_{}'.format(i)
        item_uuid = eats_rest_menu_storage.insert_brand_menu_items(
            [
                models.BrandMenuItem(
                    brand_id=brand_id,
                    origin_id=origin_id,
                    name='brand_name_{}'.format(i),
                    adult=False,
                ),
            ],
        )

        item_id = eats_rest_menu_storage.insert_place_menu_items(
            [
                models.PlaceMenuItem(
                    place_id=place_id,
                    brand_menu_item_id=item_uuid[(brand_id, origin_id)],
                    origin_id=origin_id,
                ),
            ],
        )

        eats_rest_menu_storage.insert_place_menu_item_prices(
            [
                models.PlaceMenuItemPrice(
                    place_menu_item_id=item_id[(place_id, origin_id)],
                    price=10.5,
                ),
            ],
        )

        items_uuids = {**items_uuids, **item_uuid}
        items_ids = {**items_ids, **item_id}

    return items_ids, items_uuids
