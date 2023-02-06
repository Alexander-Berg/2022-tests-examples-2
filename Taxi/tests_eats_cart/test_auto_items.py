# pylint: disable=too-many-lines
import pytest

from . import utils

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323
AUTO_ITEM_ID = 555
PLACE_ID = '123'

POST_BODY = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)
EMPTY_PROPERTIES = {'quantity': 1, 'item_options': []}


@utils.setup_auto_items(
    items={
        PLACE_ID: {
            str(AUTO_ITEM_ID): {
                'name': 'message.auto_item_title_packet',
                'description': 'Платный пакет',
                'picture_url': 'picture_url',
            },
        },
    },
)
@pytest.mark.parametrize(
    'auto_item_fee_type',
    [
        pytest.param('auto_items_fee', id='none'),
        pytest.param(
            'delivery_fee',
            id='delivery_fee',
            marks=utils.setup_auto_items_fee_type('delivery_fee'),
        ),
        pytest.param(
            'auto_items_fee',
            id='auto_items_fee',
            marks=utils.setup_auto_items_fee_type('auto_items_fee'),
        ),
    ],
)
async def test_auto_items_add_regular_item(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        auto_item_fee_type,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), str(AUTO_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json['cart']['additional_payments'][1] == {
        'amount': {
            'amount': '5 $SIGN$$CURRENCY$',
            'color': [
                {'theme': 'light', 'value': '#000000'},
                {'theme': 'dark', 'value': '#ffffff'},
            ],
        },
        'title': {
            'color': [
                {'theme': 'light', 'value': '#000000'},
                {'theme': 'dark', 'value': '#ffffff'},
            ],
            'text': 'Обязательный пакет',
        },
        'image_url': 'picture_url',
        'subtitle': {
            'color': [
                {'theme': 'light', 'value': '#000000'},
                {'theme': 'dark', 'value': '#ffffff'},
            ],
            'text': 'Платный пакет',
        },
        'type': auto_item_fee_type,
    }

    res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )

    assert len(res) == 2
    assert res[0]['quantity'] == 1
    assert res[1]['is_auto']


@utils.setup_auto_items(
    items={
        PLACE_ID: {
            str(AUTO_ITEM_ID): {
                'name': 'name',
                'description': 'description',
                'picture_url': 'picture_url',
            },
        },
    },
)
async def test_auto_items_manual_add_auto_item(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(AUTO_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(AUTO_ITEM_ID), **EMPTY_PROPERTIES),
    )

    assert response.status_code == 200

    res = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )

    assert len(res) == 1
    assert res[0]['quantity'] == 1
    assert not res[0]['is_auto']


@utils.setup_auto_items(
    items={
        PLACE_ID: {
            str(AUTO_ITEM_ID): {
                'name': 'name',
                'description': 'description',
                'picture_url': 'picture_url',
            },
        },
    },
)
async def test_auto_items_delete_manually_added_item(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), str(AUTO_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(items_db) == 2
    assert items_db[-1]['is_auto']

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(AUTO_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    item_id = items_db[-1]['id']
    assert not items_db[-1]['is_auto']

    response = await taxi_eats_cart.delete(
        f'api/v1/cart/{item_id}',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )

    assert len(items_db) == 2
    assert items_db[0]['quantity'] == 1
    assert items_db[1]['is_auto']


@utils.setup_auto_items(
    items={
        PLACE_ID: {
            str(AUTO_ITEM_ID): {
                'name': 'name',
                'description': 'description',
                'picture_url': 'picture_url',
            },
        },
    },
)
async def test_auto_items_delete_last_regular_item(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), str(AUTO_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    item_id = items_db[0]['id']
    assert len(items_db) == 2
    assert not items_db[0]['is_auto']
    assert items_db[-1]['is_auto']

    response = await taxi_eats_cart.delete(
        f'api/v1/cart/{item_id}',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )
    assert response.status_code == 200

    carts_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART, eats_cart_cursor,
    )

    assert len(carts_db) == 1
    assert carts_db[0]['deleted_at']


@utils.setup_auto_items(
    items={
        PLACE_ID: {
            str(AUTO_ITEM_ID): {
                'name': 'name',
                'description': 'description',
                'picture_url': 'picture_url',
            },
        },
    },
)
async def test_auto_items_add_item_that_was_auto(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), str(AUTO_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(items_db) == 2
    assert not items_db[0]['is_auto']
    assert items_db[-1]['is_auto']

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(AUTO_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(items_db) == 2
    assert not items_db[0]['is_auto']
    assert not items_db[-1]['is_auto']
    assert items_db[-1]['quantity'] == 2


@utils.setup_auto_items(
    items={
        PLACE_ID: {
            str(AUTO_ITEM_ID): {
                'name': 'name',
                'description': 'description',
                'picture_url': 'picture_url',
            },
        },
    },
)
async def test_auto_items_put_item_that_was_auto(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), str(AUTO_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(MENU_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    item_id = items_db[-1]['id']
    assert len(items_db) == 2
    assert not items_db[0]['is_auto']
    assert items_db[-1]['is_auto']

    response = await taxi_eats_cart.put(
        f'api/v1/cart/{item_id}',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json={'quantity': 2, 'item_options': []},
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    assert len(items_db) == 2
    assert not items_db[0]['is_auto']
    assert not items_db[-1]['is_auto']
    assert items_db[-1]['quantity'] == 2


@utils.setup_auto_items(
    items={
        PLACE_ID: {
            str(AUTO_ITEM_ID): {
                'name': 'name',
                'description': 'description',
                'picture_url': 'picture_url',
            },
        },
    },
)
async def test_auto_items_delete_last_regular_auto_item(
        taxi_eats_cart, load_json, eats_cart_cursor, local_services,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID), str(AUTO_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=dict(item_id=str(AUTO_ITEM_ID), **EMPTY_PROPERTIES),
    )
    assert response.status_code == 200

    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )
    item_id = items_db[0]['id']
    assert len(items_db) == 1
    assert not items_db[0]['is_auto']

    response = await taxi_eats_cart.delete(
        f'api/v1/cart/{item_id}',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )
    assert response.status_code == 200

    carts_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART, eats_cart_cursor,
    )
    items_db = utils.get_pg_records_as_dicts(
        utils.SELECT_CART_ITEMS, eats_cart_cursor,
    )

    assert len(carts_db) == 1
    assert carts_db[0]['deleted_at']
