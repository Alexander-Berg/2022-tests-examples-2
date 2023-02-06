import copy

import pytest


@pytest.mark.now('2022-02-22T22:01:00+0000')
@pytest.mark.pgsql('eats_corp_orders', files=['existing_order.sql'])
async def test_success(
        taxi_eats_corp_orders_web,
        check_codes_db,
        check_redis_array,
        proper_headers_code_get,
        order_id,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/user/confirm-order',
        headers=proper_headers_code_get,
        json={'order_id': order_id},
    )
    assert response.status == 200

    check_redis_array(f'confirmation_{order_id}', [True])


async def test_fails_if_no_x_eats_user(
        taxi_eats_corp_orders_web, yandex_uid, order_id,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/user/confirm-order', json={'order_id': order_id},
    )
    assert response.status == 400


async def test_fails_if_no_order_id(
        taxi_eats_corp_orders_web, yandex_uid, proper_headers_code_get,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/user/confirm-order', headers=proper_headers_code_get,
    )
    assert response.status == 400


@pytest.mark.pgsql('eats_corp_orders', files=['existing_order.sql'])
async def test_fails_if_other_user_tries_to_confirm(
        taxi_eats_corp_orders_web,
        yandex_uid,
        proper_headers_code_get,
        order_id,
):
    headers_with_other_user = copy.copy(proper_headers_code_get)
    headers_with_other_user['X-Eats-User'] = 'user_id=0'
    response = await taxi_eats_corp_orders_web.post(
        '/v1/user/confirm-order',
        headers=headers_with_other_user,
        json={'order_id': order_id},
    )
    assert response.status == 401


async def test_fails_if_order_not_exists(
        taxi_eats_corp_orders_web,
        yandex_uid,
        proper_headers_code_get,
        order_id,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/user/confirm-order',
        headers=proper_headers_code_get,
        json={'order_id': order_id},
    )
    assert response.status == 404
