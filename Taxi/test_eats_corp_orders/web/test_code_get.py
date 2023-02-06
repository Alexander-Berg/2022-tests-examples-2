import pytest


@pytest.mark.now('2022-02-22T23:00:00+0000')
async def test_generate_new_code(
        taxi_eats_corp_orders_web,
        check_codes_db,
        check_headers_redis,
        load_json,
        proper_headers_code_get,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/code', headers=proper_headers_code_get,
    )
    assert response.status == 200
    content = await response.json()

    assert content['user_code']
    assert content['qr_code']
    assert content['expires_at']
    assert content['lifetime'] > 0

    check_codes_db(load_json('expected.json')['new'])
    check_headers_redis()


@pytest.mark.now('2022-02-22T22:01:00+0000')
async def test_get_existing_code(
        taxi_eats_corp_orders_web,
        check_codes_db,
        check_headers_redis,
        load_json,
        proper_headers_code_get,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/code', headers=proper_headers_code_get,
    )
    assert response.status == 200
    content = await response.json()

    assert content['user_code']
    assert content['qr_code']
    assert content['expires_at']
    assert content['lifetime'] > 0

    check_codes_db(load_json('expected.json')['existing'])
    check_headers_redis()


async def test_fails_if_no_x_eats_user(taxi_eats_corp_orders_web, yandex_uid):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/code', headers={'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 400


async def test_fails_if_no_x_yandex_uid(taxi_eats_corp_orders_web, eats_user):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/code', headers={'X-Eats-User': eats_user},
    )
    assert response.status == 400


async def test_fails_if_unauthorized(taxi_eats_corp_orders_web):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/code', headers={'X-Eats-User': '', 'X-Yandex-UID': ''},
    )
    assert response.status == 401
