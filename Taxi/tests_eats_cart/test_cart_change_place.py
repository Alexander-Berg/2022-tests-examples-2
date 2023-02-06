import pytest

from . import utils

CURRENT_PLACE_SLUG = 'place_1'
NEW_PLACE_SLUG = 'place_2'
NEW_PLACE_SLUG_WRONG = 'place_3'

EATER_ID = 'eater3'


# TODO проверить, что скидки нормально отрабатывают (cartWithDiscounts)

PARAMS = {
    'latitude': 55.75,
    'longitude': 37.62,
    'deliveryTime': '2021-04-04T11:00:00+03:00',
    'shippingType': 'delivery',
}


@pytest.mark.pgsql('eats_cart', files=['pg_eats_cart_restaurant.sql'])
@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_restaurant.json',
)
async def test_cart_change_place_restaurant(
        taxi_eats_cart, local_services, load_json,
):
    """Запрос перевода корзины на ресторан - ошибка, в ресторанах
    нет связки core_id <-> public_id, поэтому надо отдать ошибку."""
    local_services.place_slugs = set('place_1')

    local_services.request_params = PARAMS
    request_body = {'new_place_slug': NEW_PLACE_SLUG}
    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 400

    assert response.json() == {
        'code': 20,
        'domain': 'UserData',
        'err': 'error.invalid_operation',
    }


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_cart_change_place_same_place_slug(
        taxi_eats_cart, local_services, load_json,
):
    """Запрос перевода корзины на тот же слаг -
    ничего не делаем, возвращаем текущую корзину."""
    local_services.place_slugs = set(('place_1', 'place_2'))
    local_services.eats_products_items_request = ['1', '2', '3', '4']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items_old.json',
    )

    local_services.request_params = PARAMS
    request_body = {'new_place_slug': CURRENT_PLACE_SLUG}
    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200

    resp_json = response.json()
    assert resp_json['place']['slug'] == CURRENT_PLACE_SLUG
    assert resp_json['place_slug'] == CURRENT_PLACE_SLUG


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_cart_change_place_missing(
        taxi_eats_cart, local_services, load_json,
):
    """Новый плейс не найден в кеше - возвращаем 400ку"""
    local_services.place_slugs = set(('place_1', 'place_2'))
    local_services.eats_products_items_request = ['1', '2', '3', '4']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items_new.json',
    )

    local_services.request_params = PARAMS
    request_body = {'new_place_slug': NEW_PLACE_SLUG_WRONG}

    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 400
    assert local_services.mock_eats_products_menu.times_called == 0
    assert response.json() == {
        'code': 55,
        'domain': 'UserData',
        'err': 'Недоступный ресторан',
    }


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_cart_change_place_general_case(
        taxi_eats_cart,
        local_services,
        load_json,
        mockserver,
        eats_cart_cursor,
):
    """
    Часть товаров переносится, если по части не найден маппинг.
    Также тут проверяем ограничение по количеству товара:
    в старой корзине 2 шт товаров, в новом плейсе доступно только 1 шт
    """
    local_services.place_slugs = set(('place_1', 'place_2'))
    local_services.eats_products_items_request = ['11', '12', '13']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items_new.json',
    )

    local_services.request_params = PARAMS
    request_body = {'new_place_slug': NEW_PLACE_SLUG}

    @mockserver.json_handler('/eats-products/internal/v2/products/core_id')
    def _mock_products_core_id(json_request):
        request = json_request.json
        assert request['place_id'] == 2
        assert set(request['public_ids']) == set(
            ['public_id_1', 'public_id_2', 'public_id_3', 'public_id_4'],
        )
        return {
            'products_ids': [
                {'public_id': 'public_id_1', 'core_id': 11},
                {'public_id': 'public_id_2', 'core_id': 12},
                {'public_id': 'public_id_3', 'core_id': 13},
                {'public_id': 'public_id_4'},
            ],
        }

    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200

    assert local_services.mock_eats_products_menu.times_called == 1
    assert _mock_products_core_id.times_called == 1

    resp_json = response.json()

    # Check items and prices
    assert len(resp_json['items']) == 2
    item_11 = resp_json['items'][0]
    assert item_11['decimal_price'] == '500'
    assert item_11['decimal_promo_price'] == '300'
    assert item_11['quantity'] == 1

    item_12 = resp_json['items'][1]
    assert item_12['decimal_price'] == '500'
    assert item_12['decimal_promo_price'] == '300'
    assert item_12['quantity'] == 2

    # Check place
    assert resp_json['place']['slug'] == NEW_PLACE_SLUG
    assert resp_json['place_slug'] == NEW_PLACE_SLUG

    # assert that db has changed also (tx is commited)
    eats_cart_cursor.execute(utils.SELECT_ACTIVE_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    cart = utils.pg_result_to_repr(result)[0]
    assert cart[3] == NEW_PLACE_SLUG
    assert cart[4] == '2'  # place_id
    assert cart[5] == '900.00'  # promo_subtotal
    assert cart[6] == '900.00'  # total

    cart_id = cart[0]

    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_FOR_CART, (cart_id,))
    items = eats_cart_cursor.fetchall()
    assert len(items) == 2

    place_menu_item_ids = {item[2] for item in items}
    assert place_menu_item_ids == set(['11', '12'])


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_cart_change_place_all_mapping_is_missing(
        taxi_eats_cart, local_services, load_json, mockserver,
):
    """
    Ручка маппинга товаров ничего не отдала - возвращаем ошибку,
    не трогаем корзину (клиент может сам удалить корзину,
    если пожелает).
    """
    local_services.place_slugs = set(('place_1', 'place_2'))
    local_services.eats_products_items_request = ['1', '2', '3', '4']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items_new.json',
    )

    local_services.request_params = PARAMS
    request_body = {'new_place_slug': NEW_PLACE_SLUG}

    @mockserver.json_handler('/eats-products/internal/v2/products/core_id')
    def _mock_products_core_id(json_request):
        return {'products_ids': []}

    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert _mock_products_core_id.times_called == 1
    assert local_services.mock_eats_products_menu.times_called == 0

    assert response.status_code == 400
    assert response.json() == {
        'code': 20,
        'domain': 'UserData',
        'err': 'error.invalid_operation',
    }


@pytest.mark.pgsql('eats_cart', files=['pg_eats_cart_no_public_ids.sql'])
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_cart_change_place_no_public_ids(
        taxi_eats_cart, local_services, load_json,
):
    """
    Вызвали для корзины, в которой нет public_id. Это покрывает,
    например, кейс ресторана. Должны выдать ошибку
    """
    local_services.place_slugs = set(('place_1', 'place_2'))
    local_services.eats_products_items_request = ['1', '2', '3', '4']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items_new.json',
    )

    local_services.request_params = PARAMS
    request_body = {'new_place_slug': NEW_PLACE_SLUG}

    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 400
    assert local_services.mock_eats_products_menu.times_called == 0
    assert response.json() == {
        'code': 20,
        'domain': 'UserData',
        'err': 'error.invalid_operation',
    }


@pytest.mark.eats_catalog_storage_cache(
    file='catalog_storage_cache_different_brands.json',
)
async def test_cart_change_place_another_brand(
        taxi_eats_cart, local_services, load_json,
):
    """
    Вызвали для плейса, бренд которого отличается от текущего.
    Выдаем ошибку.
    """
    local_services.place_slugs = set(('place_1', 'place_2'))
    local_services.eats_products_items_request = ['1', '2', '3', '4']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items_new.json',
    )

    local_services.request_params = PARAMS
    request_body = {'new_place_slug': NEW_PLACE_SLUG}

    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 400
    assert local_services.mock_eats_products_menu.times_called == 0
    assert response.json() == {
        'code': 200,
        'domain': 'UserData',
        'err': 'error.brands_differ',
    }


@pytest.mark.parametrize('ep_error', ['timeout', 'network', '500'])
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_cart_change_place_mapping_handler_error(
        taxi_eats_cart, local_services, load_json, mockserver, ep_error,
):
    """
    Ручка маппинга в eats-products не работает - возвращаем ошибку
    """
    local_services.place_slugs = set(('place_1', 'place_2'))
    local_services.eats_products_items_request = ['1', '2', '3', '4']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items_new.json',
    )

    local_services.request_params = PARAMS
    request_body = {'new_place_slug': NEW_PLACE_SLUG}

    @mockserver.json_handler('/eats-products/internal/v2/products/core_id')
    def _mock_products_core_id(json_request):
        if ep_error == 'timeout':
            raise mockserver.TimeoutError()
        elif ep_error == 'network':
            raise mockserver.NetworkError()
        else:
            return mockserver.make_response('bad request', status=500)

    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 400
    assert local_services.mock_eats_products_menu.times_called == 0
    assert response.json() == {
        'code': 20,
        'domain': 'UserData',
        'err': 'error.invalid_operation',
    }


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_cart_change_place_discounts(
        taxi_eats_cart,
        load_json,
        local_services,
        eats_order_stats,
        mockserver,
):
    """
    Проверяем, что скидки применяются к новым товарам.
    """

    eats_order_stats()
    local_services.available_discounts = True
    local_services.eats_discounts_response = load_json(
        'eats_discounts_response.json',
    )

    local_services.place_slugs = set(('place_1', 'place_2'))
    local_services.eats_products_items_request = ['11', '12', '13']
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items_new.json',
    )

    local_services.request_params = PARAMS

    @mockserver.json_handler('/eats-products/internal/v2/products/core_id')
    def _mock_products_core_id(json_request):
        return {'products_ids': [{'public_id': 'public_id_1', 'core_id': 11}]}

    request_body = {'new_place_slug': NEW_PLACE_SLUG}

    response = await taxi_eats_cart.post(
        'api/v1/cart/change_place',
        params=local_services.request_params,
        json=request_body,
        headers=utils.get_auth_headers(EATER_ID),
    )

    assert response.status_code == 200

    items = response.json()['items']
    assert len(items) == 1

    place_menu_item = items[0]['place_menu_item']

    assert place_menu_item['promo_price'] == 297
    assert place_menu_item['decimal_promo_price'] == '297'
