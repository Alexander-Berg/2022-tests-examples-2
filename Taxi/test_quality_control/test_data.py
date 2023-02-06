import http

import pytest

URL = '/api/v1/data'
URL_MANY = '/api/v1/data/list'


async def test_upload_by_id(qc_client):
    entity = {
        'id': '1',
        'type': 'driver',
        'data': {
            'name': 'test test',
            'park_id': 'test_park',
            'city': 'test_city',
        },
    }

    params = {'type': entity['type'], 'id': entity['id']}

    response = await qc_client.get(URL, params=params)
    assert response.status == http.HTTPStatus.NOT_FOUND

    response = await qc_client.post(URL, params=params, json=entity['data'])
    assert response.status == http.HTTPStatus.OK
    assert await response.text() == ''

    response = await qc_client.get(URL, params=params)
    result = await response.json()
    assert result

    assert result.get('id') == entity['id']
    assert result.get('type') == entity['type']
    assert result.get('data') == entity['data']

    # check groups park and city
    assert len(result.get('groups') or []) == 2

    saved_groups = dict((x['code'], x['value']) for x in result['groups'])
    assert saved_groups == {
        'park': entity['data']['park_id'],
        'city': entity['data']['city'],
    }


@pytest.mark.dontfreeze
async def test_upload_many(qc_client):
    entity_type = 'driver'
    entity_jack = {
        'id': '1',
        'type': entity_type,
        'data': {'name': 'jack', 'park_id': 'park_1', 'city': 'Москва'},
    }

    entity_bob = {
        'id': '2',
        'type': entity_type,
        'data': {'name': 'bob', 'park_id': 'park_1', 'city': 'Москва'},
    }

    entity_alice = {
        'id': '3',
        'type': entity_type,
        'data': {'name': 'alice', 'park_id': 'park_2', 'city': 'Питер'},
    }

    response = await qc_client.post(
        URL_MANY,
        params={'type': entity_type},
        json=[
            {'id': x['id'], 'data': x['data']}
            for x in [entity_jack, entity_bob, entity_alice]
        ],
    )
    assert response.status == http.HTTPStatus.OK
    assert await response.text() == ''

    # check Alice
    response = await qc_client.get(
        URL, params={'type': entity_alice['type'], 'id': entity_alice['id']},
    )
    assert response.status == http.HTTPStatus.OK

    saved_entity = await response.json()
    assert saved_entity['id'] == entity_alice['id']
    assert saved_entity['data'] == entity_alice['data']

    # check Moscow
    response = await qc_client.get(
        URL_MANY,
        params={'type': entity_type, 'group': 'city', 'group_id': 'Москва'},
    )
    assert response.status == http.HTTPStatus.OK

    moscow_entities = dict(
        (x['id'], x) for x in (await response.json())['items']
    )
    assert entity_jack['id'] in moscow_entities
    assert entity_bob['id'] in moscow_entities
    assert entity_alice['id'] not in moscow_entities


@pytest.mark.dontfreeze
async def test_upload_by_group(qc_client):
    entity_type = 'driver'
    entity_jack = {
        'id': '1',
        'type': entity_type,
        'data': {'name': 'jack', 'park_id': 'park_1', 'city': 'Москва'},
    }

    entity_bob = {
        'id': '2',
        'type': entity_type,
        'data': {'name': 'bob', 'park_id': 'park_1', 'city': 'Москва'},
    }

    entity_alice = {
        'id': '3',
        'type': entity_type,
        'data': {'name': 'alice', 'park_id': 'park_2', 'city': 'Питер'},
    }

    response = await qc_client.post(
        URL_MANY,
        params={'type': entity_type},
        json=[
            {'id': x['id'], 'data': x['data']}
            for x in [entity_jack, entity_bob, entity_alice]
        ],
    )
    assert response.status == http.HTTPStatus.OK

    new_data = {'novice': 'true', 'park_id': 'park_3', 'city': 'Новая Москва'}
    response = await qc_client.post(
        URL,
        params={'type': entity_type, 'group': 'city', 'group_id': 'Москва'},
        json=new_data,
    )
    assert response.status == http.HTTPStatus.OK
    assert await response.text() == ''

    # check all
    response = await qc_client.get(URL_MANY, params={'type': entity_type})
    assert response.status == http.HTTPStatus.OK

    saved_entities = dict(
        (x['id'], x) for x in (await response.json())['items']
    )

    assert saved_entities[entity_alice['id']]['data'] == entity_alice['data']
    assert saved_entities[entity_jack['id']]['data'] == new_data
    assert saved_entities[entity_bob['id']]['data'] == new_data
    assert (
        saved_entities[entity_jack['id']]['groups']
        == saved_entities[entity_bob['id']]['groups']
    )

    saved_new_groups = dict(
        (x['code'], x['value'])
        for x in saved_entities[entity_jack['id']]['groups']
    )
    assert saved_new_groups == {
        'park': new_data['park_id'],
        'city': new_data['city'],
    }
