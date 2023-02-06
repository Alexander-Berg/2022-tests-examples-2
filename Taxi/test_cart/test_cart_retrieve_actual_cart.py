import datetime

import pytest

from tests_grocery_cart import common


@pytest.mark.parametrize('check_key', ['yandex_uid', 'eats_id'])
async def test_200(taxi_grocery_cart, cart, check_key):
    test_headers = (
        common.TAXI_HEADERS.copy()
        if check_key == 'yandex_uid'
        else common.EDATAXI_HEADERS.copy()
    )

    await cart.modify({}, currency='RUB', headers=test_headers)

    cart.update_db()
    await cart.checkout(headers=test_headers)

    await taxi_grocery_cart.invalidate_caches()

    if check_key == 'eats_id':
        test_headers['X-Yandex-UID'] = test_headers['X-Yandex-UID'] + 'other'

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/retrieve/actual-cart',
        json={},
        headers=test_headers,
    )

    assert response.status_code == 200
    assert response.json()['cart_id'] == cart.cart_id


async def test_404(taxi_grocery_cart, cart):
    test_headers = common.EDATAXI_HEADERS.copy()

    await cart.modify({}, currency='RUB', headers=test_headers)

    cart.update_db()
    await cart.checkout(headers=test_headers)

    await taxi_grocery_cart.invalidate_caches()

    test_headers['X-Yandex-UID'] = test_headers['X-Yandex-UID'] + 'other'
    test_headers['X-YaTaxi-User'] = test_headers['X-YaTaxi-User'] + 'other'

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/retrieve/actual-cart',
        json={},
        headers=test_headers,
    )

    assert response.status_code == 404


@pytest.mark.pgsql('grocery_cart', files=['create_checked_out.sql'])
async def test_checked_out_404(taxi_grocery_cart):
    await taxi_grocery_cart.invalidate_caches()

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/retrieve/actual-cart',
        json={},
        headers=common.EDATAXI_HEADERS,
    )

    assert response.status_code == 404


INSERT_CHECKED_OUT_WITH_UPDATED_TIME = """
INSERT INTO cart.carts (
    cart_id,
    cart_version,
    user_type,
    user_id,
    session,
    bound_sessions,
    status,
    updated)
VALUES (
    %s,
    10,
    'eats_user_id',
    '123',
    'eats:123',
    array[]::TEXT[],
    'editing',
     %s);
"""


@pytest.mark.parametrize('reverse_order', [True, False])
async def test_freshest_cart_returned(
        taxi_grocery_cart, pgsql, reverse_order, now,
):
    cursor = pgsql['grocery_cart'].cursor()

    older_updated_ts = now - datetime.timedelta(hours=4)
    older_cart_id = '00000000-0000-0000-0000-000000000000'

    fresher_updated_ts = now - datetime.timedelta(hours=3)
    fresher_cart_id = '00000000-0000-0000-0000-000000000001'

    if reverse_order:
        cursor.execute(
            INSERT_CHECKED_OUT_WITH_UPDATED_TIME,
            (fresher_cart_id, fresher_updated_ts),
        )
        cursor.execute(
            INSERT_CHECKED_OUT_WITH_UPDATED_TIME,
            (older_cart_id, older_updated_ts),
        )
    else:
        cursor.execute(
            INSERT_CHECKED_OUT_WITH_UPDATED_TIME,
            (older_cart_id, older_updated_ts),
        )
        cursor.execute(
            INSERT_CHECKED_OUT_WITH_UPDATED_TIME,
            (fresher_cart_id, fresher_updated_ts),
        )

    await taxi_grocery_cart.invalidate_caches()

    test_headers = common.EDATAXI_HEADERS.copy()

    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/retrieve/actual-cart',
        json={},
        headers=test_headers,
    )

    assert response.status_code == 200
    assert response.json()['cart_id'] == fresher_cart_id


async def test_401(taxi_grocery_cart):
    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/retrieve/actual-cart', json={},
    )
    assert response.status_code == 401
