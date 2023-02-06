import json

import bson.json_util
import pytest

from tests_personal import aes_cipher


DOC_TYPES = ['identification_docs']
# from service.yaml in base64
CRYPTO_KEY = 'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8='


def _get_collection_by_url(url, mongodb):
    url_func_dict = {
        'identification_docs': mongodb.personal_identification_docs,
    }
    return url_func_dict[url]


@pytest.mark.parametrize('url', DOC_TYPES)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personal_doc_store(taxi_personal, mongodb, url):
    fields = [
        {'key': 'field1', 'value': 'value1'},
        {'key': 'field2', 'value': 'value2'},
        {'key': 'field3', 'value': 'value3'},
        {'key': 'field1', 'value': 'value1'},
    ]

    response = await taxi_personal.post(
        f'/v1/personal_doc/{url}/store', json={'fields': fields},
    )

    assert response.status_code == 200
    doc_id = response.json()['id']
    assert len(doc_id) == 32

    inserted_doc = _get_collection_by_url(url, mongodb).find_one(doc_id)
    assert (
        inserted_doc['hashed_value']
        == 'b95081abb5aa5fad3954763f425a48b9dc759eebcbfcdc8629c5d7f311740dcb'
    )

    bson_str = bson.json_util.dumps(inserted_doc['crypto_iv'])
    crypto_iv = json.loads(bson_str)['$binary']
    assert len(crypto_iv) == 24

    bson_str = bson.json_util.dumps(inserted_doc['fields'])
    fields_encoded = json.loads(bson_str)['$binary']

    cip = aes_cipher.AESCipher(CRYPTO_KEY, crypto_iv)
    assert json.loads(cip.decode(fields_encoded)) == json.loads(
        json.dumps(fields),
    )


@pytest.mark.parametrize('url', DOC_TYPES)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personal_doc_store_duplicate(taxi_personal, mongodb, url):
    request_json = {
        'fields': [
            {'key': 'field1', 'value': '1'},
            {'key': 'field2', 'value': '2'},
            {'key': 'field3', 'value': '3'},
            {'key': 'field1', 'value': '1'},
        ],
    }

    response = await taxi_personal.post(
        f'/v1/personal_doc/{url}/store', json=request_json,
    )

    assert response.status_code == 200
    doc_id = response.json()['id']
    assert doc_id == '11111111111111111111111111111111'

    inserted_doc = _get_collection_by_url(url, mongodb).find_one(doc_id)
    assert (
        inserted_doc['hashed_value']
        == '79c5f5514c9d58119f1273e2bbce0edd4a4ce7595c512fc9efdaf2c92006cd13'
    )


@pytest.mark.parametrize('url', DOC_TYPES)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personal_doc_store_hash_collision(taxi_personal, url):
    request_json = {
        'fields': [{'key': 'collision_key', 'value': 'collision_value'}],
    }

    response = await taxi_personal.post(
        f'/v1/personal_doc/{url}/store', json=request_json,
    )

    assert response.status_code == 500


@pytest.mark.parametrize('url', DOC_TYPES)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personal_doc_retrieve_existing_id(taxi_personal, url):
    response = await taxi_personal.post(
        f'/v1/personal_doc/{url}/retrieve',
        json={'id': '11111111111111111111111111111111'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'id': '11111111111111111111111111111111',
        'fields': [
            {'key': 'field1', 'value': '1'},
            {'key': 'field2', 'value': '2'},
            {'key': 'field3', 'value': '3'},
            {'key': 'field1', 'value': '1'},
        ],
    }


@pytest.mark.parametrize('url', DOC_TYPES)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personal_doc_retrieve_nonexistent_id(taxi_personal, url):
    response = await taxi_personal.post(
        f'/v1/personal_doc/{url}/retrieve', json={'id': 'nonexistent_id'},
    )

    assert response.status_code == 404
