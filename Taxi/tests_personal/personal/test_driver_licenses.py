import json

import bson.json_util
import pytest

from tests_personal import aes_cipher


CRYPTO_KEY = 'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8='


@pytest.mark.parametrize(
    'value, expected_id',
    [
        ('ABC0333333', None),
        ('ABC0111111', '1cb24be9aa8a45b89c73a5e02ce48524'),
        ('abc0111111', '1cb24be9aa8a45b89c73a5e02ce48524'),
        ('авс0111111', '1cb24be9aa8a45b89c73a5e02ce48524'),
        ('  авс01111\t11', '1cb24be9aa8a45b89c73a5e02ce48524'),
    ],
)
async def test_store(taxi_personal, mongodb, value, expected_id):
    response = await taxi_personal.post(
        'driver_licenses/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'license': value},
    )
    assert response.status_code == 200
    assert response.json()['license'] == _normalize_license(value)
    assert response.json()['license_requested'] == value

    doc = mongodb.personal_driver_licenses.find_one(
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
    assert cip.decode(value_encoded) == _normalize_license(value)


@pytest.mark.parametrize(
    'value', ['ABC0111111', 'авс0111111', '      ABC\n0111111'],
)
async def test_find(taxi_personal, value):
    response = await taxi_personal.post(
        'driver_licenses/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'license': value},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '1cb24be9aa8a45b89c73a5e02ce48524',
        'license': 'ABC0111111',
        'license_requested': value,
    }


async def test_find_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'driver_licenses/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'license': 'ABC0111111111111111'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Doc not found in mongo',
    }


async def test_retrieve(taxi_personal):
    response = await taxi_personal.post(
        'driver_licenses/retrieve',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'id': '1cb24be9aa8a45b89c73a5e02ce48524'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '1cb24be9aa8a45b89c73a5e02ce48524',
        'license': 'ABC0111111',
    }


async def test_retrieve_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'driver_licenses/retrieve',
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
            {'value': 'ABC0333333', 'expected_id': None},
            {'value': 'ABC0444444', 'expected_id': None},
        ],
        [
            {
                'value': 'ABC0111111',
                'expected_id': '1cb24be9aa8a45b89c73a5e02ce48524',
            },
            {'value': 'ABC0555555', 'expected_id': None},
        ],
        [
            {
                'value': 'авс0111111',
                'expected_id': '1cb24be9aa8a45b89c73a5e02ce48524',
            },
            {
                'value': 'Авс0222222',
                'expected_id': '2d6133b186114638a132d571ea477c2c',
            },
        ],
        [
            {
                'value': 'авс0\t222222',
                'expected_id': '2d6133b186114638a132d571ea477c2c',
            },
            {
                'value': '   авс01   11111   ',
                'expected_id': '1cb24be9aa8a45b89c73a5e02ce48524',
            },
        ],
        [
            {
                'value': 'авс0\t222222',
                'expected_id': '2d6133b186114638a132d571ea477c2c',
            },
            {'value': 'ABC0333333', 'expected_id': None},
            {
                'value': '   авс01   11111   ',
                'expected_id': '1cb24be9aa8a45b89c73a5e02ce48524',
            },
            {'value': 'авс0333333', 'expected_id': None},
            {
                'value': '      авс0\t222222\r\n',
                'expected_id': '2d6133b186114638a132d571ea477c2c',
            },
            {'value': 'abc0444444', 'expected_id': None},
            {
                'value': '   аbС01  11111',
                'expected_id': '1cb24be9aa8a45b89c73a5e02ce48524',
            },
        ],
    ],
)
async def test_bulk_store(taxi_personal, mongodb, data_items):
    request_items = [{'license': item['value']} for item in data_items]
    response = await taxi_personal.post(
        'driver_licenses/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': request_items},
    )
    assert response.status_code == 200
    response_items = response.json()['items']
    assert len(response_items) == len(data_items)

    for request_item, response_item in zip(data_items, response_items):
        normalized_value = _normalize_license(request_item['value'])
        assert response_item['license'] == normalized_value
        assert response_item['license_requested'] == request_item['value']

        inserted_doc = mongodb.personal_driver_licenses.find_one(
            response_item['id'],
        )

        bson_str = bson.json_util.dumps(inserted_doc['crypto_iv'])
        crypto_iv = json.loads(bson_str)['$binary']
        assert len(crypto_iv) == 24

        bson_str = bson.json_util.dumps(inserted_doc['value'])
        value_encoded = json.loads(bson_str)['$binary']

        cip = aes_cipher.AESCipher(CRYPTO_KEY, crypto_iv)
        assert cip.decode(value_encoded) == normalized_value

        assert response_item['id'] == inserted_doc['_id']
        if request_item['expected_id'] is not None:
            assert request_item['expected_id'] == response_item['id']


@pytest.mark.parametrize(
    'data_items',
    [
        [
            {'id': '1cb24be9aa8a45b89c73a5e02ce48524', 'value': 'ABC0111111'},
            {'id': '2d6133b186114638a132d571ea477c2c', 'value': 'ABC0222222'},
        ],
        [
            {'id': '1cb24be9aa8a45b89c73a5e02ce48524', 'value': 'ABC0111111'},
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
        'driver_licenses/bulk_retrieve',
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
        response_items[item['id']] = item['license']

    for item in data_items:
        if item['value'] is not None:
            assert item['id'] in response_items
            assert response_items[item['id']] == item['value']
        else:
            assert item['id'] not in response_items


def _normalize_license(license_):
    cyrillic_to_latin = {
        ord(a): ord(b) for a, b in zip('АВСЕНКМОРТХУ', 'ABCEHKMOPTXY')
    }
    return ''.join(license_.split()).upper().translate(cyrillic_to_latin)
