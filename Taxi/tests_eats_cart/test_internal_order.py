import pytest

from . import utils

MENU_ITEM_ID = 232323
PLACE_SLUG = 'place123'
PLACE_ID = '22'
EATER_ID = 'eater2'
ORDER_NR = 'order1'
CART_ID = '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9'
NOT_EXISTS_CART_ID = '1a73add7-9c84-4440-9d3a-12f3e71c6021'
# POST_ITEM_BODY = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)

HEADERS = {
    'X-YaTaxi-Session': 'eats:',
    'X-YaTaxi-Bound-UserIds': '',
    'X-YaTaxi-Bound-Sessions': '',
    'X-Eats-User': f'user_id={EATER_ID},',
}


@pytest.fixture(name='handle')
def set_up_handle(taxi_eats_cart, local_services, db_insert):
    class Context:
        def request(self, method, *args, **kwargs):
            return getattr(self, method)(*args, **kwargs)

        @staticmethod
        def lock_cart(for_pickup):
            return utils.call_lock_cart(
                taxi_eats_cart, EATER_ID, HEADERS, for_pickup,
            )

        @staticmethod
        def set_order(cart_id, order_nr=ORDER_NR, revision=1):
            return taxi_eats_cart.post(
                '/internal/eats-cart/v1/set_order',
                headers=HEADERS,
                json={
                    'cart_id': cart_id,
                    'order_nr': order_nr,
                    'revision': revision,
                },
            )

        @staticmethod
        def cancel_order(cart_id):
            return taxi_eats_cart.post(
                '/internal/eats-cart/v1/cancel_order',
                headers=HEADERS,
                json={'cart_id': cart_id},
            )

        @staticmethod
        def post_item(request_params, eater_id=EATER_ID):
            return taxi_eats_cart.post(
                'api/v1/cart',
                params=request_params,
                headers=utils.get_auth_headers(eater_id),
                json=dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES),
            )

        @staticmethod
        def set_order_dry_run(order_nr=ORDER_NR, eater_id=EATER_ID):
            return taxi_eats_cart.post(
                '/internal/eats-cart/v1/set_order_dry_run',
                headers=HEADERS,
                json={'eater_id': eater_id, 'order_nr': order_nr},
            )

    return Context()


@pytest.fixture(name='assert_order_is_set')
def _assert_order_is_set(eats_cart_cursor):
    def do_assert_order_is_set(eater_id, cart_id, order_nr):
        eats_cart_cursor.execute(
            'SELECT * from eats_cart.eater_cart WHERE cart_id = %s',
            (cart_id,),
        )
        assert not eats_cart_cursor.fetchall()

        eats_cart_cursor.execute(
            'SELECT eater_id, order_nr from eats_cart.carts WHERE id = %s',
            (cart_id,),
        )
        assert eats_cart_cursor.fetchone() == [eater_id, order_nr]

    return do_assert_order_is_set


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.now('2021-04-03T01:12:46+0300')
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_set_order_nr(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        handle,
        assert_order_is_set,
        for_pickup,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await handle.request('lock_cart', for_pickup)
    assert response.status_code == 200
    cart_id = response.json()['cart_id']
    revision = response.json()['revision']

    eats_cart_cursor.execute(
        'SELECT checked_out_at from eats_cart.carts WHERE eater_id = %s',
        (EATER_ID,),
    )
    result = eats_cart_cursor.fetchone()
    assert result[0].isoformat() == '2021-04-03T01:12:46+03:00'

    response = await handle.request(
        'set_order', cart_id, ORDER_NR, revision=revision,
    )
    assert response.status_code == 200

    assert_order_is_set(EATER_ID, cart_id, ORDER_NR)


CHECKED_OUT_TTL = 5000


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.config(EATS_CART_TIMEOUTS={'checked_out_ms': CHECKED_OUT_TTL})
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_setting_order_unlocks_eater(
        taxi_eats_cart, local_services, load_json, handle, for_pickup,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await handle.request('lock_cart', for_pickup)
    assert response.status_code == 200
    cart_id = response.json()['cart_id']
    revision = response.json()['revision']

    response = await handle.request(
        'post_item', local_services.request_params, EATER_ID,
    )
    assert response.status_code == 400

    response = await handle.request(
        'set_order', cart_id, ORDER_NR, revision=revision,
    )
    assert response.status_code == 200

    response = await handle.request(
        'post_item', local_services.request_params, EATER_ID,
    )
    assert response.status_code == 200


# 1. Cart is locked for checkout
# 2. Time reserved for setting order passes
# 3. Order is set on request regardless of whether any modification has occured
@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.config(EATS_CART_TIMEOUTS={'checked_out_ms': CHECKED_OUT_TTL})
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize('must_modify_cart', [True, False])
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_set_order_anyway(
        taxi_eats_cart,
        local_services,
        mocked_time,
        load_json,
        eats_cart_cursor,
        handle,
        assert_order_is_set,
        must_modify_cart,
        for_pickup,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await handle.request('lock_cart', for_pickup)
    assert response.status_code == 200
    cart_id = response.json()['cart_id']
    revision = response.json()['revision']

    checked_out_sec = CHECKED_OUT_TTL // 1000
    mocked_time.sleep(checked_out_sec + 1)
    await taxi_eats_cart.invalidate_caches()

    if must_modify_cart:
        response = await handle.request(
            'post_item', local_services.request_params, EATER_ID,
        )
        assert response.status_code == 200

    response = await handle.request(
        'set_order', cart_id, ORDER_NR, revision=revision,
    )
    assert response.status_code == 200

    assert_order_is_set(EATER_ID, cart_id, ORDER_NR)


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'repeated_order_nr,response_code',
    [
        pytest.param(ORDER_NR, 200, id='same_order_nr'),
        pytest.param(ORDER_NR + '1', 400, id='different_order_nr'),
    ],
)
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_repeated_set_order_forbidden(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        handle,
        assert_order_is_set,
        repeated_order_nr,
        response_code,
        for_pickup,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'
    response = await handle.request('lock_cart', for_pickup)
    assert response.status_code == 200
    cart_id = response.json()['cart_id']

    # First set_order
    first_order_nr = ORDER_NR
    response = await handle.request('set_order', cart_id, first_order_nr)
    assert response.status_code == 200
    assert_order_is_set(EATER_ID, cart_id, first_order_nr)

    # Repeated set_order
    response = await handle.request('set_order', cart_id, repeated_order_nr)
    assert response.status_code == response_code
    assert_order_is_set(EATER_ID, cart_id, first_order_nr)


async def test_set_order_cart_not_found(taxi_eats_cart, handle):
    response = await handle.request('set_order', NOT_EXISTS_CART_ID, ORDER_NR)
    assert response.status_code == 404


@pytest.fixture(name='assert_cart_is_locked')
def _assert_cart_is_locked(eats_cart_cursor):
    def do_assert_cart_is_locked(cart_id, is_locked):
        eats_cart_cursor.execute(
            'SELECT checked_out_at from eats_cart.carts WHERE id = %s',
            (cart_id,),
        )
        result = eats_cart_cursor.fetchone()
        if is_locked:
            assert result[0] is not None
        else:
            assert result[0] is None

    return do_assert_cart_is_locked


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.config(EATS_CART_TIMEOUTS={'checked_out_ms': CHECKED_OUT_TTL})
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize('sleep_for_sec', [0, CHECKED_OUT_TTL + 1])
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_cancel_order(
        taxi_eats_cart,
        local_services,
        mocked_time,
        load_json,
        eats_cart_cursor,
        handle,
        sleep_for_sec,
        assert_cart_is_locked,
        for_pickup,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await handle.request('lock_cart', for_pickup)
    assert response.status_code == 200
    cart_id = response.json()['cart_id']
    assert_cart_is_locked(cart_id, True)

    mocked_time.sleep(sleep_for_sec)
    await taxi_eats_cart.invalidate_caches()

    response = await handle.request('cancel_order', cart_id)
    assert response.status_code == 200
    assert_cart_is_locked(cart_id, False)


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_lock_cancel_set(
        taxi_eats_cart,
        local_services,
        load_json,
        handle,
        assert_cart_is_locked,
        assert_order_is_set,
        for_pickup,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await handle.request('lock_cart', for_pickup)
    assert response.status_code == 200
    cart_id = response.json()['cart_id']
    assert_cart_is_locked(cart_id, True)

    response = await handle.request('cancel_order', cart_id)
    assert response.status_code == 200
    assert_cart_is_locked(cart_id, False)

    response = await handle.request('set_order', cart_id, ORDER_NR)
    assert response.status_code == 200
    assert_order_is_set(EATER_ID, cart_id, ORDER_NR)
    assert_cart_is_locked(cart_id, False)


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.pgsql('eats_cart', files=['insert_values.sql'])
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(True, id='pickup'), pytest.param(False, id='delivery')),
)
async def test_lock_set_cancel(
        taxi_eats_cart,
        local_services,
        load_json,
        handle,
        assert_cart_is_locked,
        assert_order_is_set,
        for_pickup,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await handle.request('lock_cart', for_pickup)
    assert response.status_code == 200
    cart_id = response.json()['cart_id']
    assert_cart_is_locked(cart_id, True)

    response = await handle.request('set_order', cart_id, ORDER_NR)
    assert response.status_code == 200
    assert_order_is_set(EATER_ID, cart_id, ORDER_NR)
    assert_cart_is_locked(cart_id, True)

    response = await handle.request('cancel_order', cart_id)
    assert response.status_code == 200
    assert_order_is_set(EATER_ID, cart_id, ORDER_NR)
    assert_cart_is_locked(cart_id, True)
