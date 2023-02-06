import json

import bson.json_util
import pytest

from tests_personal import aes_cipher


CRYPTO_KEY = 'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8='


URLS = [
    'phones',
    'emails',
    'driver_licenses',
    'yandex_logins',
    'tins',
    'identifications',
    'telegram_logins',
    'telegram_ids',
    'deptrans_ids',
]


URLS_WITH_DATA_FILES = [
    ('phones', 'phones_items.json'),
    ('emails', 'emails_items.json'),
    ('driver_licenses', 'driver_licenses_items.json'),
    ('yandex_logins', 'yandex_logins_items.json'),
    ('tins', 'tins_items.json'),
    ('identifications', 'identifications_items.json'),
    ('telegram_logins', 'telegram_logins_items.json'),
    ('telegram_ids', 'telegram_ids_items.json'),
    ('deptrans_ids', 'deptrans_ids_items.json'),
]


# for store_invalid_data and bulk_store_invalid_data
URLS_WITH_INVALID_DATA_FILES = [
    ('phones', 'phones_items.json'),
    ('emails', 'emails_items.json'),
    ('tins', 'tins_items.json'),
    ('telegram_logins', 'telegram_logins_items.json'),
]


def _get_collection_by_url(url, mongodb):
    url_func_dict = {
        'phones': mongodb.personal_phones,
        'emails': mongodb.personal_emails,
        'driver_licenses': mongodb.personal_driver_licenses,
        'yandex_logins': mongodb.personal_yandex_logins,
        'tins': mongodb.personal_tins,
        'identifications': mongodb.personal_identifications,
        'telegram_logins': mongodb.personal_telegram_logins,
        'telegram_ids': mongodb.personal_telegram_ids,
        'deptrans_ids': mongodb.personal_deptrans_ids,
    }
    return url_func_dict[url]


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_DATA_FILES)
async def test_store(taxi_personal, mongodb, load_json, url, data_items_file):
    json_items = load_json(data_items_file)
    for data_items in json_items['store']:
        value = data_items['value']

        expected_id = data_items['expected_id']

        request_json = {'value': value}
        if 'validate' in data_items.keys():
            request_json['validate'] = data_items['validate']

        response = await taxi_personal.post(
            f'v1/{url}/store', json=request_json,
        )
        if url == 'driver_licenses':
            value = _normalize_license(value)

        assert response.status_code == 200
        assert response.json()['value'] == value

        doc = _get_collection_by_url(url, mongodb).find_one(
            {'_id': response.json()['id']},
        )
        assert doc is not None
        if 'hashed_value' in data_items.keys():
            assert doc['hashed_value'] == data_items['hashed_value']

        if expected_id is not None:
            assert doc['_id'] == expected_id

        bson_str = bson.json_util.dumps(doc['crypto_iv'])
        crypto_iv = json.loads(bson_str)['$binary']
        assert len(crypto_iv) == 24

        bson_str = bson.json_util.dumps(doc['value'])
        value_encoded = json.loads(bson_str)['$binary']
        cip = aes_cipher.AESCipher(CRYPTO_KEY, crypto_iv)
        assert cip.decode(value_encoded) == value


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_INVALID_DATA_FILES)
async def test_store_invalid_data(
        taxi_personal, load_json, url, data_items_file,
):
    json_items = load_json(data_items_file)
    for data_items in json_items['store_invalid_data']:
        response = await taxi_personal.post(
            f'v1/{url}/store', json={'value': data_items['value']},
        )
        assert response.status_code == 400


@pytest.mark.parametrize('url', URLS)
async def test_store_hash_collision(taxi_personal, url):
    response = await taxi_personal.post(
        f'v1/{url}/store',
        json={'value': 'COLLISION_VALUE', 'validate': False},
    )
    assert response.status_code == 500


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_DATA_FILES)
async def test_find(taxi_personal, load_json, url, data_items_file):
    json_items = load_json(data_items_file)
    data_items = json_items['retrieve']  # same test data as retrieve

    value = data_items['value']
    expected_id = data_items['expected_id']

    response = await taxi_personal.post(
        f'v1/{url}/find', json={'value': value},
    )
    if url == 'driver_licenses':
        value = _normalize_license(value)

    assert response.status_code == 200
    assert response.json() == {'id': expected_id, 'value': value}


@pytest.mark.parametrize('url', URLS)
async def test_find_non_existing(taxi_personal, url):
    response = await taxi_personal.post(
        f'v1/{url}/find', json={'value': 'non_existent_value'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No document with such id',
    }


@pytest.mark.parametrize('url', URLS)
async def test_find_hash_collision(taxi_personal, url):
    response = await taxi_personal.post(
        f'v1/{url}/find', json={'value': 'COLLISION_VALUE'},
    )
    assert response.status_code == 500


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_DATA_FILES)
async def test_retrieve(taxi_personal, load_json, url, data_items_file):
    json_items = load_json(data_items_file)
    data_items = json_items['retrieve']

    value = data_items['value']
    expected_id = data_items['expected_id']

    response = await taxi_personal.post(
        f'v1/{url}/retrieve', json={'id': expected_id},
    )
    if url == 'driver_licenses':
        value = _normalize_license(value)

    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=60'
    assert response.json() == {'id': expected_id, 'value': value}


@pytest.mark.parametrize('url', URLS)
async def test_retrieve_non_existing(taxi_personal, url):
    response = await taxi_personal.post(
        f'v1/{url}/retrieve', json={'id': 'non_existent_id'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No document with such id',
    }


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_DATA_FILES)
async def test_bulk_store(
        taxi_personal, mongodb, load_json, url, data_items_file,
):
    json_items = load_json(data_items_file)
    for data_items in json_items['bulk_store']:
        validate = None
        if isinstance(data_items, dict):
            if 'validate' in data_items.keys():
                validate = data_items['validate']
            data_items = data_items['values']

        request_items = [{'value': item['value']} for item in data_items]
        request_json = {'items': request_items}
        if validate is not None:
            request_json['validate'] = validate

        response = await taxi_personal.post(
            f'v1/{url}/bulk_store', json=request_json,
        )
        assert response.status_code == 200
        response_items = response.json()['items']
        assert len(response_items) == len(data_items)

        for request_item, response_item in zip(data_items, response_items):
            value = request_item['value']
            if url == 'driver_licenses':
                value = _normalize_license(request_item['value'])

            assert response_item['value'] == value
            inserted_doc = _get_collection_by_url(url, mongodb).find_one(
                response_item['id'],
            )

            bson_str = bson.json_util.dumps(inserted_doc['crypto_iv'])
            crypto_iv = json.loads(bson_str)['$binary']
            assert len(crypto_iv) == 24

            bson_str = bson.json_util.dumps(inserted_doc['value'])
            value_encoded = json.loads(bson_str)['$binary']

            cip = aes_cipher.AESCipher(CRYPTO_KEY, crypto_iv)
            assert cip.decode(value_encoded) == value

            if 'hashed_value' in request_item.keys():
                assert (
                    inserted_doc['hashed_value']
                    == request_item['hashed_value']
                )

            assert response_item['id'] == inserted_doc['_id']
            if request_item['expected_id'] is not None:
                assert response_item['id'] == request_item['expected_id']


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_INVALID_DATA_FILES)
async def test_bulk_store_invalid_data(
        taxi_personal, load_json, url, data_items_file,
):
    json_items = load_json(data_items_file)
    for values in json_items['bulk_store_invalid_data']:
        request_items = [{'value': value['value']} for value in values]
        response = await taxi_personal.post(
            f'v1/{url}/bulk_store', json={'items': request_items},
        )
        assert response.status_code == 400


@pytest.mark.parametrize('url', URLS)
async def test_bulk_store_hash_collision(taxi_personal, url):
    request_items = [{'value': 'COLLISION_VALUE'}]
    response = await taxi_personal.post(
        f'v1/{url}/bulk_store',
        json={'items': request_items, 'validate': False},
    )
    assert response.status_code == 500


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_INVALID_DATA_FILES)
async def test_bulk_store_v2(
        taxi_personal, mongodb, load_json, url, data_items_file,
):
    json_items = load_json(data_items_file)
    for data_items in json_items['bulk_store_with_errors']:
        request_values = data_items['values']
        request_items = [{'value': item['value']} for item in request_values]
        request_json = {'items': request_items, 'validate': True}
        response = await taxi_personal.post(
            f'v2/{url}/bulk_store', json=request_json,
        )
        assert response.status_code == 200
        response_items = response.json()['items']
        assert len(response_items) == len(request_values)

        for request_item, response_item in zip(request_values, response_items):
            value = request_item['value']
            if url == 'driver_licenses':
                value = _normalize_license(request_item['value'])
            assert response_item['value'] == value

            if 'id' in response_item:
                inserted_doc = _get_collection_by_url(url, mongodb).find_one(
                    response_item['id'],
                )

                bson_str = bson.json_util.dumps(inserted_doc['crypto_iv'])
                crypto_iv = json.loads(bson_str)['$binary']
                assert len(crypto_iv) == 24

                bson_str = bson.json_util.dumps(inserted_doc['value'])
                value_encoded = json.loads(bson_str)['$binary']

                cip = aes_cipher.AESCipher(CRYPTO_KEY, crypto_iv)
                assert cip.decode(value_encoded) == value

                assert response_item['id'] == inserted_doc['_id']
                if request_item['expected_id'] is not None:
                    assert response_item['id'] == request_item['expected_id']
            else:
                assert response_item['error'] == request_item['expected_error']


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_DATA_FILES)
async def test_bulk_retrieve(taxi_personal, load_json, url, data_items_file):
    json_items = load_json(data_items_file)
    for data_items in json_items['bulk_retrieve']:
        request_items = [{'id': item['id']} for item in data_items]
        response = await taxi_personal.post(
            f'v1/{url}/bulk_retrieve', json={'items': request_items},
        )
        assert response.status_code == 200
        size = len(
            {item['id'] for item in data_items if item['value'] is not None},
        )
        assert len(response.json()['items']) == size

        response_items = {}
        for item in response.json()['items']:
            response_items[item['id']] = item['value']

        for item in data_items:
            if item['value'] is not None:
                value = item['value']
                if url == 'driver_licenses':
                    value = _normalize_license(item['value'])

                assert response_items[item['id']] == value
                assert item['id'] in response_items
            else:
                assert item['id'] not in response_items


def _normalize_license(license_):
    cyrillic_to_latin = {
        ord(a): ord(b) for a, b in zip('АВСЕНКМОРТХУ', 'ABCEHKMOPTXY')
    }
    return ''.join(license_.split()).upper().translate(cyrillic_to_latin)


@pytest.mark.parametrize('url, data_items_file', URLS_WITH_DATA_FILES)
async def test_bulk_find(taxi_personal, load_json, url, data_items_file):
    json_items = load_json(data_items_file)
    for data_items in json_items['bulk_retrieve']:
        request_items = [
            {'value': item['value']}
            for item in data_items
            if item['value'] is not None
        ]
        response = await taxi_personal.post(
            f'v1/{url}/bulk_find', json={'items': request_items},
        )
        assert response.status_code == 200
        assert len(response.json()['items']) == len(
            [item for item in data_items if item['value'] is not None],
        )

        response_items = response.json()['items']
        for request_item, response_item in zip(data_items, response_items):
            if request_item['value'] is not None:
                assert response_item['value'] == request_item['value']
                assert request_item['id'] == response_item['id']
            else:
                assert request_item['id'] not in response_items


@pytest.mark.parametrize('url', URLS)
async def test_bulk_find_hash_collision(taxi_personal, url):
    request_items = [{'value': 'COLLISION_VALUE'}]
    response = await taxi_personal.post(
        f'v1/{url}/bulk_find', json={'items': request_items},
    )
    assert response.status_code == 500


@pytest.mark.config(PERSONAL_MONGO_CACHE_ENABLED=True)
@pytest.mark.parametrize('url, data_items_file', URLS_WITH_DATA_FILES)
async def test_bulk_find_cache_hit(
        taxi_personal, load_json, url, data_items_file,
):
    json_items = load_json(data_items_file)
    for data_items in json_items['bulk_retrieve']:
        request_items = [
            {'value': item['value']}
            for item in data_items
            if item['value'] is not None
        ]
        response = await taxi_personal.post(
            f'v1/{url}/bulk_find', json={'items': request_items},
        )
        response = await taxi_personal.post(
            f'v1/{url}/bulk_find', json={'items': request_items},
        )
        assert response.status_code == 200
        assert len(response.json()['items']) == len(
            [item for item in data_items if item['value'] is not None],
        )

        response_items = response.json()['items']
        for request_item, response_item in zip(data_items, response_items):
            if request_item['value'] is not None:
                assert response_item['value'] == request_item['value']
                assert request_item['id'] == response_item['id']
            else:
                assert request_item['id'] not in response_items
