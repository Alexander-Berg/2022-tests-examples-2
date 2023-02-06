import pytest

ENDPOINT = 'v2/aggregation/cars/load'


def get_canonical_response_json(response):
    got_response = response.json()
    if 'categories' in got_response:
        for item in got_response['categories']:
            item.sort()
    assert (
        got_response['cars_revision']
        == response.headers['X-YaTaxi-Cars-Revision']
    )
    del got_response['cars_revision']  # TODO(yudind): check revision
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
            'request': {'parks': [{'park_id': 'cars required'}]},
            'status_code': 400,
            'response': {},
        },
        {
            'request': {
                'parks': [
                    {'park_id': 'something', 'cars': 'must be an array'},
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
            'request': {'parks': [{'park_id': 'unknown', 'cars': []}]},
            'status_code': 200,
            'response': {'missing': [], 'categories': []},
        },
        {
            'request': {'parks': [{'park_id': 'a1', 'cars': []}]},
            'status_code': 200,
            'response': {'missing': [], 'categories': []},
        },
        # non-empty
        {
            'request': {
                'parks': [{'park_id': 'unknown', 'cars': ['someone']}],
            },
            'status_code': 200,
            'response': {
                'missing': [{'park_id': 'unknown', 'car_id': 'someone'}],
                'categories': [],
            },
        },
        {
            'request': {
                'parks': [{'park_id': 'a2_empty', 'cars': ['unknown']}],
            },
            'status_code': 200,
            'response': {
                'missing': [{'park_id': 'a2_empty', 'car_id': 'unknown'}],
                'categories': [],
            },
        },
        {
            'request': {'parks': [{'park_id': 'a1', 'cars': ['b11_empty']}]},
            'status_code': 200,
            'response': {'missing': [], 'categories': [[]]},
        },
        {
            'request': {
                'parks': [{'park_id': 'a1', 'cars': ['b11_empty', 'b12']}],
            },
            'status_code': 200,
            'response': {'missing': [], 'categories': [[], ['E']]},
        },
        {
            'request': {
                'parks': [{'park_id': 'a1', 'cars': ['b12', 'b11_empty']}],
            },
            'status_code': 200,
            'response': {'missing': [], 'categories': [['E'], []]},
        },
        {
            'request': {
                'parks': [
                    {'park_id': 'a1', 'cars': ['b12', 'unknown', 'b11_empty']},
                    {'park_id': 'a0', 'cars': ['b00']},
                ],
            },
            'status_code': 200,
            'response': {
                'missing': [{'park_id': 'a1', 'car_id': 'unknown'}],
                'categories': [['E'], [], ['A', 'B']],
            },
        },
        {
            'request': {
                'parks': [
                    {'park_id': 'a0', 'cars': ['b00', 'b10', 'unknown']},
                    {'park_id': 'a1', 'cars': ['b10', 'b11_empty', 'b12']},
                    {'park_id': 'unknown', 'cars': ['someone']},
                ],
            },
            'status_code': 200,
            'response': {
                'missing': [
                    {'park_id': 'a0', 'car_id': 'b10'},
                    {'park_id': 'a0', 'car_id': 'unknown'},
                    {'park_id': 'unknown', 'car_id': 'someone'},
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
