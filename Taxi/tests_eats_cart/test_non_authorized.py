import pytest

from . import utils

MENU_ITEM_ID = 232323
PLACE_SLUG = 'place123'
PLACE_ID = '22'
CART_WITH_EATER_ID = '1a73add7-9c84-4440-9d3a-12f3e71c6026'

ZUSER_ID = 'z000'
ZUSER_SESSION = 'taxi:' + ZUSER_ID
BOUND_USER_IDS = ('z007', '007', ZUSER_ID, 'z1')
BOUND_SESSIONS = ','.join('taxi:' + user_id for user_id in BOUND_USER_IDS)

BOUND_USER_EATS = ('007', '1', 'test')
BOUND_SESSIONS_EATS = ','.join(
    'eats:' + user_id for user_id in BOUND_USER_EATS
)

ZUSER_HEADERS = {
    'X-YaTaxi-Session': ZUSER_SESSION,
    'X-Idempotency-Token': 'zuser-idempotency',
}

AUTHORIZED_USER_ID = '111'
EATS_USER_ID = 'eater2'
SESSION_EATS = 'eats:' + AUTHORIZED_USER_ID
SESSION_TAXI = 'taxi:' + AUTHORIZED_USER_ID

HEADERS_TAXI = {
    'X-YaTaxi-Session': SESSION_TAXI,
    'X-Idempotency-Token': 'auth-idempotency',
}

HEADERS_EATS = {
    'X-YaTaxi-Session': SESSION_EATS,
    'X-Idempotency-Token': 'auth-idempotency',
    'X-YaTaxi-Bound-Sessions': BOUND_SESSIONS_EATS,
}
AUTH_HEADERS_TAXI = {
    'X-Eats-User': f'user_id={EATS_USER_ID}',
    'X-YaTaxi-Bound-UserIds': ','.join(BOUND_USER_IDS),
    'X-YaTaxi-Bound-Sessions': BOUND_SESSIONS,
    **HEADERS_TAXI,
}
AUTH_HEADERS_EATS = {'X-Eats-User': f'user_id={EATS_USER_ID}', **HEADERS_EATS}


def set_most_recent_uid(cursor, uid):
    cursor.execute(
        'SELECT id FROM eats_cart.carts ' 'ORDER BY created_at DESC LIMIT 1',
    )
    cart_id = cursor.fetchone()[0]
    cursor.execute(
        'UPDATE eats_cart.carts SET eater_id = %s WHERE id = %s',
        (uid, cart_id),
    )
    cursor.execute(
        'UPDATE eats_cart.eater_cart SET eater_id = %s WHERE cart_id = %s',
        (uid, cart_id),
    )


@pytest.mark.now('2021-12-03T01:13:31+03:00')
@pytest.mark.parametrize(
    'headers,uid_in_db',
    [
        pytest.param(ZUSER_HEADERS, ZUSER_SESSION, id='non_auth_taxi'),
        pytest.param(AUTH_HEADERS_TAXI, ZUSER_SESSION, id='auth_taxi'),
        pytest.param(HEADERS_EATS, SESSION_EATS, id='non_auth_eats'),
        pytest.param(AUTH_HEADERS_EATS, SESSION_EATS, id='auth_eats'),
    ],
)
@pytest.mark.pgsql(
    'eats_cart', files=['insert_with_eater_id.sql', 'insert_with_session.sql'],
)
@utils.additional_payment_text()
async def test_get_most_recent(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        headers,
        uid_in_db,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    set_most_recent_uid(eats_cart_cursor, uid_in_db)

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=local_services.request_params, headers=headers,
    )

    assert response.status_code == 200

    expected_json = load_json('expected_options_no_surge.json')
    del expected_json['updated_at']
    resp = response.json()
    del resp['updated_at']
    del resp['id']
    del resp['revision']
    assert resp == expected_json


@pytest.mark.parametrize(
    'headers,uid_in_db,must_update',
    [
        pytest.param(ZUSER_HEADERS, ZUSER_SESSION, False, id='non_auth_taxi'),
        pytest.param(AUTH_HEADERS_TAXI, ZUSER_SESSION, True, id='auth_taxi'),
        pytest.param(HEADERS_EATS, SESSION_EATS, False, id='non_auth_eats'),
        pytest.param(AUTH_HEADERS_EATS, SESSION_EATS, True, id='auth_eats'),
    ],
)
@pytest.mark.parametrize('available_discounts', [True, False])
@pytest.mark.pgsql('eats_cart', files=['insert_with_eater_id.sql'])
@utils.additional_payment_text()
async def test_put_into_proper_cart(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        db_insert,
        headers,
        uid_in_db,
        must_update,
        available_discounts,
):
    cart_item_price = 50
    cart_item_promo_price = 48.95
    local_services.available_discounts = available_discounts

    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    local_services.core_discounts_response = load_json(
        'get_proper_discount.json',
    )

    cart_id = db_insert.cart(
        uid_in_db,
        place_slug=PLACE_SLUG,
        place_id=PLACE_ID,
        promo_subtotal=cart_item_promo_price,
        total=cart_item_promo_price,
    )
    db_insert.eater_cart(uid_in_db, cart_id)
    cart_item_id = db_insert.cart_item(
        cart_id,
        MENU_ITEM_ID,
        price=cart_item_price,
        promo_price=cart_item_promo_price,
        quantity=1,
    )

    response = await taxi_eats_cart.put(
        f'/api/v1/cart/{cart_item_id}',
        params=local_services.request_params,
        headers=headers,
        json=utils.ITEM_PROPERTIES,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    if must_update:
        uid_in_db = EATS_USER_ID

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 2
    assert utils.pg_result_to_repr(result)[1] == [
        cart_id,
        '2',
        uid_in_db,
        PLACE_SLUG,
        PLACE_ID,
        '118.56',  # promo_subtotal
        '138.56',  # total
        '20.00',  # delivery_fee
        'delivery',
        'None',
        '(25,35)',
    ]
    if must_update:
        assert result[0]['deleted_at'] is not None
    else:
        assert result[0]['deleted_at'] is None

    eats_cart_cursor.execute(utils.SELECT_EATER_CART + ' ORDER BY id DESC')
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1 + (not must_update)
    assert utils.pg_result_to_repr(result)[0] == [uid_in_db, cart_id]
    if not must_update:
        assert utils.pg_result_to_repr(result)[1] == [
            EATS_USER_ID,
            CART_WITH_EATER_ID,
        ]

    expected_json = load_json('expected_with_options.json')
    expected_json['cart']['items'][0]['id'] = int(cart_item_id)

    response_json = response.json()
    del response_json['cart']['updated_at']
    del response_json['cart']['id']
    del response_json['cart']['revision']
    assert response_json == expected_json


@pytest.mark.parametrize(
    'headers,uid_in_db,delete_by_eater',
    [
        pytest.param(ZUSER_HEADERS, ZUSER_SESSION, False, id='non_auth_taxi'),
        pytest.param(AUTH_HEADERS_TAXI, ZUSER_SESSION, True, id='auth_taxi'),
        pytest.param(HEADERS_EATS, SESSION_EATS, False, id='non_auth_eats'),
        pytest.param(AUTH_HEADERS_EATS, SESSION_EATS, True, id='auth_eats'),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['insert_with_eater_id.sql'])
@pytest.mark.parametrize(
    'endpoint,method,code',
    [
        pytest.param('/api/v1/cart/sync', 'post', 200, id='sync'),
        pytest.param('/api/v2/cart', 'delete', 204, id='delete'),
    ],
)
async def test_delete_proper_cart(
        taxi_eats_cart,
        local_services,
        eats_cart_cursor,
        db_insert,
        headers,
        uid_in_db,
        delete_by_eater,
        method,
        endpoint,
        code,
):
    cart_item_price = 50
    cart_item_promo_price = 48.95

    cart_id = db_insert.cart(
        uid_in_db,
        place_slug=PLACE_SLUG,
        place_id=PLACE_ID,
        promo_subtotal=cart_item_promo_price,
        total=cart_item_promo_price,
        service_fee=20,
    )
    db_insert.eater_cart(uid_in_db, cart_id)
    db_insert.cart_item(
        cart_id,
        MENU_ITEM_ID,
        price=cart_item_price,
        promo_price=cart_item_promo_price,
        quantity=1,
    )

    response = await getattr(taxi_eats_cart, method)(
        endpoint,
        params=local_services.request_params,
        headers=headers,
        json={},
    )

    assert response.status_code == code

    if delete_by_eater:
        uid_in_db = EATS_USER_ID

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 2
    assert result[1]['deleted_at'] is not None
    if delete_by_eater:
        assert result[0]['deleted_at'] is not None
    else:
        assert result[0]['deleted_at'] is None

    eats_cart_cursor.execute(utils.SELECT_EATER_CART + ' ORDER BY id DESC')
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1 + (not delete_by_eater)
    if not delete_by_eater:
        assert utils.pg_result_to_repr(result)[0] == [uid_in_db, 'None']
        assert utils.pg_result_to_repr(result)[1] == [
            EATS_USER_ID,
            CART_WITH_EATER_ID,
        ]
    else:
        assert utils.pg_result_to_repr(result)[0] == [uid_in_db, 'None']


# 1. Insert cart with EATS_USER_ID
# 2. Create new cart for non-authorized user
# 3. Delete stale cart and update recent one after authorization
@pytest.mark.parametrize(
    'headers,auth_headers',
    [
        pytest.param(HEADERS_EATS, AUTH_HEADERS_EATS, id='native_eats'),
        pytest.param(ZUSER_HEADERS, AUTH_HEADERS_TAXI, id='super_app'),
    ],
)
@pytest.mark.parametrize(
    'url,request_body',
    [
        pytest.param(
            'api/v1/cart',
            dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES),
            id='add_item',
        ),
        pytest.param(
            '/api/v1/cart/sync',
            {'items': [dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)]},
            id='sync_cart',
        ),
        pytest.param(
            '/api/v1/cart/add_bulk',
            {'items': [dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)]},
            id='add_bulk_cart',
        ),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['insert_with_eater_id.sql'])
async def test_post_sequential(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        headers,
        auth_headers,
        url,
        request_body,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        url,
        params=local_services.request_params,
        headers=headers,
        json=request_body,
    )
    assert response.status_code == 200

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 2

    assert result[1]['eater_id'] == headers['X-YaTaxi-Session']
    assert result[0]['eater_id'] == EATS_USER_ID
    assert result[0]['deleted_at'] is None
    new_cart_id = result[1]['id']

    eats_cart_cursor.execute(utils.SELECT_EATER_CART + ' ORDER BY id DESC')
    result = eats_cart_cursor.fetchall()
    assert utils.pg_result_to_repr(result) == [
        [headers['X-YaTaxi-Session'], new_cart_id],
        [EATS_USER_ID, CART_WITH_EATER_ID],
    ]

    response = await taxi_eats_cart.post(
        url,
        params=local_services.request_params,
        headers=auth_headers,
        json=request_body,
    )
    assert response.status_code == 200

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    if 'sync' in url:
        assert len(result) == 3
        assert result[1]['eater_id'] == EATS_USER_ID
        assert result[1]['id'] == new_cart_id
        assert result[1]['deleted_at'] is not None
        new_cart_id = result[-1]['id']
    else:
        assert len(result) == 2

    assert result[-1]['eater_id'] == EATS_USER_ID
    assert result[-1]['id'] == new_cart_id
    assert result[0]['eater_id'] == EATS_USER_ID
    assert result[0]['id'] == CART_WITH_EATER_ID
    assert result[0]['deleted_at'] is not None

    eats_cart_cursor.execute(utils.SELECT_EATER_CART + ' ORDER BY id DESC')
    result = eats_cart_cursor.fetchall()
    assert utils.pg_result_to_repr(result) == [[EATS_USER_ID, new_cart_id]]


# 1. POST for non-authorized user
# 2. POST for authorized user
# 2. Replace session_id by eats_user_id in postgres after authorization
@pytest.mark.parametrize(
    'headers,auth_headers',
    [
        pytest.param(HEADERS_EATS, AUTH_HEADERS_EATS, id='native_eats'),
        pytest.param(ZUSER_HEADERS, AUTH_HEADERS_TAXI, id='super_app'),
    ],
)
@pytest.mark.parametrize(
    'url,request_body',
    [
        ('api/v1/cart', dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)),
        (
            '/api/v1/cart/sync',
            {'items': [dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)]},
        ),
        (
            '/api/v1/cart/add_bulk',
            {'items': [dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)]},
        ),
    ],
)
@pytest.mark.parametrize(
    'mapping_turn_on',
    [
        pytest.param(
            True,
            marks=utils.setup_available_features(['mapping_eater_cart']),
            id='mapping_turn_on',
        ),
        pytest.param(False, id='mapping_turn_off'),
    ],
)
async def test_replace_session_by_eater_id(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        headers,
        auth_headers,
        url,
        request_body,
        stq,
        mapping_turn_on,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        url,
        params=local_services.request_params,
        headers=headers,
        json=request_body,
    )
    assert response.status_code == 200

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1

    assert result[0]['eater_id'] == headers['X-YaTaxi-Session']
    new_cart_id = result[0]['id']

    eats_cart_cursor.execute(utils.SELECT_EATER_CART)
    result = eats_cart_cursor.fetchall()
    assert utils.pg_result_to_repr(result) == [
        [headers['X-YaTaxi-Session'], new_cart_id],
    ]

    response = await taxi_eats_cart.post(
        url,
        params=local_services.request_params,
        headers=auth_headers,
        json=request_body,
    )
    assert response.status_code == 200

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    if 'sync' in url:
        assert len(result) == 2
        assert result[0]['eater_id'] == EATS_USER_ID
        assert result[0]['id'] == new_cart_id
        assert result[0]['deleted_at'] is not None
        new_cart_id = result[1]['id']
    else:
        assert len(result) == 1

    assert result[-1]['eater_id'] == EATS_USER_ID
    assert result[-1]['id'] == new_cart_id
    assert result[-1]['deleted_at'] is None
    cart_id_in_mapping = new_cart_id
    eats_cart_cursor.execute(utils.SELECT_EATER_CART)
    result = eats_cart_cursor.fetchall()
    assert utils.pg_result_to_repr(result) == [[EATS_USER_ID, new_cart_id]]
    if not mapping_turn_on:
        assert stq.eats_cart_add_pair_to_mapping.times_called == 0
        return
    if 'sync' in url:
        assert stq.eats_cart_add_pair_to_mapping.times_called == 2
        stq.eats_cart_add_pair_to_mapping.next_call()
        task_info = stq.eats_cart_add_pair_to_mapping.next_call()
    else:
        assert stq.eats_cart_add_pair_to_mapping.times_called == 1
        task_info = stq.eats_cart_add_pair_to_mapping.next_call()
    assert task_info['queue'] == 'eats_cart_add_pair_to_mapping'
    assert task_info['kwargs']['eater_id'] == EATS_USER_ID
    assert task_info['kwargs']['cart_id'] == cart_id_in_mapping


@pytest.mark.parametrize(
    'headers,uid_in_db',
    [
        pytest.param(AUTH_HEADERS_TAXI, ZUSER_SESSION, id='non_auth_taxi'),
        pytest.param(AUTH_HEADERS_TAXI, EATS_USER_ID, id='auth_taxi'),
        pytest.param(AUTH_HEADERS_EATS, SESSION_EATS, id='non_auth_eats'),
        pytest.param(AUTH_HEADERS_EATS, EATS_USER_ID, id='auth_eats'),
    ],
)
async def test_user_with_deleted_cart(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        uid_in_db,
        headers,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    eats_cart_cursor.execute(
        'INSERT INTO eats_cart.eater_cart(eater_id) VALUES (%s)', (uid_in_db,),
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=headers,
        json=dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES),
    )
    assert response.status_code == 200


# cart/post is not included b/c it was extensively
# tested earlier in this module
@pytest.mark.parametrize(
    'mode,handle,response_code',
    [
        pytest.param(
            'delete',
            '/api/v1/cart/disabled-items',
            401,
            id='del_v1_disabled_items',
        ),
        pytest.param('delete', '/api/v1/cart/1', 401, id='del_v1_cart'),
        pytest.param(
            'delete', '/api/v1/cart/promocode', 401, id='del_v1_promocode',
        ),
        pytest.param(
            'delete',
            '/api/v1/cart/unavailable-items-by-time',
            401,
            id='del_v1_unavailable-items-by-time',
        ),
        pytest.param('delete', '/api/v2/cart', 401, id='del_v2_cart'),
        pytest.param('put', '/api/v1/cart/1', 401, id='put_v1_cart'),
        pytest.param(
            'post', '/api/v1/cart/promocode', 403, id='post_v1_promocode',
        ),
        pytest.param('post', '/api/v1/cart/sync', 401, id='post_v1_sync'),
        pytest.param(
            'post', '/api/v1/cart/update_bulk', 401, id='post_v1_update_bulk',
        ),
        pytest.param(
            'post', '/api/v1/cart/add_bulk', 401, id='post_v1_add_bulk',
        ),
        pytest.param('get', '/api/v1/cart', 200, id='get_v1_cart'),
    ],
)
async def test_no_session_and_eater_id(
        taxi_eats_cart, mode, handle, response_code,
):
    request_body = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)
    if mode == 'delete':
        request_body = {}
    elif mode == 'post':
        request_body['code'] = '1'

    status_code = (
        await getattr(taxi_eats_cart, mode)(
            handle, params={}, headers={}, json=request_body,
        )
    ).status_code

    assert status_code == response_code


# database contains only old eater_ids that remain only in bound sessions
# after we execute POST request eater_ids should be equal to primary user id
@pytest.mark.parametrize(
    'headers,expected_session_id',
    [
        pytest.param(AUTH_HEADERS_EATS, EATS_USER_ID, id='eats_authorized'),
        pytest.param(HEADERS_EATS, SESSION_EATS, id='eats_unauthorized'),
    ],
)
@pytest.mark.parametrize(
    'url,request_body',
    [
        ('api/v1/cart', dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)),
        (
            '/api/v1/cart/sync',
            {'items': [dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)]},
        ),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['insert_with_stale_eater_id.sql'])
async def test_bound_sessions(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        url,
        request_body,
        headers,
        expected_session_id,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    response = await taxi_eats_cart.post(
        url,
        params=local_services.request_params,
        headers=headers,
        json=request_body,
    )
    assert response.status_code == 200

    eats_cart_cursor.execute(utils.SELECT_CART + ' DESC')
    result = eats_cart_cursor.fetchall()

    if 'sync' in url:
        assert result[3]['eater_id'] == expected_session_id
        assert result[3]['deleted_at'] is not None
        assert result[0]['eater_id'] == expected_session_id
        assert result[0]['deleted_at'] is None
        assert result[2]['deleted_at'] is not None
    else:
        assert result[2]['eater_id'] == expected_session_id
        assert result[2]['deleted_at'] is None
        assert result[0]['deleted_at'] is not None

    assert result[1]['deleted_at'] is not None


async def test_authorization_status_changes_with_intact_cart(
        taxi_eats_cart, local_services, load_json, eats_cart_cursor,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    eats_cart_cursor.execute(
        'INSERT INTO eats_cart.eater_cart(eater_id) VALUES (%s)',
        (EATS_USER_ID,),
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=AUTH_HEADERS_EATS,
        json=dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES),
    )
    assert response.status_code == 200
    assert response.json()['cart']['subtotal'] == 124

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=HEADERS_EATS,
    )

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=AUTH_HEADERS_EATS,
        json=dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES),
    )
    assert response.status_code == 200
    assert response.json()['cart']['subtotal'] == 2 * 124
