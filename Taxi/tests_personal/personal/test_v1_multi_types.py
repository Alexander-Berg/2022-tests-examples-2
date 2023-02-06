import json

import bson.json_util
import pytest

from tests_personal import aes_cipher

CRYPTO_KEY = 'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8='


def _all_collections(mongodb):
    return {
        'phone': mongodb.personal_phones,
        'email': mongodb.personal_emails,
        'driver_license': mongodb.personal_driver_licenses,
        'yandex_login': mongodb.personal_yandex_logins,
        'tin': mongodb.personal_tins,
        'identification': mongodb.personal_identifications,
        'telegram_login': mongodb.personal_telegram_logins,
        'telegram_id': mongodb.personal_telegram_ids,
        'deptrans_id': mongodb.personal_deptrans_ids,
        'full_name': mongodb.personal_full_names,
        'address': mongodb.personal_addresses,
        'gps_coord': mongodb.personal_gps_coords,
        'gps': mongodb.personal_gps,
    }


def _get_collection_by_url(url, mongodb):
    return _all_collections(mongodb)[url]


def create_request(case):
    result = {'items': [item['value'] for item in case['items']]}
    if 'validate' in case:
        result['validate'] = case['validate']
    if 'normalize' in case:
        result['normalize'] = case['normalize']
    return result


def check_store_response(response, case):
    assert (
        response.status_code == 200
    ), 'invalid code in case: {}. Response: {}'.format(case, response.json())

    for i, item in enumerate(case['items']):
        response_item = response.json()['items'][i]
        assert response_item['value'] == item['value']

        if 'normalized_value' in item or 'normalized' in response_item:
            assert response_item['normalized'] == item['normalized_value']

        if 'error' in item or 'error' in response_item:
            assert response_item['error'] == item['error']
        elif 'expected_id' in item:
            assert response_item['id'] == item['expected_id']


def check_retrieve_response(response, case):
    assert (
        response.status_code == 200
    ), 'invalid code in case: {}. Response: {}'.format(case, response.json())

    def gen_key(item):
        return '{}_{}'.format(item['type'], item['id'])

    samples = {gen_key(item): item.get('value') for item in case['items']}

    found_keys = set()

    for response_item in response.json()['items']:
        sample_item = samples[gen_key(response_item)]

        found_keys.add(gen_key(response_item))

        assert response_item['value'] == sample_item

    for key, value in samples.items():
        if value is not None:
            assert key in found_keys, (
                '{} is missed in answer {}. Case {}'.format(
                    key, response.json(), case,
                )
            )


def check_find_response(response, case):
    assert (
        response.status_code == 200
    ), f'invalid code in case: {case}. Response: {response.json()}'

    for i, item in enumerate(case['items']):
        response_item = response.json()['items'][i]
        assert response_item['value'] == item['value']

        if 'normalized_value' in item or 'normalized' in response_item:
            assert response_item['normalized'] == item['normalized_value']

        if 'error' in item:
            assert response_item['error'] == item['error']
        elif item.get('missed', False):
            assert response_item['missed'] is True
        else:
            assert 'missed' not in response_item
            assert response_item['id'] == item['id']


def check_collection_data(response, case, mongodb):
    for i, item in enumerate(case['items']):
        if 'error' in item:
            continue

        response_item = response.json()['items'][i]

        doc = _get_collection_by_url(item['type'], mongodb).find_one(
            {'_id': response_item['id']},
        )

        assert doc is not None

        bson_str = bson.json_util.dumps(doc['crypto_iv'])
        crypto_iv = json.loads(bson_str)['$binary']
        assert len(crypto_iv) == 24

        if 'stored_value' in item:
            bson_str = bson.json_util.dumps(doc['value'])
            value_encoded = json.loads(bson_str)['$binary']
            cip = aes_cipher.AESCipher(CRYPTO_KEY, crypto_iv)
            decoded_value = cip.decode(value_encoded)
            assert decoded_value == item['stored_value']


async def test_multi_type_store(taxi_personal, mongodb, load_json):
    json_items = load_json('multi_types_items.json')
    for case in json_items['store']:

        request_json = create_request(case)

        response = await taxi_personal.post(
            'v1/multi_types/store', json=request_json,
        )

        check_store_response(response, case)
        check_collection_data(response, case, mongodb)


@pytest.mark.config(PERSONAL_MONGO_CACHE_ENABLED=True)
async def test_multi_type_store_cache(taxi_personal, mongodb, load_json):
    json_items = load_json('multi_types_items.json')
    for case in json_items['store']:
        request_json = create_request(case)
        response = await taxi_personal.post(
            'v1/multi_types/store', json=request_json,
        )
        check_store_response(response, case)
        check_collection_data(response, case, mongodb)

    # clear all records in collections. So cache only available
    for collection in _all_collections(mongodb).values():
        collection.delete_many({})

    # second requests from cache
    for case in json_items['store']:
        request_json = create_request(case)
        response = await taxi_personal.post(
            'v1/multi_types/store', json=request_json,
        )
        check_store_response(response, case)

    # lookup any records in collections. They should be empty
    for collection in _all_collections(mongodb).values():
        doc = collection.find_one({})
        assert doc is None


async def test_multi_type_retrieve(taxi_personal, load_json):
    json_items = load_json('multi_types_items.json')
    for case in json_items['retrieve']:
        request_json = request_json = {
            'items': [
                {'id': item['id'], 'type': item['type']}
                for item in case['items']
            ],
        }
        response = await taxi_personal.post(
            'v1/multi_types/retrieve', json=request_json,
        )
        check_retrieve_response(response, case)


@pytest.mark.config(PERSONAL_MONGO_CACHE_ENABLED=True)
async def test_multi_type_retrieve_mixed_cache(taxi_personal, load_json):
    """
    Some cases partially duplicate requested ids to check cache logic
    """
    json_items = load_json('multi_types_items.json')
    for case in json_items['retrieve']:
        request_json = {
            'items': [
                {'id': item['id'], 'type': item['type']}
                for item in case['items']
            ],
        }
        response = await taxi_personal.post(
            'v1/multi_types/retrieve', json=request_json,
        )
        check_retrieve_response(response, case)


@pytest.mark.config(PERSONAL_MONGO_CACHE_ENABLED=True)
async def test_multi_type_retrieve_cache_only(
        taxi_personal, mongodb, load_json,
):
    json_items = load_json('multi_types_items.json')
    for case in json_items['retrieve']:
        request_json = {
            'items': [
                {'id': item['id'], 'type': item['type']}
                for item in case['items']
            ],
        }
        response = await taxi_personal.post(
            'v1/multi_types/retrieve', json=request_json,
        )
        check_retrieve_response(response, case)

    # clear all records in collections. So cache only available
    for collection in _all_collections(mongodb).values():
        collection.delete_many({})

    # second requests get data only from cache
    for case in json_items['retrieve']:
        request_json = {
            'items': [
                {'id': item['id'], 'type': item['type']}
                for item in case['items']
            ],
        }
        response = await taxi_personal.post(
            'v1/multi_types/retrieve', json=request_json,
        )
        check_retrieve_response(response, case)


async def test_multi_type_find(taxi_personal, mongodb, load_json):
    json_items = load_json('multi_types_items.json')
    for case in json_items['find']:

        request_json = create_request(case)

        response = await taxi_personal.post(
            'v1/multi_types/find', json=request_json,
        )

        check_find_response(response, case)
