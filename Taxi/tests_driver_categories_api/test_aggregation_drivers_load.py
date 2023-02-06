import pytest

ENDPOINT = 'v2/aggregation/drivers/load'


def get_canonical_response_json(response):
    got_response = response.json()
    if 'categories' in got_response:
        for item in got_response['categories']:
            item.sort()
    assert (
        got_response['drivers_revision']
        == response.headers['X-YaTaxi-Drivers-Revision']
    )
    del got_response['drivers_revision']
    return got_response


@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize(
    'data',
    [
        # bad
        {'request': {}, 'status_code': 400, 'response': {}},
        {'request': {'_': []}, 'status_code': 400, 'response': {}},
        {
            'request': {'parks': [{'_': 'somethig'}]},
            'status_code': 400,
            'response': {},
        },
        {
            'request': {'parks': [{'park_id': ''}]},
            'status_code': 400,
            'response': {},
        },
        {
            'request': {'parks': [{'park_id': 'drivers required'}]},
            'status_code': 400,
            'response': {},
        },
        {
            'request': {
                'parks': [
                    {'park_id': 'something', 'drivers': 'must be an array'},
                ],
            },
            'status_code': 400,
            'response': {},
        },
        # empty
        {
            'request': {'parks': []},
            'status_code': 200,
            'response': {'missing': [], 'categories': []},
        },
        {
            'request': {'parks': [{'park_id': 'unknown', 'drivers': []}]},
            'status_code': 200,
            'response': {'missing': [], 'categories': []},
        },
        {
            'request': {'parks': [{'park_id': 'a1', 'drivers': []}]},
            'status_code': 200,
            'response': {'missing': [], 'categories': []},
        },
        # non-empty
        {
            'request': {
                'parks': [{'park_id': 'unknown', 'drivers': ['someone']}],
            },
            'status_code': 200,
            'response': {
                'missing': [{'park_id': 'unknown', 'driver_id': 'someone'}],
                'categories': [],
            },
        },
        {
            'request': {
                'parks': [{'park_id': 'a2_empty', 'drivers': ['unknown']}],
            },
            'status_code': 200,
            'response': {
                'missing': [{'park_id': 'a2_empty', 'driver_id': 'unknown'}],
                'categories': [],
            },
        },
        {
            'request': {
                'parks': [{'park_id': 'a1', 'drivers': ['b11_empty']}],
            },
            'status_code': 200,
            'response': {'missing': [], 'categories': [[]]},
        },
        {
            'request': {
                'parks': [{'park_id': 'a1', 'drivers': ['b11_empty', 'b12']}],
            },
            'status_code': 200,
            'response': {'missing': [], 'categories': [[], ['E']]},
        },
        {
            'request': {
                'parks': [{'park_id': 'a1', 'drivers': ['b12', 'b11_empty']}],
            },
            'status_code': 200,
            'response': {'missing': [], 'categories': [['E'], []]},
        },
        {
            'request': {
                'parks': [
                    {
                        'park_id': 'a1',
                        'drivers': ['b12', 'unknown', 'b11_empty'],
                    },
                    {'park_id': 'a0', 'drivers': ['b00']},
                ],
            },
            'status_code': 200,
            'response': {
                'missing': [{'park_id': 'a1', 'driver_id': 'unknown'}],
                'categories': [['E'], [], ['A', 'B']],
            },
        },
        {
            'request': {
                'parks': [
                    {'park_id': 'a0', 'drivers': ['b00', 'b10', 'unknown']},
                    {'park_id': 'a1', 'drivers': ['b10', 'b11_empty', 'b12']},
                    {'park_id': 'unknown', 'drivers': ['someone']},
                ],
            },
            'status_code': 200,
            'response': {
                'missing': [
                    {'park_id': 'a0', 'driver_id': 'b10'},
                    {'park_id': 'a0', 'driver_id': 'unknown'},
                    {'park_id': 'unknown', 'driver_id': 'someone'},
                ],
                'categories': [['A', 'B'], ['C', 'D'], [], ['E']],
            },
        },
    ],
)
async def test_first(taxi_driver_categories_api, taxi_config, pgsql, data):
    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        ENDPOINT, json=data['request'],
    )
    assert data['status_code'] == response.status_code
    if data['status_code'] == 200:
        assert data['response'] == get_canonical_response_json(response)
