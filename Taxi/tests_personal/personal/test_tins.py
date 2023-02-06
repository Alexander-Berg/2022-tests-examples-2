import json

import bson.json_util
import pytest

from tests_personal import aes_cipher


CRYPTO_KEY = 'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8='


@pytest.mark.parametrize(
    'value, expected_id',
    [
        ('000000000003', None),
        ('000000000001', '5f0a2c34e89e4320a2f89d19a7ff678b'),
    ],
)
async def test_store(taxi_personal, mongodb, value, expected_id):
    response = await taxi_personal.post(
        'tins/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'tin': value},
    )
    assert response.status_code == 200
    assert response.json()['tin'] == value

    doc = mongodb.personal_tins.find_one({'_id': response.json()['id']})
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


@pytest.mark.parametrize('value', ['', '111111111q', 'email@yandex'])
async def test_store_invalid_data(taxi_personal, value):
    response = await taxi_personal.post(
        'tins/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'tin': value},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Invalid tin'}


async def test_find(taxi_personal):
    response = await taxi_personal.post(
        'tins/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'tin': '000000000001'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '5f0a2c34e89e4320a2f89d19a7ff678b',
        'tin': '000000000001',
    }


async def test_find_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'tins/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'tin': '0000000000011111111'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Doc not found in mongo',
    }


async def test_retrieve(taxi_personal):
    response = await taxi_personal.post(
        'tins/retrieve',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'id': '5f0a2c34e89e4320a2f89d19a7ff678b'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '5f0a2c34e89e4320a2f89d19a7ff678b',
        'tin': '000000000001',
    }


async def test_retrieve_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'tins/retrieve',
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
            {'value': '000000000003', 'expected_id': None},
            {'value': '000000000004', 'expected_id': None},
        ],
        [
            {'value': '000000000005', 'expected_id': None},
            {
                'value': '000000000001',
                'expected_id': '5f0a2c34e89e4320a2f89d19a7ff678b',
            },
        ],
        [
            {
                'value': '000000000001',
                'expected_id': '5f0a2c34e89e4320a2f89d19a7ff678b',
            },
            {
                'value': '000000000002',
                'expected_id': '6ed614c5b777402f95e6f8df9c761db1',
            },
        ],
        [
            {
                'value': '000000000002',
                'expected_id': '6ed614c5b777402f95e6f8df9c761db1',
            },
            {
                'value': '000000000001',
                'expected_id': '5f0a2c34e89e4320a2f89d19a7ff678b',
            },
        ],
        [
            {
                'value': '000000000002',
                'expected_id': '6ed614c5b777402f95e6f8df9c761db1',
            },
            {
                'value': '000000000001',
                'expected_id': '5f0a2c34e89e4320a2f89d19a7ff678b',
            },
            {'value': '000000000003', 'expected_id': None},
            {'value': '000000000004', 'expected_id': None},
            {
                'value': '000000000002',
                'expected_id': '6ed614c5b777402f95e6f8df9c761db1',
            },
            {
                'value': '000000000001',
                'expected_id': '5f0a2c34e89e4320a2f89d19a7ff678b',
            },
        ],
    ],
)
async def test_bulk_store(taxi_personal, mongodb, data_items):
    request_items = [{'tin': item['value']} for item in data_items]
    response = await taxi_personal.post(
        'tins/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': request_items},
    )
    assert response.status_code == 200
    response_items = response.json()['items']
    assert len(response_items) == len(data_items)

    for request_item, response_item in zip(data_items, response_items):
        assert response_item['tin'] == request_item['value']

        inserted_doc = mongodb.personal_tins.find_one(response_item['id'])

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
    'values', [(['tin', '11111111']), (['1111111111', ''])],
)
async def test_bulk_store_invalid_data(taxi_personal, values):
    request_items = [{'tin': value} for value in values]
    response = await taxi_personal.post(
        'tins/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': request_items},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Invalid tin'}


@pytest.mark.parametrize(
    'data_items',
    [
        [
            {
                'id': '5f0a2c34e89e4320a2f89d19a7ff678b',
                'value': '000000000001',
            },
            {
                'id': '6ed614c5b777402f95e6f8df9c761db1',
                'value': '000000000002',
            },
        ],
        [
            {
                'id': '5f0a2c34e89e4320a2f89d19a7ff678b',
                'value': '000000000001',
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
        'tins/bulk_retrieve',
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
        response_items[item['id']] = item['tin']

    for item in data_items:
        if item['value'] is not None:
            assert item['id'] in response_items
            assert response_items[item['id']] == item['value']
        else:
            assert item['id'] not in response_items
