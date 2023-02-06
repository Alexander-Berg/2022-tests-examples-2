import json

import bson.json_util
import pytest

from tests_personal import aes_cipher


CRYPTO_KEY = 'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8='


@pytest.mark.parametrize(
    'value, expected_id',
    [
        ('yandex-login-333', None),
        ('yandex-login-111', 'ed0572665c754c2eba001427be933388'),
    ],
)
async def test_store(taxi_personal, mongodb, value, expected_id):
    response = await taxi_personal.post(
        'yandex_logins/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'login': value},
    )
    assert response.status_code == 200
    assert response.json()['login'] == value

    doc = mongodb.personal_yandex_logins.find_one(
        {'_id': response.json()['id']},
    )
    assert doc is not None

    if expected_id is not None:
        assert doc['_id'] == expected_id

    bson_str = bson.json_util.dumps(doc['crypto_iv'])
    crypto_iv = json.loads(bson_str)['$binary']
    assert len(crypto_iv) == 24

    bson_str = bson.json_util.dumps(doc['value'])
    value_encoded = json.loads(bson_str)['$binary']
    cip = aes_cipher.AESCipher(CRYPTO_KEY, crypto_iv)
    assert cip.decode(value_encoded) == value


async def test_find(taxi_personal):
    response = await taxi_personal.post(
        'yandex_logins/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'login': 'yandex-login-111'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': 'ed0572665c754c2eba001427be933388',
        'login': 'yandex-login-111',
    }


async def test_find_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'yandex_logins/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'login': 'yandex-login-1111111111'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Doc not found in mongo',
    }


async def test_retrieve(taxi_personal):
    response = await taxi_personal.post(
        'yandex_logins/retrieve',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'id': 'ed0572665c754c2eba001427be933388'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': 'ed0572665c754c2eba001427be933388',
        'login': 'yandex-login-111',
    }


async def test_retrieve_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'yandex_logins/retrieve',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'id': '111111111111111111111111'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Doc not found in mongo',
    }


@pytest.mark.parametrize(
    'data_items',
    [
        [
            {'value': 'yandex-login-333', 'expected_id': None},
            {'value': 'yandex-login-444', 'expected_id': None},
        ],
        [
            {'value': 'yandex-login-555', 'expected_id': None},
            {
                'value': 'yandex-login-111',
                'expected_id': 'ed0572665c754c2eba001427be933388',
            },
        ],
        [
            {
                'value': 'yandex-login-111',
                'expected_id': 'ed0572665c754c2eba001427be933388',
            },
            {
                'value': 'yandex-login-222',
                'expected_id': 'fe246436d3b3431fa07ea03f3764bffd',
            },
        ],
        [
            {
                'value': 'yandex-login-222',
                'expected_id': 'fe246436d3b3431fa07ea03f3764bffd',
            },
            {
                'value': 'yandex-login-111',
                'expected_id': 'ed0572665c754c2eba001427be933388',
            },
        ],
        [
            {
                'value': 'yandex-login-222',
                'expected_id': 'fe246436d3b3431fa07ea03f3764bffd',
            },
            {
                'value': 'yandex-login-111',
                'expected_id': 'ed0572665c754c2eba001427be933388',
            },
            {
                'value': 'yandex-login-222',
                'expected_id': 'fe246436d3b3431fa07ea03f3764bffd',
            },
            {
                'value': 'yandex-login-111',
                'expected_id': 'ed0572665c754c2eba001427be933388',
            },
            {'value': 'yandex-login-333', 'expected_id': None},
            {'value': 'yandex-login-444', 'expected_id': None},
        ],
    ],
)
async def test_bulk_store(taxi_personal, mongodb, data_items):
    request_items = [{'login': item['value']} for item in data_items]
    response = await taxi_personal.post(
        'yandex_logins/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': request_items},
    )
    assert response.status_code == 200
    response_items = response.json()['items']
    assert len(response_items) == len(data_items)

    for request_item, response_item in zip(data_items, response_items):
        assert response_item['login'] == request_item['value']

        inserted_doc = mongodb.personal_yandex_logins.find_one(
            response_item['id'],
        )

        bson_str = bson.json_util.dumps(inserted_doc['crypto_iv'])
        crypto_iv = json.loads(bson_str)['$binary']
        assert len(crypto_iv) == 24

        bson_str = bson.json_util.dumps(inserted_doc['value'])
        value_encoded = json.loads(bson_str)['$binary']

        cip = aes_cipher.AESCipher(CRYPTO_KEY, crypto_iv)
        assert cip.decode(value_encoded) == request_item['value']

        assert response_item['id'] == inserted_doc['_id']
        if request_item['expected_id'] is not None:
            assert response_item['id'] == request_item['expected_id']


@pytest.mark.parametrize(
    'data_items',
    [
        [
            {
                'id': 'ed0572665c754c2eba001427be933388',
                'value': 'yandex-login-111',
            },
            {
                'id': 'fe246436d3b3431fa07ea03f3764bffd',
                'value': 'yandex-login-222',
            },
        ],
        [
            {
                'id': 'ed0572665c754c2eba001427be933388',
                'value': 'yandex-login-111',
            },
            {'id': 'non_existing_id', 'value': None},
        ],
        [
            {'id': 'non_existing_id_1', 'value': None},
            {'id': 'non_existing_id_2', 'value': None},
        ],
    ],
)
async def test_bulk_retrieve(taxi_personal, data_items):
    request_items = [{'id': item['id']} for item in data_items]
    response = await taxi_personal.post(
        'yandex_logins/bulk_retrieve',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': request_items},
    )
    assert response.status_code == 200
    assert len(response.json()['items']) == len(
        [item for item in data_items if item['value'] is not None],
    )

    response_items = {}
    for item in response.json()['items']:
        response_items[item['id']] = item['login']

    for item in data_items:
        if item['value'] is not None:
            assert item['id'] in response_items
            assert response_items[item['id']] == item['value']
        else:
            assert item['id'] not in response_items
