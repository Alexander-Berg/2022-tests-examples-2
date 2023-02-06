import json

import bson.json_util
import pytest

from tests_personal import aes_cipher


CRYPTO_KEY = 'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8='


@pytest.mark.parametrize(
    'value, expected_id, validate',
    [
        ('email_3@yandex.ru', None, True),
        ('email_1@yandex.ru', '2f84f27dca0142a7907acad288fd24a6', True),
    ],
)
async def test_store(taxi_personal, mongodb, value, expected_id, validate):
    request_data = {'email': value}
    if validate is not None:
        request_data['validate'] = validate

    response = await taxi_personal.post(
        'emails/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json=request_data,
    )
    assert response.status_code == 200
    assert response.json()['email'] == value

    doc = mongodb.personal_emails.find_one({'_id': response.json()['id']})
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


@pytest.mark.parametrize('value', ['', 'email', 'email@yandex@yandex.ru'])
async def test_store_invalid_data(taxi_personal, value):
    response = await taxi_personal.post(
        'emails/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'email': value},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Invalid email'}


async def test_find(taxi_personal):
    response = await taxi_personal.post(
        'emails/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'email': 'email_1@yandex.ru'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '2f84f27dca0142a7907acad288fd24a6',
        'email': 'email_1@yandex.ru',
    }


async def test_find_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'emails/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'email': 'email_111111@yandex.ru'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Doc not found in mongo',
    }


async def test_retrieve(taxi_personal):
    response = await taxi_personal.post(
        'emails/retrieve',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'id': '2f84f27dca0142a7907acad288fd24a6'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '2f84f27dca0142a7907acad288fd24a6',
        'email': 'email_1@yandex.ru',
    }


async def test_retrieve_non_existing(taxi_personal):
    response = await taxi_personal.post(
        'emails/retrieve',
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
                {'value': 'email_3@yandex.ru', 'expected_id': None},
                {'value': 'email_4@yandex.ru', 'expected_id': None},
            ],
            None,
        ),
        (
            [
                {'value': 'email_5@yandex.ru', 'expected_id': None},
                {
                    'value': 'email_1@yandex.ru',
                    'expected_id': '2f84f27dca0142a7907acad288fd24a6',
                },
            ],
            None,
        ),
        (
            [
                {
                    'value': 'email_1@yandex.ru',
                    'expected_id': '2f84f27dca0142a7907acad288fd24a6',
                },
                {
                    'value': 'email_2@yandex.ru',
                    'expected_id': '1a3687a0907c41c58c6f446e9a7d4bb8',
                },
            ],
            False,
        ),
        (
            [
                {
                    'value': 'email_1@yandex.ru',
                    'expected_id': '2f84f27dca0142a7907acad288fd24a6',
                },
                {
                    'value': 'email_2@yandex.ru',
                    'expected_id': '1a3687a0907c41c58c6f446e9a7d4bb8',
                },
            ],
            None,
        ),
        (
            [
                {
                    'value': 'email_1@yandex.ru',
                    'expected_id': '2f84f27dca0142a7907acad288fd24a6',
                },
                {'value': 'email_3@yandex.ru', 'expected_id': None},
                {
                    'value': 'email_2@yandex.ru',
                    'expected_id': '1a3687a0907c41c58c6f446e9a7d4bb8',
                },
                {'value': 'email_3@yandex.ru', 'expected_id': None},
                {
                    'value': 'email_1@yandex.ru',
                    'expected_id': '2f84f27dca0142a7907acad288fd24a6',
                },
                {'value': 'email_4@yandex.ru', 'expected_id': None},
                {
                    'value': 'email_2@yandex.ru',
                    'expected_id': '1a3687a0907c41c58c6f446e9a7d4bb8',
                },
            ],
            None,
        ),
    ],
)
async def test_bulk_store(taxi_personal, mongodb, data_items, validate):
    request_items = [{'email': item['value']} for item in data_items]
    request_data = {'items': request_items}
    if validate is not None:
        request_data['validate'] = validate

    response = await taxi_personal.post(
        'emails/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json=request_data,
    )
    assert response.status_code == 200
    response_items = response.json()['items']
    assert len(response_items) == len(data_items)

    for request_item, response_item in zip(data_items, response_items):
        assert response_item['email'] == request_item['value']

        inserted_doc = mongodb.personal_emails.find_one(response_item['id'])

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
        (['email', 'email@yandex.ru']),
        (['email@yandex.ru', '']),
        (['email@yandex.ru', 'email']),
        (['email@yandex.ru', 'email@email@yandex.ru']),
    ],
)
async def test_bulk_store_invalid_data(taxi_personal, values):
    request_items = [{'email': value} for value in values]
    response = await taxi_personal.post(
        'emails/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': request_items},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Invalid email'}


@pytest.mark.parametrize(
    'data_items',
    [
        [
            {
                'id': '2f84f27dca0142a7907acad288fd24a6',
                'value': 'email_1@yandex.ru',
            },
            {
                'id': '1a3687a0907c41c58c6f446e9a7d4bb8',
                'value': 'email_2@yandex.ru',
            },
        ],
        [
            {
                'id': '2f84f27dca0142a7907acad288fd24a6',
                'value': 'email_1@yandex.ru',
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
        'emails/bulk_retrieve',
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
        response_items[item['id']] = item['email']

    for item in data_items:
        if item['value'] is not None:
            assert item['id'] in response_items
            assert response_items[item['id']] == item['value']
        else:
            assert item['id'] not in response_items
