import pytest

from tests_eats_cart import utils

PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'shippingType': 'delivery',
    'deliveryTime': '2021-04-04T11:00:00+03:00',
}
EATER_ID = 'eater1'
HEADERS = utils.get_auth_headers(EATER_ID)


@pytest.mark.parametrize(
    'endpoint,method,code',
    [
        pytest.param('/api/v1/cart/sync', 'post', 200, id='sync'),
        pytest.param('/api/v2/cart', 'delete', 204, id='delete'),
    ],
)
@pytest.mark.now('2021-06-22T15:58:18+00:00')
async def test_delete_existing_cart(
        taxi_eats_cart,
        eats_cart_cursor,
        local_services,
        load_json,
        db_insert,
        endpoint,
        method,
        code,
):
    cart_id = db_insert.cart(EATER_ID)
    db_insert.eater_cart(EATER_ID, cart_id)

    response = await getattr(taxi_eats_cart, method)(
        endpoint, params=PARAMS, headers=HEADERS, json={},
    )

    assert response.status_code == code

    if method == 'delete':
        response = await taxi_eats_cart.get(
            'api/v1/cart', params=PARAMS, headers=HEADERS,
        )
        assert response.status_code == 200
        resp_cart = response.json()
    else:
        resp_cart = response.json()['cart']

    expected_json = load_json('empty_cart.json')
    assert resp_cart == expected_json

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    assert result[0]['id'] == cart_id
    assert result[0]['deleted_at'] is not None

    eats_cart_cursor.execute(utils.SELECT_EATER_CART)
    result = eats_cart_cursor.fetchall()
    assert len(result) == 1
    assert result[0]['eater_id'] == EATER_ID
    assert result[0]['cart_id'] is None


@pytest.mark.parametrize(
    'endpoint,method, code',
    [
        pytest.param('/api/v1/cart/sync', 'post', 200, id='sync'),
        pytest.param('/api/v2/cart', 'delete', 204, id='delete'),
    ],
)
@pytest.mark.now('2021-06-22T15:58:18+00:00')
async def test_delete_no_cart(
        taxi_eats_cart,
        local_services,
        eats_cart_cursor,
        load_json,
        endpoint,
        method,
        code,
):
    response = await getattr(taxi_eats_cart, method)(
        endpoint, params=PARAMS, headers=HEADERS, json={},
    )

    assert response.status_code == code

    if method == 'delete':
        response = await taxi_eats_cart.get(
            'api/v1/cart', params=PARAMS, headers=HEADERS,
        )
        assert response.status_code == 200
        resp_cart = response.json()
    else:
        resp_cart = response.json()['cart']

    expected_json = load_json('empty_cart.json')
    assert resp_cart == expected_json

    eats_cart_cursor.execute(utils.SELECT_CART)
    result = eats_cart_cursor.fetchall()
    assert not result  # empty

    eats_cart_cursor.execute(utils.SELECT_EATER_CART)
    result = eats_cart_cursor.fetchall()
    assert not result  # empty


@pytest.mark.parametrize(
    (), utils.LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS,
)
@pytest.mark.config(EATS_CART_TIMEOUTS={'checked_out_ms': 5000})
@pytest.mark.pgsql('eats_cart', files=['current_cart.sql'])
async def test_delete_lock_cart(taxi_eats_cart, local_services):

    lock_response = await utils.call_lock_cart(
        taxi_eats_cart, EATER_ID, HEADERS,
    )
    assert lock_response.status == 200

    response = await taxi_eats_cart.delete(
        f'/api/v2/cart', params=PARAMS, headers=HEADERS,
    )
    assert response.status_code == 400
