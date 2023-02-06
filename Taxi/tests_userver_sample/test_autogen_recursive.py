import json

import pytest


@pytest.mark.parametrize(
    'data',
    [
        {'name': 'one'},
        {'name': 'one', 'entries': []},
        {'name': 'two', 'entries': [{'name': 'one', 'entries': []}]},
        {
            'name': 'three',
            'entries': [
                {
                    'name': 'two_0',
                    'entries': [{'name': 'one_0', 'entries': []}],
                },
                {'name': 'two_1', 'entries': [{'name': 'one_1'}]},
            ],
        },
    ],
)
async def test_recursive_type_in_array(taxi_userver_sample, data):
    response = await taxi_userver_sample.post(
        'autogen/recursive/type_in_array', data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'value': data}


@pytest.mark.parametrize(
    'data',
    [
        {'name': 'one', 'entries': [{}, {}, {}, {}, {}, {}]},
        {
            'name': 'two',
            'entries': [{'name': 'one', 'entries': [{}, {}, {}, {}, {}, {}]}],
        },
    ],
)
async def test_recursive_type_in_array_validation(taxi_userver_sample, data):
    response = await taxi_userver_sample.post(
        'autogen/recursive/type_in_array', data=json.dumps(data),
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'
    assert 'incorrect size, must be 5 (limit)' in response.json()['message']


@pytest.mark.parametrize(
    'data',
    [
        {},
        {'left': {}, 'right': {}},
        {'left': {}},
        {'right': {}},
        {'left': {'right': {}}, 'right': {'left': {}}},
        {
            'left': {'left': {}, 'right': {}},
            'right': {'left': {}, 'right': {}},
        },
        {
            'left': {'left': {'left': {}}, 'right': {}},
            'right': {'left': {}, 'right': {'left': {}}},
        },
    ],
)
async def test_recursive_node(taxi_userver_sample, data):
    response = await taxi_userver_sample.post(
        'autogen/recursive/node', data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'value': data}
