import json

import bson.json_util
import pytest

from tests_personal import aes_cipher


CRYPTO_KEY = 'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8='


@pytest.mark.parametrize(
    'value, expected_id, validate',
    [
        ('+73333333333', None, True),
        ('+73333333333', None, False),
        ('+73333333333', None, None),
        ('    +7(111)111-11-11', None, False),
        ('+71111111111', '8657329a87d7456380afb287874f022c', True),
        ('+7(111)111-11-11', '7c606cadc49c4cd79b0782aeff0e7318', False),
    ],
)
async def test_store(taxi_personal, mongodb, value, expected_id, validate):
    request_data = {'phone': value}
    if validate is not None:
        request_data['validate'] = validate

    response = await taxi_personal.post(
        'phones/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json=request_data,
    )
    assert response.status_code == 200
    assert response.json()['phone'] == value

    doc = mongodb.personal_phones.find_one({'_id': response.json()['id']})
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


@pytest.mark.parametrize(
    'value',
    [
        '81111111111',
        '-71111111111',
        '+7(111)111-11-11',
        '+71111a111111',
        '+',
        '',
    ],
)
async def test_store_invalid_data(taxi_personal, value):
    response = await taxi_personal.post(
        'phones/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'phone': value},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid phone number',
    }


async def test_find(taxi_personal):
    response = await taxi_personal.post(
        'phones/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'phone': '+71111111111'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '8657329a87d7456380afb287874f022c',
        'phone': '+71111111111',
    }


async def test_find_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'phones/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'phone': '+71111111111111111111'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Doc not found in mongo',
    }


async def test_retrieve(taxi_personal):
    response = await taxi_personal.post(
        'phones/retrieve',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'id': '8657329a87d7456380afb287874f022c'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '8657329a87d7456380afb287874f022c',
        'phone': '+71111111111',
    }


async def test_retrieve_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'phones/retrieve',
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
    'data_items, validate',
    [
        (
            [
                {'value': '+73333333333', 'expected_id': None},
                {'value': '+74444444444', 'expected_id': None},
            ],
            True,
        ),
        (
            [
                {
                    'value': '+71111111111',
                    'expected_id': '8657329a87d7456380afb287874f022c',
                },
                {'value': '+75555555555', 'expected_id': None},
            ],
            True,
        ),
        (
            [
                {'value': '+75555555555', 'expected_id': None},
                {
                    'value': '+71111111111',
                    'expected_id': '8657329a87d7456380afb287874f022c',
                },
            ],
            None,
        ),
        (
            [
                {
                    'value': '+71111111111',
                    'expected_id': '8657329a87d7456380afb287874f022c',
                },
                {
                    'value': '+72222222222',
                    'expected_id': '97ac523d491745d1afae88bea477cc36',
                },
            ],
            True,
        ),
        (
            [
                {'value': '    +7(111)111-11-11', 'expected_id': None},
                {
                    'value': '+7(111)111-11-11',
                    'expected_id': '7c606cadc49c4cd79b0782aeff0e7318',
                },
            ],
            False,
        ),
        (
            [
                {
                    'value': '+71111111111',
                    'expected_id': '8657329a87d7456380afb287874f022c',
                },
                {'value': '+73333333333', 'expected_id': None},
                {
                    'value': '+72222222222',
                    'expected_id': '97ac523d491745d1afae88bea477cc36',
                },
                {'value': '+73333333333', 'expected_id': None},
                {
                    'value': '+71111111111',
                    'expected_id': '8657329a87d7456380afb287874f022c',
                },
                {'value': '+74444444444', 'expected_id': None},
                {
                    'value': '+72222222222',
                    'expected_id': '97ac523d491745d1afae88bea477cc36',
                },
            ],
            None,
        ),
    ],
)
async def test_bulk_store(taxi_personal, mongodb, data_items, validate):
    request_items = [{'phone': item['value']} for item in data_items]
    request_data = {'items': request_items}
    if validate is not None:
        request_data['validate'] = validate

    response = await taxi_personal.post(
        'phones/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json=request_data,
    )
    assert response.status_code == 200
    response_items = response.json()['items']
    assert len(response_items) == len(data_items)

    for request_item, response_item in zip(data_items, response_items):
        assert response_item['phone'] == request_item['value']

        inserted_doc = mongodb.personal_phones.find_one(response_item['id'])

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
    'values',
    [
        (['+71111111111', '81111111111']),
        (['+71111111111', '-71111111111']),
        (['+71111111111', '+7(111)111-11-11']),
        (['+71111111111', '+71111a111111']),
        (['+71111111111', '+']),
        (['', '+71111111111']),
    ],
)
async def test_bulk_store_invalid_data(taxi_personal, values):
    request_items = [{'phone': value} for value in values]
    response = await taxi_personal.post(
        'phones/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': request_items},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid phone number',
    }


@pytest.mark.parametrize(
    'data_items',
    [
        [
            {
                'id': '97ac523d491745d1afae88bea477cc36',
                'value': '+72222222222',
            },
            {
                'id': '8657329a87d7456380afb287874f022c',
                'value': '+71111111111',
            },
        ],
        [
            {'id': 'non_existing_id', 'value': None},
            {
                'id': '8657329a87d7456380afb287874f022c',
                'value': '+71111111111',
            },
        ],
        [
            {
                'id': '8657329a87d7456380afb287874f022c',
                'value': '+71111111111',
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
        'phones/bulk_retrieve',
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
        response_items[item['id']] = item['phone']

    for item in data_items:
        if item['value'] is not None:
            assert item['id'] in response_items
            assert response_items[item['id']] == item['value']
        else:
            assert item['id'] not in response_items
