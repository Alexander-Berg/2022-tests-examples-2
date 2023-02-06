# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eats_restapp_authorizer_plugins.generated_tests import *
import json
import pytest

GENERATE_TOKEN_URL = '/v1/session/generate-token'
SET_URL = '/v1/session/set'
CREATE_URL = '/v1/session/create'
CURRENT_URL = '/v1/session/current'
UNSET_URL = '/v1/session/unset'
UNSET_BY_PARTNER_URL = '/v1/session/unset-by-partner'
HEADERS = {'Content-type': 'application/json'}
EXTRA = {'headers': HEADERS}


async def test_generate_token(taxi_eats_restapp_authorizer):
    response = await taxi_eats_restapp_authorizer.post(GENERATE_TOKEN_URL)

    assert response.status_code == 201
    assert 'token' in response.json()


async def test_create_session(taxi_eats_restapp_authorizer):
    data = {'partner_id': 1, 'email': 'email@yandex.ru'}
    response = await taxi_eats_restapp_authorizer.post(CREATE_URL, json=data)

    assert response.status_code == 201
    assert 'token' in response.json()


async def test_set(taxi_eats_restapp_authorizer):
    token = '000'
    data = {'token': token, 'partner_id': 1, 'email': 'email@yandex.ru'}
    response = await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 201


async def test_set_repeated(taxi_eats_restapp_authorizer):
    token = '000'
    data = {'token': token, 'partner_id': 1, 'email': 'email@yandex.ru'}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    response = await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 201


async def test_set_400(taxi_eats_restapp_authorizer):
    data = {'partner_id': 1, 'email': 'email@yandex.ru'}
    response = await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 400


async def test_set_400_token_conflict(taxi_eats_restapp_authorizer):
    token = '000'
    data = {'token': token, 'partner_id': 1, 'email': 'email@yandex.ru'}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    data = {'token': token, 'partner_id': 2, 'email': 'email@yandex.ru'}
    response = await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'TOKEN_USED_BY_OTHER_PARTNER'


async def test_set_400_after_unset_by_partner(taxi_eats_restapp_authorizer):
    token = '000'
    set_data = {'token': token, 'partner_id': 1, 'email': 'email@yandex.ru'}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(set_data), **EXTRA,
    )

    unset_by_partner_data = {'partner_id': 1}
    await taxi_eats_restapp_authorizer.post(
        UNSET_BY_PARTNER_URL, data=json.dumps(unset_by_partner_data), **EXTRA,
    )

    response = await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(set_data), **EXTRA,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'SESSION_UNSET'


async def test_current(taxi_eats_restapp_authorizer):
    token = '111'
    partner_id = 1
    email = 'email@yandex.ru'
    data = {'token': token, 'partner_id': partner_id, 'email': email}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        CURRENT_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 200
    assert response.json()['partner_id'] == partner_id
    assert response.json()['email'] == email


@pytest.mark.redis_store(
    ['set', 'partner_id:1', '{"email":"email@yandex.ru","version":"22"}'],
    ['expire', 'partner_id:1', 3000],
    ['set', 'token:111', '{"partner_id":1,"version":"22"}'],
    ['expire', 'token:111', 3000],
)
async def test_current_nearly_expired_ttl(
        taxi_eats_restapp_authorizer, redis_store,
):
    token = '111'
    partner_id = 1
    email = 'email@yandex.ru'
    data = {'token': token, 'partner_id': partner_id, 'email': email}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        CURRENT_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 200
    assert response.json()['partner_id'] == partner_id
    assert response.json()['email'] == email

    hour_sec = 60 * 60  # Seconds per hour
    token_ttl_sec = hour_sec * 24 * 7  # 7 days
    assert redis_store.ttl('partner_id:1') > token_ttl_sec - hour_sec
    assert redis_store.ttl('token:111') > token_ttl_sec - hour_sec


async def test_current_404(taxi_eats_restapp_authorizer):
    token = '222'
    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        CURRENT_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 404


async def test_current_404_after_token_conflict(taxi_eats_restapp_authorizer):
    token = '000'
    data = {'token': token, 'partner_id': 1, 'email': 'email@yandex.ru'}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    data = {'token': token, 'partner_id': 2, 'email': 'email@yandex.ru'}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        CURRENT_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 404


async def test_unset(taxi_eats_restapp_authorizer):
    # 4 запроса : set -> current -> unset -> current
    token = '333'
    partner_id = 1
    email = 'email@yandex.ru'
    data = {'token': token, 'partner_id': partner_id, 'email': email}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        CURRENT_URL, data=json.dumps(data), **EXTRA,
    )
    assert response.status_code == 200

    response = await taxi_eats_restapp_authorizer.post(
        UNSET_URL, data=json.dumps(data), **EXTRA,
    )
    assert response.status_code == 200

    response = await taxi_eats_restapp_authorizer.post(
        CURRENT_URL, data=json.dumps(data), **EXTRA,
    )
    assert response.status_code == 404


async def test_unset_404(taxi_eats_restapp_authorizer):
    token = '444'
    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        UNSET_URL, data=json.dumps(data), **EXTRA,
    )

    assert response.status_code == 404


async def test_unset_by_partner(taxi_eats_restapp_authorizer):
    token = '111'
    partner_id = 1
    email = 'email@yandex.ru'
    data = {'token': token, 'partner_id': partner_id, 'email': email}
    await taxi_eats_restapp_authorizer.post(
        SET_URL, data=json.dumps(data), **EXTRA,
    )

    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        CURRENT_URL, data=json.dumps(data), **EXTRA,
    )
    assert response.status_code == 200

    data = {'partner_id': partner_id}
    response = await taxi_eats_restapp_authorizer.post(
        UNSET_BY_PARTNER_URL, data=json.dumps(data), **EXTRA,
    )
    assert response.status_code == 200

    data = {'token': token}
    response = await taxi_eats_restapp_authorizer.post(
        CURRENT_URL, data=json.dumps(data), **EXTRA,
    )
    assert response.status_code == 404


async def test_unset_by_partner_multiple_sessions(
        taxi_eats_restapp_authorizer,
):
    token1 = '111'
    token2 = '222'
    partner_id = 1
    email = 'email@yandex.ru'
    for token in [token1, token2]:
        data = {'token': token, 'partner_id': partner_id, 'email': email}
        await taxi_eats_restapp_authorizer.post(
            SET_URL, data=json.dumps(data), **EXTRA,
        )

    data = {'partner_id': partner_id}
    response = await taxi_eats_restapp_authorizer.post(
        UNSET_BY_PARTNER_URL, data=json.dumps(data), **EXTRA,
    )
    assert response.status_code == 200

    for token in [token1, token2]:
        data = {'token': token}
        response = await taxi_eats_restapp_authorizer.post(
            CURRENT_URL, data=json.dumps(data), **EXTRA,
        )
        assert response.status_code == 404


async def test_unset_by_partner_multiple_partners(
        taxi_eats_restapp_authorizer,
):
    token1 = '111'
    token2 = '222'
    partner_id1 = 1
    partner_id2 = 2
    email = 'email@yandex.ru'
    for token, partner_id in [(token1, partner_id1), (token2, partner_id2)]:
        data = {'token': token, 'partner_id': partner_id, 'email': email}
        await taxi_eats_restapp_authorizer.post(
            SET_URL, data=json.dumps(data), **EXTRA,
        )

    data = {'partner_id': partner_id1}
    response = await taxi_eats_restapp_authorizer.post(
        UNSET_BY_PARTNER_URL, data=json.dumps(data), **EXTRA,
    )
    assert response.status_code == 200

    for token, status_code in [(token1, 404), (token2, 200)]:
        data = {'token': token}
        response = await taxi_eats_restapp_authorizer.post(
            CURRENT_URL, data=json.dumps(data), **EXTRA,
        )
        assert response.status_code == status_code
