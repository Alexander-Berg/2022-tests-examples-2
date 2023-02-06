import json

import bson
import pytest

from tests_coupons import util


@pytest.mark.parametrize('_', util.PROMOCODES_DB_MODE_PARAMS)
@pytest.mark.parametrize(
    'filters, projection, expected_result',
    [
        pytest.param(
            {'code': 'onlytaxi1'},
            ['code'],
            {'_id': '57fe25192a4b0706b90d2589', 'code': 'onlytaxi1'},
            id='onlytaxi1',
        ),
        pytest.param(
            {'series_id': 'non_existing'}, [], None, id='non_existing',
        ),
    ],
)
async def test_dbpromocodes_find_one(
        filters, projection, expected_result, taxi_coupons, mongodb, _,
):
    filters_json = json.dumps(filters)
    body = {
        'filters': str(filters_json),
        'use_primary': False,
        'projection': projection,
    }
    response = await taxi_coupons.post(
        '/internal/promocodes/find_one', json=body,
    )
    assert response.status_code == 200
    doc = response.json().get('document')

    if doc is not None:
        doc = json.loads(doc)
    assert doc == expected_result


@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
@pytest.mark.parametrize(
    'filters',
    [
        pytest.param({'code': 'onlytaxi1'}, id='onlytaxi1'),
        pytest.param(
            {'series_id': {'$in': ['services', 'foo']}, 'value': 300},
            id='filters',
        ),
        pytest.param({'series_id': 'non_existing'}, id='non_existing'),
    ],
)
async def test_dbpromocodes_count(
        filters, taxi_coupons, mongodb, collections_tag,
):
    collection = util.tag_to_promocodes_for_read(mongodb, collections_tag)

    filters_json = json.dumps(filters)
    body = {'filters': str(filters_json), 'use_primary': False}
    response = await taxi_coupons.post('/internal/promocodes/count', json=body)
    assert response.status_code == 200

    expected_count = collection.count(filters)

    assert response.json()['count'] == expected_count


@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
async def test_dbpromocodes_insert(
        taxi_coupons, mongodb, load_json, collections_tag,
):
    collections = util.tag_to_promocodes_for_write(mongodb, collections_tag)

    doc_to_insert = load_json('promocode.json')

    bson_doc = bson.BSON.encode(doc_to_insert)

    response = await taxi_coupons.post(
        '/internal/promocodes/insert',
        data=bson_doc,
        headers={'Content-Type': 'application/bson'},
    )
    assert response.status_code == 200
    for collection in collections:
        found_doc = collection.find_one({'code': doc_to_insert['code']})
        del found_doc['_id']
        assert doc_to_insert == found_doc


@pytest.mark.parametrize(
    'endpoint',
    [
        pytest.param('/internal/promocodes/find_one', id='find_one'),
        pytest.param('/internal/promocodes/count', id='count'),
    ],
)
async def test_dbpromocodes_find_400(endpoint, taxi_coupons, mongodb):
    body = {'filters': '{"series_id": "id", }', 'use_primary': False}
    response = await taxi_coupons.post(endpoint, json=body)
    assert response.status_code == 400
