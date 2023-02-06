import decimal
import json

import pytest

from . import utils

EATER_ID = 'eater2'
PLACE_SLUG = 'place123'
MENU_ITEM_ID = 232323
BRAND_ID = '999'


def make_rules_config():
    return {
        'rules': '',
        'licenses': '',
        'warning': '',
        'rules_with_storage_info': {
            'full': {
                'title': 'slug.alcohol.full_title_rules',
                'text': 'slug.alcohol.full_text_rules',
            },
            'short': 'slug.alcohol.short_text_rules',
        },
        'storage_time': 1,
    }


@pytest.mark.parametrize(
    'send_shop_place_business, core_times_called',
    [
        pytest.param(True, 0, id='send_shop_place_business'),
        pytest.param(False, 1, id='do_not_send_shop_place_business'),
    ],
)
@utils.additional_payment_text()
async def test_post_no_cart_exists(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        send_shop_place_business,
        core_times_called,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    post_body = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)
    if send_shop_place_business:
        post_body['place_business'] = 'shop'

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=post_body,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == core_times_called
    assert local_services.mock_eats_products_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    assert len(items) == 1
    cart_item_id = str(items[0]['id'])

    expected_json = load_json('expected_with_options.json')
    expected_json['item_id'] = MENU_ITEM_ID
    expected_json['id'] = int(cart_item_id)
    expected_json['cart']['items'][0]['id'] = int(cart_item_id)

    response_json = response.json()
    del response_json['cart']['updated_at']
    del response_json['cart']['id']
    del response_json['cart']['revision']
    assert response_json == expected_json


@pytest.mark.pgsql('eats_cart', files=['current_cart.sql'])
async def test_cart_get(taxi_eats_cart, local_services, load_json):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = []
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['1']
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_products_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1


@pytest.mark.parametrize(
    'has_rules',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_RETAIL_ALCOHOL_SHOPS={BRAND_ID: make_rules_config()},
            ),
        ),
        pytest.param(False),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['current_cart.sql'])
async def test_cart_rules(
        taxi_eats_cart, local_services, load_json, has_rules,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = []
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['1']
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200

    if not has_rules:
        assert 'rules' not in response.json()['place']
        return

    assert response.json()['place']['rules'] == {
        'short': 'Короткий текст правил продажи',
        'full': {
            'text': (
                'Полный текст правил продажи. Можно забронировать на 1 час.'
            ),
            'title': 'Заголовок правил продажи',
        },
    }


@pytest.mark.pgsql('eats_cart', files=['current_cart.sql'])
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                EATS_CART_REDIS={
                    'enable_menu_items_cache': True,
                    'menu_items_ttl': 1800,
                    'compatibility_save_empty_extra_info': True,
                },
            ),
            id='compatibility_on',
        ),
        pytest.param(
            marks=pytest.mark.config(
                EATS_CART_REDIS={
                    'enable_menu_items_cache': True,
                    'menu_items_ttl': 1800,
                    'compatibility_save_empty_extra_info': False,
                },
            ),
            id='compatibility_off',
        ),
        pytest.param(
            marks=pytest.mark.config(
                EATS_CART_REDIS={
                    'enable_menu_items_cache': True,
                    'menu_items_ttl': 1800,
                },
            ),
            id='compatibility_default',
        ),
    ],
)
async def test_shop_redis(
        taxi_eats_cart, local_services, load_json, redis_store,
):

    eater_id = 'eater3'

    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = []
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200

    parsed_json = json.loads(redis_store.get(f'mi:{MENU_ITEM_ID}'))

    expected_json = load_json('expected_with_options.json')
    expected_json = expected_json['cart']['items'][0]['place_menu_item']
    expected_json['weight'] = expected_json['weight'].replace('\u00a0', ' ')
    assert parsed_json['menu_item'] == expected_json

    del parsed_json['menu_item']
    expected_redis_data = {
        'place_business': 'shop',
        'place_id': '123',
        'place_slug': 'place123',
        'extra_info': {
            'weight': '1.5',
            'weight_unit': 'kg',
            'public_id': 'tomato_red_super',
            'vat': None,
            'is_catch_weight': True,
            'origin_id': 'shop_tomato_red_super',
            'is_alcohol': False,
        },
    }
    assert parsed_json == expected_redis_data

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )
    assert response.status_code == 200
    assert (
        local_services.mock_eats_products_menu.times_called == 1
    )  # must be 1, we use redis cached data on second call
    assert local_services.mock_eats_catalog.times_called == 2


@pytest.mark.pgsql('eats_cart', files=['current_cart.sql'])
async def test_partner_discounts(
        taxi_eats_cart, local_services, load_json, eats_cart_cursor,
):
    menu_item_id = 2
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(menu_item_id)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['1', '2']
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.available_discounts = True

    post_body = {
        'item_id': menu_item_id,
        'quantity': 1,
        'shipping_type': 'delivery',
    }
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=post_body,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_products_menu.times_called == 2
    assert local_services.mock_eats_catalog.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()
    # check promo_price
    assert items[0][4] is None
    assert items[4][4] is not None

    eats_cart_cursor.execute(utils.SELECT_CART)
    cart = eats_cart_cursor.fetchall()
    assert len(cart) == 3
    # check promo_subtotal
    assert cart[0][5] == decimal.Decimal('123.00')
    # check total
    assert cart[0][6] == decimal.Decimal('143.00')

    assert response.json()['cart']['total'] == 143
    assert response.json()['cart']['subtotal'] == 140


@utils.additional_payment_text()
@pytest.mark.pgsql('eats_cart', files=['cart_with_weighted.sql'])
async def test_cart_get_plus_request(
        taxi_eats_cart, local_services, load_json,
):
    eater_id = 'eater3'

    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = []
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['2', '232323']
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.plus_request = load_json('eats_plus_request.json')
    local_services.set_plus_response(status=200, json={})

    request_headers = utils.get_auth_headers(eater_id)
    request_headers['X-Yandex-UID'] = '0'
    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=request_headers,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_products_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_cashback.times_called == 1


@pytest.mark.pgsql('eats_cart', files=['cart_with_weighted.sql'])
async def test_post_cart_related_data_plus_request(
        taxi_eats_cart, load_json, local_services,
):
    eater_id = 'eater3'

    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = []
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['2', '232323']
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    plus_request = load_json('eats_plus_request.json')
    del plus_request['location']
    del plus_request['shipping_type']
    plus_request['order_id'] = 'cart_00000000-0000-0000-0000-000000000001'

    local_services.plus_checkout_request = plus_request
    local_services.set_plus_checkout_response(status=200, json={})

    request = {
        'delivery_date': '2021-04-04T08:00:00+00:00',
        'location': {'lat': 55.75, 'lon': 37.62},  # Moscow
        'eater_id': eater_id,
        'yandex_uid': '0',
    }

    request_headers = utils.get_auth_headers(eater_id, yandex_uid='0')

    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=request_headers,
        json=request,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_plus_checkout_cashback.times_called == 1
