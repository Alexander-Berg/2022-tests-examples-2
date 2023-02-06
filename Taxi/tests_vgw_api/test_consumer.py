import json

import pytest

from tests_vgw_api import db_consumers


@pytest.mark.parametrize(
    ('params', 'response_data'),
    [
        (
            {'id': 1},
            {
                'id': 1,
                'name': 'name_1',
                'enabled': False,
                'gateway_ids': ['id_1', 'id_2'],
                'quota': 0,
            },
        ),
        (
            {'id': 2},
            {
                'id': 2,
                'name': 'name_2',
                'enabled': True,
                'gateway_ids': ['id_1'],
                'quota': 0,
            },
        ),
        (
            {'id': 3},
            {
                'id': 3,
                'name': 'name_3',
                'enabled': True,
                'gateway_ids': [],
                'quota': 0,
            },
        ),
    ],
)
async def test_consumer_get(taxi_vgw_api, params, response_data):

    response = await taxi_vgw_api.get('v1/consumers/id', params=params)

    assert response.status_code == 200
    assert response.json() == response_data


@pytest.mark.parametrize(
    ('params', 'response_code'),
    [
        ({'id': 'asdsa'}, 400),
        ({'id': 100000000000000000000}, 400),
        ({'id': 39}, 404),
    ],
)
async def test_consumer_get_errors(taxi_vgw_api, params, response_code):

    response = await taxi_vgw_api.get('v1/consumers/id', params=params)

    assert response.status_code == response_code
    response_json = response.json()
    assert response_json['code'] == str(response_code)


@pytest.mark.parametrize(
    ('params', 'db_data'),
    [
        ({'id': 1}, [(2, 'id_1')]),
        ({'id': 2}, [(1, 'id_1'), (1, 'id_2')]),
        ({'id': 3}, [(1, 'id_1'), (1, 'id_2'), (2, 'id_1')]),
    ],
)
async def test_consumer_delete(taxi_vgw_api, pgsql, params, db_data):

    response = await taxi_vgw_api.delete('v1/consumers/id', params=params)

    assert response.status_code == 200
    assert db_consumers.select_consumer_voice_gateways(pgsql) == db_data


@pytest.mark.parametrize(
    ('params', 'response_code'),
    [
        ({'id': 'asdsa'}, 400),
        ({'id': 100000000000000000000}, 400),
        ({'id': 39}, 404),
    ],
)
async def test_consumer_delete_errors(taxi_vgw_api, params, response_code):

    response = await taxi_vgw_api.delete('v1/consumers/id', params=params)

    assert response.status_code == response_code
    response_json = response.json()
    assert response_json['code'] == str(response_code)


@pytest.mark.parametrize(
    ('params', 'request_data', 'response_data'),
    [
        (
            {'id': 1},
            {
                'name': 'name_new',
                'enabled': True,
                'quota': 100,
                'gateway_ids': [],
            },
            {
                'id': 1,
                'name': 'name_new',
                'enabled': True,
                'quota': 0,
                'gateway_ids': [],
            },
        ),
        (
            {'id': 2},
            {'name': 'name_new', 'enabled': True, 'gateway_ids': ['id_2']},
            {
                'id': 2,
                'name': 'name_new',
                'enabled': True,
                'quota': 0,
                'gateway_ids': ['id_2'],
            },
        ),
        (
            {'id': 3},
            {
                'name': 'name_new',
                'enabled': True,
                'gateway_ids': ['id_1', 'id_2'],
            },
            {
                'id': 3,
                'name': 'name_new',
                'enabled': True,
                'quota': 0,
                'gateway_ids': ['id_1', 'id_2'],
            },
        ),
    ],
)
async def test_consumer_put(taxi_vgw_api, params, request_data, response_data):

    response = await taxi_vgw_api.put(
        'v1/consumers/id', params=params, data=json.dumps(request_data),
    )

    assert response.status_code == 200
    get_response = await taxi_vgw_api.get('v1/consumers/id', params=params)
    assert get_response.json() == response_data


@pytest.mark.parametrize(
    ('params', 'request_data', 'response_code'),
    [
        (
            {'id': 1},
            {
                'name': 'name_new',
                'enabled': True,
                'quota': 200,
                'gateway_ids': ['id_2', 'id_none'],
            },
            404,
        ),
        ({'id': 1}, {'name': True, 'enabled': True, 'quota': 300}, 400),
    ],
)
async def test_consumer_put_errors(
        taxi_vgw_api, params, request_data, response_code,
):

    response = await taxi_vgw_api.put(
        'v1/consumers/id', params=params, data=json.dumps(request_data),
    )

    assert response.status_code == response_code
    response_json = response.json()
    assert response_json['code'] == str(response_code)
